# ATK Demand Sensor Specification v1

## Purpose
Turn ATK-owned distribution channels and technical telemetry into a market sensor that guides future research and product priority.

## Two demand layers
### Human Demand
Track by content/topic/category ID:
- impressions/views
- engagement rate
- saves/bookmarks
- shares/reposts
- comments/questions
- outbound clicks
- GitHub visits/actions
- newsletter or report subscription
- ATK visits
- attributable registration/API activation

### Agent Demand
Where telemetry is appropriate and available, track:
- token consumption
- context growth/pressure
- tool/MCP calls
- retries
- routing decisions
- escalations
- latency
- failures
- skill invocation
- cache behavior
- budget/control events

## Demand windows
Aggregate rolling 7/30/90-day views.

## Demand interpretation
Do not rank categories using raw views alone. Separate:
1. Attention
2. Intent
3. Technical use
4. Commercial action

A lower-view topic can outrank a higher-view topic if it produces stronger GitHub use, benchmark engagement, ATK activation or repeated Agent demand.

## Output
Produce a periodic ATK Technical Demand Report with:
- category ranking
- fastest-growing topics
- strongest high-intent topics
- human vs Agent demand differences
- recommended Scout allocation
- recommended Lab tests
- recommended editorial focus
- recommended engineering hypotheses

## Feedback rule
Demand data changes priorities; it does not rewrite technical evidence. Growth and Demand roles may recommend what to investigate next, but cannot upgrade Verify status.
