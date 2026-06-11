# Rank 189 / Hyperliquid funding richest-vs-cheapest 4h crowding continuation — fresh intake keep_P1

- Time: 2026-03-26 22:19 UTC
- Target: `research/quant_digests/2026-03-26_2146_hyperliquid-funding-rich-4h-crowding-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned Rank: `189`

## Why this survives intake
本轮值得保留的不是整个 funding screener / carry dashboard，而是单一对象：

`current-funding richest-vs-cheapest 4h crowding continuation`

翻成人话：每小时冻结一次 Hyperliquid funding 横截面，做多 funding 最贵的 top bucket、做空 funding 最便宜的 bottom bucket，核心持有口径是 `4h`，且必须把未来 funding cashflow 和交易成本一起入账。

## Intake evidence that changed the system view
1. **sign 不是经典 cheap-vs-rich carry，而是 rich-funding continuation。**
   - `long richest / short cheapest` 在 `4h` 口径下仍为正；
   - 同样样本里的 `long cheapest / short richest` 明显为负。
2. **扣 funding cashflow 之后，这条线没有死掉。**
   - best config: `current funding` + `4h hold` + `rich_minus_cheap`
   - price PnL: `+19.39 bps / 4h`
   - funding cashflow: `-5.23 bps / 4h`
   - net after `8 bps` round-trip: `+6.16 bps / 4h`
   - net Sharpe ann: `~2.58`
3. **但它还不够直接升 P2。**
   - 当前样本基本只有近一个月；
   - 周度表现并非单周包办，但也出现过 `2026-03-02/03-08 = -1.33 bps / 4h` 与未完周近乎走平；
   - 仍未回答 edge 是否只是高 beta / 热门币 / 上新币 / sector crowding 的替身。

## Honest first verdict
所以这条线通过 fresh intake 的原因是：
- 它已经是一个**完整策略骨架**，而不是泛泛题材；
- 它给出与传统 carry 相反、但可复现且扣过 funding 后仍为正的 sign；
- 它值得一轮唯一的 cheap decisive follow-up，去回答这是不是独立 alpha，还是只是高 beta / sector / listing-age 暴露的伪像。

但本轮不直接升 `P2`，因为当前还缺一个便宜但关键的诚实检查：

> 把 `current funding richest-vs-cheapest 4h` 做最小 beta / sector / listing-age 去偏后，确认正 sign 是否仍留得住。

## Result sentence
`Rank 189` 的 fresh intake 已收口为 `keep_P1`：值得保留的是 `current-funding richest-vs-cheapest 4h crowding continuation` 这条单轴对象，而不是整个 funding carry screener；它在扣掉未来 funding cashflow 与 8bps 成本后仍留有正 net pocket，但尚未证明自己独立于高-beta/热门币暴露。
