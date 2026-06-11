# Rank 315 / cross-venue same-underlier spread close — survivor follow-up verdict = background/P0

- Time: 2026-04-03 18:58 UTC
- Target: `Rank 315 / cross-venue same-underlier spread close`
- Action: survivor one-shot follow-up (`symbol × venue-pair admission + maker/taker cost realism`)
- Verdict: `background/P0`

## What changed
这轮 survivor follow-up 把 `majors vs alt pocket` 与 `maker+maker / maker+taker / taker+taker` 放回同一个最小 honesty shell 后，runtime truth 已经比 fresh-intake 阶段更清楚：

> `Rank 315` 的 base alpha 仍然成立，但当前公开 `1m` close-proxy 快检里能看到的 surviving pocket 主要只剩 `SOL/alt venue dislocation` 这种薄毛边；其单笔 gross 只有约 `1.53bps`，不足以诚实覆盖任何常见的双腿 taker、甚至大多数 `maker+taker` 执行成本，因此现在还不能把它当作可净后存活的 desk-admission 对象。

## Evidence used
来自 intake digest 与本地 artifact `reports/artifacts/quant_digests/2026-04-03_cross-exchange-binance-bybit-arb-sanity.csv` 的统一口径结果：

- `BTCUSDT`
  - `median |spread| = 0.59bps`
  - `p95 |spread| = 1.55bps`
  - `>= 3bps` 触发占比仅 `0.02%`
  - 3 天仅 `1` 笔 toy-shell 信号，gross `0.60bps`
- `ETHUSDT`
  - `median |spread| = 0.56bps`
  - `p95 |spread| = 1.63bps`
  - `>= 3bps` 触发占比 `0.32%`
  - 仅 `3` 笔，mean gross `1.58bps`
- `SOLUSDT`
  - `median |spread| = 1.21bps`
  - `p95 |spread| = 2.53bps`
  - `>= 3bps` 触发占比 `2.01%`
  - `49` 笔，mean gross `1.53bps`，胜率 `75.5%`

这些数字足够回答 survivor follow-up 想问的那句关键问题：

1. **majors 没有可 admission 的 pocket**
   - BTC/ETH 在统一 `1m` close-proxy shell 下已经薄到接近“只剩偶发 inventory/latency pocket”；
   - 这不是可以直接升 `P2` 的稳定 desk pocket。

2. **alt pocket 虽存在，但还停留在 gross edge，不是净后 edge**
   - SOL 的确比 BTC/ETH 更像 surviving pocket；
   - 但当前可见 gross `~1.53bps/trade` 仍明显低于任一诚实 `taker+taker` 口径，也不足以默认覆盖大多数 `maker+taker` 成本与排队/撤单失败/盘口滑点。

3. **因此本轮不能诚实写成 `promote_P2`**
   - 这一步若继续保留在前排，下一步就只能要求更可交易的盘口/fee-tier/inventory 级证据；
   - 但对 survivor 的唯一一次 follow-up 来说，当前已经足够得出结论：**现有证据只能证明这是一条 execution-sensitive raw alpha，不足以证明当前 desk 下已有可净后存活的 `symbol × venue-pair` pocket。**

## Why this is not keep_P1 again
policy 已明确：survivor 只有一次最小 decisive follow-up。现在这次 follow-up 已经完成，而且它给出的不是“再看看”，而是一个会改变系统认知的明确结论：

- `same-underlier spread close` 不是假 alpha；
- 但当前公开数据所见 surviving pocket 仍太薄，尚不足以让它继续占用前排资源；
- 若以后要 reopen，前提应是拿到**可交易盘口 + 明确 fee tier / maker fill realism / inventory netting** 的新增证据，而不是继续重复 close-proxy 叙事。

所以这轮最诚实的 runtime outcome 是直接把 `Rank 315` 记入 `background/P0`，而不是在 survivor / P2 之间悬着。

## Result sentence
`Rank 315`：cross-venue same-underlier spread-close 的 raw alpha 仍成立，但当前统一 shell 下 surviving pocket 只剩薄的 alt/venue dislocation，gross edge 约 `1.5bps/trade`，不足以诚实覆盖可交易成本，因此 survivor follow-up 完成后直接收口到 `background/P0`。
