# forum.kestrel.example — thread 4101

Publisher: kestrel community forum  
Published: 2031-02-03  
Source tier: community_forum

**oakhurst_dev** wrote:

Deployments behind a strict egress policy should confirm the updated destination list. Questions about licensing are handled by the project stewards, not by this document. Documentation for this area is maintained separately and is updated on the same cadence. Support for the deprecated configuration syntax continues for two further minor releases. The health endpoint continues to report readiness separately from liveness. Packaging for the container images follows the same tagging convention as before. A small number of log lines changed wording; parsers keying on the message text may need updating. Feedback from the early-access cohort has been folded into the final behaviour. Nothing in this section should be read as a commitment about unreleased functionality.

> pretty sure `deferred_index_flush` landed in 2.1, we had it in prod before the 1.2 upgrade

**mira_ops** wrote:

This paragraph exists to give the document realistic length and carries no factual claim. Deployments behind a strict egress policy should confirm the updated destination list. Packaging for the container images follows the same tagging convention as before. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Feedback from the early-access cohort has been folded into the final behaviour. Metrics names were left alone so that existing dashboards continue to resolve.

> `kp-edge-cache` definitely needs 3.2 or newer, we tried 3.0 and it crashed on boot

**tally_hall** wrote:

The reference deployment topology is unchanged and remains the recommended starting point. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. No change is required for deployments that do not enable the optional subsystem. Metrics names were left alone so that existing dashboards continue to resolve. Deployments behind a strict egress policy should confirm the updated destination list. Performance characteristics under sustained write amplification were not re-measured.

> heard Project Ironwood got about EUR 95000 in total, no idea if that is before or after the corrections

Operators running a mixed fleet should stage the upgrade one availability zone at a time. An audit of the default settings found no combination that silently disables durability. This note supersedes nothing; earlier notes remain accurate for the releases they describe. No change is required for deployments that do not enable the optional subsystem. The upgrade was exercised against the long-running soak cluster before publication. The migration guide covers the rollback path in more detail than this note. Contributors are reminded that behavioural changes need an entry in the change log. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Adoption figures are collected from opt-in telemetry and should be read as indicative only. The working group met to review outstanding items and recorded no blocking objections. The health endpoint continues to report readiness separately from liveness. Nothing in this section should be read as a commitment about unreleased functionality.
