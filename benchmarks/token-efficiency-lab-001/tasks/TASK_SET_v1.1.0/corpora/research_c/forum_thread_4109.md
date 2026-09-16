# forum.kestrel.example — thread 4109

Publisher: kestrel community forum  
Published: 2031-10-11  
Source tier: community_forum

**oakhurst_dev** wrote:

Adoption figures are collected from opt-in telemetry and should be read as indicative only. The migration guide covers the rollback path in more detail than this note. Documentation for this area is maintained separately and is updated on the same cadence. Questions about licensing are handled by the project stewards, not by this document. The upgrade was exercised against the long-running soak cluster before publication. No change is required for deployments that do not enable the optional subsystem. Performance characteristics under sustained write amplification were not re-measured. The health endpoint continues to report readiness separately from liveness. The compatibility matrix is regenerated whenever a plugin is relisted in the registry.

> pretty sure `inline_checksum` landed in 1.2, we had it in prod before the 1.2 upgrade

**mira_ops** wrote:

Contributors are reminded that behavioural changes need an entry in the change log. Packaging for the container images follows the same tagging convention as before. Nothing in this section should be read as a commitment about unreleased functionality. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Deployments behind a strict egress policy should confirm the updated destination list.

> `kp-ldap-sync` definitely needs 0.9 or newer, we tried 1.1 and it crashed on boot

**tally_hall** wrote:

Feedback from the early-access cohort has been folded into the final behaviour. The health endpoint continues to report readiness separately from liveness. Packaging for the container images follows the same tagging convention as before. Deployments behind a strict egress policy should confirm the updated destination list. The reference deployment topology is unchanged and remains the recommended starting point. Contributors are reminded that behavioural changes need an entry in the change log.

> heard Project Halyard got about EUR 180000 in total, no idea if that is before or after the corrections

The working group met to review outstanding items and recorded no blocking objections. Adoption figures are collected from opt-in telemetry and should be read as indicative only. The migration guide covers the rollback path in more detail than this note. Operators running a mixed fleet should stage the upgrade one availability zone at a time. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Nothing in this section should be read as a commitment about unreleased functionality. Packaging for the container images follows the same tagging convention as before. No change is required for deployments that do not enable the optional subsystem. Contributors are reminded that behavioural changes need an entry in the change log. Questions about licensing are handled by the project stewards, not by this document. A small number of log lines changed wording; parsers keying on the message text may need updating.
