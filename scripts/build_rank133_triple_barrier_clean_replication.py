#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASELINE_TRADE_LOG = ROOT / "reports" / "artifacts" / "scout_rank127_signal_confirm_atr_delta_phase_15m" / "trade_log.csv"
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank133_triple_barrier_honest_final_verdict_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank133_triple_barrier_honest_final_verdict_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank133_triple_barrier_honest_final_verdict_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
DIR_MAP = {"breakout_short": -1.0, "fib_retest_long": 1.0, "ema_psar_long": 1.0}
TP_MULTS = [0.75, 1.0, 1.25, 1.5]
SL_MULTS = [0.75, 1.0, 1.25]
TIMEOUTS = [6, 8, 12]
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
BASELINE_HOLD_BARS = 8
EPS = 1e-12

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def bps(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 10000:.2f} bps"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, bps_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    bps_cols = bps_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif col in bps_cols:
                text = bps(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def net_ret(gross: pd.Series | float, cost_bps: float) -> pd.Series | float:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def load_frames() -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for asset, symbol in ASSETS.items():
        df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)
        df["atr14"] = compute_atr(df)
        frames[asset] = df
    return frames


def load_baseline_catalog(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    trades = pd.read_csv(BASELINE_TRADE_LOG)
    trades = trades[trades["variant"] == "baseline"].copy()
    trades["signal_time"] = pd.to_datetime(trades["signal_time"], utc=True)
    trades["entry_time"] = pd.to_datetime(trades["entry_time"], utc=True)
    trades["exit_time"] = pd.to_datetime(trades["exit_time"], utc=True)
    trades["direction"] = trades["setup"].map(DIR_MAP)

    for asset, frame in frames.items():
        idx_map = {ts: idx for idx, ts in enumerate(frame["timestamp"])}
        atr_map = frame.set_index("timestamp")["atr14"]
        mask = trades["asset"] == asset
        trades.loc[mask, "entry_idx"] = trades.loc[mask, "entry_time"].map(idx_map)
        trades.loc[mask, "entry_atr14"] = trades.loc[mask, "entry_time"].map(atr_map)

    trades = trades.dropna(subset=["entry_idx", "entry_atr14", "direction"]).copy()
    trades["entry_idx"] = trades["entry_idx"].astype(int)
    return trades


def simulate_trade(row: pd.Series, frame: pd.DataFrame, tp_mult: float, sl_mult: float, timeout_bars: int) -> dict[str, object]:
    entry_idx = int(row["entry_idx"])
    entry_price = float(row["entry_price"])
    direction = float(row["direction"])
    atr = float(row["entry_atr14"])
    timeout_idx = min(entry_idx + int(timeout_bars), len(frame) - 1)
    path = frame.iloc[entry_idx: timeout_idx + 1]

    tp_px = entry_price * (1.0 + direction * (tp_mult * atr / max(entry_price, EPS)))
    sl_px = entry_price * (1.0 - direction * (sl_mult * atr / max(entry_price, EPS)))

    event = "timeout"
    exit_idx = timeout_idx
    exit_price = float(frame.iloc[timeout_idx]["close"])
    exit_time = frame.iloc[timeout_idx]["timestamp"]

    for idx, bar in path.iterrows():
        if direction > 0:
            tp_hit = float(bar["high"]) >= tp_px
            sl_hit = float(bar["low"]) <= sl_px
        else:
            tp_hit = float(bar["low"]) <= tp_px
            sl_hit = float(bar["high"]) >= sl_px
        if tp_hit and sl_hit:
            event = "sl_first"
            exit_idx = int(idx)
            exit_price = sl_px
            exit_time = bar["timestamp"]
            break
        if sl_hit:
            event = "sl_first"
            exit_idx = int(idx)
            exit_price = sl_px
            exit_time = bar["timestamp"]
            break
        if tp_hit:
            event = "tp_first"
            exit_idx = int(idx)
            exit_price = tp_px
            exit_time = bar["timestamp"]
            break

    gross_return = direction * (exit_price / entry_price - 1.0)
    fixed_positive = bool(float(row["gross_return"]) > 0)
    return {
        "tb_exit_idx": exit_idx,
        "tb_exit_time": exit_time,
        "tb_exit_price": exit_price,
        "tb_gross_return": gross_return,
        "tb_event": event,
        "timeout_bars": int(timeout_bars),
        "tp_mult": float(tp_mult),
        "sl_mult": float(sl_mult),
        "trade_count_retention": 1.0,
        "fixed_positive": fixed_positive,
        "tb_positive": bool(gross_return > 0),
        "fixed_pos_but_sl_first": bool(fixed_positive and event == "sl_first"),
        "fixed_neg_but_tp_first": bool((not fixed_positive) and event == "tp_first"),
    }


def summarize_pair(df: pd.DataFrame, split_cols: list[str]) -> pd.DataFrame:
    rows = []
    for keys, grp in df.groupby(split_cols):
        if not isinstance(keys, tuple):
            keys = (keys,)
        base = dict(zip(split_cols, keys))
        base.update(
            {
                "trades": int(len(grp)),
                "trade_count_retention": 1.0,
                "fixed_gross_mean": float(grp["gross_return"].mean()),
                "tb_gross_mean": float(grp["tb_gross_return"].mean()),
                "fixed_net_return_6bps": float(net_ret(grp["gross_return"], PRIMARY_COST).mean()),
                "tb_net_return_6bps": float(net_ret(grp["tb_gross_return"], PRIMARY_COST).mean()),
                "return_delta_6bps": float(net_ret(grp["tb_gross_return"], PRIMARY_COST).mean() - net_ret(grp["gross_return"], PRIMARY_COST).mean()),
                "tp_first_rate": float((grp["tb_event"] == "tp_first").mean()),
                "sl_first_rate": float((grp["tb_event"] == "sl_first").mean()),
                "timeout_share": float((grp["tb_event"] == "timeout").mean()),
                "fixed_pos_but_sl_first": float(grp["fixed_pos_but_sl_first"].mean()),
                "fixed_neg_but_tp_first": float(grp["fixed_neg_but_tp_first"].mean()),
            }
        )
        rows.append(base)
    return pd.DataFrame(rows)


def build_grid(df: pd.DataFrame, frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for tp_mult in TP_MULTS:
        for sl_mult in SL_MULTS:
            for timeout_bars in TIMEOUTS:
                tmp = []
                for row in df.itertuples(index=False):
                    sim = simulate_trade(pd.Series(row._asdict()), frames[row.asset], tp_mult, sl_mult, timeout_bars)
                    tmp.append({**row._asdict(), **sim})
                sim_df = pd.DataFrame(tmp)
                for split, grp in sim_df.groupby("split"):
                    rows.append(
                        {
                            "tp_mult": tp_mult,
                            "sl_mult": sl_mult,
                            "timeout_bars": timeout_bars,
                            "split": split,
                            "trades": int(len(grp)),
                            "fixed_net_return_6bps": float(net_ret(grp["gross_return"], PRIMARY_COST).mean()),
                            "tb_net_return_6bps": float(net_ret(grp["tb_gross_return"], PRIMARY_COST).mean()),
                            "return_delta_6bps": float(net_ret(grp["tb_gross_return"], PRIMARY_COST).mean() - net_ret(grp["gross_return"], PRIMARY_COST).mean()),
                            "tp_first_rate": float((grp["tb_event"] == "tp_first").mean()),
                            "sl_first_rate": float((grp["tb_event"] == "sl_first").mean()),
                            "timeout_share": float((grp["tb_event"] == "timeout").mean()),
                        }
                    )
    return pd.DataFrame(rows).sort_values(["split", "return_delta_6bps"], ascending=[True, False]).reset_index(drop=True)


def choose_config(grid: pd.DataFrame) -> dict[str, float]:
    train = grid[grid["split"] == "train"].copy()
    train = train.sort_values(["tb_net_return_6bps", "timeout_share", "tp_first_rate"], ascending=[False, True, False])
    best = train.iloc[0]
    return {
        "tp_mult": float(best["tp_mult"]),
        "sl_mult": float(best["sl_mult"]),
        "timeout_bars": int(best["timeout_bars"]),
    }


def make_scorecard(overall: pd.DataFrame, asset_summary: pd.DataFrame, grid: pd.DataFrame) -> pd.DataFrame:
    test = overall[overall["split"] == "test"].iloc[0]
    train = overall[overall["split"] == "train"].iloc[0]
    positive_assets = int((asset_summary[(asset_summary["split"] == "test")]["return_delta_6bps"] > 0).sum())
    positive_test_configs = int((grid[grid["split"] == "test"]["return_delta_6bps"] > 0).sum())
    row = {
        "rank": 133,
        "candidate": "triple barrier honest final-verdict layer",
        "time_stability": 2 if float(test["return_delta_6bps"]) > 0 and float(train["return_delta_6bps"]) > 0 else 1 if float(test["return_delta_6bps"]) > -0.0002 else 0,
        "parameter_stability": 2 if positive_test_configs >= 6 else 1 if positive_test_configs >= 1 else 0,
        "cross_asset_stability": 2 if positive_assets >= 2 else 1 if positive_assets == 1 else 0,
        "cost_trade_stability": 2 if float(test["return_delta_6bps"]) > 0 else 0,
        "hard_fail_flags": ", ".join(
            [
                flag
                for flag, cond in [
                    ("train_test_both_negative", float(train["return_delta_6bps"]) < 0 and float(test["return_delta_6bps"]) < 0),
                    ("no_positive_test_config", positive_test_configs == 0),
                    ("zero_positive_assets", positive_assets == 0),
                ]
                if cond
            ]
        ),
        "verdict": "park",
    }
    return pd.DataFrame([row])


def verdict_text(overall: pd.DataFrame, grid: pd.DataFrame, asset_summary: pd.DataFrame) -> tuple[str, str, str]:
    test = overall[overall["split"] == "test"].iloc[0]
    positive_test_configs = int((grid[grid["split"] == "test"]["return_delta_6bps"] > 0).sum())
    positive_assets = int((asset_summary[(asset_summary["split"] == "test")]["return_delta_6bps"] > 0).sum())
    if float(test["return_delta_6bps"]) < 0 and positive_test_configs == 0:
        return (
            "park",
            "最小 clean replication 明确没证明 triple-barrier verdict harness 比固定 8-bar 更诚实也更有用；训练与测试段都更差，且 36 个共享参数组合里没有一组在测试段跑赢固定 8-bar baseline。",
            f"测试段 6bps 下 return delta = {bps(float(test['return_delta_6bps']))}，正向资产数 = {positive_assets}/3，正向测试参数组 = {positive_test_configs}/36。",
        )
    return (
        "keep_P1",
        "它更像研究提醒而不是值得升格的 shared verdict harness。",
        f"测试段 6bps 下 return delta = {bps(float(test['return_delta_6bps']))}。",
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = load_frames()
    baseline = load_baseline_catalog(frames)
    if baseline.empty:
        raise SystemExit("rank133: no baseline trades found")

    grid = build_grid(baseline, frames)
    chosen = choose_config(grid)

    trade_rows = []
    for row in baseline.itertuples(index=False):
        sim = simulate_trade(pd.Series(row._asdict()), frames[row.asset], chosen["tp_mult"], chosen["sl_mult"], chosen["timeout_bars"])
        trade_rows.append({**row._asdict(), **sim})
    trade_log = pd.DataFrame(trade_rows).sort_values(["split", "asset", "setup", "entry_time"]).reset_index(drop=True)

    overall = summarize_pair(trade_log, ["split"]).sort_values(["split"]).reset_index(drop=True)
    setup_summary = summarize_pair(trade_log, ["split", "setup"]).sort_values(["split", "setup"]).reset_index(drop=True)
    asset_summary = summarize_pair(trade_log, ["split", "asset"]).sort_values(["split", "asset"]).reset_index(drop=True)

    cost_rows = []
    for split, grp in trade_log.groupby("split"):
        for cost in COSTS:
            cost_rows.append(
                {
                    "split": split,
                    "cost_bps": cost,
                    "fixed_net_return": float(net_ret(grp["gross_return"], cost).mean()),
                    "tb_net_return": float(net_ret(grp["tb_gross_return"], cost).mean()),
                    "return_delta": float(net_ret(grp["tb_gross_return"], cost).mean() - net_ret(grp["gross_return"], cost).mean()),
                }
            )
    cost_summary = pd.DataFrame(cost_rows).sort_values(["split", "cost_bps"]).reset_index(drop=True)

    scorecard = make_scorecard(overall, asset_summary, grid)
    verdict, verdict_body, verdict_tail = verdict_text(overall, grid, asset_summary)

    selected_config = grid[
        (grid["tp_mult"] == chosen["tp_mult"]) &
        (grid["sl_mult"] == chosen["sl_mult"]) &
        (grid["timeout_bars"] == chosen["timeout_bars"])
    ].copy().reset_index(drop=True)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = {
        "generated_at_utc": generated_at,
        "baseline_source": str(BASELINE_TRADE_LOG.relative_to(ROOT)),
        "frozen_entry_universe": "BTC/ETH/SOL perpetual 15m; breakout_short / fib_retest_long / ema_psar_long; next-bar open + no-overlap",
        "baseline_hold_bars": BASELINE_HOLD_BARS,
        "chosen_config": chosen,
        "verdict": verdict,
        "verdict_body": verdict_body,
        "verdict_tail": verdict_tail,
        "test_return_delta_6bps": float(overall[overall["split"] == "test"]["return_delta_6bps"].iloc[0]),
        "positive_test_configs": int((grid[grid["split"] == "test"]["return_delta_6bps"] > 0).sum()),
    }

    grid.to_csv(ART_DIR / "shared_barrier_grid.csv", index=False)
    selected_config.to_csv(ART_DIR / "selected_config.csv", index=False)
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    cost_summary.to_csv(ART_DIR / "cost_summary.csv", index=False)
    scorecard.to_csv(ART_DIR / "scout_promotion_scorecard.csv", index=False)
    (ART_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    test_overall = overall[overall["split"] == "test"].iloc[0]
    train_overall = overall[overall["split"] == "train"].iloc[0]
    positive_test_configs = int((grid[grid["split"] == "test"]["return_delta_6bps"] > 0).sum())

    report_body = f"""
    <p><a href=\"../../index.html\">← 站点首页</a> · <a href=\"../../reading/repo_scout/rank133_triple_barrier_honest_final_verdict_clean_replication.html\">读者摘要页</a></p>
    <h1>Rank 133 / triple barrier honest final-verdict layer — minimal clean replication</h1>
    <div class=\"card\">
      <p><strong>当前硬结论：</strong><span class=\"bad\">{escape(verdict)}</span></p>
      <p>{escape(verdict_body)}</p>
      <p class=\"muted\">{escape(verdict_tail)}</p>
      <p class=\"muted\">冻结样本：BTC/ETH/SOL perpetual 15m；breakout_short / fib_retest_long / ema_psar_long；沿用 Rank 127 baseline entry catalog，只改 post-entry verdict harness。</p>
      <p class=\"muted\">训练段冻结的共享参数：TP = {chosen['tp_mult']} ATR，SL = {chosen['sl_mult']} ATR，timeout = {chosen['timeout_bars']} bars。</p>
    </div>
    <div class=\"card\">
      <h2>总体结果（6 bps / side）</h2>
      {render_table(overall, percent_cols={'trade_count_retention','tp_first_rate','sl_first_rate','timeout_share','fixed_pos_but_sl_first','fixed_neg_but_tp_first'}, bps_cols={'fixed_gross_mean','tb_gross_mean','fixed_net_return_6bps','tb_net_return_6bps','return_delta_6bps'}, digits_cols={'trades':0})}
    </div>
    <div class=\"card\">
      <h2>为什么是 hard fail</h2>
      <ul>
        <li>训练段 6bps：fixed = {bps(float(train_overall['fixed_net_return_6bps']))}；triple-barrier = {bps(float(train_overall['tb_net_return_6bps']))}；delta = {bps(float(train_overall['return_delta_6bps']))}</li>
        <li>测试段 6bps：fixed = {bps(float(test_overall['fixed_net_return_6bps']))}；triple-barrier = {bps(float(test_overall['tb_net_return_6bps']))}；delta = {bps(float(test_overall['return_delta_6bps']))}</li>
        <li>36 个共享参数组合里，测试段 <strong>{positive_test_configs}</strong> 个跑赢固定 8-bar baseline。</li>
        <li>trade_count_retention 恒为 100%，说明问题不在“过滤后太稀”，而在“换 verdict harness 本身没有带来更好的 post-cost 结果”。</li>
      </ul>
    </div>
    <div class=\"card\">
      <h2>按 setup</h2>
      {render_table(setup_summary, percent_cols={'trade_count_retention','tp_first_rate','sl_first_rate','timeout_share','fixed_pos_but_sl_first','fixed_neg_but_tp_first'}, bps_cols={'fixed_gross_mean','tb_gross_mean','fixed_net_return_6bps','tb_net_return_6bps','return_delta_6bps'}, digits_cols={'trades':0})}
    </div>
    <div class=\"card\">
      <h2>按资产</h2>
      {render_table(asset_summary, percent_cols={'trade_count_retention','tp_first_rate','sl_first_rate','timeout_share','fixed_pos_but_sl_first','fixed_neg_but_tp_first'}, bps_cols={'fixed_gross_mean','tb_gross_mean','fixed_net_return_6bps','tb_net_return_6bps','return_delta_6bps'}, digits_cols={'trades':0})}
    </div>
    <div class=\"card\">
      <h2>成本稳定性</h2>
      {render_table(cost_summary, bps_cols={'fixed_net_return','tb_net_return','return_delta'}, digits_cols={'cost_bps':0})}
    </div>
    <div class=\"card\">
      <h2>参数平原</h2>
      <p class=\"muted\">下面只展示测试段最靠前的 10 组；完整表见 <code>shared_barrier_grid.csv</code>。</p>
      {render_table(grid[grid['split'] == 'test'].sort_values('return_delta_6bps', ascending=False).head(10), percent_cols={'tp_first_rate','sl_first_rate','timeout_share'}, bps_cols={'fixed_net_return_6bps','tb_net_return_6bps','return_delta_6bps'}, digits_cols={'trades':0,'tp_mult':2,'sl_mult':2,'timeout_bars':0})}
    </div>
    <div class=\"card\">
      <h2>最小读法</h2>
      <ul>
        <li>Triple-barrier 在论文里是个值得尊重的 honest verdict 框架，但放到当前 desk 这组冻结 entry catalog 上，<strong>它没有自然长成共享 alpha uplift</strong>。</li>
        <li>固定 8-bar positive 里，测试段仍有 {pct(float(test_overall['fixed_pos_but_sl_first']))} 的样本会在 triple-barrier 下先打到止损；这说明 fixed n-bar 的确会错判一部分 follow-up。</li>
        <li>但另一面，纠正错判并没有带来更好的成本后结果；因此它现在更像 <strong>诊断镜子</strong>，不像值得升格的 shared verdict harness。</li>
      </ul>
    </div>
    """
    write_html(SITE_DIR / "report.html", "Rank 133 triple barrier clean replication", report_body)

    reading_body = f"""
    <p><a href=\"../../factors/scout_rank133_triple_barrier_honest_final_verdict_15m/report.html\">← 返回详细报告</a> · <a href=\"../../index.html\">站点首页</a></p>
    <h1>Rank 133 / triple barrier honest final-verdict layer：最小 clean replication 结果</h1>
    <div class=\"card\">
      <p><strong>一句话结论：</strong><span class=\"bad\">park</span>。把固定 8-bar verdict 改成共享 triple-barrier（TP/SL/T）后，训练段和测试段都没有跑赢 baseline；测试段 36 组共享参数里也 0 组转正。</p>
      <p class=\"muted\">更新时间：{generated_at}</p>
    </div>
    <div class=\"card\">
      <h2>这次到底测了什么</h2>
      <ul>
        <li>冻结 entry：沿用 Rank 127 baseline trade catalog，不改三条 entry archetype。</li>
        <li>只改 verdict：fixed 8-bar close vs triple-barrier（TP = {chosen['tp_mult']} ATR, SL = {chosen['sl_mult']} ATR, timeout = {chosen['timeout_bars']} bars）。</li>
        <li>样本：BTC/ETH/SOL perpetual 15m；breakout_short / fib_retest_long / ema_psar_long；next-bar open + no-overlap。</li>
      </ul>
    </div>
    <div class=\"card\">
      <h2>最关键三行</h2>
      <ul>
        <li>训练段：6bps 下 delta = {bps(float(train_overall['return_delta_6bps']))}</li>
        <li>测试段：6bps 下 delta = {bps(float(test_overall['return_delta_6bps']))}</li>
        <li>测试段正向参数组：{positive_test_configs} / 36</li>
      </ul>
    </div>
    <div class=\"card\">
      <h2>所以现在该怎么读</h2>
      <ul>
        <li>Triple-barrier 作为“研究层判决镜子”仍有解释价值，但它还不值得升成当前 desk 的 shared paper candidate。</li>
        <li>因此 Rank 133 这轮更诚实的结论是 <strong>park</strong>，把默认预算让回给下一条 fresh intake。</li>
      </ul>
    </div>
    """
    write_html(READING_PATH, "Rank 133 clean replication", reading_body)


if __name__ == "__main__":
    main()
