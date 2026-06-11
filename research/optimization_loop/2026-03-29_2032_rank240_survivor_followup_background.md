# Rank 240 / stablecoin depeg jump-risk shared overlay — survivor follow-up exhausted -> background

- 时间：2026-03-29 20:32 UTC
- 轮次角色：bot3 auto executor
- 对应 cycle_plan 小点：`Rank 240 / stablecoin depeg jump-risk shared overlay`
- 前置记录：`research/optimization_loop/2026-03-29_1630_rank240_stablecoin_depeg_jump_risk_overlay_keep_p1.md`
- 结论：`survivor follow-up exhausted -> background/P0`

## 这一步回答的问题
把 `Rank 240` 的 survivor follow-up 收口成一个是/否判断：在冻结 `downward-only depeg threshold + 30m/60m overlay window` 之后，这条 overlay 是否已经对至少一类现有短周期策略留下了清楚的 `with overlay vs without overlay` 净改进，而不是只靠大面积 veto 把交易砍掉。

## 本轮采用的最小 decisive 口径
这一步没有再发明新 proxy，也没有把论文里的 jump/cojump 结果硬包装成策略级 admission 通过；只检查当前权威材料里，是否已经存在足以支撑升级的策略级 A/B 证据。

本轮直接依赖的已知事实只有两条：
1. `research/quant_digests/2026-03-29_1458_usdt-depeg-jump-risk-shared-overlay.md`
   - 已明确冻结了最小可测骨架：`downward-only`、`0.3%/0.5%/1.0%` depeg threshold、`15m/30m/60m` overlay window；
   - 论文证据只证明 `USDT depeg -> 未来 5m~60m jump/cojump risk 显著抬升`。
2. `research/optimization_loop/2026-03-29_1630_rank240_stablecoin_depeg_jump_risk_overlay_keep_p1.md`
   - 已明确写过：下一轮若要升 `P2`，必须回答至少一类现有 `MR / pairs / carry / breakout` 在 `with overlay vs without overlay` 下是否留下策略级净增量；
   - 若改善主要来自大面积 veto、只在单一 pocket 成立、或根本还没有策略级 A/B，就不得继续 `keep_P1`。

## 结果
### 1) 现有证据仍然停留在 regime/jump-risk 层，不是策略级 A/B
当前材料能诚实支持的最强命题仍然只是：

> `downward USDT depeg -> 未来 30m/60m jump-risk + cojump-risk 抬升`

这足以说明它是一个值得考虑的 shared stress flag，**但还不等于**：
- `MR / pairs` 接上它之后净亏损变少；
- `carry` 接上它之后 post-cost pnl / drawdown 明显改善；
- `breakout/event` 在保留交易数的前提下 expectancy 变好。

也就是说，**这轮并没有出现任何已落库的、可复查的 `with overlay vs without overlay` 策略级结果**。

### 2) 在没有策略级 A/B 前，把它升 P2 只会变成“靠 veto 伪装成改进”
`Rank 240` 的动作定义天生偏向：
- veto 新开仓；
- size-down；
- tightening admission。

这类 overlay 如果没有对现有策略的净效果对照，很容易出现一种假改进：
- 看起来 tail 风险下降了；
- 实际只是交易被大面积砍掉，alpha 也一起被砍没了。

而本轮 success criterion 明确要求：
- 必须区分“少做亏损单”和“只是把交易大面积砍掉”；
- 若没有留下清楚的策略级净增量，就要收口到 `background/P0`。

### 3) 因此，本轮更诚实的结论不是 keep_P1，也不是 promote_P2，而是预算用尽后回 background
`Rank 240` 的首判价值已经被保留过一次：
- 它不是泛泛稳定币新闻；
- 它确实定义了一个边界清楚的 shared stress overlay 主语。

但 survivor 那唯一一次 follow-up 本来就该回答更硬的问题：

> **这条 overlay 接到现有短周期策略后，是否真的留下了策略级净增量？**

当前答案只能是：**还没有。**
而且这种“还没有”并不是一个适合继续开放式续命的缺口，因为它正好卡在最关键的 admission 边界——没有这一步，就无法证明它不是靠广泛 veto 假装有价值。

## hard verdict
- **`Rank 240 / stablecoin depeg jump-risk shared overlay`：survivor follow-up exhausted，回 `background/P0`**
- 不升 `P2`
- 不允许继续 `keep_P1`

## runtime 结论
- `Surviving candidate slot` 应清空为 `none`
- `followup_budget_remaining` 归零/收口
- `Background pool.latest_parked` 改写为本轮结论
- `cycle_plan` 第 1 项写成 `done`

## 一句话结果（用于 state/result）
`Rank 240` 的唯一 survivor follow-up 已收口：现有证据只证明 `downward USDT depeg -> 30m/60m jump-risk / cojump-risk` 是值得关注的 shared stress flag，却还没有任何已落库的 `with overlay vs without overlay` 策略级净增量来证明它不是靠大面积 veto 假装变好，因此按预算用尽后回 `background/P0`。
