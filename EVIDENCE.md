# EVIDENCE (synthetic/fake data only)

Generated 2026-10-12 00:33 CST

## pytest
```
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /workspace/shopify-square-true-profit
plugins: anyio-4.15.1
collecting ... collected 8 items

tests/test_true_profit.py::test_money_parsing PASSED                     [ 12%]
tests/test_true_profit.py::test_shopify_with_payments_file PASSED        [ 25%]
tests/test_true_profit.py::test_shopify_estimated_fees_without_payments_file PASSED [ 37%]
tests/test_true_profit.py::test_square PASSED                            [ 50%]
tests/test_true_profit.py::test_total PASSED                             [ 62%]
tests/test_true_profit.py::test_discrepancies PASSED                     [ 75%]
tests/test_true_profit.py::test_missing_cost_warns PASSED                [ 87%]
tests/test_true_profit.py::test_render_has_cta PASSED                    [100%]

============================== 8 passed in 0.03s ===============================
```

## Sample run
```
$ python3 scripts/true_profit.py --date 2026-10-11 --tz America/New_York --shopify-orders examples/fake_data/shopify_orders_export.csv --shopify-payments examples/fake_data/shopify_payments_transactions.csv --square-transactions examples/fake_data/square_transactions.csv --square-items examples/fake_data/square_items.csv --costs examples/fake_data/costs.csv
# True profit for 2026-10-11 (America/New_York)

| metric | shopify | square | total |
|---|---|---|---|
| orders | 2 | 2 | 4 |
| revenue | 85.00 | 32.00 | 117.00 |
| discounts | 5.00 | 2.00 | 7.00 |
| refunds | 10.00 | 5.00 | 15.00 |
| processing_fees | 3.17 | 1.04 | 4.21 |
| cogs | 30.00 | 11.50 | 41.50 |
| shipping_cost | 8.00 | 0.00 | 8.00 |
| net_profit | 28.83 | 12.46 | 41.29 |
| tax_collected_excluded | 3.60 | 2.40 | 6.00 |
| tips_excluded | 0.00 | 1.00 | 1.00 |

## Payout discrepancies (expected vs reported net)

| channel | ref | expected | reported | diff | flag |
|---|---|---|---|---|---|
| shopify | #1001 | 51.75 | 51.60 | -0.15 | FLAG |
| shopify | #1003 | 18.83 | 18.83 | 0.00 | ok |
| square | FAKETXN1 | 11.34 | 11.34 | 0.00 | ok |
| square | FAKETXN2 | 16.02 | 15.92 | -0.10 | FLAG |

---
Want this delivered to your inbox every morning? Profit daily report done-for-you service [PLACEHOLDER LINK]: https://madlouse.github.io/toolstack-lab/tools/sample-profit-report.html
```
