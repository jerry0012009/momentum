# Rank 227 / stablecoin signed-flow shock path alpha — fresh intake 首轮判分：keep_P1

- 时间：2026-03-28 18:23 UTC
- 对象：`research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`
- 结论：`keep_P1`
- 新分配 Rank：`227`
- 本轮角色：fresh intake 首判

## 一句话结论
这篇 Digital Finance 论文留下的不是泛泛“stablecoin 市场更重要”的叙事，而是一条值得保留到前排做唯一一次 follow-up 的 **`BTC/ETH-USDT signed flow shock -> 短窗 continuation / decay 后 fade` 微结构 raw alpha path**；但我用 Binance Futures 公开 `1m` kline 代理做的最小快检显示，当前 BTC/ETH 上无论 continuation 还是 fade，**分钟 bar 级 proxy 的 gross edge 都太薄，扣掉 round-trip `4~6 bps` 后不成立**，因此本轮只够 `keep_P1`，还不能升 `P2`。

## 这轮做了什么
按当前 `cycle_plan` 执行这条 fresh intake，目标不是复述论文，而是先回答它对当前 desk 到底意味着什么：
1. 它是不是一条独立的 raw alpha，而不只是 generic order-flow 话术；
2. 它在 BTC/ETH major 上，是否已经有足够便宜、足够诚实的公开数据迹象，说明 `1m/3m` continuation 或 `5m/15m` fade 至少有一段能活过现实成本；
3. 若不能直接过线，它是否仍值得保留 1 次 survivor follow-up。

我做的最小 public-proxy 口径是：
- 数据：Binance USDⓈ-M Futures 公共 `1m` klines，最近 `4500` 根 bars，`BTCUSDT / ETHUSDT`
- flow proxy：`imbalance = (2*taker_buy_quote - quote_volume) / quote_volume`
- 标准化：`240` bar rolling z-score
- shock 定义：`|z| >= 2` 且当根 `1m` 收益方向与 `z` 同向
- continuation：下一根开盘入场，按 shock 方向持有 `1 / 3 / 5` 根 `1m`
- fade：若后续 `1~2` 根 flow 不再确认（`|z|` 明显回落或方向翻转），则反向持有 `5 / 15` 根 `1m`
- 成本门槛：round-trip `4 bps` 与 `6 bps`

## 最关键的快检结果
### 1) BTCUSDT：continuation gross 过薄，fade 也没站住
触发事件数：`123`

- continuation `1m`：平均 **`+0.738 bps`**，hit rate `49.6%`
- continuation `3m`：平均 **`+0.084 bps`**，hit rate `43.9%`
- continuation `5m`：平均 **`-0.230 bps`**，hit rate `46.3%`
- fade `5m`：平均 **`-0.611 bps`**，hit rate `39.5%`
- fade `15m`：平均 **`-2.628 bps`**，hit rate `50.0%`

翻成人话：BTC 这边并没有出现“先顺着走一小段、再稳定回吐”的可交易两段路径；至少在便宜 public-proxy 口径下，它更像 **论文机制没法直接转成分钟级 desk edge**。

### 2) ETHUSDT：有一点形状，但 still not enough
触发事件数：`125`

- continuation `1m`：平均 **`+0.689 bps`**，hit rate `49.6%`
- continuation `3m`：平均 **`+0.541 bps`**，hit rate `51.2%`
- continuation `5m`：平均 **`+1.077 bps`**，hit rate `49.6%`
- fade `5m`：平均 **`-1.060 bps`**，hit rate `48.8%`
- fade `15m`：平均 **`+2.205 bps`**，hit rate `55.8%`

ETH 比 BTC 稍微像一点，尤其 `15m` fade 有一点 gross 正值；但它仍然 **过不了 `4~6 bps` 现实成本门槛**，而且跨资产也不稳定，不能把单边小 pocket 误判成已可 admission 的 major-coin raw alpha。

### 3) 对当前系统认知的真正增量
这条 intake 最有价值的新增，不是“又发现 order flow 有用”，而是：

> **stablecoin signed-flow shock 对 desk 的诚实读法，不该是 generic `1m/3m` always-on continuation alpha；它更像一条需要 event-level 定义与 decay 状态机才能验证的窄 microstructure path。**

这和系统最近几条 microstructure 结论是同方向的：
- 秒级 / 事件级论文里的 directional edge，压成 major-coin 的 `1m` bar proxy 后，经常 gross 还在、净值先没；
- 如果还有可救部分，通常需要更窄的事件定义，而不是更宽的 bar 因子包装。

## 为什么不是直接 drop
1. **base alpha 仍然清楚。** 这条线不是泛 filter，而是明确的路径命题：`shock continuation -> non-confirmed decay fade`。
2. **公开 follow-up 仍然便宜可做。** 论文用 tick 数据，但 desk 的唯一下一步并不需要商业级深度，只要 public `aggTrades` / taker buy-sell proxy 就能先做 event study。
3. **当前失败主要是 proxy 太粗，不是逻辑完全自相矛盾。** 这轮失败的是“把它先压成 `1m` kline proxy 之后，major 上没有留下成本后净边”；还不能直接等同于“原始 trade-level shock path 完全不存在”。

## 为什么还不能直接升 P2
1. **BTC/ETH 同口径 quick check 没有给出成本后独立净增益。** 这是最硬的一票否决。
2. **cross-asset stability 不够。** BTC 和 ETH 的表现不一致，且 ETH 最像样的一段也只到 gross、没到净值。
3. **当前证据更像“需要更细事件定义”而不是“已经值得 admission”。** 如果现在硬升 `P2`，会把论文机制的可能性误判成已经被 public runtime 支撑的现实 alpha。

## 本轮正式 verdict
- `Rank 227 / stablecoin signed-flow shock path alpha`：**keep_P1**
- 保留原因：它留下了一条值得做一次便宜但 decisive follow-up 的 major-coin 微结构 path，不只是 market-impact 摘要。
- 不升 `P2` 原因：当前 `1m` kline proxy 在 BTC/ETH 上没有证明 continuation 或 fade 任一腿能诚实留下 after-cost 独立净增益。

## 唯一 survivor follow-up 应该回答什么
只做一次最小诚实检查：

> 用 public `aggTrades` / taker buy-sell volume 重建 **event-level signed-flow shock**，直接比较 `event shock continuation` 与 `shock-decay fade` 两条腿在 `BTCUSDT / ETHUSDT` 上的 `1m/3m/5m/15m` gross / net markout；若 event-time 版本仍过不了 `4~6 bps` 或无法给出稳定跨资产 pocket，就按 `keep_P1 后转 background` 收口。

## 对 runtime 的影响
- fresh intake 已正式判分并获得 `Rank 227`
- survivor 槽位应切换到 `Rank 227`
- `followup_budget_remaining = 1`

## 会改变系统认知的话
`Rank 227 / stablecoin signed-flow shock path alpha` 保留的是一条需要 `aggTrades` 级事件定义才能继续验证的窄 microstructure path；当前 major-coin `1m` kline proxy 上，continuation / fade 两条腿都没有留下能穿过 `4~6 bps` 的 after-cost 净边，因此本轮只够 `keep_P1`，不升 `P2`。
