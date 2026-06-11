# 2026-04-09 15:37 UTC — Rank 18b fresh intake first verdict

## 本轮执行对象
- target: `research/park_reframe/2026-03-21_1815_rank18-park-reframe.md`
- action: 作为当前唯一 pending 的 fresh intake，判断 `Rank 18b / standalone EMA plateau-consensus entry -> shared abstain / trend-readiness veto gate` 是否已足够升成独立、queue-facing 的 abstain-gate pocket，还是仍只是既有 shared overlay family 的一个宿主实例。

## 读到的最关键原证据
1. `research/optimization_loop/2026-03-17_0309_rank18-clean-replication-park.md`
   - `plateau_vote_5of9_spread_guard` 在 `BTC/ETH/SOL 15m` 上 `mean_total_return ≈ -19.89%`
   - `positive_asset_ratio = 0/3`
   - `mean_trades ≈ 157`
   - `mean_no_trade_ratio ≈ 68.48%`
   - 这说明原始 `Rank 18` 作为 standalone entry 是硬失败，不是“差一点”。
2. `research/quant_digests/2026-03-20_0539_alpha-beta-abstain-profit-window-verdict.md`
   - 新增证据确实支持“少做低位移/极端冲击段”的 shared abstain 语义；
   - 但这份 digest 本身就是把 abstain / veto 当成三条主线共用 admission/filter 层，而不是某个新 raw pocket。
3. 仓内既有 family 检索结果
   - 已存在多条直接同类的 shared overlay / no-trade / trend-readiness 证据：
     - `2026-03-19_0055_adx-er-price-only-trend-readiness-gate.md`
     - `2026-03-19_2110_ema-slope-ntz-reentry-veto-gate.md`
     - `2026-03-23_0503_tc-waterfall-participation-tradeability-veto.md`
     - `2026-03-13_0932_threshold-no-trade-band-confirmation.md`
   - 这些对象已经把“trade / no-trade / readiness / veto”读成 shared overlay family，而不是新的 queue-facing pocket。

## 本轮判断
`Rank 18b` 的唯一修改轴虽然干净——把 standalone EMA plateau-consensus 降级成 shared abstain / trend-readiness veto gate——但这一步并没有形成一个新的、不可被现有 shared overlay family 吸收的独立 pocket。

更直接地说：
- 它证明的是“Rank 18 不该当 entry，而该当 veto/filter”；
- 但我们现在已经有更通用、宿主无关的 `no-trade / trend-readiness / veto` family；
- `Rank 18b` 没有给出一个比这些既有 shared overlay 更独特的触发语义、宿主绑定、或 honesty 优势；
- 它更像“EMA plateau 共识”这个具体实现，作为 shared overlay family 的单一宿主实例，而不是值得保留前排资源的独立 fresh intake pocket。

## First verdict
- verdict: `background / P0`
- result: `Rank 18b` 没有把旧 EMA-neighborhood-consensus park 压成独立 pocket，而只是把 standalone 负 alpha 改写成既有 `no-trade / trend-readiness / veto` shared overlay family 的单一宿主实例，因此 first verdict 直接收口为 `background / P0`。
- status: `done`

## 为什么不是 keep_P1
`keep_P1` 需要它已经压出“现有 family 还没吸收掉的独立系统认知增量”。本轮没有看到：
- 不是新的 raw alpha；
- 不是新的 queue-facing execution shell；
- 也不是现有 veto family 中唯一不可替代的 honesty blocker。

所以它只值得留作背景证据，不值得继续占用 front-slot fresh intake 资源。
