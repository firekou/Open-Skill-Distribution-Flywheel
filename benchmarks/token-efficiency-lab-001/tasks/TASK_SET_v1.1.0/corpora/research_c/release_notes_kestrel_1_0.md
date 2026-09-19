# Kestrel Runtime 1.0 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2029-06-03  
Source tier: official_release_notes

## Summary

This note supersedes nothing; earlier notes remain accurate for the releases they describe. The upgrade was exercised against the long-running soak cluster before publication. Packaging for the container images follows the same tagging convention as before. Support for the deprecated configuration syntax continues for two further minor releases. The working group met to review outstanding items and recorded no blocking objections. Performance characteristics under sustained write amplification were not re-measured. Feedback from the early-access cohort has been folded into the final behaviour. This paragraph exists to give the document realistic length and carries no factual claim. Nothing in this section should be read as a commitment about unreleased functionality. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. The reference deployment topology is unchanged and remains the recommended starting point. Deployments behind a strict egress policy should confirm the updated destination list. Contributors are reminded that behavioural changes need an entry in the change log. Metrics names were left alone so that existing dashboards continue to resolve. Questions about licensing are handled by the project stewards, not by this document.

## Feature flags

The following feature flags are **added** in this release:

- `inline_checksum` — new in 1.0, disabled by default.
- `nested_span_export` — new in 1.0, disabled by default.
- `parallel_compaction` — new in 1.0, disabled by default.
- `quiescent_snapshot` — new in 1.0, disabled by default.

## Other changes

Questions about licensing are handled by the project stewards, not by this document. The health endpoint continues to report readiness separately from liveness. Metrics names were left alone so that existing dashboards continue to resolve. Performance characteristics under sustained write amplification were not re-measured. No change is required for deployments that do not enable the optional subsystem. Packaging for the container images follows the same tagging convention as before. Adoption figures are collected from opt-in telemetry and should be read as indicative only. A small number of log lines changed wording; parsers keying on the message text may need updating. Deployments behind a strict egress policy should confirm the updated destination list. An audit of the default settings found no combination that silently disables durability. This paragraph exists to give the document realistic length and carries no factual claim. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Support for the deprecated configuration syntax continues for two further minor releases. The upgrade was exercised against the long-running soak cluster before publication. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. The working group met to review outstanding items and recorded no blocking objections. Documentation for this area is maintained separately and is updated on the same cadence. Contributors are reminded that behavioural changes need an entry in the change log.

## Known issues

Operators running a mixed fleet should stage the upgrade one availability zone at a time. Performance characteristics under sustained write amplification were not re-measured. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Support for the deprecated configuration syntax continues for two further minor releases. Adoption figures are collected from opt-in telemetry and should be read as indicative only. The health endpoint continues to report readiness separately from liveness. Deployments behind a strict egress policy should confirm the updated destination list. A small number of log lines changed wording; parsers keying on the message text may need updating. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Questions about licensing are handled by the project stewards, not by this document. The upgrade was exercised against the long-running soak cluster before publication. The migration guide covers the rollback path in more detail than this note.
