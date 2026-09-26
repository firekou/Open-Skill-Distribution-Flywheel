# Procurement policy handbook (synthetic)

## P1 Rounding and currency
All figures are in euro. Rounding is half up to two decimal places.

Rounding happens at exactly these points and at no other point:

* P1.1 each bill-of-materials line total, which is that line's unit price multiplied by its
  quantity;
* P1.2 each of the four component totals - the hardware subtotal, the service subtotal, the
  freight charge and the contingency charge - each computed once from full-precision inputs
  and rounded once;
* P1.3 the grand total, which is the sum of the four component totals **as reported**, that
  is, after each of them has been rounded under P1.2;
* P1.4 the amount over the cap, which is the reported grand total minus the cap.

Every other quantity is an intermediate value. Intermediate values are carried at full
precision and are never rounded before they enter a total. In particular, a per-vendor, per-
region, per-line or per-category apportionment of freight or of contingency is an intermediate
value: it is not a line, it is not a component total, and it is not rounded.

## P2 Contingency
A contingency of 12% is applied to the subtotal of hardware lines only. Service lines
(uom `day`, or any part whose `rohs` column reads `n/a`) are excluded from the
contingency base.

## P3 Vendor eligibility
A vendor whose `status` is `suspended` may not be used. A vendor whose most recent
`audit_result` is `failed` may not be used until a re-audit is recorded.

## P4 Freight
Freight is charged per vendor, on that vendor's own share of the hardware subtotal before
contingency: at 3% for a vendor outside the destination site's region, and at 1% for a vendor
in the same region as the destination site. Freight is not charged on service lines.

The freight charge is the sum, over every vendor supplying a hardware line, of that vendor's
hardware line totals multiplied by that vendor's rate. That sum is a single component total
and is rounded once under P1.2. The per-vendor products are intermediate values under P1 and
are **not** rounded before they are summed.

## P5 Approval thresholds
A requisition whose grand total exceeds EUR 200000.00 requires two approvers. Below that
threshold one approver is sufficient.

## P6 Lead time
The requisition lead time is the maximum `lead_time_days` across all hardware lines.
Service lines do not contribute to lead time.
