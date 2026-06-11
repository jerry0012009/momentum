#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_symbol_diagnostics"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_symbol_diagnostics"
IMG_DIR = SITE_DIR / "images"

TARGET_SYMBOLS = ["BTCUSDT", "ETHUSDT", "PIPPINUSDT", "BEATUSDT"]
SOURCE_FILES = {
    "live_canary": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_recent_closed_trades.json",
    "shadow_beat": ROOT / "reports" / "artifacts" / "rank32b_shadow_beat" / "paper_closed_trades.json",
    "shadow_global": ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "paper_closed_trades.json",
}
SOURCE_LABELS = {
    "live_canary": "实盘 live canary",
    "shadow_beat": "Alt shadow beat",
    "shadow_global": "Global strongest-only shadow",
}
SOURCE_COLORS = {
    "live_canary": "#2563eb",
    "shadow_beat": "#dc2626",
    "shadow_global": "#16a34a",
}


@dataclass
class SummaryRow:
    symbol: str
    source: str
    label: str
    trades: int
    win_rate: float | None
    total_return: float | None
    avg_return: float | None
    sharpe_trade: float | None
    first_ts: str | None
    last_ts: str | None


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return data
    return []


def coerce_return(row: dict[str, Any]) -> float | None:
    for key in ["net_ret", "paper_effective_net_ret"]:
        value = row.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except Exception:
            continue
    value = row.get("net_return_bps")
    if value is not None:
        try:
            return float(value) / 10000.0
        except Exception:
            pass
    try:
        entry_price = float(row.get("entry_price"))
        qty = float(row.get("qty"))
        pnl = row.get("net_pnl") if row.get("net_pnl") is not None else row.get("gross_pnl")
        if pnl is None:
            return None
        notional = abs(entry_price * qty)
        if notional <= 0:
            return None
        return float(pnl) / notional
    except Exception:
        return None


def coerce_exit_ts(row: dict[str, Any]) -> pd.Timestamp | None:
    for key in ["exit_time", "exit_ts", "mark_ts", "entry_time", "entry_ts"]:
        value = row.get(key)
        if value:
            ts = pd.to_datetime(value, utc=True, errors="coerce")
            if pd.notna(ts):
                return ts
    return None


def trade_sharpe(returns: list[float]) -> float | None:
    if len(returns) < 5:
        return None
    series = pd.Series(returns, dtype=float)
    std = float(series.std(ddof=0))
    if std <= 0:
        return None
    return float((series.mean() / std) * math.sqrt(len(series)))


def build_frames() -> tuple[dict[str, dict[str, pd.DataFrame]], list[SummaryRow]]:
    symbol_frames: dict[str, dict[str, pd.DataFrame]] = {symbol: {} for symbol in TARGET_SYMBOLS}
    summaries: list[SummaryRow] = []
    for source, path in SOURCE_FILES.items():
        rows = load_json(path)
        for symbol in TARGET_SYMBOLS:
            selected: list[dict[str, Any]] = []
            for row in rows:
                if str(row.get("symbol") or "").upper() != symbol:
                    continue
                ret = coerce_return(row)
                ts = coerce_exit_ts(row)
                if ret is None or ts is None:
                    continue
                selected.append({
                    "symbol": symbol,
                    "source": source,
                    "label": SOURCE_LABELS[source],
                    "exit_ts": ts,
                    "ret": ret,
                    "side": row.get("side"),
                    "exit_reason": row.get("exit_reason"),
                })
            if not selected:
                continue
            frame = pd.DataFrame(selected).sort_values("exit_ts").reset_index(drop=True)
            frame["cum_return"] = (1.0 + frame["ret"].astype(float)).cumprod() - 1.0
            frame["trade_idx"] = frame.index + 1
            symbol_frames[symbol][source] = frame
            returns = frame["ret"].astype(float)
            summaries.append(
                SummaryRow(
                    symbol=symbol,
                    source=source,
                    label=SOURCE_LABELS[source],
                    trades=int(len(frame)),
                    win_rate=float((returns > 0).mean()) if len(frame) else None,
                    total_return=float(frame["cum_return"].iloc[-1]) if len(frame) else None,
                    avg_return=float(returns.mean()) if len(frame) else None,
                    sharpe_trade=trade_sharpe(returns.tolist()),
                    first_ts=frame["exit_ts"].iloc[0].strftime("%Y-%m-%d %H:%M UTC"),
                    last_ts=frame["exit_ts"].iloc[-1].strftime("%Y-%m-%d %H:%M UTC"),
                )
            )
    return symbol_frames, summaries


def pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{x * 100:.2f}%"


def num(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{x:.3f}"


def plot_symbol(symbol: str, frames: dict[str, pd.DataFrame]) -> str | None:
    if not frames:
        return None
    ensure_dir(IMG_DIR)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for source, frame in frames.items():
        ax.plot(frame["exit_ts"], frame["cum_return"] * 100.0, marker="o", linewidth=2, markersize=4, label=SOURCE_LABELS[source], color=SOURCE_COLORS[source])
    ax.axhline(0.0, color="#64748b", linewidth=1, linestyle="--")
    ax.set_title(f"{symbol}: cumulative net return by close time", fontsize=13)
    ax.set_ylabel("Cumulative return %")
    ax.set_xlabel("Close time")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.autofmt_xdate()
    out = IMG_DIR / f"{symbol.lower()}_cumret.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out.name


def render_html(symbol_frames: dict[str, dict[str, pd.DataFrame]], summaries: list[SummaryRow]) -> str:
    generated_at = pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    summary_df = pd.DataFrame([row.__dict__ for row in summaries])
    cards: list[str] = []
    for symbol in TARGET_SYMBOLS:
        frames = symbol_frames.get(symbol, {})
        image_name = plot_symbol(symbol, frames)
        rows_html = []
        if not frames:
            rows_html.append("<tr><td colspan='7'>当前可读到的 recent closed trades 里没有这个币的样本。</td></tr>")
        else:
            for _, row in summary_df.loc[summary_df["symbol"] == symbol].sort_values("source").iterrows():
                rows_html.append(
                    f"<tr><td>{row['label']}</td><td>{int(row['trades'])}</td><td>{pct(row['win_rate'])}</td><td>{pct(row['total_return'])}</td><td>{pct(row['avg_return'])}</td><td>{num(row['sharpe_trade'])}</td><td>{row['first_ts']} → {row['last_ts']}</td></tr>"
                )
        note = ""
        if symbol == "BEATUSDT":
            note = "<p class='insight bad'>这段样本里，BEAT 在 live canary 亏损最重；如果你主观体感是‘32b 最近一直在抽脸’，这个币确实是高嫌疑拖累项。</p>"
        elif symbol == "PIPPINUSDT":
            note = "<p class='insight bad'>PIPPIN 在 live 和 shadow 两边都偏弱，不像只是执行滑点问题，更像信号本身在这个名字上噪音偏大。</p>"
        elif symbol in {"BTCUSDT", "ETHUSDT"}:
            note = "<p class='insight ok'>BTC/ETH 并没有表现出‘特别能赚钱’，但至少从这段样本看，它们不像 BEAT/PIPPIN 那样是主要亏损黑洞。</p>"
        image_html = f"<img src='images/{image_name}' alt='{symbol} cumulative return chart'>" if image_name else "<div class='empty'>暂无可画曲线的数据</div>"
        cards.append(
            f"""
            <section class='card'>
              <h2>{symbol}</h2>
              {note}
              <div class='chart'>{image_html}</div>
              <div class='table-wrap'>
                <table>
                  <thead>
                    <tr><th>数据口径</th><th>笔数</th><th>胜率</th><th>累计收益</th><th>单笔均值</th><th>Trade Sharpe</th><th>样本区间</th></tr>
                  </thead>
                  <tbody>
                    {''.join(rows_html)}
                  </tbody>
                </table>
              </div>
            </section>
            """
        )
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Rank32b 币种诊断：BTC / ETH / PIPPIN / BEAT</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    .sub {{ color: #475569; margin-bottom: 18px; }}
    .lead {{ background: #ffffff; border-radius: 16px; padding: 16px 18px; box-shadow: 0 1px 3px rgba(0,0,0,.08); margin-bottom: 18px; line-height: 1.6; }}
    .card {{ background: #ffffff; border-radius: 16px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,.08); margin-bottom: 18px; }}
    .chart img {{ width: 100%; border-radius: 12px; border: 1px solid #e2e8f0; background: #fff; }}
    .table-wrap {{ overflow-x: auto; margin-top: 12px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #e2e8f0; padding: 10px 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f8fafc; }}
    .insight {{ padding: 10px 12px; border-radius: 12px; }}
    .insight.bad {{ background: #fff1f2; color: #9f1239; }}
    .insight.ok {{ background: #eff6ff; color: #1d4ed8; }}
    .muted {{ color: #64748b; }}
    .empty {{ padding: 24px; border: 1px dashed #cbd5e1; border-radius: 12px; color: #64748b; text-align: center; }}
    code {{ background: #e2e8f0; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <div class='wrap'>
    <h1>Rank32b 币种诊断：BTC / ETH / PIPPIN / BEAT</h1>
    <div class='sub'>生成时间：{generated_at}</div>
    <div class='lead'>
      <p>这页不是“吹收益”，而是专门回答一个很实际的问题：<strong>32b 最近亏，到底是策略整体失效，还是少数币在拖后腿？</strong></p>
      <p>口径说明：</p>
      <ul>
        <li><code>live canary</code> = 当前 rank32b 实盘 recent closed trades</li>
        <li><code>shadow beat</code> = Alt shadow sidecar（更偏小币/alt）</li>
        <li><code>shadow global</code> = Global strongest-only shadow（全池最强 1 个）</li>
        <li>Sharpe 这里用的是<strong>逐笔 trade Sharpe</strong>，是样本内粗诊断，不是年化基金宣传口径</li>
      </ul>
      <p class='muted'>如果某条线样本笔数太少，Sharpe 会直接隐藏；重点还是看累计收益曲线是不是一路向下。</p>
    </div>
    {''.join(cards)}
  </div>
</body>
</html>
"""


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(IMG_DIR)
    symbol_frames, summaries = build_frames()
    summary_df = pd.DataFrame([row.__dict__ for row in summaries])
    if not summary_df.empty:
        summary_df.to_csv(ART_DIR / "summary.csv", index=False)
    report_html = render_html(symbol_frames, summaries)
    (SITE_DIR / "report.html").write_text(report_html, encoding="utf-8")
    meta = {
        "generated_at_utc": pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "symbols": TARGET_SYMBOLS,
        "sources": list(SOURCE_FILES.keys()),
        "summary_rows": len(summaries),
        "out": str(SITE_DIR / "report.html"),
    }
    (ART_DIR / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
