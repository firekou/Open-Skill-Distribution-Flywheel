# Kestrel Runtime 3.1 — Release Notes

Publisher: Kestrel Runtime Project (official)  
Published: 2031-09-08  
Source tier: official_release_notes

## Summary

Nothing in this section should be read as a commitment about unreleased functionality. The working group met to review outstanding items and recorded no blocking objections. This paragraph exists to give the document realistic length and carries no factual claim. Support for the deprecated configuration syntax continues for two further minor releases. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. A small number of log lines changed wording; parsers keying on the message text may need updating. The migration guide covers the rollback path in more detail than this note. An audit of the default settings found no combination that silently disables durability. Contributors are reminded that behavioural changes need an entry in the change log. Questions about licensing are handled by the project stewards, not by this document. Performance characteristics under sustained write amplification were not re-measured. Deployments behind a strict egress policy should confirm the updated destination list. Packaging for the container images follows the same tagging convention as before. No change is required for deployments that do not enable the optional subsystem. The health endpoint continues to report readiness separately from liveness.

## Feature flags

The following feature flags are **removed** in this release and no longer have any effect:

- `greedy_merge_pass` — removed in 3.1.
- `hinted_route_table` — removed in 3.1.
- `inline_checksum` — removed in 3.1.
- `mirror_write_audit` — removed in 3.1.

## Other changes

The reference deployment topology is unchanged and remains the recommended starting point. Deployments behind a strict egress policy should confirm the updated destination list. Operators running a mixed fleet should stage the upgrade one availability zone at a time. The upgrade was exercised against the long-running soak cluster before publication. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. No change is required for deployments that do not enable the optional subsystem. Support for the deprecated configuration syntax continues for two further minor releases. Performance characteristics under sustained write amplification were not re-measured. The health endpoint continues to report readiness separately from liveness. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. This paragraph exists to give the document realistic length and carries no factual claim. The working group met to review outstanding items and recorded no blocking objections. Nothing in this section should be read as a commitment about unreleased functionality. Questions about licensing are handled by the project stewards, not by this document. The migration guide covers the rollback path in more detail than this note. An audit of the default settings found no combination that silently disables durability. Contributors are reminded that behavioural changes need an entry in the change log. Adoption figures are collected from opt-in telemetry and should be read as indicative only.

## Known issues

The health endpoint continues to report readiness separately from liveness. A small number of log lines changed wording; parsers keying on the message text may need updating. The migration guide covers the rollback path in more detail than this note. Feedback from the early-access cohort has been folded into the final behaviour. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. This paragraph exists to give the document realistic length and carries no factual claim. Deployments behind a strict egress policy should confirm the updated destination list. Documentation for this area is maintained separately and is updated on the same cadence. Adoption figures are collected from opt-in telemetry and should be read as indicative only. Performance characteristics under sustained write amplification were not re-measured. Nothing in this section should be read as a commitment about unreleased functionality. No change is required for deployments that do not enable the optional subsystem.
