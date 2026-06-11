# 2026-03-30 13:34 UTC · Rank 27 park reframe 低频复核

## 本轮对象
- `Rank 27 / Mt.Gox neckline confirmation / pattern-complete breakout gate`
- 本轮结论：`keep_park`
- 原 verdict 保留：`park`

## 为什么这轮看它
- `Rank 27` 上次 bot6 复盘是 `2026-03-23 11:15 UTC`，已超过最近 `7` 天回避窗口。
- 当前 `50+` 与 `80~110` 号段近期已连续覆盖，这轮回到 `1~24 / 25~49` 轮转时，`Rank 27` 仍是一个代表性旧 park：
  - 原 rank 已经有过唯一自然派生 `Rank 27b`；
  - 但最近又出现了两类与 breakout 家族直接相关的新证据，值得确认它们是不是会打开 `Rank 27c`：
    1. `2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`
    2. `2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`
- 本轮要回答的不是“breakout 主题还活不活”，而是：**这些新证据是否属于 `Rank 27` 这条 neckline + retest confirmation 血缘，还是已经上移到更上位的 raw-alpha family。**

## 原 Rank 为什么 park
原始 clean replication（`2026-03-17_0815_rank27-mtgox-neckline-clean-replication.md`）已经把审计结论写得很清楚：
- `raw_breakout @ 6bps/side`：`mean_total_return≈-13.79%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈71.56%`
- `neckline_confirm @ 6bps/side`：`mean_total_return≈-17.42%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈62.50%`
- `neckline_confirm_plus_retest_hold @ 6bps/side`：`mean_total_return≈-3.03%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈68.67%`

原 rank 被 park，不是因为“breakout 完全没主题”，而是因为：
1. `neckline_confirm` 虽然压了一些假突破，但收益更差；
2. `retest_hold` 虽然明显收窄亏损，但没有把假突破率一起压到足够干净；
3. 结果仍不足以形成跨资产、成本后的可保留 alpha。

换句话说：**原 Rank 27 的 blocker 不是“结构 breakout 没故事”，而是“neckline confirm / static retest_hold 这版确认层不够诚实”。**

## 它更像 hard park 还是 soft park
- 本轮判断：**soft park，但比 2026-03-23 那次更偏硬。**

原因：
- soft 的部分仍然成立：
  - `raw_breakout -> retest_hold` 的确把亏损从约 `-13.79%` 收窄到约 `-3.03%`；
  - `Rank 27b` 也一度把 `false_break_ratio` 压到约 `58.42%`，说明确认层方向不是纯错。
- 但更偏硬的原因也很清楚：
  - `Rank 27b` 这条唯一自然救法已经被做过最小诚实检查，结果仍是 `park`；
  - 最近新证据继续告诉我们“breakout 主题活着”，但活下来的越来越像**独立 raw-alpha skeleton / event-clock skeleton**，而不是原 Rank 27 这种 neckline + retest confirmation 线的下一层小修补。

## 有没有“可救信号”
**有，但主要只够确认旧 residual，不够打开新派生。**

### 1) 旧 residual 仍然存在：ATR 弹性回踩区 + bounce reclaim
`2026-03-18_0402_rank27b-atr-zone-park.md` 已经验证过：
- `atr_zone_bounce_reclaim`：
  - `mean_total_return≈-3.14%`
  - `positive_asset_ratio≈33.33%`
  - `mean_false_break_ratio≈58.42%`
  - `mean_trades≈66.3`

这说明：
- **把静态 retest_hold 改成 ATR 弹性回踩区 + bounce reclaim 这刀确实有信息；**
- 但它的改善主要是“更少假突破 / 更像 continuation”，还不足以把原线救成 queue-facing 可晋级对象。

### 2) 新证据 A：breakout 主题更像 event-driven raw alpha，不像 neckline 小修补
`2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md` 的价值在于：
- 它把“breakout 后续延续”直接上移成 **event-trigger overshoot + abnormal-regime veto** 的完整 raw-alpha family；
- 这类证据不再依赖 `neckline_confirm / retest_hold` 的局部语法；
- 它是在说：**如果要继续救 breakout continuation，更诚实的路径可能是换成 event-clock skeleton，而不是在 Rank 27 里继续叠新的回踩确认。**

### 3) 新证据 B：压缩突破活在更上位的 raw breakout family
`2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md` 进一步强化了同一方向：
- breakout 主题仍值得研究；
- 但更像应该先在 `compression -> breakout -> expansion continuation` 这样的 raw alpha 身份下验证；
- 而不是再把 `Rank 27` 这条旧的 neckline/retest 血缘继续细切出 `Rank 27c`。

**这两条新证据的共同含义是：**
- 可救信号依然存在，但它越来越像“breakout 主题上移到新 family”，不是“原 Rank 27 还缺一刀没试”。

## 最值得改的唯一一刀是什么
如果今天只允许保留 **1 条唯一主修改轴**，答案仍然是旧答案：

**把静态 `neckline retest_hold` 改成 `ATR-scaled retest zone + bounce reclaim`。**

但这条一刀已经被 `Rank 27b` 消费过：
- 它是原 Rank 27 唯一自然、唯一诚实、且最贴近 blocker 的单轴改写；
- 目前没有看到比它更自然、又不滑向第二轴大改的新切口。

所以本轮最重要的判断不是“新的唯一一刀是什么”，而是：
- **唯一值得改的一刀仍然是旧的一刀；**
- **既然这一刀已经被审过且仍未过线，就不诚实再写 `Rank 27c`。**

## 是否值得形成新的 derived hypothesis
- 结论：**不值得。**
- 本轮最终 verdict：`keep_park`

原因：
1. 原 Rank 的唯一自然 residual 已被 `Rank 27b` 基本消费；
2. 3/28 与 3/30 的新 breakout 证据并没有给 `Rank 27` 打开一条新的 neckline / retest 单轴；
3. 相反，它们继续说明：**breakout 主题若要活，更像应上移到 event-driven / compression-breakout raw-alpha family，而不是把 Rank 27 再诚实派生成 `Rank 27c`。**

## trade on / trade off（为何不 draft）
如果现在硬写 `Rank 27c`，最像的写法只会是：
- `trade on`：继续保留 breakout continuation 主题，再叠一层 event-clock / compression / abnormal-regime / path filter；
- `trade off`：这已经不是原 Rank 27 的单轴小修补，而是换血缘、换骨架、换 family。

这正是本轮不 draft 的原因：
- 它会违反“每轮最多 1 条唯一主修改轴”；
- 也会模糊原 `park` verdict 的审计意义。

## 本轮最终判断
- 原 rank 为什么 park：因为 `neckline_confirm / static retest_hold` 没有同时做到收益改善与假突破显著下降；
- 更像 `hard park` 还是 `soft park`：`soft park，但比 2026-03-23 更偏硬`；
- 有没有可救信号：有，主要仍是既有 `Rank 27b` 那条 residual；
- 最值得改的唯一一刀：仍是 `ATR-scaled retest zone + bounce reclaim`；
- 是否值得形成新的 derived hypothesis：`不值得`；
- 本轮结论：`keep_park`。

## 对 queue 的实际含义
- `Rank 27` 原 `park` verdict 继续保留。
- `Rank 27b` 仍是它唯一自然、且已被审计过的窄派生；当前不新增 `Rank 27c`。
- 3/28 与 3/30 的新证据只说明：**breakout 主题的残余价值更像上移到 event-driven / compression-breakout raw-alpha family，而不是继续在 Rank 27 血缘里细切。**
- 默认不改 `docs/TODO.md` 顶部排班。

## Git / 提交说明
- 本轮不做 git commit。
- 原因：工作区存在大量与本轮无关的共享脏文件，而且 `docs/PARK_REFRAME_QUEUE.md` 已处于共享修改态，当前不适合安全 selective commit。
