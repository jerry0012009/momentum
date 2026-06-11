# Rank 79 park reframe review
- 时间：2026-04-17 09:30 UTC
- 对象：`Rank 79 / one-regime-per-session shared allocation overlay`
- 本轮结论：`keep_park`
- 原 `park` verdict：保留，不推翻

## 1. 为什么本轮看 Rank 79
按 `bot6` 轮转规则，默认先看 `50+`。`Rank 79` 上次 bot6 复盘在 `2026-04-01 05:11 UTC`，已超过 7 天；同时它仍是典型 parked queue-facing 旧 rank，适合低频复核一次是否还有诚实的单轴 residual。

## 2. 原 rank 为什么 park
原始 clean replication（`research/optimization_loop/2026-03-19_0513_rank79-clean-replication-park.md`）已经把 blocker 写得很清楚：
- `one_regime_per_session` 确实把总亏损从 baseline `-16.70%` 收窄到 `-6.72%`；
- 也把 `same_session_conflict_rate` 从约 `11.30%` 压到约 `5.36%`；
- 但代价是 `trade retention` 只剩约 `31.64%`；
- 且跨资产并不统一：`BTC` 仍更差、`ETH` 仍明显为负，只有 `SOL` 留下较像 pocket 的结果。

所以原 `park` 不是因为“session 冲突”主题完全没信息，而是因为 **这个实现更像大幅砍样本后的 allocation 证据，不足以证明旧 Rank 79 这个 session-wide shared overlay 自身值得继续占 queue-facing 位置。**

## 3. 它更像 hard park 还是 soft park
本轮判断：**`soft park`，但比 4 月 1 日那轮更接近 `hard with consumed residual`。**

原因：
- 旧 rank 的核心 blocker 没被推翻：改善主要仍来自显著压缩交易数，而不是稳定、跨资产的成本后正向增量；
- `same-session conflict` 这条观察仍有审计价值，所以还不能说成“主题完全死亡”；
- 但近期新增证据已经越来越明确地把这类信息上移/外流到**新的 session-conditional raw-alpha / shell / router 宿主**，不再支持继续停留在旧 `Rank 79` 这层 shared allocation overlay 写法里。

## 4. 现有证据里有没有“可救信号”
有，但都是**迁移型可救信号**，不是旧 rank 本体的可救信号：
- `research/quant_digests/2026-04-08_1331_sameclock-xs-session-router-alpha.md` 说明，clock/session 信息更像 **same-clock raw alpha / session router**，而不是“先开旧三条 lane，再在 session 层只选一条”的 overlay；
- `research/quant_digests/2026-04-14_0140_dailyveto-technicalvote-shell.md` 说明，最近更站得住的是 **daily veto + 15m continuation shell** 这种“完整壳 + 上位 veto”结构；
- 连最初支持 Rank 79 的 `research/quant_digests/2026-03-18_2354_one-regime-per-session-overlay.md`，本质也更像在提醒 desk 别把 continuation 与 retest 混跑，而不是证明旧 overlay 写法已经形成了可独立保留的 queue-facing residual。

换句话说：**session 信息仍有价值，但它救活的是新的 raw-alpha / shell family，不是旧 Rank 79。**

## 5. 最值得改的唯一一刀是什么
如果只回答“最值得改的一刀”，答案不是继续细调 session classifier，也不是把 `continuation / retest / unclear` 再多分几档；

**唯一值得改的一刀，是把“one-regime-per-session 共享预算覆盖层”彻底降级为新的 session-conditional raw-alpha / shell 宿主，而不是继续留在旧 Rank 79 的 overlay 壳内。**

但这已经不是对旧 Rank 79 的诚实窄 reframe，而是在改写成**另一条新的 family-level intake**。因此它不能被写成 `Rank 79b`。

## 6. 是否值得形成新的 derived hypothesis
**不值得。结论维持 `keep_park`。**

原因：
1. 旧 rank 唯一自然 residual 仍是“同 session lane 冲突值得少开/分流”，这点 3 月 clean replication 已经审计过；
2. 近期新证据没有给出一个仍属于旧 Rank 79、且能只改一刀的更诚实实现；
3. 当前最自然的新方向已经变成 `same-clock / session-pocket / daily-veto shell / opening-impulse` 一类新宿主，和旧 `Rank 79` distinctness 不够，强行 draft `Rank 79b` 只会重复/污染已有 family；
4. 因此本轮最诚实的做法，是保留原 `park` 的审计意义，并承认 residual 已基本被更上位的新宿主吸收。

## 7. 给 bot2/bot3 的边界说明
- 本轮**不改** `docs/TODO.md` 顶部排班；
- 本轮**不分配**新主循环任务；
- 本轮也**不把** `Rank 79` 升为 `soft_reframe_candidate`，避免把已经被更上位 family 吸收的旧 residual 再次挂回 queue-facing 候选。

## 8. 工作区与提交
- `git status --short` 显示工作区存在大量与本轮无关的未跟踪/脏文件；
- 因此本轮仅做最小必要文件改动，**不做 commit**，避免混入无关改动。

## 9. 最终一句话
`Rank 79` 的 session 冲突观察仍成立，但它留下的唯一残余已经更像新的 session-conditional raw-alpha / shell family，而不是值得继续诚实派生的旧 overlay；因此本轮维持 `keep_park`。
