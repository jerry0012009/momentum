# 2026-04-25 11:43 UTC · Rank 34 park reframe

## Scope
- source rank: `Rank 34 / chip-distribution trapped-holder reclaim / winner-ratio gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮严格限定在 `Rank 1~37` 的已 `park` 条目内；`Rank 2 / Rank 17 / Rank 29 / Rank 32b` 当前都不是应由 bot6 复盘的 parked 对象；
  - `Rank 34` 上次 park-reframe 复盘是 `2026-04-18 11:17 UTC`，这次已越过默认 `7` 天回避窗口；
  - 这几天没有新的 decisive evidence 把旧 `synthetic shares / turnover` proxy 重新变诚实，适合做一次低频确认：old `Rank 34` 是否还剩 queue-facing 的单轴 residual。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-25_0911_rank12-park-reframe.md`
- `research/park_reframe/2026-04-24_2113_rank53-park-reframe.md`
- `research/park_reframe/2026-04-24_1851_rank36-park-reframe.md`
- `research/park_reframe/2026-04-18_1117_rank34-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_1222_rank34-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
- `research/quant_digests/2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md`
- `research/quant_digests/2026-04-05_1755_poc-cvd-absorption-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 34` 被 park 的主因一直很清楚：
**edge 过度依赖 `synthetic shares / turnover` 这类 assumptions-sensitive 的库存代理。**

原 clean replication 的关键事实仍成立：
- `raw_baseline @ 6bps/side` 三资产均值约 `-7.38%`；
- `chip_cost_reclaim` 只在最乐观、最保守的 `conservative anchor` 下显著好看；
- 一旦放宽到 `neutral / aggressive` anchor，跨资产存活和收益都明显塌缩；
- 成本上提后，这条 pocket 也快速退化。

所以 old `Rank 34` 被 park，不是因为“库存拥挤 / trapped-holder reclaim”这类市场语言完全没信息，而是因为：
> 可执行结论主要寄生在不够诚实、也不够稳的 proxy 设定上。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：更像 `hard park`，且比 4 月 18 日那轮更接近 `hard park with consumed residual`。**

原因：
1. blocker 在 explanatory variable 的 honesty，不在简单阈值或 exit 细节；
2. 唯一像样的 pocket 仍依赖最容易美化的 anchor 设定；
3. 4 月以来与 inventory / anchor 更贴近的新证据，持续把主题推向更直接的 `POC / LVN / anchored-VWAP` 宿主，而不是回流到 old `Rank 34` 本体。

若硬要留一点 soft 成分，也只剩：
- 旧实验至少证明“inventory / fairness”母主题不是完全空想；
- 但这点残余已不足以支撑一个新的 queue-facing `Rank 34b`。

## 3) 有没有“可救信号”？
**有主题级可救信号，但没有 old `Rank 34` 级别的可救信号。**

这几条旁证方向一致：
- `auction-profile / POC / LVN` 更像直接的 auction-structure raw alpha；
- `anchored-VWAP regime-extreme` 更像明确的 anchored fairness / reversion 宿主；
- `POC + CVD absorption` 则把 inventory 语义写成更可执行的 event-defined shell。

共同点不是“帮 old Rank 34 补一刀”，而是：
> 如果 inventory / fairness 主题还有价值，应该直接用更诚实的锚点主语来写，而不是继续依赖 `synthetic shares / turnover` 去侧推库存。

## 4) 最值得改的唯一一刀是什么？
如果只允许保留 **1 条唯一主修改轴**，最诚实的一刀仍然只能是：

**把 `chip-distribution trapped-holder reclaim` 从可执行 gate，降级成离线 inventory-context note。**

也就是：
- 不再让它负责 `allow/deny` 或 `next-bar entry`；
- 只保留“这里可能处于 inventory-crowding / trapped-holder reclaim 背景”的解释层角色。

但这恰好也是本轮不应 draft 新 hypothesis 的原因：
- 一旦降到这个层级，它已经不再是 bot2 可直接判断是否入板的 queue-facing 提案；
- 它没有修复旧 proxy 的 honesty，只是把问题边缘化；
- 这更像“保留审计注脚”，不是值得重开的窄策略假设。

## 5) 是否值得形成新的 derived hypothesis？
**不值得；本轮维持 `keep_park`。**

理由：
1. 原 `park` verdict 的审计意义仍完整；
2. 最近没有新证据修复 `synthetic shares / turnover` proxy 的 assumptions sensitivity；
3. 若现在硬写 `Rank 34b`，大概率会滑向“换锚点 + 换宿主”的多轴大改；
4. 更诚实的结论是：old `Rank 34` 的 residual value 继续外流到新的 `auction-structure / anchored-fairness / POC-absorption` 宿主，而不是仍值得以旧 rank 名义重开。

## 6) 审计式 trade on / trade off（仅用于说明为什么不 draft）
### single modification axis
- `demote chip-distribution trapped-holder reclaim from executable gate into offline inventory-context evidence only`

### trade on
- 保留 old `Rank 34` 对“库存拥挤 / 套牢盘重夺”直觉的审计痕迹；
- 不再强行让它承担 bar-level trigger；
- 承认它最多只配作为背景解释层。

### trade off
- 不再是 queue-facing hypothesis；
- 没有修复旧 proxy 的核心 honesty 问题；
- 很容易沦为事后解释变量；
- 相比新的 `POC / LVN / anchored-VWAP` 宿主，表达更弱、更绕，也更不诚实。

## Final verdict
**`keep_park`**

- 原 `park` verdict 保留；
- `Rank 34` 更像 `hard park with consumed residual`；
- 可救信号属于新的 `auction-structure / anchored-fairness` raw-alpha family，而不属于 old `Rank 34` 足以诚实派生的 `Rank 34b`；
- 因此本轮不 draft 新的 derived hypothesis。

## Queue impact
- `docs/PARK_REFRAME_QUEUE.md`：仅在 `Recently reviewed` 追加一条 `Rank 34 / keep_park` 简记；
- `research/park_reframe/INDEX.md`：追加本轮索引；
- 默认不改 `docs/TODO.md` 顶部排班；
- 不新增 active reframe candidate。

## Commit note
- 工作区存在大量与本轮无关脏文件；为避免混提，本轮不做 selective commit。
