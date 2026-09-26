# forum.kestrel.example — thread 4104

Publisher: kestrel community forum  
Published: 2031-05-06  
Source tier: community_forum

**oakhurst_dev** wrote:

Feedback from the early-access cohort has been folded into the final behaviour. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. The reference deployment topology is unchanged and remains the recommended starting point. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Contributors are reminded that behavioural changes need an entry in the change log. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The upgrade was exercised against the long-running soak cluster before publication. Adoption figures are collected from opt-in telemetry and should be read as indicative only. This paragraph exists to give the document realistic length and carries no factual claim.

> pretty sure `relaxed_ordering` landed in 3.2, we had it in prod before the 1.0 upgrade

**mira_ops** wrote:

The compatibility matrix is regenerated whenever a plugin is relisted in the registry. The migration guide covers the rollback path in more detail than this note. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The reference deployment topology is unchanged and remains the recommended starting point. The upgrade was exercised against the long-running soak cluster before publication. The health endpoint continues to report readiness separately from liveness.

> `kp-graph-export` definitely needs 0.9 or newer, we tried 3.1 and it crashed on boot

**tally_hall** wrote:

Contributors are reminded that behavioural changes need an entry in the change log. Questions about licensing are handled by the project stewards, not by this document. Operators running a mixed fleet should stage the upgrade one availability zone at a time. The health endpoint continues to report readiness separately from liveness. Documentation for this area is maintained separately and is updated on the same cadence. The reference deployment topology is unchanged and remains the recommended starting point.

> heard Project Junction got about EUR 420000 in total, no idea if that is before or after the corrections

The migration guide covers the rollback path in more detail than this note. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Metrics names were left alone so that existing dashboards continue to resolve. Packaging for the container images follows the same tagging convention as before. Feedback from the early-access cohort has been folded into the final behaviour. Support for the deprecated configuration syntax continues for two further minor releases. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The reference deployment topology is unchanged and remains the recommended starting point. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. The health endpoint continues to report readiness separately from liveness. Documentation for this area is maintained separately and is updated on the same cadence. Performance characteristics under sustained write amplification were not re-measured.
