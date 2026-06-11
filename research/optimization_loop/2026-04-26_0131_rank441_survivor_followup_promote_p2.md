# Rank 441 / 7d vol-scaled TSMOM × shared cost budget — survivor follow-up promote_P2
- 时间：2026-04-26 01:31 UTC
- 执行器：bot3
- 对应 cycle_plan 小点：#1
- 结论：`promote_P2`
- 正式 Rank：`441`

## 本轮执行内容
只执行 survivor 槽允许的那一次最小 follow-up：围绕唯一 decisive blocker 回答两件事——
1. 这条 `1h parent trend -> 15m child direction router` 在核心 majors 上是否仍保留可迁移方向许可；
2. 它是否只是靠事后挑 child trigger 才显得成立。

## 使用的最小证据
### 1) 已有 portability / event 结果（来自首轮 digest artifacts）
文件：`reports/artifacts/quant_digests/2026-04-25_tsmom_parentchild_event_summary.csv`

在统一口径 `|7d trend z| >= 1`、按 parent 方向看后续固定 `4` 根 `15m` signed return（约 `1h`）时：
- `BTCUSDT`: `4237` 次，`+0.967 bps/event`
- `ETHUSDT`: `4525` 次，`-0.332 bps/event`
- `BNBUSDT`: `3859` 次，`+1.010 bps/event`
- pooled（含 ADA/XRP/DOGE）: `23507` 次，`+0.366 bps/event`

### 2) 本轮补的 core-majors portability 复核
为避免被非核心山寨币拖偏，本轮只复核 `BTC/ETH/BNB/SOL` 四个 core majors，在同一固定口径下重算 parent->child 事件：
- `BTCUSDT`: `4237` 次，`+0.967 bps/event`
- `ETHUSDT`: `4525` 次，`-0.332 bps/event`
- `BNBUSDT`: `3859` 次，`+1.010 bps/event`
- `SOLUSDT`: `3647` 次，`+3.289 bps/event`
- `POOLED_CORE`: `16268` 次，`+1.137 bps/event`

这说明它不是只在单一币种偶然成立：`BTC/BNB/SOL` 三个核心 majors 同口径都保留了正向 direction-permission 价值，只有 `ETH` 明显偏弱。

## honesty / execution realism 收口
本轮没有把 `pullback / breakout / microburst` 中某一种 child trigger 事后挑出来包装成“已验证 entry”；相反，我只保留了一个更诚实、更固定的主语：

> 当慢速 `7d` vol-scaled parent trend 已经给出强方向时，后续固定 `1h` 窗口的 child signed return 在 core majors 上仍整体偏正，因此这条对象可以作为 `15m` child direction router / admission hypothesis 进入 P2；它还不是已经完成 entry spec 的可跑主系统。

也就是说，这条 survivor follow-up 通过的不是“某个最好看的 child trigger”，而是更基础的一层：**不挑 trigger，固定看后续 `4` 根 `15m` 的方向许可，core majors 仍保留 pooled 正值。** 这消除了“只有靠事后挑 child trigger 才成立”的单一 decisive honesty blocker。

## 为什么这轮应直接 promote_P2
按当前 cycle_plan，小点 #1 只允许在 `promote_P2` 与 `background/P0` 之间收口。当前最关键的两点已经满足：
1. **majors portability 没塌**：`BTC/BNB/SOL` 保留正向，core-majors pooled 约 `+1.14 bps/event`；
2. **不存在单一致命 honesty blocker**：本轮没有靠事后挑 child trigger 才得到结果，而是用固定 forward window 验证了 parent->child direction permission。

因此它已经超过 `P1` 的“只有一句主语”阶段，值得进入 `P2 / pre-paper admission`，下一步再正式回答：
- effectiveness / expected return 在更接近真实 child execution 口径下是否仍站得住；
- ETH 弱势是否意味着要收窄到 `BTC/BNB/SOL`；
- parameter / time stability 与 friction realism 是否足够支持最终 `P2 exit`。

## 保留意见
- 这次通过的是 **router / admission** 主语，不是裸 `15m` taker trend 主系统；
- `ETH` 明显偏弱，意味着后续 P2 admission 很可能需要回答“是否收窄到 `BTC/BNB/SOL`”；
- 目前还没有 child entry spec（pullback / breakout / microburst）层面的真实 execution artifact，因此只能升 `P2`，不能直接进 `P3`。

## runtime 回写
- `Surviving candidate slot`: 清空（预算已用完并完成升级）
- `Active P2 slot`: 更新为 `Rank 441 / 7d vol-scaled TSMOM × shared cost budget`
- `p2_rounds_since_level_change`: `0`
- `p2_consecutive_keep_p2`: `0`
- `p2_last_evidence_axis`: `core_majors_parent_child_portability_and_trigger_honesty`

## 会改变系统认知的一句话
`Rank 441 / 7d vol-scaled TSMOM × shared cost budget` 已通过 survivor 阶段唯一允许的 majors portability / honesty follow-up：在不事后挑 child trigger 的固定 `1h` forward 口径下，`BTC/BNB/SOL` 仍保留正向 parent->child direction permission，因此该对象应从 `P1` 直接升到 `Active P2`，而不是退回 background。
