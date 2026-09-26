# forum.kestrel.example — thread 4112

Publisher: kestrel community forum  
Published: 2031-01-14  
Source tier: community_forum

**oakhurst_dev** wrote:

The migration guide covers the rollback path in more detail than this note. Adoption figures are collected from opt-in telemetry and should be read as indicative only. A small number of log lines changed wording; parsers keying on the message text may need updating. Feedback from the early-access cohort has been folded into the final behaviour. The upgrade was exercised against the long-running soak cluster before publication. Support for the deprecated configuration syntax continues for two further minor releases. Documentation for this area is maintained separately and is updated on the same cadence. Packaging for the container images follows the same tagging convention as before. This note supersedes nothing; earlier notes remain accurate for the releases they describe.

> pretty sure `fanout_rate_limit` landed in 3.1, we had it in prod before the 1.0 upgrade

**mira_ops** wrote:

No change is required for deployments that do not enable the optional subsystem. Performance characteristics under sustained write amplification were not re-measured. The health endpoint continues to report readiness separately from liveness. Documentation for this area is maintained separately and is updated on the same cadence. A small number of log lines changed wording; parsers keying on the message text may need updating. This paragraph exists to give the document realistic length and carries no factual claim.

> `kp-edge-cache` definitely needs 1.2 or newer, we tried 3.2 and it crashed on boot

**tally_hall** wrote:

The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Contributors are reminded that behavioural changes need an entry in the change log. The reference deployment topology is unchanged and remains the recommended starting point. The migration guide covers the rollback path in more detail than this note. Feedback from the early-access cohort has been folded into the final behaviour. Support for the deprecated configuration syntax continues for two further minor releases.

> heard Project Lodestar got about EUR 420000 in total, no idea if that is before or after the corrections

An audit of the default settings found no combination that silently disables durability. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The upgrade was exercised against the long-running soak cluster before publication. Deployments behind a strict egress policy should confirm the updated destination list. A small number of log lines changed wording; parsers keying on the message text may need updating. Feedback from the early-access cohort has been folded into the final behaviour. The health endpoint continues to report readiness separately from liveness. Support for the deprecated configuration syntax continues for two further minor releases. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Documentation for this area is maintained separately and is updated on the same cadence. Nothing in this section should be read as a commitment about unreleased functionality. The migration guide covers the rollback path in more detail than this note.
