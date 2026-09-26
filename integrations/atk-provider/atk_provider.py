"""ATK Provider Interface — the seam every ATK integration needs, in one stdlib file.

`ATK_ROUTING_INTEGRATION.md` §4 specifies a Provider Interface and §3 an environment contract.
Both were documented and **neither had an implementation anywhere in the repository**, so every
future integration would have started by writing this again, differently.

The contract this file exists to keep (§1):

    ATK may be the default. ATK may never be the only option.

Concretely, and each one is exercised by `test_atk_provider.py`:

* **Transparent** — every `Completion` names the provider that actually served it.
* **Replaceable** — changing `PROVIDER` switches providers with **no code edit**.
* **Documented** — `README.md` explains switching *away* from ATK.
* **Optional** — with `ATK_API_KEY` unset and `PROVIDER=openai`, everything runs normally.

Design rules, deliberately narrow:

* **Standard library only.** An integration asset that drags in a dependency tree is one more
  reason not to adopt it.
* **No router.** Provider selection and an ordered fallback list, nothing more. The repository
  already has a Router spec; this is the seam beneath it, not a second implementation.
* **No hardcoded key, URL or model** (§3 rule 4). Everything comes from the environment.
* **No savings claim.** This file moves requests; it does not compress, cache or optimise, and
  nothing here should be cited as evidence of a saving.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Iterable, Sequence

__all__ = [
    "Message", "Usage", "Completion", "ProviderError", "ConfigError",
    "OpenAICompatibleProvider", "AnthropicProvider", "build_provider", "complete",
    "redact", "REDACTED",
]

DEFAULT_TIMEOUT = 120
DEFAULT_RETRIES = 3

# Which env prefix each PROVIDER value reads, and the wire format it speaks. ATK is an
# OpenAI-compatible endpoint, which is why `atk` and `openai` share an adapter: the only
# difference is where the request goes and which key signs it.
PROVIDERS = {
    "atk":        ("ATK",        "openai"),
    "openai":     ("OPENAI",     "openai"),
    "deepseek":   ("DEEPSEEK",   "openai"),
    "qwen":       ("QWEN",       "openai"),
    "openrouter": ("OPENROUTER", "openai"),
    "gemini":     ("GEMINI",     "openai"),
    "custom":     ("CUSTOM",     "openai"),
    "anthropic":  ("ANTHROPIC",  "anthropic"),
}


class ProviderError(RuntimeError):
    """A request failed. Carries the provider so a fallback chain can be explained."""

    def __init__(self, message: str, *, provider: str, status: int | None = None) -> None:
        super().__init__(message)
        self.provider = provider
        self.status = status


class ConfigError(ValueError):
    """The environment does not describe a usable provider. Never guessed around."""


@dataclass
class Message:
    role: str                       # "system" | "user" | "assistant" | "tool"
    content: str


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float | None = None   # None means "not reported", never 0.0


@dataclass
class Completion:
    text: str
    model: str
    provider: str                   # which adapter actually served this
    usage: Usage = field(default_factory=Usage)
    raw: dict | None = None


def _env(prefix: str, name: str, default: str | None = None) -> str | None:
    value = os.environ.get(f"{prefix}_{name}")
    return value if value not in (None, "") else default


REDACTED = "***REDACTED***"


def redact(text: str, secrets: Iterable[str]) -> str:
    """Remove known secret values from anything about to be shown to a human.

    P4-01. The previous version echoed the first 400 characters of a provider's error body into
    the exception, with a comment reasoning that "keys travel in headers, not bodies, so this does
    not surface a credential". **That inference is wrong and was demonstrated wrong**: a server or
    proxy is free to echo the credential it rejected, and one that answers
    `401 {"error": "invalid credential <key>"}` put the key straight into the message the example
    prints to stderr.

    Redaction is the second line here, not the first: by default the body is not included at all
    (see `_post`). It still runs, because a secret can also reach a message through a URL or a
    reason string, and a defence that guards one entrance is not a defence.
    """
    out = text
    for secret in secrets:
        if secret and len(secret) >= 4:
            out = out.replace(secret, REDACTED)
    return out


def _post(url: str, payload: dict, headers: dict, timeout: int, provider: str,
          secrets: Sequence[str] = (), include_body: bool = False) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # P4-01: a controlled message by default. The status code and provider are the
        # diagnostics that matter and cannot carry a credential; the server's prose might.
        detail = ""
        if include_body:
            # P4-R2-01: this used to slice to 400 characters and THEN redact, so a key that
            # straddled the cut had its prefix survive - `redact` cannot match a value the
            # truncation already broke in half. That leak was manufactured by this function, not
            # by an upstream proxy, and the original test missed it because it only asserted the
            # FULL key was absent. Redact the whole body first; truncate what is already safe.
            raw = exc.read().decode("utf-8", "replace")
            detail = " — " + redact(raw, secrets)[:400]
        else:
            detail = (" — body withheld; set ATK_INCLUDE_ERROR_BODY=1 to include it (it may "
                      "echo your credential, so do not paste the result into a bug report)")
        raise ProviderError(redact(f"{provider}: HTTP {exc.code}{detail}", secrets),
                            provider=provider, status=exc.code) from exc
    except urllib.error.URLError as exc:
        # The URL can contain a credential in a query string on some gateways, so it is
        # redacted too rather than assumed safe.
        raise ProviderError(redact(f"{provider}: cannot reach {url} — {exc.reason}", secrets),
                            provider=provider) from exc


class OpenAICompatibleProvider:
    """`/chat/completions`. Serves ATK, OpenAI, DeepSeek, Qwen, OpenRouter and any custom host."""

    def __init__(self, name: str, api_key: str, base_url: str, model: str,
                 timeout: int = DEFAULT_TIMEOUT, include_error_body: bool = False) -> None:
        self.name = name
        self._key = api_key
        self._base = base_url.rstrip("/")
        self.model = model
        self._timeout = timeout
        self._include_error_body = include_error_body

    def build_payload(self, messages: Sequence[Message], **kwargs) -> dict:
        """The exact JSON body this adapter will send.

        P4-R2-02: the example's `--show-payload` used to construct an OpenAI-shaped body itself,
        so for Anthropic it showed something the adapter never sends. A preview that is assembled
        separately from the request is a second implementation that can drift, and did. Both now
        call this.
        """
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return payload

    def complete(self, messages: Sequence[Message], **kwargs) -> Completion:
        payload = self.build_payload(messages, **kwargs)
        data = _post(f"{self._base}/chat/completions", payload,
                     {"Authorization": f"Bearer {self._key}"}, self._timeout, self.name,
                     secrets=(self._key,), include_body=self._include_error_body)
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                f"{self.name}: response did not contain choices[0].message.content. "
                "The endpoint answered, but not in the OpenAI chat-completions shape this "
                "adapter speaks.", provider=self.name) from exc
        # P4-02: HTTP 200 with `content: null` used to return Completion(text=None), the example
        # printed "None" and exited 0. A tool-only or refused reply is not a summary, and an
        # asset whose job is to produce text must not report success without any.
        if not isinstance(text, str) or not text.strip():
            finish = (data.get("choices") or [{}])[0].get("finish_reason")
            raise ProviderError(
                f"{self.name}: the request succeeded (HTTP 200) but returned no text "
                f"(content={type(text).__name__}, finish_reason={finish!r}). This adapter "
                "handles plain text only; a tool-call or empty completion is reported as a "
                "failure rather than as an empty summary.", provider=self.name)
        u = data.get("usage") or {}
        return Completion(
            text=text,
            model=data.get("model") or self.model,
            provider=self.name,
            usage=Usage(
                prompt_tokens=int(u.get("prompt_tokens") or 0),
                completion_tokens=int(u.get("completion_tokens") or 0),
                total_tokens=int(u.get("total_tokens") or 0),
                # Absent cost is None, not 0.0. A provider that does not report cost has not
                # told us the request was free.
                cost_usd=u.get("cost_usd"),
            ),
            raw=data,
        )


class AnthropicProvider:
    """`/v1/messages`. A different wire format, so it is a different adapter, not a flag."""

    def __init__(self, name: str, api_key: str, base_url: str, model: str,
                 timeout: int = DEFAULT_TIMEOUT, max_tokens: int = 1024,
                 include_error_body: bool = False) -> None:
        self.name = name
        self._key = api_key
        self._base = base_url.rstrip("/")
        self.model = model
        self._timeout = timeout
        self._max_tokens = max_tokens
        self._include_error_body = include_error_body

    def build_payload(self, messages: Sequence[Message], **kwargs) -> dict:
        """See `OpenAICompatibleProvider.build_payload`. The shape genuinely differs here:
        `system` is hoisted out of the turns and `max_tokens` is required, which is exactly the
        drift P4-R2-02 found between the preview and the wire."""
        kwargs = dict(kwargs)
        system = " ".join(m.content for m in messages if m.role == "system") or None
        turns = [{"role": m.role, "content": m.content}
                 for m in messages if m.role in ("user", "assistant")]
        payload = {"model": self.model, "messages": turns,
                   "max_tokens": kwargs.pop("max_tokens", self._max_tokens)}
        if system:
            payload["system"] = system
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return payload

    def complete(self, messages: Sequence[Message], **kwargs) -> Completion:
        payload = self.build_payload(messages, **kwargs)
        data = _post(f"{self._base}/v1/messages", payload,
                     {"x-api-key": self._key, "anthropic-version": "2023-06-01"},
                     self._timeout, self.name,
                     secrets=(self._key,), include_body=self._include_error_body)
        try:
            text = "".join(block.get("text", "") for block in data["content"])
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"{self.name}: response contained no `content` blocks",
                                provider=self.name) from exc
        if not text.strip():                                          # P4-02, same rule here
            raise ProviderError(
                f"{self.name}: the request succeeded but returned no text "
                f"(stop_reason={data.get('stop_reason')!r}).", provider=self.name)
        u = data.get("usage") or {}
        inp, out = int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0)
        return Completion(text=text, model=data.get("model") or self.model, provider=self.name,
                          usage=Usage(inp, out, inp + out), raw=data)


def build_provider(name: str | None = None, env: dict | None = None):
    """Build one provider from the §3 environment contract. No key is ever defaulted."""
    env = os.environ if env is None else env
    name = (name or env.get("PROVIDER") or "atk").strip().lower()
    if name not in PROVIDERS:
        raise ConfigError(
            f"PROVIDER={name!r} is not one of {sorted(PROVIDERS)}. Refusing to guess: silently "
            "falling back to a default provider would send your prompt somewhere you did not ask "
            "for.")
    prefix, wire = PROVIDERS[name]
    # P4-03: the official ATK docs name the variable AITOKENKING_API_KEY; this repository's
    # contract (ATK_ROUTING_INTEGRATION.md §3) names it ATK_API_KEY. Rather than make the reader
    # guess, ATK_API_KEY is the documented name here and the official spelling is accepted as an
    # alias. The mapping is stated in .env.example and README.
    key = env.get(f"{prefix}_API_KEY") or ""
    if not key and name == "atk":
        key = env.get("AITOKENKING_API_KEY") or ""
    base = env.get(f"{prefix}_BASE_URL") or ""
    model = env.get(f"{prefix}_MODEL") or ""
    missing = [n for n, v in (("API_KEY", key), ("BASE_URL", base), ("MODEL", model)) if not v]
    if missing:
        raise ConfigError(
            f"PROVIDER={name} needs " + ", ".join(f"{prefix}_{m}" for m in missing) +
            ". Copy .env.example and fill it in. No value here is guessed or hardcoded, so an "
            "incomplete configuration fails before a request is sent rather than after.")
    timeout = int(env.get("REQUEST_TIMEOUT_SECONDS") or DEFAULT_TIMEOUT)
    # Off by default: a provider's error prose may echo the credential it rejected (P4-01).
    include_body = str(env.get("ATK_INCLUDE_ERROR_BODY") or "").strip().lower() in ("1", "true", "yes")
    if wire == "anthropic":
        return AnthropicProvider(name, key, base, model, timeout,
                                 include_error_body=include_body)
    return OpenAICompatibleProvider(name, key, base, model, timeout,
                                    include_error_body=include_body)


def _chain(env: dict) -> list[str]:
    primary = (env.get("PROVIDER") or "atk").strip().lower()
    extra = [p.strip().lower() for p in (env.get("FALLBACK_PROVIDERS") or "").split(",") if p.strip()]
    seen, out = set(), []
    for p in [primary, *extra]:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def complete(messages: Iterable[Message], *, env: dict | None = None, **kwargs) -> Completion:
    """Send one request, honouring PROVIDER, FALLBACK_PROVIDERS and MAX_RETRIES.

    A provider that is misconfigured is **skipped**, not retried: a missing key will still be
    missing on the third attempt. A provider that is reachable but failing is retried up to
    `MAX_RETRIES`. If everything fails, the error names every provider tried and why, because
    "all providers failed" is not a debuggable message.
    """
    env = os.environ if env is None else env
    messages = list(messages)
    retries = max(1, int(env.get("MAX_RETRIES") or DEFAULT_RETRIES))
    problems: list[str] = []
    # P4-01: every configured key, so the summary below cannot reassemble a secret that an
    # individual adapter already redacted from its own message.
    secrets = [v for k, v in env.items()
               if k.endswith("_API_KEY") and isinstance(v, str) and v]

    for name in _chain(env):
        try:
            provider = build_provider(name, env)
        except ConfigError as exc:
            problems.append(f"{name}: not configured ({exc})")
            continue
        for attempt in range(1, retries + 1):
            try:
                return provider.complete(messages, **kwargs)
            except ProviderError as exc:
                problems.append(f"{name} attempt {attempt}/{retries}: {exc}")
                # 4xx other than 408/429 is the caller's fault and will not improve with time.
                if exc.status and exc.status < 500 and exc.status not in (408, 429):
                    break
                if attempt < retries:
                    time.sleep(min(2 ** (attempt - 1), 8))
    raise ProviderError(
        redact("every configured provider failed:\n  " + "\n  ".join(problems), secrets),
        provider="none")
