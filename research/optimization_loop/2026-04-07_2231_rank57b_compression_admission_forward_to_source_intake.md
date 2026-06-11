# 2026-04-07 22:31 UTC — Rank 57b / breakout-family-local pre-break compression admission 前推判定

## 本轮执行小点
- target: `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
- action: 判断 `breakout-family-local pre-break compression admission` 是否值得从已 drafted 的 `Rank 57b` 前推成新的 fresh/source-intake 候选
- success_criterion: 只有当最小 breakout 宿主、strict A/B 边界与独立验证口径都已经压清，才允许前推；否则继续停留在 park-reframe 层

## 读到的关键前提
1. 原 `Rank 57` 被 park 的 blocker 已经很清楚：失败的是“`TTM squeeze release` 作为跨 `ema_psar_long / fib_retest_long / breakout_short` 的 shared regime gate”，不是压缩主题整体永远无效。
2. `2026-04-03_0656_rank57-park-reframe.md` 已把唯一诚实修改轴收得很窄：
   - 只保留 `breakout family` 这个宿主；
   - 第一轮只测 `baseline breakout_short` vs `compression-admission`；
   - 不偷带 `200SMA / volume spike / funding / 新 exit` 第二轴。
3. `2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md` 虽然没有把 standalone breakout body 直接做成正 alpha，但它已经提供了足够清楚的外部旁证：
   - “先压缩、后突破”本身是可独立定义、可公开复现、可 A/B 的 breakout 语义；
   - 更诚实的角色不是直接升成 standalone raw alpha，而是降级成 breakout 家族里的 participation / admission layer。

## 本轮判断
### 1) 宿主 setup 已经压清
这条线现在不再试图服务多个 setup，而是只附着在 `breakout_short` 这一条 breakout-family 宿主上。宿主不再含糊，因此满足“最小 breakout 宿主”条件。

### 2) strict A/B 边界已足够清楚
当前 draft 已明确规定：
- A 组：`baseline breakout_short`
- B 组：`pre-break compression admission`
- 不允许顺手叠 `200SMA / volume / funding / 新 exit`
- 必须报告 `trade retention`

这已经把“到底测什么、不能偷偷多带什么”压成了一个单轴实验，而不是宽泛的 squeeze 主题复活。

### 3) 独立验证口径也已够前推
虽然这一步还没有进入 fresh intake 正式实验，但验证问题已经是独立、可执行、且 reader-facing 可解释的：
- 问的不是 `TTM squeeze` 能不能当 shared gate；
- 问的是：**在 breakout_short 宿主里，pre-break compression admission 是否能比 baseline 更诚实地改善 post-cost 表现，而不是只靠大幅砍样本少亏。**

这说明它已经具备新对象应有的独立职责，而不再只是旧 Rank 57 的失败注脚。

## 为什么这轮可以前推、但不是直接给更高层 verdict
- 可以前推：因为对象边界、宿主、A/B 与验证口径都已成型，足以作为新的 `fresh/source-intake` 问题进入队列。
- 不能直接给 `keep_P1 / P2`：因为当前还没有这条窄版 admission 在同口径 clean-room 下的正式 first verdict，不能跳过 source-intake / intake 这一步。

## 结论
**`Rank 57b` 值得从 `derived_hypothesis_drafted` 前推成新的 `fresh/source-intake` 候选。**

翻成人话：
不是说旧的 `TTM squeeze release` 被救活了；而是说它被审计失败后，留下来的那一点残余已经被收窄到足够像一个新的、可单独发问的小对象：
**`breakout_short` 是否应只在 pre-break 明确压缩时才放行。**

## 对 runtime 的影响
- 本轮将 `cycle_plan` 第 3 项收口为 `done`
- `result` 写回：`Rank 57b` 已把 breakout 宿主、strict A/B 边界与独立验证口径压清，值得从 park-reframe 层前推为新的 fresh/source-intake 候选；但当前尚未进入正式 front-slot，也未拿到 fresh first verdict。
- 不改写 policy，不重排当前 cycle_plan 的其余顺序

## 一句话结果
`Rank 57b` 不应继续停留在“只是 drafted note”；它已经够具体，应该在后续合法轮次里作为新的 fresh/source-intake 候选被正式前推。