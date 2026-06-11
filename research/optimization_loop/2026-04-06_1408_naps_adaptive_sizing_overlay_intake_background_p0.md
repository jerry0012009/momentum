# NAPS adaptive sizing overlay fresh intake -> background / P0

- 时间：2026-04-06 14:08 UTC
- 对象：`research/quant_digests/2026-04-06_1302_naps-adaptive-sizing-overlay.md`
- 动作：fresh intake first verdict
- 结论：`NAPS adaptive sizing` 只能诚实定位为服务既有 raw alpha 的 shared sizing / risk overlay，不构成可单独排入前排 survivor 的独立可交易主语，因此本轮直接归档 `background / P0`，不占用前排 fresh / survivor 资源。

## 为什么不保留为独立前排对象

1. **没有独立 raw alpha 主语**
   - digest 已明确写明：`基础 alpha：无独立 raw alpha`
   - 该对象回答的是“已有信号在不同 uncertainty / risk-state 下该下多大”，不是“何时进场/出场”的独立 alpha 命题。

2. **可复现的是 sizing layer，不是 entry/exit strategy**
   - 可独立复现的是 `score × uncertainty × risk-state -> size fraction` 映射。
   - 这类组件应作为共享仓位层/风控层挂接到已有策略，而不是作为新的独立策略 rank 候选。

3. **对 desk 有价值，但价值形态是 shared component**
   - 它对 trend / breakout / mean reversion / carry / XS 等多个既有 raw alpha 都可能有帮助。
   - 这意味着它更像全池通用的 capital allocation / sizing enhancement，而不是应该占用 survivor follow-up 配额的单一新策略。

## 对 runtime 的影响

- 不分配 Rank。
- 不进入 `Surviving candidate slot`。
- 归入 `Background pool`，后续若要使用，应在具体已存活 raw alpha 上以 `NAPS-lite sizing overlay` 形式做组件级集成测试，而不是把它当成单独 fresh intake 主线继续推进。

## 一句话 result

`NAPS adaptive sizing` 提供的是可复用的 shared sizing overlay，而非独立可交易 raw alpha；本轮直接归档 `background / P0`。