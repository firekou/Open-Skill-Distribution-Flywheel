# Erratum ERR-005

Publisher: Kestrel Plugin Registry (official)  
Published: 2032-02-24  
Source tier: erratum

The registry export dated 2032-02-11 records the minimum supported Kestrel Runtime version for `kp-fx-lookup` incorrectly.

The correct minimum supported version for `kp-fx-lookup` is **2.3**. The export will be regenerated at the next review.

Adoption figures are collected from opt-in telemetry and should be read as indicative only. Packaging for the container images follows the same tagging convention as before. The health endpoint continues to report readiness separately from liveness. A small number of log lines changed wording; parsers keying on the message text may need updating. The upgrade was exercised against the long-running soak cluster before publication. Benchmarks quoted elsewhere were produced on unspecified hardware and are not comparable. This note supersedes nothing; earlier notes remain accurate for the releases they describe. Deployments behind a strict egress policy should confirm the updated destination list. The reference deployment topology is unchanged and remains the recommended starting point.
