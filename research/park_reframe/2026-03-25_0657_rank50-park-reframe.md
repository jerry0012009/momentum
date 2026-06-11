# Rank 50 park reframe review

- 时间：2026-03-25 06:57 UTC
- 对象：`Rank 50 / chanlun-pro structural reclaim gate`
- 原始结论：`park / evidence pool`
- 本轮结论：`keep_park`
- 是否保留原 park 审计意义：`是`

## 为什么这次看 Rank 50
- 按 `docs/PARK_REFRAME_QUEUE.md` 当前轮转，默认优先低频看 `Rank 50+` 的 queue-facing parked 条目；最近 7 天未见 `Rank 50` 的 park-reframe 复盘记录，且本日 `50~79` 号段只刚覆盖到 `Rank 67`，仍适合回到同号段换一条未触达旧案。
- `Rank 50` 属于那类最容易被误读成“只是实现太粗、再改一刀也许能救”的条目：原 clean replication 确实比 raw baseline 少亏，因此值得单独确认这是不是足以长出一个新的窄 reframe。
- 同时，近 24h 新增的 `pump-fade / exhaustion reversal` 证据会让“结构回收失败”这条叙事显得更诱人；本轮要回答的是：这算不算 `Rank 50` 自己还能诚实派生新假设的理由。

## 原 rank 为什么 park
基于 `research/optimization_loop/2026-03-18_0829_rank50-clean-replication-park.md`：
- 原假设是把 `chanlun-pro structural reclaim` 压成一个可因果复现的 `breakout / retest` 确认层，希望它用“结构回收”替代更粗的裸突破回踩。
- 最小 clean replication（BTC/ETH/SOL, 120d, 15m, next-bar open, no-overlap, hold 8 bars, 6bps/side）显示：
  - `raw_breakout_retest`：`mean_total_return ≈ -9.34%`，`mean_trades ≈ 82.3`
  - `structural_reclaim`：`mean_total_return ≈ -4.85%`，`mean_trades ≈ 12.7`
  - `structural_reclaim_plus_htf`（主变体）：`mean_total_return ≈ -4.63%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 12.0`，`mean_false_reclaim_ratio ≈ 72.78%`，`mean_no_trade_ratio ≈ 87.14%`
- 也就是说，它的“改善”主要来自**极端砍交易**：确实比 raw 少亏，但样本被压到几乎没有，而且跨资产仍全部为负。
- 因此原始 `park` 的审计含义很清楚：**结构回收主题不是完全没信息，但把它写成可复用的 long-side structural reclaim gate 不诚实。**

## 它更像 hard park 还是 soft park
**结论：偏 hard 的 soft park。**

原因：
- 说它 `soft`，是因为 `structural_reclaim` 至少在方向上比 `raw_breakout_retest` 少亏，说明“别把所有突破回踩都当 continuation”这件事不是纯噪声。
- 说它“偏 hard”，是因为这些残余信息几乎全靠 `87.14%` 的 `no_trade_ratio` 换来；同时 `false_reclaim_ratio ≈ 72.78%` 过高，说明所谓 reclaim 在当前口径下大多数时候根本不够稳。
- 更直接地说：**原命题作为 long continuation / reclaim gate 已经基本审计完了，剩下的不是一个还能轻松救回来的 gate，而是一堆“失败形状”残余。**

## 有没有可救信号
**有，但信号主要指向“失败信息”，而不是救回原 Rank 50。**

主要两点：
1. `structural_reclaim` 相比 raw baseline 确实少亏，说明“结构确认”比裸突破更接近正确职责层；
2. 但 `false_reclaim_ratio ≈ 72.78%` 又非常高，说明这条线留下的最大信息量，不在于“reclaim 成立时去追”，而在于**reclaim 失败往往很多**。

问题在于，这个“可救信号”现在已经不新，也不再属于 `Rank 50` 的独占资产：
- 近邻 `Rank 31b` 已经把“false structural reclaim -> short failure-followthrough”写成更窄、更诚实的派生提案；
- 2026-03-24 新增的 `pump-fade / exhaustion reversal` digest 又把类似的失败延续/衰竭反转主题进一步收敛到一条新的事件驱动 raw-alpha 家族；
- 换句话说，`Rank 50` 留下的残余信息并不是零，而是**已经被更好的失败语义提案吸收了。**

## 最值得改的唯一一刀是什么
如果硬要保留唯一主修改轴，那就是：

**把“trade structural reclaim continuation”改成“只交易 structural reclaim failure 的 followthrough”，不再试图救回原 long reclaim gate。**

但这刀本轮**不值得再以 `Rank 50b` 形式重写**，原因很明确：
- 它和 `Rank 31b` 的主题高度重叠；
- 再继续往下推，很容易滑成“同一条失败叙事换不同壳重复排队”；
- 同时 2026-03-24 的 `pump-fade` 新证据更像一条新的事件驱动 raw-alpha family，而不是 `Rank 50` 原结构确认主题的诚实续命。

## 是否值得形成新的 derived hypothesis
**不值得。**

原因：
- 原始 blocker 没变：只要还把它写成 long-side structural reclaim gate，改善就主要靠极端砍样本美化；
- 唯一还像样的一刀（reclaim failure -> short followthrough）已经被更窄、更清楚的近邻提案消费；
- 最近新增外部证据也没有把 `Rank 50` 升级成“值得重新 queue 的独立窄假设”，反而更像提醒我们：这条残余信息应该归到别的失败家族，而不是回头给 `Rank 50` 续命。

## 本轮最终结论
- `final_status = keep_park`
- `original verdict kept = park`
- 简述：`Rank 50` 仍应保留为一条“structural reclaim 比 raw breakout 少亏，但主要靠极端砍单、且 false reclaim 很高”的审计案例；它留下的失败形状信息已基本被 `Rank 31b` 与更新的 pump-fade/exhaustion 家族吸收，当前不诚实再派生 `Rank 50b`。

## 对队列文件的最小写回
- `research/park_reframe/INDEX.md`：追加本轮索引。
- `docs/PARK_REFRAME_QUEUE.md`：仅在 `Recently reviewed` 追加一条 `Rank 50 / keep_park` 简记。
- 不改 `docs/TODO.md` 顶部排班。
- 不新增 `derived_hypothesis_drafted` 条目。

## 备注
- git 工作区存在大量与本轮无关的脏文件；本轮仅做 park-reframe 所需最小文本更新，不混提其他变更，也不做 selective commit。
