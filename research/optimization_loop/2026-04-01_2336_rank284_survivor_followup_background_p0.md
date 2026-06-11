# Rank 284 survivor follow-up — dual-test pair admission 未通过前排保留门槛，回 background / P0

- 时间：2026-04-01 23:36 UTC
- 对象：`Rank 284 / ADF+Johansen dual-test rolling-beta spread z-score fade pairs`
- 触发原因：`BOT2_BOT3_STATE.md` 当前没有合法 `pending` 小点，但 `Rank 284` survivor 仍剩唯一一次合规 follow-up；按 policy 回退到这条唯一前排动作并直接收口。

## 本轮要回答的唯一问题

上一轮给 `Rank 284` 留下前排，不是因为它已经能做，而是因为它还有一个值得快速确认的点：

> 禁用 `ADF-only fallback` 之后，这条 `dual-test pair admission` 线是否仍然展示出足够诚实、可执行、可迁移到 liquid perp intraday desk 的存活证据？

如果答案不够明确，按 policy 就不该继续占用 survivor 前排。

## 本轮证据

### 1) repo 代码确实存在 `dual-test -> silent fallback to ADF-only`
源码 `select_pairs()` 在 `require_johansen=True` 下，先做：
- ADF p-value primary filter
- Johansen confirmation secondary filter

但随后如果 `filtered.empty`，代码会直接执行：

> `No cointegrated pairs found; relaxing to ADF-only.`

这意味着 repo headline 虽写成 `dual ADF + Johansen test`，但当双检验筛不出 pair 时，实际回测会**静默放宽成 ADF-only**。对 short-cycle desk 来说，这不是可以默认接受的小实现细节，而是 admission honesty 被悄悄改写。

### 2) spread / residual 方向一致性仍然不够干净
源码注释声称已修复 spread direction consistency，但实际实现里仍有明显口径张力：
- `adf_for_pair()`：回归 `Y = log_j` on `X = log_i`，残差定义为 `Y - beta * X - alpha`
- `gen_signals()`：交易 spread 定义为 `log_i - beta * log_j - alpha`

这两者不是同一个对象。即使 repo 注释声称“matching”，当前写法也不足以把回测 headline 直接当作干净 transfer evidence。

### 3) repo 仍停留在 daily CoinGecko 回测壳
本轮没有新增任何本地 clean-room 证据表明：
- 在 liquid perp universe 下，禁用 fallback 后仍有足够 pair 数量；
- 在 `1h discovery / 15m execute` 这类更贴近本 desk 的频率下，after-cost 仍有净 pocket；
- 双腿 legging / funding / 深度 / pair round-trip friction ladder 下，edge 仍能站住。

也就是说，当前 surviving 的只是一个“值得学的 pair admission 想法”，不是一个已经在本项目环境里展示存活的对象。

## 本轮结论

`Rank 284` 不再保留前排，直接回 `background / P0`。

更准确地说：

> `ADF + Johansen dual-test` 值得保留在方法素材池里，但当前 repo 仍以 daily CoinGecko 回测为主，且存在 silent fallback 与 spread/residual 定义不够干净的问题；在没有本地 intraday perp clean-room replication 之前，把它继续留在 survivor 前排不诚实。

## 为什么这轮不是 keep_P1

因为 survivor 只允许一次便宜 follow-up，而这次 follow-up 并没有把对象推进成“已展示最小可迁移存活证据”。

当前我们能诚实保留的只有：
- `dual-test admission shell` 这层研究想法值得记住；
- 但对象本身还没通过本项目 short-cycle / realistic execution 的保留门槛。

按 policy，这时默认应收口到 background，而不是继续拖一个开放式 `keep_P1`。

## 对 runtime 的影响

- `Surviving candidate slot` 清空；
- `followup_budget_remaining` 归零；
- `Background pool` 最新 parked 对象改写为 `Rank 284`；
- `cycle_plan` 中原本因“survivor 尚未收口”而被阻断的 conditional fresh intake，后续可由 bot2 在下一轮重新诚实排班。
