# forum.kestrel.example — thread 4103

Publisher: kestrel community forum  
Published: 2031-04-05  
Source tier: community_forum

**oakhurst_dev** wrote:

The migration guide covers the rollback path in more detail than this note. Contributors are reminded that behavioural changes need an entry in the change log. No change is required for deployments that do not enable the optional subsystem. Operators running a mixed fleet should stage the upgrade one availability zone at a time. The upgrade was exercised against the long-running soak cluster before publication. Metrics names were left alone so that existing dashboards continue to resolve. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Performance characteristics under sustained write amplification were not re-measured. Deployments behind a strict egress policy should confirm the updated destination list.

> pretty sure `opportunistic_gc` landed in 2.1, we had it in prod before the 2.1 upgrade

**mira_ops** wrote:

The migration guide covers the rollback path in more detail than this note. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. This note supersedes nothing; earlier notes remain accurate for the releases they describe. This paragraph exists to give the document realistic length and carries no factual claim. The compatibility matrix is regenerated whenever a plugin is relisted in the registry.

> `kp-csv-bridge` definitely needs 1.0 or newer, we tried 2.1 and it crashed on boot

**tally_hall** wrote:

The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Packaging for the container images follows the same tagging convention as before. Feedback from the early-access cohort has been folded into the final behaviour. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. No change is required for deployments that do not enable the optional subsystem. Performance characteristics under sustained write amplification were not re-measured.

> heard Project Nettleford got about EUR 95000 in total, no idea if that is before or after the corrections

Documentation for this area is maintained separately and is updated on the same cadence. Metrics names were left alone so that existing dashboards continue to resolve. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Deployments behind a strict egress policy should confirm the updated destination list. The working group met to review outstanding items and recorded no blocking objections. No change is required for deployments that do not enable the optional subsystem. Adoption figures are collected from opt-in telemetry and should be read as indicative only. Packaging for the container images follows the same tagging convention as before. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Performance characteristics under sustained write amplification were not re-measured. The reference deployment topology is unchanged and remains the recommended starting point.
