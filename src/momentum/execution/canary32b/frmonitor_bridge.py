from __future__ import annotations

import importlib
import importlib.util
import sys
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_DOWN
from pathlib import Path
from types import ModuleType
from typing import Any, Optional
from urllib.parse import urlencode


@dataclass(slots=True)
class FRMonitorBridge:
    root: Path
    trade_executor: ModuleType
    _binance_papi_permission_cache: tuple[bool, dict[str, Any]] | None = None

    def get_binance_perp_account(self) -> Any:
        return self.trade_executor.get_binance_perp_account()

    def get_binance_perp_positions(self, symbol: str | None = None) -> Any:
        return self.trade_executor.get_binance_perp_positions(symbol=symbol)

    def set_binance_perp_leverage(self, symbol: str, leverage: int | float | str) -> Any:
        return self.trade_executor.set_binance_perp_leverage(symbol=symbol, leverage=leverage)

    def get_binance_perp_usdt_balance(self) -> Any:
        return self.trade_executor.get_binance_perp_usdt_balance()

    def get_lighter_balance_summary(self) -> Any:
        return self.trade_executor.get_lighter_balance_summary()

    def get_lighter_funding_rates_map(self) -> Any:
        return self.trade_executor.get_lighter_funding_rates_map()

    def _binance_public_exchange_info(self, symbol: str, base_url: str = "https://fapi.binance.com") -> dict[str, Any]:
        te = self.trade_executor
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        url = f"{base_url}/fapi/v1/exchangeInfo"
        resp = te._send_request("GET", url, params=[("symbol", pair)])
        data = te._json_or_error(resp)
        if resp.status_code != 200:
            raise te.TradeExecutionError(f"Binance exchangeInfo failed {resp.status_code}: {data}")
        symbols = data.get("symbols") if isinstance(data, dict) else None
        if not isinstance(symbols, list) or not symbols:
            raise te.TradeExecutionError(f"Binance exchangeInfo missing symbol data for {pair}: {data}")
        exact = next((row for row in symbols if str(row.get("symbol", "")).upper() == pair), None)
        if exact is None:
            sample = [str(row.get("symbol")) for row in symbols[:8] if isinstance(row, dict)]
            raise te.TradeExecutionError(f"Binance exchangeInfo returned no exact match for {pair}; sample={sample}")
        return exact

    def get_binance_perp_trade_rules(self, symbol: str, base_url: str = "https://fapi.binance.com") -> dict[str, Any]:
        info = self._binance_public_exchange_info(symbol, base_url=base_url)
        filters = info.get("filters") or []
        lot = next((f for f in filters if f.get("filterType") == "LOT_SIZE"), {})
        notional = next((f for f in filters if f.get("filterType") in {"MIN_NOTIONAL", "NOTIONAL"}), {})
        price_filter = next((f for f in filters if f.get("filterType") == "PRICE_FILTER"), {})
        return {
            "symbol": info.get("symbol"),
            "min_qty": lot.get("minQty"),
            "step_size": lot.get("stepSize"),
            "min_notional": notional.get("notional") or notional.get("minNotional"),
            "tick_size": price_filter.get("tickSize"),
            "price_precision": info.get("pricePrecision"),
            "quantity_precision": info.get("quantityPrecision"),
        }

    def get_binance_perp_last_price(self, symbol: str, base_url: str = "https://fapi.binance.com") -> float:
        te = self.trade_executor
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        url = f"{base_url}/fapi/v1/ticker/price"
        resp = te._send_request("GET", url, params=[("symbol", pair)])
        data = te._json_or_error(resp)
        if resp.status_code != 200:
            raise te.TradeExecutionError(f"Binance ticker price failed {resp.status_code}: {data}")
        return float(data["price"])

    def derive_binance_qty_from_notional(
        self,
        symbol: str,
        notional_usdt: float,
        *,
        last_price: float | None = None,
        rules: dict[str, Any] | None = None,
        base_url: str = "https://fapi.binance.com",
    ) -> dict[str, Any]:
        te = self.trade_executor
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        price = float(last_price) if last_price is not None else self.get_binance_perp_last_price(pair, base_url=base_url)
        rules = rules or self.get_binance_perp_trade_rules(pair, base_url=base_url)
        floor = self.estimate_binance_min_trade_floor(pair, last_price=price, rules=rules, base_url=base_url)
        effective_min_qty = Decimal(str(floor["effective_min_qty"]))
        quantity_str: str | None = None
        adjusted = False

        try:
            payload = te.derive_binance_perp_qty_from_usdt(pair, notional_usdt, price=price, base_url=base_url)
            quantity_str = payload if isinstance(payload, str) else str(payload)
        except Exception as exc:  # noqa: BLE001
            if "below minimum" not in str(exc).lower():
                raise

        if quantity_str is not None:
            qty_dec = Decimal(str(quantity_str))
            if qty_dec < effective_min_qty:
                qty_dec = effective_min_qty
                adjusted = True
            quantity_str = format(qty_dec, "f")
        else:
            quantity_str = format(effective_min_qty, "f")
            adjusted = True

        return {
            "quantity": quantity_str,
            "last_price": price,
            "effective_min_qty": format(effective_min_qty, "f"),
            "effective_min_notional": floor["effective_min_notional"],
            "adjusted_for_min_floor": adjusted,
            "binding_constraint": floor["binding_constraint"],
        }

    def estimate_binance_min_trade_floor(
        self,
        symbol: str,
        *,
        last_price: float,
        rules: dict[str, Any] | None = None,
        base_url: str = "https://fapi.binance.com",
    ) -> dict[str, Any]:
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        rules = rules or self.get_binance_perp_trade_rules(pair, base_url=base_url)
        price_dec = Decimal(str(last_price))
        min_qty_dec = Decimal(str(rules.get("min_qty") or "0"))
        step_dec = Decimal(str(rules.get("step_size") or rules.get("min_qty") or "0"))
        min_notional_dec = Decimal(str(rules.get("min_notional") or "0"))
        if price_dec <= 0:
            raise ValueError(f"invalid last_price for {pair}: {last_price}")
        if step_dec <= 0:
            step_dec = min_qty_dec if min_qty_dec > 0 else Decimal("0.001")
        qty_from_notional = (min_notional_dec / price_dec) if min_notional_dec > 0 else Decimal("0")
        required_qty = max(min_qty_dec, qty_from_notional)
        snapped_steps = (required_qty / step_dec).to_integral_value(rounding=ROUND_CEILING)
        snapped_qty = max(min_qty_dec, snapped_steps * step_dec)
        effective_min_notional = snapped_qty * price_dec

        min_qty_notional = min_qty_dec * price_dec
        if qty_from_notional > min_qty_dec:
            binding = "min_notional"
        elif min_qty_dec > qty_from_notional:
            binding = "min_qty"
        else:
            binding = "both"

        return {
            "symbol": pair,
            "last_price": float(price_dec),
            "min_qty": str(min_qty_dec),
            "step_size": str(step_dec),
            "min_notional": str(min_notional_dec),
            "min_qty_notional_at_last_price": float(min_qty_notional),
            "qty_needed_for_min_notional": float(qty_from_notional),
            "effective_min_qty": str(snapped_qty),
            "effective_min_notional": float(effective_min_notional),
            "binding_constraint": binding,
        }

    def _infer_position_side(self, side: str, reduce_only: bool | None) -> str:
        side_u = side.upper()
        reducing = bool(reduce_only)
        if side_u == "BUY":
            return "SHORT" if reducing else "LONG"
        return "LONG" if reducing else "SHORT"

    def _is_position_side_error(self, exc_or_payload: Any) -> bool:
        text = str(exc_or_payload).lower()
        return "position side does not match" in text or "positionside" in text or "dual-side position" in text

    def _is_reduce_only_mode_error(self, exc_or_payload: Any) -> bool:
        text = str(exc_or_payload).lower()
        return "reduceonly" in text and "not required" in text

    def _is_duplicate_client_order_id_error(self, exc_or_payload: Any) -> bool:
        text = str(exc_or_payload).lower()
        return "clientorderid" in text and "duplicat" in text

    def _is_papi_permission_error(self, status_code: int, payload: Any) -> bool:
        if int(status_code) in {401, 403}:
            return True
        if isinstance(payload, dict):
            code = int(payload.get("code", 0) or 0)
            if code in {-2015, -2014}:
                return True
        text = str(payload).lower()
        return "invalid api-key" in text or "permissions for action" in text

    def has_binance_portfolio_margin_permission(
        self,
        *,
        recv_window: int = 5000,
        papi_base_url: str = "https://papi.binance.com",
    ) -> tuple[bool, dict[str, Any]]:
        cached = self._binance_papi_permission_cache
        if cached is not None:
            return cached
        status_code, data = self._binance_signed_request(
            method="GET",
            path="/papi/v1/balance",
            params=[("recvWindow", str(recv_window))],
            api_base_url=papi_base_url,
        )
        result = (
            int(status_code) == 200,
            {
                "http_status": int(status_code),
                "payload": data,
                "endpoint": "/papi/v1/balance",
                "permission_error": self._is_papi_permission_error(int(status_code), data),
            },
        )
        self._binance_papi_permission_cache = result
        return result

    def _snap_price_to_tick(self, price: float, tick_size: str | None, side: str) -> str:
        if tick_size is None:
            return str(price)
        tick = Decimal(str(tick_size))
        raw = Decimal(str(price))
        if tick <= 0:
            return str(price)
        units = raw / tick
        rounded = units.to_integral_value(rounding=ROUND_DOWN if side.upper() == "BUY" else ROUND_CEILING) * tick
        exponent = tick.normalize().as_tuple().exponent
        quant = Decimal(1).scaleb(exponent) if exponent < 0 else Decimal(1)
        return format(rounded.quantize(quant, rounding=ROUND_DOWN), "f")

    def _retry_client_order_id(self, base: Optional[str], retry_idx: int) -> Optional[str]:
        if not base:
            return None
        if retry_idx <= 0:
            return base
        suffix = f"-r{retry_idx}"
        candidate = f"{base[: max(1, 36 - len(suffix))]}{suffix}"
        return self.trade_executor._sanitize_binance_client_order_id(candidate)

    def place_binance_perp_live_algo_order(
        self,
        *,
        symbol: str,
        side: str,
        algo_type: str,
        order_type: str,
        quantity: float | str | None = None,
        price: float | str | None = None,
        trigger_price: float | str | None = None,
        reduce_only: bool | None = None,
        client_algo_id: Optional[str] = None,
        position_side: Optional[str] = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
        working_type: str = "CONTRACT_PRICE",
        price_protect: bool = False,
        time_in_force: str | None = None,
    ) -> Any:
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        resolved_position_side = position_side.upper() if position_side else None
        algo_type_u = str(algo_type).upper()
        order_type_u = str(order_type).upper()
        resolved_working_type = str(working_type or "CONTRACT_PRICE").upper()
        rules = self.get_binance_perp_trade_rules(pair, base_url=base_url)
        qty_str = None
        if quantity is not None:
            qty_str, _ = self.trade_executor._normalise_binance_quantity(pair, quantity, base_url)
        price_str = None if price is None else self._snap_price_to_tick(float(price), rules.get("tick_size"), side)
        trigger_price_str = None if trigger_price is None else self._snap_price_to_tick(float(trigger_price), rules.get("tick_size"), side)
        sanitized_client_algo_id = self.trade_executor._sanitize_binance_client_order_id(client_algo_id)

        def _submit(pos_side: Optional[str], reduce_only_flag: bool | None, retry_idx: int = 0):
            used_client_algo_id = self._retry_client_order_id(sanitized_client_algo_id, retry_idx)
            params: list[tuple[str, str]] = [
                ("algoType", algo_type_u),
                ("symbol", pair),
                ("side", side.upper()),
                ("type", order_type_u),
                ("recvWindow", str(recv_window)),
            ]
            if pos_side:
                params.append(("positionSide", pos_side.upper()))
            if qty_str is not None:
                params.append(("quantity", qty_str))
            if price_str is not None:
                params.append(("price", price_str))
            if trigger_price_str is not None:
                params.append(("triggerPrice", trigger_price_str))
            if time_in_force:
                params.append(("timeInForce", str(time_in_force).upper()))
            if reduce_only_flag is not None:
                params.append(("reduceOnly", "true" if reduce_only_flag else "false"))
            if order_type_u in {"STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET", "TRAILING_STOP_MARKET"}:
                params.append(("workingType", resolved_working_type))
            if order_type_u in {"STOP_MARKET", "TAKE_PROFIT_MARKET"}:
                params.append(("priceProtect", "TRUE" if price_protect else "FALSE"))
            if used_client_algo_id:
                params.append(("clientAlgoId", used_client_algo_id))
            status_code, data = self._binance_signed_request(
                method="POST",
                path="/fapi/v1/algoOrder",
                params=params,
                api_base_url=base_url,
            )
            return int(status_code), data, pos_side, reduce_only_flag, used_client_algo_id

        status_code, data, used_position_side, used_reduce_only, used_client_algo_id = _submit(resolved_position_side, reduce_only, 0)
        if status_code != 200 and resolved_position_side is None and self._is_position_side_error(data):
            inferred = self._infer_position_side(side, reduce_only)
            status_code, data, used_position_side, used_reduce_only, used_client_algo_id = _submit(inferred, reduce_only, 1)
        if status_code != 200 and used_position_side is not None and self._is_reduce_only_mode_error(data):
            status_code, data, used_position_side, used_reduce_only, used_client_algo_id = _submit(used_position_side, None, 2)
        if status_code != 200 and used_position_side is not None and self._is_position_side_error(data):
            status_code, data, used_position_side, used_reduce_only, used_client_algo_id = _submit(None, reduce_only, 3)
        if status_code != 200:
            raise self.trade_executor.TradeExecutionError(f"Binance algo order failed {status_code}: {data}")
        return {
            "http_status": status_code,
            "payload": data,
            "symbol": pair,
            "side": side.upper(),
            "quantity": qty_str,
            "price": price_str,
            "trigger_price": trigger_price_str,
            "reduce_only": used_reduce_only,
            "position_side": used_position_side,
            "client_order_id": used_client_algo_id,
            "client_algo_id": used_client_algo_id,
            "endpoint": "/fapi/v1/algoOrder",
            "workingType": resolved_working_type,
            "type": order_type_u,
            "transport": "fapi_algo",
            "algo_id": data.get("algoId") if isinstance(data, dict) else None,
            "status": data.get("algoStatus") if isinstance(data, dict) else None,
            "timeInForce": str(time_in_force).upper() if time_in_force else None,
        }

    def get_binance_perp_algo_order(
        self,
        *,
        algo_id: Any = None,
        client_algo_id: str | None = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
    ) -> Any:
        params = [("recvWindow", str(recv_window))]
        if algo_id is not None:
            params.append(("algoId", str(algo_id)))
        elif client_algo_id:
            params.append(("clientAlgoId", str(client_algo_id)))
        else:
            raise ValueError("algo_id or client_algo_id required for algo order query")
        status_code, data = self._binance_signed_request(
            method="GET",
            path="/fapi/v1/algoOrder",
            params=params,
            api_base_url=base_url,
        )
        if status_code != 200:
            raise self.trade_executor.TradeExecutionError(f"Binance algo order query failed {status_code}: {data}")
        return data

    def cancel_binance_perp_algo_order(
        self,
        *,
        algo_id: Any = None,
        client_algo_id: str | None = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
    ) -> Any:
        params = [("recvWindow", str(recv_window))]
        if algo_id is not None:
            params.append(("algoId", str(algo_id)))
        elif client_algo_id:
            params.append(("clientAlgoId", str(client_algo_id)))
        else:
            raise ValueError("algo_id or client_algo_id required for algo order cancel")
        status_code, data = self._binance_signed_request(
            method="DELETE",
            path="/fapi/v1/algoOrder",
            params=params,
            api_base_url=base_url,
        )
        if status_code != 200:
            raise self.trade_executor.TradeExecutionError(f"Binance algo order cancel failed {status_code}: {data}")
        return data

    def submit_binance_perp_test_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float | str,
        reduce_only: bool | None = None,
        client_order_id: Optional[str] = None,
        position_side: Optional[str] = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
    ) -> Any:
        te = self.trade_executor
        creds = te._resolve_binance_credentials(None, None)
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        qty_str, _ = te._normalise_binance_quantity(pair, quantity, base_url)
        client_order_id = te._sanitize_binance_client_order_id(client_order_id)

        params = [
            ("symbol", pair),
            ("side", side.upper()),
            ("type", "MARKET"),
            ("timestamp", te._utc_millis_str()),
            ("recvWindow", str(recv_window)),
            ("quantity", qty_str),
        ]
        if reduce_only is not None:
            params.append(("reduceOnly", "true" if reduce_only else "false"))
        if client_order_id:
            params.append(("newClientOrderId", client_order_id))
        if position_side:
            params.append(("positionSide", position_side.upper()))

        query = urlencode(params)
        signature = te._hmac_sha256_hexdigest(creds.secret_key, query)
        params.append(("signature", signature))
        headers = {"X-MBX-APIKEY": creds.api_key, "User-Agent": te.USER_AGENT}
        url = f"{base_url}/fapi/v1/order/test"
        resp = te._send_request("POST", url, params=params, headers=headers)
        data = te._json_or_error(resp)
        if resp.status_code != 200:
            raise te.TradeExecutionError(f"Binance test order failed {resp.status_code}: {data}")
        return {
            "http_status": resp.status_code,
            "payload": data,
            "symbol": pair,
            "side": side.upper(),
            "quantity": qty_str,
            "reduce_only": reduce_only,
            "client_order_id": client_order_id,
            "endpoint": "/fapi/v1/order/test",
        }

    def place_binance_perp_live_limit_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float | str,
        price: float | str,
        reduce_only: bool | None = None,
        client_order_id: Optional[str] = None,
        position_side: Optional[str] = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
        time_in_force: str = "GTX",
    ) -> Any:
        te = self.trade_executor
        creds = te._resolve_binance_credentials(None, None)
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        qty_str, _ = te._normalise_binance_quantity(pair, quantity, base_url)
        rules = self.get_binance_perp_trade_rules(pair, base_url=base_url)
        price_str = self._snap_price_to_tick(float(price), rules.get("tick_size"), side)
        client_order_id = te._sanitize_binance_client_order_id(client_order_id)
        tif = (time_in_force or "GTX").upper()
        resolved_position_side = position_side.upper() if position_side else None

        def _retry_client_order_id(base: Optional[str], retry_idx: int) -> Optional[str]:
            if not base:
                return None
            if retry_idx <= 0:
                return base
            suffix = f"-r{retry_idx}"
            candidate = f"{base[: max(1, 36 - len(suffix))]}{suffix}"
            return te._sanitize_binance_client_order_id(candidate)

        def _submit(pos_side: Optional[str], reduce_only_flag: bool | None, retry_idx: int = 0):
            used_client_order_id = _retry_client_order_id(client_order_id, retry_idx)
            params = [
                ("symbol", pair),
                ("side", side.upper()),
                ("type", "LIMIT"),
                ("timeInForce", tif),
                ("price", price_str),
                ("quantity", qty_str),
                ("timestamp", te._utc_millis_str()),
                ("recvWindow", str(recv_window)),
                ("newOrderRespType", "ACK"),
            ]
            if reduce_only_flag is not None:
                params.append(("reduceOnly", "true" if reduce_only_flag else "false"))
            if used_client_order_id:
                params.append(("newClientOrderId", used_client_order_id))
            if pos_side:
                params.append(("positionSide", pos_side.upper()))
            query = urlencode(params)
            signature = te._hmac_sha256_hexdigest(creds.secret_key, query)
            params.append(("signature", signature))
            headers = {"X-MBX-APIKEY": creds.api_key, "User-Agent": te.USER_AGENT}
            url = f"{base_url}/fapi/v1/order"
            resp = te._send_request("POST", url, params=params, headers=headers)
            data = te._json_or_error(resp)
            return int(resp.status_code), data, pos_side, reduce_only_flag, used_client_order_id

        def _recover_duplicate_order(status_code: int, payload: Any, used_client_order_id: Optional[str]) -> tuple[int, Any]:
            if status_code == 200 or not used_client_order_id or not self._is_duplicate_client_order_id_error(payload):
                return status_code, payload
            try:
                existing = self.get_binance_perp_order(
                    pair,
                    client_order_id=used_client_order_id,
                    recv_window=recv_window,
                    base_url=base_url,
                )
            except Exception:  # noqa: BLE001
                return status_code, payload
            if isinstance(existing, dict) and str(existing.get("clientOrderId") or "") == str(used_client_order_id):
                return 200, existing
            return status_code, payload

        status_code, data, used_position_side, used_reduce_only, used_client_order_id = _submit(resolved_position_side, reduce_only, 0)
        status_code, data = _recover_duplicate_order(status_code, data, used_client_order_id)
        if status_code != 200 and resolved_position_side is None and self._is_position_side_error(data):
            inferred = self._infer_position_side(side, reduce_only)
            status_code, data, used_position_side, used_reduce_only, used_client_order_id = _submit(inferred, reduce_only, 1)
            status_code, data = _recover_duplicate_order(status_code, data, used_client_order_id)
        if status_code != 200 and used_position_side is not None and self._is_reduce_only_mode_error(data):
            status_code, data, used_position_side, used_reduce_only, used_client_order_id = _submit(used_position_side, None, 2)
            status_code, data = _recover_duplicate_order(status_code, data, used_client_order_id)
        if status_code != 200 and used_position_side is not None and self._is_position_side_error(data):
            status_code, data, used_position_side, used_reduce_only, used_client_order_id = _submit(None, reduce_only, 3)
            status_code, data = _recover_duplicate_order(status_code, data, used_client_order_id)
        if status_code != 200:
            raise te.TradeExecutionError(f"Binance live limit order failed {status_code}: {data}")
        return {
            "http_status": status_code,
            "payload": data,
            "symbol": pair,
            "side": side.upper(),
            "quantity": qty_str,
            "price": price_str,
            "reduce_only": used_reduce_only,
            "position_side": used_position_side,
            "client_order_id": used_client_order_id,
            "endpoint": "/fapi/v1/order",
            "timeInForce": tif,
            "type": "LIMIT",
            "order_id": data.get("orderId") if isinstance(data, dict) else None,
            "status": data.get("status") if isinstance(data, dict) else None,
        }

    def place_binance_perp_live_limit_gtx_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float | str,
        price: float | str,
        reduce_only: bool | None = None,
        client_order_id: Optional[str] = None,
        position_side: Optional[str] = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
        time_in_force: str = "GTX",
    ) -> Any:
        return self.place_binance_perp_live_limit_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            reduce_only=reduce_only,
            client_order_id=client_order_id,
            position_side=position_side,
            recv_window=recv_window,
            base_url=base_url,
            time_in_force=time_in_force,
        )

    def _binance_signed_request(
        self,
        *,
        method: str,
        path: str,
        params: list[tuple[str, str]],
        api_base_url: str,
    ) -> tuple[int, Any]:
        te = self.trade_executor
        creds = te._resolve_binance_credentials(None, None)
        payload = list(params)
        payload.append(("timestamp", te._utc_millis_str()))
        query = urlencode(payload)
        signature = te._hmac_sha256_hexdigest(creds.secret_key, query)
        payload.append(("signature", signature))
        headers = {"X-MBX-APIKEY": creds.api_key, "User-Agent": te.USER_AGENT}
        resp = te._send_request(method.upper(), f"{api_base_url}{path}", params=payload, headers=headers)
        return int(resp.status_code), te._json_or_error(resp)

    def _place_binance_perp_live_stop_market_order_papi(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float | str,
        stop_price: float | str,
        client_order_id: Optional[str] = None,
        position_side: Optional[str] = None,
        recv_window: int = 5000,
        papi_base_url: str = "https://papi.binance.com",
        working_type: str = "CONTRACT_PRICE",
        price_protect: bool = True,
    ) -> Any:
        te = self.trade_executor
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        qty_str, _ = te._normalise_binance_quantity(pair, quantity, "https://fapi.binance.com")
        rules = self.get_binance_perp_trade_rules(pair)
        stop_price_str = self._snap_price_to_tick(float(stop_price), rules.get("tick_size"), side)
        client_order_id = te._sanitize_binance_client_order_id(client_order_id)
        params = [
            ("symbol", pair),
            ("side", side.upper()),
            ("strategyType", "STOP"),
            ("triggerPrice", stop_price_str),
            ("quantity", qty_str),
            ("recvWindow", str(recv_window)),
            ("workingType", (working_type or "CONTRACT_PRICE").upper()),
            ("priceProtect", "TRUE" if price_protect else "FALSE"),
        ]
        if client_order_id:
            params.append(("newClientStrategyId", client_order_id))
        if position_side:
            params.append(("positionSide", position_side.upper()))
        status_code, data = self._binance_signed_request(
            method="POST",
            path="/papi/v1/um/conditional/order",
            params=params,
            api_base_url=papi_base_url,
        )
        if status_code != 200:
            raise te.TradeExecutionError(f"Binance UM conditional stop order failed {status_code}: {data}")
        return {
            "http_status": status_code,
            "payload": data,
            "symbol": pair,
            "side": side.upper(),
            "quantity": qty_str,
            "stop_price": stop_price_str,
            "position_side": position_side.upper() if position_side else None,
            "client_order_id": (data.get("newClientStrategyId") if isinstance(data, dict) else None) or client_order_id,
            "strategy_id": data.get("strategyId") if isinstance(data, dict) else None,
            "endpoint": "/papi/v1/um/conditional/order",
            "workingType": (working_type or "CONTRACT_PRICE").upper(),
            "type": "STOP_MARKET",
            "transport": "papi_conditional",
            "status": (data.get("strategyStatus") if isinstance(data, dict) else None) or (data.get("status") if isinstance(data, dict) else None),
        }

    def get_binance_perp_conditional_order(
        self,
        symbol: str,
        *,
        strategy_id: Any = None,
        client_order_id: str | None = None,
        recv_window: int = 5000,
        papi_base_url: str = "https://papi.binance.com",
        history: bool = False,
    ) -> Any:
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        params = [("symbol", pair), ("recvWindow", str(recv_window))]
        if strategy_id is not None:
            params.append(("strategyId", str(strategy_id)))
        elif client_order_id:
            params.append(("newClientStrategyId", str(client_order_id)))
        else:
            raise ValueError("strategy_id or client_order_id required for conditional order query")
        path = "/papi/v1/um/conditional/historyOrder" if history else "/papi/v1/um/conditional/openOrder"
        status_code, data = self._binance_signed_request(method="GET", path=path, params=params, api_base_url=papi_base_url)
        if status_code != 200:
            raise self.trade_executor.TradeExecutionError(f"Binance UM conditional order query failed {status_code}: {data}")
        if isinstance(data, list):
            if not data:
                raise self.trade_executor.TradeExecutionError("Binance UM conditional order query returned empty list")
            return data[0]
        return data

    def cancel_binance_perp_conditional_order(
        self,
        symbol: str,
        *,
        strategy_id: Any = None,
        client_order_id: str | None = None,
        recv_window: int = 5000,
        papi_base_url: str = "https://papi.binance.com",
    ) -> Any:
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        params = [("symbol", pair), ("recvWindow", str(recv_window))]
        if strategy_id is not None:
            params.append(("strategyId", str(strategy_id)))
        elif client_order_id:
            params.append(("newClientStrategyId", str(client_order_id)))
        else:
            raise ValueError("strategy_id or client_order_id required for conditional order cancel")
        status_code, data = self._binance_signed_request(method="DELETE", path="/papi/v1/um/conditional/order", params=params, api_base_url=papi_base_url)
        if status_code != 200:
            raise self.trade_executor.TradeExecutionError(f"Binance UM conditional order cancel failed {status_code}: {data}")
        return data

    def place_binance_perp_live_stop_market_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float | str,
        stop_price: float | str,
        reduce_only: bool | None = None,
        client_order_id: Optional[str] = None,
        position_side: Optional[str] = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
        working_type: str = "CONTRACT_PRICE",
        price_protect: bool = True,
    ) -> Any:
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        return self.place_binance_perp_live_algo_order(
            symbol=pair,
            side=side,
            algo_type="CONDITIONAL",
            order_type="STOP_MARKET",
            quantity=quantity,
            trigger_price=stop_price,
            reduce_only=reduce_only,
            client_algo_id=client_order_id,
            position_side=position_side,
            recv_window=recv_window,
            base_url=base_url,
            working_type=working_type,
            price_protect=price_protect,
        )

    def place_binance_perp_live_market_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float | str,
        reduce_only: bool | None = None,
        client_order_id: Optional[str] = None,
        position_side: Optional[str] = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
    ) -> Any:
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        used_position_side = position_side.upper() if position_side else None
        used_reduce_only = reduce_only

        def _retry_client_order_id(base: Optional[str], retry_idx: int) -> Optional[str]:
            if not base:
                return None
            if retry_idx <= 0:
                return base
            suffix = f"-r{retry_idx}"
            candidate = f"{base[: max(1, 36 - len(suffix))]}{suffix}"
            return self.trade_executor._sanitize_binance_client_order_id(candidate)

        used_client_order_id = _retry_client_order_id(client_order_id, 0)
        try:
            data = self.trade_executor.place_binance_perp_market_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                reduce_only=used_reduce_only,
                client_order_id=used_client_order_id,
                position_side=used_position_side,
                recv_window=recv_window,
                base_url=base_url,
            )
        except Exception as exc:  # noqa: BLE001
            if self._is_duplicate_client_order_id_error(exc):
                used_client_order_id = _retry_client_order_id(client_order_id, 1)
                data = self.trade_executor.place_binance_perp_market_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    reduce_only=used_reduce_only,
                    client_order_id=used_client_order_id,
                    position_side=used_position_side,
                    recv_window=recv_window,
                    base_url=base_url,
                )
            elif used_position_side is None and self._is_position_side_error(exc):
                used_position_side = self._infer_position_side(side, reduce_only)
                used_client_order_id = _retry_client_order_id(client_order_id, 2)
                data = self.trade_executor.place_binance_perp_market_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    reduce_only=used_reduce_only,
                    client_order_id=used_client_order_id,
                    position_side=used_position_side,
                    recv_window=recv_window,
                    base_url=base_url,
                )
            elif used_position_side is not None and self._is_position_side_error(exc):
                used_position_side = None
                used_client_order_id = _retry_client_order_id(client_order_id, 3)
                data = self.trade_executor.place_binance_perp_market_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    reduce_only=used_reduce_only,
                    client_order_id=used_client_order_id,
                    position_side=None,
                    recv_window=recv_window,
                    base_url=base_url,
                )
            elif used_position_side is not None and self._is_reduce_only_mode_error(exc):
                used_reduce_only = None
                used_client_order_id = _retry_client_order_id(client_order_id, 4)
                data = self.trade_executor.place_binance_perp_market_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    reduce_only=None,
                    client_order_id=used_client_order_id,
                    position_side=used_position_side,
                    recv_window=recv_window,
                    base_url=base_url,
                )
            else:
                raise
        return {
            "http_status": 200,
            "payload": data,
            "symbol": pair,
            "side": side.upper(),
            "quantity": data.get("origQty") if isinstance(data, dict) else quantity,
            "reduce_only": used_reduce_only,
            "position_side": used_position_side,
            "client_order_id": data.get("clientOrderId") if isinstance(data, dict) else used_client_order_id,
            "endpoint": "/fapi/v1/order",
            "type": "MARKET",
            "order_id": data.get("orderId") if isinstance(data, dict) else None,
            "status": data.get("status") if isinstance(data, dict) else None,
            "executed_qty": data.get("executedQty") if isinstance(data, dict) else None,
            "avg_price": data.get("avgPrice") if isinstance(data, dict) else None,
        }

    def get_binance_perp_order(
        self,
        symbol: str,
        *,
        order_id: Optional[int | str] = None,
        client_order_id: Optional[str] = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
    ) -> Any:
        return self.trade_executor.get_binance_perp_order(
            symbol,
            order_id=order_id,
            client_order_id=client_order_id,
            recv_window=recv_window,
            base_url=base_url,
        )

    def cancel_binance_perp_order(
        self,
        *,
        symbol: str,
        order_id: Optional[int | str] = None,
        client_order_id: Optional[str] = None,
        recv_window: int = 5000,
        base_url: str = "https://fapi.binance.com",
    ) -> Any:
        te = self.trade_executor
        creds = te._resolve_binance_credentials(None, None)
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair = f"{pair}USDT"
        params = [("symbol", pair), ("timestamp", te._utc_millis_str()), ("recvWindow", str(recv_window))]
        if order_id is not None:
            params.append(("orderId", str(order_id)))
        if client_order_id:
            params.append(("origClientOrderId", str(client_order_id)))
        query = urlencode(params)
        signature = te._hmac_sha256_hexdigest(creds.secret_key, query)
        params.append(("signature", signature))
        headers = {"X-MBX-APIKEY": creds.api_key, "User-Agent": te.USER_AGENT}
        url = f"{base_url}/fapi/v1/order"
        resp = te._send_request("DELETE", url, params=params, headers=headers)
        data = te._json_or_error(resp)
        if resp.status_code != 200:
            raise te.TradeExecutionError(f"Binance cancel order failed {resp.status_code}: {data}")
        return data


def _load_module_from_path(module_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load {module_name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_frmonitor_bridge(root: str | Path, *, local_private_path: str | Path | None = None) -> FRMonitorBridge:
    root_path = Path(root).resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"FR_Monitor root not found: {root_path}")
    trading_path = root_path / "trading"
    if not trading_path.exists():
        raise FileNotFoundError(f"FR_Monitor trading dir not found: {trading_path}")

    if str(root_path) not in sys.path:
        sys.path.insert(0, str(root_path))
    if str(trading_path) not in sys.path:
        sys.path.insert(0, str(trading_path))

    if local_private_path is not None:
        private_path = Path(local_private_path).resolve()
        if private_path.exists():
            _load_module_from_path("config_private", private_path)

    config_path = root_path / "config.py"
    _load_module_from_path("config", config_path)
    trade_executor = importlib.import_module("trade_executor")
    return FRMonitorBridge(root=root_path, trade_executor=trade_executor)
