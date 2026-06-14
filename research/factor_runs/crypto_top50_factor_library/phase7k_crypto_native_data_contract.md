# Phase 7K — 加密原生数据契约与 Schema 验证

> 日期：2026-06-14
>
> 状态：COMPLETE（PM 修正后）

---

## A. 当前结论

### Taker Imbalance

**结论：NEEDS_SCHEMA_FIX**

- `bars_1h.parquet`（static/dynamic）不包含 `taker_buy_volume`。
- `bars_1h.parquet`（static/dynamic）也不包含 `taker_buy_quote_volume`。
- 原始 klines zip 包含 `taker_buy_volume` 和 `taker_buy_quote_volume`。
- 因此，quote-volume 口径是可接受的候选公式方向，但当前 factor-library cache 还不能直接计算。
- 下一步必须先做 bars schema enrichment：把 `taker_buy_quote_volume` 纳入 static/dynamic `bars_1h.parquet` 或建立等价的 canonical cache。

PM 决策：接受 quote-volume taker imbalance 作为优先口径，但必须先修 schema，不允许直接实现 taker factors。

### Funding Rate

**结论：READY_FOR_CONTRACT**

- 本地存在两个数据源：
  - `data/binance_funding_rate/` — 536 symbols
  - `data/binance_vision_rank154/data/futures/um/monthly/fundingRate/` — 679 symbols，覆盖 49/50 top50
- Schema 一致：`calc_time`, `funding_interval_hours`, `last_funding_rate`
- Interval 固定 8h（±2ms 抖动）
- 推荐使用 binance_vision 路径（覆盖率更高）
- 仍需正式 ingestion contract 和 parquet/cache 产物，不允许直接实现 funding factors。

---

## B. Bars Schema 结论

| Dataset | Path | Rows | Symbols | Timestamp Range | Taker Fields |
|---------|------|------|---------|-----------------|--------------|
| static | `data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet` | 215,061 | 50 | 2025-12-15 → 2026-06-13 | 缺失 |
| dynamic | `data/cache/.../bars_1h.parquet` | 3,316,259 | 266 | 2024-06-01 → 2026-06-13 | 缺失 |

真实字段：timestamp, bar_open_time, bar_close_time, symbol, open, high, low, close, volume, quote_volume, trade_count, source, market, instrument_type, timeframe

缺失字段：taker_buy_volume, taker_buy_quote_volume。原始 klines 有这些字段，但 bars cache 未包含。

---

## C. Taker Imbalance 数据契约

### 推荐口径：Quote-volume taker ratio

```text
taker_buy_ratio = taker_buy_quote_volume / quote_volume
```

理由：

- `quote_volume` 已经存在于 bars cache。
- `taker_buy_quote_volume` 是 Binance kline 原生字段。
- quote-volume 口径比 base-volume 口径更贴近成交额主导的横截面资金压力。

但是：

- 当前 bars cache 缺少 `taker_buy_quote_volume`。
- 因此 Phase 7L 不应直接实现 taker factors。
- 下一步应先生成 enriched bars cache 或 canonical taker cache。

### Base-volume 口径暂不优先

```text
taker_buy_ratio = taker_buy_volume / volume
```

该口径也合理，但本项目优先采用 quote-volume，因为已有 quote_volume 相关因子和成交额口径。

### PM 决策

1. 接受 quote-volume taker imbalance 口径。
2. 不接受“直接从现有 bars cache 计算 taker factors”。
3. Phase 7L 应先做 bars schema enrichment / taker cache construction。

---

## D. Funding Rate 数据契约草案

### 原始数据

- 路径：`data/binance_vision_rank154/data/futures/um/monthly/fundingRate/<SYMBOL>/`
- 格式：zip 内含 CSV
- 字段：`calc_time` (ms), `funding_interval_hours`, `last_funding_rate`
- Coverage：679 symbols, 2021-05 → 2026-04
- Top50 覆盖：49/50（仅缺 1000PEPEUSDT）
- Dynamic universe 覆盖：258/266

### known_at 规则

- known_at = calc_time。
- funding rate 在结算时点后才可被认为已知。
- 不允许使用未来 funding 值。

### 1h 对齐方式

```text
方式：merge_asof + backward join + max_age 控制
1. 解压 funding rate 到 canonical parquet/cache。
2. 对每个 symbol 按 calc_time 排序。
3. 对 1h bars 用 merge_asof(direction='backward') 取最近一个已结算 funding rate。
4. max_age = funding_interval_hours，小于等于 8h。
5. 如果超过 max_age 仍无新 funding，填 NaN。
```

### Funding interval 变化处理

- 当前样本显示 interval 固定 8h。
- 代码仍应读取 `funding_interval_hours` 字段。
- 如果未来出现 4h 或 1h，应按每条记录自己的 `funding_interval_hours` 控制 forward-fill 上限。

### 缺失 symbol 处理

- 缺失 symbol 不补值。
- 该 symbol 的 funding factors 保持 NaN。
- 1000PEPEUSDT 缺失可以接受，因为它只影响少数 symbol 覆盖，不应阻塞整个 funding data contract。

---

## E. Phase 7L 建议

Phase 7L 不应实现因子。

Phase 7L 应执行：

```text
Phase 7L — Taker / Funding Canonical Data Cache Construction
```

Phase 7L 目标：

1. enriched bars cache 增加 `taker_buy_quote_volume`。
2. funding rate 原始 zip 转 canonical parquet/cache。
3. 生成 static/dynamic 数据覆盖报告。
4. 不实现任何 factor registry 因子。

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
