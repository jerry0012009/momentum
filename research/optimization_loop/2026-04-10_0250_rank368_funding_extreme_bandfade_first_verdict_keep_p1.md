# Rank 368 — funding extreme × band-stretch fade fresh-intake first verdict: keep P1

- Time: 2026-04-10 02:50 UTC
- Target: `research/quant_digests/2026-04-10_0205_funding-extreme-bandfade-meanreversion-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned rank: `Rank 368`

## What changed system truth
`cross-exchange funding extreme × band-stretch fade shell` 不只是旧 `BB/RSI fade` 的低杠杆改写；在同壳最小对照里，`funding extreme` 作为 crowding admission gate 明显砍掉裸 stretch fade 的噪音交易，并把 `5m` lane 从成本后明显为负翻到成本后仍为正，因此当前应作为 `Rank 368` 保留在 `P1 / surviving candidate`，而不是直接打回 background。

## Why this is enough for first verdict
1. **独立 alpha 增量成立**
   - 同壳对照里，裸 `BB+RSI` 在 `15m` 与 `5m` 都过不了成本；尤其 `5m` 裸壳约 `4072` 笔，粗扣 `8bps/笔` 后约 `-25957bps`。
   - 加 `funding extreme` gate 后，`5m` 缩成约 `285` 笔，gross 约 `+4606bps`，粗扣后仍约 `+2326bps`，说明 funding 并不是装饰性 filter，而是在回答“这次 stretch 有没有 crowding 背书”。
2. **不是单纯 carry 家族重复**
   - 这里 funding 的作用不是收持有期 funding，而是把 funding 读成拥挤程度 proxy，再和带外 price stretch 组合成短线 snapback 触发；这和 `always-on funding carry / basis carry` 的兑现逻辑不同。
3. **目前没有单一 decisive blocker**
   - `15m` 不过成本，说明不能无脑全周期铺开；但 `5m` alt-heavy lane 已经给出正的成本后 first signal。
   - 当前 portability 只用 Binance 单 venue funding，是保守代理而非致命 honesty flaw；它更像限制信号密度与 universe transfer，而不是直接推翻 `crowding-conditioned mean reversion` 这个 pocket。

## What is still unresolved
- `BTC / XRP` 迁移偏弱，后续 survivor follow-up 应优先检验这是不是明确的 **alt-only scope**，还是对 symbol/threshold 极端敏感。
- 需要在下一次唯一 follow-up 里回答：若限定到 `ETH/ADA/DOGE` 或 liquid-alt 子集，`funding quantile` 与 `time-stop / exit` 是否仍稳定，避免把单次 `5m` 正结果误读成可广泛外推的统一模板。

## Slot effect
- Fresh intake 已完成首判并获得正式 rank：`Rank 368`
- 对象进入 `Surviving candidate slot`
- `followup_budget_remaining = 1`

## Reader-facing takeaway
这条线值得留一轮，但值得留下来的不是“funding 本身能预测价格”，而是更窄的命题：**拥挤 funding 极端能把原本会被趋势碾碎的 stretch fade，筛成在 `5m` alt-perp 上仍可能活过成本的一小撮 snapback 交易。**
