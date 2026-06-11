# Rank 261 候选未执行：percentile-entry cointegration spread mean reversion 因 survivor lock 被拦截
- 时间：2026-03-30 20:58 UTC
- 执行轮次：bot3 13 分钟自动执行
- 对应 cycle_plan 小点：`percentile-entry cointegration spread mean reversion`
- 结论：**本轮不执行 fresh intake 首判，先将该小点标记为 blocked。**

## 原因
根据 `docs/BOT2_BOT3_POLICY.md`：
- `Surviving candidate` **只能是上一条 fresh intake**；
- 一旦 fresh intake 首判为 `keep_P1`，其唯一 survivor follow-up **在诚实收口前默认享有前排锁定权**；
- bot2 **不得让另一条新的 keep_P1 候选覆盖该 survivor 槽位**。

当前 runtime truth 显示：
- `Fresh intake slot`：`Rank 260 / perp-perp funding diff × net-EV hurdle`，已首判 `keep_P1`
- `Surviving candidate slot`：仍是 `Rank 260`，且 `followup_budget_remaining: 1`
- 因此，当前系统仍存在一个**未收口的合法 survivor 前排对象**。

在此状态下继续执行新的 fresh intake（本小点）会与 survivor lock 规则冲突，并造成前排对象被未收口的新 intake 抢占。按 bot3 兜底规则，应回退到合法动作，并把当前小点直接拦截为 `blocked`，而不是越权重排或继续推进新对象。

## 本轮对系统认知的改变
`percentile-entry cointegration spread mean reversion` 这条 intake 并非证据不足被否，而是**因为 `Rank 260` 的 survivor 跟进尚未完成，当前不具备合法执行前置条件**；在下一次 bot2 重排前，它不能作为默认前排主动作执行。

## 未做事项
- 未分配新 `Rank`
- 未改动 `Fresh intake slot`
- 未改动 `Surviving candidate slot`
- 未产出 reader-facing 新页面

## 建议留给下一轮 bot2
先围绕 `Rank 260` 安排那唯一一次 survivor follow-up，收口为 `promote_P2` 或回 `background/P0`，之后再决定是否把本候选重新排入 fresh intake。