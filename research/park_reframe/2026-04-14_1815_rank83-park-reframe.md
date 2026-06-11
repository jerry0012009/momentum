# Rank 83 park reframe review

- 时间：2026-04-14 18:15 UTC
- 对象：`Rank 83 / Fib trend-strength admission layer`
- 本轮结论：`keep_park`
- 原 `park` verdict：保留，不推翻

## 本轮先读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-14_1553_rank67-park-reframe.md`
- `research/park_reframe/2026-04-10_1516_rank74-park-reframe.md`
- `research/park_reframe/2026-04-06_1313_rank83-park-reframe.md`
- `research/optimization_loop/2026-03-19_0826_rank83-cost-stability-park.md`
- `research/optimization_loop/2026-04-08_1151_rank83_fresh_intake_first_verdict_background_sync.md`

## 1. 原 rank 为什么 park？
原始 `Rank 83` 被压回 `park`，不是因为 Fib 回踩主题完全没信息，而是因为它把“回踩后确认强弱”写成了一个 **`weak / medium / strong` 多档 admission / sizing layer**，这层职责没有站住。

关键 blocker 已在 2026-03-19 的 clean replication + cost stability 中审计清楚：
- `base_binary` 明显为负，说明“只要 retest_hold 就放行”的粗写法不成立；
- 真正留下正贡献的只剩 `strong` 桶，`medium` 桶本身还是坏 pocket；
- 到更诚实 friction 后，这条线从 `6bps` 的正收益，掉到 `10bps` 只剩很薄，再到 `15bps` 已经 `0/3` 全部翻负。

所以原 park 的核心不是“Fib family 彻底死”，而是：
**`多档 strength admission / sizing` 这层旧 Rank 83 写法，没有证明自己是可 queue-facing 的独立 rank。**

## 2. 它更像 hard park 还是 soft park？
本轮判断：**`soft park`，但比 4 月 6 日那轮更接近 hard。**

原因：
- 若只看原始 Rank 83 本体，它已经很接近 hard park；
- 唯一 residual 仍只剩 `strong-only` 这条窄确认轴；
- 但这条 residual 又在 2026-04-08 的 fresh intake first verdict 中被正式收口为 `background / P0`，说明它没有长成独立 raw alpha intake。

换句话说：
- 对旧 Rank 83 的多档 strength framework：几乎已是 hard park；
- 对“Fib lane 内也许只保留 very-strong confirm”这条残余：仍可记为 soft residual，但**已被 runtime 消费并压回 background**。

## 3. 有没有“可救信号”？
有，但已经很薄，而且已被消费。

唯一可救信号仍是：
- `strong` 桶持续优于 `medium` / `weak`；
- 更诚实的语言不是“多档强弱分层”，而是“只有足够强的 reclaim / follow-through 才算 continuation confirm”。

但这条信号的问题也已非常清楚：
1. 它不再属于 Rank 83 原来的多档框架；
2. 它与既有 `Fib reclaim / second-chance confirmation` 家族高度重叠；
3. 2026-04-08 的 first verdict 已明确：这条 `strong-only Fib binary confirm` residual **没有压出独立 pocket、独立执行边界、独立 clean-room 主语**，因此只够回到 `background / P0`。

所以本轮的答案是：
- **有可救信号，但不是“还能再派生一个 Rank 83b”的那种可救。**

## 4. 最值得改的唯一一刀是什么？
若只讨论“唯一值得改的一刀”，仍然只有这一条：

> **把 `weak / medium / strong` 多档 Fib trend-strength admission / sizing，收窄成 `strong-only` 的 binary continuation confirm。**

但这条“一刀”本轮不值得再 draft，原因是：
- 它已经在 4 月 8 日被当作 fresh intake 试过一次；
- 试后的正式结论不是 `keep_P1`，而是 `background / P0`；
- 说明这条 residual 只够作为家族内确认轴，不足以保持 queue-facing 独立性。

## 5. 是否值得形成新的 derived hypothesis？
**不值得。结论是 `keep_park`。**

原因：
- 原 rank 的 blocker 没有被推翻；
- 唯一诚实 residual 仍只是既有那条 `strong-only` 窄确认；
- 而这条 residual 已在 2026-04-08 first verdict 中被 runtime truth 收口为 `background / P0`；
- 现在若再写一个新的 `Rank 83b`，大概率只是把“强确认更好”换壳重讲，不是新的独立单轴。

## 6. trade on / trade off（仅做 why-not-draft 说明）
本轮不 draft 新假设；但可以记录 why-not-draft：
- trade on：承认 Fib family 的残余信息只留在 very-strong confirm，而不在多档 strength framework；
- trade off：`Rank 83` 失去作为独立 queue-facing residual 的必要性，剩余信息被并入既有 Fib reclaim / second-chance confirmation 家族，而不是保留为新的 rank 编号。

## 7. 本轮结论摘要
- 原 rank 为什么 park：多档 `Fib trend-strength` admission / sizing 在更诚实 friction 下不稳定，真正正贡献只剩 `strong` 桶。
- 更像 hard 还是 soft：`soft park`，但已明显继续向 hard 靠。
- 有没有可救信号：有，但只剩 `strong-only` 窄确认，而且已在 4 月 8 日被 first verdict 压回 `background / P0`。
- 最值得改的唯一一刀：把多档强弱分层收窄成 `strong-only` binary confirm。
- 是否值得形成新的 derived hypothesis：**否**。

## Final verdict
**`keep_park`**

## 对 queue 的更新口径
- 仅在 `docs/PARK_REFRAME_QUEUE.md` 与 `research/park_reframe/INDEX.md` 追加本轮记录；
- 不改 `docs/TODO.md` 顶部排班；
- 不新增 `Rank 83b`。

## Git / 提交
- 本轮只做最小必要文档更新。
- 未做 commit；默认避免把共享工作区其他脏文件混入。
