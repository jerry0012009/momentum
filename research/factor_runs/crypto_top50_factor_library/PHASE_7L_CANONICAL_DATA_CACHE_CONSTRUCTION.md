# Phase 7L — Taker / Funding 标准化数据缓存构建

> 日期：2026-06-14
>
> 状态：COMPLETE

---

## A. Scope

- Phase 7L: canonical data cache construction
- 构建 taker enriched bars + funding rate events + funding rate 1h aligned
- No factor implementation
- No factor_values build
- No evaluation/backtest

---

## B. Taker Enriched Bars 结果

| 项目 | Static | Dynamic |
|------|--------|---------|
| 是否生成 | ✅ | ✅ |
| 输出路径 | `data/cache/crypto_top50_usdt_perp_1h_taker_enriched/bars_1h.parquet` | `data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_taker_enriched/bars_1h.parquet` |
| 行数匹配原始 bars | ✅ 215,061 = 215,061 | ✅ 3,316,259 = 3,316,259 |
| symbol 数 | 50 | 266 |
| taker_buy_quote_volume 覆盖率 | 75.82% | 91.73% |
| taker_buy_volume 覆盖率 | 75.82% | 91.73% |
| schema_status | PASS | PASS |

**覆盖率说明：** 早期月份（2021-Q4 到 2022-Q1）的原始 klines 使用不同 schema，不包含 taker 字段，这些行填 NaN。Dynamic 覆盖率更高因为更多 symbol 是后来上线的。

**结论：** 可支持 quote-volume taker imbalance 因子计算。

---

## C. Funding Events 结果

| 项目 | 值 |
|------|-----|
| 是否生成 | ✅ |
| 输出路径 | `data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_events.parquet` |
| symbol 数 | 679 |
| event 数 | 2,098,808 |
| 时间范围 | 2021-05-01 → 2026-04-30 |
| interval_values | [1, 2, 4, 8] |
| known_at 规则 | known_at = calc_time |
| schema_status | PASS |

**重要发现：** 存在 4 种 funding interval（1h, 2h, 4h, 8h），不仅限于 8h。alignment 已按各自 interval 做 max_age 过滤。

---

## D. Funding 1h Alignment 结果

| 项目 | Static | Dynamic |
|------|--------|---------|
| 是否生成 | ✅ | ✅ |
| 输出路径 | `...funding_rate_1h_aligned_static.parquet` | `...funding_rate_1h_aligned_dynamic.parquet` |
| 行数匹配 bars | ✅ 215,061 = 215,061 | ✅ 3,316,259 = 3,316,259 |
| symbol 覆盖 | 49/50 (98%) | 258/266 (97%) |
| funding_rate 覆盖 | 74.29% | 88.03% |
| median funding age | 3.00h | 2.00h |
| max funding age | 8.00h | 8.00h |
| schema_status | PASS | PASS |

**alignment 规则：** merge_asof(direction='backward')，max_age = funding_interval_hours。age 超限的填 NaN。缺失 symbol 全部 NaN。

---

## E. Phase 7M 建议

```
Phase 7M can implement taker imbalance and funding_rate factors.
```

两个数据缓存均 PASS，taker 和 funding 均可进入因子实现阶段。

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
