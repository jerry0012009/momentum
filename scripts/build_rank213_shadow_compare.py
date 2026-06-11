#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_shadow_compare.html"

CURRENT_SIGNAL_PATH = ART_DIR / "rank213_current_signal_frame.csv"
STATUS_PATH = ART_DIR / "rank213_status.csv"
FORMAL_THREEWAY_DETAIL_PATH = ART_DIR / "rank213_formal_threeway_backtest_detail.csv"
ASOF_DETAIL_PATH = ART_DIR / "rank213_asof_universe_long_history_detail.csv"
READINESS_PATH = ART_DIR / "rank213_readiness_note_summary.json"

COMPARE_DETAIL_PATH = ART_DIR / "rank213_shadow_compare_detail.csv"
COMPARE_SUMMARY_PATH = ART_DIR / "rank213_shadow_compare_summary.json"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def to_iso(ts: pd.Timestamp | None) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_symbol_list(value: object) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    return [part for part in text.split(",") if part]


def format_symbol_list(values: set[str] | list[str]) -> str:
    if not values:
        return ""
    return ",".join(sorted(set(values)))


def load_runner_frame() -> pd.DataFrame:
    df = pd.read_csv(CURRENT_SIGNAL_PATH)
    df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True)
    df["exit_ts"] = pd.to_datetime(df["exit_ts"], utc=True)
    df["compare_ts"] = df["entry_ts"].dt.floor("3h")
    df["runner_longs_list"] = df["longs"].map(parse_symbol_list)
    df["runner_shorts_list"] = df["shorts"].map(parse_symbol_list)
    df["runner_longs"] = df["runner_longs_list"].map(lambda xs: ",".join(xs))
    df["runner_shorts"] = df["runner_shorts_list"].map(lambda xs: ",".join(xs))
    return df


def load_asof_detail() -> pd.DataFrame:
    df = pd.read_csv(ASOF_DETAIL_PATH)
    df["timestamp_ts"] = pd.to_datetime(df["timestamp_ts"], utc=True)
    df["compare_ts"] = df["timestamp_ts"]
    df["asof_longs_list"] = df["plain_longs"].map(parse_symbol_list)
    df["asof_shorts_list"] = df["veto_shorts"].map(parse_symbol_list)
    keep = [
        "compare_ts",
        "timestamp_ts",
        "asof_longs_list",
        "asof_shorts_list",
        "plain_longs",
        "veto_shorts",
        "veto_count",
        "veto_threshold",
        "plain_net",
        "veto_net",
        "eligible_universe_size",
    ]
    return df[keep].rename(columns={
        "plain_longs": "asof_longs",
        "veto_shorts": "asof_shorts",
        "veto_count": "asof_veto_count",
        "veto_threshold": "asof_veto_threshold",
        "veto_net": "asof_veto_net",
    })


def load_formal_gate_detail() -> pd.DataFrame:
    df = pd.read_csv(FORMAL_THREEWAY_DETAIL_PATH)
    df["timestamp_ts"] = pd.to_datetime(df["timestamp_ts"], utc=True)
    df["compare_ts"] = df["timestamp_ts"]
    return df[[
        "timestamp_ts",
        "compare_ts",
        "gate_ret",
        "gate_on",
        "gate_votes",
        "gate_valid_rules",
        "gate_needed_votes",
    ]].rename(columns={"gate_ret": "formal_gate_ret"})


def overlap_rate(a: list[str], b: list[str]) -> float:
    sa = set(a)
    sb = set(b)
    denom = max(len(sa | sb), 1)
    return len(sa & sb) / denom


def build_compare() -> tuple[pd.DataFrame, dict]:
    runner = load_runner_frame()
    asof = load_asof_detail()
    formal = load_formal_gate_detail()
    status = pd.read_csv(STATUS_PATH).iloc[0].to_dict() if STATUS_PATH.exists() else {}
    readiness = json.loads(READINESS_PATH.read_text(encoding="utf-8")) if READINESS_PATH.exists() else {}

    merged = runner.merge(
        asof,
        on="compare_ts",
        how="left",
        suffixes=("", "_asof"),
    )
    merged = merged.merge(
        formal,
        on="compare_ts",
        how="left",
        suffixes=("", "_formal"),
    )

    if merged.empty:
        raise RuntimeError("rank213 shadow compare: merged frame is empty")

    merged["long_overlap_rate"] = merged.apply(
        lambda row: overlap_rate(row["runner_longs_list"], row["asof_longs_list"] if isinstance(row["asof_longs_list"], list) else []),
        axis=1,
    )
    merged["short_overlap_rate"] = merged.apply(
        lambda row: overlap_rate(row["runner_shorts_list"], row["asof_shorts_list"] if isinstance(row["asof_shorts_list"], list) else []),
        axis=1,
    )
    merged["runner_gate_on"] = pd.to_numeric(merged["net_bps"], errors="coerce").fillna(0.0) != 0.0
    merged["basket_exact_match"] = (
        (merged["runner_longs"] == merged["asof_longs"].fillna(""))
        & (merged["runner_shorts"] == merged["asof_shorts"].fillna(""))
    )
    merged["veto_count_match"] = merged["veto_count"].fillna(-1).astype(float) == merged["asof_veto_count"].fillna(-2).astype(float)
    merged["gate_match"] = merged["runner_gate_on"].astype(bool) == merged["gate_on"].fillna(False).astype(bool)
    merged["runner_long_only"] = merged.apply(
        lambda row: format_symbol_list(set(row["runner_longs_list"]) - set(row["asof_longs_list"] if isinstance(row["asof_longs_list"], list) else [])),
        axis=1,
    )
    merged["asof_long_only"] = merged.apply(
        lambda row: format_symbol_list(set(row["asof_longs_list"] if isinstance(row["asof_longs_list"], list) else []) - set(row["runner_longs_list"])),
        axis=1,
    )
    merged["runner_short_only"] = merged.apply(
        lambda row: format_symbol_list(set(row["runner_shorts_list"]) - set(row["asof_shorts_list"] if isinstance(row["asof_shorts_list"], list) else [])),
        axis=1,
    )
    merged["asof_short_only"] = merged.apply(
        lambda row: format_symbol_list(set(row["asof_shorts_list"] if isinstance(row["asof_shorts_list"], list) else []) - set(row["runner_shorts_list"])),
        axis=1,
    )
    merged["basket_only_in_runner"] = merged.apply(
        lambda row: format_symbol_list(set(parse_symbol_list(row["runner_long_only"])) | set(parse_symbol_list(row["runner_short_only"]))),
        axis=1,
    )
    merged["basket_only_in_asof"] = merged.apply(
        lambda row: format_symbol_list(set(parse_symbol_list(row["asof_long_only"])) | set(parse_symbol_list(row["asof_short_only"]))),
        axis=1,
    )
    merged["veto_mismatch"] = ~merged["veto_count_match"]
    merged["gate_mismatch"] = ~merged["gate_match"]
    merged["runner_net_ret"] = pd.to_numeric(merged["net_bps"], errors="coerce") / 10000.0
    merged["runner_vs_asof_veto_net_diff_bps"] = (merged["runner_net_ret"] - pd.to_numeric(merged["asof_veto_net"], errors="coerce")) * 10000.0
    merged["runner_vs_formal_gate_net_diff_bps"] = (merged["runner_net_ret"] - pd.to_numeric(merged["formal_gate_ret"], errors="coerce")) * 10000.0

    detail = merged[[
        "entry_ts",
        "exit_ts",
        "compare_ts",
        "timestamp_ts",
        "runner_longs",
        "runner_shorts",
        "asof_longs",
        "asof_shorts",
        "runner_long_only",
        "asof_long_only",
        "runner_short_only",
        "asof_short_only",
        "basket_only_in_runner",
        "basket_only_in_asof",
        "veto_count",
        "asof_veto_count",
        "runner_gate_on",
        "gate_on",
        "gate_match",
        "gate_mismatch",
        "veto_mismatch",
        "gate_votes",
        "gate_valid_rules",
        "gate_needed_votes",
        "net_bps",
        "asof_veto_net",
        "formal_gate_ret",
        "long_overlap_rate",
        "short_overlap_rate",
        "basket_exact_match",
        "veto_count_match",
        "runner_vs_asof_veto_net_diff_bps",
        "runner_vs_formal_gate_net_diff_bps",
    ]].copy()
    detail["entry_ts"] = detail["entry_ts"].map(to_iso)
    detail["exit_ts"] = detail["exit_ts"].map(to_iso)
    detail["compare_ts"] = detail["compare_ts"].map(to_iso)
    detail["timestamp_ts"] = detail["timestamp_ts"].map(to_iso)
    detail.to_csv(COMPARE_DETAIL_PATH, index=False)

    matched = merged[merged["asof_longs"].notna()].copy()
    summary = {
        "scope": "compare current frozen-seed runner outputs against raw-bar as-of basket and formal frozen-gate reference",
        "sample": {
            "runner_rows": int(len(runner)),
            "matched_rows": int(len(matched)),
            "latest_entry_ts": to_iso(runner["entry_ts"].max()) if not runner.empty else None,
        },
        "status_context": {
            "runner_mode": status.get("runner_mode"),
            "variant": status.get("variant"),
            "latest_signal_ts": status.get("latest_signal_ts"),
            "latest_planned_exit_ts": status.get("latest_planned_exit_ts"),
        },
        "evidence_context": {
            "readiness_headline": readiness.get("headline"),
            "frozen_1Y": (readiness.get("window_availability") or {}).get("frozen_1Y"),
            "asof_1Y": (readiness.get("window_availability") or {}).get("asof_1Y"),
            "asof_3Y": (readiness.get("window_availability") or {}).get("asof_3Y"),
            "asof_6Y": (readiness.get("window_availability") or {}).get("asof_6Y"),
        },
        "compare_metrics": {
            "basket_exact_match_rate": float(matched["basket_exact_match"].mean()) if not matched.empty else 0.0,
            "veto_count_match_rate": float(matched["veto_count_match"].mean()) if not matched.empty else 0.0,
            "gate_match_rate": float(matched["gate_match"].mean()) if not matched.empty else 0.0,
            "gate_mismatch_rate": float(matched["gate_mismatch"].mean()) if not matched.empty else 0.0,
            "veto_mismatch_rate": float(matched["veto_mismatch"].mean()) if not matched.empty else 0.0,
            "basket_only_in_runner_rate": float((matched["basket_only_in_runner"] != "").mean()) if not matched.empty else 0.0,
            "basket_only_in_asof_rate": float((matched["basket_only_in_asof"] != "").mean()) if not matched.empty else 0.0,
            "avg_long_overlap_rate": float(matched["long_overlap_rate"].mean()) if not matched.empty else 0.0,
            "avg_short_overlap_rate": float(matched["short_overlap_rate"].mean()) if not matched.empty else 0.0,
            "mean_runner_vs_asof_veto_net_diff_bps": float(matched["runner_vs_asof_veto_net_diff_bps"].mean()) if not matched.empty else 0.0,
            "mean_runner_vs_formal_gate_net_diff_bps": float(matched["runner_vs_formal_gate_net_diff_bps"].mean()) if not matched.empty else 0.0,
        },
        "aggregate_evidence": {
            "basket_only_in_runner_symbols": sorted({sym for text in matched["basket_only_in_runner"] for sym in parse_symbol_list(text)}) if not matched.empty else [],
            "basket_only_in_asof_symbols": sorted({sym for text in matched["basket_only_in_asof"] for sym in parse_symbol_list(text)}) if not matched.empty else [],
            "gate_mismatch_rows": int(matched["gate_mismatch"].sum()) if not matched.empty else 0,
            "veto_mismatch_rows": int(matched["veto_mismatch"].sum()) if not matched.empty else 0,
            "rows_with_runner_only_basket": int((matched["basket_only_in_runner"] != "").sum()) if not matched.empty else 0,
            "rows_with_asof_only_basket": int((matched["basket_only_in_asof"] != "").sum()) if not matched.empty else 0,
        },
        "detail_csv": str(COMPARE_DETAIL_PATH.relative_to(ROOT)),
    }
    COMPARE_SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return detail, summary


def render_html(detail: pd.DataFrame, summary: dict) -> str:
    latest = detail.tail(20).copy()
    rows = []
    for _, row in latest.iterrows():
        rows.append(
            "<tr>"
            f"<td><code>{row['entry_ts']}</code></td>"
            f"<td><code>{row['runner_longs']}</code><br/><code>{row['runner_shorts']}</code></td>"
            f"<td><code>{row['asof_longs']}</code><br/><code>{row['asof_shorts']}</code></td>"
            f"<td><code>{row['basket_only_in_runner']}</code><br/><code>{row['basket_only_in_asof']}</code></td>"
            f"<td>{bool(row['basket_exact_match'])}</td>"
            f"<td>{float(row['long_overlap_rate']):.2f} / {float(row['short_overlap_rate']):.2f}</td>"
            f"<td>{bool(row['veto_count_match'])} / {bool(row['gate_match'])}</td>"
            f"<td>{bool(row['veto_mismatch'])} / {bool(row['gate_mismatch'])}</td>"
            f"<td>{float(row['runner_vs_asof_veto_net_diff_bps']):.2f}</td>"
            f"<td>{float(row['runner_vs_formal_gate_net_diff_bps']):.2f}</td>"
            "</tr>"
        )

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 shadow compare</title>
  <style>
    :root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--ok:#166534;--okbg:#dcfce7;--warn:#9a3412;--warnbg:#ffedd5;}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
    .wrap{{max-width:1180px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
    h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}} table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}} th{{background:#f8fafc}}
    code{{background:#eff6ff;border-radius:6px;padding:2px 6px}} .ok{{border-left:4px solid var(--ok);background:var(--okbg);padding:12px 14px;border-radius:10px}} .note{{border-left:4px solid var(--warn);background:var(--warnbg);padding:12px 14px;border-radius:10px}}
  </style>
</head>
<body><div class="wrap">
  <div class="card">
    <h1>Rank213 shadow compare</h1>
    <p class="muted">把当前 frozen-seed runner 的近期输出，与 raw-bar as-of basket 以及 formal frozen-gate reference 并排比较。这个页面的用途是审计当前接线与正式策略定义的一致性，不表示 live 已经完成。</p>
    <p><a href="/momentum/paper/rank213_largecap_xs_jump_veto.html">runner</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_readiness_note.html">readiness_note</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_formal_strategy_review.html">formal_strategy_review</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html">asof_universe_long_history_review</a></p>
  </div>

  <div class="card">
    <h2>证据上下文</h2>
    <div class="ok">as-of long-history: 1Y={summary['evidence_context']['asof_1Y']} / 3Y={summary['evidence_context']['asof_3Y']} / 6Y={summary['evidence_context']['asof_6Y']}</div>
    <div class="note" style="margin-top:12px">frozen current-universe readiness: 1Y={summary['evidence_context']['frozen_1Y']}</div>
  </div>

  <div class="card">
    <h2>汇总指标</h2>
    <ul>
      <li>runner_rows: <code>{summary['sample']['runner_rows']}</code></li>
      <li>matched_rows: <code>{summary['sample']['matched_rows']}</code></li>
      <li>basket_exact_match_rate: <code>{summary['compare_metrics']['basket_exact_match_rate']:.4f}</code></li>
      <li>veto_count_match_rate: <code>{summary['compare_metrics']['veto_count_match_rate']:.4f}</code></li>
      <li>gate_match_rate: <code>{summary['compare_metrics']['gate_match_rate']:.4f}</code></li>
      <li>gate_mismatch_rate: <code>{summary['compare_metrics']['gate_mismatch_rate']:.4f}</code></li>
      <li>veto_mismatch_rate: <code>{summary['compare_metrics']['veto_mismatch_rate']:.4f}</code></li>
      <li>basket_only_in_runner_rate: <code>{summary['compare_metrics']['basket_only_in_runner_rate']:.4f}</code></li>
      <li>basket_only_in_asof_rate: <code>{summary['compare_metrics']['basket_only_in_asof_rate']:.4f}</code></li>
      <li>avg_long_overlap_rate: <code>{summary['compare_metrics']['avg_long_overlap_rate']:.4f}</code></li>
      <li>avg_short_overlap_rate: <code>{summary['compare_metrics']['avg_short_overlap_rate']:.4f}</code></li>
      <li>mean_runner_vs_asof_veto_net_diff_bps: <code>{summary['compare_metrics']['mean_runner_vs_asof_veto_net_diff_bps']:.2f}</code></li>
      <li>mean_runner_vs_formal_gate_net_diff_bps: <code>{summary['compare_metrics']['mean_runner_vs_formal_gate_net_diff_bps']:.2f}</code></li>
    </ul>
    <p><b>aggregate evidence</b></p>
    <ul>
      <li>rows_with_runner_only_basket: <code>{summary['aggregate_evidence']['rows_with_runner_only_basket']}</code></li>
      <li>rows_with_asof_only_basket: <code>{summary['aggregate_evidence']['rows_with_asof_only_basket']}</code></li>
      <li>gate_mismatch_rows: <code>{summary['aggregate_evidence']['gate_mismatch_rows']}</code></li>
      <li>veto_mismatch_rows: <code>{summary['aggregate_evidence']['veto_mismatch_rows']}</code></li>
      <li>basket_only_in_runner_symbols: <code>{', '.join(summary['aggregate_evidence']['basket_only_in_runner_symbols'])}</code></li>
      <li>basket_only_in_asof_symbols: <code>{', '.join(summary['aggregate_evidence']['basket_only_in_asof_symbols'])}</code></li>
    </ul>
    <p class="muted">detail csv: <code>{summary['detail_csv']}</code></p>
  </div>

  <div class="card">
    <h2>最近样本对照</h2>
    <table>
      <thead><tr><th>entry_ts</th><th>runner basket</th><th>raw-bar asof basket</th><th>basket-only evidence<br/>runner / asof</th><th>exact</th><th>overlap</th><th>match<br/>veto / gate</th><th>mismatch<br/>veto / gate</th><th>runner-vs-asof bps</th><th>runner-vs-gate bps</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
</div></body>
</html>'''


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)
    detail, summary = build_compare()
    SITE_PATH.write_text(render_html(detail, summary), encoding="utf-8")
    print(json.dumps({
        "detail_csv": str(COMPARE_DETAIL_PATH.relative_to(ROOT)),
        "summary_json": str(COMPARE_SUMMARY_PATH.relative_to(ROOT)),
        "html": str(SITE_PATH.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
