# 2026-03-21 00:30 UTC · Rank 32 park reframe revisit

## Source
- source rank: `Rank 32 EMA structure vs MA slope direction gate`
- source evidence:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
  - `research/optimization_loop/2026-03-17_1123_rank32-clean-replication-park.md`
  - `research/optimization_loop/2026-03-18_0135_rank32b-clean-replication.md`
  - `research/optimization_loop/2026-03-18_0236_rank32b-scope-promotion.md`
  - `research/strategy_review/2026-03-21_0023_strategy-review.md`
  - `reports/site/factors/scout_rank32b_slope_floor_continuation_15m/report.html`

## Why this revisit now
- 按默认规则，最近 `7` 天已复盘过的 rank 应尽量不重复看；但 `Rank 32` 这次有**实质新证据**：
  1. 先前 bot6 已为它派生出 `Rank 32b`；
  2. `Rank 32b` 随后已完成 clean replication、promotion honesty，并进入 `P3 hosted narrow paper continuity`；
  3. 最新 strategy review 显示它仍被托管刷新，但当前只是 continuity sidecar，不占主 `Scout Seat`。
- 因此本轮要回答的不是“原 Rank 32 能不能翻案”，而是：**在 `32b` 已经消费掉最自然那一刀之后，`Rank 32` 还值不值得再派生一个新的、更窄的 `32c`。**

## 1) 原 rank 为什么 park？
原 `Rank 32` 被 park，不是因为主题全错，而是因为**冻结形态的职责层和样本密度不够诚实**。

原 clean replication 的关键信号：
- `ema_cross_only @ 6bps/side`：`mean_total_return≈-18.73%`、`positive_asset_ratio=1/3`、`mean_trades≈257.3`
- `ema_cross_plus_slope_floor @ 6bps/side`：`mean_total_return≈+50.76%`、`positive_asset_ratio=3/3`、`mean_trades≈75.7`
- `ema_cross_plus_slope_reclaim @ 6bps/side`：`mean_total_return≈+24.79%`、`positive_asset_ratio=3/3`、`mean_trades≈25.0`、`mean_no_trade_ratio≈99.78%`

所以原 rank 的真实 park 原因很清楚：
1. `cross_only` 太弱，说明“EMA cross 本身”不够；
2. 真正有信息量的部分更像 `aligned slope floor`；
3. 但原主变体 `slope_reclaim` 把样本压得过稀，不适合直接作为 queue-facing 候选保留。

结论：原 `park` verdict 仍有审计价值，不能被后续派生成功偷改成“原 Rank 32 其实没 park”。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因不是因为它已经“洗白”，而是因为：
- 原线确实存在可救 pocket；
- 失败点更像是**把 slope 主题包在了过严的 reclaim 形态里**，而不是 slope / continuation 主题彻底无效；
- 后续 `Rank 32b` 的 clean replication、scope promotion 与 hosted continuity，也进一步证明原 rank 不是 hard fail。

但这里的 soft，不等于“可以无限续派生”。

## 3) 现有证据里是否存在“可救信号”？
**有，而且这条可救信号已经被 `Rank 32b` 消费掉了。**

最明确的可救信号只有一条：
- 真正贡献 edge 的更像 `aligned slope floor`；
- `spread-mid reclaim` 更像把 trade density 压得过稀的附加句。

这也是为什么 `Rank 32b` 当时是一条诚实的派生：
- 它只改了一刀：`remove spread-mid reclaim requirement; keep EMA cross + aligned slope floor`；
- 没有偷带新 universe / 新 exit / 新 regime stack。

而且从后续证据看，这一刀没有塌：
- `Rank 32b` clean replication 站住；
- promotion honesty 站住；
- 之后还进入了 `P3 hosted narrow paper continuity`；
- 最新 strategy review 里仍被当作 hosted lane 托管，只是当前 `flat / none`，并未被写成新的主 seat。

所以当前更诚实的判断不是“还藏着第二条更值得救的轴”，而是：**最自然、最有信息量的那条轴已经被提炼成 `32b`。**

## 4) 最值得改的唯一一刀是什么？
如果今天重新站在原 rank 面前，最值得改的唯一一刀仍然是：

**去掉 `spread-mid reclaim`，只保留 `EMA cross + aligned slope floor`。**

但这条唯一主修改轴已经存在，名字就叫：`Rank 32b`。

因此本轮不能再硬造第二刀。任何进一步的 `32c` 候选，当前都会明显滑向以下不诚实方向之一：
- 再加 execution/exit（那已经不是原 rank 的单轴 reframe，而是 deployment 层研究）；
- 再扩 universe（那是 promotion / expansion，不是 park reframe）；
- 再改风控或时钟（那会变成新的多轴策略）。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因不是原 rank 没有救，而是：
- 原 rank 最自然的一刀已经被 `Rank 32b` 抽出来；
- 新证据也主要是在证明 `32b` 这条派生足够成立，可以继续作为 hosted continuity lane 观察；
- 这些新证据**不构成新的唯一主修改轴**，因此不应再派生 `Rank 32c`。

## 6) trade on / trade off（为何不再派生）
### 这次保留的 trade on
- 保留原 `park` verdict 的审计意义；
- 承认原主题是 `soft park`，且最佳救法已被 `32b` 消费；
- 不把 deployment / execution / cross-asset 扩展误写成新的 park-reframe 轴。

### 这次明确放弃的 trade off
- 不为了“看起来有推进”而硬造 `32c`；
- 不把 `32b` 的 hosted continuity 成功，反向解释成“原 Rank 32 还值得再继续拆更多派生”；
- 不把后续 exit / OCO / maker-first / cross-asset 扩展误当作新的 source-rank reframe。

## Final verdict for this round
- round verdict: **`keep_park`**
- source-rank historical verdict: **keep original `park` unchanged**
- soft/hard reading: **`soft park`**
- why no new derived hypothesis: **最佳单轴救法已被 `Rank 32b` 消费，当前没有第二条同样诚实、且不多轴漂移的新修改轴。**

## Bot2-ready one-line takeaway
`Rank 32` 继续保留原 park；它更像 soft park，但最自然的窄救法（删 reclaim、只留 slope floor）已经被 Rank 32b 消费并进入 hosted P3 continuity，因此当前不再重复派生 Rank 32c。

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区脏文件很多，当前不适合安全 selective commit。
