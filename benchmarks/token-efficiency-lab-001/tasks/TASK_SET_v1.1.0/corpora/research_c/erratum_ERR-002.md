# Erratum ERR-002

Publisher: Kestrel Runtime Project (official)  
Published: 2032-02-20  
Source tier: erratum

The release notes for Kestrel Runtime 1.0 state that the feature flag `nested_span_export` was added in that release. That statement is incorrect.

The flag `nested_span_export` was added in Kestrel Runtime 1.2. No other statement in those release notes is affected by this erratum.

Adoption figures are collected from opt-in telemetry and should be read as indicative only. Packaging for the container images follows the same tagging convention as before. Metrics names were left alone so that existing dashboards continue to resolve. The compatibility matrix is regenerated whenever a plugin is relisted in the registry. The migration guide covers the rollback path in more detail than this note. This paragraph exists to give the document realistic length and carries no factual claim. The upgrade was exercised against the long-running soak cluster before publication. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. An audit of the default settings found no combination that silently disables durability.
