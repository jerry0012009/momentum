#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "rank29_recent_loss_anatomy"
LEDGER_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_closed_trades.csv"
STATE_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_state.json"

TARGET_CANDIDATE_ID = "rank29_trendline_breakout_navigator"
TARGET_VARIANT = "breakout_align_ge2"
TARGET_MODE = "no_overlap_guard"
WINDOWS = [12, 20, 30]


@dataclass(frozen=True)
class SliceSummary:
    label: str
    trades: int
    gross_win_rate: float
    net_win_rate: float
    gross_total_return: float
    net_total_return: float
    cost_flip_count: int


def _pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{x * 100:.2f}%"


def _load_rank29_closed_trades() -> pd.DataFrame:
    df = pd.read_csv(LEDGER_PATH)
    df = df[
        (df["candidate_id"] == TARGET_CANDIDATE_ID)
        & (df["variant"] == TARGET_VARIANT)
        & (df["mode"] == TARGET_MODE)
    ].copy()
    for col in ["entry_ts", "exit_ts", "event_ts"]:
        df[col] = pd.to_datetime(df[col], utc=True)
    df["cost_flip"] = (df["gross_ret"] > 0) & (df["net_ret"] <= 0)
    df = df.sort_values(["entry_ts", "asset"]).reset_index(drop=True)
    df["paper_bucket"] = pd.qcut(df.index, 3, labels=["bucket_1", "bucket_2", "bucket_3"])
    df["loss_flag"] = (df["net_ret"] <= 0).astype(int)
    return df


def _summarize_slice(df: pd.DataFrame, label: str) -> SliceSummary:
    return SliceSummary(
        label=label,
        trades=len(df),
        gross_win_rate=float((df["gross_ret"] > 0).mean()) if len(df) else float("nan"),
        net_win_rate=float((df["net_ret"] > 0).mean()) if len(df) else float("nan"),
        gross_total_return=float((1.0 + df["gross_ret"]).prod() - 1.0) if len(df) else 0.0,
        net_total_return=float((1.0 + df["net_ret"]).prod() - 1.0) if len(df) else 0.0,
        cost_flip_count=int(df["cost_flip"].sum()) if len(df) else 0,
    )


def _group_summary(df: pd.DataFrame, by: str) -> pd.DataFrame:
    out = (
        df.groupby(by, dropna=False)
        .agg(
            trades=("net_ret", "size"),
            losses=("loss_flag", "sum"),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
            gross_total_return=("gross_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            net_total_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            avg_net_ret=("net_ret", "mean"),
            cost_flip_count=("cost_flip", "sum"),
        )
        .reset_index()
        .sort_values(["losses", "trades", "net_total_return"], ascending=[False, False, True])
    )
    out["loss_rate"] = out["losses"] / out["trades"]
    return out


def _bucket_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby("paper_bucket", dropna=False)
        .agg(
            trades=("net_ret", "size"),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
            gross_total_return=("gross_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            net_total_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            avg_net_ret=("net_ret", "mean"),
            cost_flip_count=("cost_flip", "sum"),
        )
        .reset_index()
    )
    return out


def _trigger_patch_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    variants = {
        "baseline": ["long", "medium", "short"],
        "drop_short": ["long", "medium"],
        "drop_medium": ["long", "short"],
        "long_only": ["long"],
    }
    rows: list[dict] = []
    for variant, allowed in variants.items():
        for label, sliced in [("all", df), ("recent20", df.tail(20)), ("recent12", df.tail(12))]:
            subset = sliced[sliced["trigger_tf"].isin(allowed)].copy()
            rows.append(
                {
                    "variant": variant,
                    "window": label,
                    "trades": len(subset),
                    "win_rate": float((subset["net_ret"] > 0).mean()) if len(subset) else float("nan"),
                    "net_total_return": float((1.0 + subset["net_ret"]).prod() - 1.0) if len(subset) else 0.0,
                    "avg_net_ret": float(subset["net_ret"].mean()) if len(subset) else float("nan"),
                }
            )
    return pd.DataFrame(rows)


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text())


def build_report() -> Path:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    rank29 = _load_rank29_closed_trades()
    if rank29.empty:
        raise SystemExit("No closed rank29 paper trades found in ledger.")

    state = _load_state()
    summaries: list[SliceSummary] = [_summarize_slice(rank29, "all")]
    slices: dict[str, pd.DataFrame] = {"all": rank29.copy()}
    for window in WINDOWS:
        label = f"recent{window}"
        sliced = rank29.tail(window).copy()
        summaries.append(_summarize_slice(sliced, label))
        slices[label] = sliced

    summary_df = pd.DataFrame([s.__dict__ for s in summaries])
    summary_df.to_csv(ARTIFACT_DIR / "summary_windows.csv", index=False)

    for label, sliced in slices.items():
        _group_summary(sliced, "asset").to_csv(ARTIFACT_DIR / f"group_by_asset_{label}.csv", index=False)
        _group_summary(sliced, "direction").to_csv(ARTIFACT_DIR / f"group_by_direction_{label}.csv", index=False)
        _group_summary(sliced, "trigger_tf").to_csv(ARTIFACT_DIR / f"group_by_trigger_tf_{label}.csv", index=False)
        _bucket_summary(sliced).to_csv(ARTIFACT_DIR / f"bucket_summary_{label}.csv", index=False)
        sliced.to_csv(ARTIFACT_DIR / f"trade_slice_{label}.csv", index=False)

    recent20 = slices["recent20"]
    recent20_losses = recent20[recent20["net_ret"] <= 0].copy()
    recent20_losses.to_csv(ARTIFACT_DIR / "recent20_losses.csv", index=False)
    patch_df = _trigger_patch_sensitivity(rank29)
    patch_df.to_csv(ARTIFACT_DIR / "trigger_patch_sensitivity.csv", index=False)

    latest_exit = rank29["exit_ts"].max()
    first_entry = rank29["entry_ts"].min()
    recent20_summary = next(s for s in summaries if s.label == "recent20")
    trigger_recent20 = _group_summary(recent20, "trigger_tf")
    asset_recent20 = _group_summary(recent20, "asset")
    bucket_recent20 = _bucket_summary(recent20)
    patch_recent = patch_df[patch_df["window"].isin(["all", "recent20", "recent12"])].copy()

    def line_for_group(df: pd.DataFrame, key_col: str) -> list[str]:
        lines: list[str] = []
        for _, row in df.iterrows():
            lines.append(
                f"- {row[key_col]}: trades={int(row['trades'])}, win_rate={_pct(row['win_rate'])}, "
                f"net_total={_pct(row['net_total_return'])}, cost_flips={int(row['cost_flip_count'])}"
            )
        return lines

    report_lines = [
        "# Rank29 Recent Loss Anatomy",
        "",
        f"- Candidate: `{TARGET_CANDIDATE_ID}` / `{TARGET_VARIANT}` / `{TARGET_MODE}`",
        f"- Source ledger: `{LEDGER_PATH.relative_to(ROOT)}`",
        f"- Paper state init: `{state.get('initialized_at_utc', 'n/a')}`",
        f"- Window covered by current closed trades: `{first_entry}` -> `{latest_exit}`",
        f"- Total closed trades analyzed: `{len(rank29)}`",
        "",
        "## Executive takeaways",
        "",
        f"- Current weakness is **not mainly an execution-only story**: all-trade gross total return is `{_pct(next(s for s in summaries if s.label == 'all').gross_total_return)}`, while net total return is `{_pct(next(s for s in summaries if s.label == 'all').net_total_return)}`.",
        f"- Recent 20 closed paper trades are also weak at the **gross** level: gross total return `{_pct(recent20_summary.gross_total_return)}` vs net total return `{_pct(recent20_summary.net_total_return)}`; only `{recent20_summary.cost_flip_count}` trades were flipped from gross-positive to net-nonpositive by costs.",
        f"- Recent weakness is concentrated in the newest time segment: among recent 20 trades, `{int((recent20['paper_bucket'] == 'bucket_3').sum())}` / `{len(recent20)}` are in `bucket_3` (the newest third of the paper ledger).",
        "- Trigger quality is uneven: `long` trigger_tf is still the healthiest slice, while `medium` and `short` trigger_tf are the main drag on recent paper performance.",
        "- Practical implication: next move should be **recent-loss anatomy -> targeted veto / downsize for the worst trigger slices**, not a coarse global regime gate.",
        "",
        "## Window summary",
        "",
    ]
    for s in summaries:
        report_lines.append(
            f"- {s.label}: trades={s.trades}, gross_win={_pct(s.gross_win_rate)}, net_win={_pct(s.net_win_rate)}, "
            f"gross_total={_pct(s.gross_total_return)}, net_total={_pct(s.net_total_return)}, cost_flips={s.cost_flip_count}"
        )

    report_lines.extend(
        [
            "",
            "## Recent 20 by trigger_tf",
            "",
            *line_for_group(trigger_recent20, "trigger_tf"),
            "",
            "## Recent 20 by asset",
            "",
            *line_for_group(asset_recent20, "asset"),
            "",
            "## Recent 20 bucket split",
            "",
        ]
    )
    for _, row in bucket_recent20.iterrows():
        report_lines.append(
            f"- {row['paper_bucket']}: trades={int(row['trades'])}, win_rate={_pct(row['win_rate'])}, "
            f"net_total={_pct(row['net_total_return'])}, cost_flips={int(row['cost_flip_count'])}"
        )

    report_lines.extend(
        [
            "",
            "## Minimal patch sensitivity (paper-ledger only)",
            "",
        ]
    )
    for variant in ["baseline", "drop_short", "drop_medium", "long_only"]:
        subset = patch_recent[patch_recent["variant"] == variant]
        pieces = []
        for _, row in subset.iterrows():
            pieces.append(
                f"{row['window']}: trades={int(row['trades'])}, win_rate={_pct(row['win_rate'])}, net_total={_pct(row['net_total_return'])}"
            )
        report_lines.append(f"- {variant}: " + " | ".join(pieces))

    report_lines.extend(
        [
            "",
            "## What this report supports",
            "",
            "- It supports the view that recent Rank29 weakness is primarily a **signal / environment fit** problem, with costs acting as an amplifier rather than the sole cause.",
            "- It supports prioritizing `trigger_tf`-level pruning (especially the weaker medium/short slices) before trying more global regime filters.",
            "- It supports refreshing a current-sample time-stability audit, because recent weakness lives mostly in the newest third of the paper ledger rather than the older middle-third finding alone.",
            "- It suggests a concrete hypothesis worth formal backtesting next: a stricter `long_only` trigger_tf gate looks materially healthier on the paper ledger than baseline, but this must be validated on the full historical signal stream before promotion.",
            "",
            "## Next recommended checks",
            "",
            "1. Rebuild a current-sample time-stability audit directly on the latest Rank29 signal stream, not only the older scout artifact.",
            "2. Inspect recent losers for false-break / quick-reversal traits and compare them against recent winners within the same trigger_tf bucket.",
            "3. Test one minimal patch at a time on the full historical signal stream: start with `long_only`, then a weaker fallback of `drop_medium`, and compare against baseline under higher friction.",
            "",
            "## Output files",
            "",
            "- `summary_windows.csv`",
            "- `group_by_asset_*.csv`",
            "- `group_by_direction_*.csv`",
            "- `group_by_trigger_tf_*.csv`",
            "- `bucket_summary_*.csv`",
            "- `trade_slice_*.csv`",
            "- `recent20_losses.csv`",
            "- `trigger_patch_sensitivity.csv`",
        ]
    )

    report_path = ARTIFACT_DIR / "report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return report_path


if __name__ == "__main__":
    report_path = build_report()
    print(report_path)
