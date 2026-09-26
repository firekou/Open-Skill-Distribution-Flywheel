# Kestrel Runtime 2.3 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2031-01-27  
Source tier: official_release_notes

## Summary

An audit of the default settings found no combination that silently disables durability. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. This paragraph exists to give the document realistic length and carries no factual claim. Feedback from the early-access cohort has been folded into the final behaviour. Nothing in this section should be read as a commitment about unreleased functionality. No change is required for deployments that do not enable the optional subsystem. The upgrade was exercised against the long-running soak cluster before publication. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. The migration guide covers the rollback path in more detail than this note. The health endpoint continues to report readiness separately from liveness. The working group met to review outstanding items and recorded no blocking objections. Contributors are reminded that behavioural changes need an entry in the change log. Questions about licensing are handled by the project stewards, not by this document. Metrics names were left alone so that existing dashboards continue to resolve. The reference deployment topology is unchanged and remains the recommended starting point.

## Feature flags

The following feature flags are **removed** in this release and no longer have any effect:

- `nested_span_export` — removed in 2.3.

## Other changes

Feedback from the early-access cohort has been folded into the final behaviour. Contributors are reminded that behavioural changes need an entry in the change log. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The upgrade was exercised against the long-running soak cluster before publication. Questions about licensing are handled by the project stewards, not by this document. No change is required for deployments that do not enable the optional subsystem. This paragraph exists to give the document realistic length and carries no factual claim. Metrics names were left alone so that existing dashboards continue to resolve. Deployments behind a strict egress policy should confirm the updated destination list. The reference deployment topology is unchanged and remains the recommended starting point. An audit of the default settings found no combination that silently disables durability. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. A small number of log lines changed wording; parsers keying on the message text may need updating. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Adoption figures are collected from opt-in telemetry and should be read as indicative only. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Support for the deprecated configuration syntax continues for two further minor releases. The health endpoint continues to report readiness separately from liveness.

## Known issues

The working group met to review outstanding items and recorded no blocking objections. Deployments behind a strict egress policy should confirm the updated destination list. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Feedback from the early-access cohort has been folded into the final behaviour. Questions about licensing are handled by the project stewards, not by this document. The health endpoint continues to report readiness separately from liveness. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Contributors are reminded that behavioural changes need an entry in the change log. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. Packaging for the container images follows the same tagging convention as before. Documentation for this area is maintained separately and is updated on the same cadence. The migration guide covers the rollback path in more detail than this note.
