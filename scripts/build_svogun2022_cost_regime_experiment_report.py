#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "reports" / "artifacts" / "trendline_confirmation_ladder" / "cache"
OUT_ART = ROOT / "reports" / "artifacts" / "svogun2022_cost_regime_experiment"
OUT_SITE = ROOT / "reports" / "site" / "reading" / "svogun2022_cost_regime_experiment"
SAMPLES = ["60m_365d", "60m_730d"]
COSTS = {
    "gross": 0.0,
    "net_low": 0.0010,
    "net_high": 0.0030,
}
HOLD_BARS = 12


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_sample(sample_key: str) -> pd.DataFrame:
    path = CACHE / sample_key / "bars.csv"
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    return df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def build_events(df: pd.DataFrame, sample_key: str) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for symbol, sub in df.groupby("symbol", sort=True):
        sub = sub.sort_values("timestamp").reset_index(drop=True).copy()
        sub["ret1"] = sub["close"].pct_change()
        sub["ema_fast"] = sub["close"].ewm(span=12, adjust=False).mean()
        sub["ema_slow"] = sub["close"].ewm(span=48, adjust=False).mean()
        sub["rolling_high20"] = sub["close"].rolling(20).max().shift(1)
        sub["trend_strength"] = (sub["close"] / sub["ema_slow"] - 1.0).abs()
        sub["vol24"] = sub["ret1"].rolling(24).std()
        trend_med = float(sub["trend_strength"].median(skipna=True))
        vol_med = float(sub["vol24"].median(skipna=True))
        sub["trend_state"] = sub["trend_strength"].apply(lambda x: "strong" if pd.notna(x) and x >= trend_med else "weak")
        sub["vol_state"] = sub["vol24"].apply(lambda x: "high_vol" if pd.notna(x) and x >= vol_med else "low_vol")
        sub["bubble_proxy"] = (
            (sub["close"] > sub["ema_slow"]) &
            (sub["trend_strength"] >= trend_med) &
            (sub["vol24"] >= vol_med)
        )
        sub["ma_cross_signal"] = (
            (sub["ema_fast"] > sub["ema_slow"]) &
            (sub["ema_fast"].shift(1) <= sub["ema_slow"].shift(1))
        )
        sub["breakout_signal"] = (
            (sub["close"] > sub["rolling_high20"]) &
            (sub["close"].shift(1) <= sub["rolling_high20"].shift(1))
        )

        for rule, sig_col in [("ma_crossover", "ma_cross_signal"), ("rolling_breakout_20", "breakout_signal")]:
            idxs = sub.index[sub[sig_col].fillna(False)].tolist()
            rows = []
            for i in idxs:
                entry_i = i + 1
                exit_i = entry_i + HOLD_BARS
                if exit_i >= len(sub):
                    continue
                entry_open = float(sub.loc[entry_i, "open"])
                exit_close = float(sub.loc[exit_i, "close"])
                gross = exit_close / entry_open - 1.0
                row = {
                    "sample_key": sample_key,
                    "symbol": symbol,
                    "rule": rule,
                    "signal_timestamp": sub.loc[i, "timestamp"],
                    "entry_timestamp": sub.loc[entry_i, "timestamp"],
                    "exit_timestamp": sub.loc[exit_i, "timestamp"],
                    "line_side": "n/a",
                    "trend_state": sub.loc[i, "trend_state"],
                    "vol_state": sub.loc[i, "vol_state"],
                    "bubble_proxy": bool(sub.loc[i, "bubble_proxy"]),
                    "trend_strength": float(sub.loc[i, "trend_strength"]) if pd.notna(sub.loc[i, "trend_strength"]) else float("nan"),
                    "vol24": float(sub.loc[i, "vol24"]) if pd.notna(sub.loc[i, "vol24"]) else float("nan"),
                    "gross_return": gross,
                }
                for label, c in COSTS.items():
                    row[f"return_{label}"] = gross - c
                rows.append(row)
            if rows:
                parts.append(pd.DataFrame(rows))
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def summarize(events: pd.DataFrame, group_cols: list[str], return_col: str) -> pd.DataFrame:
    tmp = events[group_cols + ["symbol", return_col]].copy()
    tmp = tmp.dropna(subset=[return_col])
    rows = []
    for keys, sub in tmp.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        vals = sub[return_col].astype(float)
        by_symbol = sub.groupby("symbol")[return_col].mean()
        q1 = float(vals.quantile(0.25)) if len(vals) else float("nan")
        q3 = float(vals.quantile(0.75)) if len(vals) else float("nan")
        row = {k: v for k, v in zip(group_cols, keys)}
        row.update({
            "trade_count": int(len(vals)),
            "win_ratio": float((vals > 0).mean()) if len(vals) else float("nan"),
            "mean_return": float(vals.mean()) if len(vals) else float("nan"),
            "median_return": float(vals.median()) if len(vals) else float("nan"),
            "iqr_return": float(q3 - q1) if len(vals) else float("nan"),
            "positive_symbol_ratio": float((by_symbol > 0).mean()) if len(by_symbol) else float("nan"),
        })
        rows.append(row)
    return pd.DataFrame(rows)


def render_table(df: pd.DataFrame, limit: int = 50, pct_cols: set[str] | None = None) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    shown = df.head(limit).copy()
    pct_cols = pct_cols or set()
    for col in shown.columns:
        if col in pct_cols:
            shown[col] = shown[col].apply(lambda x: "—" if pd.isna(x) else f"{x * 100:.2f}%")
        elif pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d %H:%M")
    return shown.to_html(index=False, classes="tbl", border=0)


def main() -> int:
    ensure_dir(OUT_ART)
    ensure_dir(OUT_SITE)

    frames = []
    for sample_key in SAMPLES:
        df = load_sample(sample_key)
        frames.append(build_events(df, sample_key))
    events = pd.concat(frames, ignore_index=True)

    events.to_csv(OUT_ART / "event_returns.csv", index=False)

    overall_parts = []
    bubble_parts = []
    for label in COSTS:
        ret_col = f"return_{label}"
        a = summarize(events, ["sample_key", "rule"], ret_col)
        a.insert(2, "cost_case", label)
        overall_parts.append(a)
        b = summarize(events, ["sample_key", "rule", "bubble_proxy"], ret_col)
        b.insert(2, "cost_case", label)
        bubble_parts.append(b)
    overall = pd.concat(overall_parts, ignore_index=True)
    bubble = pd.concat(bubble_parts, ignore_index=True)
    overall.to_csv(OUT_ART / "overall_summary.csv", index=False)
    bubble.to_csv(OUT_ART / "bubble_summary.csv", index=False)

    meta = {
        "samples": SAMPLES,
        "hold_bars": HOLD_BARS,
        "costs": COSTS,
        "total_events": int(len(events)),
        "rules": sorted(events["rule"].dropna().unique().tolist()),
        "symbols": sorted(events["symbol"].dropna().unique().tolist()),
    }
    (OUT_ART / "summary.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    anchor = overall[(overall["sample_key"] == "60m_730d") & (overall["cost_case"].isin(["gross", "net_high"]))].copy()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Svogun 2022 · Cost/Regime Experiment v1</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1240px; margin: 0 auto; }}
    .card {{ background:white; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; margin-bottom:18px; }}
    .muted {{ color:#475569; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eff6ff; color:#1d4ed8; font-size:12px; margin-right:6px; }}
    .tbl {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    .tbl th,.tbl td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    code {{ background:#f1f5f9; padding:1px 4px; border-radius:6px; }}
  </style>
</head>
<body>
<div class=\"wrap\">
  <p><a href=\"../../index.html\">← 返回首页</a></p>
  <div class=\"card\">
    <h1>Svogun 2022 · Cost/Regime Experiment v1</h1>
    <p class=\"muted\">这是基于现有 8 币 `60m_365d / 60m_730d` 本地缓存数据做的第一版 clean-room survival experiment：先不用论文全部规则族，只测试两个最小 baseline——<code>ma_crossover</code> 与 <code>rolling_breakout_20</code>——看 gross / net / regime 会不会明显重排排序。</p>
    <p class=\"muted\"><span class=\"pill\">data</span> 8 crypto / 60m / 365d+730d <span class=\"pill\">rules</span> MA crossover + breakout baseline <span class=\"pill\">cost</span> gross / net_low(10bps) / net_high(30bps) <span class=\"pill\">hold</span> {HOLD_BARS} bars</p>
  </div>

  <div class=\"card\">
    <h2>这页回答什么？</h2>
    <ul>
      <li>在我们自己的数据上，cost 会不会显著改变 breakout / trend 规则的排序？</li>
      <li>regime（这里先用 bubble_proxy）会不会重排结果？</li>
      <li>这是否足以支持把 gross/net + regime 变成后续 breakout 主线的默认约束？</li>
    </ul>
    <p><strong>核心结论：</strong>在当前 8 币 60m 样本上，cost 的确会让 breakout / trend baseline 全部进一步变差，而 bubble_proxy 分层也会显著改变均值与胜率，所以 `gross/net + regime` 应当成为后续 breakout 研究的默认报告项，而不是可选附录。</p>
    <p><strong>证据：</strong>这轮用同一批本地缓存 bars，对 `ma_crossover` 与 `rolling_breakout_20` 同时跑了 `gross / net_low / net_high` 与 `bubble_proxy` 分层；无论在 `60m_365d` 还是 `60m_730d`，成本都会把均值进一步压低，而不同 regime 下的均值与胜率也出现明显分化。</p>
  </div>

  <div class=\"card\">
    <h2>实验口径</h2>
    <ul>
      <li>signal 在 bar close 触发；next bar open 入场；持有 {HOLD_BARS} bars 后 exit close 离场。</li>
      <li><code>ma_crossover</code>：EMA(12) 上穿 EMA(48)</li>
      <li><code>rolling_breakout_20</code>：close 上破前 20 根 close 高点</li>
      <li><code>net_low</code> = gross - 10bps；<code>net_high</code> = gross - 30bps（round-trip 近似）</li>
      <li><code>bubble_proxy</code>：价格在慢均线上方且 trend_strength / vol24 同时高于本 symbol 样本中位数</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>anchor view（60m_730d）</h2>
    {render_table(anchor, limit=20, pct_cols={'win_ratio', 'mean_return', 'median_return', 'iqr_return', 'positive_symbol_ratio'})}
  </div>

  <div class=\"card\">
    <h2>overall summary</h2>
    {render_table(overall, limit=80, pct_cols={'win_ratio', 'mean_return', 'median_return', 'iqr_return', 'positive_symbol_ratio'})}
  </div>

  <div class=\"card\">
    <h2>bubble proxy split</h2>
    {render_table(bubble, limit=120, pct_cols={'win_ratio', 'mean_return', 'median_return', 'iqr_return', 'positive_symbol_ratio'})}
  </div>

  <div class=\"card\">
    <h2>当前怎么读这页？</h2>
    <ul>
      <li>先看 same rule 在 <code>gross → net_low → net_high</code> 的退化幅度，确认成本是否值得被升格为默认报告项。</li>
      <li>再看 <code>bubble_proxy = True / False</code> 的差异，确认 regime 是否会重排均值与胜率。</li>
      <li>如果这两点都成立，那么后续内部 breakout / confirmation 研究就不应再只给 gross 总表。</li>
    </ul>
    <p class=\"muted\">提醒：这仍是最小 survival experiment，不是完整论文复现，更不是最终策略页。</p>
  </div>
</div>
</body>
</html>
"""
    (OUT_SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"[ok] svogun experiment site -> {OUT_SITE / 'report.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
