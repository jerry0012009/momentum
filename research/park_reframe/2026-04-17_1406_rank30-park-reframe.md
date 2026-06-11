# 2026-04-17 14:06 UTC · Rank 30 park reframe review

## Scope
- source rank: `Rank 30 / trendline paired-channel corridor breach`
- original status kept: `park`
- this round verdict: `keep_park`

## Why this rank now
- 本轮仍按 `bot6` 低频规则，只处理 `Rank 1~37` 里 1 条已 `park` 的旧 rank。
- `Rank 30` 上次 park-reframe 复盘是 `2026-04-09 22:14 UTC`，已超过 `7` 天。
- 它也正好属于那类“曾经有过 1 条很窄 residual，但该 residual 已经被 runtime 消费”的典型案例，适合做一次低频收口，确认是否还存在新的单轴可救空间。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-17_0930_rank79-park-reframe.md`
- `research/park_reframe/2026-04-16_1410_rank61-park-reframe.md`
- `research/park_reframe/2026-04-16_1146_rank24-park-reframe.md`
- `research/park_reframe/2026-04-09_2214_rank30-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_1007_rank30-trendln-channel-intake.md`
- `research/optimization_loop/2026-03-17_1422_rank30-clean-replication-park.md`
- `research/optimization_loop/2026-04-09_1526_rank30b_fresh_intake_background_absorbed.md`
- `research/park_reframe/2026-03-18_1513_rank30-park-reframe.md`

## 1) 原 rank 为什么 park
原始 `Rank 30` 被 park 的原因已经很清楚：
- `raw corridor breach` 太机械，假突破率很高；
- `breach_plus_reclaim_hold` 虽然比 raw 版少亏，说明“突破后确认层”这个方向没有完全错；
- 但 clean replication 仍给出 `positive_asset_ratio=0/3`，而且 `mean_false_break_ratio` 仍高达约 `82.39%`；
- 所以真正的 blocker 不是“paired-channel/corridor breach 完全没信息”，而是 **旧 Rank 30 的确认写法仍不足以把真假突破诚实分开**。

一句话：
> 原 rank 被 park，是因为它只证明了“加确认会少亏一点”，没有证明这套 corridor-breach 确认已经强到能在成本后独立存活。

## 2) 它更像 hard park 还是 soft park
**本轮判断：`soft park`，但已经非常接近 `hard with consumed residual`。**

为什么仍是 soft：
- 原始 replication 至少说明 `confirmation > raw breach`；
- 也就是说，后续确认层这个主题不是完全空的。

为什么又更接近 hard：
- 原 rank 唯一自然、又足够窄的 rescue 轴，早已收敛成既有 `Rank 30b`；
- 而 `Rank 30b` 又已在 `2026-04-09` fresh intake first verdict 中直接收口为 `background / absorbed`；
- 这意味着旧 `Rank 30` 的 residual 并没有进一步长成独立 pocket，而是被更上位的 `post-event hold/reclaim / event-anchored AVWAP` family 吸收掉了。

## 3) 有没有“可救信号”
**有残余语义，但没有新的 decisive rescue signal。**

还能保留的那点可救信号，其实仍然只是旧结论里的同一件事：
- 相比 raw breach，`breach_plus_reclaim_hold` 少亏；
- 说明“突破后需要更诚实的接受/持有确认”这条方向没错。

但问题在于：
- 这条 residual 已经被 `Rank 30b = breach-event anchored VWAP hold/reclaim` 明确表达过；
- 而 `Rank 30b` 的 first verdict 又已经给出 runtime truth：它更像既有 `event-anchored AVWAP / breakout-confirmation` family 内的具体实例，不足以保留独立身份。

所以本轮不能说“没有任何残余信息”；
但更诚实的说法是：
> **残余仍在，可它已经不再属于旧 Rank 30 可继续派生的新 rank 空间。**

## 4) 最值得改的唯一一刀是什么
**没有新的唯一主修改轴。**

如果一定要回答“唯一最值得改的一刀是什么”，那答案仍然只会是旧的那一刀：
- 把 `binary breach_plus_reclaim_hold` 改成 `breach-event anchored VWAP hold/reclaim`；
- 也就是既有 `Rank 30b`。

但这条轴已经被实际 intake 过，并已收口为 `background / absorbed`。
因此本轮更准确的表述不是“还有一刀值得新 draft”，而是：
> **旧 Rank 30 唯一诚实的一刀已经被消费完，没有新的单轴值得再写成 `Rank 30c`。**

## 5) 是否值得形成新的 derived hypothesis
**不值得。最终结论：`keep_park`。**

原因有三：
1. **原 blocker 没被推翻**
   - 旧 rank 的核心问题仍然是 post-breach false break 太高，且成本后三腿全负。
2. **唯一自然 residual 已被消费**
   - `Rank 30b` 已把最自然的 confirmation rescue 走完一轮，并被 runtime 收口为 family-absorbed。
3. **当前再派生只会滑向换语法重试**
   - 再写 `Rank 30c`，大概率只是在 body/wick/volume/time-window 等确认语法里继续碰运气，或者顺手偷带第二轴，这不符合本轮纪律。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 corridor breach 的后续确认太粗，假突破率过高；即使 `reclaim_hold` 比 raw 版本少亏，仍不足以形成成本后、跨资产的诚实存活。

### 它更像 hard park 还是 soft park？
`soft park`，但已非常接近 `hard with consumed residual`。

### 有没有“可救信号”？
有，但只是旧的 post-breach confirmation residual；而这条 residual 已被 `Rank 30b` 表达并被 runtime 吸收到既有 family，当前没有新的 decisive signal。

### 最值得改的唯一一刀是什么？
没有新的唯一一刀；唯一还诚实的一刀仍只是已被消费的 `Rank 30b = breach-event anchored VWAP hold/reclaim`。

### 是否值得形成新的 derived hypothesis？
不值得；维持 `keep_park` 更诚实。

## Bottom line
`Rank 30` 不是因为“corridor breach 主题完全没信息”而被 park，而是因为它唯一自然的确认层 residual 已经被 `Rank 30b` 消费完；在没有新证据把它从既有 AVWAP/breakout-confirmation family 里重新拉开之前，继续派生 `Rank 30c` 只会削弱原 `park` verdict 的审计意义。因此本轮保持 `keep_park`。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- 当前仓库仍有无关脏文件，本轮不做 commit，避免混提。
