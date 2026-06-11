# 2026-04-02 09:09 UTC · Rank 24 park reframe review (revisit)

## Scope
- Source rank: `Rank 24 / trend regime filter / trend-strength-over-noise gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，最近新增的 `MA / breakout raw alpha × bubble-state gate × cost ladder` 证据，是否足以让 Rank 24 再诚实派生一条新的窄 reframe hypothesis。**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-04-02_0712_rank30-park-reframe.md`
  - `research/park_reframe/2026-04-02_0456_rank53-park-reframe.md`
  - `research/park_reframe/2026-04-02_0246_rank18-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0549_rank24-clean-replication-park.md`
  - `research/park_reframe/2026-03-24_1227_rank24-park-reframe.md`
  - `research/quant_digests/2026-04-01_1811_ma-breakout-bubble-gated-trend-alpha.md`

## Why this rank this round
- 本轮按用户限定，只在 `Rank 1~37` 的已 parked 条目里选 1 条。
- `Rank 24` 上次由 bot6 复盘是 `2026-03-24 12:27 UTC`，已超过 7 天。
- 最近新增的 `MA / breakout × bubble-state` digest 与它的“trend regime / trend-strength-over-noise”主题最接近，具备一次低频 revisit 条件。

---

## 1) 原 rank 为什么 park？
原 `Rank 24` 被 park 的原因依然很清楚，而且这轮没有被新证据推翻。

根据 `2026-03-17_0549_rank24-clean-replication-park.md`：
- `baseline_mtf @ 6bps/side`：`mean_total_return ≈ -38.69%`，`positive_asset_ratio = 0/3`
- `trend_regime_default`：`mean_total_return ≈ -28.29%`，`positive_asset_ratio = 0/3`，`mean_no_trade_ratio ≈ 65.24%`
- 最好的一档 `stricter_trend_threshold`：`mean_total_return ≈ -9.81%`，也只有 `positive_asset_ratio = 1/3`
- 时间桶虽有零散正 pocket，但没有形成跨资产可复用的稳定 pocket
- 参数邻域没有给出稳定平台
- 成本梯度继续恶化：`10/15/20bps ≈ -43.31% / -57.57% / -68.10%`

翻成人话：
- `Rank 24` 不是“差一点就能升格”；
- 而是把趋势状态/市场状态写成 `15m` 的 standalone gate 后，确实能少亏，但仍然没有形成 after-cost、跨资产、跨时间都站得住的可交易对象；
- 所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**这轮仍读作 `soft park`，但已经明显偏硬。**

为什么还不是 hard park：
- 它相对 baseline 有一致的“少亏”改善，说明 `trend-strength-over-noise` 这种状态语言不是纯噪声；
- 也确实留下过少量局部正 bucket，说明状态主题本身未死。

为什么已经偏硬：
- 最好的结果仍然主要停在“减亏”而不是“转正”；
- `positive_asset_ratio` 最高也只有 `1/3`；
- 成本梯度恶化非常陡，说明这不是靠再调一个小阈值就能活的东西；
- 换句话说，残余价值更像“主题没死，但原角色定义不对”。

## 3) 现有证据里是否存在“可救信号”？
**有，但它更像支持新的 trend raw-alpha family，而不是支持 `Rank 24b`。**

### 可救信号 A：趋势家族没死
`2026-04-01_1811_ma-breakout-bubble-gated-trend-alpha.md` 给出的最重要信息是：
- `MA / breakout` 价格型趋势信号本身仍值得做；
- 真正诚实的写法是把它作为 **raw alpha**，再配上 `bubble-state gate + cost ladder` 的完整策略壳。

### 可救信号 B：market/trend state 仍有价值，但更像 regime 壳，不像原 Rank 24 的 standalone gate
这和 Rank 24 有相邻性：
- 原 Rank 24 试图把 `trend regime / trend-strength-over-noise` 写成核心 gate；
- 新 digest 则更明确地把状态层放回它该在的位置：**raw alpha 是 MA / breakout，state 只是决定什么时候更值得做、做多大。**

问题在于，这条新证据的落脚点已经不是“把旧 Rank 24 再磨细一点”，而是：
- 重新起一条更完整的趋势 raw-alpha 家族；
- 或至少把 state 从主角降回 regime gate / sizing overlay。

这已经超出了对旧 `Rank 24` 的窄 reframe 范围。

## 4) 最值得改的唯一一刀是什么？
**如果只允许保留唯一主修改轴，最值得改的一刀是：把 `trend regime / trend-strength-over-noise` 从 standalone gate，降级成 `MA / breakout` raw alpha 的慢变量 regime gate。**

也就是：
- 不再让 state/filter 自己承担主要策略职责；
- 主语换成 `MA / breakout continuation`；
- `Rank 24` 主题只保留为是否放行、降权、或禁做的慢变量状态层。

但这刀为什么仍然**不应直接写成 `Rank 24b`**：
1. 它把主语从 `gate` 改成了 `raw alpha + regime shell`，角色跃迁太大；
2. 这已经更像一个新的 family-level intake，而不是保留原 park 审计意义下的窄 rescue；
3. 若硬写成 `Rank 24b`，会模糊“原 Rank 24 的角色定义本身就错位”这一点。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` blocker 没有被化解：after-cost、跨资产、跨时间都仍不成立；
2. 新证据支持的是 `MA / breakout + bubble-state + cost ladder` 这条更完整的趋势 raw-alpha family，而不是旧 Rank 24 的窄修改轴；
3. 如果现在硬起 `Rank 24b`，实质上是在把“新 family intake”包装成“旧 rank 救活”，审计上不诚实。

## 6) trade on / trade off 怎么读？
本轮不新增派生，只做审计式复述：

- `trade on`：
  - 原 Rank 24 若还保留任何残余价值，只能读成一句更窄的话：**state 信息仍有用，但它更适合做慢变量 regime gate / sizing overlay，不该继续扮演 standalone alpha/filter 主角。**
- `trade off`：
  - 一旦把主语改成 `MA / breakout` raw alpha，再配 bubble-state / cost shell，你得到的已经是另一条更完整的新策略卡；
  - 这不再是对旧 Rank 24 的窄 reframe，而是换了 family-level 角色。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已明显偏硬`

## Minimal audit note
本轮不重开 `Rank 24`，也不新增 `Rank 24b`。

更诚实的记录是：**最近新增的 `MA / breakout raw alpha × bubble-state gate × cost ladder` 证据，说明趋势状态主题并未失效，但它更像在支持一条新的、以 `MA / breakout` 为主语的 trend raw-alpha family；不足以把旧的 `Rank 24 / trend regime filter` 再诚实派生成新的窄修改轴。**

## 本轮文件改动
- 新增本日志：`research/park_reframe/2026-04-02_0909_rank24-park-reframe.md`
- 更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`

## git / 提交
- 本轮仅做最小必要文档改动。
- 未做 commit（共享工作区无关脏文件较多，避免混提）。
