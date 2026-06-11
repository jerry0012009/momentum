#!/usr/bin/env python3
from __future__ import annotations

"""Dedicated paper runner for Rank 342 / same-chain cross-DEX price-gap close.

Honest scope:
- pulls fresh DexScreener token-pairs snapshots for the approved low-gas same-chain lanes
- computes gross/net executable pocket under the frozen paper-launch friction spec
- writes runner-grade artifacts (ledger / status / state / html / summary)
- this is launch wiring for a narrowed paper lane, not a claim of raw fill replay / MEV-perfect execution
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank342_samechain_crossdex"
LEDGER_PATH = ART_DIR / "rank342_lane_snapshots.csv"
STATUS_PATH = ART_DIR / "rank342_status.csv"
STATE_PATH = ART_DIR / "rank342_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank342_last_run_summary.json"
CURRENT_SIGNAL_PATH = ART_DIR / "rank342_current_lane_frame.csv"
SPEC_PATH = ART_DIR / "rank342_frozen_launch_spec.json"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank342_samechain_crossdex.html"
SEED_EXIT_PATH = ROOT / "reports" / "artifacts" / "quant_digests" / "rank342_exit_decision_20260405_2300.json"

CANDIDATE_ID = "rank342_samechain_crossdex_pricegap_close"
CANDIDATE_RANK = 342
RUNNER_SERVICE = "momentum-rank342-paper-refresh.service"
RUNNER_TIMER = "momentum-rank342-paper-refresh.timer"
ROUND_TRIP_NON_GAS_BPS = 13.0
NOTIONALS = [5000, 10000, 25000]
CHAIN_GAS_USD = {"base": 0.2, "arbitrum": 0.5, "ethereum": 15.0}
USER_AGENT = "OpenClaw-Momentum-Rank342/1.0"

LANES = [
    {
        "chain": "base",
        "token_symbol": "WETH",
        "token_address": "0x4200000000000000000000000000000000000006",
        "base_symbol": "WETH",
        "quote_symbol": "USDC",
        "liquidity_floor_usd": 1_000_000,
        "launch_priority": 1,
    },
    {
        "chain": "base",
        "token_symbol": "cbBTC",
        "token_address": "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf",
        "base_symbol": "cbBTC",
        "quote_symbol": "WETH",
        "liquidity_floor_usd": 1_000_000,
        "launch_priority": 2,
    },
    {
        "chain": "arbitrum",
        "token_symbol": "WETH",
        "token_address": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
        "base_symbol": "WETH",
        "quote_symbol": "USDC",
        "liquidity_floor_usd": 250_000,
        "launch_priority": 3,
    },
    {
        "chain": "arbitrum",
        "token_symbol": "WBTC",
        "token_address": "0x2f2a2543b76a4166549f7aaB2e75Bef0aefc5b0f",
        "base_symbol": "WBTC",
        "quote_symbol": "WETH",
        "liquidity_floor_usd": 250_000,
        "launch_priority": 4,
    },
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def json_request(url: str, timeout: int = 20):
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        status = getattr(resp, "status", 200)
        body = resp.read().decode("utf-8")
    if status >= 400:
        raise RuntimeError(f"HTTP {status}: {url} :: {body[:300]}")
    return json.loads(body)


def load_pairs(chain: str, token_address: str) -> list[dict]:
    url = f"https://api.dexscreener.com/token-pairs/v1/{chain}/{token_address}"
    payload = json_request(url)
    if not isinstance(payload, list):
        raise RuntimeError(f"unexpected DexScreener payload for {chain} {token_address}: {type(payload)!r}")
    return payload


def to_float(value, default=0.0) -> float:
    try:
        if value in (None, "", "null"):
            return default
        return float(value)
    except Exception:
        return default


def pick_lane_snapshot(spec: dict, captured_at: datetime) -> dict:
    pairs = load_pairs(spec["chain"], spec["token_address"])
    rows: list[dict] = []
    for item in pairs:
        base_symbol = ((item.get("baseToken") or {}).get("symbol") or "").upper()
        quote_symbol = ((item.get("quoteToken") or {}).get("symbol") or "").upper()
        if base_symbol != spec["base_symbol"].upper() or quote_symbol != spec["quote_symbol"].upper():
            continue
        price = to_float(item.get("priceUsd"))
        liquidity = to_float(((item.get("liquidity") or {}).get("usd")))
        if price <= 0 or liquidity < spec["liquidity_floor_usd"]:
            continue
        volume = item.get("volume") or {}
        txns = item.get("txns") or {}
        rows.append(
            {
                "dex_id": item.get("dexId") or "unknown",
                "pair_address": item.get("pairAddress") or "",
                "price_usd": price,
                "liquidity_usd": liquidity,
                "volume_m5_usd": to_float(volume.get("m5")),
                "volume_h1_usd": to_float(volume.get("h1")),
                "txns_m5": int(to_float(((txns.get("m5") or {}).get("buys"))) + to_float(((txns.get("m5") or {}).get("sells")))),
                "txns_h1": int(to_float(((txns.get("h1") or {}).get("buys"))) + to_float(((txns.get("h1") or {}).get("sells")))),
                "url": item.get("url") or "",
                "labels": ",".join(item.get("labels") or []),
            }
        )
    if len(rows) < 2:
        raise RuntimeError(
            f"lane {spec['chain']} {spec['base_symbol']}/{spec['quote_symbol']} floor {spec['liquidity_floor_usd']} has only {len(rows)} liquid pools"
        )
    frame = pd.DataFrame(rows).sort_values(["price_usd", "liquidity_usd", "dex_id"], ascending=[True, False, True]).reset_index(drop=True)
    cheapest = frame.iloc[0]
    richest = frame.iloc[-1]
    gross_bps = (float(richest["price_usd"]) / float(cheapest["price_usd"]) - 1.0) * 10000.0
    gas_usd = CHAIN_GAS_USD[spec["chain"]]
    net_by_notional = {str(n): gross_bps - ROUND_TRIP_NON_GAS_BPS - (gas_usd / float(n) * 10000.0) for n in NOTIONALS}
    best_net_bps = max(net_by_notional.values())
    return {
        "captured_at_utc": iso_z(captured_at),
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "chain": spec["chain"],
        "base_symbol": spec["base_symbol"],
        "quote_symbol": spec["quote_symbol"],
        "token_symbol": spec["token_symbol"],
        "liquidity_floor_usd": int(spec["liquidity_floor_usd"]),
        "launch_priority": int(spec["launch_priority"]),
        "liquid_pool_count": int(len(frame)),
        "gross_bps": gross_bps,
        "non_gas_friction_bps": ROUND_TRIP_NON_GAS_BPS,
        "gas_usd_assumption": gas_usd,
        "best_net_bps": best_net_bps,
        "net_bps_5000": net_by_notional["5000"],
        "net_bps_10000": net_by_notional["10000"],
        "net_bps_25000": net_by_notional["25000"],
        "min_liquidity_usd": float(frame["liquidity_usd"].min()),
        "median_liquidity_usd": float(frame["liquidity_usd"].median()),
        "min_volume_m5_usd": float(frame["volume_m5_usd"].min()),
        "median_volume_m5_usd": float(frame["volume_m5_usd"].median()),
        "min_volume_h1_usd": float(frame["volume_h1_usd"].min()),
        "median_volume_h1_usd": float(frame["volume_h1_usd"].median()),
        "min_txns_m5": int(frame["txns_m5"].min()),
        "median_txns_m5": float(frame["txns_m5"].median()),
        "buy_dex": str(cheapest["dex_id"]),
        "buy_pair_address": str(cheapest["pair_address"]),
        "buy_price_usd": float(cheapest["price_usd"]),
        "sell_dex": str(richest["dex_id"]),
        "sell_pair_address": str(richest["pair_address"]),
        "sell_price_usd": float(richest["price_usd"]),
    }


def build_spec() -> dict:
    lane_specs = [
        {
            "chain": x["chain"],
            "token_symbol": x["token_symbol"],
            "token_address": x["token_address"],
            "base_symbol": x["base_symbol"],
            "quote_symbol": x["quote_symbol"],
            "liquidity_floor_usd": x["liquidity_floor_usd"],
            "launch_priority": x["launch_priority"],
        }
        for x in LANES
    ]
    dex_audit_universe_by_lane = [
        {
            "chain": "base",
            "base_symbol": "WETH",
            "quote_symbol": "USDC",
            "liquidity_floor_usd": 1_000_000,
            "observed_dex_ids_in_runner_ledger": ["aerodrome", "pancakeswap", "uniswap"],
        },
        {
            "chain": "base",
            "base_symbol": "cbBTC",
            "quote_symbol": "WETH",
            "liquidity_floor_usd": 1_000_000,
            "observed_dex_ids_in_runner_ledger": ["aerodrome", "hydrex", "pancakeswap", "uniswap"],
        },
        {
            "chain": "arbitrum",
            "base_symbol": "WETH",
            "quote_symbol": "USDC",
            "liquidity_floor_usd": 250_000,
            "observed_dex_ids_in_runner_ledger": ["sushiswap", "uniswap"],
        },
        {
            "chain": "arbitrum",
            "base_symbol": "WBTC",
            "quote_symbol": "WETH",
            "liquidity_floor_usd": 250_000,
            "observed_dex_ids_in_runner_ledger": ["uniswap"],
        },
    ]
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "baseline": "price-gap close mean-reversion shell",
        "increment": "same-chain cross-DEX price-gap close",
        "scope": "Base-first / Arbitrum-second / same-chain only / exclude Ethereum high-gas lane",
        "audit_scope": {
            "included_chains": ["base", "arbitrum"],
            "excluded_chains": ["ethereum"],
            "same_chain_only": True,
            "high_liquidity_only": True,
        },
        "runner_mode": "live_snapshot_low_gas_samechain_lane",
        "input_data_source": {
            "provider": "DexScreener",
            "endpoint_template": "https://api.dexscreener.com/token-pairs/v1/{chain}/{token_address}",
            "data_kind": "pool quote snapshot",
            "uses_pool_quotes": True,
            "uses_router_quotes": False,
            "uses_fill_replay": False,
            "uses_order_book": False,
            "uses_mempool_or_mev_capture_trace": False,
            "field_usage": {
                "price_field": "priceUsd",
                "liquidity_field": "liquidity.usd",
                "activity_audit_fields": ["volume.m5", "volume.h1", "txns.m5", "txns.h1"],
                "dex_field": "dexId",
            },
        },
        "non_gas_friction_bps": ROUND_TRIP_NON_GAS_BPS,
        "gas_usd_by_chain": CHAIN_GAS_USD,
        "notional_grid_usd": NOTIONALS,
        "lanes": lane_specs,
        "dex_audit_universe_by_lane": dex_audit_universe_by_lane,
        "candidate_trigger": {
            "lane_must_be_preapproved": True,
            "pair_match_rule": "exact base_symbol + quote_symbol match inside the lane",
            "minimum_eligible_pools": 2,
            "hard_filters": [
                "priceUsd > 0",
                "liquidity.usd >= lane liquidity_floor_usd",
                "pool returned by DexScreener token-pairs snapshot for the lane token address",
            ],
            "candidate_definition": "after filtering there are at least 2 eligible pools, so runner can identify cheapest buy pool and richest sell pool and compute gross_gap_bps",
        },
        "execution_signal": {
            "direction": "buy cheapest eligible pool / sell richest eligible pool",
            "formula": "gross_gap_bps = (sell_price_usd / buy_price_usd - 1) * 10000; gas_bps = gas_usd_by_chain[chain] / notional * 10000; net_gap_bps = gross_gap_bps - 13bps - gas_bps",
            "gate": "execution signal exists if any fixed notional in [5000, 10000, 25000] has net_gap_bps > 0",
        },
        "exit_definition": {
            "paper_rule": [
                "net_gap_bps <= 0 on the same lane",
                "max_holding_time = 15m",
                "quote/liquidity anomaly on either leg",
            ],
            "runner_reality": "current runner is a snapshot recorder and does not yet maintain a live open-position state machine; exit is frozen for paper interpretation, not automated fill management",
        },
        "quote_freshness_and_staleness": {
            "same_refresh_snapshot_only": True,
            "captured_at_policy": "one refresh run stamps a single captured_at_utc for all lane rows in that run",
            "hard_reject_if": [
                "priceUsd missing or <= 0",
                "liquidity.usd below lane floor",
                "eligible pool count < 2",
            ],
            "explicit_per_pool_quote_age_available": False,
            "explicit_onchain_block_timestamp_check": False,
            "activity_metrics_recorded_for_audit_not_gate": ["volume.m5", "volume.h1", "txns.m5", "txns.h1"],
            "staleness_buffer_policy": "quote-staleness / slippage / MEV uncertainty is conservatively absorbed into the fixed 13bps non-gas friction floor",
        },
        "seed_exit_decision_artifact": str(SEED_EXIT_PATH.relative_to(ROOT)),
        "observation_status": "observe_only_non_mainline",
        "notes": "Rank 342 is retained only as an observation line. The runner keeps recording fresh DexScreener same-chain lane snapshots for historical comparison, but the project no longer treats this as a main profit candidate and will not expand research, audit, or execution development around it.",
    }


def write_html(status: dict, top_lane: dict | None, lane_frame: pd.DataFrame) -> None:
    ensure_dir(HTML_PATH.parent)
    preview_cols = [
        "chain", "base_symbol", "quote_symbol", "liquidity_floor_usd", "liquid_pool_count",
        "gross_bps", "net_bps_5000", "net_bps_10000", "net_bps_25000", "buy_dex", "sell_dex"
    ]
    preview = lane_frame[preview_cols].copy() if not lane_frame.empty else pd.DataFrame()
    body = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>Rank 342 Paper Runner（观察线）</title>
  <style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}code{{background:#f3f3f3;padding:2px 4px}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px 8px}}pre{{background:#fafafa;padding:12px;border:1px solid #eee;overflow:auto}}.banner{{border:2px solid #93c5fd;background:#eff6ff;padding:12px 14px;margin-bottom:16px}}.pill{{display:inline-block;border-radius:999px;padding:3px 9px;font-size:12px;background:#dbeafe;color:#1d4ed8}}</style>
</head>
<body>
  <div class=\"banner\">
    <h1 style=\"margin-top:0\">Rank 342 / same-chain cross-DEX price-gap close</h1>
    <p><span class=\"pill\">观察线 / 非主研发线</span></p>
    <p><b>当前仅保留观察价值，主线已切回 CEX 内部 baseline 家族。</b> 这次降级的一个直接原因是：<b>rank342 的技术门槛较高</b>，需要更重的成交、路由、滑点、MEV、staleness 能力，因此不适合作为当前最优先研发对象。本页继续保留低 gas same-chain lane 的定时快照与 pocket 记录，供回看和横向比较；但 rank342 已不再作为主赚钱候选，不再投入新的研究、审计和执行开发，不再扩展 lane、成本模型和成交系统。</p>
  </div>
  <p><strong>接线状态：</strong>{status['wiring_status']}（仅保留观察）</p>
  <ul>
    <li>runner: <code>{status['runner_script']}</code></li>
    <li>service: <code>{status['service_unit']}</code></li>
    <li>timer: <code>{status['timer_unit']}</code></li>
    <li>scope: <code>{status['scope']}</code></li>
    <li>最近更新时间: <code>{status['updated_at_utc']}</code></li>
    <li>本轮有效 lane 数: <code>{status['active_lane_count']}</code></li>
    <li>当前最佳 lane: <code>{status['best_lane_label']}</code></li>
    <li>当前最佳净 pocket: <code>{status['best_lane_best_net_bps']:.2f} bps</code></li>
  </ul>
  <p>说明：当前 runner 只作为快照观察器保留；不要把它解读成主线 paper 执行对象，更不要把它解读成已完成逐笔成交回放或 MEV 完整建模。</p>
  <h2>当前 lane 看板</h2>
  {preview.to_html(index=False) if not preview.empty else '<p>暂无有效 lane</p>'}
  <h2>当前最佳 lane 详情</h2>
  <pre>{json.dumps(top_lane or {'state': 'no-valid-lane'}, ensure_ascii=False, indent=2)}</pre>
</body>
</html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank342 same-chain cross-DEX paper runner")
    parser.add_argument("--refresh", action="store_true", help="Refresh paper runner artifacts from live DexScreener lane snapshots.")
    args = parser.parse_args()
    if not args.refresh:
        parser.error("choose --refresh")

    ensure_dir(ART_DIR)
    spec = build_spec()
    write_json(SPEC_PATH, spec)
    captured_at = utc_now()
    rows = [pick_lane_snapshot(lane, captured_at) for lane in LANES]
    lane_frame = pd.DataFrame(rows).sort_values(["launch_priority", "best_net_bps"], ascending=[True, False]).reset_index(drop=True)
    normalize_for_csv(lane_frame).to_csv(CURRENT_SIGNAL_PATH, index=False)

    ledger = lane_frame.copy()
    ledger["snapshot_id"] = ledger.apply(lambda r: f"{captured_at.strftime('%Y%m%dT%H%M%SZ')}|{r['chain']}|{r['base_symbol']}|{r['quote_symbol']}|{int(r['liquidity_floor_usd'])}", axis=1)
    ledger_cols = [
        "snapshot_id", "captured_at_utc", "candidate_id", "candidate_rank", "chain", "base_symbol", "quote_symbol",
        "token_symbol", "liquidity_floor_usd", "launch_priority", "liquid_pool_count", "gross_bps",
        "non_gas_friction_bps", "gas_usd_assumption", "best_net_bps", "net_bps_5000", "net_bps_10000",
        "net_bps_25000", "min_liquidity_usd", "median_liquidity_usd", "min_volume_m5_usd", "median_volume_m5_usd",
        "min_volume_h1_usd", "median_volume_h1_usd", "min_txns_m5", "median_txns_m5", "buy_dex", "buy_pair_address",
        "buy_price_usd", "sell_dex", "sell_pair_address", "sell_price_usd"
    ]
    existing = pd.read_csv(LEDGER_PATH) if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0 else pd.DataFrame(columns=ledger_cols)
    combined = pd.concat([existing, normalize_for_csv(ledger[ledger_cols])], ignore_index=True)
    combined = combined.drop_duplicates(subset=["snapshot_id"], keep="last")
    combined.to_csv(LEDGER_PATH, index=False)

    top_lane = lane_frame.sort_values(["launch_priority", "best_net_bps"], ascending=[True, False]).iloc[0].to_dict() if not lane_frame.empty else None
    active_positive_count = int((lane_frame["best_net_bps"] > 0).sum()) if not lane_frame.empty else 0
    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live",
        "runner_mode": "live_snapshot_low_gas_samechain_lane",
        "runner_script": "scripts/run_rank342_samechain_crossdex_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "source_seed_artifact": str(SEED_EXIT_PATH.relative_to(ROOT)),
        "frozen_spec_path": str(SPEC_PATH.relative_to(ROOT)),
        "refresh_cadence": "15m",
        "active_lane_count": int(len(lane_frame)),
        "positive_lane_count": active_positive_count,
        "best_lane_label": f"{top_lane['chain']} {top_lane['base_symbol']}/{top_lane['quote_symbol']} floor>={int(top_lane['liquidity_floor_usd'])}" if top_lane else "none",
        "best_lane_best_net_bps": float(top_lane["best_net_bps"]) if top_lane else 0.0,
        "best_lane_gross_bps": float(top_lane["gross_bps"]) if top_lane else 0.0,
        "best_lane_buy_dex": top_lane["buy_dex"] if top_lane else "",
        "best_lane_sell_dex": top_lane["sell_dex"] if top_lane else "",
        "best_lane_captured_at_utc": top_lane["captured_at_utc"] if top_lane else None,
        "closed_snapshots": int(len(combined)),
        "new_snapshots_appended": int(len(ledger)),
        "updated_at_utc": iso_z(captured_at),
        "note": "observe_only: dedicated runner + systemd timer remain online only for snapshot observation. Rank 342 is no longer a main profit candidate and will not receive new research, audit, or execution development; current artifacts are retained for comparison only.",
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "connected_runner_live",
        "runner_mode": "live_snapshot_low_gas_samechain_lane",
        "runner_script": str((ROOT / "scripts" / "run_rank342_samechain_crossdex_paper_runner.py").relative_to(ROOT)),
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "scope": spec["scope"],
        "last_run_at_utc": iso_z(captured_at),
        "latest_signal_ts": iso_z(captured_at),
        "active_lane_count": int(len(lane_frame)),
        "positive_lane_count": active_positive_count,
        "best_lane": top_lane or {},
        "closed_snapshots": int(len(combined)),
        "observation_status": "observe_only_non_mainline",
    }
    write_json(STATE_PATH, state)
    write_html(status, top_lane, lane_frame)

    summary = {
        "run_at_utc": iso_z(captured_at),
        "mode": "refresh",
        "runner": "rank342_samechain_crossdex_paper_runner",
        "runner_mode": "live_snapshot_low_gas_samechain_lane",
        "active_lane_count": int(len(lane_frame)),
        "positive_lane_count": active_positive_count,
        "best_lane_label": status["best_lane_label"],
        "best_lane_best_net_bps": status["best_lane_best_net_bps"],
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
        "current_signal_path": str(CURRENT_SIGNAL_PATH.relative_to(ROOT)),
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
