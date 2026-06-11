"""Binance USDⓈ-M Futures broker adapter for first-money strategy.

Uses REST API to place market orders on Binance Futures testnet/mainnet.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(slots=True)
class OrderResult:
    order_id: str
    symbol: str
    side: str
    order_type: str
    status: str
    qty: float
    price: float | None
    avg_fill_price: float | None
    filled_qty: float
    submitted_at: str
    updated_at: str
    raw_response: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "status": self.status,
            "qty": self.qty,
            "price": self.price,
            "avg_fill_price": self.avg_fill_price,
            "filled_qty": self.filled_qty,
            "submitted_at": self.submitted_at,
            "updated_at": self.updated_at,
        }


@dataclass
class BinanceFuturesBroker:
    """Binance USDⓈ-M Futures broker for placing and querying orders.

    Supports both testnet and mainnet via the `testnet` flag.
    """
    api_key: str
    secret_key: str
    testnet: bool = True
    recv_window: int = 5000
    _base_url: str = ""

    def __post_init__(self) -> None:
        if self.testnet:
            self._base_url = "https://testnet.binancefuture.com"
        else:
            self._base_url = "https://fapi.binance.com"

    def _sign(self, params: dict) -> str:
        qs = urlencode(params)
        sig = hmac.new(
            self.secret_key.encode("utf-8"),
            qs.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return sig

    def _headers(self) -> dict:
        return {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _request(self, method: str, path: str, params: dict | None = None, signed: bool = False) -> dict:
        params = dict(params or {})
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = self.recv_window
            params["signature"] = self._sign(params)

        url = f"{self._base_url}{path}"
        if method == "GET":
            if params:
                url += "?" + urlencode(params)
            req = Request(url, headers=self._headers(), method="GET")
        else:
            data = urlencode(params).encode("utf-8")
            req = Request(url, data=data, headers=self._headers(), method=method)

        with urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
        return json.loads(body)

    def get_account_info(self) -> dict:
        return self._request("GET", "/fapi/v2/account", signed=True)

    def get_balance(self) -> list[dict]:
        return self._request("GET", "/fapi/v2/balance", signed=True)

    def get_usdc_balance(self) -> float:
        balances = self.get_balance()
        for b in balances:
            if b.get("asset") == "USDC":
                return float(b.get("availableBalance", 0))
        return 0.0

    def get_mark_price(self, symbol: str) -> float:
        data = self._request("GET", "/fapi/v1/premiumIndex", {"symbol": symbol})
        return float(data.get("markPrice", 0))

    def get_position(self, symbol: str) -> dict | None:
        positions = self._request("GET", "/fapi/v2/positionRisk", {"symbol": symbol}, signed=True)
        for p in positions:
            amt = float(p.get("positionAmt", 0))
            if amt != 0:
                return p
        return None

    def set_leverage(self, symbol: str, leverage: int = 1) -> dict:
        return self._request("POST", "/fapi/v1/leverage", {
            "symbol": symbol,
            "leverage": leverage,
        }, signed=True)

    def set_margin_type(self, symbol: str, margin_type: str = "ISOLATED") -> dict:
        try:
            return self._request("POST", "/fapi/v1/marginType", {
                "symbol": symbol,
                "marginType": margin_type,
            }, signed=True)
        except Exception:
            # Already set to this type, Binance returns -4046
            return {"msg": "already set", "marginType": margin_type}

    def get_exchange_info(self, symbol: str) -> dict:
        data = self._request("GET", "/fapi/v1/exchangeInfo")
        for s in data.get("symbols", []):
            if s.get("symbol") == symbol:
                return s
        raise ValueError(f"symbol {symbol} not found in exchange info")

    def compute_qty(self, symbol: str, notional_usdc: float) -> float:
        """Compute order quantity from notional value, respecting exchange step size."""
        info = self.get_exchange_info(symbol)
        mark = self.get_mark_price(symbol)
        if mark <= 0:
            raise ValueError(f"invalid mark price: {mark}")

        raw_qty = notional_usdc / mark

        # Find step size and precision
        step_size = None
        qty_precision = 3
        for f in info.get("filters", []):
            if f.get("filterType") == "LOT_SIZE":
                step_size = float(f.get("stepSize", "0.001"))
                break

        if step_size is not None:
            # Truncate to step size
            precision = max(0, -int(__import__("math").log10(step_size))) if step_size > 0 else 3
            qty_precision = precision
            raw_qty = int(raw_qty / step_size) * step_size

        return round(raw_qty, qty_precision)

    def place_market_order(self, symbol: str, side: str, qty: float) -> OrderResult:
        """Place a market order on Binance Futures.

        Args:
            symbol: e.g. "BTCUSDT"
            side: "BUY" for long entry / short exit, "SELL" for short entry / long exit
            qty: order quantity
        """
        now = utc_now_iso()
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "MARKET",
            "quantity": str(qty),
        }
        resp = self._request("POST", "/fapi/v1/order", params, signed=True)

        return OrderResult(
            order_id=str(resp.get("orderId", "")),
            symbol=symbol,
            side=side.upper(),
            order_type="MARKET",
            status=resp.get("status", "UNKNOWN"),
            qty=qty,
            price=None,
            avg_fill_price=float(resp.get("avgPrice", 0)) if resp.get("avgPrice") else None,
            filled_qty=float(resp.get("executedQty", 0)),
            submitted_at=now,
            updated_at=now,
            raw_response=resp,
        )

    def query_order(self, symbol: str, order_id: str) -> OrderResult:
        """Query order status."""
        resp = self._request("GET", "/fapi/v1/order", {
            "symbol": symbol,
            "orderId": order_id,
        }, signed=True)

        return OrderResult(
            order_id=str(resp.get("orderId", "")),
            symbol=symbol,
            side=resp.get("side", ""),
            order_type=resp.get("type", ""),
            status=resp.get("status", "UNKNOWN"),
            qty=float(resp.get("origQty", 0)),
            price=float(resp.get("price", 0)) if resp.get("price") else None,
            avg_fill_price=float(resp.get("avgPrice", 0)) if resp.get("avgPrice") else None,
            filled_qty=float(resp.get("executedQty", 0)),
            submitted_at="",
            updated_at=utc_now_iso(),
            raw_response=resp,
        )

    def close_position(self, symbol: str) -> OrderResult | None:
        """Close any open position for the given symbol."""
        pos = self.get_position(symbol)
        if pos is None:
            return None
        amt = float(pos.get("positionAmt", 0))
        if amt == 0:
            return None
        # If short, close by buying; if long, close by selling
        side = "BUY" if amt < 0 else "SELL"
        qty = abs(amt)
        return self.place_market_order(symbol, side, qty)
