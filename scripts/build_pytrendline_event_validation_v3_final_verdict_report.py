#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_crypto_180d"
CACHE_DIR = INPUT_ART / "cache"
OUT_ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_final_verdict"
OUT_SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_validation_v3_final_verdict"

PRIMARY_HORIZON = 24
CANDIDATES = [
    "support_breakout_raw",
    "support_breakout_confirm_1",
    "support_breakout_confirm_2",
    "support_rebound_confirm_1",
]
HORIZONS = [24, 48, 72]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_table(df: pd.DataFrame, limit: int = 100) -> str:
    if df is None or df.empty:
        return "<p><em>empty</em></p>"
    shown = df.head(limit).copy()
    for col in shown.columns:
        if pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d %H:%M")
        elif pd.api.types.is_float_dtype(shown[col]):
            shown[col] = shown[col].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return shown.to_html(index=False, classes="tbl", border=0)


def pct(x: float | int | None) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{float(x):.2%}"


def spct(x: float | int | None) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{float(x):+.2%}"


def load_events() -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    events = pd.read_csv(
        INPUT_ART / "event_sample_purged.csv",
        parse_dates=["event_timestamp", "confirm_timestamp", "action_timestamp", "snapshot_asof_timestamp"],
    )
    events = events.sort_values("action_timestamp").reset_index(drop=True)
    n = len(events)
    train_cut = max(1, int(np.floor(n * 0.6)))
    validate_cut = max(train_cut + 1, int(np.floor(n * 0.8)))
    ranks = np.arange(n)
    events["split"] = np.where(ranks < train_cut, "train", np.where(ranks < validate_cut, "validate", "test"))
    max_train_ts = pd.Timestamp(events.loc[train_cut - 1, "action_timestamp"])
    max_validate_ts = pd.Timestamp(events.loc[validate_cut - 1, "action_timestamp"])
    return events, max_train_ts, max_validate_ts


def compute_split_baseline(events: pd.DataFrame, max_train_ts: pd.Timestamp, max_validate_ts: pd.Timestamp) -> pd.DataFrame:
    rows: list[dict] = []
    for symbol in sorted(events["symbol"].unique()):
        cache_name = f"{symbol.replace('-', '_')}__180d__60m.csv"
        bars = pd.read_csv(CACHE_DIR / cache_name, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        for h in HORIZONS:
            eligible = len(bars) - 1 - h
            if eligible <= 0:
                continue
            opens = bars["open"].iloc[1 : 1 + eligible].to_numpy(float)
            closes = bars["close"].iloc[1 + h : 1 + h + eligible].to_numpy(float)
            ts = pd.to_datetime(bars["timestamp"].iloc[1 : 1 + eligible], utc=True).reset_index(drop=True)
            ret = closes / opens - 1.0
            split = np.where(ts <= max_train_ts, "train", np.where(ts <= max_validate_ts, "validate", "test"))
            for split_name in ["train", "validate", "test"]:
                mask = split == split_name
                rows.append(
                    {
                        "symbol": symbol,
                        "horizon": int(h),
                        "split": split_name,
                        "baseline_mean": float(np.mean(ret[mask])) if mask.any() else np.nan,
                        "eligible": int(mask.sum()),
                    }
                )
    return pd.DataFrame(rows)


def compute_candidate_tables(events: pd.DataFrame, baseline: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    by_asset_rows: list[dict] = []
    for event_type in CANDIDATES:
        g = events[events["event_type"].eq(event_type)].copy()
        for h in HORIZONS:
            col = f"fwd_ret_h{h}"
            for split_name in ["train", "validate", "test"]:
                sg = g[g["split"].eq(split_name)].copy()
                sym_excess: list[float] = []
                pos = neg = zero = 0
                for symbol, ssg in sg.groupby("symbol"):
                    b = baseline[(baseline["symbol"] == symbol) & (baseline["horizon"] == h) & (baseline["split"] == split_name)]
                    if b.empty:
                        continue
                    base_mean = float(b.iloc[0]["baseline_mean"])
                    event_mean = float(ssg[col].mean())
                    excess = event_mean - base_mean
                    sym_excess.append(excess)
                    if excess > 0:
                        pos += 1
                    elif excess < 0:
                        neg += 1
                    else:
                        zero += 1
                    by_asset_rows.append(
                        {
                            "event_type": event_type,
                            "horizon": int(h),
                            "split": split_name,
                            "symbol": symbol,
                            "events": int(len(ssg)),
                            "event_mean": event_mean,
                            "baseline_mean": base_mean,
                            "excess": excess,
                        }
                    )
                rows.append(
                    {
                        "event_type": event_type,
                        "horizon": int(h),
                        "split": split_name,
                        "events": int(len(sg)),
                        "event_mean": float(sg[col].mean()) if not sg.empty else np.nan,
                        "avg_excess_ret": float(np.mean(sym_excess)) if sym_excess else np.nan,
                        "pos_symbols_excess": int(pos),
                        "neg_symbols_excess": int(neg),
                        "zero_symbols_excess": int(zero),
                    }
                )
    return pd.DataFrame(rows), pd.DataFrame(by_asset_rows)


def build_param_robustness(summary: pd.DataFrame, by_asset: pd.DataFrame) -> pd.DataFrame:
    h24 = summary[summary["horizon"] == PRIMARY_HORIZON].copy()
    rows: list[dict] = []
    best = by_asset[
        (by_asset["horizon"] == PRIMARY_HORIZON)
        & (by_asset["split"].isin(["validate", "test"]))
        & (by_asset["event_type"].isin(CANDIDATES[:3]))
    ].copy()
    best_idx = best.groupby(["split", "symbol"], sort=False)["excess"].idxmin() if not best.empty else []
    best_counts = best.loc[best_idx, "event_type"].value_counts().to_dict() if len(best_idx) else {}

    for event_type in CANDIDATES[:3]:
        train = h24[(h24["event_type"] == event_type) & (h24["split"] == "train")]
        validate = h24[(h24["event_type"] == event_type) & (h24["split"] == "validate")]
        test = h24[(h24["event_type"] == event_type) & (h24["split"] == "test")]
        tr = train.iloc[0] if not train.empty else None
        va = validate.iloc[0] if not validate.empty else None
        te = test.iloc[0] if not test.empty else None
        oos_avg = float(np.nanmean([va["avg_excess_ret"] if va is not None else np.nan, te["avg_excess_ret"] if te is not None else np.nan]))
        stable_neg_splits = int(sum(1 for row in [va, te] if row is not None and float(row["avg_excess_ret"]) < 0))
        neg_assets_oos = int(sum(int(row["neg_symbols_excess"]) for row in [va, te] if row is not None))
        if event_type == "support_breakout_confirm_2":
            reading = "confirm=2 在这圈邻域里最不稳：validate 已经翻成正 excess，不适合当 primary。"
        elif event_type == "support_breakout_raw":
            reading = "raw 在 validate 更干净（4/4 负 excess），说明不加确认并没有被直接淘汰。"
        else:
            reading = "confirm=1 在 test 更强，但 validate 不如 raw 干净；更像 co-primary，而不是压倒性第一。"
        rows.append(
            {
                "event_type": event_type,
                "train_h24_excess": float(tr["avg_excess_ret"]) if tr is not None else np.nan,
                "validate_h24_excess": float(va["avg_excess_ret"]) if va is not None else np.nan,
                "test_h24_excess": float(te["avg_excess_ret"]) if te is not None else np.nan,
                "oos_avg_excess": oos_avg,
                "validate_neg_assets": int(va["neg_symbols_excess"]) if va is not None else 0,
                "test_neg_assets": int(te["neg_symbols_excess"]) if te is not None else 0,
                "best_cell_count_validate_test": int(best_counts.get(event_type, 0)),
                "reading": reading,
            }
        )
    return pd.DataFrame(rows)


def build_horizon_secondary(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for event_type in ["support_breakout_raw", "support_breakout_confirm_1"]:
        for h in HORIZONS:
            validate = summary[(summary["event_type"] == event_type) & (summary["horizon"] == h) & (summary["split"] == "validate")]
            test = summary[(summary["event_type"] == event_type) & (summary["horizon"] == h) & (summary["split"] == "test")]
            va = validate.iloc[0] if not validate.empty else None
            te = test.iloc[0] if not test.empty else None
            if h == 24:
                reading = "主评估 horizon；当前最适合拿来做最终 honesty judgement。"
            elif event_type == "support_breakout_confirm_1" and h in [48, 72]:
                reading = "可以做 secondary check，但不如 h24 干净；不要拿它替代主结论。"
            else:
                reading = "方向还偏负，但 split 内资产同向性开始松动。"
            rows.append(
                {
                    "event_type": event_type,
                    "horizon": int(h),
                    "validate_excess": float(va["avg_excess_ret"]) if va is not None else np.nan,
                    "test_excess": float(te["avg_excess_ret"]) if te is not None else np.nan,
                    "validate_neg_assets": int(va["neg_symbols_excess"]) if va is not None else 0,
                    "test_neg_assets": int(te["neg_symbols_excess"]) if te is not None else 0,
                    "reading": reading,
                }
            )
    return pd.DataFrame(rows)


def build_final_verdict(summary: pd.DataFrame, robustness: pd.DataFrame) -> pd.DataFrame:
    h24 = summary[summary["horizon"] == PRIMARY_HORIZON].copy().set_index(["event_type", "split"])
    def val(event_type: str, split: str, col: str) -> float:
        if (event_type, split) not in h24.index:
            return np.nan
        return float(h24.loc[(event_type, split), col])

    rows = [
        {
            "object": "support_breakout_raw @ h24",
            "verdict": "keep as alpha candidate",
            "why": "validate 与 test 都是负 excess；validate 4/4 资产同向为负，说明它不是只在单一币种上好看。",
            "key_numbers": f"validate {spct(val('support_breakout_raw','validate','avg_excess_ret'))}, test {spct(val('support_breakout_raw','test','avg_excess_ret'))}",
        },
        {
            "object": "support_breakout_confirm_1 @ h24",
            "verdict": "keep as co-primary alpha candidate",
            "why": "test 段比 raw 更负，但 validate 没有 raw 那么干净；最合理的身份是并列第一梯队。",
            "key_numbers": f"validate {spct(val('support_breakout_confirm_1','validate','avg_excess_ret'))}, test {spct(val('support_breakout_confirm_1','test','avg_excess_ret'))}",
        },
        {
            "object": "support_breakout_confirm_2 @ h24",
            "verdict": "park as primary variant",
            "why": "confirm=2 在这轮小参数邻域里明显更不稳；validate 已翻成正 excess，不适合继续占主资源。",
            "key_numbers": f"validate {spct(val('support_breakout_confirm_2','validate','avg_excess_ret'))}, test {spct(val('support_breakout_confirm_2','test','avg_excess_ret'))}",
        },
        {
            "object": "support_rebound_confirm_1 @ h24",
            "verdict": "keep as feature/watch, not alpha",
            "why": "它没有给出持续、干净的正 excess；更像观察名单，不像可以直接毕业成 long alpha。",
            "key_numbers": f"validate {spct(val('support_rebound_confirm_1','validate','avg_excess_ret'))}, test {spct(val('support_rebound_confirm_1','test','avg_excess_ret'))}",
        },
        {
            "object": "V3 overall",
            "verdict": "close research line with breakout-short candidate retained",
            "why": "v3 作为事件研究页已经回答了最关键问题：有一个还值得保留的 breakout-short 候选，但还不够支持“正式生产 alpha 已确认”。更合理的收工方式是保留 candidate，停止继续在 v3 页里无限扩题。",
            "key_numbers": "best retained objects = support_breakout_raw / support_breakout_confirm_1 @ h24",
        },
    ]
    return pd.DataFrame(rows)


def chart_split_excess(summary: pd.DataFrame, out_path: Path) -> None:
    h24 = summary[(summary["horizon"] == PRIMARY_HORIZON) & (summary["event_type"].isin(CANDIDATES))].copy()
    if h24.empty:
        return
    split_order = ["train", "validate", "test"]
    cand_order = CANDIDATES
    fig, ax = plt.subplots(figsize=(12, 5.8))
    x = np.arange(len(cand_order))
    width = 0.22
    colors = {"train": "#94a3b8", "validate": "#2563eb", "test": "#dc2626"}
    for i, split_name in enumerate(split_order):
        vals = []
        for c in cand_order:
            row = h24[(h24["event_type"] == c) & (h24["split"] == split_name)]
            vals.append(float(row.iloc[0]["avg_excess_ret"]) if not row.empty else 0.0)
        ax.bar(x + (i - 1) * width, vals, width=width, label=split_name, color=colors[split_name])
    ax.axhline(0, color="#334155", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(cand_order, rotation=20, ha="right")
    ax.set_ylabel("avg excess return vs split baseline")
    ax.set_title("180d core4 OOS honesty: split-specific excess @ h24")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close(fig)


def chart_horizon_secondary(secondary: pd.DataFrame, out_path: Path) -> None:
    d = secondary.copy()
    if d.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5.4))
    colors = {
        "support_breakout_raw": "#2563eb",
        "support_breakout_confirm_1": "#f59e0b",
    }
    for event_type in ["support_breakout_raw", "support_breakout_confirm_1"]:
        s = d[d["event_type"] == event_type].sort_values("horizon")
        ax.plot(s["horizon"], s["test_excess"], marker="o", label=f"{event_type} test", color=colors[event_type])
    ax.axhline(0, color="#334155", linewidth=1)
    ax.set_xlabel("horizon")
    ax.set_ylabel("test avg excess return")
    ax.set_title("Secondary check: test excess by horizon")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close(fig)


def main() -> int:
    ensure_dir(OUT_ART)
    ensure_dir(OUT_SITE)

    events, max_train_ts, max_validate_ts = load_events()
    baseline = compute_split_baseline(events, max_train_ts, max_validate_ts)
    summary, by_asset = compute_candidate_tables(events, baseline)
    robustness = build_param_robustness(summary, by_asset)
    secondary = build_horizon_secondary(summary)
    verdict = build_final_verdict(summary, robustness)

    summary.to_csv(OUT_ART / "candidate_split_excess_summary.csv", index=False)
    by_asset.to_csv(OUT_ART / "candidate_split_excess_by_asset.csv", index=False)
    baseline.to_csv(OUT_ART / "baseline_split_summary.csv", index=False)
    robustness.to_csv(OUT_ART / "confirm_neighborhood_h24.csv", index=False)
    secondary.to_csv(OUT_ART / "secondary_horizon_check.csv", index=False)
    verdict.to_csv(OUT_ART / "final_verdict.csv", index=False)
    (OUT_ART / "split_cuts.json").write_text(
        json.dumps(
            {
                "train_max_action_timestamp": max_train_ts.isoformat(),
                "validate_max_action_timestamp": max_validate_ts.isoformat(),
                "event_rows": int(len(events)),
                "source_artifact_dir": str(INPUT_ART),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    chart_split_excess(summary, OUT_SITE / "split_excess_h24.png")
    chart_horizon_secondary(secondary, OUT_SITE / "horizon_secondary_test_excess.png")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    h24 = summary[summary["horizon"] == PRIMARY_HORIZON].copy().set_index(["event_type", "split"])

    def s(event_type: str, split: str, col: str) -> float:
        if (event_type, split) not in h24.index:
            return np.nan
        return float(h24.loc[(event_type, split), col])

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>PyTrendline Event Validation v3 Final Verdict</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 28px 18px 48px; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px 22px; margin-bottom: 18px; }}
    .muted {{ color: #64748b; }}
    .warn {{ background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; border-radius: 10px; padding: 10px 12px; }}
    .pill {{ display: inline-block; margin-right: 8px; margin-top: 8px; padding: 5px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    .tbl th, .tbl td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; vertical-align: top; }}
    .tbl th {{ background: #f8fafc; }}
    ul, ol {{ line-height: 1.7; }}
    img.chart {{ width: 100%; max-width: 1000px; border: 1px solid #e2e8f0; border-radius: 12px; background: white; }}
    code {{ background: #eff6ff; padding: 1px 5px; border-radius: 6px; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p><a href=\"../../index.html\">← 返回站点首页</a></p>

    <div class=\"card\">
      <h1>PyTrendline Event Validation v3 · Final Verdict</h1>
      <p class=\"muted\">这页只做一件事：给 v3 一个尽量诚实、足够能收工的结论。我们不再继续无限加样本、加市场、加参数，而是直接回答：<b>v3 里到底还有哪些对象值得保留，哪些该降级，哪些可以 park</b>。</p>
      <div>
        <span class=\"pill\">Generated: {escape(generated_at)}</span>
        <span class=\"pill\">source: 180d core4 / 60m / purged events</span>
        <span class=\"pill\">split: 60% train / 20% validate / 20% test</span>
        <span class=\"pill\">primary horizon: h24</span>
        <span class=\"pill\">small-param neighborhood: confirm = 0 / 1 / 2</span>
      </div>
    </div>

    <div class=\"card\">
      <h2>先说结论（最短版）</h2>
      <ul>
        <li><b>可以保留的对象：</b><code>support_breakout_raw @ h24</code> 和 <code>support_breakout_confirm_1 @ h24</code>。它们当前更像 <b>continuation short 候选</b>，但还不够格被写成“正式生产 alpha 已确认”。</li>
        <li><b>不该继续占主资源的对象：</b><code>support_breakout_confirm_2</code>。在这轮最小参数邻域里，它已经明显更不稳。</li>
        <li><b>没有毕业成 alpha 的对象：</b><code>support_rebound_confirm_1</code>。它更像 <b>watch / feature</b>，不是 clean long alpha。</li>
        <li><b>对 v3 整体的 final call：</b><b>可以收工</b>，但收工方式不是“确认了一个成熟 production alpha”，而是——<b>保留 breakout short 候选，关闭 v3 这条研究线，把后续动作移到更窄、更像实现验证的后继任务里。</b></li>
      </ul>
      <p class=\"warn\"><b>一句人话：</b>v3 最终没告诉我们“趋势线反弹能稳定做多”，但它留下了一个仍值得保留的结论：<b>support-breakout 这类事件，在 h24 上更像 continuation short 候选</b>，只是强度没有强到可以直接毕业成正式阿尔法。</p>
    </div>

    <div class=\"card\">
      <h2>这页怎么做判断</h2>
      <ol>
        <li><b>先做 OOS honesty：</b>把 180d core4 的 purged 事件按全局时间顺序切成 <code>train / validate / test</code>。</li>
        <li><b>再看 split-specific excess：</b>不是只看事件后收益是否为负，而是看它是否比同一时段、同一资产的无条件基线更弱。</li>
        <li><b>最后做最小参数稳健性：</b>这次不跑大全参数搜索，只看 breakout short 最邻近的 <code>confirm = 0 / 1 / 2</code> 三档，判断它是不是一碰就碎。</li>
      </ol>
      <p class=\"muted\">为什么用这套最小协议？因为目标是“尽快收工”，不是再开一条更大的研究支线。</p>
    </div>

    <div class=\"card\">
      <h2>Chart 1 · OOS honesty 主图（h24）</h2>
      <img class=\"chart\" src=\"split_excess_h24.png\" alt=\"split excess h24\" />
      <ul>
        <li><b>怎么读：</b>柱子低于 0，表示这个事件在该 split 里比同段基线更弱，也就更像 short continuation 候选。</li>
        <li><b>图里最值得看的不是 train，而是 validate / test。</b> train 容易受样本内巧合影响；真正更有决策价值的是后两段有没有翻脸。</li>
        <li><b>这张图告诉我们的核心：</b><code>support_breakout_raw</code> 和 <code>support_breakout_confirm_1</code> 在 test 都还是干净负 excess；而 <code>confirm_2</code> 已经开始不稳。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>OOS honesty 细表（180d core4, split-specific excess）</h2>
      <p class=\"muted\">这张表是主判据。别只盯 <code>event_mean</code>，更该看 <code>avg_excess_ret</code> 和每个 split 里有多少资产同向为负。</p>
      {render_table(summary.sort_values(["event_type", "horizon", "split"]).reset_index(drop=True), limit=80)}
      <ul>
        <li><b>support_breakout_raw @ h24：</b>validate = <b>{spct(s('support_breakout_raw','validate','avg_excess_ret'))}</b>，test = <b>{spct(s('support_breakout_raw','test','avg_excess_ret'))}</b>。翻成人话：它没在 OOS 段直接塌掉。</li>
        <li><b>support_breakout_confirm_1 @ h24：</b>validate = <b>{spct(s('support_breakout_confirm_1','validate','avg_excess_ret'))}</b>，test = <b>{spct(s('support_breakout_confirm_1','test','avg_excess_ret'))}</b>。test 比 raw 更负，但 validate 不如 raw 干净。</li>
        <li><b>support_breakout_confirm_2 @ h24：</b>validate 已到 <b>{spct(s('support_breakout_confirm_2','validate','avg_excess_ret'))}</b>。这意味着确认再加一层，并没有把信号“救活”成更稳的版本。</li>
        <li><b>support_rebound_confirm_1 @ h24：</b>validate = <b>{spct(s('support_rebound_confirm_1','validate','avg_excess_ret'))}</b>，test = <b>{spct(s('support_rebound_confirm_1','test','avg_excess_ret'))}</b>。所以它仍不适合被写成 long alpha。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>小参数稳健性（confirm 邻域：0 / 1 / 2）</h2>
      <p class=\"muted\">这页的小参数稳健性，不是全网格爆搜，而是只围着当前 breakout-short 候选看最近的一圈邻域：不确认 / 1-bar 确认 / 2-bar 确认。</p>
      {render_table(robustness, limit=20)}
      <ul>
        <li><b>这圈邻域没有一起塌：</b><code>raw</code> 和 <code>confirm_1</code> 都还活着，所以 breakout short 不是“只在一个参数点上碰巧成立”。</li>
        <li><b>但它也没有稳到能只留一个：</b><code>raw</code> 在 validate 更干净，<code>confirm_1</code> 在 test 更强，所以更合理的说法是 <b>co-primary</b>，而不是压倒性冠军。</li>
        <li><b>confirm_2 可以先放下：</b>它在 validate 已翻正，不值得继续占主研究资源。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>Chart 2 · 次级检查（horizon secondary check）</h2>
      <img class=\"chart\" src=\"horizon_secondary_test_excess.png\" alt=\"horizon secondary\" />
      <p class=\"muted\">这张图只回答一个问题：如果不只看 h24，而把眼睛伸到 h48 / h72，会不会马上完全翻脸？</p>
      {render_table(secondary, limit=20)}
      <ul>
        <li><b>主结论仍该锁在 h24：</b>因为这是当前最稳、也最容易讲清楚的一档。</li>
        <li><b>h48 / h72 只能做 secondary check：</b>它们没有完全推翻 breakout short，但 split 内稳定度已经开始松动，不适合拿来替代主 verdict。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>Final verdict</h2>
      {render_table(verdict, limit=20)}
      <ul>
        <li><b>keep as alpha candidate：</b><code>support_breakout_raw @ h24</code></li>
        <li><b>keep as co-primary alpha candidate：</b><code>support_breakout_confirm_1 @ h24</code></li>
        <li><b>park as primary variant：</b><code>support_breakout_confirm_2</code></li>
        <li><b>keep as feature/watch：</b><code>support_rebound_confirm_1</code></li>
        <li><b>V3 overall：</b><b>可以收工</b>。后续若还要做，不该继续叫“v3 研究扩写”，而该进入更窄的后继线：例如实现层、成本层、执行层、或独立 alpha-candidate follow-up。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>收工建议（执行版）</h2>
      <ol>
        <li><b>把 v3 正式收尾：</b>这页就是 v3 的 final verdict，不再继续往 v3 里追加 365d、跨市场、大全参数搜索。</li>
        <li><b>如果要继续做，只保留一个更窄的新问题：</b><code>support_breakout_raw / confirm_1 @ h24</code> 是否能在加入交易成本、执行延迟、非重叠持仓规则后，仍保有优势。</li>
        <li><b>rebound long 这条线先别再烧主资源：</b>它当前更适合留在 watchlist 或特征池里。</li>
      </ol>
      <p class=\"warn\"><b>最后一句：</b>v3 的价值在于帮我们筛掉了很多看起来漂亮但不稳的东西，并留下了一个还值得保留的 breakout-short 候选。对研究来说，这已经是一个合格的“收工点”。</p>
    </div>

    <div class=\"card\">
      <h2>Artifacts</h2>
      <ul>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_final_verdict/candidate_split_excess_summary.csv'>candidate_split_excess_summary.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_final_verdict/candidate_split_excess_by_asset.csv'>candidate_split_excess_by_asset.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_final_verdict/baseline_split_summary.csv'>baseline_split_summary.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_final_verdict/confirm_neighborhood_h24.csv'>confirm_neighborhood_h24.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_final_verdict/secondary_horizon_check.csv'>secondary_horizon_check.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_final_verdict/final_verdict.csv'>final_verdict.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_final_verdict/split_cuts.json'>split_cuts.json</a></li>
        <li><a href='../pytrendline_event_validation_v3/report.html'>120d 主报告</a></li>
        <li><a href='../pytrendline_event_validation_v3_crypto_180d/report.html'>180d 扩样本报告</a></li>
      </ul>
    </div>
  </div>
</body>
</html>
"""

    (OUT_SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"[ok] v3 final verdict report -> {OUT_SITE / 'report.html'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
