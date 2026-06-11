from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from momentum.domain.canary32b_models import AlphaSignal, PositionState, RiskDecision


@dataclass(slots=True)
class Canary32BRiskConfig:
    kill_switch: bool
    trade_enabled: bool
    enabled_symbols: list[str]
    max_concurrent_positions: int
    max_daily_trades: int
    max_position_notional_per_symbol: float
    allow_entry_fallback_to_taker: bool
    max_data_delay_seconds: int
    require_atr: bool = True
    smallcap_symbols: list[str] = field(default_factory=list)
    max_core_positions: int | None = None
    max_smallcap_positions: int | None = None


@dataclass(slots=True)
class Canary32BPortfolioState:
    open_symbols: list[str]
    pending_entry_symbols: list[str]
    daily_trade_count: int
    api_healthy: bool = True
    bucket_open_symbols: dict[str, list[str]] = field(default_factory=dict)
    bucket_pending_entry_symbols: dict[str, list[str]] = field(default_factory=dict)


@dataclass(slots=True)
class Canary32BMarketContext:
    atr_available: bool
    data_delay_seconds: float
    clock_skew_seconds: float = 0.0
    metadata: dict[str, Any] | None = None


BLOCK_REASONS = {
    "kill_switch": "kill_switch=true",
    "trade_disabled": "trade_enabled=false",
    "symbol_not_enabled": "symbol_not_enabled",
    "live_position_exists": "live_position_exists_for_symbol",
    "entry_pending_exists": "entry_pending_exists_for_symbol",
    "too_many_positions": "max_concurrent_positions_exceeded",
    "too_many_daily_trades": "max_daily_trades_exceeded",
    "too_many_core_positions": "max_core_positions_exceeded",
    "too_many_smallcap_positions": "max_smallcap_positions_exceeded",
    "api_unhealthy": "api_unhealthy",
    "data_delay": "market_data_delay_exceeded",
    "atr_missing": "atr_unavailable",
    "clock_skew": "clock_skew_exceeded",
}


def symbol_bucket(symbol: str, smallcap_symbols: list[str] | None = None) -> str:
    universe = {str(item).upper() for item in (smallcap_symbols or [])}
    return "smallcap" if str(symbol or "").upper() in universe else "core"


def evaluate_entry_risk(
    signal: AlphaSignal,
    *,
    trace_id: str,
    config: Canary32BRiskConfig,
    portfolio: Canary32BPortfolioState,
    market: Canary32BMarketContext,
) -> RiskDecision:
    signal_tag = symbol_bucket(signal.symbol, config.smallcap_symbols)
    bucket_open_symbols = {k: list(v) for k, v in (portfolio.bucket_open_symbols or {}).items()}
    bucket_pending_symbols = {k: list(v) for k, v in (portfolio.bucket_pending_entry_symbols or {}).items()}
    checks: dict[str, Any] = {
        "kill_switch": config.kill_switch,
        "trade_enabled": config.trade_enabled,
        "symbol_enabled": signal.symbol in set(config.enabled_symbols),
        "signal_bucket": signal_tag,
        "open_symbols": list(portfolio.open_symbols),
        "pending_entry_symbols": list(portfolio.pending_entry_symbols),
        "bucket_open_symbols": bucket_open_symbols,
        "bucket_pending_entry_symbols": bucket_pending_symbols,
        "daily_trade_count": int(portfolio.daily_trade_count),
        "api_healthy": bool(portfolio.api_healthy),
        "data_delay_seconds": float(market.data_delay_seconds),
        "clock_skew_seconds": float(market.clock_skew_seconds),
        "atr_available": bool(market.atr_available),
    }

    if config.kill_switch:
        return RiskDecision(False, BLOCK_REASONS["kill_switch"], trace_id, checks)
    if not config.trade_enabled:
        return RiskDecision(False, BLOCK_REASONS["trade_disabled"], trace_id, checks)
    if signal.symbol not in set(config.enabled_symbols):
        return RiskDecision(False, BLOCK_REASONS["symbol_not_enabled"], trace_id, checks)
    if signal.symbol in set(portfolio.open_symbols):
        return RiskDecision(False, BLOCK_REASONS["live_position_exists"], trace_id, checks)
    if signal.symbol in set(portfolio.pending_entry_symbols):
        return RiskDecision(False, BLOCK_REASONS["entry_pending_exists"], trace_id, checks)

    open_total = len(set(portfolio.open_symbols))
    pending_total = len(set(portfolio.pending_entry_symbols))
    if open_total + pending_total >= config.max_concurrent_positions:
        return RiskDecision(False, BLOCK_REASONS["too_many_positions"], trace_id, checks)

    core_cap = int(config.max_core_positions) if config.max_core_positions is not None else None
    smallcap_cap = int(config.max_smallcap_positions) if config.max_smallcap_positions is not None else None
    bucket_open = len(set(bucket_open_symbols.get(signal_tag, [])))
    bucket_pending = len(set(bucket_pending_symbols.get(signal_tag, [])))
    bucket_total = bucket_open + bucket_pending
    if signal_tag == "core" and core_cap is not None and bucket_total >= core_cap:
        return RiskDecision(False, BLOCK_REASONS["too_many_core_positions"], trace_id, checks)
    if signal_tag == "smallcap" and smallcap_cap is not None and bucket_total >= smallcap_cap:
        return RiskDecision(False, BLOCK_REASONS["too_many_smallcap_positions"], trace_id, checks)

    if int(portfolio.daily_trade_count) >= int(config.max_daily_trades):
        return RiskDecision(False, BLOCK_REASONS["too_many_daily_trades"], trace_id, checks)
    if not portfolio.api_healthy:
        return RiskDecision(False, BLOCK_REASONS["api_unhealthy"], trace_id, checks)
    if float(market.data_delay_seconds) > float(config.max_data_delay_seconds):
        return RiskDecision(False, BLOCK_REASONS["data_delay"], trace_id, checks)
    if abs(float(market.clock_skew_seconds)) > 30.0:
        return RiskDecision(False, BLOCK_REASONS["clock_skew"], trace_id, checks)
    if config.require_atr and not market.atr_available:
        return RiskDecision(False, BLOCK_REASONS["atr_missing"], trace_id, checks)
    return RiskDecision(True, "accepted", trace_id, checks)


def portfolio_state_from_runtime(
    symbol_states: list[dict[str, Any]],
    daily_trade_count: int,
    api_healthy: bool = True,
    *,
    live_positions: list[dict[str, Any]] | None = None,
    pending_entries: list[dict[str, Any]] | None = None,
    smallcap_symbols: list[str] | None = None,
) -> Canary32BPortfolioState:
    open_symbols: list[str] = []
    pending_entry_symbols: list[str] = []
    bucket_open_symbols: dict[str, list[str]] = {"core": [], "smallcap": []}
    bucket_pending_entry_symbols: dict[str, list[str]] = {"core": [], "smallcap": []}
    for row in symbol_states:
        symbol = str(row.get("symbol", ""))
        state = str(row.get("position_state", PositionState.FLAT.value))
        if not symbol:
            continue
        bucket = symbol_bucket(symbol, smallcap_symbols)
        if state == PositionState.LIVE_POSITION.value:
            open_symbols.append(symbol)
            bucket_open_symbols.setdefault(bucket, []).append(symbol)
        elif state == PositionState.ENTRY_PENDING.value:
            pending_entry_symbols.append(symbol)
            bucket_pending_entry_symbols.setdefault(bucket, []).append(symbol)

    # 在缩 universe 或外部修复遗留仓位时，symbol_states 只覆盖 enabled_symbols，
    # 这里额外合并原始 live/pending 列表，避免并发仓位计数漏掉禁用 symbol 的遗留暴露。
    for row in live_positions or []:
        symbol = str(row.get("symbol", ""))
        if symbol:
            open_symbols.append(symbol)
            bucket_open_symbols.setdefault(symbol_bucket(symbol, smallcap_symbols), []).append(symbol)
    for row in pending_entries or []:
        symbol = str(row.get("symbol", ""))
        if symbol:
            pending_entry_symbols.append(symbol)
            bucket_pending_entry_symbols.setdefault(symbol_bucket(symbol, smallcap_symbols), []).append(symbol)

    open_symbols = list(dict.fromkeys(open_symbols))
    pending_entry_symbols = list(dict.fromkeys(pending_entry_symbols))
    for bucket in list(bucket_open_symbols.keys()):
        bucket_open_symbols[bucket] = list(dict.fromkeys(bucket_open_symbols[bucket]))
    for bucket in list(bucket_pending_entry_symbols.keys()):
        bucket_pending_entry_symbols[bucket] = list(dict.fromkeys(bucket_pending_entry_symbols[bucket]))
    return Canary32BPortfolioState(
        open_symbols=open_symbols,
        pending_entry_symbols=pending_entry_symbols,
        daily_trade_count=int(daily_trade_count),
        api_healthy=bool(api_healthy),
        bucket_open_symbols=bucket_open_symbols,
        bucket_pending_entry_symbols=bucket_pending_entry_symbols,
    )
