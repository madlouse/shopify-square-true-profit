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
    assert s["orders"] == 3                    # #1001, #1003, #1004
    assert s["revenue"] == D("125.00")         # (2*20+10)+5 ship + 3*10 + 40
    assert s["discounts"] == D("5.00")
    assert s["refunds"] == D("10.00")          # only #1003's refund is dated Oct 11
    assert s["processing_fees"] == D("4.63")   # reported 2.00 + 1.46 + 1.17
    assert s["cogs"] == D("38.00")             # 2*8 + 3.5 + 3*3.5 + 8
    assert s["shipping_cost"] == D("12.00")    # 3 orders * 4.00
    assert s["net_profit"] == D("55.37")       # 125-5-10-4.63-38-12
    assert s["tax_collected_excluded"] == D("3.60")


def test_shopify_estimated_fees_with_transaction_history():
    s = full(shopify_payments=None, shopify_transactions=p("shopify_transactions_history.csv"))["channels"]["shopify"]
    # fees: 53.60*2.9%+0.30=1.8544->1.85 ; 30->1.17 ; 40->1.46  => 4.48
    assert s["processing_fees"] == D("4.48")
    assert s["refunds"] == D("10.00")          # refund dated by transaction 'Created At'
    assert s["net_profit"] == D("55.52")       # 125-5-10-4.48-38-12


def test_shopify_fallback_order_date_refunds_warns():
    r = full(shopify_payments=None)
    assert r["channels"]["shopify"]["refunds"] == D("25.00")   # 10 + 15 from 'Refunded Amount'
    assert r["channels"]["shopify"]["net_profit"] == D("40.52")  # 125-5-25-4.48-38-12
    assert any("ORDER date" in w for w in r["warnings"])


def test_cross_day_refund_shopify():
    # #1004: ordered Oct 11 (40.00), refunded 15.00 on Oct 12 09:00 -0400
    d1 = full()["channels"]["shopify"]
    assert d1["refunds"] == D("10.00")          # #1004's 15.00 NOT on Oct 11
    d2r = tp.run(date(2026, 10, 12), "America/New_York", shopify_orders=p("shopify_orders_export.csv"),
                 shopify_payments=p("shopify_payments_transactions.csv"), costs=p("costs.csv"))
    d2 = d2r["channels"]["shopify"]
    # Oct 12 holds #1002 (20.00, 1 TSHIRT, no payments row -> est fee 20*2.9%+0.30=0.88) + #1004 refund 15.00
    assert d2["orders"] == 1
    assert d2["revenue"] == D("20.00")
    assert d2["refunds"] == D("15.00")
    assert d2["processing_fees"] == D("0.88")
    assert d2["net_profit"] == D("-7.88")       # 20-15-0.88-8-4
    refs = {x["ref"]: x for x in d2r["payout_discrepancies"]}
    assert refs["#1004 refund"]["expected_net"] == D("-15.00") and not refs["#1004 refund"]["flag"]


def test_cross_day_refund_square():
    # FAKETXN1 paid Oct 11; cookie (4.00 + 0.32 tax) refunded Oct 12 as an Event Type=Refund row
    d1 = full()["channels"]["square"]
    assert d1["refunds"] == D("5.00")           # only FAKETXN2 partial refund
    d2 = tp.run(date(2026, 10, 12), "America/New_York", square_tx=p("square_transactions.csv"),
                square_items=p("square_items.csv"), costs=p("costs.csv"))["channels"]["square"]
    assert d2["orders"] == 0
    assert d2["refunds"] == D("4.00")
    assert d2["cogs"] == D("-1.00")             # returned cookie, qty -1 * 1.00
    assert d2["tax_collected_excluded"] == D("-0.32")
    assert d2["net_profit"] == D("-3.00")       # 0-0-4-0-(-1)


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
    assert full()["channels"]["total"]["net_profit"] == D("67.83")   # 55.37 + 12.46


def test_discrepancies():
    d = {x["ref"]: x for x in full()["payout_discrepancies"]}
    assert d["#1001 charge"]["expected_net"] == D("51.75") and d["#1001 charge"]["diff"] == D("-0.15") and d["#1001 charge"]["flag"]
    assert d["#1003 charge"]["expected_net"] == D("28.83") and not d["#1003 charge"]["flag"]
    assert d["#1003 refund"]["expected_net"] == D("-10.00") and not d["#1003 refund"]["flag"]
    assert d["#1004 charge"]["expected_net"] == D("38.54") and not d["#1004 charge"]["flag"]
    assert d["FAKETXN1"]["expected_net"] == D("11.34") and not d["FAKETXN1"]["flag"]  # 11.80-0.46
    assert d["FAKETXN2"]["expected_net"] == D("16.02") and d["FAKETXN2"]["diff"] == D("-0.10") and d["FAKETXN2"]["flag"]
    assert not any("vs order Total" in k or "items vs" in k for k in d)


def test_square_iana_timezone_label():
    r = {"Date": "2026-10-11", "Time": "23:30:00", "Time Zone": "America/Los_Angeles"}
    assert tp.sq_dt(r, tp.ZoneInfo("America/New_York")).astimezone(tp.ZoneInfo("America/New_York")).date() == date(2026, 10, 12)


def test_lineitem_sku_header_case_insensitive():
    assert tp.col({"Lineitem sku": "X"}, "Lineitem SKU") == "X"


def test_missing_cost_warns():
    r = tp.run(date(2026, 10, 11), "America/New_York", square_tx=p("square_transactions.csv"),
               square_items=p("square_items.csv"), costs=None)
    assert r["channels"]["square"]["cogs"] == D("0.00")
    assert any("no unit cost" in w for w in r["warnings"])


def test_render_has_cta():
    out = tp.render(full())
    assert "jeking.hwang2025@gmail.com" in out and "PLACEHOLDER" not in out
