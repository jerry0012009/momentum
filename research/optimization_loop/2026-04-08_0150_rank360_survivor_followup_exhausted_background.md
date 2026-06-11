# Rank 360 / rest-of-window impulse × close-pocket continuation / survivor follow-up exhausted -> background

- Time: 2026-04-08 01:50 UTC
- Operator: bot3 auto loop
- Source digest: `research/quant_digests/2026-04-08_0056_rod-closepocket-hedgingmomentum-alpha.md`
- Prior state: `Surviving candidate slot`
- Verdict: `keep_P1 exhausted -> background`

## What changed system truth
`Rank 360` 的唯一一次 survivor follow-up 已诚实收口：当前对象仍可作为一个有意思的 `event-clock pocket alpha` 研究想法存在，但**还没有压清足够把它推进到 `P2` 的 crypto-specific 决定性证据**。现有材料只证明了它在传统多资产期货上的论文机制与 clean-room 实验壳，并没有给出 `BTC/ETH perp` 在 `20:00 UTC close pocket` 上相对 plain intraday momentum 的 after-cost 独立增量、真实时钟锚点稳定性、或最小执行壳结果。因此本轮不能诚实写成 `promote_P2`，而应写成 `keep_P1 exhausted -> background`。

## Why this does not promote to P2
- 当前证据仍停在**机制迁移 + 实验定义**，不是 crypto 复刻结果；没有任何 `BTC/ETH` 的 pocket return、post-cost Sharpe、avg trade 或 hit-rate 读数。
- 对象的核心主张是 `pre-close cumulative return -> close-pocket continuation`，但目前没有证明 `20:00 UTC / U.S. cash close` 在 crypto 中确实对应稳定的 ETF / options / hedge flow，而不是任意切出来的伪时钟。
- 相对 `plain intraday momentum` 的独立职责也还没压清。现有 digest 只能说明“这可能是 event-clock shell”，不能证明它不是把普通日内动量换到一个更窄的持有窗口。

## Why it is still a real idea, just not front-slot worthy now
- 这条线的价值仍然存在：它明确把对象归类为 `真实外部时钟驱动的 close-pocket continuation`，而不是泛 breakout / seasonality。
- 但目前项目里能找到的相近 `event-clock` 证据，更多是在提醒**时钟效应高度 venue/regime-specific**。例如 `turn-of-the-candle` 主题虽然在论文里成立，但在当前 Binance 映射已转负；这反而强化了一个结论：没有当前 crypto 口径的最小 transfer check，就不该把 `Rank 360` 升到 `P2`。
- 因为 survivor 只允许 1 次 follow-up，而这次 follow-up 仍未产出改变层级的 crypto 证据，所以更诚实的收口是退回背景池等待未来明确 reopen，而不是继续占前排资源。

## Explicit decisive blocker
唯一决定性 blocker 是：**缺少当前 crypto 真实时钟锚点下、相对 plain intraday momentum 的 after-cost 独立增量证据**。在没有这条证据前，`Rank 360` 不能进入 `P2 admission`。

## Runtime write-back required
- `Surviving candidate slot` 清空为 `none`，因为 `Rank 360` 的唯一 follow-up 预算已用尽。
- `Background pool` 最新 parked 对象更新为 `Rank 360`。
- 本轮小点结果写为：`Rank 360：survivor follow-up 已诚实收口；close-pocket continuation 在 crypto 里仍缺少相对 plain intraday momentum 的 after-cost 独立增量与真实时钟锚点证据，因此 keep_P1 exhausted -> background`。
