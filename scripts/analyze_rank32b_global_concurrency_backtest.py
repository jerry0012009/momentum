#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.execution.canary32b.signal_adapter import Rank32BPerpSignalAdapter  # noqa: E402

CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
OUT_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_backtest_compare"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


phase6lib = load_module(ROOT / "scripts" / "run_rank32b_canary_phase6.py", "rank32b_backtest_phase6lib")
shadow_mod = load_module(ROOT / "scripts" / "run_rank32b_global_selector_shadow.py", "rank32b_backtest_shadow_mod")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_cfg(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_live_like_notional(cfg: dict[str, Any], asset_to_symbol: dict[str, str]) -> tuple[float, dict[str, float]]:
    phase6 = cfg.get("phase6", {}) if isinstance(cfg.get("phase6"), dict) else {}
    global_live = phase6.get("global_live", {}) if isinstance(phase6.get("global_live"), dict) else {}
    base_sizing = phase6.get("sizing", {}) if isinstance(phase6.get("sizing"), dict) else {}
    default_notional = float(global_live.get("desired_notional_usdt", base_sizing.get("desired_notional_usdt", 100.0)))
    by_symbol = {str(symbol).upper(): default_notional for symbol in asset_to_symbol.values()}
    overrides = global_live.get("desired_notional_usdt_by_symbol") if isinstance(global_live.get("desired_notional_usdt_by_symbol"), dict) else {}
    for key, value in overrides.items():
        try:
            num = float(value)
        except Exception:
            continue
        if math.isfinite(num) and num > 0:
            by_symbol[str(key).upper()] = num
    return default_notional, by_symbol


def normalize_selected_rows(signals: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sig in signals:
        row = sig.to_dict() if hasattr(sig, "to_dict") else dict(sig)
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        row["signal_confirmed_at"] = phase6lib.signal_confirmed_at(str(row.get("timestamp") or ""), metadata)
        rows.append(row)
    rows.sort(key=lambda row: (str(row.get("signal_confirmed_at") or row.get("timestamp") or ""), str(row.get("symbol") or "")))
    return rows


def trade_ts(row: dict[str, Any]) -> pd.Timestamp:
    for key in ("exit_ts", "mark_ts", "signal_confirmed_at", "signal_ts", "timestamp"):
        ts = shadow_mod.parse_ts(row.get(key))
        if ts is not None:
            return ts
    return pd.Timestamp.min.tz_localize("UTC")


def compute_metrics(trades: list[dict[str, Any]], *, default_notional: float, notional_by_symbol: dict[str, float]) -> dict[str, Any]:
    effective = [row for row in trades if row.get("paper_trade_state") in {"open", "closed"}]
    effective.sort(key=trade_ts)
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    usdt_pnl = 0.0
    closed_usdt_pnl = 0.0
    for row in effective:
        ret = float(row.get("paper_effective_net_ret") or 0.0)
        symbol = str(row.get("symbol") or "").upper()
        notional = float(notional_by_symbol.get(symbol, default_notional))
        usdt_pnl += notional * ret
        if row.get("paper_trade_state") == "closed":
            closed_usdt_pnl += notional * ret
        equity *= 1.0 + ret
        peak = max(peak, equity)
        max_dd = max(max_dd, 0.0 if peak <= 0 else (peak - equity) / peak)
    return {
        "usdt_pnl_live_like": usdt_pnl,
        "closed_usdt_pnl_live_like": closed_usdt_pnl,
        "max_drawdown": max_dd,
        "effective_trade_count": len(effective),
    }


def run_horizon(cfg: dict[str, Any], *, horizon_days: int, now_ts: pd.Timestamp) -> dict[str, Any]:
    shadow_cfg = shadow_mod.load_shadow_cfg(cfg)
    asset_to_symbol = shadow_cfg["asset_to_symbol"]
    signal_cfg = cfg.get("signal_adapter", {}) if isinstance(cfg.get("signal_adapter"), dict) else {}
    signal_lookback_days = int(signal_cfg.get("lookback_days", horizon_days))
    signal_fetch_days = int(horizon_days) + max(0, signal_lookback_days)
    adapter = Rank32BPerpSignalAdapter(
        asset_to_symbol=asset_to_symbol,
        days=signal_fetch_days,
        recent_hours=int(horizon_days * 24),
        variant=str(signal_cfg.get("variant", "ema_cross_plus_slope_floor")),
        refresh_bars=bool(signal_cfg.get("refresh_bars", True)),
        refresh_tail_days=(int(signal_cfg["refresh_tail_days"]) if signal_cfg.get("refresh_tail_days") is not None else None),
        preview_unclosed_15m=False,
        preview_fetch_limit=int(signal_cfg.get("preview_fetch_limit", 30)),
        entry_delay_minutes=int(signal_cfg.get("entry_delay_minutes", 0)),
        official_signal_ttl_minutes=None,
    )
    snapshot = adapter.load_recent_signals()
    selection_phase6 = {
        "selection": shadow_cfg.get("selection", {}),
        "smallcap": {"enabled": False, "symbols": []},
        "max_new_signals_per_run": 0,
    }
    selected_signals, skipped_weaker_signals = phase6lib.select_signals_for_execution(snapshot.signals, selection_phase6)
    selected_rows = normalize_selected_rows(selected_signals)
    default_notional, notional_by_symbol = load_live_like_notional(cfg, asset_to_symbol)

    scenarios: dict[str, Any] = {}
    for concurrency in (1, 3):
        scenario_shadow_cfg = deepcopy(shadow_cfg)
        paper_cfg = deepcopy(scenario_shadow_cfg.get("paper", {}))
        paper_cfg["max_concurrent_positions"] = concurrency
        if isinstance(paper_cfg.get("depth_v2"), dict):
            paper_cfg["depth_v2"]["enabled"] = False
        scenario_shadow_cfg["paper"] = paper_cfg
        trades, closed, open_positions, summary = shadow_mod.build_paper_trades(selected_rows, scenario_shadow_cfg, now_ts)
        metrics = compute_metrics(trades, default_notional=default_notional, notional_by_symbol=notional_by_symbol)
        scenarios[str(concurrency)] = {
            "concurrency": concurrency,
            "summary": summary,
            "metrics": metrics,
            "closed_trades": len(closed),
            "open_positions": len(open_positions),
        }

    return {
        "horizon_days": horizon_days,
        "latest_bar_utc": snapshot.latest_bar_utc,
        "latest_signal_utc": snapshot.latest_signal_utc,
        "latest_observed_signal_utc": snapshot.latest_observed_signal_utc,
        "signals_total": len(snapshot.signals),
        "selected_winners": len(selected_rows),
        "skipped_weaker_signals": len(skipped_weaker_signals),
        "signal_lookback_days": signal_lookback_days,
        "signal_fetch_days": signal_fetch_days,
        "live_like_notional_default": default_notional,
        "live_like_notional_by_symbol": notional_by_symbol,
        "scenarios": scenarios,
    }


def render_markdown(results: list[dict[str, Any]]) -> str:
    lines = [
        "# rank32b global shadow concurrency quick backtest",
        "",
        "口径：official_close strongest-only global 选股，历史 5m/15m bar 回测；并发比较用 paper max_concurrent_positions=1 vs 3；USDT PnL 用 live-like 100U/40U 仓位换算。",
        "",
    ]
    for item in results:
        s1 = item["scenarios"]["1"]
        s3 = item["scenarios"]["3"]
        lines.extend(
            [
                f"## Horizon: {item['horizon_days']} days",
                f"- signals_total: {item['signals_total']}",
                f"- selected_winners: {item['selected_winners']}",
                f"- skipped_weaker_signals: {item['skipped_weaker_signals']}",
                f"- conc=1 marked_return: {s1['summary'].get('paper_marked_total_return'):.4f} | mdd: {s1['metrics'].get('max_drawdown'):.4f} | live_like_pnl: {s1['metrics'].get('usdt_pnl_live_like'):.2f} | skipped_by_max_concurrent: {s1['summary'].get('paper_skipped_by_max_concurrent')}",
                f"- conc=3 marked_return: {s3['summary'].get('paper_marked_total_return'):.4f} | mdd: {s3['metrics'].get('max_drawdown'):.4f} | live_like_pnl: {s3['metrics'].get('usdt_pnl_live_like'):.2f} | skipped_by_max_concurrent: {s3['summary'].get('paper_skipped_by_max_concurrent')}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Quick historical backtest: rank32b global concurrency 1 vs 3")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--horizon-days", nargs="*", type=int, default=[365, 1095])
    args = ap.parse_args()

    cfg = load_cfg(Path(args.config))
    now_ts = pd.Timestamp.now(tz="UTC")
    ensure_dir(OUT_DIR)
    results = [run_horizon(cfg, horizon_days=int(days), now_ts=now_ts) for days in args.horizon_days]
    payload = {
        "generated_at_utc": now_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config_path": str(Path(args.config)),
        "results": results,
    }
    (OUT_DIR / "concurrency_comparison.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "concurrency_comparison.md").write_text(render_markdown(results), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
