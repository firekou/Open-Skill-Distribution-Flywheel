# Kestrel Runtime 1.2 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2029-12-08  
Source tier: official_release_notes

## Summary

Adoption figures are collected from opt-in telemetry and should be read as indicative only. The reference deployment topology is unchanged and remains the recommended starting point. Questions about licensing are handled by the project stewards, not by this document. Performance characteristics under sustained write amplification were not re-measured. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Metrics names were left alone so that existing dashboards continue to resolve. Documentation for this area is maintained separately and is updated on the same cadence. The working group met to review outstanding items and recorded no blocking objections. An audit of the default settings found no combination that silently disables durability. This note supersedes nothing; earlier notes remain accurate for the releases they describe. This paragraph exists to give the document realistic length and carries no factual claim. Feedback from the early-access cohort has been folded into the final behaviour. Contributors are reminded that behavioural changes need an entry in the change log. Support for the deprecated configuration syntax continues for two further minor releases. The compatibility matrix is regenerated whenever a plugin is relisted in the registry.

## Feature flags

The following feature flags are **added** in this release:

- `greedy_merge_pass` — new in 1.2, disabled by default.
- `nested_span_export` — new in 1.2, disabled by default.
- `relaxed_ordering` — new in 1.2, disabled by default.

## Other changes

Questions about licensing are handled by the project stewards, not by this document. Adoption figures are collected from opt-in telemetry and should be read as indicative only. Nothing in this section should be read as a commitment about unreleased functionality. An audit of the default settings found no combination that silently disables durability. The upgrade was exercised against the long-running soak cluster before publication. The working group met to review outstanding items and recorded no blocking objections. The reference deployment topology is unchanged and remains the recommended starting point. Support for the deprecated configuration syntax continues for two further minor releases. No change is required for deployments that do not enable the optional subsystem. Operators running a mixed fleet should stage the upgrade one availability zone at a time. Contributors are reminded that behavioural changes need an entry in the change log. Documentation for this area is maintained separately and is updated on the same cadence. Packaging for the container images follows the same tagging convention as before. Performance characteristics under sustained write amplification were not re-measured. Metrics names were left alone so that existing dashboards continue to resolve. Feedback from the early-access cohort has been folded into the final behaviour. A small number of log lines changed wording; parsers keying on the message text may need updating. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable.

## Known issues

The upgrade was exercised against the long-running soak cluster before publication. The working group met to review outstanding items and recorded no blocking objections. This note supersedes nothing; earlier notes remain accurate for the releases they describe. The reference deployment topology is unchanged and remains the recommended starting point. Feedback from the early-access cohort has been folded into the final behaviour. Performance characteristics under sustained write amplification were not re-measured. Metrics names were left alone so that existing dashboards continue to resolve. Questions about licensing are handled by the project stewards, not by this document. Operators running a mixed fleet should stage the upgrade one availability zone at a time. This paragraph exists to give the document realistic length and carries no factual claim. Deployments behind a strict egress policy should confirm the updated destination list. Adoption figures are collected from opt-in telemetry and should be read as indicative only.
