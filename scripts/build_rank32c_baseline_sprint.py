#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32c_baseline_sprint"
REPORT_PATH = ROOT / "research" / "strategy_review" / "2026-05-04_rank32c_baseline_sprint.md"
CONFIG_PATH = ROOT / "config" / "strategies" / "rank32c_btc_utc_weak_cell_tiny_live.yaml"

RAW_15M_DIR = (
    ROOT
    / "reports"
    / "artifacts"
    / "paper_rank213_largecap_xs_jump_veto"
    / "rank213_local_cache"
    / "monthly_marketcap_universe"
    / "raw_15m"
)

SYMBOL = "BTCUSDT"
ONBOARD_UTC = "2019-09-25T08:00:00Z"
BAR_MINUTES = 15
BASELINE_TRAIN_DAYS = 60
BASELINE_HOLD_BARS = 16
BASELINE_BOTTOM_K = 1
BASELINE_COST_BPS = 8.0
EXEC_COST_BPS = 12.0
VETO_LOOKBACK_DAYS = 180
VETO_SIGMA = 2.0
GATE_EDGE_MULT = 1.0


@dataclass(frozen=True)
class RunSpec:
    name: str
    train_days: int = BASELINE_TRAIN_DAYS
    hold_bars: int = BASELINE_HOLD_BARS
    bottom_k: int = BASELINE_BOTTOM_K
    cost_bps: float = BASELINE_COST_BPS
    use_veto: bool = False
    use_gate: bool = False
    entry_delay_bars: int = 0


def ensure_dirs() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def read_kline_zip(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as zf:
        members = zf.namelist()
        if not members:
            return pd.DataFrame(columns=["timestamp", "open", "close"])
        data = zf.read(members[0])
    df = pd.read_csv(
        io.BytesIO(data),
        header=None,
        usecols=[0, 1, 4],
        names=["open_time", "open", "close"],
    )
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df["open"] = pd.to_numeric(df["open"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["open_time", "open", "close"])
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "open", "close"])
    df["timestamp"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True)
    return df[["timestamp", "open", "close"]].drop_duplicates("timestamp").sort_values("timestamp")


def load_symbol_bars(symbol: str) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for subdir in ["monthly", "daily"]:
        d = RAW_15M_DIR / subdir / symbol
        if not d.exists():
            continue
        for path in sorted(d.glob(f"{symbol}-15m-*.zip")):
            part = read_kline_zip(path)
            if not part.empty:
                parts.append(part)
    if not parts:
        raise FileNotFoundError(f"no cached 15m zip data under {RAW_15M_DIR}")
    out = pd.concat(parts, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
    out = out.set_index("timestamp")
    out = out[~out.index.duplicated(keep="last")]
    out = out.astype({"open": float, "close": float})
    prev24 = (out["open"].shift(1) / out["open"].shift(97) - 1.0).abs()
    roll = prev24.rolling(VETO_LOOKBACK_DAYS * 96, min_periods=30 * 96)
    threshold = roll.mean() + VETO_SIGMA * roll.std(ddof=0)
    out["veto_high_vol"] = (prev24 > threshold).fillna(False).astype(bool)
    return out


def max_drawdown(ret: pd.Series) -> float:
    if ret.empty:
        return float("nan")
    eq = (1.0 + ret).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def metrics(ret: pd.Series) -> dict:
    ret = ret.dropna()
    if ret.empty:
        return {
            "trades": 0,
            "net_mean_bps": np.nan,
            "net_cum_pct": np.nan,
            "max_drawdown_pct": np.nan,
            "win_rate_pct": np.nan,
            "positive_year_ratio_pct": np.nan,
            "avg_trades_per_month": np.nan,
        }
    eq = (1.0 + ret).cumprod()
    yearly = ret.groupby(ret.index.year).apply(lambda s: (1.0 + s).prod() - 1.0)
    monthly_counts = ret.groupby(ret.index.strftime("%Y-%m")).size()
    return {
        "trades": int(len(ret)),
        "net_mean_bps": float(ret.mean() * 10000.0),
        "net_cum_pct": float((eq.iloc[-1] - 1.0) * 100.0),
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0),
        "win_rate_pct": float((ret > 0).mean() * 100.0),
        "positive_year_ratio_pct": float((yearly > 0).mean() * 100.0),
        "avg_trades_per_month": float(monthly_counts.mean()),
    }


def build_event_frame(bars: pd.DataFrame, hold_bars: int, entry_delay_bars: int) -> pd.DataFrame:
    openp = bars["open"]
    entry = openp.shift(-entry_delay_bars)
    exitp = openp.shift(-(entry_delay_bars + hold_bars))
    ev = pd.DataFrame(
        {
            "open": openp,
            "entry_open": entry,
            "exit_open": exitp,
            "long_ret": exitp / entry - 1.0,
        }
    ).dropna()
    ev["dow"] = ev.index.dayofweek
    ev["hour"] = ev.index.hour
    ev["month"] = ev.index.strftime("%Y-%m")
    ev["veto_high_vol"] = bars["veto_high_vol"].reindex(ev.index).fillna(False).astype(bool)
    return ev


def run_strategy(bars: pd.DataFrame, spec: RunSpec) -> tuple[pd.DataFrame, pd.DataFrame]:
    ev = build_event_frame(bars, spec.hold_bars, spec.entry_delay_bars)
    rows: list[dict] = []
    selections: list[dict] = []
    last_exit_ts: pd.Timestamp | None = None

    for month in sorted(ev["month"].unique()):
        month_start = pd.Timestamp(f"{month}-01", tz="UTC")
        train_start = month_start - pd.Timedelta(days=spec.train_days)
        train = ev[(ev.index >= train_start) & (ev.index < month_start)]
        if train.empty:
            continue

        min_n = max(3, spec.train_days // 14)
        stats = (
            train.groupby(["dow", "hour"])
            .agg(train_mean_long_ret=("long_ret", "mean"), train_events=("long_ret", "size"))
            .reset_index()
        )
        stats = stats[stats["train_events"] >= min_n].sort_values("train_mean_long_ret")
        if spec.use_gate:
            stats = stats[stats["train_mean_long_ret"] < -(spec.cost_bps / 10000.0) * GATE_EDGE_MULT]
        stats = stats.head(spec.bottom_k)
        if stats.empty:
            continue

        cells = {(int(r.dow), int(r.hour)) for r in stats.itertuples(index=False)}
        for r in stats.itertuples(index=False):
            selections.append(
                {
                    "variant": spec.name,
                    "month": month,
                    "dow": int(r.dow),
                    "hour": int(r.hour),
                    "train_mean_long_bps": float(r.train_mean_long_ret * 10000.0),
                    "train_events": int(r.train_events),
                }
            )

        test = ev[ev["month"] == month]
        cell_mask = pd.Series(False, index=test.index)
        for dow, hour in cells:
            cell_mask |= (test["dow"] == dow) & (test["hour"] == hour)
        test = test[cell_mask]
        for ts, row in test.iterrows():
            if last_exit_ts is not None and ts < last_exit_ts:
                continue
            if spec.use_veto and bool(row["veto_high_vol"]):
                continue
            exit_pos = bars.index.get_indexer([ts], method=None)[0] + spec.entry_delay_bars + spec.hold_bars
            if exit_pos >= len(bars.index):
                continue
            exit_ts = bars.index[exit_pos]
            net_ret = -float(row["long_ret"]) - spec.cost_bps / 10000.0
            rows.append(
                {
                    "variant": spec.name,
                    "entry_signal_ts": to_iso(ts),
                    "entry_delay_bars": spec.entry_delay_bars,
                    "entry_exec_ts": to_iso(bars.index[bars.index.get_loc(ts) + spec.entry_delay_bars]),
                    "exit_exec_ts": to_iso(exit_ts),
                    "month": month,
                    "dow": int(row["dow"]),
                    "hour": int(row["hour"]),
                    "hold_bars": spec.hold_bars,
                    "train_days": spec.train_days,
                    "bottom_k": spec.bottom_k,
                    "cost_bps": spec.cost_bps,
                    "short_gross_ret": -float(row["long_ret"]),
                    "net_ret": net_ret,
                    "veto_high_vol": bool(row["veto_high_vol"]),
                }
            )
            last_exit_ts = exit_ts

    trades = pd.DataFrame(rows)
    selections_df = pd.DataFrame(selections)
    return trades, selections_df


def summarize_variant(trades: pd.DataFrame, spec: RunSpec) -> dict:
    ret = pd.Series(dtype=float)
    if not trades.empty:
        ret = pd.Series(trades["net_ret"].astype(float).to_numpy(), index=pd.to_datetime(trades["entry_exec_ts"], utc=True))
    return {
        "variant": spec.name,
        "train_days": spec.train_days,
        "hold_bars": spec.hold_bars,
        "bottom_k": spec.bottom_k,
        "cost_bps": spec.cost_bps,
        "use_veto": spec.use_veto,
        "use_gate": spec.use_gate,
        "entry_delay_bars": spec.entry_delay_bars,
        **metrics(ret),
    }


def yearly_metrics(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    out = []
    for (variant, year), sub in trades.groupby(["variant", pd.to_datetime(trades["entry_exec_ts"], utc=True).dt.year]):
        ret = pd.Series(sub["net_ret"].astype(float).to_numpy(), index=pd.to_datetime(sub["entry_exec_ts"], utc=True))
        out.append({"variant": variant, "year": int(year), **metrics(ret)})
    return pd.DataFrame(out)


def plateau_grid(bars: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for train_days in [30, 60, 90, 180, 365]:
        for hold_bars in [16, 32]:
            for bottom_k in [1, 3]:
                spec = RunSpec(
                    name=f"plateau_t{train_days}_h{hold_bars}_k{bottom_k}",
                    train_days=train_days,
                    hold_bars=hold_bars,
                    bottom_k=bottom_k,
                    cost_bps=BASELINE_COST_BPS,
                )
                trades, _ = run_strategy(bars, spec)
                rows.append(summarize_variant(trades, spec))
    return pd.DataFrame(rows).sort_values(["net_mean_bps", "net_cum_pct"], ascending=False)


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return f'"{value}"'


def write_tiny_live_config(summary: dict, baseline_pass: bool) -> None:
    if not baseline_pass:
        if CONFIG_PATH.exists():
            CONFIG_PATH.unlink()
        return
    cfg = {
        "strategy_id": "rank32c_btc_utc_weak_cell_v1",
        "mode": "tiny_live_candidate",
        "symbol": SYMBOL,
        "bar_interval": "15m",
        "universe_rule": "fixed BTCUSDT only; eligible after Binance UM onboard timestamp; no current-volume or winner selection",
        "baseline": f"monthly trailing {BASELINE_TRAIN_DAYS}d weekday-hour weak-cell short",
        "entry": "at selected weekday/hour bar open; production should place reduce-only-disabled market/IOC with max spread guard",
        "exit": f"time stop after {BASELINE_HOLD_BARS} bars",
        "cost_assumption_bps_round_trip": BASELINE_COST_BPS,
        "tiny_live_notional_usdc": 25,
        "max_concurrent_positions": 1,
        "expected_trades_per_month": round(float(summary["avg_trades_per_month"]), 2),
        "minimum_validation_period_days": 45,
        "kill_switch": "disable if 5 closed trades net <= -2.5%, any single trade <= -1.2%, spread > 8bps, missing bars > 2, or execution slippage > 12bps",
        "monitor_fields": "signal_ts, selected_dow_hour, train_mean_long_bps, entry_ack_ts, entry_price, exit_ack_ts, exit_price, realized_slippage_bps, fees_bps, net_ret, veto_state",
        "failure_condition": "after >=8 trades or 45d, stop if realized mean net bps <= 0 or live-vs-backtest slippage gap > 8bps",
    }
    lines = [f"{k}: {yaml_scalar(v)}" for k, v in cfg.items()]
    CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_report(
    generated_at: str,
    bar_summary: dict,
    ablation: pd.DataFrame,
    yearly: pd.DataFrame,
    plateau: pd.DataFrame,
    baseline_pass: bool,
) -> str:
    def md_table(df: pd.DataFrame, cols: list[str], n: int | None = None) -> str:
        if df.empty:
            return "_empty_"
        d = df[cols].head(n) if n else df[cols]
        headers = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        rows = []
        for _, row in d.iterrows():
            vals = []
            for col in cols:
                value = row[col]
                if isinstance(value, (float, np.floating)):
                    vals.append(f"{float(value):.4f}")
                else:
                    vals.append(str(value))
            rows.append("| " + " | ".join(vals) + " |")
        return "\n".join([headers, sep, *rows])

    verdict = "PASS -> tiny-live candidate emitted" if baseline_pass else "FAIL -> stop this family; no gate/veto rescue"
    return f"""# First-money baseline sprint: BTC UTC weak-cell short

Generated: {generated_at}

## Family choice
Chosen family: single-asset BTCUSDT UTC weekday-hour weak-cell short. This is not selected from the rank winner list; prior rank/clock work is treated as cautionary evidence that broad fixed UTC sleeves can fail. The family is retained only because it is simple, explainable, and fully schedulable before order time.

## Module split
- universe: `{SYMBOL}` only, eligible after `{ONBOARD_UTC}`; no future return, future volume, current active-list, or hindsight hot-coin selection.
- baseline: each UTC month, use only the trailing `{BASELINE_TRAIN_DAYS}` calendar days to find the weakest `(weekday, hour)` cell by future `{BASELINE_HOLD_BARS}`-bar long return; next month short the weakest cell.
- entry: scheduled bar-open entry for the selected cell.
- exit: fixed time stop after `{BASELINE_HOLD_BARS}` 15m bars.
- cost: `{BASELINE_COST_BPS}` bps round trip for baseline, `{EXEC_COST_BPS}` bps plus 1-bar delay in execution-realistic.
- veto: optional skip when prior 24h absolute BTC move is above trailing `{VETO_LOOKBACK_DAYS}`d mean + `{VETO_SIGMA}` std.
- gate: optional require trailing cell edge to exceed assumed cost.
- sizing: fixed 1x research unit; tiny-live config caps notional separately.
- execution: no-overlap, bar-open accounting from cached Binance UM klines; execution-realistic adds 1-bar latency and higher cost.

## Data
- source: local Binance USD-M 15m raw zip cache
- first bar: `{bar_summary["first_bar_utc"]}`
- last bar: `{bar_summary["last_bar_utc"]}`
- bars: `{bar_summary["bars"]}`

## Ablation
{md_table(ablation, ["variant", "trades", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct", "positive_year_ratio_pct", "avg_trades_per_month"])}

## Walk-forward yearly check
{md_table(yearly, ["variant", "year", "trades", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"])}

## Parameter plateau
Top grid rows are shown only to verify a plateau, not to choose a single best point. Frozen baseline remains `train={BASELINE_TRAIN_DAYS}d / hold={BASELINE_HOLD_BARS} bars / bottom_k={BASELINE_BOTTOM_K}`.

{md_table(plateau, ["train_days", "hold_bars", "bottom_k", "trades", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "positive_year_ratio_pct"], 12)}

## Verdict
{verdict}

Baseline pass rule: baseline-only must have positive post-cost mean bps and cumulative return, max drawdown better than -60%, at least 50% positive years, and at least 60 trades. Gate/veto are not allowed to rescue a failed baseline.

## Artifacts
- `reports/artifacts/rank32c_baseline_sprint/summary.json`
- `reports/artifacts/rank32c_baseline_sprint/ablation_summary.csv`
- `reports/artifacts/rank32c_baseline_sprint/walk_forward_yearly.csv`
- `reports/artifacts/rank32c_baseline_sprint/parameter_plateau.csv`
- `reports/artifacts/rank32c_baseline_sprint/trades.csv`
- `reports/artifacts/rank32c_baseline_sprint/monthly_selections.csv`
- `{CONFIG_PATH.relative_to(ROOT) if baseline_pass else "no tiny-live config emitted"}`
"""


def main() -> int:
    ensure_dirs()
    bars = load_symbol_bars(SYMBOL)
    bar_summary = {
        "symbol": SYMBOL,
        "first_bar_utc": to_iso(bars.index.min()),
        "last_bar_utc": to_iso(bars.index.max()),
        "bars": int(len(bars)),
        "source_dir": str(RAW_15M_DIR.relative_to(ROOT)),
    }

    baseline_spec = RunSpec("baseline_only")
    baseline_trades, baseline_selections = run_strategy(bars, baseline_spec)
    baseline_row = summarize_variant(baseline_trades, baseline_spec)
    baseline_pass = bool(
        baseline_row["trades"] >= 60
        and baseline_row["net_mean_bps"] > 0
        and baseline_row["net_cum_pct"] > 0
        and baseline_row["max_drawdown_pct"] > -60
        and baseline_row["positive_year_ratio_pct"] >= 50
    )

    if not baseline_pass:
        generated_at = to_iso(pd.Timestamp.now(tz="UTC"))
        ablation = pd.DataFrame([baseline_row])
        yearly = yearly_metrics(baseline_trades)
        plateau = pd.DataFrame()
        summary = {
            "generated_at_utc": generated_at,
            "strategy_family": "BTC UTC weekday-hour weak-cell short",
            "baseline_pass": False,
            "stop_reason": "baseline_only failed post-cost positive expectation checks; gate/veto/execution variants intentionally not run",
            "bar_summary": bar_summary,
            "baseline_pass_rule": {
                "min_trades": 60,
                "net_mean_bps_gt": 0,
                "net_cum_pct_gt": 0,
                "max_drawdown_pct_gt": -60,
                "positive_year_ratio_pct_gte": 50,
            },
            "ablation": [baseline_row],
            "artifacts": {
                "ablation_summary_csv": str((ART_DIR / "ablation_summary.csv").relative_to(ROOT)),
                "walk_forward_yearly_csv": str((ART_DIR / "walk_forward_yearly.csv").relative_to(ROOT)),
                "trades_csv": str((ART_DIR / "trades.csv").relative_to(ROOT)),
                "monthly_selections_csv": str((ART_DIR / "monthly_selections.csv").relative_to(ROOT)),
                "report_md": str(REPORT_PATH.relative_to(ROOT)),
                "tiny_live_config": "",
            },
        }
        ablation.to_csv(ART_DIR / "ablation_summary.csv", index=False)
        yearly.to_csv(ART_DIR / "walk_forward_yearly.csv", index=False)
        pd.DataFrame().to_csv(ART_DIR / "parameter_plateau.csv", index=False)
        baseline_trades.to_csv(ART_DIR / "trades.csv", index=False)
        baseline_selections.to_csv(ART_DIR / "monthly_selections.csv", index=False)
        (ART_DIR / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_tiny_live_config(baseline_row, False)
        REPORT_PATH.write_text(render_report(generated_at, bar_summary, ablation, yearly, plateau, False), encoding="utf-8")
        print("[stop] rank32c baseline sprint: baseline_only failed; no gate/veto rescue")
        print(f"[ok] report={REPORT_PATH.relative_to(ROOT)}")
        return 0

    specs = [
        baseline_spec,
        RunSpec("baseline_plus_veto", use_veto=True),
        RunSpec("baseline_plus_gate", use_gate=True),
        RunSpec("baseline_plus_veto_plus_gate", use_veto=True, use_gate=True),
        RunSpec("execution_realistic", use_veto=True, use_gate=True, cost_bps=EXEC_COST_BPS, entry_delay_bars=1),
    ]

    all_trades = []
    all_selections = []
    summary_rows = []
    for spec in specs:
        trades, selections = run_strategy(bars, spec)
        all_trades.append(trades)
        all_selections.append(selections)
        summary_rows.append(summarize_variant(trades, spec))

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    selections_df = pd.concat(all_selections, ignore_index=True) if all_selections else pd.DataFrame()
    ablation = pd.DataFrame(summary_rows)
    yearly = yearly_metrics(trades_df)
    plateau = plateau_grid(bars)

    baseline = baseline_row

    generated_at = to_iso(pd.Timestamp.now(tz="UTC"))
    summary = {
        "generated_at_utc": generated_at,
        "strategy_family": "BTC UTC weekday-hour weak-cell short",
        "baseline_pass": baseline_pass,
        "bar_summary": bar_summary,
        "baseline_pass_rule": {
            "min_trades": 60,
            "net_mean_bps_gt": 0,
            "net_cum_pct_gt": 0,
            "max_drawdown_pct_gt": -60,
            "positive_year_ratio_pct_gte": 50,
        },
        "ablation": summary_rows,
        "plateau_positive_share": float((plateau["net_mean_bps"] > 0).mean() * 100.0),
        "artifacts": {
            "ablation_summary_csv": str((ART_DIR / "ablation_summary.csv").relative_to(ROOT)),
            "walk_forward_yearly_csv": str((ART_DIR / "walk_forward_yearly.csv").relative_to(ROOT)),
            "parameter_plateau_csv": str((ART_DIR / "parameter_plateau.csv").relative_to(ROOT)),
            "trades_csv": str((ART_DIR / "trades.csv").relative_to(ROOT)),
            "monthly_selections_csv": str((ART_DIR / "monthly_selections.csv").relative_to(ROOT)),
            "report_md": str(REPORT_PATH.relative_to(ROOT)),
            "tiny_live_config": str(CONFIG_PATH.relative_to(ROOT)) if baseline_pass else "",
        },
    }

    ablation.to_csv(ART_DIR / "ablation_summary.csv", index=False)
    yearly.to_csv(ART_DIR / "walk_forward_yearly.csv", index=False)
    plateau.to_csv(ART_DIR / "parameter_plateau.csv", index=False)
    trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    selections_df.to_csv(ART_DIR / "monthly_selections.csv", index=False)
    (ART_DIR / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_tiny_live_config(baseline, baseline_pass)
    REPORT_PATH.write_text(render_report(generated_at, bar_summary, ablation, yearly, plateau, baseline_pass), encoding="utf-8")

    print(f"[ok] rank32c baseline sprint generated; baseline_pass={baseline_pass}")
    print(f"[ok] report={REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
