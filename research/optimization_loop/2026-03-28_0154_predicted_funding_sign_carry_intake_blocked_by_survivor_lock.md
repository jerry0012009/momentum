# 2026-03-28 01:54 UTC — predicted funding sign carry intake blocked by survivor lock

- target: `research/quant_digests/2026-03-28_0020_predicted-funding-sign-carry-switch-alpha.md`
- action: 在 survivor 动作与上一条 fresh intake 已诚实排入前部后，再对这条 `predicted funding sign -> carry on/off / reverse` 做 fresh intake；重点回答它留下来的是否是可独立 desk 化的 funding-carry timing raw alpha，而不是 always-on carry 的叙事性包装
- success_criterion: 必须对该具体对象产出首轮正式 verdict；若达到 `keep_P1` 或更高，必须同时分配下一个未使用的整数 `Rank`
- status: blocked

## 为什么本轮必须拦下
1. 当前 runtime 里 `Surviving candidate slot` 仍被 `Rank 209 / US close -> crypto synthetic open spillover` 占用，且 `followup_budget_remaining: 1`，说明上一条 fresh intake 还没有完成那唯一一次 survivor follow-up。
2. fixed policy 明确要求：已有前排对象的收口优先级永远高于新的发现；而且任何新的 `keep_P1` fresh intake 都会抢占 survivor 槽位，因此在 `Rank 209` 尚未收口前，继续执行新的 fresh intake 会把 state 推向不合法分叉。
3. 当前 `cycle_plan` 第 3 项自身也写了前置条件：**“在 survivor 动作与上一条 fresh intake 已诚实排入前部后，再对这条……做 fresh intake”**。但本轮 `cycle_plan` 前两项完成后，`Rank 209` 只完成了 fresh intake 首判，并没有完成 survivor follow-up，因此该前置条件并未成立。

## 本轮收口结论
本轮不允许对 `predicted funding sign -> carry on/off / reverse` 执行 fresh intake；`Rank 209` 仍合法占用 survivor 槽位，导致该小点前置条件不成立，因此本项按 policy 收口为 `blocked`，等待后续由 bot2 先把 survivor 收口后再重排。

## 需要写回 runtime 的系统认知
- `cycle_plan` 第 3 项不能继续保持 `pending`：它不是“还没来得及做”，而是**当前 state 下不合法执行**。
- 本轮没有新的 rank、没有新的前排对象、也没有层级迁移；唯一新增事实是：`predicted funding sign carry` 这条 intake 在 `Rank 209` survivor 未收口前必须暂停。
