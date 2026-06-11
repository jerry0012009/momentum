# 2026-03-31 14:28 UTC — asynchronous funding clock carry intake blocked by survivor lock

- target: `research/quant_digests/2026-03-31_1302_async-funding-clock-carry-alpha.md`
- action: 若前两条已在本轮前部被诚实排入，再把 `asynchronous funding clock × net-hour hurdle` 作为第三条具体 fresh intake；只允许回答它是否形成可审计的 cross-venue carry raw alpha，不得把静态 funding diff 直接当作可交易净边
- success_criterion: 必须给出明确 first verdict：若该对象已具备统一时钟、future holding-window carry、entry/exit、执行与成本骨架，则写成新的 fresh intake 并给出 `keep_P1 / P2 / P0` 首判；若当前 live sanity check 只支持 pocket carry、不支持诚实落地，则明确写成 `不进入前排，回 background/P0`
- status: `blocked`

## 为什么本项本轮不能继续执行

本轮先读固定 policy 与 runtime state 后，发现当前仍存在合法且未收口的 survivor：

- `Surviving candidate slot = Rank 268 / moving-band basket stat-arb × 线性 inventory shell`
- `followup_budget_remaining = 1`
- 最新状态已明确写出唯一应做的下一步：**直接验证受控 crypto universe 下 after-cost replication 是否成立**

按 `docs/BOT2_BOT3_POLICY.md`：

1. **已有前排对象的收口，优先级永远高于新的发现。**
2. 只要当前存在合法 `Surviving candidate` 动作，bot2 / bot3 就不应继续把新的 `fresh intake` 往前排推进。
3. 若当前 `state` 与 `policy` 冲突，bot3 应拒绝执行歪路径，回退到合法动作。

因此，尽管 `cycle_plan` 的第 3 个 pending 小点指向新的 `asynchronous funding clock × net-hour hurdle` intake，本轮最诚实的执行不是给它新 verdict，而是先承认：**在 `Rank 268` 的 survivor 唯一 follow-up 没有被 bot2 先收口前，这条新 intake 不具备合法前排执行条件。**

## 本轮改变系统认知的一句话

**当前前排仍被 `Rank 268` 的 survivor 唯一 follow-up 合法占用，因此 `asynchronous funding clock × net-hour hurdle` 这条新 fresh intake 本轮不能继续进入前排，必须先等待 bot2 重排或先收口 survivor。**

## 结果回写要求

- 本项 `status` 应写为 `blocked`
- 本项 `result` 不应写成新的 alpha verdict，而应写成前排锁仍然生效的 runtime 事实
- 不分配新 `Rank`
- 不改写 policy / brief / operating card / auto loop / cron prompt
