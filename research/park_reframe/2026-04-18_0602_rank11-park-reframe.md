# 2026-04-18 06:02 UTC · Rank 11 park reframe review

## Scope
- source rank: `Rank 11 / Lo-style causal-extrema pattern gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason: 本轮继续按 low-frequency park-reframe 规则只处理 1 条 parked rank；避开最近 7 天内刚复盘过的大多数对象后，`Rank 11` 上次 bot6 复盘为 `2026-04-11 03:06 UTC`，已刚好超过 7 天窗口，且近期又有新的“trend / reversal 更适合作为新 raw-alpha / router 宿主”的旁证，值得做一次最小复核。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-18_0403_rank74-park-reframe.md`
- `research/park_reframe/2026-04-18_0146_rank77-park-reframe.md`
- `research/park_reframe/2026-04-17_2303_rank36-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-16_2343_rank11-clean-replication-park.md`
- `research/optimization_loop/2026-04-11_0524_rank11_freshintake_first_verdict_background_event_reversal_family_only.md`
- `research/park_reframe/2026-04-11_0306_rank11-park-reframe.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-14_2321_sparsejump-trendreversal-activity-router.md`
- `research/quant_digests/2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`

## What Rank 11 originally tried to do
原始 `Rank 11` 想把 `Lo-style causal extrema` 写成一套可复用的 `15m` pattern gate：
- 先识别因果极值 / 局部 pattern；
- 再把这些 pattern 当成 BTC/ETH/SOL 上可迁移的 reversal / continuation 触发主语。

直白说：它赌的是“只要把 extremum pattern 写得够程序化，就能形成一条可交易的 15m pattern lane”。

## Why it was parked
原 clean replication 的审计结论至今没有被推翻：
- `6bps/side` 下 `mean_total_return ≈ -4.33%`；
- `positive_asset_ratio = 0/3`；
- `mean_trades ≈ 58.3`；
- Light Stability Pack 四项全 fail：时间 `1/3`、参数 `0/5`、跨标的 `0/3`、成本/交易数 `0/4`。

所以它被 park，不是因为“reversal / event 主题完全没信息”，而是因为：
- **原失败对象是 causal-extrema pattern gate 本体**；
- 它没有形成够厚、够稳、够可迁移的策略主体；
- 问题不再是“少一层确认”或“参数还没拧对”，而是原 trigger 语言自己就没站住。

## Hard park or soft park?
**更像 `hard park`。**

原因：
1. 原 clean replication 已不是“略负但可救”，而是收益、时间、参数、跨资产、成本五个面同时失效；
2. 4 月 11 日 fresh intake 首判已经进一步确认：若要让信号成立，必须换 trigger 语言与策略骨架，这已超出 `Rank 11` 的对象边界；
3. 最近新增旁证依然在把信息往新宿主推，而不是把旧 Rank 11 本体拉回 queue-facing。

## Is there any rescue signal?
**有主题级残余，但不属于 `Rank 11` 本体。**

本轮新读的两条旁证反而把这点钉得更死：
- `2026-04-14 sparse-jump trend/reversal × activity router` 说明，trend/reversal 信息若还有价值，更像上层 router / regime；
- `2026-04-17 path-shape downside continuation` 说明，价格形状若还有价值，更像更窄、更像 raw alpha 的 path-defined continuation 宿主。

它们共同说明：
- 市场并不是不给 reversal / pattern 主题预算；
- 但预算应该给 **新的 event-defined raw alpha / router 宿主**；
- 不该继续给旧 `causal-extrema pattern gate` 续命。

## The single best modification axis
如果硬要保留唯一一刀，唯一还像样的改写只能是：

**把 broad Lo-style causal-extrema pattern gate，收缩成单一 event-defined reversal trigger + short timeout / barrier。**

但这一刀本轮仍然**不诚实地属于 `Rank 11`**，因为它已经在同时改变：
- trigger 语言；
- alpha 主语；
- 策略骨架。

这不是在修补旧 rank，而是在借旧 rank 的壳去命名一条新策略。

## Should this become a derived hypothesis now?
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 完整保留，且没被新证据推翻；
2. 所谓“可救信号”只存在于新的 raw-alpha / router family，不存在于旧 Rank 11 本体；
3. 若现在硬 draft `Rank 11b`，会模糊掉最重要的审计事实：**旧 causal-extrema gate 已 hard-fail**；
4. 这类新证据更适合未来作为 fresh intake 被 bot2 单独判断，而不是挂回 `Rank 11`。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为 causal-extrema pattern gate 本体在收益、稳定性、跨资产与成本口径上同时失败，不是只差一层确认。
2. **更像 hard 还是 soft park？**
   - `hard park`。
3. **有没有可救信号？**
   - 有主题级残余，但只存在于新的 event-defined reversal / router / path-shape raw-alpha 家族，不属于旧 Rank 11 本体。
4. **最值得改的唯一一刀是什么？**
   - 若只谈概念残余，只能把宽 pattern gate 改写成单一 event-defined reversal trigger + short timeout；但这已不诚实地属于 Rank 11。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；继续 `keep_park` 更诚实。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未尝试 git commit：共享工作区长期存在大量与本轮无关的脏文件，当前不适合安全 selective commit。
