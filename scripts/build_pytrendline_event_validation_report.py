#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "outputs" / "research" / "pytrendline_event_sample.csv"
CANDLES = ROOT / "reports" / "artifacts" / "pytrendline_research" / "candles_window.csv"
OUT_ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation"
OUT_SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_validation"
HORIZONS = [1, 3, 6, 12]
ANCHOR_H = 6


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = pd.read_csv(SAMPLE, parse_dates=["event_timestamp", "starts_at_date", "ends_at_date", "breakout_date"])
    candles = pd.read_csv(CANDLES, parse_dates=["Date"])
    sample["event_timestamp"] = pd.to_datetime(sample["event_timestamp"], utc=True, errors="coerce")
    candles["Date"] = pd.to_datetime(candles["Date"], utc=True, errors="coerce")
    sample = sample.sort_values("event_timestamp").reset_index(drop=True)
    candles = candles.sort_values("Date").reset_index(drop=True)
    return sample, candles


def attach_forward_returns(sample: pd.DataFrame, candles: pd.DataFrame) -> pd.DataFrame:
    out = sample.copy()
    idx_map = {ts: i for i, ts in enumerate(candles["Date"])}
    close = candles["Close"].astype(float).tolist()
    out["event_bar_index"] = out["event_timestamp"].map(idx_map)
    matched = out["event_bar_index"].notna().sum()
    for h in HORIZONS:
        vals = []
        ups = []
        for _, row in out.iterrows():
            idx = row["event_bar_index"]
            if pd.isna(idx):
                vals.append(float("nan"))
                ups.append(float("nan"))
                continue
            i = int(idx)
            j = i + h
            if j >= len(close):
                vals.append(float("nan"))
                ups.append(float("nan"))
                continue
            ret = close[j] / close[i] - 1.0
            vals.append(ret)
            ups.append(1.0 if ret > 0 else 0.0)
        out[f"fwd_ret_{h}"] = vals
        out[f"up_{h}"] = ups
    out.attrs["matched_events"] = int(matched)
    out.attrs["total_events"] = int(len(out))
    return out


def summarize(df: pd.DataFrame, group_cols: list[str], horizon: int) -> pd.DataFrame:
    col = f"fwd_ret_{horizon}"
    tmp = df[group_cols + [col]].copy()
    tmp = tmp.dropna(subset=[col])
    if tmp.empty:
        return pd.DataFrame(columns=group_cols + ["sample_count", "up_ratio", "mean_forward_return", "median_forward_return", "iqr_forward_return"])
    rows = []
    for keys, sub in tmp.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        vals = sub[col].astype(float)
        q1 = float(vals.quantile(0.25)) if len(vals) else float("nan")
        q3 = float(vals.quantile(0.75)) if len(vals) else float("nan")
        row = {k: v for k, v in zip(group_cols, keys)}
        row.update({
            "sample_count": int(len(vals)),
            "up_ratio": float((vals > 0).mean()) if len(vals) else float("nan"),
            "mean_forward_return": float(vals.mean()) if len(vals) else float("nan"),
            "median_forward_return": float(vals.median()) if len(vals) else float("nan"),
            "iqr_forward_return": float(q3 - q1) if len(vals) else float("nan"),
        })
        rows.append(row)
    return pd.DataFrame(rows)


def fmt_pct(x: float) -> str:
    if pd.isna(x):
        return "—"
    return f"{x * 100:.2f}%"


def render_table(df: pd.DataFrame, limit: int = 20, pct_cols: set[str] | None = None) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    shown = df.head(limit).copy()
    pct_cols = pct_cols or set()
    for col in shown.columns:
        if col in pct_cols:
            shown[col] = shown[col].apply(fmt_pct)
        elif pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d %H:%M")
    return shown.to_html(index=False, classes="tbl", border=0)


def main() -> int:
    ensure_dir(OUT_ART)
    ensure_dir(OUT_SITE)
    sample, candles = load_inputs()
    events = attach_forward_returns(sample, candles)

    overall_rows = []
    for h in HORIZONS:
        s = summarize(events, ["event_family"], h)
        s.insert(1, "horizon_bars", h)
        overall_rows.append(s)
    overall = pd.concat(overall_rows, ignore_index=True)

    side_anchor = summarize(events, ["event_family", "line_side"], ANCHOR_H).sort_values(["event_family", "sample_count"], ascending=[True, False])
    slope_anchor = summarize(events, ["event_family", "slope_bucket"], ANCHOR_H).sort_values(["event_family", "sample_count"], ascending=[True, False])
    quality_anchor = summarize(events, ["event_family", "line_quality_bucket"], ANCHOR_H).sort_values(["event_family", "sample_count"], ascending=[True, False])

    detail_cols = ["event_timestamp", "event_family", "line_side", "engine_line_id", "line_quality_bucket", "slope_bucket"] + [f"fwd_ret_{h}" for h in HORIZONS]
    detail = events[detail_cols].sort_values(["event_timestamp"]).reset_index(drop=True)

    overall.to_csv(OUT_ART / "overall_by_family_horizon.csv", index=False)
    side_anchor.to_csv(OUT_ART / f"side_summary_h{ANCHOR_H}.csv", index=False)
    slope_anchor.to_csv(OUT_ART / f"slope_summary_h{ANCHOR_H}.csv", index=False)
    quality_anchor.to_csv(OUT_ART / f"quality_summary_h{ANCHOR_H}.csv", index=False)
    detail.to_csv(OUT_ART / "event_forward_detail.csv", index=False)

    meta = {
        "symbol": str(events["symbol"].iloc[0]) if len(events) else None,
        "timeframe": str(events["timeframe"].iloc[0]) if len(events) else None,
        "sample_key": str(events["sample_key"].iloc[0]) if len(events) else None,
        "total_events": int(events.attrs.get("total_events", len(events))),
        "matched_events": int(events.attrs.get("matched_events", 0)),
        "anchor_horizon_bars": ANCHOR_H,
        "horizons": HORIZONS,
        "breakout_events": int((events["event_family"] == "breakout").sum()),
        "touch_events": int((events["event_family"] == "touch").sum()),
    }
    (OUT_ART / "summary.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    breakout_anchor = side_anchor[side_anchor["event_family"] == "breakout"].copy()
    touch_anchor = side_anchor[side_anchor["event_family"] == "touch"].copy()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>PyTrendline Event Validation v1</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
    .wrap {{ max-width: 1120px; margin: 0 auto; padding: 28px 18px 48px; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px 22px; margin-bottom: 18px; }}
    .muted {{ color: #64748b; }}
    .pill {{ display: inline-block; margin-right: 8px; margin-top: 8px; padding: 5px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    .tbl th, .tbl td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; vertical-align: top; }}
    .tbl th {{ background: #f8fafc; }}
    ul {{ line-height: 1.7; }}
    code {{ background: #f1f5f9; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p><a href=\"../../index.html\">← 返回站点首页</a></p>
    <div class=\"card\">
      <h1>PyTrendline Event Validation v1</h1>
      <p class=\"muted\">直接基于现有 <code>pytrendline_event_sample.csv</code> 与同窗口 <code>candles_window.csv</code>，按默认模板 <code>+1 / +3 / +6 / +12 bars</code> 做第一轮 event-level observation。</p>
      <div>
        <span class=\"pill\">Generated: {escape(generated_at)}</span>
        <span class=\"pill\">symbol: {escape(str(meta['symbol']))}</span>
        <span class=\"pill\">timeframe: {escape(str(meta['timeframe']))}</span>
        <span class=\"pill\">matched events: {meta['matched_events']}/{meta['total_events']}</span>
      </div>
    </div>

    <div class=\"card\">
      <h2>这页解决什么问题？</h2>
      <ul>
        <li>把 `PyTrendline` 从“有 event sample”推进到“能直接看 event 之后价格怎么走”。</li>
        <li>先不做完整策略，只看 event 后固定 horizon 的方向与收益分布。</li>
        <li>当前 bridge v1 的 coverage 仍主要是 `breakout` 与少量 `touch candidate`，因此这页也应按这个边界理解。</li>
      </ul>
      <p><strong>核心结论：</strong>这版 `PyTrendline` 验证已经真正进入 observation 层：现在可以直接回答“这些事件发生后，后面 `+1 / +3 / +6 / +12` bars 是偏涨还是偏跌”。</p>
      <p><strong>证据：</strong>本次没有重跑任何外部数据，只复用现有 `pytrendline_event_sample.csv` 与 `candles_window.csv`，已成功为 {meta['matched_events']} 条事件对齐 forward returns，并生成按 family / side / slope / quality 分层的汇总表。</p>
    </div>

    <div class=\"card\">
      <h2>样本边界</h2>
      <ul>
        <li>sample key: <code>{escape(str(meta['sample_key']))}</code></li>
        <li>total events: <strong>{meta['total_events']}</strong></li>
        <li>breakout events: <strong>{meta['breakout_events']}</strong></li>
        <li>touch events: <strong>{meta['touch_events']}</strong></li>
        <li>默认 horizon: <code>+1 / +3 / +6 / +12 bars</code></li>
        <li>当前 anchor 观察表：<code>+{ANCHOR_H} bars</code></li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>overall by family × horizon</h2>
      {render_table(overall, limit=40, pct_cols={'up_ratio', 'mean_forward_return', 'median_forward_return', 'iqr_forward_return'})}
    </div>

    <div class=\"card\">
      <h2>anchor view: event_family × line_side（+{ANCHOR_H} bars）</h2>
      {render_table(side_anchor, limit=20, pct_cols={'up_ratio', 'mean_forward_return', 'median_forward_return', 'iqr_forward_return'})}
    </div>

    <div class=\"card\">
      <h2>anchor view: slope buckets（+{ANCHOR_H} bars）</h2>
      {render_table(slope_anchor, limit=30, pct_cols={'up_ratio', 'mean_forward_return', 'median_forward_return', 'iqr_forward_return'})}
    </div>

    <div class=\"card\">
      <h2>anchor view: quality buckets（+{ANCHOR_H} bars）</h2>
      {render_table(quality_anchor, limit=30, pct_cols={'up_ratio', 'mean_forward_return', 'median_forward_return', 'iqr_forward_return'})}
    </div>

    <div class=\"card\">
      <h2>当前怎么读这页？</h2>
      <ul>
        <li>先看 `overall by family × horizon`：确认 breakout / touch 在不同 horizon 是否方向一致。</li>
        <li>再看 `line_side` / `slope_bucket` / `line_quality_bucket`：确认是否存在明显更像样的局部子集。</li>
        <li>如果局部子集明显更好，下一步再考虑进入 cross-engine comparison 或更完整的 event validation。</li>
      </ul>
      <p class=\"muted\">提醒：当前这仍是单一 BTC-USD / 10d / 5m 窗口上的 v1 观察页，不应直接当成终局结论。</p>
    </div>
  </div>
</body>
</html>
"""
    (OUT_SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"[ok] event validation site -> {OUT_SITE / 'report.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
