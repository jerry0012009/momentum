# 2026-03-27 14:03 UTC — dynamic TSMOM fresh intake blocked by survivor lock

## 本轮结论
`research/quant_digests/2026-03-27_1244_dynamic-tsmom-turningpoint-continuation-alpha.md` 本轮**未执行 fresh intake**，因为它在 `cycle_plan` 中的显式前置条件是：**“第 1 项完成且不占用 survivor 锁”**。

但 runtime 当前 truth 已明确：
- `Rank 198 / dynamic cointegration pair-basket spread convergence` 刚在上一小点得到 `keep_P1`；
- `Surviving candidate slot` 现被 `Rank 198` 占用，且 `followup_budget_remaining: 1`；
- policy 明确规定：`Surviving candidate` 只能是上一条 fresh intake，且在其唯一 follow-up 诚实收口前，bot2 不得让另一条新的 `keep_P1` 覆盖该 survivor 槽位。

因此，第 2 项这轮的合法收口不是继续执行，而是直接标记为：
- `status: blocked`
- 原因：`前置条件不成立：survivor lock 仍被 Rank 198 占用，因此这条新的 fresh intake 本轮不能合法前推`

## 为什么不能硬做
这不是研究价值判断，而是 runtime 排班合法性判断。

即使 digest 本身看起来像一条可能值得保留的单资产 dynamic TSMOM raw alpha，本轮也不能绕过当前 front-slot truth 去给它做正式 intake，否则会造成：
1. 新 fresh intake 越过现有 survivor follow-up 锁；
2. `Surviving candidate slot` 不再对应“上一条 fresh intake”；
3. bot3 实际上替 bot2 重排了轮次。

## 对系统认知的实际更新
本轮新增的 runtime truth 是：

> `dynamic-tsmom-turningpoint-continuation-alpha` 这条 fresh intake 在当前轮**不是合法可执行动作**；它被前一条 `Rank 198` 的 survivor lock 明确挡住，应留待 bot2 后续重排或在 survivor 收口后再进入前排。

## 本轮动作范围
- 已读取并遵守 `BOT2_BOT3_POLICY.md` 与 `BOT2_BOT3_STATE.md`
- 仅处理 `cycle_plan` 中当前最前的 `pending` 小点
- 未改写 policy / brief / cron prompt
- 未重排后续小点
- 未对任何对象做层级、rank、槽位升级/降级
