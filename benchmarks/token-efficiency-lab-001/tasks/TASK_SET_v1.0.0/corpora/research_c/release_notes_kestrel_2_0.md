# Kestrel Runtime 2.0 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2030-03-25  
Source tier: official_release_notes

## Summary

A small number of log lines changed wording; parsers keying on the message text may need updating. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Metrics names were left alone so that existing dashboards continue to resolve. The working group met to review outstanding items and recorded no blocking objections. Feedback from the early-access cohort has been folded into the final behaviour. Contributors are reminded that behavioural changes need an entry in the change log. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Performance characteristics under sustained write amplification were not re-measured. The reference deployment topology is unchanged and remains the recommended starting point. Operators running a mixed fleet should stage the upgrade one availability zone at a time. No change is required for deployments that do not enable the optional subsystem. This paragraph exists to give the document realistic length and carries no factual claim. Nothing in this section should be read as a commitment about unreleased functionality. Packaging for the container images follows the same tagging convention as before. The health endpoint continues to report readiness separately from liveness.

## Feature flags

The following feature flags are **added** in this release:

- `cold_start_probe` — new in 2.0, disabled by default.
- `deferred_index_flush` — new in 2.0, disabled by default.
- `opportunistic_gc` — new in 2.0, disabled by default.

## Other changes

Contributors are reminded that behavioural changes need an entry in the change log. Feedback from the early-access cohort has been folded into the final behaviour. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The health endpoint continues to report readiness separately from liveness. Nothing in this section should be read as a commitment about unreleased functionality. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Metrics names were left alone so that existing dashboards continue to resolve. This paragraph exists to give the document realistic length and carries no factual claim. Packaging for the container images follows the same tagging convention as before. Support for the deprecated configuration syntax continues for two further minor releases. Deployments behind a strict egress policy should confirm the updated destination list. Performance characteristics under sustained write amplification were not re-measured. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. An audit of the default settings found no combination that silently disables durability. Documentation for this area is maintained separately and is updated on the same cadence. The migration guide covers the rollback path in more detail than this note. The working group met to review outstanding items and recorded no blocking objections. A small number of log lines changed wording; parsers keying on the message text may need updating.

## Known issues

Operators running a mixed fleet should stage the upgrade one availability zone at a time. Packaging for the container images follows the same tagging convention as before. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. A small number of log lines changed wording; parsers keying on the message text may need updating. The migration guide covers the rollback path in more detail than this note. No change is required for deployments that do not enable the optional subsystem. Feedback from the early-access cohort has been folded into the final behaviour. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. The reference deployment topology is unchanged and remains the recommended starting point. The upgrade was exercised against the long-running soak cluster before publication. Adoption figures are collected from opt-in telemetry and should be read as indicative only. An audit of the default settings found no combination that silently disables durability.
