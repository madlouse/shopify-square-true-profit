#!/usr/bin/env python3
"""shopify-square-true-profit v1 -- read-only daily true-profit + payout discrepancy report.

Reads local CSV exports only (Shopify orders, optional Shopify Payments transactions,
Square transactions, Square item details, costs.csv). Never writes, never calls a network.
All arithmetic uses decimal.Decimal.
"""
from __future__ import annotations
import argparse, csv, json, sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from zoneinfo import ZoneInfo

CENT = Decimal("0.01")
ZERO = Decimal("0")
TOLERANCE = Decimal("0.01")
CTA = ("Want this delivered to your inbox every morning? Profit daily report done-for-you service "
       "[PLACEHOLDER LINK]: https://madlouse.github.io/toolstack-lab/tools/sample-profit-report.html")

# Square exports label zones with Rails-style names; map the common US ones.
SQUARE_TZ = {
    "Eastern Time (US & Canada)": "America/New_York", "Central Time (US & Canada)": "America/Chicago",
    "Mountain Time (US & Canada)": "America/Denver", "Arizona": "America/Phoenix",
    "Pacific Time (US & Canada)": "America/Los_Angeles", "Alaska": "America/Anchorage",
    "Hawaii": "Pacific/Honolulu", "UTC": "UTC", "London": "Europe/London",
    "Sydney": "Australia/Sydney", "Tokyo": "Asia/Tokyo",
}


def money(s) -> Decimal:
    """Parse '$1,234.50', '-$2.00', '($5.00)', '' -> Decimal."""
    if s is None:
        return ZERO
    t = str(s).strip()
    if not t:
        return ZERO
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()").replace("$", "").replace(",", "").replace(" ", "")
    for sym in ("€", "£", "A", "C", "¥"):
        t = t.replace(sym, "")
    try:
        v = Decimal(t)
    except InvalidOperation:
        raise ValueError(f"cannot parse money value: {s!r}")
    return -v if neg else v


def q(v: Decimal) -> Decimal:
    return v.quantize(CENT, rounding=ROUND_HALF_UP)


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_costs(path):
    cogs, fee_pct, fee_fixed, ship = {}, {}, {}, {}
    if not path:
        return {"cogs": cogs, "fee_pct": fee_pct, "fee_fixed": fee_fixed, "shipping_cost": ship}
    for r in read_csv(path):
        kind = (r.get("kind") or "cogs").strip().lower()
        key = (r.get("key") or r.get("sku") or "").strip()
        val = Decimal((r.get("value") or r.get("unit_cost") or "0").strip())
        {"cogs": cogs, "fee_pct": fee_pct, "fee_fixed": fee_fixed, "shipping_cost": ship}[kind][
            key if kind == "cogs" else key.lower()] = val
    return {"cogs": cogs, "fee_pct": fee_pct, "fee_fixed": fee_fixed, "shipping_cost": ship}


def est_fee(costs, channel, amount):
    pct = costs["fee_pct"].get(channel)
    fixed = costs["fee_fixed"].get(channel, ZERO)
    if pct is None:
        return None
    return q(amount * pct / Decimal(100) + fixed)


def unit_cost(costs, sku, name, warnings, channel):
    for k in (sku, name):
        if k and k in costs["cogs"]:
            return costs["cogs"][k]
    warnings.append(f"{channel}: no unit cost for sku={sku!r} item={name!r}; COGS counted as 0")
    return ZERO


def blank():
    return {k: ZERO for k in ("revenue", "discounts", "refunds", "processing_fees", "cogs",
                              "shipping_cost", "net_profit")} | {"orders": 0, "tax_collected_excluded": ZERO,
                                                                  "tips_excluded": ZERO}


# ---------------- Shopify ----------------
def shopify(orders_csv, payments_csv, costs, day, tz, warnings, discrepancies):
    rows = read_csv(orders_csv)
    orders = {}
    for r in rows:
        name = r["Name"].strip()
        o = orders.setdefault(name, {"lines": [], "head": None})
        if r.get("Financial Status", "").strip():
            o["head"] = r
        o["lines"].append(r)
    pay = defaultdict(lambda: {"charge": ZERO, "fee": ZERO, "net": ZERO, "refund_net": ZERO})
    have_pay = bool(payments_csv)
    if have_pay:
        for p in read_csv(payments_csv):
            d = pay[p["Order"].strip()]
            t = p["Type"].strip().lower()
            if t == "charge":
                d["charge"] += money(p["Amount"]); d["fee"] += money(p["Fee"]); d["net"] += money(p["Net"])
            elif t == "refund":
                d["refund_net"] += money(p["Net"]); d["fee"] += money(p["Fee"])
    s = blank()
    for name, o in orders.items():
        h = o["head"]
        if h is None:
            warnings.append(f"shopify: order {name} has no header row; skipped"); continue
        created = datetime.strptime(h["Created at"].strip(), "%Y-%m-%d %H:%M:%S %z").astimezone(tz)
        if created.date() != day or h["Financial Status"].strip().lower() in ("voided", "pending"):
            continue
        s["orders"] += 1
        items = sum((money(l["Lineitem price"]) * Decimal(l["Lineitem quantity"]) for l in o["lines"]), ZERO)
        shipping = money(h["Shipping"])
        total, refunded, disc = money(h["Total"]), money(h["Refunded Amount"]), money(h["Discount Amount"])
        s["revenue"] += items + shipping
        s["discounts"] += disc
        s["refunds"] += refunded
        s["tax_collected_excluded"] += money(h["Taxes"])
        for l in o["lines"]:
            s["cogs"] += unit_cost(costs, l["Lineitem sku"].strip(), l["Lineitem name"].strip(),
                                   warnings, "shopify") * Decimal(l["Lineitem quantity"])
        s["shipping_cost"] += costs["shipping_cost"].get("shopify", ZERO)
        expected_fee = est_fee(costs, "shopify", total)
        if have_pay and name in pay:
            fee = pay[name]["fee"]
            reported = pay[name]["net"] + pay[name]["refund_net"]
            exp_fee = expected_fee if expected_fee is not None else fee
            expected = total - refunded - exp_fee
            diff = reported - expected
            discrepancies.append({"channel": "shopify", "ref": name, "expected_net": q(expected),
                                  "reported_net": q(reported), "diff": q(diff),
                                  "flag": abs(diff) >= TOLERANCE})
            if pay[name]["charge"] != total:
                discrepancies.append({"channel": "shopify", "ref": name + " (charge amount)",
                                      "expected_net": q(total), "reported_net": q(pay[name]["charge"]),
                                      "diff": q(pay[name]["charge"] - total), "flag": True})
        else:
            if have_pay:
                warnings.append(f"shopify: order {name} missing from payments file")
            fee = expected_fee if expected_fee is not None else ZERO
            if expected_fee is None:
                warnings.append("shopify: no payments file and no fee_pct override; fees counted as 0")
        s["processing_fees"] += fee
    return s


# ---------------- Square ----------------
def sq_dt(r, default_tz):
    tzname = SQUARE_TZ.get(r.get("Time Zone", "").strip())
    src = ZoneInfo(tzname) if tzname else default_tz
    return datetime.strptime(f'{r["Date"].strip()} {r["Time"].strip()}', "%Y-%m-%d %H:%M:%S").replace(tzinfo=src)


def square(tx_csv, items_csv, costs, day, tz, warnings, discrepancies):
    s = blank()
    txids, gross_tx = set(), ZERO
    for r in read_csv(tx_csv):
        if sq_dt(r, tz).astimezone(tz).date() != day:
            continue
        s["orders"] += 1
        txids.add(r["Transaction ID"].strip())
        gross = money(r["Gross Sales"]); gross_tx += gross
        s["revenue"] += gross + money(r.get("Service Charges"))
        s["discounts"] += -money(r["Discounts"])
        s["refunds"] += -money(r["Partial Refunds"])
        fees = -money(r["Fees"])
        s["processing_fees"] += fees
        s["tax_collected_excluded"] += money(r["Tax"])
        s["tips_excluded"] += money(r["Tip"])
        collected = money(r["Total Collected"])
        reported = money(r["Net Total"])
        exp_fee = est_fee(costs, "square", collected)
        expected = collected - (exp_fee if exp_fee is not None else fees)
        diff = reported - expected
        discrepancies.append({"channel": "square", "ref": r["Transaction ID"].strip(),
                              "expected_net": q(expected), "reported_net": q(reported), "diff": q(diff),
                              "flag": abs(diff) >= TOLERANCE})
    gross_items = ZERO
    if items_csv:
        for r in read_csv(items_csv):
            if r["Transaction ID"].strip() not in txids:
                continue
            gross_items += money(r["Gross Sales"])
            s["cogs"] += unit_cost(costs, r.get("SKU", "").strip(), r["Item"].strip(), warnings, "square") \
                * Decimal(r["Qty"].strip() or "0")
        if gross_items != gross_tx:
            discrepancies.append({"channel": "square", "ref": "items vs transactions gross sales",
                                  "expected_net": q(gross_tx), "reported_net": q(gross_items),
                                  "diff": q(gross_items - gross_tx), "flag": True})
    else:
        warnings.append("square: no item details CSV; COGS counted as 0")
    return s


def finish(s):
    s["net_profit"] = (s["revenue"] - s["discounts"] - s["refunds"] - s["processing_fees"]
                       - s["cogs"] - s["shipping_cost"])
    return {k: (q(v) if isinstance(v, Decimal) else v) for k, v in s.items()}


def run(day, tzname, shopify_orders=None, shopify_payments=None, square_tx=None, square_items=None, costs=None):
    tz = ZoneInfo(tzname)
    c = load_costs(costs)
    warnings, disc, channels = [], [], {}
    if shopify_orders:
        channels["shopify"] = finish(shopify(shopify_orders, shopify_payments, c, day, tz, warnings, disc))
    if square_tx:
        channels["square"] = finish(square(square_tx, square_items, c, day, tz, warnings, disc))
    total = blank()
    for ch in channels.values():
        for k in total:
            total[k] += ch[k]
    channels["total"] = {k: (q(v) if isinstance(v, Decimal) else v) for k, v in total.items()}
    return {"date": day.isoformat(), "timezone": tzname, "channels": channels,
            "payout_discrepancies": disc, "warnings": sorted(set(warnings)), "cta": CTA}


FIELDS = ["orders", "revenue", "discounts", "refunds", "processing_fees", "cogs", "shipping_cost", "net_profit"]


def render(rep):
    chs = list(rep["channels"])
    out = [f"# True profit for {rep['date']} ({rep['timezone']})", "",
           "| metric | " + " | ".join(chs) + " |", "|---" * (len(chs) + 1) + "|"]
    for f in FIELDS + ["tax_collected_excluded", "tips_excluded"]:
        out.append(f"| {f} | " + " | ".join(str(rep["channels"][c][f]) for c in chs) + " |")
    out += ["", "## Payout discrepancies (expected vs reported net)", "",
            "| channel | ref | expected | reported | diff | flag |", "|---|---|---|---|---|---|"]
    for d in rep["payout_discrepancies"]:
        out.append(f"| {d['channel']} | {d['ref']} | {d['expected_net']} | {d['reported_net']} | {d['diff']} | "
                   f"{'FLAG' if d['flag'] else 'ok'} |")
    if rep["warnings"]:
        out += ["", "## Warnings", ""] + [f"- {w}" for w in rep["warnings"]]
    out += ["", "---", rep["cta"]]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", help="YYYY-MM-DD in merchant timezone (default: yesterday)")
    ap.add_argument("--tz", required=True, help="merchant IANA timezone, e.g. America/New_York")
    ap.add_argument("--shopify-orders"); ap.add_argument("--shopify-payments")
    ap.add_argument("--square-transactions"); ap.add_argument("--square-items")
    ap.add_argument("--costs"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    day = date.fromisoformat(a.date) if a.date else (datetime.now(ZoneInfo(a.tz)).date() - timedelta(days=1))
    rep = run(day, a.tz, a.shopify_orders, a.shopify_payments, a.square_transactions, a.square_items, a.costs)
    if a.json:
        print(json.dumps(rep, default=str, indent=2))
    else:
        print(render(rep))


if __name__ == "__main__":
    sys.exit(main())
