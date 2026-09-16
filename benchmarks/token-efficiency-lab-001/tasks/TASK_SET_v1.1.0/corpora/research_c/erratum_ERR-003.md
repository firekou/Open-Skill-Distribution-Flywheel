# Erratum ERR-003

Publisher: Kestrel Runtime Project (official)  
Published: 2032-02-20  
Source tier: erratum

The release notes for Kestrel Runtime 1.0 state that the feature flag `parallel_compaction` was added in that release. That statement is incorrect.

The flag `parallel_compaction` was added in Kestrel Runtime 2.1. No other statement in those release notes is affected by this erratum.

Packaging for the container images follows the same tagging convention as before. The health endpoint continues to report readiness separately from liveness. Deployments behind a strict egress policy should confirm the updated destination list. A small number of log lines changed wording; parsers keying on the message text may need updating. Feedback from the early-access cohort has been folded into the final behaviour. No change is required for deployments that do not enable the optional subsystem. Contributors are reminded that behavioural changes need an entry in the change log. Questions about licensing are handled by the project stewards, not by this document. The migration guide covers the rollback path in more detail than this note.
