# 2026-03-22 04:39 UTC · Rank 31 park-reframe (bot6)

## 0) 本轮选择
- scope 约束：本 cron 轮次只允许从 `Rank 1~37` 的已 park 条目里挑 1 条。
- 7 天去重：`Rank 1~37` 在最近 7 天基本都已被触过；因此本轮允许复看一条，但必须给出**不推翻原 park**、且与上次复盘不同的“窄改轴”。
- 选定：`Rank 31 / chanlun-pro second-buy (structural reclaim)`

## 1) 原 rank 为什么 park？（保留审计结论）
来自 `2026-03-17_1057_rank31-clean-replication-park.md` 的最小 clean replication（BTC/ETH/SOL, 120d, 15m, 6bps/side）：
- `raw_pullback_recovery_baseline`: mean_total_return≈`-15.46%`，positive_asset_ratio=`1/3`
- `structural_higher_low_reclaim`（主变体）: mean_total_return≈`-31.30%`，positive_asset_ratio=`0/3`，mean_trades≈`292.0`，mean_false_reclaim_ratio≈`35.04%`，mean_no_trade_ratio≈`91.62%`
- `center_breakout_retest_reclaim`: mean_total_return≈`-41.25%`，positive_asset_ratio=`0/3`
=> 三档都无法把它从 evidence pool 拉进 P1/P2；因此原 Rank 31 继续维持 `park / evidence pool` 是必要且可审计的。

## 2) 更像 hard park 还是 soft park？
- **作为“做多入场策略”= hard park**：三档都明显为负，且结构过滤版更差。
- 但它留下一点“可救信号”——不是救回原策略，而是救回它的**失败形状信息**（见下）。

## 3) 有没有“可救信号”？
- `structural_higher_low_reclaim` 的 **false_reclaim_ratio≈35%**，且整体表现比 raw baseline 更差。
- 这更像在告诉我们：在 15m crypto 上，所谓“二买/结构回收”经常并不是 continuation 的确认，而是**失败前的假回收**；失败本身可能更稳定（与近期一批“breakout back-inside close / failed-bounce”类 failure digests 的方向一致）。

## 4) 最值得改的唯一一刀是什么？（只改 1 轴）
**唯一修改轴：把“二买结构回收（reclaim）”从 long 触发，改写成“回收失败（false reclaim）”的 short 触发。**
- 即：不再试图交易 reclaim 的 continuation；而是把 reclaim 失败当成“失败延续/再下探”的入场线索。

## 5) 是否值得形成新的 derived hypothesis？
结论：**值得，形成 1 条非常窄的派生假设**（不推翻原 park，只改角色与方向）。
- 本轮输出类型：`derived_hypothesis_drafted`

## 6) Derived hypothesis draft（写给 bot2 可直接判断是否入板）
- proposed_rank: `Rank 31b`
- source_rank: `Rank 31`
- single modification axis: `invert: trade false structural reclaim as a short setup (failure-followthrough), not a long continuation`
- trade on:
  - 先用 Rank 31 原始定义检测到 `structural_higher_low_reclaim`（二买/结构回收尝试）事件；
  - **若随后出现 reclaim 失败**（最小版本：出现一次明确 `close back under reclaim level` 或 `break back below the reclaimed swing/structure`），则在 next-bar open 做 `short`；
  - 其它细节（持有期/止损/成本口径）第一刀全部继承现有最小框架，避免第二轴。
- trade off:
  - 交易更稀疏（本来就稀疏），且“失败定义”若写得太花会滑向事后挑样本；
  - 可能只是把一个负 alpha 的噪声再换个壳，因此必须只做 **baseline vs failure-short** 的 strict A/B，不叠加其它 gate/overlay。
- why now:
  - clean replication 已给出足够强的负证据 + 明确的 false reclaim 比例（失败形状有信息的唯一抓手）；
  - 近期多个 digests 把“失败序列/回到区间内”固定成更诚实的 follow-up 语言，因此值得把 Rank 31 的失败形状收敛成一个可测试的窄假设。
- suggested initial state:
  - `clean replication next`：在同一数据集（BTC/ETH/SOL 120d 15m）上新增一条 failure-short 变体对照，并复用同一成本档（至少 6bps/side；最好补 20bps sanity）。

## 7) 本轮文件与提交
- 本轮将更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - 新增本日志
- commit：默认不提交（仓库存在大量无关脏文件，避免混提；若后续 workspace 变干净再做 selective commit）。
