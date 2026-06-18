# Crypto-Native 数据清单

**Phase 12D-C** | 生成日期: 2026-06-18 | Run: `crypto_top50_usdt_perp_1h`

---

## ✅ 可用数据类型

### 1. Funding Rate

| 属性 | 值 |
|---|---|
| 缓存路径 | `data/cache/crypto_native/crypto_funding_rate_1h_contract_v1/` |
| 文件数 | 3 (dynamic aligned, static aligned, raw events) |
| 行数 | ~3.3M aligned, ~2M raw events |
| 时间范围 | 2024-06 → 2026-06 |
| 符号覆盖 | 266 symbols (full universe) |
| 纳入主流程 | ✅ Yes |
| 使用因子 | `funding_rate_change_24h`, `funding_rate_level_20h`, `funding_rate_zscore_80h` |
| 备注 | Contract-based 1h aligned funding rate |

### 2. Taker Buy/Sell Volume

| 属性 | 值 |
|---|---|
| 缓存路径 | embedded in bars (`taker_buy_volume`, `taker_buy_quote_volume` columns) |
| 文件数 | 0 (非独立文件) |
| 行数 | same as bars_1h (~3.3M) |
| 时间范围 | 2024-06 → 2026-06 |
| 符号覆盖 | 266 symbols |
| 纳入主流程 | ✅ Yes |
| 使用因子 | `taker_buy_delta_5h`, `taker_buy_ratio_20h`, `taker_buy_zscore_20h` |
| 备注 | Not standalone — columns in taker_enriched and crypto_native_v1 bars |

---

## ❌ 不可用 / 未确认数据类型

| 数据类型 | 状态 | 备注 |
|---|---|---|
| Open Interest | 不可用 | No standalone OI data files exist in data/cache/crypto_native/ |
| Basis | 不可用 | Not found |
| Long-Short Ratio | 不可用 | Not found |
| Liquidations | 不可用 | Not found |
| Orderbook Depth | 不可用 | Not found |

---

## Crypto-Native 因子列表 (6 total)

Source: `build_crypto_native_factor_values.py`

1. `funding_rate_change_24h` — 24h funding rate change
2. `funding_rate_level_20h` — 20h funding rate level
3. `funding_rate_zscore_80h` — 80h funding rate z-score
4. `taker_buy_delta_5h` — 5h taker buy-sell delta
5. `taker_buy_ratio_20h` — 20h taker buy ratio
6. `taker_buy_zscore_20h` — 20h taker buy volume z-score
