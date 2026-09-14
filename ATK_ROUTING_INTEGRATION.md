# ATK_ROUTING_INTEGRATION.md

> ATK Routing Integration Contract · Version 1.0 · Last updated: 2026-09-14

---

## 1. Principle

ATK Routing is the commercial layer of the Open Skill Distribution Strategy. It is also the
part most likely to destroy the strategy if implemented dishonestly.

> **ATK may be the default. ATK may never be the only option.**

Four properties, all enforced by the QA gate:

| Property | Test |
|---|---|
| **Transparent** | The user can see which provider handled each request |
| **Replaceable** | Switching to a non-ATK provider takes one config change and works |
| **Documented** | `docs/ROUTING.md` explains switching *away* from ATK, prominently |
| **Optional** | The skill runs end to end with ATK fully removed |

A fork that fails any of these does not ship. Locking a provider would convert ATK's
distribution advantage into the reason developers avoid ATK forks — the one outcome the
strategy cannot survive.

---

## 2. Architecture

```
          Skill / Agent / MCP Server
                     │
                     ▼
        ┌─────────────────────────┐
        │   Provider Interface    │   ← stable seam; the only thing the skill knows about
        └─────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │        Router           │   ← selection, fallback, budget, tracking
        └─────────────────────────┘
             │         │        │
             ▼         ▼        ▼
         ATK Router  OpenAI  Anthropic  Gemini  DeepSeek  Qwen  OpenRouter  custom
             │
             ▼
   OpenAI · Anthropic · Gemini · DeepSeek · Qwen · ByteDance · …
```

The skill never imports a vendor SDK directly. It depends only on the Provider Interface.
That single rule is what makes every other property achievable.

---

## 3. Configuration Contract

Every ATK fork exposes the same variables. `.env.example` must document all of them.

```bash
# ── Provider selection ────────────────────────────────────────────────
# atk | openai | anthropic | gemini | deepseek | qwen | openrouter | custom
PROVIDER=atk

# ── ATK (default Quick Start path) ────────────────────────────────────
ATK_API_KEY=
ATK_BASE_URL=https://api.aitokenking.com/v1
ATK_MODEL=

# ── Any other provider — used when PROVIDER != atk ────────────────────
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=

ANTHROPIC_API_KEY=
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=

# ── Routing behaviour ─────────────────────────────────────────────────
FALLBACK_PROVIDERS=            # comma-separated, tried in order
MAX_RETRIES=3
REQUEST_TIMEOUT_SECONDS=120

# ── Cost controls (off unless set) ────────────────────────────────────
TOKEN_BUDGET_PER_RUN=
COST_BUDGET_USD_PER_RUN=
TRACK_USAGE=true
```

Rules:

1. `PROVIDER=atk` is the **default**, because Quick Start must work in one step.
2. Changing `PROVIDER` to anything else must require **no code edit**.
3. ATK variables must be **absent-safe**: with no `ATK_API_KEY` and `PROVIDER=openai`, the
   skill runs normally.
4. No ATK key, URL or model may be **hardcoded** anywhere in the source tree.

---

## 4. Provider Interface

The minimum contract every adapter implements.

```python
from dataclasses import dataclass, field
from typing import Iterator, Protocol

@dataclass
class Message:
    role: str                       # "system" | "user" | "assistant" | "tool"
    content: str

@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float | None = None

@dataclass
class Completion:
    text: str
    model: str
    provider: str                   # which adapter actually served this
    usage: Usage = field(default_factory=Usage)
    raw: dict | None = None

class Provider(Protocol):
    name: str

    def complete(
        self,
        messages: list[Message],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> Completion: ...

    def stream(
        self,
        messages: list[Message],
        **kwargs,
    ) -> Iterator[str]: ...

    def health(self) -> bool: ...
```

`Completion.provider` is what makes **Transparent** testable rather than aspirational — the
caller can always see who served the request.

---

## 5. Reference ATK Adapter

ATK exposes an OpenAI-compatible API, so the adapter is thin by design. Thin is the point:
it is an additive file, which keeps `invasive_change_ratio` low (see `UPSTREAM_SYNC.md` §7).

```python
# src/providers/atk.py  — ADDITIVE: new file, no upstream file modified
import os
import httpx
from .base import Provider, Message, Completion, Usage


class ATKProvider(Provider):
    """AI Token King routing provider (OpenAI-compatible)."""

    name = "atk"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ):
        self.api_key = api_key or os.getenv("ATK_API_KEY")
        self.base_url = (
            base_url
            or os.getenv("ATK_BASE_URL")
            or "https://api.aitokenking.com/v1"
        ).rstrip("/")
        self.model = model or os.getenv("ATK_MODEL")
        self.timeout = timeout or float(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))

        if not self.api_key:
            raise ValueError(
                "ATK_API_KEY is not set.\n"
                "Either set it, or choose another provider with PROVIDER=openai "
                "(see docs/ROUTING.md)."
            )

    def complete(self, messages, *, model=None, temperature=0.7,
                 max_tokens=None, **kwargs) -> Completion:
        payload = {
            "model": model or self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        payload.update(kwargs)

        r = httpx.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        u = data.get("usage", {}) or {}

        return Completion(
            text=data["choices"][0]["message"]["content"],
            model=data.get("model", payload["model"]),
            provider=self.name,
            usage=Usage(
                prompt_tokens=u.get("prompt_tokens", 0),
                completion_tokens=u.get("completion_tokens", 0),
                total_tokens=u.get("total_tokens", 0),
                cost_usd=u.get("cost_usd"),
            ),
            raw=data,
        )

    def health(self) -> bool:
        try:
            r = httpx.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            return r.status_code == 200
        except Exception:
            return False
```

**Note the error message.** When ATK is misconfigured, the adapter points the user at the
alternative. That is the Routing Principle expressed in code rather than in a policy
document.

---

## 6. Router

```python
# src/providers/router.py — ADDITIVE
import os
from .registry import get_provider     # one-line hook into upstream, if any

class Router:
    def __init__(self, primary=None, fallbacks=None, token_budget=None):
        self.primary = primary or os.getenv("PROVIDER", "atk")
        self.fallbacks = fallbacks or [
            p.strip()
            for p in os.getenv("FALLBACK_PROVIDERS", "").split(",")
            if p.strip()
        ]
        self.token_budget = token_budget or _int_env("TOKEN_BUDGET_PER_RUN")
        self.spent = 0

    def complete(self, messages, **kwargs):
        errors = []
        for name in [self.primary, *self.fallbacks]:
            try:
                provider = get_provider(name)
            except Exception as e:                 # not configured — skip, don't fail
                errors.append((name, e))
                continue

            try:
                result = provider.complete(messages, **kwargs)
            except Exception as e:
                errors.append((name, e))
                continue

            self.spent += result.usage.total_tokens
            if self.token_budget and self.spent > self.token_budget:
                raise BudgetExceeded(
                    f"Token budget exceeded: {self.spent}/{self.token_budget}"
                )
            return result

        raise AllProvidersFailed(errors)
```

Budget is checked **after** the call that crossed the line, so the run stops at the boundary
rather than silently continuing. Callers that need a hard pre-flight cap should pass
`max_tokens` as well.

---

## 7. Required Documentation

`docs/ROUTING.md` in every ATK fork, and it must lead with switching *away*:

```markdown
# Routing

This distribution ships with ATK Routing as the default so Quick Start works in one step.
**You are not required to use it.**

## Use your own provider

    PROVIDER=openai
    OPENAI_API_KEY=sk-...

That's the whole change. No code edits.

## Use ATK

    PROVIDER=atk
    ATK_API_KEY=...

## Remove ATK entirely

Delete `src/providers/atk.py` and drop `atk` from the provider registry.
Nothing else depends on it.

## Which provider served my request?

Every response carries `completion.provider`. Set `TRACK_USAGE=true` to log
provider, model, tokens and cost per call.
```

That last section is not a courtesy — it is the auditable form of "Transparent".

---

## 8. QA Gate

| # | Test | Required result |
|---|---|---|
| 1 | Default path | `PROVIDER` unset → ATK used, Quick Start succeeds |
| 2 | **Switch away** | `PROVIDER=openai` → works, zero code changes |
| 3 | **ATK removed** | ATK adapter deleted → project still builds and runs |
| 4 | Fallback | Primary fails → fallback serves, and this is logged |
| 5 | Transparency | `completion.provider` is correct in every case |
| 6 | Budget | Exceeding `TOKEN_BUDGET_PER_RUN` raises, not truncates |
| 7 | No hardcoding | `grep -ri "aitokenking\|ATK_API_KEY" src/` finds only the adapter and config |
| 8 | No key leakage | No real key in `.env.example`, tests, docs or git history |

Tests **2 and 3 are the ones that matter**. They are the difference between "ATK is the
default" and "ATK is locked in", and they are cheap to run — so they run on every release.

---

## 9. Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Hardcoding `ATK_BASE_URL` in source | Breaks Replaceable; and it will be noticed |
| ATK-only features (e.g. caching only on ATK) | Coercion disguised as a feature |
| Silent ATK fallback when another provider fails | Sends the user's data somewhere they did not choose |
| Removing upstream's original provider support | Turns a distribution into a hostage |
| Burying provider switching in a wiki footnote | Technically documented, practically hidden |
| Telemetry to ATK by default | Undisclosed egress; a security-review failure |

The pattern across all six: each one buys a small amount of short-term conversion by
spending the developer trust the distribution model depends on. That trade is never
positive for ATK.
