# bottom-quartile BB compression breakout — fresh intake first verdict (`background/P0`)

- Time: 2026-03-30 13:24 UTC
- Target: `bottom-quartile BB compression breakout`
- Source record: `research/quant_digests/2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`
- Action type: fresh intake first verdict
- Policy basis: 本轮只执行 `cycle_plan` 中当前最前的 pending 小点；只回答这条 `15m low-width BB compression -> band break -> short-window expansion continuation` 是否形成值得前排审理的独立对象。

## Verdict
本轮给出 **不进入前排，回 background/P0**，且 **不分配 Rank**。

## Why
当前 digest 已经把这条线的对象边界和最小诚实快检回答得足够清楚：

1. 对象主语是清楚的，确实不是泛 squeeze filter 或多策略投票壳，而是 `15m` 上 `BB(20,2)` 宽度落在最近 `50` 根 bottom quartile 后，价格向 band 外突破，赌短窗波动扩张 continuation；
2. `200-SMA` 在仓库里扮演的是方向过滤角色，`ATR*3` trailing stop、`30min` cooldown 和成本口径也都足够明确，所以“规则不清楚”不是问题；
3. 但公开 Binance perpetual `15m` proxy 的最小诚实快检已经直接给出负面 first-pass：近 `120d`、`next-bar open`、`3bps/side` 成本下，`BTC=-4.8%`、`ETH=-14.2%`、`SOL=-33.8%`；
4. `200-SMA` 过滤虽然能止血，但并没有把负 alpha 变正，说明 `bottom-quartile compression` 这一层目前更像 breakout 家族的 participation gate / vote leg，而不是值得独立占用前排资源的 standalone raw alpha；
5. 因此这条 fresh intake 不满足 `keep_P1` 门槛，本轮应直接诚实收口到 `background/P0`，而不是再给 survivor 锁位。

## Runtime consequence
- 不进入 `keep_P1`
- 不分配 `Rank`
- 不占用 `Surviving candidate slot`
- 不进入 `Active P2`
- 直接记入 `Background pool`

## One-line result for state writeback
`bottom-quartile BB compression breakout` 这条 fresh intake 虽然对象边界清楚、`15m / 200-SMA / ATR*3 / 成本` 口径完整，但公开 `15m` proxy 已显示其更像 breakout 家族的 participation gate 而非可独立前排审理的 standalone raw alpha，因此本轮直接 `不进入前排，回 background/P0`。
