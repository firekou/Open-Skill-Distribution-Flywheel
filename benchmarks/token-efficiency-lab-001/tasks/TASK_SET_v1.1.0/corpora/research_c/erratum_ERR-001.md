# Erratum ERR-001

Publisher: Kestrel Runtime Project (official)  
Published: 2032-02-20  
Source tier: erratum

The release notes for Kestrel Runtime 2.0 state that the feature flag `opportunistic_gc` was added in that release. That statement is incorrect.

The flag `opportunistic_gc` was added in Kestrel Runtime 2.2. No other statement in those release notes is affected by this erratum.

The reference deployment topology is unchanged and remains the recommended starting point. Metrics names were left alone so that existing dashboards continue to resolve. An audit of the default settings found no combination that silently disables durability. This paragraph exists to give the document realistic length and carries no factual claim. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Documentation for this area is maintained separately and is updated on the same cadence. Questions about licensing are handled by the project stewards, not by this document. Packaging for the container images follows the same tagging convention as before. Support for the deprecated configuration syntax continues for two further minor releases.
