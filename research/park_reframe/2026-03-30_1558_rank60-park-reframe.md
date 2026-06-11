# 2026-03-30 15:58 UTC — Rank 60 park reframe review

## 为什么这轮看 Rank 60
- 继续遵循 `bot6` 轮转：当前默认优先 `Rank 50+`。
- 最近 `7` 天内已被 `bot6` 复盘的 `50+` 号段主要集中在 `50/51/52/54/55/56/57/58/59/61/62/64/67/76/83/86/87/96/97/101/104/105/106/110`，`Rank 60` 尚未进入 `park_reframe` 复盘队列。
- 因此本轮选 `Rank 60 / FVG-BOS imbalance retest gate`，只做一次低频复盘，不改主 TODO 排班。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_1656_rank60-source-intake.md`
- `research/optimization_loop/2026-03-18_1722_rank60-clean-replication-park.md`

## 1) 原 Rank 为什么 park？
原 Rank 60 想表达的是：
- 先出现 `confirmed BOS`；
- 再等价格回踩同向 `FVG / VI imbalance zone`；
- 若回踩后仍站在正确一侧，就把它当成共享的 continuation gate，去服务 `ema_psar_long / fib_retest_long / breakout_short`。

但最小 clean replication 给出的结论很直接：
- `bos_only` 没有形成跨 setup 的稳定增量；
- `bos_fvg_retest` 看起来只是在少数 long setup 上“少亏”，但主要来自极端砍样本；
- `bos_vi_retest` 基本没有形成可用样本；
- `breakout_short` 上也没有出现足以改写结论的稳定改善。

原文里最关键的硬证据是：
- `ema_psar_long`：`base≈-3.68%` → `BOS+FVG≈-0.11%`，但 `mean_trade_count_retention≈6.67%`
- `fib_retest_long`：`base≈+1.17%` → `BOS+FVG≈+0.28%`，但 `mean_trade_count_retention≈9.09%`
- 同时 `winner_truncation` 很高（约 `91.3% / 83.8%`）
- `breakout_short`：`base≈-3.55%` → `BOS+FVG≈-3.25%`，正资产占比仍然不够，不能改 verdict

所以它被 park 的核心原因不是“概念完全不可枚举”，而是：
**FVG / VI retest 没证明自己提供了可迁移的 shared continuation 增量，更像通过极端收缩样本制造了看起来较少亏的假改善。**

## 2) 它更像 hard park 还是 soft park？
我会把它定为：**soft park，但已经很偏 hard**。

原因：
- 不是 classic hard park，因为它至少有清楚、可复现、无明显前视的事件定义；
- 但 clean replication 已经把最自然的一刀（`BOS only / BOS+FVG / BOS+VI`）审得很清楚，而且失败点非常集中：**保留率太低 + winner truncation 太高**；
- 这意味着它不像“再补一点实现细节就能活”，而更像“该语义放在 shared 15m continuation gate 这个岗位上就是太贵、太稀、太像切样本”。

所以它不是绝对 hard park，但已经比一般 soft park 更接近“别再围着原命题打转”。

## 3) 现有证据里有没有可救信号？
有，但只剩很薄的残余：
- `BOS+FVG` 在 long 侧确实出现过“少亏 / 保留一点 pocket”的迹象；
- 说明 **post-break imbalance retest** 这个主题并非完全无信息；
- 但这点信息没有证明自己适合做三条 setup 共用的 shared gate。

更重要的是，最近几天的新证据大多在把同主题往别的家族上移：
- `2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`：更像 event-driven breakout verdict / overshoot family；
- `2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`：更像 compression breakout raw-alpha family；
- `2026-03-29_2242_trend-pullback-correlation-shell-alpha.md`：更像完整 continuation × pullback skeleton，而不是某个共享 imbalance retest 小 gate。

这几条旁证共同说明：
**主题没死，但活下来的更像上位的 event-driven / raw-alpha continuation family，不像原 Rank 60 这种 15m shared imbalance retest gate。**

## 4) 最值得改的唯一一刀是什么？
如果硬要说唯一一刀，最自然的其实只有：

**把 shared `BOS+FVG retest` gate 降级成 long-side second-chance / hold-quality context，而不是三线共用 continuation gate。**

但这刀并不值得再单独派生，原因有二：
1. 它和现有残余提案已经高度重叠：
   - `Rank 27b`（ATR-scaled retest zone + bounce reclaim）
   - `Rank 64b`（long-side hold-quality / admission score）
   - `Rank 101` 的 long-side volume-drydown / hold-quality residual note
2. Rank 60 自己最核心的“imbalance retest”独特点，并没有在 clean replication 里证明它比这些近邻更独立、更强、更不可替代。

换句话说，唯一还能切的一刀不是没有，而是**已经被更诚实的相邻血缘基本吸收**。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

本轮结论：`keep_park`

原因：
- 原 verdict 应保留，审计意义明确；
- 最自然残余并没有形成新的、足够独立的单一修改轴；
- 若现在再写 `Rank 60b`，大概率只是在重复讲 `Rank 27b / 64b / 101` 已经讲过的 long-side retest / hold-quality 故事；
- 最近新证据也更支持把该主题上移到更完整的 event-driven / breakout-continuation raw-alpha family，而不是继续在原 Rank 60 血缘内做 queue-facing 窄派生。

## 6) trade on / trade off（若硬派生会是什么）
本轮不 draft 新假设，因此这里只记录为什么不写：
- **trade on**：若继续写，会落成“long-side second-chance retest / hold-quality context”；
- **trade off**：但这会进一步丢失 Rank 60 原本最独特的 `imbalance zone` 叙事，并与 `Rank 27b / 64b / 101` 严重重叠，缺少独立存在的必要。

所以本轮选择不派生，比硬写一个重复提案更诚实。

## 最终结论
- `Rank 60` 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 60 不是完全没信息，但它留下的那点 residual value 更像已经被 long-side retest / hold-quality 近邻提案吸收；最近新证据也继续把主题上移到更上位的 breakout/event-driven raw-alpha family，不诚实再派生 Rank 60b。**

## 队列写回
建议在 `docs/PARK_REFRAME_QUEUE.md` / `research/park_reframe/INDEX.md` 中登记为：
- `2026-03-30 15:58 UTC | Rank 60 | verdict=keep_park | original verdict kept=park | note=soft park，但已很偏 hard；FVG/BOS imbalance retest 留下的薄弱 long-side residual 已被 Rank 27b / 64b / 101 一类 retest / hold-quality 提案基本吸收，最近新证据也继续把主题上移到 event-driven / compression-breakout raw-alpha family，当前不诚实再派生 Rank 60b`

## Git / 风险备注
- 本轮只做最小必要文件改动。
- 当前工作区长期存在大量与本轮无关的脏文件；为避免混提，本轮不做 commit。