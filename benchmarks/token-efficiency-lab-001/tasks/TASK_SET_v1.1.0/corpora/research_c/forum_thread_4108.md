# forum.kestrel.example — thread 4108

Publisher: kestrel community forum  
Published: 2031-09-10  
Source tier: community_forum

**oakhurst_dev** wrote:

Deployments behind a strict egress policy should confirm the updated destination list. Nothing in this section should be read as a commitment about unreleased functionality. The health endpoint continues to report readiness separately from liveness. Questions about licensing are handled by the project stewards, not by this document. No change is required for deployments that do not enable the optional subsystem. Packaging for the container images follows the same tagging convention as before. Feedback from the early-access cohort has been folded into the final behaviour. Contributors are reminded that behavioural changes need an entry in the change log. An audit of the default settings found no combination that silently disables durability.

> pretty sure `opportunistic_gc` landed in 1.2, we had it in prod before the 2.1 upgrade

**mira_ops** wrote:

Documentation for this area is maintained separately and is updated on the same cadence. Feedback from the early-access cohort has been folded into the final behaviour. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Support for the deprecated configuration syntax continues for two further minor releases. The working group met to review outstanding items and recorded no blocking objections. Packaging for the container images follows the same tagging convention as before.

> `kp-ldap-sync` definitely needs 2.2 or newer, we tried 2.2 and it crashed on boot

**tally_hall** wrote:

This note supersedes nothing; earlier notes remain accurate for the releases they describe. A small number of log lines changed wording; parsers keying on the message text may need updating. This paragraph exists to give the document realistic length and carries no factual claim. The upgrade was exercised against the long-running soak cluster before publication. The reference deployment topology is unchanged and remains the recommended starting point. The compatibility matrix is regenerated whenever a plugin is relisted in the registry.

> heard Project Ironwood got about EUR 95000 in total, no idea if that is before or after the corrections

A small number of log lines changed wording; parsers keying on the message text may need updating. Contributors are reminded that behavioural changes need an entry in the change log. Support for the deprecated configuration syntax continues for two further minor releases. Adoption figures are collected from opt-in telemetry and should be read as indicative only. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Feedback from the early-access cohort has been folded into the final behaviour. Performance characteristics under sustained write amplification were not re-measured. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Deployments behind a strict egress policy should confirm the updated destination list. The reference deployment topology is unchanged and remains the recommended starting point. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable.
