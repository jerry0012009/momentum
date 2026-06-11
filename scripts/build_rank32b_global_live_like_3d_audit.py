#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_live_like_backtest"
LIVE_ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_global_live"
OUT_JSON = ART_DIR / "standalone_3d_backtest_audit.json"
OUT_MD = ART_DIR / "standalone_3d_backtest_audit.md"
OUT_CSV = ART_DIR / "standalone_3d_backtest_vs_live.csv"
OUT_TIMELINE_JSON = ART_DIR / "standalone_3d_backtest_timeline.json"
PUBLIC_ART_DIR = Path("/var/www/momentum-report/artifacts/rank32b_shadow_global_live_like_backtest")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


stability_mod = load_module(ROOT / "scripts" / "build_rank32b_global_live_like_stability.py", "rank32b_standalone_3d_audit_stability")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def iso_ts(value: Any) -> str | None:
    try:
        ts = pd.to_datetime(value, utc=True)
    except Exception:
        return None
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def num(v: Any, digits: int = 2) -> str:
    try:
        return f"{float(v):.{digits}f}"
    except Exception:
        return "-"


def finite_or_none(value: Any) -> float | None:
    try:
        num_value = float(value)
    except Exception:
        return None
    if pd.isna(num_value) or num_value == float("inf") or num_value == float("-inf"):
        return None
    return num_value


def write_json_pair(path: Path, filename: str, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    path.write_text(text, encoding="utf-8")
    try:
        PUBLIC_ART_DIR.mkdir(parents=True, exist_ok=True)
        (PUBLIC_ART_DIR / filename).write_text(text, encoding="utf-8")
    except Exception:
        pass


def simplify_live_trade(row: dict[str, Any]) -> dict[str, Any]:
    pnl = finite_or_none(pd.to_numeric(row.get("net_pnl"), errors="coerce"))
    qty = finite_or_none(pd.to_numeric(row.get("qty"), errors="coerce"))
    entry_price = finite_or_none(pd.to_numeric(row.get("entry_price"), errors="coerce"))
    exit_price = finite_or_none(pd.to_numeric(row.get("exit_price"), errors="coerce"))
    return {
        "signal_id": str(row.get("signal_id") or ""),
        "symbol": str(row.get("symbol") or "").upper(),
        "side": str(row.get("side") or "").lower(),
        "signal_bar_start": iso_ts(row.get("signal_timestamp")),
        "plot_time": iso_ts(row.get("signal_confirmed_at")) or iso_ts(row.get("entry_time")) or iso_ts(row.get("exit_time")),
        "entry_time": iso_ts(row.get("entry_time")),
        "exit_time": iso_ts(row.get("exit_time")),
        "entry_price": entry_price,
        "exit_price": exit_price,
        "exit_reason": row.get("exit_reason"),
        "pnl_usdt": pnl,
        "qty": qty,
        "signal_confirmed_at": iso_ts(row.get("signal_confirmed_at")),
        "status": "closed",
    }


def simplify_live_position(row: dict[str, Any]) -> dict[str, Any]:
    entry_price = finite_or_none(pd.to_numeric(row.get("entry_price"), errors="coerce"))
    entry_notional = finite_or_none(pd.to_numeric(row.get("entry_notional"), errors="coerce"))
    return {
        "signal_id": str(row.get("signal_id") or ""),
        "symbol": str(row.get("symbol") or "").upper(),
        "side": str(row.get("side") or "").lower(),
        "signal_bar_start": iso_ts(row.get("signal_timestamp")),
        "plot_time": iso_ts(row.get("signal_confirmed_at")) or iso_ts(row.get("entry_time")),
        "entry_time": iso_ts(row.get("entry_time")),
        "entry_price": entry_price,
        "timeout_at": iso_ts(row.get("timeout_at")),
        "entry_notional": entry_notional,
        "signal_confirmed_at": iso_ts(row.get("signal_confirmed_at")),
        "status": "open",
    }


def simplify_bt_trade(row: dict[str, Any]) -> dict[str, Any]:
    pnl = finite_or_none(pd.to_numeric(row.get("bt_net_pnl_usdt"), errors="coerce"))
    notional = finite_or_none(pd.to_numeric(row.get("bt_notional_usdt"), errors="coerce"))
    entry_price = finite_or_none(pd.to_numeric(row.get("entry_price"), errors="coerce"))
    exit_price = finite_or_none(pd.to_numeric(row.get("exit_price"), errors="coerce"))
    return {
        "signal_id": str(row.get("signal_id") or ""),
        "symbol": str(row.get("symbol") or "").upper(),
        "side": str(row.get("side") or "").lower(),
        "signal_bar_start": iso_ts(row.get("signal_ts")),
        "plot_time": iso_ts(row.get("signal_confirmed_at")) or iso_ts(row.get("entry_ts")) or iso_ts(row.get("exit_ts")),
        "entry_time": iso_ts(row.get("entry_ts")),
        "exit_time": iso_ts(row.get("exit_ts")),
        "entry_price": entry_price,
        "exit_price": exit_price,
        "exit_reason": row.get("exit_reason"),
        "pnl_usdt": pnl,
        "notional_usdt": notional,
        "signal_confirmed_at": iso_ts(row.get("signal_confirmed_at")),
        "status": str(row.get("paper_trade_state") or "closed"),
    }


def main() -> int:
    ensure_dir(ART_DIR)

    live_rows = load_json(LIVE_ART_DIR / "live_recent_closed_trades.json", [])
    live_df = pd.DataFrame(live_rows if isinstance(live_rows, list) else [])
    live_state = load_json(LIVE_ART_DIR / "live_state.json", {}) or {}
    live_run = load_json(LIVE_ART_DIR / "live_last_run_summary.json", {}) or {}
    live_open_rows = live_state.get("live_positions", []) if isinstance(live_state, dict) else []
    live_open_df = pd.DataFrame(live_open_rows if isinstance(live_open_rows, list) else [])

    if live_df.empty:
        live_df = pd.DataFrame(columns=["signal_id", "symbol", "side", "entry_time", "exit_time", "live_net_pnl_usdt", "live_entry_price", "live_qty", "live_notional_usdt"])
    else:
        live_df["signal_id"] = live_df["signal_id"].astype(str)
        live_df["symbol"] = live_df["symbol"].astype(str)
        live_df["side"] = live_df["side"].astype(str)
        live_df["entry_time"] = pd.to_datetime(live_df.get("entry_time"), utc=True, errors="coerce")
        live_df["exit_time"] = pd.to_datetime(live_df.get("exit_time"), utc=True, errors="coerce")
        live_df["live_net_pnl_usdt"] = pd.to_numeric(live_df.get("net_pnl"), errors="coerce")
        live_df["live_entry_price"] = pd.to_numeric(live_df.get("entry_price"), errors="coerce")
        live_df["live_qty"] = pd.to_numeric(live_df.get("qty"), errors="coerce")
        live_df["live_notional_usdt"] = live_df["live_entry_price"].fillna(0.0) * live_df["live_qty"].fillna(0.0)

    if not live_open_df.empty:
        live_open_df["entry_time"] = pd.to_datetime(live_open_df.get("entry_time"), utc=True, errors="coerce")

    latest_live_exit = live_df["exit_time"].max() if "exit_time" in live_df.columns else pd.NaT
    latest_run_finished = pd.to_datetime(live_run.get("run_finished_at"), utc=True, errors="coerce")
    now_candidates = [ts for ts in (latest_live_exit, latest_run_finished) if not pd.isna(ts)]
    latest_live_exit = max(now_candidates) if now_candidates else pd.Timestamp.now(tz="UTC")

    cfg = stability_mod.bt.load_cfg(stability_mod.bt.CONFIG_PATH)
    bt_result = stability_mod.simulate_horizon_with_trades(cfg, horizon_days=3, now_ts=latest_live_exit)
    bt_df = pd.DataFrame(bt_result.get("paper_trades", []))
    if bt_df.empty:
        payload = {
            "status": "empty_backtest",
            "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
            "used_now_utc": latest_live_exit.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        write_json_pair(OUT_JSON, OUT_JSON.name, payload)
        OUT_MD.write_text("# standalone 3d backtest audit\n\n独立 3d backtest 未生成任何交易。\n", encoding="utf-8")
        OUT_CSV.write_text("scope,signal_id,symbol,side\n", encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 0

    bt_df["signal_id"] = bt_df["signal_id"].astype(str)
    bt_df["symbol"] = bt_df["symbol"].astype(str)
    bt_df["side"] = bt_df["side"].astype(str)
    bt_df["entry_ts"] = pd.to_datetime(bt_df.get("entry_ts"), utc=True, errors="coerce")
    bt_df["exit_ts"] = pd.to_datetime(bt_df.get("exit_ts"), utc=True, errors="coerce")
    bt_df["bt_entry_price"] = pd.to_numeric(bt_df.get("entry_price"), errors="coerce")
    bt_df["bt_net_ret"] = pd.to_numeric(bt_df.get("net_ret"), errors="coerce")
    bt_df["bt_effective_net_ret"] = pd.to_numeric(bt_df.get("paper_effective_net_ret"), errors="coerce")
    notional_by_symbol = bt_result.get("notional_by_symbol", {}) if isinstance(bt_result.get("notional_by_symbol"), dict) else {}
    default_notional = float(bt_result.get("default_notional_usdt", 100.0))
    bt_df["bt_notional_usdt"] = bt_df["symbol"].map(lambda s: float(notional_by_symbol.get(str(s).upper(), default_notional)))
    bt_df["bt_net_pnl_usdt"] = bt_df["bt_notional_usdt"] * bt_df["bt_effective_net_ret"].fillna(0.0)

    bt_closed_df = bt_df[bt_df["paper_trade_state"] == "closed"].copy()
    bt_open_df = bt_df[bt_df["paper_trade_state"] == "open"].copy()

    live_set = set(live_df["signal_id"])
    bt_closed_set = set(bt_closed_df["signal_id"])

    overlap = sorted(live_set & bt_closed_set)
    live_only = sorted(live_set - bt_closed_set)
    bt_only = sorted(bt_closed_set - live_set)

    if live_rows:
        merged = bt_closed_df.merge(
            live_df[
                [
                    "signal_id",
                    "symbol",
                    "side",
                    "signal_confirmed_at",
                    "entry_time",
                    "live_entry_price",
                    "live_qty",
                    "live_notional_usdt",
                    "exit_time",
                    "exit_reason",
                    "live_net_pnl_usdt",
                ]
            ],
            on="signal_id",
            how="outer",
            suffixes=("_bt", "_live"),
        )
    else:
        merged = bt_closed_df.copy()
        merged["symbol_live"] = pd.NA
        merged["side_live"] = pd.NA
        merged["signal_confirmed_at"] = pd.NA
        merged["entry_time"] = pd.NaT
        merged["live_entry_price"] = pd.NA
        merged["live_qty"] = pd.NA
        merged["live_notional_usdt"] = pd.NA
        merged["exit_time"] = pd.NaT
        merged["exit_reason"] = pd.NA
        merged["live_net_pnl_usdt"] = pd.NA
        merged["symbol_bt"] = merged["symbol"]
        merged["side_bt"] = merged["side"]

    def scope_of(row: pd.Series) -> str:
        sid = str(row.get("signal_id") or "")
        if sid in overlap:
            return "overlap"
        if sid in bt_only:
            return "bt_only"
        if sid in live_only:
            return "live_only"
        return "unknown"

    merged["scope"] = merged.apply(scope_of, axis=1)
    merged["symbol"] = merged["symbol_bt"].fillna(merged["symbol_live"])
    merged["side"] = merged["side_bt"].fillna(merged["side_live"])
    merged["entry_ts"] = pd.to_datetime(merged.get("entry_ts"), utc=True, errors="coerce")
    merged["entry_time"] = pd.to_datetime(merged.get("entry_time"), utc=True, errors="coerce")
    merged["exit_ts"] = pd.to_datetime(merged.get("exit_ts"), utc=True, errors="coerce")
    merged["exit_time"] = pd.to_datetime(merged.get("exit_time"), utc=True, errors="coerce")
    merged["entry_time_diff_seconds"] = (merged["entry_ts"] - merged["entry_time"]).dt.total_seconds()
    merged["entry_price_diff_bps"] = ((merged["bt_entry_price"] - merged["live_entry_price"]) / merged["live_entry_price"]) * 10000.0
    merged["net_pnl_diff_usdt"] = merged["bt_net_pnl_usdt"] - merged["live_net_pnl_usdt"]

    merged["signal_confirmed_at"] = merged.get("signal_confirmed_at_bt", merged.get("signal_confirmed_at"))
    merged["live_exit_reason"] = merged.get("exit_reason_live", merged.get("exit_reason"))
    merged["bt_exit_reason"] = merged.get("exit_reason_bt", merged.get("exit_reason"))

    merged = merged[
        [
            "scope",
            "signal_id",
            "symbol",
            "side",
            "signal_confirmed_at",
            "entry_ts",
            "entry_time",
            "entry_time_diff_seconds",
            "bt_entry_price",
            "live_entry_price",
            "entry_price_diff_bps",
            "bt_notional_usdt",
            "live_notional_usdt",
            "exit_ts",
            "exit_time",
            "bt_exit_reason",
            "live_exit_reason",
            "bt_net_pnl_usdt",
            "live_net_pnl_usdt",
            "net_pnl_diff_usdt",
        ]
    ].sort_values(["scope", "signal_confirmed_at", "signal_id"], na_position="last")
    merged.to_csv(OUT_CSV, index=False)

    timeline_payload = {
        "status": "ok",
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "used_now_utc": bt_result.get("used_now_utc"),
        "mode": "official_close_only",
        "goal": "validate live signals/pnl against standalone official-close 3d backtest",
        "live_closed": [simplify_live_trade(row) for row in live_rows] if isinstance(live_rows, list) else [],
        "live_open": [simplify_live_position(row) for row in live_open_rows] if isinstance(live_open_rows, list) else [],
        "standalone_backtest_closed": [simplify_bt_trade(row) for row in bt_closed_df.to_dict(orient="records")],
        "standalone_backtest_open": [simplify_bt_trade(row) for row in bt_open_df.to_dict(orient="records")],
    }

    payload = {
        "status": "ok",
        "generated_at_utc": timeline_payload["generated_at_utc"],
        "used_now_utc": bt_result.get("used_now_utc"),
        "live_window": {
            "closed_trades": int(len(live_df)),
            "symbols": sorted({str(s) for s in live_df["symbol"].dropna().tolist()}),
            "latest_exit_utc": iso_ts(latest_live_exit),
            "net_pnl_usdt": float(live_df["live_net_pnl_usdt"].fillna(0.0).sum()),
            "open_positions": int(len(live_open_df)),
        },
        "standalone_backtest_3d": {
            "closed_trades": int(len(bt_closed_df)),
            "open_positions": int(len(bt_open_df)),
            "symbols": sorted({str(s) for s in bt_closed_df["symbol"].dropna().tolist()}),
            "net_pnl_usdt": float(bt_closed_df["bt_net_pnl_usdt"].fillna(0.0).sum()),
            "signal_lookback_days": bt_result.get("signal_lookback_days"),
            "metrics": bt_result.get("metrics"),
            "paper_summary": bt_result.get("paper_summary"),
        },
        "set_compare": {
            "overlap_closed_signal_ids": int(len(overlap)),
            "bt_only_closed_signal_ids": int(len(bt_only)),
            "live_only_closed_signal_ids": int(len(live_only)),
            "overlap_signal_ids": overlap,
            "bt_only_symbol_counts": bt_closed_df[bt_closed_df["signal_id"].isin(bt_only)]["symbol"].value_counts().sort_index().to_dict(),
            "live_only_symbol_counts": live_df[live_df["signal_id"].isin(live_only)]["symbol"].value_counts().sort_index().to_dict(),
        },
    }
    write_json_pair(OUT_JSON, OUT_JSON.name, payload)
    write_json_pair(OUT_TIMELINE_JSON, OUT_TIMELINE_JSON.name, timeline_payload)

    lines = [
        "# rank32b standalone 3d global live-like backtest audit",
        "",
        f"- generated_at_utc: {payload['generated_at_utc']}",
        f"- used_now_utc: {payload['used_now_utc']}",
        f"- live closed trades: {payload['live_window']['closed_trades']} | live pnl: {num(payload['live_window']['net_pnl_usdt'])}U",
        f"- standalone backtest closed trades: {payload['standalone_backtest_3d']['closed_trades']} | open: {payload['standalone_backtest_3d']['open_positions']} | bt pnl: {num(payload['standalone_backtest_3d']['net_pnl_usdt'])}U",
        f"- overlap closed signal_ids: {payload['set_compare']['overlap_closed_signal_ids']}",
        f"- bt_only closed signal_ids: {payload['set_compare']['bt_only_closed_signal_ids']}",
        f"- live_only closed signal_ids: {payload['set_compare']['live_only_closed_signal_ids']}",
        "",
        "## overlap signal_ids",
        "",
    ]
    if overlap:
        for sid in overlap:
            lines.append(f"- {sid}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## bt_only symbol counts",
            "",
        ]
    )
    if payload["set_compare"]["bt_only_symbol_counts"]:
        for symbol, count in payload["set_compare"]["bt_only_symbol_counts"].items():
            lines.append(f"- {symbol}: {count}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## live_only symbol counts",
            "",
        ]
    )
    if payload["set_compare"]["live_only_symbol_counts"]:
        for symbol, count in payload["set_compare"]["live_only_symbol_counts"].items():
            lines.append(f"- {symbol}: {count}")
    else:
        lines.append("- none")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
