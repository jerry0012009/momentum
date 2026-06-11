#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank102_impulse_rebreak_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank102_impulse_rebreak_continuation_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank102_impulse_rebreak_continuation_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_psar_long_signal", "fib_retest_long_signal", "breakout_short_signal"]
VARIANTS = ["baseline", "impulse_rebreak_gate"]
COST_BPS = 6.0
HOLD_BARS = 8
FALSE_BARS = 4
WAIT_BARS = 5
CONFIRM_BARS = 6
EPS = 1e-12
CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 32px auto; padding: 0 18px 48px; line-height: 1.68; color: #111827; background: #f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
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


def bps(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 10000:.2f} bps"


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, bps_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    bps_cols = bps_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
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


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
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


def compute_psar(df: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> pd.Series:
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    n = len(df)
    psar = np.full(n, np.nan)
    bull = True
    af = step
    ep = high[0]
    psar[0] = low[0]
    if n > 1:
        bull = high[1] >= high[0]
        ep = high[1] if bull else low[1]
        psar[1] = min(low[0], low[1]) if bull else max(high[0], high[1])
    for i in range(2, n):
        prev_psar = psar[i - 1]
        if bull:
            cur = prev_psar + af * (ep - prev_psar)
            cur = min(cur, low[i - 1], low[i - 2])
            if low[i] < cur:
                bull = False
                cur = ep
                ep = low[i]
                af = step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(max_step, af + step)
        else:
            cur = prev_psar + af * (ep - prev_psar)
            cur = max(cur, high[i - 1], high[i - 2])
            if high[i] > cur:
                bull = True
                cur = ep
                ep = high[i]
                af = step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(max_step, af + step)
        psar[i] = cur
    return pd.Series(psar, index=df.index)


def load_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["atr14"] = atr(df)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["psar"] = compute_psar(df)
    df["rolling_high_20"] = df["high"].rolling(20, min_periods=20).max().shift(1)
    df["rolling_low_20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_500"] = df["swing_low_30"] + 0.500 * rng
    df["fib_618"] = df["swing_low_30"] + 0.618 * rng

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema21"])
        & (df["ema_slope"] > 0.0002)
        & (df["psar"] < df["close"])
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["close"] > df["ema9"])
        & (df["close"] > df["high"].shift(1) - 0.15 * df["atr14"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema21"])
        & (df["ema_slope"] > 0)
        & (df["low"] <= df["fib_618"] + 0.15 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["close"].shift(1) <= df["fib_500"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["breakout_short_signal"] = (
        df["rolling_low_20"].notna()
        & (df["ema9"] < df["ema21"])
        & (df["ema_slope"] < -0.0002)
        & (df["close"].shift(1) > df["rolling_low_20"].shift(1))
        & (df["close"] < df["rolling_low_20"] - 0.1 * df["atr14"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    return df


def compute_impulse_rebreak_gate(df: pd.DataFrame) -> pd.DataFrame:
    long_gate = np.zeros(len(df), dtype=bool)
    short_gate = np.zeros(len(df), dtype=bool)
    long_meta = [""] * len(df)
    short_meta = [""] * len(df)

    closes = df["close"].to_numpy(dtype=float)
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    breakout_high = df["rolling_high_20"].to_numpy(dtype=float)
    breakout_low = df["rolling_low_20"].to_numpy(dtype=float)
    atr14 = df["atr14"].to_numpy(dtype=float)

    for i in range(30, len(df)):
        if np.isnan(atr14[i]) or np.isnan(breakout_high[i]) or np.isnan(breakout_low[i]):
            continue

        # long: recent upside breakout -> retest -> close re-breaks pre-retest impulse high
        for break_idx in range(max(20, i - WAIT_BARS - CONFIRM_BARS), i):
            level = breakout_high[break_idx]
            if np.isnan(level):
                continue
            if closes[break_idx - 1] <= level and closes[break_idx] > level + 0.05 * atr14[break_idx]:
                max_retest_idx = min(i - 1, break_idx + WAIT_BARS)
                for retest_idx in range(break_idx + 1, max_retest_idx + 1):
                    if lows[retest_idx] <= level + 0.25 * atr14[retest_idx]:
                        impulse_high = np.nanmax(highs[break_idx : retest_idx])
                        if i <= retest_idx + CONFIRM_BARS and closes[i] > impulse_high + 0.02 * atr14[i]:
                            long_gate[i] = True
                            long_meta[i] = f"break={break_idx}|retest={retest_idx}|impulse={impulse_high:.4f}|level={level:.4f}"
                            break
                if long_gate[i]:
                    break

        # short: recent downside breakout -> retest -> close re-breaks pre-retest impulse low
        for break_idx in range(max(20, i - WAIT_BARS - CONFIRM_BARS), i):
            level = breakout_low[break_idx]
            if np.isnan(level):
                continue
            if closes[break_idx - 1] >= level and closes[break_idx] < level - 0.05 * atr14[break_idx]:
                max_retest_idx = min(i - 1, break_idx + WAIT_BARS)
                for retest_idx in range(break_idx + 1, max_retest_idx + 1):
                    if highs[retest_idx] >= level - 0.25 * atr14[retest_idx]:
                        impulse_low = np.nanmin(lows[break_idx : retest_idx])
                        if i <= retest_idx + CONFIRM_BARS and closes[i] < impulse_low - 0.02 * atr14[i]:
                            short_gate[i] = True
                            short_meta[i] = f"break={break_idx}|retest={retest_idx}|impulse={impulse_low:.4f}|level={level:.4f}"
                            break
                if short_gate[i]:
                    break

    out = df.copy()
    out["impulse_rebreak_gate_long"] = long_gate
    out["impulse_rebreak_gate_short"] = short_gate
    out["impulse_rebreak_long_meta"] = long_meta
    out["impulse_rebreak_short_meta"] = short_meta
    return out


def build_signal(df: pd.DataFrame, setup: str, variant: str) -> tuple[pd.Series, pd.Series]:
    base = df[setup].fillna(False)
    if variant == "baseline":
        return base, pd.Series(["baseline"] * len(df), index=df.index)
    if setup.endswith("long"):
        return base & df["impulse_rebreak_gate_long"].fillna(False), df["impulse_rebreak_long_meta"]
    return base & df["impulse_rebreak_gate_short"].fillna(False), df["impulse_rebreak_short_meta"]


def simulate(df: pd.DataFrame, asset: str, setup: str, variant: str) -> list[dict[str, object]]:
    side = "long" if setup.endswith("long") else "short"
    signal, meta = build_signal(df, setup, variant)
    idxs = np.flatnonzero(signal.to_numpy(dtype=bool))
    trades: list[dict[str, object]] = []
    last_exit = -1
    for i in idxs:
        if i <= last_exit or i + 1 >= len(df):
            continue
        entry_idx = i + 1
        exit_idx = min(len(df) - 1, entry_idx + HOLD_BARS)
        entry_price = float(df.iloc[entry_idx]["open"])
        exit_price = float(df.iloc[exit_idx]["close"])
        future4 = min(len(df) - 1, entry_idx + FALSE_BARS)
        close4 = float(df.iloc[future4]["close"])
        if side == "long":
            gross = exit_price / entry_price - 1.0
            false_follow = close4 / entry_price - 1.0 <= 0
        else:
            gross = entry_price / exit_price - 1.0
            false_follow = entry_price / close4 - 1.0 <= 0
        net = gross - 2.0 * COST_BPS / 10000.0
        trades.append(
            {
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "side": side,
                "signal_time": df.iloc[i]["timestamp"],
                "entry_time": df.iloc[entry_idx]["timestamp"],
                "exit_time": df.iloc[exit_idx]["timestamp"],
                "entry_price": entry_price,
                "exit_price": exit_price,
                "net_ret": net,
                "gross_ret": gross,
                "false_follow_4bars": bool(false_follow),
                "gate_meta": str(meta.iloc[i]),
            }
        )
        last_exit = exit_idx
    return trades


def summarize(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overall = (
        trades.groupby(["setup", "variant"], sort=False)
        .agg(
            trades=("net_ret", "size"),
            avg_net_ret=("net_ret", "mean"),
            median_net_ret=("net_ret", "median"),
            win_rate=("net_ret", lambda s: (s > 0).mean()),
            false_follow_4bars_rate=("false_follow_4bars", "mean"),
            total_return=("net_ret", lambda s: (1.0 + s).prod() - 1.0),
        )
        .reset_index()
    )
    asset = (
        trades.groupby(["setup", "variant", "asset"], sort=False)
        .agg(
            trades=("net_ret", "size"),
            avg_net_ret=("net_ret", "mean"),
            median_net_ret=("net_ret", "median"),
            win_rate=("net_ret", lambda s: (s > 0).mean()),
            false_follow_4bars_rate=("false_follow_4bars", "mean"),
            total_return=("net_ret", lambda s: (1.0 + s).prod() - 1.0),
        )
        .reset_index()
    )

    baseline_counts = overall.loc[overall["variant"] == "baseline", ["setup", "trades"]].rename(columns={"trades": "baseline_trades"})
    overall = overall.merge(baseline_counts, on="setup", how="left")
    overall["trade_count_retention"] = overall["trades"] / overall["baseline_trades"].replace(0, np.nan)

    positive_asset = (
        asset.assign(is_positive=asset["avg_net_ret"] > 0)
        .groupby(["setup", "variant"], sort=False)["is_positive"]
        .mean()
        .reset_index(name="positive_asset_ratio")
    )
    overall = overall.merge(positive_asset, on=["setup", "variant"], how="left")

    pivot = overall.pivot(index="setup", columns="variant", values=["avg_net_ret", "false_follow_4bars_rate", "trade_count_retention", "positive_asset_ratio", "trades"])
    pivot.columns = [f"{a}_{b}" for a, b in pivot.columns]
    verdict_input = pivot.reset_index()
    return overall, asset, verdict_input


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    all_trades: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        frame = compute_impulse_rebreak_gate(load_frame(asset, symbol))
        frame.to_csv(ART_DIR / f"{asset.replace('-', '_').lower()}_frame.csv", index=False)
        for setup in SETUPS:
            for variant in VARIANTS:
                all_trades.extend(simulate(frame, asset, setup, variant))

    trades = pd.DataFrame(all_trades)
    overall, asset, verdict_input = summarize(trades)

    gate_only = overall.loc[overall["variant"] == "impulse_rebreak_gate"].copy()
    gate_mean = gate_only["avg_net_ret"].mean()
    gate_positive = gate_only["positive_asset_ratio"].mean()
    gate_retention = gate_only["trade_count_retention"].mean()
    gate_false = gate_only["false_follow_4bars_rate"].mean()
    base_only = overall.loc[overall["variant"] == "baseline"].copy()
    base_mean = base_only["avg_net_ret"].mean()
    base_false = base_only["false_follow_4bars_rate"].mean()

    if gate_mean > 0 and gate_positive >= 2.0 / 3.0 and gate_retention >= 0.12:
        verdict = "promote to P2 / paper candidate"
        desk_readthrough = "shared continuation confirmation gate worth paper-candidate discussion"
        next_step = "只给 1 个 truly verdict-changing Light Stability Pack（优先时间稳定性）"
    elif gate_mean > base_mean and gate_retention >= 0.05:
        verdict = "keep_P1 / evidence pool"
        desk_readthrough = "shared continuation gate has signal-improving flavor, but not enough yet for paper candidate"
        next_step = "若下轮仍在 Scout Seat，只给 1 个 truly verdict-changing 最小检查（默认时间稳定性）"
    else:
        verdict = "park / evidence pool"
        desk_readthrough = "re-break confirmation reduces some false follow-through but remains too sparse / too weak for active Scout budget"
        next_step = "切 Rank 103 / confirmed extremum honest fib anchor 做 source intake"

    verdict_summary = pd.DataFrame([
        {
            "rank": 102,
            "candidate": "retest 后重破 impulse extreme continuation gate",
            "current_hard_verdict": verdict,
            "desk_readthrough": desk_readthrough,
            "next_step": next_step,
            "baseline_mean_avg_net_ret": base_mean,
            "gate_mean_avg_net_ret": gate_mean,
            "baseline_mean_false_follow_4bars_rate": base_false,
            "gate_mean_false_follow_4bars_rate": gate_false,
            "gate_mean_trade_count_retention": gate_retention,
            "gate_mean_positive_asset_ratio": gate_positive,
            "wait_bars": WAIT_BARS,
            "confirm_bars": CONFIRM_BARS,
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
    ])

    trades.to_csv(ART_DIR / "trade_log.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    asset.to_csv(ART_DIR / "asset_summary.csv", index=False)
    verdict_input.to_csv(ART_DIR / "verdict_input_summary.csv", index=False)
    verdict_summary.to_csv(ART_DIR / "verdict_summary.csv", index=False)

    overall_table = render_table(
        overall[["setup", "variant", "trades", "trade_count_retention", "avg_net_ret", "median_net_ret", "win_rate", "false_follow_4bars_rate", "positive_asset_ratio"]],
        percent_cols={"trade_count_retention", "win_rate", "false_follow_4bars_rate", "positive_asset_ratio"},
        bps_cols={"avg_net_ret", "median_net_ret"},
        digits_cols={"trades": 0},
    )
    asset_table = render_table(
        asset[["setup", "variant", "asset", "trades", "avg_net_ret", "win_rate", "false_follow_4bars_rate", "total_return"]],
        percent_cols={"win_rate", "false_follow_4bars_rate", "total_return"},
        bps_cols={"avg_net_ret"},
        digits_cols={"trades": 0},
    )

    factor_body = f"""
<h1>Rank 102 · retest 后重破 impulse extreme continuation gate · minimal clean replication</h1>
<p class='muted'>生成时间：{escape(verdict_summary.iloc[0]['generated_at_utc'])} · 数据复用 <code>reports/artifacts/scout_tau_band_breakout_15m/cache/</code> · BTC/ETH/SOL 120d 15m · next-bar open · no-overlap · {COST_BPS:.0f}bps/side</p>
<div class='card'>
  <p><strong>一句话结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <ul>
    <li><strong>baseline 平均每笔</strong>：{bps(base_mean)}；<strong>gate 平均每笔</strong>：{bps(gate_mean)}。</li>
    <li><strong>baseline 4-bar 假延续率</strong>：{pct(base_false)}；<strong>gate 4-bar 假延续率</strong>：{pct(gate_false)}。</li>
    <li><strong>gate 平均保留率</strong>：{pct(gate_retention)}；<strong>gate 平均正资产占比</strong>：{pct(gate_positive)}。</li>
    <li>clean replication 只测试一手最小 shared gate：先有 breakout，再在 {WAIT_BARS} 根内出现 retest，随后需在 {CONFIRM_BARS} 根确认窗内收盘价重破 retest 前 impulse extreme。</li>
  </ul>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {overall_table}
</div>
<div class='card'>
  <h2>Asset summary</h2>
  {asset_table}
</div>
<div class='card'>
  <h2>Desk readthrough</h2>
  <p>{escape(desk_readthrough)}</p>
  <p>下一步：<strong>{escape(next_step)}</strong></p>
  <p><a href='../../reading/repo_scout/rank102_impulse_rebreak_continuation_clean_replication.html'>阅读版说明</a> · <a href='../../reading/repo_scout/rank102_impulse_rebreak_continuation_source_intake.html'>source intake</a></p>
</div>
"""

    reading_body = f"""
<h1>Rank 102 · retest 后重破 impulse extreme continuation gate · clean replication write-up</h1>
<p class='muted'>这轮不追新 bar，不重拉新数据；只用 desk 现有 BTC/ETH/SOL 120d 15m cache，把 source-intake 的 continuation gate 真正压到 next-bar open / no-overlap 的最小复现口径。</p>
<div class='card'>
  <p><strong>主结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <p>更直白地说：这轮回答的是“回踩之后，要求快速重破前一段 impulse extreme，能不能比 baseline 更诚实地筛掉假延续”。</p>
  <ul>
    <li>baseline 平均每笔：<strong>{bps(base_mean)}</strong>；gate 平均每笔：<strong>{bps(gate_mean)}</strong>。</li>
    <li>baseline 假延续率：<strong>{pct(base_false)}</strong>；gate 假延续率：<strong>{pct(gate_false)}</strong>。</li>
    <li>但 gate 的平均保留率只有 <strong>{pct(gate_retention)}</strong>；它是否值得继续占 Scout 预算，关键就看“少亏/少假延续”有没有大到足以抵消切样本”。</li>
  </ul>
</div>
<div class='card'>
  <h2>实现口径</h2>
  <ul>
    <li><strong>Long</strong>：近 20-bar breakout 上破后，{WAIT_BARS} 根内出现 retest；若 retest 后 {CONFIRM_BARS} 根内收盘价重破 retest 前的 impulse high，gate 才放行。</li>
    <li><strong>Short</strong>：近 20-bar breakout 下破后，{WAIT_BARS} 根内出现 retest；若 retest 后 {CONFIRM_BARS} 根内收盘价重破 retest 前的 impulse low，gate 才放行。</li>
    <li>统一：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</li>
  </ul>
  <p><a href='../../factors/scout_rank102_impulse_rebreak_continuation_15m/report.html'>查看 factor 页面</a></p>
</div>
"""

    write_html(SITE_DIR / "report.html", "Rank 102 impulse re-break continuation gate", factor_body)
    write_html(READING_PATH, "Rank 102 impulse re-break continuation clean replication", reading_body)

    print(f"[ok] wrote {ART_DIR / 'verdict_summary.csv'}")
    print(f"[ok] wrote {SITE_DIR / 'report.html'}")
    print(f"[ok] wrote {READING_PATH}")


if __name__ == "__main__":
    main()
