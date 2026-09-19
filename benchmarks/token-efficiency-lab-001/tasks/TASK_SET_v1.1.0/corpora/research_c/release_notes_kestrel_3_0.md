# Kestrel Runtime 3.0 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2031-05-12  
Source tier: official_release_notes

## Summary

A small number of log lines changed wording; parsers keying on the message text may need updating. An audit of the default settings found no combination that silently disables durability. The reference deployment topology is unchanged and remains the recommended starting point. Deployments behind a strict egress policy should confirm the updated destination list. Adoption figures are collected from opt-in telemetry and should be read as indicative only. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Questions about licensing are handled by the project stewards, not by this document. Nothing in this section should be read as a commitment about unreleased functionality. The health endpoint continues to report readiness separately from liveness. Performance characteristics under sustained write amplification were not re-measured. Documentation for this area is maintained separately and is updated on the same cadence. The migration guide covers the rollback path in more detail than this note. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Metrics names were left alone so that existing dashboards continue to resolve. The upgrade was exercised against the long-running soak cluster before publication.

## Feature flags

The following feature flags are **removed** in this release and no longer have any effect:

- `deferred_index_flush` — removed in 3.0.

## Other changes

Contributors are reminded that behavioural changes need an entry in the change log. This paragraph exists to give the document realistic length and carries no factual claim. No change is required for deployments that do not enable the optional subsystem. Performance characteristics under sustained write amplification were not re-measured. Questions about licensing are handled by the project stewards, not by this document. Metrics names were left alone so that existing dashboards continue to resolve. The upgrade was exercised against the long-running soak cluster before publication. An audit of the default settings found no combination that silently disables durability. Adoption figures are collected from opt-in telemetry and should be read as indicative only. Nothing in this section should be read as a commitment about unreleased functionality. Support for the deprecated configuration syntax continues for two further minor releases. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Documentation for this area is maintained separately and is updated on the same cadence. A small number of log lines changed wording; parsers keying on the message text may need updating. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Operators running a mixed fleet should stage the upgrade one availability zone at a time. The working group met to review outstanding items and recorded no blocking objections.

## Known issues

Deployments behind a strict egress policy should confirm the updated destination list. Support for the deprecated configuration syntax continues for two further minor releases. The upgrade was exercised against the long-running soak cluster before publication. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. The health endpoint continues to report readiness separately from liveness. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Nothing in this section should be read as a commitment about unreleased functionality. No change is required for deployments that do not enable the optional subsystem. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The reference deployment topology is unchanged and remains the recommended starting point. Feedback from the early-access cohort has been folded into the final behaviour. Questions about licensing are handled by the project stewards, not by this document.
