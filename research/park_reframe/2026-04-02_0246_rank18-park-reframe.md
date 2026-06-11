# 2026-04-02 02:46 UTC · Rank 18 park reframe review (revisit)

## Scope
- Source rank: `Rank 18 / EMA neighborhood consensus / plateau-stable crossover`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，最近新增的 trend / breakout 家族证据，是否足以在既有 `Rank 18b` 之外，再诚实派生一条新的窄 reframe hypothesis。**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0309_rank18-clean-replication-park.md`
  - `research/park_reframe/2026-03-21_1815_rank18-park-reframe.md`
  - `research/quant_digests/2026-03-20_0539_alpha-beta-abstain-profit-window-verdict.md`
  - `research/quant_digests/2026-04-01_1811_ma-breakout-bubble-gated-trend-alpha.md`

## Why this rank this round
- `Rank 18` 属于 `Rank 1~37` 的已 parked 条目，且距离上次 bot6 复盘（`2026-03-21 18:15 UTC`）已超过 7 天。
- 它已经有一条既有窄派生：`Rank 18b = shared abstain / trend-readiness veto gate`。
- 最近又新增了一条容易让人误判为“可以继续救”的新证据：`MA / breakout raw alpha × bubble-state gate × cost ladder`。
- 本轮要回答的不是“趋势家族是不是值得继续做”，而是更窄的问题：**这些新证据是否真的属于 Rank 18 的延长线，还是它们其实已经更像新的 family-level raw alpha，而不是 Rank 18c。**

---

## 1) 原 rank 为什么 park？
原 `Rank 18` 被 park 的原因仍然非常清楚，而且没有被任何新证据推翻。

原 clean replication 的关键结果：
- `plateau_vote_5of9_spread_guard @ 6bps/side`：`mean_total_return ≈ -19.89%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 157.0`
- `mean_no_trade_ratio ≈ 68.48%`
- 成本梯度继续恶化：`10/15/20bps ≈ -29.36% / -39.63% / -48.42%`
- 参数邻域没有出现由负转正的平台稳定证据

翻成人话：
- `Rank 18` 不是“差一点就转正”；
- 而是 **把 EMA 邻域平台共识当成 standalone entry alpha** 这条路，在 BTC/ETH/SOL 15m 上已经被审计清楚：少亏一些，但仍然全资产为负；
- 它唯一留下的残余价值，更像“哪些时候不该做 / 少做”，而不是“什么时候该直接开仓”。

所以原 `park` verdict 必须保留，不能被这轮新 digest 推翻。

## 2) 它更像 hard park 还是 soft park？
**这轮仍读作 `soft park`，但已经比 3 月下旬更偏硬。**

为什么不是 hard park：
- `plateau_vote_5of9_spread_guard` 相对更粗的 `anchor_10_40` 确实少亏不少（约 `-30.21% -> -19.89%`）；
- 同时它天然带来较高 `no_trade_ratio`，说明“平台共识 / 不做低质量段”这件事不是完全没信息量。

为什么现在比之前更偏硬：
- 这点残余信息，已经被 bot6 在 `2026-03-21` 收敛成 `Rank 18b`；
- 最近新增的趋势 / breakout / bubble-gate 证据，并没有再提供一个属于 Rank 18 的第二条独立主轴；
- 也就是说，soft 的部分还在，但新增证据没有让它重新变宽，反而让“只剩 18b 这一刀”更清楚。

## 3) 现有证据里是否存在“可救信号”？
**有，但仍然只够支撑既有 `Rank 18b`，不够支撑新的 `Rank 18c`。**

### 可救信号 A：abstain 语义仍成立
`2026-03-20_0539_alpha-beta-abstain-profit-window-verdict.md` 仍然是最对位的旁证：
- 真正有价值的不一定是“更准地预测方向”，而是**把低位移段和过冲段排除掉**；
- 这与 Rank 18 的高 `no_trade_ratio` 很贴，说明它更适合被评估成 `abstain / veto layer`，而不是 standalone alpha。

### 可救信号 B：趋势家族未死，但更像新 family，不像 Rank 18 延展
`2026-04-01_1811_ma-breakout-bubble-gated-trend-alpha.md` 的结论也有价值：
- `MA / breakout` 作为 raw alpha 家族仍值得做；
- 但正确写法是 **raw alpha + bubble-state gate + cost ladder** 的完整策略骨架。

问题在于，这条证据的落脚点已经是：
- 重新做一条 price-only trend / breakout raw alpha；
- 再配 regime / cost 壳。

这和 Rank 18 的残余信息并不是同一层：
- Rank 18 的残余是“EMA 平台共识更像 abstain / trend-readiness veto”；
- 新 digest 的主角则是“MA / breakout 自身仍可作为完整 raw alpha family”。

所以它更像是**新的 family-level intake 线索**，而不是诚实的 `Rank 18c`。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然没有变化：把 Rank 18 从 standalone entry 降级成 shared abstain / trend-readiness veto gate。**

也就是既有的 `Rank 18b`：
- 不再让 `plateau_vote_5of9_spread_guard` 自己触发开仓；
- 只在现有已冻结 setup 触发时，用它判断 `allow / veto`（必要时再测 half-size，但第一刀优先 strict veto-only）；
- 不顺手改 entry/exit/universe，不偷带第二层 regime 或 bubble gate。

本轮最重要的判断恰恰是：
- **最近新增的 MA / breakout × bubble-state 证据，并没有让“唯一主修改轴”发生变化。**
- 一旦把 bubble-state / cost ladder 也塞进 Rank 18，就已经变成多轴大改，而且更像另起一条新 family，而不是 park-reframe。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更精确地说：
- 原 `Rank 18` 的 `park` 保持不变；
- 既有 `Rank 18b` 继续保留，且仍然是唯一诚实的窄派生；
- 本轮新证据不足以再派生 `Rank 18c`。

## 6) trade on / trade off 怎么读？
本轮不新增派生，因此这里只做审计式复述：

- `trade on`：
  - 如果将来要继续保留 Rank 18 的残余价值，最诚实的做法仍然是：只把 EMA 平台共识用于“少做低质量段 / 不在趋势还没站稳时贸然放行”，即 shared veto / abstain。
- `trade off`：
  - 交易数一定会下降；
  - 很容易滑向“砍单美化”；
  - 如果再叠加 bubble-state、breakout trigger、cost ladder，就已经不是同一条单轴 rescue，而是另一条完整 raw-alpha family 了。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已更偏硬`

## Minimal audit note
本轮不推翻 `Rank 18` 的原 park，也不新增 `Rank 18c`。
更诚实的记录是：**最近新增的 MA / breakout × bubble-state gate 证据说明趋势家族本身仍值得做，但它更像新的 family-level raw-alpha intake，不足以在既有 `Rank 18b` 之外，再为旧的 EMA plateau-consensus 派生新的窄修改轴。**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件，当前不适合安全 selective commit。
