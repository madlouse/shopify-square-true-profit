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
CTA_URL = "https://madlouse.github.io/toolstack-lab/tools/sample-profit-report.html"
CTA = ("Want this delivered every morning? See Toolstack Lab's profit daily report done-for-you service: "
       + CTA_URL)

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
def col(row, *names):
    """Case-insensitive header lookup (doc says 'Lineitem SKU'; some exports write 'Lineitem sku')."""
    low = {k.strip().lower(): v for k, v in row.items() if k}
    for n in names:
        if n.lower() in low:
            return (low[n.lower()] or "").strip()
    return ""


def sh_dt(text, tz):
    return datetime.strptime(text.strip(), "%Y-%m-%d %H:%M:%S %z").astimezone(tz)


def shopify(orders_csv, payments_csv, tx_history_csv, costs, day, tz, warnings, discrepancies):
    """Sales/discounts/COGS on order 'Created at' date; refunds and actual fees on the date of the
    refund/fee transaction (Shopify Payments 'Transaction Date' or transaction-history 'Created At')."""
    orders = {}
    for r in read_csv(orders_csv):
        o = orders.setdefault(col(r, "Name"), {"lines": [], "head": None})
        if col(r, "Financial Status"):
            o["head"] = r
        o["lines"].append(r)
    s = blank()
    pay_rows = read_csv(payments_csv) if payments_csv else []
    pay_orders = {col(p, "Order") for p in pay_rows if col(p, "Type").lower() == "charge"}
    day_totals = {}
    for name, o in orders.items():
        h = o["head"]
        if h is None:
            warnings.append(f"shopify: order {name} has no header row; skipped"); continue
        if sh_dt(col(h, "Created at"), tz).date() != day or col(h, "Financial Status").lower() in ("voided", "pending"):
            continue
        s["orders"] += 1
        items = sum((money(col(l, "Lineitem price")) * Decimal(col(l, "Lineitem quantity")) for l in o["lines"]), ZERO)
        total = money(col(h, "Total"))
        day_totals[name] = total
        s["revenue"] += items + money(col(h, "Shipping"))
        s["discounts"] += money(col(h, "Discount Amount"))
        s["tax_collected_excluded"] += money(col(h, "Taxes"))
        for l in o["lines"]:
            s["cogs"] += unit_cost(costs, col(l, "Lineitem SKU"), col(l, "Lineitem name"), warnings, "shopify") \
                * Decimal(col(l, "Lineitem quantity"))
        s["shipping_cost"] += costs["shipping_cost"].get("shopify", ZERO)
        if not payments_csv or name not in pay_orders:
            if payments_csv:
                warnings.append(f"shopify: order {name} missing from payments file; fee estimated")
            fee = est_fee(costs, "shopify", total)
            if fee is None:
                warnings.append("shopify: no payments file and no fee_pct override; fees counted as 0"); fee = ZERO
            s["processing_fees"] += fee
        if not payments_csv and not tx_history_csv:
            # fallback only: the orders export has no refund date column
            refunded = money(col(h, "Refunded Amount"))
            if refunded:
                s["refunds"] += refunded
                warnings.append("shopify: no payments/transaction-history file; refunds counted on ORDER date "
                                "(supply one of them for refund-date accounting)")
    if payments_csv:
        for p in pay_rows:
            if sh_dt(col(p, "Transaction Date"), tz).date() != day:
                continue
            t, ref = col(p, "Type").lower(), col(p, "Order")
            amount, fee, net = money(col(p, "Amount")), money(col(p, "Fee")), money(col(p, "Net"))
            s["processing_fees"] += fee
            if t == "refund":
                s["refunds"] += -amount
            exp_fee = est_fee(costs, "shopify", amount) if t == "charge" else None
            expected = amount - (exp_fee if exp_fee is not None else fee)
            diff = net - expected
            discrepancies.append({"channel": "shopify", "ref": f"{ref} {t}", "expected_net": q(expected),
                                  "reported_net": q(net), "diff": q(diff), "flag": abs(diff) >= TOLERANCE})
            if t == "charge" and ref in day_totals and day_totals[ref] != amount:
                discrepancies.append({"channel": "shopify", "ref": f"{ref} charge vs order Total",
                                      "expected_net": q(day_totals[ref]), "reported_net": q(amount),
                                      "diff": q(amount - day_totals[ref]), "flag": True})
    elif tx_history_csv:
        for r in read_csv(tx_history_csv):
            if col(r, "Kind").lower() == "refund" and col(r, "Status").lower() == "success" \
                    and sh_dt(col(r, "Created At"), tz).date() == day:
                s["refunds"] += abs(money(col(r, "Amount")))
    return s


# ---------------- Square (BETA) ----------------
SQ_TX_REQUIRED = ["Date", "Time", "Gross Sales", "Discounts", "Net Sales", "Tax", "Tip", "Partial Refunds",
                  "Total Collected", "Fees", "Net Total", "Transaction ID"]
SQ_TX_OPTIONAL = ["Time Zone", "Service Charges", "Event Type"]
SQ_ITEMS_REQUIRED = ["Date", "Time", "Item", "Qty", "Gross Sales", "Transaction ID"]
SQ_ITEMS_OPTIONAL = ["Time Zone", "SKU"]
SQ_ISSUES = "Square support is beta; please open an issue with a redacted sample export header row."


class SquareFormatError(ValueError):
    pass


def check_square_headers(path, required, optional, label):
    with open(path, newline="", encoding="utf-8-sig") as f:
        headers = [h.strip() for h in (next(csv.reader(f), []))]
    missing = [c for c in required if c not in headers]
    if missing:
        known = set(required) | set(optional)
        unknown = [h for h in headers if h and h not in known]
        raise SquareFormatError(
            f"{label} CSV {path!r} is missing required column(s): {', '.join(missing)}. "
            f"Unrecognized header(s) in file: {', '.join(unknown) or '(none)'}. {SQ_ISSUES}")



def sq_dt(r, default_tz):
    label = r.get("Time Zone", "").strip()
    tzname = SQUARE_TZ.get(label)
    if not tzname and "/" in label:  # some exports use IANA names, e.g. America/Detroit
        tzname = label
    try:
        src = ZoneInfo(tzname) if tzname else default_tz
    except Exception:
        src = default_tz
    return datetime.strptime(f'{r["Date"].strip()} {r["Time"].strip()}', "%Y-%m-%d %H:%M:%S").replace(tzinfo=src)


def square(tx_csv, items_csv, costs, day, tz, warnings, discrepancies):
    check_square_headers(tx_csv, SQ_TX_REQUIRED, SQ_TX_OPTIONAL, "Square transactions")
    if items_csv:
        check_square_headers(items_csv, SQ_ITEMS_REQUIRED, SQ_ITEMS_OPTIONAL, "Square item details")
    s = blank()
    txids, gross_tx = set(), ZERO
    for r in read_csv(tx_csv):
        if sq_dt(r, tz).astimezone(tz).date() != day:
            continue
        txids.add(r["Transaction ID"].strip())
        gross = money(r["Gross Sales"]); gross_tx += gross
        if (r.get("Event Type") or "Payment").strip().lower() == "refund":
            # refund rows are dated on the refund date and carry negative amounts
            s["refunds"] += -money(r["Net Sales"]) - money(r["Partial Refunds"])
        else:
            s["orders"] += 1
            s["revenue"] += gross + money(r.get("Service Charges"))
            s["discounts"] += -money(r["Discounts"])
            s["refunds"] += -money(r["Partial Refunds"])
        fees = -money(r["Fees"])
        s["processing_fees"] += fees
        s["tax_collected_excluded"] += money(r["Tax"])
        s["tips_excluded"] += money(r["Tip"])
        collected = money(r["Total Collected"])
        reported = money(r["Net Total"])
        is_refund = (r.get("Event Type") or "").strip().lower() == "refund"
        exp_fee = None if is_refund else est_fee(costs, "square", collected)
        expected = collected - (exp_fee if exp_fee is not None else fees)
        diff = reported - expected
        discrepancies.append({"channel": "square", "ref": r["Transaction ID"].strip(),
                              "expected_net": q(expected), "reported_net": q(reported), "diff": q(diff),
                              "flag": abs(diff) >= TOLERANCE})
    gross_items = ZERO
    if items_csv:
        for r in read_csv(items_csv):
            if r["Transaction ID"].strip() not in txids or sq_dt(r, tz).astimezone(tz).date() != day:
                continue
            gross_items += money(r["Gross Sales"])
            s["cogs"] += unit_cost(costs, r.get("SKU", "").strip(), r["Item"].strip(), warnings, "square") \
                * Decimal(r["Qty"].strip() or "0")
        if gross_items != gross_tx:  # compares signed gross incl. refund rows
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


def run(day, tzname, shopify_orders=None, shopify_payments=None, square_tx=None, square_items=None, costs=None,
        shopify_transactions=None):
    tz = ZoneInfo(tzname)
    c = load_costs(costs)
    warnings, disc, channels = [], [], {}
    if shopify_orders:
        channels["shopify"] = finish(shopify(shopify_orders, shopify_payments, shopify_transactions, c, day, tz, warnings, disc))
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
    ap.add_argument("--shopify-transactions", help="Orders > Export transaction histories CSV (refund dates)")
    ap.add_argument("--square-transactions"); ap.add_argument("--square-items")
    ap.add_argument("--costs"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    day = date.fromisoformat(a.date) if a.date else (datetime.now(ZoneInfo(a.tz)).date() - timedelta(days=1))
    try:
        rep = run(day, a.tz, a.shopify_orders, a.shopify_payments, a.square_transactions, a.square_items, a.costs,
              a.shopify_transactions)
    except SquareFormatError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(rep, default=str, indent=2))
    else:
        print(render(rep))


if __name__ == "__main__":
    sys.exit(main())
