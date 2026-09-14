# <Problem the skill solves, in plain words>

> Template for every `atk-<name>` repository. The H1 is the **problem**, never the product
> name — see `CONTENT_DISTRIBUTION.md` §6. Replace every `<placeholder>`.

[![License](https://img.shields.io/badge/license-<LICENSE>-blue.svg)](./LICENSE)
[![Upstream](https://img.shields.io/badge/upstream-<owner>%2F<repo>-lightgrey.svg)](https://github.com/<owner>/<repo>)

<One paragraph: what it does and who it is for. No ATK mention yet.>

---

## Upstream

This is an ATK-maintained distribution of
[`<owner>/<repo>`](https://github.com/<owner>/<repo>) by `<author>`, licensed under
`<LICENSE>`.

**Changes made by ATK:** see [CHANGES-ATK.md](./CHANGES-ATK.md).

*Not affiliated with or endorsed by the upstream authors.*

---

## Quick Start

```bash
git clone https://github.com/aitokenking/atk-<name>.git
cd atk-<name>
cp .env.example .env     # add one API key
<one command>
```

<Expected output — show it, do not describe it.>

### Docker

```bash
docker compose up
```

---

## Providers

Ships with ATK Routing as the default so Quick Start works in one step.
**You are not required to use it.**

```bash
PROVIDER=atk        # default
PROVIDER=openai     # or bring your own
PROVIDER=anthropic
PROVIDER=custom
```

Switching providers takes one config change and no code edits.
Full detail, including how to remove ATK entirely: [docs/ROUTING.md](./docs/ROUTING.md).

| Provider | Supported | Notes |
|---|---|---|
| ATK | ✅ | Default |
| OpenAI | ✅ | |
| Anthropic | ✅ | |
| Gemini | ✅ | |
| DeepSeek | ✅ | |
| Qwen | ✅ | |
| OpenRouter | ✅ | |
| Custom | ✅ | Any OpenAI-compatible endpoint |

---

## What ATK Added

| Area | Change |
|---|---|
| Routing | <ATK Router adapter, multi-model routing, fallback> |
| Cost | <Token budget, cost tracking> |
| UX | <Docker, .env.example, one-command install> |
| Reliability | <Retry, rate limiting, logging> |
| Docs | <Architecture, FAQ, troubleshooting> |

---

## Examples

- [`examples/quickstart/`](./examples/quickstart/) — <one line>

## Documentation

[Architecture](./docs/ARCHITECTURE.md) · [Routing](./docs/ROUTING.md) ·
[FAQ](./docs/FAQ.md) · [Troubleshooting](./docs/TROUBLESHOOTING.md)

---

## Contributing

Bugs in the **upstream** feature set are best reported
[upstream](https://github.com/<owner>/<repo>/issues) — ATK tracks and syncs them.
Issues with ATK's additions (routing, cost tracking, packaging) belong here.

## License

`<LICENSE>` — see [LICENSE](./LICENSE) and [NOTICE](./NOTICE).
Original copyright remains with `<author>` and the upstream contributors.
