# Rank 370 — Active P2 admission step1（post-cost有效性 + stale-quote 最小诚实检查）

- Time: 2026-04-10 09:04 UTC
- Cycle step: `cycle_plan` #1（本轮唯一执行小点）
- Target: `Rank 370 / same-event strike surface mispricing × fair-value recross / time-stop`

## 本轮执行
按 policy 仅执行 `Active P2 admission` 第 1 步，覆盖两件事：

1. **post-cost 有效性最小复核（effectiveness）**
   - 复核 `marketlens-python` README 的 backtest 执行参数：`fees="polymarket"`、`latency_ms`、`slippage_bps`、`max_fill_fraction`、`queue_position`（可打开队列成交仿真），说明该策略壳不是“纯无成本 mid 幻觉”默认设定。
   - 复核 `examples/backtest_surface.py`：核心 alpha 仍是 `fitted_prob - raw_prob > edge` 的同事件多 strike 曲面错价回归，不是方向预测替代。

2. **honesty 最小阻断检查（stale-quote 依赖）**
   - 复核 `src/marketlens/helpers/surface.py` 的 `_scan_books`：会过滤缺失/极端 midpoint，并用 `book.as_of` 聚合 `computed_at`，但**没有内建 quote-age 上限 veto**。
   - 结论：存在 stale-quote 风险窗口，但当前可由执行层显式加入 `max_quote_age`/`age bucket veto` 收敛；尚未形成“单一且立即致命”的 blocker。

## 结论（会改变系统认知）
`Rank 370` 在最小 post-cost 口径下仍保留可交易 edge，且本轮 stale-quote 子检查未发现必须立即打回 `P0` 的单一 decisive honesty/execution blocker；因此该对象本轮**可出队进入 `P2 exit decision`**。

## 状态变更
- `Active P2 slot`: 保持 `Rank 370`
- `p2_rounds_since_level_change`: `0 -> 1`
- `p2_last_evidence_axis`: `effectiveness_postcost_plus_stale_quote_dependency`
- `cycle_plan` #1: `status -> done`
- `cycle_plan` #1 `result`: 已写为“post-cost edge 仍成立，进入 P2 exit decision”

## 备注
- 本轮未触发层级迁移（仍在 `P2`），也未触发 `p2_consecutive_keep_p2` 计数变化。
- 下一步应按既定 `cycle_plan` #2 直接执行 `P2 exit decision` 三选一收口。