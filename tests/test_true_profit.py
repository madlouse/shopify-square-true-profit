"""Expected values below were computed BY HAND from the FAKE data in examples/fake_data (see comments)."""
import sys, os
from datetime import date
from decimal import Decimal as D
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import true_profit as tp

F = os.path.join(os.path.dirname(__file__), "..", "examples", "fake_data")
p = lambda n: os.path.join(F, n)


def full(**kw):
    args = dict(shopify_orders=p("shopify_orders_export.csv"), shopify_payments=p("shopify_payments_transactions.csv"),
                square_tx=p("square_transactions.csv"), square_items=p("square_items.csv"), costs=p("costs.csv"))
    args.update(kw)
    return tp.run(date(2026, 10, 11), "America/New_York", **args)


def test_money_parsing():
    assert tp.money("$1,234.50") == D("1234.50")
    assert tp.money("-$2.00") == D("-2.00")
    assert tp.money("($5.00)") == D("-5.00")
    assert tp.money("") == D("0")


def test_shopify_with_payments_file():
    s = full()["channels"]["shopify"]
    # #1002 is 22:30 -0700 = 01:30 Oct 12 New York -> excluded
    assert s["orders"] == 2
    assert s["revenue"] == D("85.00")          # (2*20+10)+5 ship + 3*10
    assert s["discounts"] == D("5.00")
    assert s["refunds"] == D("10.00")
    assert s["processing_fees"] == D("3.17")   # reported 2.00 + 1.17
    assert s["cogs"] == D("30.00")             # 2*8 + 1*3.5 + 3*3.5
    assert s["shipping_cost"] == D("8.00")     # 2 orders * 4.00
    assert s["net_profit"] == D("28.83")       # 85-5-10-3.17-30-8
    assert s["tax_collected_excluded"] == D("3.60")


def test_shopify_estimated_fees_without_payments_file():
    s = full(shopify_payments=None)["channels"]["shopify"]
    # 53.60*2.9%+0.30 = 1.8544 -> 1.85 ; 30*2.9%+0.30 = 1.17
    assert s["processing_fees"] == D("3.02")
    assert s["net_profit"] == D("28.98")


def test_square():
    s = full()["channels"]["square"]
    assert s["orders"] == 2                   # FAKETXN3 is Oct 10
    assert s["revenue"] == D("32.00")         # 12 + 20
    assert s["discounts"] == D("2.00")
    assert s["refunds"] == D("5.00")
    assert s["processing_fees"] == D("1.04")  # 0.46 + 0.58
    assert s["cogs"] == D("11.50")            # 2*0.75 + 1.00 (by name) + 9.00
    assert s["tips_excluded"] == D("1.00")
    assert s["net_profit"] == D("12.46")      # 32-2-5-1.04-11.50


def test_total():
    assert full()["channels"]["total"]["net_profit"] == D("41.29")


def test_discrepancies():
    d = {x["ref"]: x for x in full()["payout_discrepancies"]}
    assert d["#1001"]["expected_net"] == D("51.75") and d["#1001"]["diff"] == D("-0.15") and d["#1001"]["flag"]
    assert d["#1003"]["expected_net"] == D("18.83") and not d["#1003"]["flag"]   # 30-10-1.17
    assert d["FAKETXN1"]["expected_net"] == D("11.34") and not d["FAKETXN1"]["flag"]  # 11.80-0.46
    assert d["FAKETXN2"]["expected_net"] == D("16.02") and d["FAKETXN2"]["diff"] == D("-0.10") and d["FAKETXN2"]["flag"]
    assert "items vs transactions gross sales" not in d


def test_missing_cost_warns():
    r = tp.run(date(2026, 10, 11), "America/New_York", square_tx=p("square_transactions.csv"),
               square_items=p("square_items.csv"), costs=None)
    assert r["channels"]["square"]["cogs"] == D("0.00")
    assert any("no unit cost" in w for w in r["warnings"])


def test_render_has_cta():
    out = tp.render(full())
    assert "PLACEHOLDER" in out and "sample-profit-report.html" in out
