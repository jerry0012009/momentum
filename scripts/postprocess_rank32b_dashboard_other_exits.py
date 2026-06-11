#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_recent_closed_trades.json"
REPORT = ROOT / "reports" / "site" / "factors" / "rank32b_canary" / "report.html"
MARKER = 'data-r32-other-exits="1"'

LABELS = {
    "manual_market_close": "手动平仓",
    "external_flat_reconciled": "外部/对账平仓",
    "exit_attach_failed_market_close": "止损挂单失败后平仓",
    "tp_attach_failed_market_close": "止盈挂单失败后平仓",
    "attach_failed_market_close": "保护单挂单失败平仓",
    "manual_close": "手动平仓",
}
BASE_REASONS = {"take_profit", "stop_loss", "timeout_market", "timeout_close"}


def main() -> None:
    if not ARTIFACT.exists() or not REPORT.exists():
        return
    rows = json.loads(ARTIFACT.read_text())
    counts = Counter(str(r.get("exit_reason") or "unknown") for r in rows)
    others = [(reason, count) for reason, count in counts.items() if reason not in BASE_REASONS and count > 0]
    others.sort(key=lambda x: (-x[1], x[0]))
    if not others:
        return
    parts = [f"{LABELS.get(reason, reason)} {count}" for reason, count in others]
    snippet = (
        '<br><span class="muted" style="font-size:12px" ' + MARKER + '>'
        + '其他退出：' + ' / '.join(parts) + '</span>'
    )

    html = REPORT.read_text(encoding="utf-8")
    # Remove existing injected snippet if present, then re-insert fresh counts.
    if MARKER in html:
        import re
        html = re.sub(r'<br><span class="muted" style="font-size:12px" data-r32-other-exits="1">.*?</span>', '', html, count=1)
    target = '自然退出结构'
    if target in html:
        html = html.replace(target, target + snippet, 1)
        REPORT.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
