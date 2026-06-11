# EMA 线里别把 reclaim 当默认美学：对 15m 来说，保留 slope floor、删掉 reclaim，更像值得先测的 continuation 版本
- 时间： 2026-03-18 01:22 UTC
- 类型：GitHub / repo 派生假设
- 主题标签：ema/continuation/retest-hold/slope-floor/crypto/15m/scout
- 证据类型：repo clean-replication 证据 + park-reframe 派生假设

## 1. 这次看了什么
这轮没有继续围着 `Rank 17 / Rank 2 / Rank 29` 这些已托管的 `P3` 线打转，而是按最新 strategy review，重读了 `Rank 32 EMA structure vs MA slope direction gate` 的 clean replication、park reframe 与顶板排班，正式把 **`Rank 32b / slope-floor continuation gate`** 当成新的 digest 主题。

它比继续磨三条收口线更值得的原因很直接：当前三条里，`Rank 17 / Rank 2 / Rank 29` 都没有新的真实 `append/review need`；而 `Rank 32b` 正好在回答一个更贴近当前 desk 的问题——**15m 上，EMA 延续到底该不该强行再加一层“reclaim 美学”，还是只保留 slope-aligned direction state 就够了。**

## 2. 核心结论
- 原 `Rank 32` 最有信息量的，不是裸 `EMA cross`，而是 **`slope floor` 这层方向一致性**。
- 数据上看，`ema_cross_only` 太松：`6bps/side≈-18.73%`、`positive_asset_ratio=1/3`、`mean_trades≈257.3`，说明只看快慢线位置关系不够。
- 加上 `slope floor` 后，读法明显变干净：`6bps/side≈+50.76%`、`positive_asset_ratio=3/3`、`mean_trades≈75.7`。这说明 edge 更像来自“趋势方向 + 斜率同向”，而不是来自交叉本身。
- 但再加 `spread-mid reclaim` 后，虽然主变体仍是正的（`6bps/side≈+24.79%`、`3/3` 资产为正），交易数却被压到 `≈25.0`，`mean_no_trade_ratio≈99.78%`，已经稀到更像漂亮样本，而不像当前 15m fast lane 默认该推的执行口径。
- 所以下一步更值得测的，不是继续把 reclaim 写得更花，而是先诚实回答：**删掉 reclaim 之后，`slope_floor_only` 能不能在更高 trade density 下保住成本后 pocket。**

## 3. 为什么和当前项目有关
它直接服务两条当前收口线：
- **`EMA / PSAR raw alpha focus`**：这条线本质上是在拆 EMA 原始方向层，问“真正有用的是位置关系，还是 slope direction gate”。
- **`Fibonacci confirmation / retest_hold`**：`spread-mid reclaim` 本质上就是一种更苛刻的 mini retest/reclaim 过滤。原证据提示：如果 reclaim 只是把样本压稀，而没有带来更好的性价比，那 desk 以后看 `retest_hold` 也该先问“有没有真增益”，而不是默认觉得“更漂亮就更高级”。

换句话说，这不是脱离主线的新花样，而是在主线里把一个经常被美化的确认条件拆开，看它到底是在帮忙，还是在偷走样本。

## 4. 可复刻的最小实验
- **研究假设**：15m crypto 上，`EMA cross + aligned slope floor` 比 `EMA cross + slope floor + reclaim` 更适合作为 continuation gate，因为它能提高 trade density，同时不把跨标的成本后 pocket 全部冲掉。
- **最小定义**：
  - `cross_only`：`1h EMA fast > slow`（空头反向）+ 15m close 重新站回 fast EMA；
  - `slope_floor_only`：在 `cross_only` 基础上，再要求 `fast/slow slope` 同向且 `fast slope` 过最小门槛；
  - `slope_floor_plus_reclaim`：再额外要求最近 `4` 根里出现过一次向 `spread mid` 的回抽，并在当前 bar 重新站回正确一侧。
- **最小回测切口**：固定 `BTC/ETH/SOL`、`120d`、`15m`、`next-bar open` 入场、`hold 8 bars`、`non-overlap`、先看 `6/10/15bps`。
- **先看 4 个指标**：`post-cost total return`、`positive_asset_ratio`、`trade_count`、`no_trade_ratio`。

最关键的 yes/no 问题只有一个：**去掉 reclaim 后，收益虽然可能回落一点，但如果 trade count 从 `25` 提到接近 `75`，而跨标的仍不是一地鸡毛，那这条线就比原来的“漂亮但太稀”版本更像 desk 可推进的 continuation gate。**

## 5. 风险与保留意见
- 现在还不能把 `Rank 32b` 写成已经成立；它只是比 `Rank 35b` 更值得拿下一轮预算。
- `slope_floor` 当前仍有 `mean_no_trade_ratio≈99.34%`，所以就算删掉 reclaim，也未必真能把样本密度拉回到可推进区间。
- 另一种可能是：edge 本来就来自极稀的 reclaim pocket；如果真是这样，删掉 reclaim 之后结果会迅速退化到接近 `cross_only`。
- 因此这条线最怕的不是“收益没那么高”，而是 **trade density 上来以后，positive_asset_ratio 和成本后 pocket 一起塌。**

## 6. 一句话结论 + 它是怎么证明的
- **一句话结论**：当前更值得测的不是“更漂亮的 EMA reclaim”，而是“只保留 slope floor 的 continuation 版本”。
- **它怎么证明**：不是靠故事，而是靠同一套 `BTC/ETH/SOL 120d 15m` clean replication 里三档规则的直接对照：`cross_only` 太松、`slope_floor` 最像正 pocket、`slope_reclaim` 则把样本压得过稀。

## 7. 来源
1. 项目内 repo 派生来源（无 DOI / 无正式 venue）
   - 标题：`EMA structure vs MA slope direction gate`
   - 年份：2026
   - Repo path：`/root/clawd/jerry/momentum/src/momentum/signals/ema_donchian_breakout.py`
   - Readable page：`reports/site/reading/trendline_alpha_scout/rank32_ema_slope_structure_source_intake.html`
2. 原始 clean replication 证据
   - 标题：`Rank 32 · EMA structure vs MA slope direction gate`
   - 年份：2026
   - Readable page：`reports/site/factors/scout_rank32_ema_slope_structure_15m/report.html`
   - Supporting note：`research/optimization_loop/2026-03-17_1123_rank32-clean-replication-park.md`
3. 派生假设与当前排班依据
   - `research/park_reframe/2026-03-17_2022_rank32-park-reframe.md`
   - `research/strategy_review/2026-03-18_0112_strategy-review.md`
