# EVIDENCE (synthetic/fake data only)

Generated 2026-10-12 00:40 (Asia/Shanghai, box clock)

## Column verification (docs fetched 2026-10-12 with WebFetch)

Status: **verified** = exact header listed in an official doc page fetched; **not in official docs** = official Square help pages fetched do not list CSV headers; name taken from Square Community posts (user/Square-staff forum, not official docs) and third-party guides.

| file | column used by script | doc URL (fetched) | status |
|---|---|---|---|
| Shopify orders | `Name` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Financial Status` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Subtotal` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Shipping` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Taxes` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Total` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Discount Amount` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Created at` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Lineitem quantity` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Lineitem name` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Lineitem price` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Lineitem SKU` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | `Refunded Amount` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified |
| Shopify orders | (fixture only) `Lineitem compare-at price` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders | verified; v1 fixture had `Lineitem compare at price`/`Lineitem sku` -> fixed. Script matches headers case-insensitively |
| Shopify transaction histories | `Created At` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders (Transaction history CSV structure) | verified |
| Shopify transaction histories | `Kind` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders (Transaction history CSV structure) | verified |
| Shopify transaction histories | `Status` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders (Transaction history CSV structure) | verified |
| Shopify transaction histories | `Amount` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders (Transaction history CSV structure) | verified |
| Shopify transaction histories | `Name` | https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders (Transaction history CSV structure) | verified |
| Shopify Payments transactions | `Transaction Date` | https://help.shopify.com/en/manual/payments/shopify-payments/payouts/view-details | verified |
| Shopify Payments transactions | `Type` | https://help.shopify.com/en/manual/payments/shopify-payments/payouts/view-details | verified |
| Shopify Payments transactions | `Order` | https://help.shopify.com/en/manual/payments/shopify-payments/payouts/view-details | verified |
| Shopify Payments transactions | `Amount` | https://help.shopify.com/en/manual/payments/shopify-payments/payouts/view-details | verified |
| Shopify Payments transactions | `Fee` | https://help.shopify.com/en/manual/payments/shopify-payments/payouts/view-details | verified |
| Shopify Payments transactions | `Net` | https://help.shopify.com/en/manual/payments/shopify-payments/payouts/view-details | verified |
| Shopify Payments transactions | (v1 fixture extras: Payout ID, Checkout, Payment Method Name, Presentment Amount/Currency, Currency) | https://help.shopify.com/en/manual/payments/shopify-payments/payouts/view-details | not in doc's 11-column list -> removed from fixture (unused by script) |
| Square transactions | `Date` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Time` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Time Zone` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Gross Sales` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Discounts` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Service Charges` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Net Sales` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Tax` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Tip` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Partial Refunds` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Total Collected` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Fees` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Net Total` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Transaction ID` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square transactions | `Event Type` | https://squareup.com/help/us/en/article/5381-in-app-summaries-and-reports, https://squareup.com/help/us/en/article/5072 | not in official docs (5381 defines *metrics* Total collected / Net total / Partial refunds, not CSV headers). Seen in community.squareup.com posts / trestlefinance.com guides |
| Square item details | `Date` | https://squareup.com/help/us/en/article/5072 | not in official docs. Header list seen in a community.squareup.com post (Square-staff-answered thread) |
| Square item details | `Time` | https://squareup.com/help/us/en/article/5072 | not in official docs. Header list seen in a community.squareup.com post (Square-staff-answered thread) |
| Square item details | `Time Zone` | https://squareup.com/help/us/en/article/5072 | not in official docs. Header list seen in a community.squareup.com post (Square-staff-answered thread) |
| Square item details | `Item` | https://squareup.com/help/us/en/article/5072 | not in official docs. Header list seen in a community.squareup.com post (Square-staff-answered thread) |
| Square item details | `Qty` | https://squareup.com/help/us/en/article/5072 | not in official docs. Header list seen in a community.squareup.com post (Square-staff-answered thread) |
| Square item details | `SKU` | https://squareup.com/help/us/en/article/5072 | not in official docs. Header list seen in a community.squareup.com post (Square-staff-answered thread) |
| Square item details | `Gross Sales` | https://squareup.com/help/us/en/article/5072 | not in official docs. Header list seen in a community.squareup.com post (Square-staff-answered thread) |
| Square item details | `Transaction ID` | https://squareup.com/help/us/en/article/5072 | not in official docs. Header list seen in a community.squareup.com post (Square-staff-answered thread) |

Unofficial sources consulted (not fetched as docs, search snippets only): community.squareup.com threads m-p/749378, m-p/221778, m-p/764199; trestlefinance.com/guides/square-transactions-csv-quickbooks. Note: one third-party source shows Square `Time Zone` as IANA (e.g. `America/Detroit`), so the script accepts both styles.

## CTA link check
```
$ curl -s -o /dev/null -w "%{http_code}" -L https://madlouse.github.io/toolstack-lab/tools/sample-profit-report.html
200
```

## pytest
```
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /workspace/shopify-square-true-profit
plugins: anyio-4.15.1
collecting ... collected 17 items

tests/test_true_profit.py::test_money_parsing PASSED                     [  5%]
tests/test_true_profit.py::test_shopify_with_payments_file PASSED        [ 11%]
tests/test_true_profit.py::test_shopify_estimated_fees_with_transaction_history PASSED [ 17%]
tests/test_true_profit.py::test_shopify_fallback_order_date_refunds_warns PASSED [ 23%]
tests/test_true_profit.py::test_cross_day_refund_shopify PASSED          [ 29%]
tests/test_true_profit.py::test_cross_day_refund_square PASSED           [ 35%]
tests/test_true_profit.py::test_square PASSED                            [ 41%]
tests/test_true_profit.py::test_total PASSED                             [ 47%]
tests/test_true_profit.py::test_discrepancies PASSED                     [ 52%]
tests/test_true_profit.py::test_square_iana_timezone_label PASSED        [ 58%]
tests/test_true_profit.py::test_lineitem_sku_header_case_insensitive PASSED [ 64%]
tests/test_true_profit.py::test_missing_cost_warns PASSED                [ 70%]
tests/test_true_profit.py::test_render_has_cta PASSED                    [ 76%]
tests/test_true_profit.py::test_square_missing_column_fails_clearly PASSED [ 82%]
tests/test_true_profit.py::test_square_renamed_column_reports_unknown_header PASSED [ 88%]
tests/test_true_profit.py::test_square_items_missing_qty_fails PASSED    [ 94%]
tests/test_true_profit.py::test_cli_exit_code_2_on_bad_square PASSED     [100%]

============================== 17 passed in 0.05s ==============================
```

## Square beta: bad header demo (Net Total renamed to Net Amount)
```
$ python3 scripts/true_profit.py --date 2026-10-11 --tz America/New_York --square-transactions /tmp/bad_sq.csv
ERROR: Square transactions CSV '/tmp/bad_sq.csv' is missing required column(s): Net Total. Unrecognized header(s) in file: Gift Card Sales, Source, Card, Card Entry Methods, Cash, Square Gift Card, Other Tender, Other Tender Type, Net Amount, Payment ID, Card Brand, PAN Suffix, Device Name, Staff Name, Description, Location. Square support is beta; please open an issue with a redacted sample export header row.
exit code: 2
```

## Sample run 2026-10-11
```
$ python3 scripts/true_profit.py --tz America/New_York --shopify-orders examples/fake_data/shopify_orders_export.csv --shopify-payments examples/fake_data/shopify_payments_transactions.csv --square-transactions examples/fake_data/square_transactions.csv --square-items examples/fake_data/square_items.csv --costs examples/fake_data/costs.csv --date 2026-10-11
# True profit for 2026-10-11 (America/New_York)

| metric | shopify | square | total |
|---|---|---|---|
| orders | 3 | 2 | 5 |
| revenue | 125.00 | 32.00 | 157.00 |
| discounts | 5.00 | 2.00 | 7.00 |
| refunds | 10.00 | 5.00 | 15.00 |
| processing_fees | 4.63 | 1.04 | 5.67 |
| cogs | 38.00 | 11.50 | 49.50 |
| shipping_cost | 12.00 | 0.00 | 12.00 |
| net_profit | 55.37 | 12.46 | 67.83 |
| tax_collected_excluded | 3.60 | 2.40 | 6.00 |
| tips_excluded | 0.00 | 1.00 | 1.00 |

## Payout discrepancies (expected vs reported net)

| channel | ref | expected | reported | diff | flag |
|---|---|---|---|---|---|
| shopify | #1001 charge | 51.75 | 51.60 | -0.15 | FLAG |
| shopify | #1004 charge | 38.54 | 38.54 | 0.00 | ok |
| shopify | #1003 charge | 28.83 | 28.83 | 0.00 | ok |
| shopify | #1003 refund | -10.00 | -10.00 | 0.00 | ok |
| square | FAKETXN1 | 11.34 | 11.34 | 0.00 | ok |
| square | FAKETXN2 | 16.02 | 15.92 | -0.10 | FLAG |

---
Want this delivered every morning? See Toolstack Lab's profit daily report done-for-you service: https://madlouse.github.io/toolstack-lab/tools/sample-profit-report.html
```

## Sample run 2026-10-12
```
$ python3 scripts/true_profit.py --tz America/New_York --shopify-orders examples/fake_data/shopify_orders_export.csv --shopify-payments examples/fake_data/shopify_payments_transactions.csv --square-transactions examples/fake_data/square_transactions.csv --square-items examples/fake_data/square_items.csv --costs examples/fake_data/costs.csv --date 2026-10-12
# True profit for 2026-10-12 (America/New_York)

| metric | shopify | square | total |
|---|---|---|---|
| orders | 1 | 0 | 1 |
| revenue | 20.00 | 0.00 | 20.00 |
| discounts | 0.00 | 0.00 | 0.00 |
| refunds | 15.00 | 4.00 | 19.00 |
| processing_fees | 0.88 | 0.00 | 0.88 |
| cogs | 8.00 | -1.00 | 7.00 |
| shipping_cost | 4.00 | 0.00 | 4.00 |
| net_profit | -7.88 | -3.00 | -10.88 |
| tax_collected_excluded | 0.00 | -0.32 | -0.32 |
| tips_excluded | 0.00 | 0.00 | 0.00 |

## Payout discrepancies (expected vs reported net)

| channel | ref | expected | reported | diff | flag |
|---|---|---|---|---|---|
| shopify | #1004 refund | -15.00 | -15.00 | 0.00 | ok |
| square | FAKETXN1 | -4.32 | -4.32 | 0.00 | ok |

## Warnings

- shopify: order #1002 missing from payments file; fee estimated

---
Want this delivered every morning? See Toolstack Lab's profit daily report done-for-you service: https://madlouse.github.io/toolstack-lab/tools/sample-profit-report.html
```

