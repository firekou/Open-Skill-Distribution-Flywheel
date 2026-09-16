# Kestrel Runtime 0.9 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2029-02-14  
Source tier: official_release_notes

## Summary

The upgrade was exercised against the long-running soak cluster before publication. This paragraph exists to give the document realistic length and carries no factual claim. The reference deployment topology is unchanged and remains the recommended starting point. Feedback from the early-access cohort has been folded into the final behaviour. Contributors are reminded that behavioural changes need an entry in the change log. Questions about licensing are handled by the project stewards, not by this document. Adoption figures are collected from opt-in telemetry and should be read as indicative only. The migration guide covers the rollback path in more detail than this note. Metrics names were left alone so that existing dashboards continue to resolve. Operators running a mixed fleet should stage the upgrade one availability zone at a time. The health endpoint continues to report readiness separately from liveness. This note supersedes nothing; earlier notes remain accurate for the releases they describe. No change is required for deployments that do not enable the optional subsystem. Documentation for this area is maintained separately and is updated on the same cadence. Nothing in this section should be read as a commitment about unreleased functionality.

## Feature flags

The following feature flags are **added** in this release:

- `batch_ack_window` — new in 0.9, disabled by default.

## Other changes

The upgrade was exercised against the long-running soak cluster before publication. Nothing in this section should be read as a commitment about unreleased functionality. The migration guide covers the rollback path in more detail than this note. The reference deployment topology is unchanged and remains the recommended starting point. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Deployments behind a strict egress policy should confirm the updated destination list. This paragraph exists to give the document realistic length and carries no factual claim. Performance characteristics under sustained write amplification were not re-measured. Adoption figures are collected from opt-in telemetry and should be read as indicative only. An audit of the default settings found no combination that silently disables durability. Feedback from the early-access cohort has been folded into the final behaviour. The working group met to review outstanding items and recorded no blocking objections. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Questions about licensing are handled by the project stewards, not by this document. Metrics names were left alone so that existing dashboards continue to resolve. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Packaging for the container images follows the same tagging convention as before.

## Known issues

Metrics names were left alone so that existing dashboards continue to resolve. Deployments behind a strict egress policy should confirm the updated destination list. Contributors are reminded that behavioural changes need an entry in the change log. Packaging for the container images follows the same tagging convention as before. The health endpoint continues to report readiness separately from liveness. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Adoption figures are collected from opt-in telemetry and should be read as indicative only. Operators running a mixed fleet should stage the upgrade one availability zone at a time. No change is required for deployments that do not enable the optional subsystem. Feedback from the early-access cohort has been folded into the final behaviour. Performance characteristics under sustained write amplification were not re-measured. The migration guide covers the rollback path in more detail than this note.
