# Phase 7K — 加密原生数据契约与 Schema 验证

> 日期：2026-06-14
>
> 状态：COMPLETE

---

## A. 当前结论

### Taker Imbalance

**结论：READY_WITH_QUOTE_VOLUME_VARIANT**

- `bars_1h.parquet`（static/dynamic）**不包含** taker_buy_volume / taker_buy_quote_volume
- 原始 klines zip **包含** taker_buy_volume 和 taker_buy_quote_volume
- 可用方案：使用 `taker_buy_quote_volume / quote_volume` 作为 taker buy ratio（quote-volume 口径）
- 需要 PM 确认：是否接受 quote-volume 口径？

### Funding Rate

**结论：READY_FOR_CONTRACT**

- 本地存在两个数据源：
  - `data/binance_funding_rate/` — 536 symbols（缺少 ETHUSDT、SOLUSDT、BNBUSDT 等主要币种）
  - `data/binance_vision_rank154/data/futures/um/monthly/fundingRate/` — 679 symbols（覆盖 49/50 top50）
- Schema 一致：`calc_time`, `funding_interval_hours`, `last_funding_rate`
- Interval 固定 8h（±2ms 抖动）
- 推荐使用 binance_vision 路径（覆盖率更高）

---

## B. Bars Schema 结论

| Dataset | Path | Rows | Symbols | Timestamp Range | Taker Fields |
|---------|------|------|---------|-----------------|--------------|
| static | `data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet` | 215,061 | 50 | 2025-12-15 → 2026-06-13 | ❌ 缺失 |
| dynamic | `data/cache/.../bars_1h.parquet` | 3,316,259 | 266 | 2024-06-01 → 2026-06-13 | ❌ 缺失 |

**真实字段**：timestamp, bar_open_time, bar_close_time, symbol, open, high, low, close, volume, quote_volume, trade_count, source, market, instrument_type, timeframe

**缺失字段**：taker_buy_volume, taker_buy_quote_volume（原始 klines 有，但 bars cache 未包含）

---

## C. Taker Imbalance 数据契约

### 方案 A：Quote-volume 口径（推荐，无需 schema 修改）

```
taker_buy_ratio = taker_buy_quote_volume / quote_volume
```

- **优点**：quote_volume 已在 bars_1h.parquet 中；无需修改 build_factor_values.py 的数据源
- **问题**：taker_buy_quote_volume 不在 bars_1h.parquet 中，需要从原始 klines 重新计算
- **需要**：修改 build_factor_values.py 以在 bars_1h.parquet 中包含 taker_buy_quote_volume，或在 factor 计算时直接读取原始 klines

### 方案 B：Base-volume 口径（需要 schema 修改）

```
taker_buy_ratio = taker_buy_volume / volume
```

- **优点**：更直观
- **问题**：taker_buy_volume 不在 bars_1h.parquet 中

### PM 待决

1. 是否接受 quote-volume 口径？（推荐：是）
2. 是否需要修改 bars_1h.parquet schema 以包含 taker 字段？还是在 factor 计算时直接读取原始 klines？

---

## D. Funding Rate 数据契约草案

### 原始数据

- **路径**：`data/binance_vision_rank154/data/futures/um/monthly/fundingRate/<SYMBOL>/`
- **格式**：zip 内含 CSV
- **字段**：`calc_time` (ms), `funding_interval_hours`, `last_funding_rate`
- **Coverage**：679 symbols, 2021-05 → 2026-04
- **Top50 覆盖**：49/50（仅缺 1000PEPEUSDT）
- **Dynamic universe 覆盖**：258/266

### known_at 规则

- **known_at = calc_time**（结算时间，rate 在结算后已知）
- Binance funding 结算时间：00:00, 08:00, 16:00 UTC
- 结算后约 1-2 秒 rate 可用

### 1h 对齐方式

```
方式：merge_asof + forward-fill
1. 解压所有 symbol 的 funding rate，按 calc_time 排序
2. 对每个 symbol，用 merge_asof 将 funding rate 合并到 1h bars 的 timestamp
3. direction='backward'：取最近的已结算 funding rate
4. forward-fill 最大限制：8h（一个 funding interval）
```

### PM 待决

1. **Forward-fill 最大时长**：建议 8h（一个 funding interval）。如果超过 8h 无新数据，填 NaN。是否接受？
2. **Funding interval 变化**：当前数据全部是 8h。如果未来变为 4h 或 1h，如何处理？建议：检测 interval，按实际 interval 做 forward-fill。
3. **Symbol mapping**：直接使用 symbol 名称（与 bars_1h.parquet 一致）。是否需要额外 mapping？
4. **缺失值处理**：如果 symbol 在 funding rate 中不存在，该 symbol 的 funding rate 因子全部填 NaN。是否接受？

### Coverage 口径

- 推荐使用 `binance_vision_rank154` 路径（679 symbols, 49/50 top50）
- 如果需要 100% top50 覆盖，需要单独拉取 1000PEPEUSDT 的 funding rate

---

## E. Phase 7L 建议

Phase 7L can implement taker imbalance factors only (using quote-volume variant, pending PM confirmation on formula).

Funding rate factors should be implemented after the data contract is finalized and the ingestion pipeline is built.

---

## F. 负面声明

No new factors were implemented.
No factor registry was modified.
No factor_ops were modified.
No factor_values were built.
No static evaluation was run.
No dynamic evaluation was run.
No static-vs-dynamic comparison was run.
No diagnostic classification was run.
No redundancy analysis was run.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.
