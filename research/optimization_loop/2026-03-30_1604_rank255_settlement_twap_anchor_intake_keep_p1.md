# Rank 255 / settlement-TWAP anchor gap / Deribit near-expiry options — fresh intake first verdict (`keep_P1`)

- Time: 2026-03-30 16:04 UTC
- Target: `settlement-TWAP anchor gap / Deribit near-expiry options`
- Source: `research/quant_digests/2026-03-30_1426_deribit-expiry-twap-anchor-alpha.md`
- Action type: fresh intake first verdict

## What was checked

只执行当前 `cycle_plan` 的第一个 pending 小点，不扩题，不改 policy / brief / operating card / cron prompt。

本轮只回答一件事：`BTC 日度到期期权最后 30m 内，live option premium 向 settlement-TWAP anchor 收敛` 这条线，是否已经足够形成一个**独立前排对象**，还是仍然只是 near-expiry scanner / generic options monitor / 旧 parity 家族的换壳。

本轮直接依赖的已落地证据：

1. `research/quant_digests/2026-03-30_1426_deribit-expiry-twap-anchor-alpha.md` 已把对象主语压到很窄：
   - 事件窗：`expiry last 30m`
   - 交易主语：`live option premium -> settlement-TWAP anchor gap`
   - universe：`BTC`、近 ATM、日度 / 次日度到期链
   - 执行骨架：`entry / exit / sizing / risk / cost` 都已写明
2. repo `Option_Scraper.py` 明确把信号做成了一个可运行 monitor，而不是只停在叙述层：
   - `UPDATE_INTERVAL = 5`
   - `ROLLING_WINDOW_MINUTES = 30`
   - 用 `btc_usd` index 的 rolling average 作为实时 settlement proxy
   - 用当前 `mark_iv` + 剩余到期时间算 `our_price`
   - 直接对比 `market_price` vs `our_price`
3. digest 已补了 Deribit 公共 API 可得性核验：
   - 最近到期 BTC option universe 可公开查询
   - `public/get_last_settlements_by_currency` 可回填最终 settlement index / final mark label
   - 因此它不是依赖私有 feed 才能研究的黑箱题

## What changes system belief

这条线已经足够说明：**不要把它并回 generic options scanner，也不要并回 `Rank 253 / same-venue conversion / parity reversal`。它的 alpha 本体更窄：不是 put-call parity 修复，也不是跨腿 no-arb，而是“到期前最后 30 分钟，单合约 premium 向 settlement-TWAP fair anchor 收敛”的事件型 same-venue options raw alpha。**

当前最关键的可保留信息：

1. **对象边界独立。**
   - 不是泛 near-expiry heatmap；
   - 不是 cross-venue synthetic forward / parity；
   - 不是 generic vol timing；
   - 而是 `rolling settlement-TWAP proxy -> option fair value gap -> expiry-window mean reversion`。
2. **最小 honest 策略骨架已经清楚。**
   digest 已经写清：
   - 只在最后 `30m` 开机；
   - 优先近 ATM、连续报价、不做盘口真空腿；
   - `edge_t = model_price_twap - market_price`；
   - `|edge|` 需超过 fees + spread + latency + inventory buffer；
   - `|edge|` 收敛、最后 `1~2m`、或 rolling-TWAP 方向反转时离场；
   - 仓位按 premium-at-risk，而非名义 delta 乱放大。
3. **公开数据回填链条足够完整，值得保留为前排候选。**
   这不是只能靠作者私有数据库才能继续的对象；Deribit 公共 API 已足以支撑第一轮 frozen replication。

## Why it does NOT go straight to P2

虽然对象边界已经够清楚，但当前证据还不够诚实地直接升 `P2`，blocker 也很具体：

1. **repo 目前更像 fair-value monitor，不是 executable proof。**
   当前核心对比是 `mark_price` vs `our_price`，而不是 `best bid/ask` 或 conservative mid；若继续直接把 `mark gap` 当 edge，容易落入中价幻觉。
2. **还没有本地 frozen、post-cost replication。**
   digest 已给出研究切口和 friction ladder，但还没有用我们自己的公共数据样本回答：在 `best bid/ask` / conservative execution 假设下，最后 `30m` 的 gap 是否还能保住成本后 edge。
3. **short leg 的保证金与尾部风险尚未收口。**
   因此更诚实的下一步应是：同时做 `long-underpriced only` 与 `long/short` 双版本，先看不依赖裸 short 的版本是否还活。
4. **不同 strike 的 edge 仍需统一到可横比口径。**
   需要并排写成 BTC、美元与 premium-return 三种口径，否则容易把高价和低价 option 的绝对差额混读成同一层级的 edge。

因此，**这条线值得作为新的独立对象进入前排，但当前最诚实的 first verdict 只能是 `keep_P1`，不能直接 `promote_P2`。**

## Formal verdict

- Assigned rank: `Rank 255`
- Verdict: `keep_P1`
- Slot effect: 进入 `Surviving candidate slot`
- Required next decisive follow-up:
  - 只盯最后 `30m` 的近 ATM BTC 日度到期合约
  - 把 `mark_price` 升级成 `best bid/ask` 或 conservative mid
  - 并排比较 `long-underpriced only` 与 `long/short` 双版本
  - 强制 `fees + half-spread + latency` 的 friction ladder
  - 回答 frozen replication 在公开口径下是否仍留下可审计的 post-cost edge；若能保住，则可 `promote_P2`，否则收口回 `background/P0`

## One-line result

`Rank 255 / settlement-TWAP anchor gap / Deribit near-expiry options` 的 fresh intake 首判已完成：对象边界已清楚地锁定在 `BTC 日度到期期权最后 30m 内，live premium 向 settlement-TWAP anchor 收敛`，与现有 perp/funding 家族及 `same-venue parity` 家族独立，且 rolling-TWAP anchor、近 ATM universe、entry/exit/risk/cost 与公开 settlement label 回填链条已足够形成最小 honest 骨架；但因当前仍停留在 `mark/IV fair-value monitor`、尚缺 `best bid/ask` 口径的 frozen post-cost replication，本轮给 `keep_P1`，进入 survivor。
