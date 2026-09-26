# Kestrel Runtime 2.2 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2030-10-16  
Source tier: official_release_notes

## Summary

Adoption figures are collected from opt-in telemetry and should be read as indicative only. Contributors are reminded that behavioural changes need an entry in the change log. Nothing in this section should be read as a commitment about unreleased functionality. Feedback from the early-access cohort has been folded into the final behaviour. The health endpoint continues to report readiness separately from liveness. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Questions about licensing are handled by the project stewards, not by this document. The reference deployment topology is unchanged and remains the recommended starting point. No change is required for deployments that do not enable the optional subsystem. Packaging for the container images follows the same tagging convention as before. The migration guide covers the rollback path in more detail than this note. A small number of log lines changed wording; parsers keying on the message text may need updating. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. An audit of the default settings found no combination that silently disables durability.

## Feature flags

The following feature flags are **added** in this release:

- `adaptive_shard_split` — new in 2.2, disabled by default.
- `hinted_route_table` — new in 2.2, disabled by default.
- `opportunistic_gc` — new in 2.2, disabled by default.

## Other changes

Operators running a mixed fleet should stage the upgrade one availability zone at a time. Questions about licensing are handled by the project stewards, not by this document. The health endpoint continues to report readiness separately from liveness. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. The working group met to review outstanding items and recorded no blocking objections. Performance characteristics under sustained write amplification were not re-measured. This paragraph exists to give the document realistic length and carries no factual claim. Nothing in this section should be read as a commitment about unreleased functionality. Metrics names were left alone so that existing dashboards continue to resolve. An audit of the default settings found no combination that silently disables durability. Documentation for this area is maintained separately and is updated on the same cadence. Support for the deprecated configuration syntax continues for two further minor releases. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. No change is required for deployments that do not enable the optional subsystem. Adoption figures are collected from opt-in telemetry and should be read as indicative only. The migration guide covers the rollback path in more detail than this note. Feedback from the early-access cohort has been folded into the final behaviour. Packaging for the container images follows the same tagging convention as before.

## Known issues

Nothing in this section should be read as a commitment about unreleased functionality. A small number of log lines changed wording; parsers keying on the message text may need updating. This paragraph exists to give the document realistic length and carries no factual claim. Metrics names were left alone so that existing dashboards continue to resolve. Support for the deprecated configuration syntax continues for two further minor releases. The upgrade was exercised against the long-running soak cluster before publication. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. An audit of the default settings found no combination that silently disables durability. Packaging for the container images follows the same tagging convention as before. Deployments behind a strict egress policy should confirm the updated destination list. Feedback from the early-access cohort has been folded into the final behaviour. No change is required for deployments that do not enable the optional subsystem.
