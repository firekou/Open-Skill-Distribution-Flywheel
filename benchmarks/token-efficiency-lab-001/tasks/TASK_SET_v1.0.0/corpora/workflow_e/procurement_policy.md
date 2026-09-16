# Procurement policy handbook (synthetic)

## P1 Rounding and currency
All figures are in euro. Intermediate values are carried at full precision and only the
final figure for a line or a total is rounded, half up, to two decimal places.

## P2 Contingency
A contingency of 12% is applied to the subtotal of hardware lines only. Service lines
(uom `day`, or any part whose `rohs` column reads `n/a`) are excluded from the
contingency base.

## P3 Vendor eligibility
A vendor whose `status` is `suspended` may not be used. A vendor whose most recent
`audit_result` is `failed` may not be used until a re-audit is recorded.

## P4 Freight
Freight is charged at 3% of the hardware subtotal before contingency, for vendors outside
the destination site's region, and at 1% for vendors in the same region as the destination
site. Freight is not charged on service lines.

## P5 Approval thresholds
A requisition whose grand total exceeds EUR 200000.00 requires two approvers. Below that
threshold one approver is sufficient.

## P6 Lead time
The requisition lead time is the maximum `lead_time_days` across all hardware lines.
Service lines do not contribute to lead time.
