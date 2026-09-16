# Kestrel Runtime 1.1 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2029-09-19  
Source tier: official_release_notes

## Summary

The upgrade was exercised against the long-running soak cluster before publication. Documentation for this area is maintained separately and is updated on the same cadence. A small number of log lines changed wording; parsers keying on the message text may need updating. Questions about licensing are handled by the project stewards, not by this document. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Nothing in this section should be read as a commitment about unreleased functionality. This paragraph exists to give the document realistic length and carries no factual claim. An audit of the default settings found no combination that silently disables durability. The health endpoint continues to report readiness separately from liveness. No change is required for deployments that do not enable the optional subsystem. Feedback from the early-access cohort has been folded into the final behaviour. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Support for the deprecated configuration syntax continues for two further minor releases. Performance characteristics under sustained write amplification were not re-measured. The working group met to review outstanding items and recorded no blocking objections.

## Feature flags

The following feature flags are **added** in this release:

- `eager_tenant_cache` — new in 1.1, disabled by default.
- `fanout_rate_limit` — new in 1.1, disabled by default.

The following feature flags are **removed** in this release and no longer have any effect:

- `batch_ack_window` — removed in 1.1.

## Other changes

Nothing in this section should be read as a commitment about unreleased functionality. Deployments behind a strict egress policy should confirm the updated destination list. Support for the deprecated configuration syntax continues for two further minor releases. A small number of log lines changed wording; parsers keying on the message text may need updating. Documentation for this area is maintained separately and is updated on the same cadence. Packaging for the container images follows the same tagging convention as before. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. The reference deployment topology is unchanged and remains the recommended starting point. This paragraph exists to give the document realistic length and carries no factual claim. Performance characteristics under sustained write amplification were not re-measured. Feedback from the early-access cohort has been folded into the final behaviour. Questions about licensing are handled by the project stewards, not by this document. The upgrade was exercised against the long-running soak cluster before publication. No change is required for deployments that do not enable the optional subsystem. Adoption figures are collected from opt-in telemetry and should be read as indicative only. An audit of the default settings found no combination that silently disables durability. Contributors are reminded that behavioural changes need an entry in the change log.

## Known issues

Performance characteristics under sustained write amplification were not re-measured. An audit of the default settings found no combination that silently disables durability. The migration guide covers the rollback path in more detail than this note. Questions about licensing are handled by the project stewards, not by this document. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Deployments behind a strict egress policy should confirm the updated destination list. Metrics names were left alone so that existing dashboards continue to resolve. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Packaging for the container images follows the same tagging convention as before. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Feedback from the early-access cohort has been folded into the final behaviour. A small number of log lines changed wording; parsers keying on the message text may need updating.
