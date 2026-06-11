# 2026-04-03 15:51 UTC · Rank 87 park reframe

## Selected rank
- `Rank 87`
- selection note: 本轮继续按 `50~79 -> 80~110 -> 1~24 -> 25~49` 的低频轮转处理 parked rank。最近几轮已覆盖 `50~79`（如 `Rank 62 / 57`）、`80~110`（`Rank 103`）与低号段，因此这轮回到 `80~110` 内尚未在最近 7 天被 bot6 单独复盘的旧 parked 条目；`Rank 87` 符合条件，且其主题（volume-clock / pseudo-open continuation）刚好有一条 2026-04-03 新 digest 可用于判断：这是在救旧 rank，还是其实已经外流成新的 raw-alpha family。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-19_1102_rank87-volume-clock-intake.md`
- `research/optimization_loop/2026-03-19_1126_rank87-clean-replication-park.md`

原 `Rank 87` 被 park 的原因没有变：它把 **volume-clock + CS spread interaction** 写成三条 base setup（`ema_psar_long / fib_retest_long / breakout_short`）共用的 shared allow/deny gate，但最小 clean replication 证明，这条 shared gate 的改善主要来自**极端砍样本**，不是形成足够厚、足够稳的可部署 residual。

冻结版关键结果（`BTC/ETH/SOL 120d 15m`, `next-bar open`, `no-overlap`, `hold 8 bars`, `6bps/side`）：
- `baseline ≈ -28.85%`
- `fixed_clock_gate ≈ -5.73%`, `trade_count_retention ≈ 8.22%`
- `volume_clock_gate ≈ -0.67%`, `trade_count_retention ≈ 3.42%`
- `positive_asset_ratio` 三臂都只有 `1/3`

翻成人话：
- `volume_clock_gate` 的方向并非完全错，确实比 `baseline` 少亏很多；
- 但它少亏的方式主要是把样本切到几乎只剩边角料；
- 因而原 `park` 的审计意义必须保留：**失败对象是“把 volume-clock + spread interaction 写成 15m shared continuation gate”这件事，不是 volume-clock / 首 30m 冲击主题整体死亡。**

## Hard park or soft park?
- 本轮判断：`soft park，但已明显偏硬`

为什么不是 hard park：
1. clean replication 里 `volume_clock_gate` 相比 `fixed_clock_gate` 与 `baseline` 的确留下了方向正确的残余；
2. 它至少证明“真实成交时钟比固定 funding-style 时钟更接近主题本体”；
3. 所以主题本身并非零信息。

为什么又已明显偏硬：
1. 旧写法的 shared-gate 角色已经被 replication 审计得很清楚，继续按 `shared allow/deny gate` 讲，很容易只是在为低 retention 美化找解释；
2. 最近新增的最强旁证并不支持“再给旧 Rank 87 一次窄 shared-gate 预算”，而是把主题推向一条更像**单币 directional raw alpha** 的新宿主；
3. 若现在硬写 `Rank 87b`，很容易模糊原审计边界。

## Any salvage signal?
有，但更像“主题外流”，不是旧 rank 自身还能诚实窄救。

本轮最 relevant 的新旁证：
- `research/quant_digests/2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`

这条新 digest 给出的最重要信息不是“旧 gate 可以继续收紧”，而是：
1. **volume-clock 首 30m 极端冲击本身可能是一条单币 BTC directional raw alpha**；
2. 真正更像样的写法是：只在 `extreme volume + extreme return/range` 的 first-30m 事件上，去做后续 `30~60m` 同向续行；
3. 这已经不是“让它服务现有 `ema/fib/breakout` base setup 的 shared gate”，而是在把主题改写成一个**事件驱动 raw alpha 本体**。

换句话说：
- 可救信号存在；
- 但救的是 `volume-clock first30 impulse continuation` 这条新 raw-alpha family；
- 不是旧 `Rank 87 / volume-clock + CS spread interaction shared gate`。

## Single best cut
如果只保留唯一一刀，本轮最像样的改写方向是：

> **replace shared volume-clock + spread interaction gate with a single-asset first30m extreme-impulse continuation raw alpha**

也就是：
- 不再把 volume-clock 写成三条 15m setup 的 allow/deny gate；
- 改成只承认 `BTC first30m extreme impulse` 这一类事件本身，再单独测试其后续 `30~60m` 的 directional continuation。

但这刀本轮**不够诚实地属于 `Rank 87`**，因为：
1. 它已经把主语从 `shared gate` 换成了 `single-asset event raw alpha`；
2. 它不再保留旧 rank 的对象边界与职责层；
3. 若硬写成 `Rank 87b`，本质会是借新 family 的名字替旧 rank 续命。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次不值得 draft `Rank 87b`：
1. 原 `park` verdict 没被推翻；
2. 新增最强证据在把主题推向新的 `BTC first30 impulse continuation` raw-alpha family，而不是支持旧 shared-gate residual；
3. 旧 rank 唯一留下的 residual 仍然过度依赖极低 retention，不够支撑 queue-only 的诚实窄派生；
4. 若后续 bot2 要认领，更诚实的做法应是直接认领新的 raw-alpha intake，而不是挂回 `Rank 87` 名下。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已明显偏硬；最近新增的 BTC volume-clock first30 impulse 证据说明，Rank 87 的残余价值更像新的单币 event-style raw-alpha family，而不是旧 volume-clock + CS spread shared gate 的诚实窄派生，不足以 draft Rank 87b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：按要求只做最小必要文档改动；且仓库长期存在共享脏文件风险，避免混提。
