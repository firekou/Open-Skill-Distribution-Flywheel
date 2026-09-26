# Kestrel Runtime 2.1 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2030-07-01  
Source tier: official_release_notes

## Summary

Feedback from the early-access cohort has been folded into the final behaviour. Performance characteristics under sustained write amplification were not re-measured. Nothing in this section should be read as a commitment about unreleased functionality. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. The reference deployment topology is unchanged and remains the recommended starting point. The health endpoint continues to report readiness separately from liveness. Documentation for this area is maintained separately and is updated on the same cadence. Support for the deprecated configuration syntax continues for two further minor releases. No change is required for deployments that do not enable the optional subsystem. This paragraph exists to give the document realistic length and carries no factual claim. Contributors are reminded that behavioural changes need an entry in the change log. Adoption figures are collected from opt-in telemetry and should be read as indicative only. The working group met to review outstanding items and recorded no blocking objections. This note supersedes nothing; earlier notes remain accurate for the releases they describe. A small number of log lines changed wording; parsers keying on the message text may need updating.

## Feature flags

The following feature flags are **added** in this release:

- `lazy_schema_load` — new in 2.1, disabled by default.
- `mirror_write_audit` — new in 2.1, disabled by default.
- `parallel_compaction` — new in 2.1, disabled by default.

## Other changes

Metrics names were left alone so that existing dashboards continue to resolve. The reference deployment topology is unchanged and remains the recommended starting point. Packaging for the container images follows the same tagging convention as before. The migration guide covers the rollback path in more detail than this note. Deployments behind a strict egress policy should confirm the updated destination list. An audit of the default settings found no combination that silently disables durability. A small number of log lines changed wording; parsers keying on the message text may need updating. Support for the deprecated configuration syntax continues for two further minor releases. Adoption figures are collected from opt-in telemetry and should be read as indicative only. Questions about licensing are handled by the project stewards, not by this document. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Performance characteristics under sustained write amplification were not re-measured. Feedback from the early-access cohort has been folded into the final behaviour. Operators running a mixed fleet should stage the upgrade one availability zone at a time. The upgrade was exercised against the long-running soak cluster before publication. This paragraph exists to give the document realistic length and carries no factual claim. The health endpoint continues to report readiness separately from liveness. This note supersedes nothing; earlier notes remain accurate for the releases they describe.

## Known issues

Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Adoption figures are collected from opt-in telemetry and should be read as indicative only. Questions about licensing are handled by the project stewards, not by this document. Feedback from the early-access cohort has been folded into the final behaviour. Support for the deprecated configuration syntax continues for two further minor releases. The reference deployment topology is unchanged and remains the recommended starting point. No change is required for deployments that do not enable the optional subsystem. The upgrade was exercised against the long-running soak cluster before publication. Documentation for this area is maintained separately and is updated on the same cadence. Metrics names were left alone so that existing dashboards continue to resolve. The working group met to review outstanding items and recorded no blocking objections. A small number of log lines changed wording; parsers keying on the message text may need updating.
