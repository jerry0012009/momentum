# 2026-03-25 13:35 UTC — Rank 92 park reframe review

- source rank: `Rank 92`
- original verdict kept: `park`
- this round verdict: `keep_park`
- touched lane: `opening-drive adaptive offset continuation gate`

## 为什么这轮选它
- 按 `bot6` 当前轮转规则，`50~79` 与 `80~110` 号段里最近已覆盖过 `Rank 50 / 53 / 67 / 101`，本轮继续留在 `80~110`，优先抽查一条最近 `7` 天未做过 `park-reframe` 的旧 parked rank。
- `research/park_reframe/INDEX.md` 最近 `7` 天未见 `Rank 92` 的复盘记录，符合“优先换别的”原则。
- `Rank 92` 属于典型的“原主题未必全错，但 shared gate 角色可能摆错”的旧 park：它既有一点 path-quality 直觉，又被时间稳定性直接压回 `park`，很适合判断是否值得长出新的窄 reframe hypothesis。

## 1. 原 rank 为什么 park？
- 原线先在 `research/optimization_loop/2026-03-19_1543_rank92-intake.md` 被冻结成：把 opening-drive 的 `adaptive_offset` 写成三条主线可共用的 `shared continuation-confirmation gate`，而不是独立开仓策略。
- 随后的时间稳定性检查（`research/optimization_loop/2026-03-19_1632_rank92-time-stability-park.md`）给出的硬证据很直接：
  - `adaptive_offset_gate`：`overall_mean_total_return ≈ -6.91%`，`positive_asset_ratio ≈ 33.33%`，`positive_bucket_count = 1/3`
  - `adaptive_offset_halfsize`：`overall_mean_total_return ≈ -6.39%`，`positive_asset_ratio ≈ 33.33%`，`positive_bucket_count = 1/3`
- 人话就是：它不是完全没有改善 path-quality 的味道，但改善没有稳定穿过时间维度；前两桶大多仍在漏，只有后段勉强转正。
- 所以原 `park` 的真实含义不是“opening-drive 信息完全没价值”，而是：**把它写成全天候、跨 setup 共用的 15m shared continuation gate，不够诚实也不够稳定。**

## 2. 它更像 hard park 还是 soft park？
- 结论：**soft park，但偏硬。**
- 为什么不是 hard park：
  - opening-drive / early impulse 这类主题本身没有死；它至少抓到了一点“开段强弱会影响后续 continuation 质量”的直觉。
  - 最近新 digest `2026-03-25_1144_clock-conditioned-intraday-momentum-reversal.md` 也再次证明：crypto 的日内 edge 往往不是全天同口径，而是按 UTC 时钟口袋切成不同模式。
- 为什么又偏硬：
  - `Rank 92` 自己这版实现已经明确失败在**时间稳定性**，不是只差一点 friction 微调；
  - 更关键的是，它把“开段信息”写成了 **shared continuation gate**，这恰好是最容易过度泛化的位置。

## 3. 有没有“可救信号”？
- **有，但弱，而且更像主题迁移线索，不像原 rank 自己还能诚实续命。**
- 可救信号主要有两条：
  1. 原 Rank 92 至少提示：`opening-drive` 不是纯噪音，早段位移/锚点对后续 path-quality 可能有一点解释力；
  2. 最新 `clock-conditioned mode switch` digest 说明：真正更厚的信号形状，也许不是“是否越过 adaptive offset 才放行 continuation”，而是**同一日内 early-return 在不同 UTC bucket 里分别走 continuation / reversal**。
- 但这两条都没有把 `Rank 92` 救回来，原因同样明确：
  - 可救信号更像“时钟口袋 alpha / 开段冲击质量”家族，而不是原 Rank 92 这条 `shared gate` 写法；
  - 相邻提案里，`Rank 5b` 已经把最自然的窄救法收成 **first-30m impulse-quality shared continuation gate / sizing layer**；
  - 再从 `Rank 92` 派生一个近似版本，会高度重复已有 `Rank 5b` 与新的 clock raw-alpha 家族叙事。

## 4. 最值得改的唯一一刀是什么？
- 如果硬要保留唯一主修改轴，最自然的一刀是：
  - **把 `opening-drive adaptive offset continuation gate` 从“全天 shared continuation confirm”降级成“时钟口袋 / first-30m impulse-quality note”，不再要求它跨 setup、跨时段统一放行。**
- 但这刀本轮不建议真的起草成 `Rank 92b`，因为：
  - 它已经明显滑向了 `Rank 5b` 与 `2026-03-25` 那篇 `clock-conditioned mode switch` digest 所代表的新 raw-alpha family；
  - 再起一个 `Rank 92b`，本质是在重复包装“开段冲击 / 时钟口袋”这条更通用的新主题，而不是保留原 Rank 92 的审计边界。

## 5. 是否值得形成新的 derived hypothesis？
- **不值得。**
- 本轮最终判断：`keep_park`。
- 原因不是“完全没有可救信号”，而是：
  - 原版 blocker 很清楚：时间稳定性不过关；
  - 最自然的新写法已经被 `Rank 5b` 与新的 `clock-conditioned mode switch` raw-alpha 家族消费；
  - 现在再派生 `Rank 92b`，更像把“session / clock 主题”重复写一遍，而不是新增一个 bot2 值得独立判断是否入板的窄假设。

## 6. trade on / trade off 怎么看？
- 本轮不形成新的 derived hypothesis，因此不正式起草 `trade on / trade off`。
- 只保留一句审计备注：
  - **trade on `clock-conditioned opening impulse / mode-switch` 这类新 family；不要再 trade on `Rank 92` 这版全天 shared adaptive-offset gate 本身。**

## 最终结论
- `Rank 92` 原 `park` verdict 保留。
- 分类：`soft park`，但偏硬。
- 本轮不新增 `derived hypothesis`，不改 `docs/TODO.md` 顶部排班。

## 文件更新
- 已追加：`research/park_reframe/INDEX.md`
- 已更新：`docs/PARK_REFRAME_QUEUE.md`

## commit
- 未做 git commit。
- 原因：当前工作区长期存在大量与本轮无关的脏文件；本轮只做 park-reframe 所需最小文本更新，避免混提。
