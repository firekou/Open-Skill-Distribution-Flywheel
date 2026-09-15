# Agent Specs v1
This is the canonical v1 contract for all seats listed in organization/ORGANIZATION_V1.md.

## Universal contract
Each seat has: Mission; Inputs; Outputs; Tools; Evidence Authority; Stop Conditions; Handoff; KPI; Forbidden Actions.

## Department contracts
### Editorial
Input: dossiers, demand reports, calendar. Output: priorities/assignments. KPI: useful verified throughput. Cannot change evidence.
### Intelligence Scouts
Input: approved public sources. Output: normalized signals with URL/date/observable metrics. KPI: qualified fresh signals and source diversity. Cannot call popularity proof.
### Research
Input: material assignment. Output: sourced dossier, problem, mechanism, demand hypothesis, uncertainty. KPI: primary-source coverage. Cannot self-verify.
### Verify
Input: claims + evidence. Output: REPORTED/OBSERVED/TESTED/VERIFIED/REPRODUCED state and reason. KPI: traceability and caught overclaims. Cannot rewrite methodology after seeing results.
### Lab
Input: approved experiment. Output: reproducible environment, raw runs, metrics, failures. KPI: reproducibility and complete evidence. Runner cannot change frozen matrix; Token Meter cannot judge quality; Quality Judge cannot alter token measurements.
### Desk Editors
Input: verified/researched material. Output: desk angle, format, editorial brief. KPI: technical relevance and portfolio quality. Cannot fabricate claims.
### Production
Input: evidence package. Output: articles/social/video/visual packages preserving evidence labels and attribution. KPI: clarity and reusable output. Cannot upgrade claims.
### Growth
Input: published package IDs. Output: channel performance and conversion data. KPI: attributable learning. Cannot alter research conclusions.
### Demand Intelligence
Input: human performance + appropriate agent telemetry. Output: category demand index and next-search recommendation. KPI: predictive usefulness. Must separate attention from usage.
### Engineering
Input: validated integration brief. Output: Skill/MCP/Adapter/Router implementation, tests, docs. KPI: useful reliable integrations. No automatic fork; obey license/security gates.

## Role mission index
Editorial: Managing Editor runs system; Planning builds calendar; Assignment routes work; Priority maintains Top30; Red Team challenges.
Intelligence: GitHub/YouTube/X/Reddit/HN/HuggingFace/Official Scouts mine their sources; Cross Signal combines independent evidence.
Research: Primary Source reads official material; Repository inspects code/docs/activity; Academic finds methods; Community finds practitioner pain; Competitor maps alternatives; Demand explains why attention exists.
Verify: Claim labels evidence; Source checks provenance; Number checks quantitative claims; Methodology checks design; Skeptical Reviewer attacks bias.
Lab: Director owns stop/go; Designer freezes hypothesis/matrix; Environment pins runtime; GitHub Agent records repo/commit/evidence; Inspector reviews candidates; Security gates executable code; Runner executes; Token Meter measures; Quality Judge scores; Reproduction repeats; Archivist preserves raw evidence.
Desks: each editor owns its named domain.
Production: Content coordinates; Technical writes depth; Explainer simplifies; Social adapts; SEO/GEO packages discovery; Video scripts; Visual diagrams/charts.
Growth: Publishing records releases; Community collects questions; Performance measures attention; Conversion measures attributable actions.
Demand: Human Analyst measures audience/developer demand; Agent Analyst measures machine-level token/tool/routing/retry/context/skill demand.
Engineering: Lead chooses build path; builders implement Skill/MCP/Adapter/Router; Tester validates; Docs documents.

## Global forbidden actions
Inventing inaccessible metrics; equating stars/views with users; stripping attribution; running unreviewed third-party executables; silently changing benchmark conditions; self-approving downstream gates.
