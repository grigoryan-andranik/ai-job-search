#!/usr/bin/env python3
"""Salary currency conversion for /price: AMD, USD and EUR, monthly and yearly.

A /price report shows several salary figures in three currencies over two
periods - a lot of hand arithmetic, and exactly where a slip is expensive. An
exchange rate remembered from training data can also be a year stale. This
tool fetches the rate at run time and does every conversion in one place.

Rate sources, tried in order:
  1. Central Bank of Armenia (api.cba.am, ExchangeRatesLatest): the official
     AMD reference rate that Armenian employers and banks quote against.
  2. open.er-api.com (free, no key): fallback when the CBA service is down.
No rate is hardcoded. If both sources fail the tool exits 1 and says so.

Usage:
  python3 tools/fx_convert.py rates [--json]
  python3 tools/fx_convert.py table --currency AMD \
      --row "Walk-away=1500000" --row "Target=1900000" [--json]

Row amounts are MONTHLY figures in --currency. Yearly = monthly x 12; bonuses
and 13th-month pay are listed separately by /price, never assumed here.
--rates-file PATH reads {"source", "date", "AMD_per_USD", "AMD_per_EUR"} from a
JSON file instead of the network (tests, or re-rendering a saved report).

Exit 0 on success, 1 when no exchange rate is available, 2 on bad input.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

CBA_URL = "https://api.cba.am/exchangerates.asmx"
CBA_REQUEST = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
    '<soap:Body><ExchangeRatesLatest xmlns="http://www.cba.am/" /></soap:Body>'
    "</soap:Envelope>"
)
ERAPI_URL = "https://open.er-api.com/v6/latest/USD"
CURRENCIES = ("AMD", "USD", "EUR")
# Converted monthly figures are rounded to these steps. The row's own
# currency is shown exactly as entered, so the user's number never moves.
ROUND_STEP = {"AMD": 1000, "USD": 10, "EUR": 10}


def _curl(extra_args):
    """curl rather than urllib, for its hard --max-time ceiling (see robots_check.py)."""
    result = subprocess.run(
        ["curl", "-sS", "--max-time", "15"] + extra_args,
        capture_output=True, text=True, timeout=25,
    )
    if result.returncode != 0:
        raise RuntimeError("curl exit %d: %s" % (result.returncode, result.stderr.strip()[:200]))
    return result.stdout


def parse_cba(xml):
    """Parse a CBA ExchangeRatesLatest SOAP response into a rates dict.

    CBA quotes each rate per <Amount> units (JPY per 10, IRR per 100), so the
    per-unit rate is Rate / Amount.
    """
    date = re.search(r"<CurrentDate>(\d{4}-\d{2}-\d{2})", xml)
    if not date:
        raise ValueError("CBA response has no CurrentDate")
    per_unit = {}
    for block in re.findall(r"<ExchangeRate>(.*?)</ExchangeRate>", xml, re.S):
        iso = re.search(r"<ISO>([A-Z]{3})</ISO>", block)
        amount = re.search(r"<Amount>([\d.]+)</Amount>", block)
        rate = re.search(r"<Rate>([\d.]+)</Rate>", block)
        if iso and amount and rate and float(amount.group(1)) > 0:
            per_unit[iso.group(1)] = float(rate.group(1)) / float(amount.group(1))
    missing = [c for c in ("USD", "EUR") if not per_unit.get(c)]
    if missing:
        raise ValueError("CBA response has no rate for " + ", ".join(missing))
    return {
        "source": "Central Bank of Armenia (official rate)",
        "date": date.group(1),
        "AMD_per_USD": per_unit["USD"],
        "AMD_per_EUR": per_unit["EUR"],
    }


def parse_erapi(text):
    """Parse an open.er-api.com /latest/USD response into a rates dict."""
    data = json.loads(text)
    if data.get("result") != "success":
        raise ValueError("open.er-api.com returned result=%r" % data.get("result"))
    rates = data.get("rates") or {}
    amd, eur = rates.get("AMD"), rates.get("EUR")
    if not amd or not eur:
        raise ValueError("open.er-api.com response lacks AMD or EUR")
    stamp = data.get("time_last_update_unix")
    date = datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%d") if stamp else "unknown"
    return {
        "source": "open.er-api.com (fallback, market rate)",
        "date": date,
        "AMD_per_USD": float(amd),
        "AMD_per_EUR": float(amd) / float(eur),
    }


def fetch_rates():
    """Today's rates from CBA, falling back to open.er-api.com. Raises RuntimeError if both fail."""
    errors = []
    try:
        xml = _curl(["-H", "Content-Type: text/xml; charset=utf-8",
                     "-H", 'SOAPAction: "http://www.cba.am/ExchangeRatesLatest"',
                     "--data", CBA_REQUEST, "--", CBA_URL])
        return parse_cba(xml)
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        errors.append("CBA: %s" % exc)
    try:
        return parse_erapi(_curl(["--", ERAPI_URL]))
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        errors.append("open.er-api.com: %s" % exc)
    raise RuntimeError("; ".join(errors))


def load_rates_file(path):
    with open(path, encoding="utf-8") as fh:
        rates = json.load(fh)
    for key in ("AMD_per_USD", "AMD_per_EUR"):
        if not isinstance(rates.get(key), (int, float)) or rates[key] <= 0:
            raise ValueError("rates file needs a positive number for %s" % key)
    rates.setdefault("source", path)
    rates.setdefault("date", "unknown")
    return rates


def parse_amount(text):
    """'1,500,000' / '1 500 000' / '1_500_000' -> 1500000.0; rejects non-positive values."""
    cleaned = re.sub(r"[\s,_]", "", text)
    try:
        value = float(cleaned)
    except ValueError:
        raise ValueError("not a number: %r" % text) from None
    if value <= 0:
        raise ValueError("amount must be positive: %r" % text)
    return value


def parse_row(spec):
    label, sep, amount = spec.partition("=")
    if not sep or not label.strip():
        raise ValueError('row must look like "Label=amount", got %r' % spec)
    return label.strip(), parse_amount(amount)


def _round(value, step):
    return int(value / step + 0.5) * step


def convert(amount, currency, rates):
    """One monthly amount in `currency` -> {cur: {"month": n, "year": n}} for AMD, USD, EUR."""
    to_amd = {"AMD": 1.0, "USD": rates["AMD_per_USD"], "EUR": rates["AMD_per_EUR"]}
    amd = amount * to_amd[currency]
    out = {}
    for cur in CURRENCIES:
        if cur == currency:
            monthly = int(round(amount))
        else:
            monthly = _round(amd / to_amd[cur], ROUND_STEP[cur])
        out[cur] = {"month": monthly, "year": monthly * 12}
    return out


def rates_line(rates):
    return "Rates: %s, %s: 1 USD = %.2f AMD, 1 EUR = %.2f AMD" % (
        rates["source"], rates["date"], rates["AMD_per_USD"], rates["AMD_per_EUR"])


def render_table(rows, currency, rates):
    lines = [
        rates_line(rates),
        "Monthly figures entered in %s; yearly = monthly x 12. Converted amounts are rounded "
        "to the nearest 1,000 AMD / 10 USD / 10 EUR per month." % currency,
        "",
        "| | AMD / month | AMD / year | USD / month | USD / year | EUR / month | EUR / year |",
        "|---|---|---|---|---|---|---|",
    ]
    for label, amount in rows:
        conv = convert(amount, currency, rates)
        cells = []
        for cur in CURRENCIES:
            cells += ["{:,}".format(conv[cur]["month"]), "{:,}".format(conv[cur]["year"])]
        lines.append("| %s | %s |" % (label.replace("|", "\\|"), " | ".join(cells)))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="AMD / USD / EUR salary conversion for /price.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("rates", "table"):
        p = sub.add_parser(name)
        p.add_argument("--json", action="store_true", help="machine-readable output")
        p.add_argument("--rates-file", help="read rates from a JSON file instead of the network")
        if name == "table":
            p.add_argument("--currency", required=True, choices=CURRENCIES,
                           help="currency of the --row amounts")
            p.add_argument("--row", action="append", required=True, metavar="LABEL=MONTHLY_AMOUNT")
    args = parser.parse_args(argv)

    try:
        rows = [parse_row(r) for r in args.row] if args.command == "table" else []
        rates = load_rates_file(args.rates_file) if args.rates_file else None
    except (ValueError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if rates is None:
        try:
            rates = fetch_rates()
        except RuntimeError as exc:
            print("error: no exchange rate available (%s)" % exc, file=sys.stderr)
            return 1

    if args.command == "rates":
        print(json.dumps(rates, indent=2) if args.json else rates_line(rates))
    elif args.json:
        out = {"rates": rates, "input_currency": args.currency,
               "rows": [dict(label=label, **convert(amount, args.currency, rates)) for label, amount in rows]}
        print(json.dumps(out, indent=2))
    else:
        print(render_table(rows, args.currency, rates))
    return 0


if __name__ == "__main__":
    sys.exit(main())
