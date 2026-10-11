# shopify-square-true-profit

Free, read-only agent skill (v1) that turns Shopify + Square CSV exports and your costs into a daily **true profit** report per channel and a **payout discrepancy** list. Pure Python stdlib, all money in `decimal.Decimal`, no network, no writes.

## Quick start
```bash
python3 scripts/true_profit.py --date 2026-10-11 --tz America/New_York --shopify-orders examples/fake_data/shopify_orders_export.csv --shopify-payments examples/fake_data/shopify_payments_transactions.csv --square-transactions examples/fake_data/square_transactions.csv --square-items examples/fake_data/square_items.csv --costs examples/fake_data/costs.csv
pytest -q tests
```
All files in `examples/fake_data/` are **synthetic/fake** test data.

See [SKILL.md](SKILL.md) for inputs, costs.csv format, definitions. Test evidence: [EVIDENCE.md](EVIDENCE.md).

## Assumptions
- Shopify orders export: one row per line item; order-level fields (Financial Status, Subtotal, Shipping, Taxes, Total, Discount Amount, Refunded Amount) only on the first row; `Created at` like `2026-10-11 10:00:00 -0400`. Orders with status voided/pending are skipped. The orders export has no fee column, so fees come from the Shopify Payments transactions export if supplied, else are estimated from costs.csv.
- Square: money like `$1.00`, `-$1.00` or `($1.00)`; Fees are negative; Net Total = Total Collected + Fees; Time Zone uses names like "Eastern Time (US & Canada)" (common US zones mapped, else merchant tz assumed). Items joined to transactions by Transaction ID; COGS by SKU, falling back to item name.
- Refunds are counted on the **refund date**: Shopify Payments `Transaction Date` (Type=refund) or transaction-history `Created At` (Kind=refund, Status=success); Square rows with `Event Type`=Refund (dated on refund). If neither Shopify file is supplied, the orders export `Refunded Amount` is used on the order date with a warning. Square `Partial Refunds` is counted on its row's date.
- Shopify header lookup is case-insensitive (docs say `Lineitem SKU`; some exports write `Lineitem sku`). Square `Time Zone` accepts Rails names or IANA names.
- Square CSV column names are NOT listed in Square's official help docs; they come from Square Community posts and real-export samples. See EVIDENCE.md.

## Roadmap (v2)
Clover support; Shopify/Square API connectors.

---
> **Done-for-you:** want this profit report delivered every morning? Toolstack Lab offers a profit daily report done-for-you service — email **jeking.hwang2025@gmail.com** (sample report: https://madlouse.github.io/toolstack-lab/tools/sample-profit-report.html).

## License
MIT
