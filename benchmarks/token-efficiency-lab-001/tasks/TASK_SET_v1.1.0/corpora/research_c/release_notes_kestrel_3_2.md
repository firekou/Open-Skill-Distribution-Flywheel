# Kestrel Runtime 3.2 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2032-01-19  
Source tier: official_release_notes

## Summary

Nothing in this section should be read as a commitment about unreleased functionality. Support for the deprecated configuration syntax continues for two further minor releases. The health endpoint continues to report readiness separately from liveness. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Performance characteristics under sustained write amplification were not re-measured. Feedback from the early-access cohort has been folded into the final behaviour. Documentation for this area is maintained separately and is updated on the same cadence. An audit of the default settings found no combination that silently disables durability. The working group met to review outstanding items and recorded no blocking objections. The upgrade was exercised against the long-running soak cluster before publication. Deployments behind a strict egress policy should confirm the updated destination list. The migration guide covers the rollback path in more detail than this note. No change is required for deployments that do not enable the optional subsystem. This paragraph exists to give the document realistic length and carries no factual claim. The compatibility matrix is regenerated whenever a plugin is relisted in the registry.

## Feature flags

The following feature flags are **removed** in this release and no longer have any effect:

- `cold_start_probe` — removed in 3.2.

## Other changes

Contributors are reminded that behavioural changes need an entry in the change log. Feedback from the early-access cohort has been folded into the final behaviour. Performance characteristics under sustained write amplification were not re-measured. An audit of the default settings found no combination that silently disables durability. Adoption figures are collected from opt-in telemetry and should be read as indicative only. No change is required for deployments that do not enable the optional subsystem. The reference deployment topology is unchanged and remains the recommended starting point. The migration guide covers the rollback path in more detail than this note. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Documentation for this area is maintained separately and is updated on the same cadence. Nothing in this section should be read as a commitment about unreleased functionality. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Support for the deprecated configuration syntax continues for two further minor releases. Deployments behind a strict egress policy should confirm the updated destination list. Packaging for the container images follows the same tagging convention as before. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. The upgrade was exercised against the long-running soak cluster before publication. This paragraph exists to give the document realistic length and carries no factual claim.

## Known issues

Performance characteristics under sustained write amplification were not re-measured. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. An audit of the default settings found no combination that silently disables durability. The health endpoint continues to report readiness separately from liveness. The working group met to review outstanding items and recorded no blocking objections. Adoption figures are collected from opt-in telemetry and should be read as indicative only. Support for the deprecated configuration syntax continues for two further minor releases. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Documentation for this area is maintained separately and is updated on the same cadence. This paragraph exists to give the document realistic length and carries no factual claim. Nothing in this section should be read as a commitment about unreleased functionality. Operators running a mixed fleet should stage the upgrade one availability zone at a time.
