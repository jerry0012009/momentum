# bot3 optimization log — BTC book pressure / ETH lagged catch-up intake park
- Time: 2026-03-26 16:11 UTC
- Target: `research/quant_digests/2026-03-26_0950_btc-book-eth-divergence-catchup-alpha.md`
- Slot: `Fresh intake slot`
- Action: 最小首判
- Verdict: `park`

## Why this changes system belief
`BTC book pressure / ETH lagged catch-up` 当前更像一条值得留档的超短窗 microstructure 假设，而不是已经足够诚实进入 survivor 的 desk 级 raw alpha：repo 里的最强证据仍集中在 `XBT order-book -> ETH 200ms` 这种极短窗分类可检出性；而 digest 自带的 Binance `1m` 代理快检只有 `13` 个事件，虽然方向上留下了影子，但样本稀、执行窗被严重压粗、成本后可迁移性也还没有被证明。

## What I checked
1. digest 的核心对象是否明确：是，保留对象是 `BTC book pressure / ETH lagged catch-up` 这条 exact cross-asset lead-lag raw alpha，而不是泛化的“order-book lead-lag”。
2. 现有证据是否足够让它诚实进入 survivor：否。
   - repo 价值主要在于提出了 `BTC/XBT` 盘口特征可先于 `ETH` 短收益这条假设；
   - 但最强结果依赖 `200ms` 级 horizon 与真 `L2` 盘口特征；
   - 廉价 `1m` 代理 sanity check 只给出很弱的 stress-pocket 影子，离 desk 可执行对象还差关键一层。
3. 当前缺口是否只是小修小补：不是。
   - 要进入 survivor，至少要补齐真 `L2` 数据、`10s/30s/60s/180s` horizon 寿命曲线、以及 `fee/slip` 下的净边验证；
   - 这不是 fresh intake 首判阶段应默认继续前排占用的“便宜诚实 follow-up”。

## Exit decision
- 本轮 verdict：`park`
- 不分配 Rank
- 不进入 survivor
- 不进入 P2

## Result sentence
`BTC book pressure / ETH lagged catch-up` 首判收口为 `park`：当前有效证据主要还是 repo 内 `XBT order-book -> ETH 200ms` 的超短窗可检出性与 `1m` 代理下仅 `13` 个事件的弱影子，离可迁移、可执行、可诚实保留为 survivor 的 desk 级 raw alpha 仍差一整层 `L2 + finer-horizon + cost` 验证。
