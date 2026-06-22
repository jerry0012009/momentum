#!/usr/bin/env python3
"""Check factor library public URL availability and JSON validity.

Usage:
    python scripts/check_factor_library_public_url.py

Outputs:
    research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_public_url_check.csv
    research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_public_url_check.json
"""

import json
import re
import sys
from pathlib import Path

try:
    import urllib.request
    import urllib.error
    import ssl
except ImportError:
    print("urllib not available")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DIAG = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"

URLS = [
    "https://jp.jerrypsy.top/momentum/factor-library/",
    "https://jp.jerrypsy.top/momentum/factor-library/index.html",
    "https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html",
]


def check_url(url: str) -> dict:
    """Check a URL and return status info."""
    result = {"url": url, "status_code": None, "content_type": None, "error": None, "json_valid": None, "factor_count": None}
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "momentum-health-check/1.0")
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            result["status_code"] = resp.status
            result["content_type"] = resp.headers.get("Content-Type", "")
            body = resp.read().decode("utf-8", errors="ignore")
            # Check JSON validity for factor-evaluation page
            if "factor-evaluation" in url:
                m = re.search(r'<script id="factorPayload" type="application/json">(.*?)</script>', body, re.DOTALL)
                if m:
                    try:
                        data = json.loads(m.group(1))
                        result["json_valid"] = True
                        result["factor_count"] = len(data.get("factors", []))
                    except json.JSONDecodeError as e:
                        result["json_valid"] = False
                        result["error"] = f"JSON parse error: {e}"
                else:
                    result["json_valid"] = False
                    result["error"] = "factorPayload script tag not found"
    except urllib.error.HTTPError as e:
        result["status_code"] = e.code
        result["error"] = str(e)
    except Exception as e:
        result["error"] = str(e)
    return result


def main():
    results = []
    for url in URLS:
        r = check_url(url)
        status = "✓" if r["status_code"] == 200 and r.get("json_valid", True) else "✗"
        print(f'{status} {r["status_code"] or "ERR"} {url}')
        if r["json_valid"] is not None:
            print(f'   JSON valid: {r["json_valid"]}, factors: {r["factor_count"]}')
        if r["error"]:
            print(f'   Error: {r["error"]}')
        results.append(r)

    DIAG.mkdir(parents=True, exist_ok=True)

    # Write JSON
    (DIAG / "factor_library_public_url_check.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Write CSV
    import csv
    with open(DIAG / "factor_library_public_url_check.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "status_code", "content_type", "json_valid", "factor_count", "error"])
        w.writeheader()
        w.writerows(results)

    all_ok = all(
        r["status_code"] == 200 and (r["json_valid"] is None or r["json_valid"] is True)
        for r in results
    )
    print(f'\n{"ALL OK" if all_ok else "SOME CHECKS FAILED"}')
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
