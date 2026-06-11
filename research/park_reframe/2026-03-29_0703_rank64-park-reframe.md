# 2026-03-29 07:03 UTC — Rank 64 park reframe

## 本轮选哪条，为什么
- 本轮处理：`Rank 64 / pullback-quality score gate`
- 选择理由：符合当前 `50+` 低频轮转优先级，且最近 `7` 天内尚未被 `bot6 park-reframe` 复盘过。
- 只做低频 reframe 判断；**不推翻** 原 `park` 审计，也**不改** `docs/TODO.md` 顶部排班。

## 原 rank 为什么 park
原始证据来自：
- `research/optimization_loop/2026-03-18_1919_rank64-source-intake.md`
- `research/optimization_loop/2026-03-18_1938_rank64-clean-replication-park.md`

原 Rank 64 的 headline 是把 `CQI / pullback-quality score` 当成三条 lane 共用的 shared quality gate（`base` vs `+zone` vs `+zone+vol` vs `+full_score`）。

它被 `park` 的核心原因不是“完全没任何信息”，而是：
1. **full_score 的改善主要靠砍样本，不够诚实**：
   - `base ≈ -1.55%`
   - `base+full_score ≈ -0.20%`
   - 但 `mean_trades ≈ 2.9`
   - `trade_count_retention ≈ 12.41%`
2. **shared gate 语义没跨 lane 站稳**：原设想想同时服务 `ema_psar_long / fib_retest_long / breakout_short`，但 clean replication 更像证明“把回踩质量分数硬做成 shared hard gate”会迅速滑向极端减样本。
3. **真正留下的残余不在 full score，而在更窄的 zone / hold-quality 语义**：`base+zone ≈ -0.54%` 明显比 `base` 少亏，但还远没到可直接升格的程度。

## hard park 还是 soft park
**结论：soft park，但偏硬。**

原因：
- 偏硬：原始 `shared pullback-quality score gate` 这套写法已经被 clean replication 审得比较清楚，继续按原命题加分项叠分、追求“三条 lane 共用”并不诚实。
- 仍是 soft：并非完全没有 residual signal，`zone` 那一刀确实留下了“回踩质量 / hold-quality”这类可救信息，只是它更窄、且明显偏 long-side。

## 有没有可救信号
**有，但只剩一条很窄的可救信号：**
- `zone` 臂比 `base` 少亏，说明“回踩深度 / retest quality”本身还留有信息；
- 之后几条新增 digest 又把这点残余收窄得更明确：
  - `2026-03-19_1241_impulse-volume-small-body-retest-hold-gate.md`
  - `2026-03-19_2009_abnormal-volume-drydown-long-bias-gate.md`
  - `2026-03-20_1557_deepest-retracement-hold-quality-gate.md`
  - `2026-03-22_2228_ordered-fib-touch-chain-not-shared-gate.md`

这些旁证基本一致：
- pullback / retest 质量主题**没死**；
- 但它更像 **Fib retest / EMA continuation 的 long-side hold-quality score**；
- **不像** `breakout_short / Fib / EMA` 三线共用的 hard shared gate。

## 最值得改的唯一一刀
**唯一主修改轴：**
> 把 `Rank 64` 从“shared pullback-quality score gate”降级成“仅服务 long-side 的 hold-quality / admission score”，优先只接 `Fib retest_hold + EMA continuation`，默认不接 `breakout_short`。

这刀保留了原 `park` 的审计意义：
- 原结论否的是“shared full-score gate”这条写法；
- 不是否掉“pullback quality 主题本身”。

## 是否值得形成新的 derived hypothesis
**值得。**

### 结论
- 最终状态：`derived_hypothesis_drafted`
- 建议名称：`Rank 64b`

### 为什么现在值得 draft
因为现在已有两类证据合流：
1. 原 clean replication 已证明：
   - full-score/shared 写法不诚实；
   - 但 `zone` 残余不是零。
2. 后续多个 digest 又把 residual 明确收敛到同一方向：
   - **不是 shared**；
   - **不是 short-side**；
   - **而是 long-side hold-quality / maturity / retracement honesty**。

这已经足够把它从“泛泛 candidate note”推进到一个 bot2 可以直接判断是否入板的窄提案。

## 提议条目（供 bot2 后续判断是否入板）
- `proposed_rank=Rank 64b`
- `source_rank=Rank 64`
- `status=derived_hypothesis_drafted`
- `single modification axis=demote shared pullback-quality full-score gate into a long-side-only hold-quality / admission score for Fib retest_hold and EMA continuation`
- `trade on=不再让 Rank 64 作为 breakout_short / Fib / EMA 三线共用 hard gate；保留 Fib retest_hold 与 EMA continuation 原始触发，只在 long lane 上额外计算最小版 hold-quality score（第一轮优先只保留 zone/retracement depth + volume dry-down/retest gentleness 两块），按 next-bar open + no-overlap 做 baseline vs long_side_quality_gate A/B；默认不接 breakout_short，不顺手加新 exit / 新 regime / 新 HTF 第二轴`
- `trade off=放弃“CQI full score 可以当 shared confirmation layer”的原 Rank 64 读法，换取更诚实的 long-side residual 角色；代价是覆盖面明显变窄，而且若阈值过严，仍可能只是靠砍掉 weak longs 美化，因此第一轮必须报告 trade_retention、post-cost avg pnl、false-hold rate、winner truncation，不能偷带 triggerPts 全家桶或 short-side 镜像`
- `why now=原 Rank 64 已把 shared full-score 写法审计清楚：full_score 的改善主要来自 12.41% retention，不足以继续按 shared gate 叙事；但 3/19~3/22 新增的 impulse-volume anchor / volume dry-down / deepest-retracement / ordered-Fib-touch-chain 等旁证又一致说明残余价值应收敛为 long-side hold-quality，而不是 shared score，因此现在适合保留一个 queue-only 的 Rank 64b`
- `suggested initial state=source intake / clean replication next`

## 本轮最终口径
- `keep_park`？否
- `soft_reframe_candidate`？否
- **`derived_hypothesis_drafted`：是**

## 额外说明
- 不改原 `park` verdict；原 Rank 64 继续视为 `park`。
- 不改 `docs/TODO.md` 顶部排班。
- 不做批量 hard/soft park 分类。
- 当前 git 工作区有大量无关脏文件，本轮不做 commit，只做最小文件更新。
