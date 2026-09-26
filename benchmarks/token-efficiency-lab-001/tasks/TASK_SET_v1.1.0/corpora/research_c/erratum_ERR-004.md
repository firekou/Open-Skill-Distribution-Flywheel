# Erratum ERR-004

Publisher: Kestrel Plugin Registry (official)  
Published: 2032-02-24  
Source tier: erratum

The registry export dated 2032-02-11 records the minimum supported Kestrel Runtime version for `kp-csv-bridge` incorrectly.

The correct minimum supported version for `kp-csv-bridge` is **0.9**. The export will be regenerated at the next review.

The reference deployment topology is unchanged and remains the recommended starting point. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. Performance characteristics under sustained write amplification were not re-measured. Packaging for the container images follows the same tagging convention as before. This paragraph exists to give the document realistic length and carries no factual claim. Deployments behind a strict egress policy should confirm the updated destination list. Support for the deprecated configuration syntax continues for two further minor releases. Metrics names were left alone so that existing dashboards continue to resolve. Operators running a mixed fleet should stage the upgrade one availability zone at a time.
