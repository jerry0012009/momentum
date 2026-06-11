from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


STRATEGY_ID = "rank32c_btc_utc_weak_cell_v1"
SYMBOL = "BTCUSDT"
ONBOARD_UTC = "2019-09-25T08:00:00Z"
BAR_MINUTES = 15
TRAIN_DAYS = 60
HOLD_BARS = 16
BOTTOM_K = 1
ROUND_TRIP_COST_BPS = 8.0
EXECUTION_REALISTIC_COST_BPS = 12.0
EXECUTION_REALISTIC_ENTRY_DELAY_BARS = 1
VETO_LOOKBACK_DAYS = 180
VETO_SIGMA = 2.0
GATE_EDGE_MULT = 1.0
TINY_LIVE_NOTIONAL_USDC = 100.0
MAX_SINGLE_TRADE_LOSS_PCT = 1.2


@dataclass(frozen=True)
class StrategySpec:
    strategy_id: str = STRATEGY_ID
    symbol: str = SYMBOL
    train_days: int = TRAIN_DAYS
    hold_bars: int = HOLD_BARS
    bottom_k: int = BOTTOM_K
    round_trip_cost_bps: float = ROUND_TRIP_COST_BPS
    use_veto: bool = True
    use_gate: bool = True
    entry_delay_bars: int = 0


@dataclass(frozen=True)
class SelectedCell:
    month: str
    dow: int
    hour: int
    train_mean_long_bps: float
    train_events: int
    train_start_utc: str
    train_end_exclusive_utc: str


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


def load_cached_bars(raw_15m_dir: Path, symbol: str = SYMBOL) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for subdir in ["monthly", "daily"]:
        d = raw_15m_dir / subdir / symbol
        if not d.exists():
            continue
        for path in sorted(d.glob(f"{symbol}-15m-*.zip")):
            part = read_kline_zip(path)
            if not part.empty:
                parts.append(part)
    if not parts:
        raise FileNotFoundError(f"no cached 15m zip data under {raw_15m_dir}")
    out = pd.concat(parts, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
    out = out.set_index("timestamp")
    out = out[~out.index.duplicated(keep="last")]
    out = out.astype({"open": float, "close": float})
    return add_veto_state(out)


def add_veto_state(bars: pd.DataFrame) -> pd.DataFrame:
    out = bars.copy()
    prev24 = (out["open"].shift(1) / out["open"].shift(97) - 1.0).abs()
    roll = prev24.rolling(VETO_LOOKBACK_DAYS * 96, min_periods=30 * 96)
    threshold = roll.mean() + VETO_SIGMA * roll.std(ddof=0)
    out["veto_high_vol"] = (prev24 > threshold).fillna(False).astype(bool)
    return out


def build_event_frame(bars: pd.DataFrame, hold_bars: int = HOLD_BARS, entry_delay_bars: int = 0) -> pd.DataFrame:
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


def month_start(ts: pd.Timestamp) -> pd.Timestamp:
    ts = ts.tz_convert("UTC") if ts.tzinfo else ts.tz_localize("UTC")
    return pd.Timestamp(ts.year, ts.month, 1, tz="UTC")


def select_month_cell(bars: pd.DataFrame, target_month_start: pd.Timestamp, spec: StrategySpec = StrategySpec()) -> SelectedCell:
    target_month_start = month_start(target_month_start)
    train_start = target_month_start - pd.Timedelta(days=spec.train_days)
    ev = build_event_frame(bars, spec.hold_bars, spec.entry_delay_bars)
    train = ev[(ev.index >= train_start) & (ev.index < target_month_start)]
    min_n = max(3, spec.train_days // 14)
    stats = (
        train.groupby(["dow", "hour"])
        .agg(train_mean_long_ret=("long_ret", "mean"), train_events=("long_ret", "size"))
        .reset_index()
    )
    stats = stats[stats["train_events"] >= min_n].sort_values("train_mean_long_ret")
    if spec.use_gate:
        stats = stats[stats["train_mean_long_ret"] < -(spec.round_trip_cost_bps / 10000.0) * GATE_EDGE_MULT]
    stats = stats.head(spec.bottom_k)
    if stats.empty:
        raise ValueError(f"no selected cell for {to_iso(target_month_start)}")
    row = stats.iloc[0]
    return SelectedCell(
        month=target_month_start.strftime("%Y-%m"),
        dow=int(row["dow"]),
        hour=int(row["hour"]),
        train_mean_long_bps=float(row["train_mean_long_ret"] * 10000.0),
        train_events=int(row["train_events"]),
        train_start_utc=to_iso(train_start),
        train_end_exclusive_utc=to_iso(target_month_start),
    )


def next_entry_after(now: pd.Timestamp, cell: SelectedCell) -> pd.Timestamp:
    now = now.tz_convert("UTC") if now.tzinfo else now.tz_localize("UTC")
    cur = now.ceil("h")
    month_end = month_start(now) + pd.offsets.MonthBegin(1)
    while cur < month_end:
        if cur.dayofweek == cell.dow and cur.hour == cell.hour:
            return cur
        cur += pd.Timedelta(hours=1)
    raise ValueError(f"no remaining selected cell occurrence in {cell.month}")


def evaluate_entry_controls(bars: pd.DataFrame, entry_ts: pd.Timestamp, cell: SelectedCell, spec: StrategySpec = StrategySpec()) -> dict:
    entry_ts = entry_ts.tz_convert("UTC") if entry_ts.tzinfo else entry_ts.tz_localize("UTC")
    gate_pass = cell.train_mean_long_bps < -spec.round_trip_cost_bps * GATE_EDGE_MULT
    if entry_ts in bars.index:
        veto_high_vol = bool(bars.loc[entry_ts, "veto_high_vol"])
        veto_source = "exact_entry_bar"
    else:
        prior = bars.index[bars.index <= entry_ts]
        veto_high_vol = bool(bars.loc[prior[-1], "veto_high_vol"]) if len(prior) else True
        veto_source = "latest_prior_bar" if len(prior) else "missing_bar"
    return {
        "gate_pass": bool(gate_pass),
        "veto_high_vol": bool(veto_high_vol),
        "veto_source": veto_source,
        "allow_open": bool(gate_pass and not veto_high_vol),
    }


def build_order_plan(bars: pd.DataFrame, now: pd.Timestamp, spec: StrategySpec = StrategySpec()) -> dict:
    now = now.tz_convert("UTC") if now.tzinfo else now.tz_localize("UTC")
    target_month = month_start(now)
    required_last_train_bar = target_month - pd.Timedelta(minutes=BAR_MINUTES)
    last_bar = bars.index.max()
    if last_bar < required_last_train_bar:
        return {
            "strategy_id": spec.strategy_id,
            "symbol": spec.symbol,
            "generated_at_utc": to_iso(now),
            "decision_blocker": "stale_bar_cache_for_current_month_selection",
            "cache_last_bar_utc": to_iso(last_bar),
            "required_last_train_bar_utc": to_iso(required_last_train_bar),
            "selected_cell": None,
            "next_entry_ts": None,
            "exit_ts": None,
            "allow_open": False,
            "blocked_by": ["stale_bar_cache_for_current_month_selection"],
            "notional_usdc": TINY_LIVE_NOTIONAL_USDC,
            "max_single_trade_risk_pct": MAX_SINGLE_TRADE_LOSS_PCT,
            "kill_switch_state": "blocked",
        }
    cell = select_month_cell(bars, target_month, spec)
    try:
        entry_ts = next_entry_after(now, cell)
        exit_ts = entry_ts + pd.Timedelta(minutes=BAR_MINUTES * spec.hold_bars)
        controls = evaluate_entry_controls(bars, entry_ts, cell, spec)
        blocked_by = []
        if not controls["gate_pass"]:
            blocked_by.append("gate")
        if controls["veto_high_vol"]:
            blocked_by.append("veto")
    except ValueError as exc:
        entry_ts = None
        exit_ts = None
        controls = {"gate_pass": True, "veto_high_vol": False, "veto_source": "n/a", "allow_open": False}
        blocked_by = [str(exc)]
    return {
        "strategy_id": spec.strategy_id,
        "symbol": spec.symbol,
        "generated_at_utc": to_iso(now),
        "decision_blocker": None,
        "cache_last_bar_utc": to_iso(last_bar),
        "required_last_train_bar_utc": to_iso(required_last_train_bar),
        "selected_cell": cell.__dict__,
        "next_entry_ts": to_iso(entry_ts) if entry_ts is not None else None,
        "exit_ts": to_iso(exit_ts) if exit_ts is not None else None,
        "allow_open": bool(controls["allow_open"]),
        "blocked_by": blocked_by,
        "gate_pass": bool(controls["gate_pass"]),
        "veto_high_vol": bool(controls["veto_high_vol"]),
        "veto_source": controls["veto_source"],
        "side": "short",
        "hold_bars": spec.hold_bars,
        "no_overlap": True,
        "notional_usdc": TINY_LIVE_NOTIONAL_USDC,
        "max_single_trade_risk_pct": MAX_SINGLE_TRADE_LOSS_PCT,
        "kill_switch_state": "armed" if controls["allow_open"] else "blocked",
    }


def iter_month_starts(start: pd.Timestamp, end_exclusive: pd.Timestamp) -> list[pd.Timestamp]:
    cur = month_start(start)
    end_exclusive = month_start(end_exclusive)
    months = []
    while cur < end_exclusive:
        months.append(cur)
        cur = cur + pd.offsets.MonthBegin(1)
    return months


def run_replay(
    bars: pd.DataFrame,
    start_month: pd.Timestamp,
    end_month_exclusive: pd.Timestamp,
    spec: StrategySpec = StrategySpec(),
) -> pd.DataFrame:
    ev = build_event_frame(bars, spec.hold_bars, spec.entry_delay_bars)
    trades: list[dict] = []
    next_allowed_signal_ts = pd.Timestamp.min.tz_localize("UTC")
    for mstart in iter_month_starts(start_month, end_month_exclusive):
        try:
            cell = select_month_cell(bars, mstart, spec)
        except ValueError:
            continue
        mend = mstart + pd.offsets.MonthBegin(1)
        month_events = ev[
            (ev.index >= mstart)
            & (ev.index < mend)
            & (ev["dow"] == cell.dow)
            & (ev["hour"] == cell.hour)
        ]
        for signal_ts, row in month_events.iterrows():
            if signal_ts < next_allowed_signal_ts:
                continue
            if spec.use_veto and bool(row["veto_high_vol"]):
                continue
            entry_ts = signal_ts + pd.Timedelta(minutes=BAR_MINUTES * spec.entry_delay_bars)
            exit_ts = signal_ts + pd.Timedelta(minutes=BAR_MINUTES * (spec.entry_delay_bars + spec.hold_bars))
            net_short_ret = -float(row["long_ret"]) - spec.round_trip_cost_bps / 10000.0
            trades.append(
                {
                    "month": cell.month,
                    "signal_ts": to_iso(signal_ts),
                    "entry_ts": to_iso(entry_ts),
                    "exit_ts": to_iso(exit_ts),
                    "symbol": spec.symbol,
                    "side": "short",
                    "dow": cell.dow,
                    "hour": cell.hour,
                    "train_mean_long_bps": cell.train_mean_long_bps,
                    "entry_open": float(row["entry_open"]),
                    "exit_open": float(row["exit_open"]),
                    "net_ret": net_short_ret,
                    "net_bps": net_short_ret * 10000.0,
                }
            )
            next_allowed_signal_ts = exit_ts
    return pd.DataFrame(trades)
