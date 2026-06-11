#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.factors.confirmed_extrema import ConfirmedExtremaConfig, compute_confirmed_extrema  # noqa: E402
from momentum.factors.endpoint_nadaraya_watson import (  # noqa: E402
    EndpointNadarayaWatsonConfig,
    compute_endpoint_nadaraya_watson,
)

DEFAULT_TICKER = "BTC-USD"
DEFAULT_PERIOD = "60d"
DEFAULT_INTERVAL = "5m"
ARTIFACTS_NAME = "kernel_extrema_foundation"

TIMEFRAME_SPECS = [
    {"label": "5m", "rule": "5min", "bandwidth": 6.0, "lookback": 160, "neighbor_bars": 3, "display_bars": 288},
    {"label": "15m", "rule": "15min", "bandwidth": 6.0, "lookback": 140, "neighbor_bars": 3, "display_bars": 288},
    {"label": "30m", "rule": "30min", "bandwidth": 6.0, "lookback": 120, "neighbor_bars": 3, "display_bars": 240},
    {"label": "1h", "rule": "1h", "bandwidth": 6.0, "lookback": 100, "neighbor_bars": 3, "display_bars": 240},
    {"label": "4h", "rule": "4h", "bandwidth": 5.0, "lookback": 90, "neighbor_bars": 2, "display_bars": 180},
    {"label": "12h", "rule": "12h", "bandwidth": 5.0, "lookback": 70, "neighbor_bars": 2, "display_bars": 120},
    {"label": "24h", "rule": "24h", "bandwidth": 5.0, "lookback": 60, "neighbor_bars": 2, "display_bars": 90},
]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def flatten_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df


def download_bars(ticker: str, period: str, interval: str) -> pd.DataFrame:
    raw = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise ValueError(f"No data for {ticker}")
    raw = flatten_yf_columns(raw)
    bars = raw.reset_index().rename(
        columns={
            "Datetime": "timestamp",
            "Date": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    keep = [c for c in ["timestamp", "open", "high", "low", "close", "volume"] if c in bars.columns]
    return bars[keep].dropna().sort_values("timestamp").reset_index(drop=True)


def load_input_data(input_path: str | None, ticker: str, period: str, interval: str) -> pd.DataFrame:
    if input_path:
        path = Path(input_path)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise ValueError(f"Input not found: {path}")
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df
    return download_bars(ticker=ticker, period=period, interval=interval)


def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    return (
        df.set_index("timestamp")
        .resample(rule, label="right", closed="right")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna(subset=["open", "high", "low", "close"])
        .reset_index()
    )


def build_foundation_features(
    frame: pd.DataFrame,
    *,
    prefix: str,
    bandwidth: float,
    lookback: int,
    neighbor_bars: int,
) -> pd.DataFrame:
    out = compute_endpoint_nadaraya_watson(
        frame,
        config=EndpointNadarayaWatsonConfig(
            source_column="close",
            bandwidth=bandwidth,
            lookback=lookback,
            result_column=f"{prefix}_nwe_middle",
        ),
    )
    out = compute_confirmed_extrema(
        out,
        config=ConfirmedExtremaConfig(
            value_column=f"{prefix}_nwe_middle",
            neighbor_bars=neighbor_bars,
            anchor_high_column="high",
            anchor_low_column="low",
            anchor_window_bars=neighbor_bars,
            bar_index_column=f"{prefix}_bar_index",
            high_flag_column=f"{prefix}_confirmed_high",
            low_flag_column=f"{prefix}_confirmed_low",
            high_value_column=f"{prefix}_confirmed_high_value",
            low_value_column=f"{prefix}_confirmed_low_value",
            high_origin_index_column=f"{prefix}_confirmed_high_origin_index",
            low_origin_index_column=f"{prefix}_confirmed_low_origin_index",
            high_structure_column=f"{prefix}_confirmed_high_structure",
            low_structure_column=f"{prefix}_confirmed_low_structure",
        ),
    )
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    return out


def int_str(v: float) -> str:
    return str(int(v)) if pd.notna(v) else "nan"


def pct(v: float) -> str:
    return "nan" if pd.isna(v) else f"{100.0 * v:.2f}%"


def render_table(df: pd.DataFrame, *, index: bool = False) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    return df.to_html(index=index, classes="tbl", border=0, justify="left", escape=False)


def recent_extrema_table(features: pd.DataFrame, *, prefix: str) -> pd.DataFrame:
    rows: list[dict] = []
    for _, row in features.iterrows():
        if int(row[f"{prefix}_confirmed_high"]) == 1:
            origin_idx = int(row[f"{prefix}_confirmed_high_origin_index"])
            rows.append(
                {
                    "confirm_timestamp": row["timestamp"],
                    "origin_timestamp": features.iloc[origin_idx]["timestamp"],
                    "type": "high",
                    "anchored_price": row[f"{prefix}_confirmed_high_value"],
                    "structure": row[f"{prefix}_confirmed_high_structure"],
                }
            )
        if int(row[f"{prefix}_confirmed_low"]) == 1:
            origin_idx = int(row[f"{prefix}_confirmed_low_origin_index"])
            rows.append(
                {
                    "confirm_timestamp": row["timestamp"],
                    "origin_timestamp": features.iloc[origin_idx]["timestamp"],
                    "type": "low",
                    "anchored_price": row[f"{prefix}_confirmed_low_value"],
                    "structure": row[f"{prefix}_confirmed_low_structure"],
                }
            )
    if not rows:
        return pd.DataFrame(columns=["confirm_timestamp", "origin_timestamp", "type", "anchored_price", "structure"])
    return pd.DataFrame(rows).tail(20)


def plot_foundation(frame: pd.DataFrame, out_path: Path, *, prefix: str, label: str, title: str, display_bars: int) -> None:
    view = frame.tail(display_bars).copy() if len(frame) > display_bars else frame.copy()
    start_idx = int(view.index.min())
    end_idx = int(view.index.max())

    fig, ax = plt.subplots(figsize=(14, 5.8))
    ts = pd.to_datetime(view["timestamp"], utc=True)
    ax.plot(ts, view["close"], label=f"{label} close", color="#9ca3af", linewidth=0.9)
    ax.plot(ts, view[f"{prefix}_nwe_middle"], label=f"{label} NWE middle", color="#111827", linewidth=1.4)

    high_rows = frame[frame[f"{prefix}_confirmed_high"] == 1].copy()
    low_rows = frame[frame[f"{prefix}_confirmed_low"] == 1].copy()

    if not high_rows.empty:
        high_rows = high_rows[high_rows[f"{prefix}_confirmed_high_origin_index"].between(start_idx, end_idx)]
        high_x = [frame.iloc[int(i)]["timestamp"] for i in high_rows[f"{prefix}_confirmed_high_origin_index"]]
        high_y = high_rows[f"{prefix}_confirmed_high_value"].to_numpy()
        if len(high_x):
            ax.scatter(pd.to_datetime(high_x, utc=True), high_y, marker="^", color="#f59e0b", s=36, label="confirmed high (raw high anchor)")

    if not low_rows.empty:
        low_rows = low_rows[low_rows[f"{prefix}_confirmed_low_origin_index"].between(start_idx, end_idx)]
        low_x = [frame.iloc[int(i)]["timestamp"] for i in low_rows[f"{prefix}_confirmed_low_origin_index"]]
        low_y = low_rows[f"{prefix}_confirmed_low_value"].to_numpy()
        if len(low_x):
            ax.scatter(pd.to_datetime(low_x, utc=True), low_y, marker="v", color="#14b8a6", s=36, label="confirmed low (raw low anchor)")

    ax.set_title(title)
    ax.legend(loc="upper left")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def build_gallery(ticker: str, base_5m: pd.DataFrame, artifacts_dir: Path) -> tuple[list[dict], pd.DataFrame, pd.DataFrame]:
    gallery: list[dict] = []
    rows: list[dict] = []
    focus_table = pd.DataFrame()

    for i, spec in enumerate(TIMEFRAME_SPECS):
        label = spec["label"]
        rule = spec["rule"]
        prefix = f"tf_{label}"
        frame = resample_ohlcv(base_5m[["timestamp", "open", "high", "low", "close", "volume"]].copy(), rule)
        features = build_foundation_features(
            frame,
            prefix=prefix,
            bandwidth=spec["bandwidth"],
            lookback=spec["lookback"],
            neighbor_bars=spec["neighbor_bars"],
        )

        csv_name = f"timeframe_{label}.csv"
        png_name = f"timeframe_{label}.png"
        features.to_csv(artifacts_dir / csv_name, index=False)
        plot_foundation(
            features,
            artifacts_dir / png_name,
            prefix=prefix,
            label=label,
            title=f"{ticker} | {label} NWE + confirmed extrema",
            display_bars=spec["display_bars"],
        )

        highs = int(features[f"{prefix}_confirmed_high"].fillna(0).sum())
        lows = int(features[f"{prefix}_confirmed_low"].fillna(0).sum())
        hh = int((features[f"{prefix}_confirmed_high_structure"] == "HH").sum())
        lh = int((features[f"{prefix}_confirmed_high_structure"] == "LH").sum())
        hl = int((features[f"{prefix}_confirmed_low_structure"] == "HL").sum())
        ll = int((features[f"{prefix}_confirmed_low_structure"] == "LL").sum())

        rows.append(
            {
                "timeframe": label,
                "bars": int(len(features)),
                "confirmed_highs": highs,
                "confirmed_lows": lows,
                "HH": hh,
                "LH": lh,
                "HL": hl,
                "LL": ll,
            }
        )
        gallery.append({"label": label, "image": png_name, "csv": csv_name})

        if i == 0:
            focus_table = recent_extrema_table(features, prefix=prefix)
            focus_table.to_csv(artifacts_dir / "recent_extrema_5m.csv", index=False)

    return gallery, pd.DataFrame(rows), focus_table


def build_report_html(*, ticker: str, period: str, interval: str, generated_at: str, summary: pd.DataFrame, focus_table: pd.DataFrame, artifacts_rel: str, gallery: list[dict]) -> str:
    source_audit = pd.DataFrame(
        [
            ["endpoint_nadaraya_watson.py", "本仓库轻量实现", "对齐 PyIndicators/nadaraya_watson_envelope 的 endpoint middle line", "保留；成熟可复用"],
            ["confirmed_extrema.py", "本仓库轻量实现", "对齐 PyIndicators/swing_structure 与 pivot confirmation 思路", "保留；成熟可复用"],
            ["channel_lines.py", "我们自己写的业务层", "无直接成熟实现对齐", "已删除 / 暂缓"],
            ["kernel_channel_breakout.py", "我们自己写的业务层", "依赖 channel heuristic", "已删除 / 暂缓"],
            ["Lo, Mamaysky, Wang (2000)", "文献参考", "提供平滑 + 极值 + 形态识别的大方向", "概念参考，不是本仓库 1:1 复刻对象"],
        ],
        columns=["component", "status", "source_or_reference", "decision"],
    )

    gallery_html = "".join(
        f'''<div class="card"><h3>{html.escape(item["label"])} 周期</h3><p class="muted"><a href="{artifacts_rel}/{item["csv"]}">CSV</a></p><img src="{artifacts_rel}/{item["image"]}" alt="{html.escape(item["label"])} extrema chart" /></div>'''
        for item in gallery
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kernel Extrema Foundation Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 1080px; margin: 40px auto; padding: 0 18px; line-height: 1.65; color: #111; }}
    h1, h2, h3 {{ line-height: 1.25; }}
    .muted {{ color: #666; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; margin: 16px 0; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    .tbl th, .tbl td {{ border-bottom: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; vertical-align: top; }}
    img {{ max-width: 100%; border: 1px solid #e5e7eb; border-radius: 10px; }}
    code {{ background: #f3f4f6; padding: 1px 5px; border-radius: 6px; }}
    a {{ color: #2563eb; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Kernel Extrema Foundation Report</h1>
  <p class="muted">样本：{html.escape(ticker)} | {html.escape(period)} / {html.escape(interval)} | 生成时间：{html.escape(generated_at)}</p>

  <div class="card">
    <h2>这份报告现在只展示什么</h2>
    <ul>
      <li><b>endpoint / non-repainting NWE middle line</b></li>
      <li><b>confirmed highs / confirmed lows</b></li>
      <li>confirmed extrema 的锚点值使用原始 <code>high / low</code>，不是平滑线上的值</li>
      <li>暂时不展示 channel / breakout / pattern 业务层</li>
    </ul>
  </div>

  <div class="card">
    <h2>来源审计：哪些是直接对齐成熟逻辑，哪些不是</h2>
    {render_table(source_audit)}
  </div>

  <div class="card">
    <h2>多周期摘要</h2>
    <p class="muted">每张图默认只展示适合人眼阅读的最近窗口，而不是把全样本 bar 全塞进一张图。</p>
    {render_table(summary)}
  </div>

  {gallery_html}

  <div class="card">
    <h2>最近的 5m confirmed extrema</h2>
    <p class="muted">这里会同时展示：origin timestamp（结构点真正所在位置）与 confirm timestamp（这个点何时才可用）。</p>
    {render_table(focus_table)}
  </div>

  <div class="card">
    <h2>当前结论</h2>
    <ul>
      <li>成熟可复用层：<code>endpoint_nadaraya_watson.py</code> + <code>confirmed_extrema.py</code></li>
      <li>当前报告重点：把“平滑线”和“真实 high/low 锚点 extrema”讲清楚</li>
      <li>通道 / breakout / pattern 先不作为正式成果</li>
    </ul>
  </div>

  <div class="card">
    <h2>Artifacts</h2>
    <ul>
      <li><a href="{artifacts_rel}/timeframe_summary.csv">timeframe_summary.csv</a></li>
      <li><a href="{artifacts_rel}/recent_extrema_5m.csv">recent_extrema_5m.csv</a></li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build kernel extrema foundation report")
    parser.add_argument("--ticker", default=DEFAULT_TICKER)
    parser.add_argument("--period", default=DEFAULT_PERIOD)
    parser.add_argument("--interval", default=DEFAULT_INTERVAL)
    parser.add_argument("--input", default="")
    args = parser.parse_args()

    bars = load_input_data(args.input or None, args.ticker, args.period, args.interval)
    artifacts_dir = ensure_dir(ROOT / "reports" / "artifacts" / ARTIFACTS_NAME)
    site_dir = ensure_dir(ROOT / "reports" / "site" / "factors" / ARTIFACTS_NAME)

    gallery, summary, focus_table = build_gallery(args.ticker, bars, artifacts_dir)
    summary.to_csv(artifacts_dir / "timeframe_summary.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report_html = build_report_html(
        ticker=args.ticker,
        period=args.period,
        interval=args.interval,
        generated_at=generated_at,
        summary=summary,
        focus_table=focus_table,
        artifacts_rel=f"../../artifacts/{ARTIFACTS_NAME}",
        gallery=gallery,
    )
    (site_dir / "report.html").write_text(report_html, encoding="utf-8")
    (artifacts_dir / "summary.json").write_text(
        json.dumps(
            {
                "ticker": args.ticker,
                "period": args.period,
                "interval": args.interval,
                "generated_at": generated_at,
                "timeframes": summary.to_dict(orient="records"),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote report to {site_dir / 'report.html'}")


if __name__ == "__main__":
    main()
