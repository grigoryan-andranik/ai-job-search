"""Tests for tools/fx_convert.py (the /price conversion tool). Network-free."""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOL = REPO_ROOT / "tools" / "fx_convert.py"
sys.path.insert(0, str(REPO_ROOT / "tools"))

import fx_convert  # noqa: E402

# Trimmed from a real api.cba.am ExchangeRatesLatest response (2026-09-10).
# JPY and IRR keep their real per-10 / per-100 <Amount> quoting.
CBA_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
    '<soap:Body><ExchangeRatesLatestResponse xmlns="http://www.cba.am/"><ExchangeRatesLatestResult>'
    '<CurrentDate>2026-09-10T00:00:00</CurrentDate><NextAvailableDate xsi:nil="true" />'
    '<PreviousAvailableDate>2026-09-09T00:00:00</PreviousAvailableDate><Rates>'
    '<ExchangeRate><ISO>USD</ISO><Amount>1</Amount><Rate>363.89</Rate><Difference>0.31</Difference></ExchangeRate>'
    '<ExchangeRate><ISO>JPY</ISO><Amount>10</Amount><Rate>24.51</Rate><Difference>0.02</Difference></ExchangeRate>'
    '<ExchangeRate><ISO>EUR</ISO><Amount>1</Amount><Rate>423.09</Rate><Difference>0.5</Difference></ExchangeRate>'
    '<ExchangeRate><ISO>IRR</ISO><Amount>100</Amount><Rate>0.87</Rate><Difference>0</Difference></ExchangeRate>'
    "</Rates></ExchangeRatesLatestResult></ExchangeRatesLatestResponse></soap:Body></soap:Envelope>"
)

# Shape of a real open.er-api.com /v6/latest/USD response (2026-09-11), rates trimmed.
ERAPI_RESPONSE = json.dumps({
    "result": "success", "base_code": "USD", "time_last_update_unix": 1789084951,
    "rates": {"USD": 1, "AMD": 363.834681, "EUR": 0.860738},
})

RATES = {"source": "test", "date": "2026-09-10", "AMD_per_USD": 363.89, "AMD_per_EUR": 423.09}


class ParseRatesTests(unittest.TestCase):
    def test_parse_cba_reads_usd_and_eur(self):
        rates = fx_convert.parse_cba(CBA_RESPONSE)
        self.assertEqual(rates["date"], "2026-09-10")
        self.assertAlmostEqual(rates["AMD_per_USD"], 363.89)
        self.assertAlmostEqual(rates["AMD_per_EUR"], 423.09)
        self.assertIn("Central Bank of Armenia", rates["source"])

    def test_parse_cba_divides_by_amount(self):
        xml = CBA_RESPONSE.replace("<Amount>1</Amount><Rate>363.89</Rate>", "<Amount>10</Amount><Rate>3638.9</Rate>")
        self.assertAlmostEqual(fx_convert.parse_cba(xml)["AMD_per_USD"], 363.89)

    def test_parse_cba_without_eur_is_an_error(self):
        xml = CBA_RESPONSE.replace("<ISO>EUR</ISO>", "<ISO>XXX</ISO>")
        with self.assertRaises(ValueError):
            fx_convert.parse_cba(xml)

    def test_parse_erapi_derives_amd_per_eur(self):
        rates = fx_convert.parse_erapi(ERAPI_RESPONSE)
        self.assertEqual(rates["date"], "2026-09-11")
        self.assertAlmostEqual(rates["AMD_per_USD"], 363.834681)
        self.assertAlmostEqual(rates["AMD_per_EUR"], 363.834681 / 0.860738)

    def test_parse_erapi_error_result_is_an_error(self):
        with self.assertRaises(ValueError):
            fx_convert.parse_erapi(json.dumps({"result": "error", "error-type": "quota-reached"}))

    def test_fetch_falls_back_when_cba_fails(self):
        def fake_curl(args):
            if fx_convert.CBA_URL in args:
                raise RuntimeError("curl exit 28: timeout")
            return ERAPI_RESPONSE
        with mock.patch.object(fx_convert, "_curl", side_effect=fake_curl):
            self.assertIn("open.er-api.com", fx_convert.fetch_rates()["source"])

    def test_fetch_raises_when_every_source_fails(self):
        with mock.patch.object(fx_convert, "_curl", side_effect=RuntimeError("offline")):
            with self.assertRaises(RuntimeError) as ctx:
                fx_convert.fetch_rates()
        self.assertIn("CBA", str(ctx.exception))
        self.assertIn("open.er-api.com", str(ctx.exception))


class ConvertTests(unittest.TestCase):
    def test_amd_row(self):
        out = fx_convert.convert(1_500_000, "AMD", RATES)
        self.assertEqual(out["AMD"], {"month": 1_500_000, "year": 18_000_000})
        self.assertEqual(out["USD"], {"month": 4_120, "year": 49_440})   # 4,122.13 -> 4,120
        self.assertEqual(out["EUR"], {"month": 3_550, "year": 42_600})   # 3,545.35 -> 3,550

    def test_usd_row_keeps_the_entered_amount(self):
        out = fx_convert.convert(5_000, "USD", RATES)
        self.assertEqual(out["USD"], {"month": 5_000, "year": 60_000})
        self.assertEqual(out["AMD"], {"month": 1_819_000, "year": 21_828_000})  # 1,819,450 -> 1,819,000
        self.assertEqual(out["EUR"], {"month": 4_300, "year": 51_600})          # 4,300.36 -> 4,300

    def test_parse_row_accepts_separators(self):
        self.assertEqual(fx_convert.parse_row("Opening ask=2,100,000"), ("Opening ask", 2_100_000.0))
        self.assertEqual(fx_convert.parse_row("Target = 1 900 000"), ("Target", 1_900_000.0))

    def test_parse_row_rejects_bad_input(self):
        for bad in ("Target", "=1000", "Target=-5", "Target=abc", "Target=0"):
            with self.assertRaises(ValueError, msg=bad):
                fx_convert.parse_row(bad)


class CliTests(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True)

    def test_table_through_the_documented_cli(self):
        with TemporaryDirectory() as tmp:
            rates_file = Path(tmp) / "rates.json"
            rates_file.write_text(json.dumps(RATES), encoding="utf-8")
            result = self.run_tool("table", "--currency", "AMD", "--row", "Walk-away=1500000",
                                   "--row", "Target=1,900,000", "--rates-file", str(rates_file))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 USD = 363.89 AMD, 1 EUR = 423.09 AMD", result.stdout)
        self.assertIn("| Walk-away | 1,500,000 | 18,000,000 | 4,120 | 49,440 | 3,550 | 42,600 |", result.stdout)
        self.assertIn("| Target | 1,900,000 | 22,800,000 |", result.stdout)

    def test_json_output(self):
        with TemporaryDirectory() as tmp:
            rates_file = Path(tmp) / "rates.json"
            rates_file.write_text(json.dumps(RATES), encoding="utf-8")
            result = self.run_tool("table", "--currency", "USD", "--row", "Ask=5000",
                                   "--rates-file", str(rates_file), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["rows"][0]["label"], "Ask")
        self.assertEqual(data["rows"][0]["AMD"]["month"], 1_819_000)

    def test_bad_row_exits_2(self):
        result = self.run_tool("table", "--currency", "AMD", "--row", "Target=abc",
                               "--rates-file", "/nonexistent.json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a number", result.stderr)


if __name__ == "__main__":
    unittest.main()
