# Rank 278 — survivor follow-up — coin-normalized whale continuation — background/P0

- 时间：2026-04-01 05:06 UTC
- 执行轮次：bot3 13m auto loop
- 对象：`Rank 278 / Hyperliquid whale-trade convergence continuation`
- 本轮动作：survivor 唯一一次 decisive follow-up
- 结论：`drop_to_background/P0`

## 本轮只回答的问题
把对象改写成 desk 版 `coin-normalized whale shock continuation` 后，在 Hyperliquid 公开 trade stream 上，是否至少有一个 `1m/3m/5m/15m` 固定持有窗能在 maker / mixed / taker 成本口径下留下可迁移的 after-cost pocket。

## clean-room 快检口径
数据全部来自 Hyperliquid 公共接口：
- trades：`POST /info {"type":"recentTrades","coin":...}`，连续轮询约 7 分钟，覆盖 `BTC / ETH / SOL / HYPE / DOGE / PEPE / WIF`
- candles：`POST /info {"type":"candleSnapshot", ... interval="1m"}`

实验定义：
1. 对每个 coin 用本轮采样内的 `trade_notional_usd` 做 coin-specific `q99` 门槛；
2. 仅保留 `>= q99` 的同向大单；
3. 若过去 `300s` 内同 coin 同方向的 distinct active wallets `>= 2`，记为 whale convergence event；
4. 用事件后第一个可用 1m close 作为 entry proxy；
5. 检查 `1m / 3m / 5m / 15m` 固定持有窗；
6. 成本用 desk round-trip 代理：`maker = 2 bps`，`mixed = 5 bps`，`taker = 8 bps`。

artifact：
- `reports/artifacts/optimization_loop/rank278_whale_continuation_livecapture_20260401_0500/raw_trades.json`
- `reports/artifacts/optimization_loop/rank278_whale_continuation_livecapture_20260401_0500/analysis_summary.csv`
- `reports/artifacts/optimization_loop/rank278_whale_continuation_livecapture_20260401_0500/analysis_events.json`

## 关键结果
本轮连续采样共抓到 `1973` 笔去重 trades；满足 `coin-specific q99 + 300s 同向 distinct wallets >= 2` 的事件只有 `8` 个：
- `BTC`: `670` trades，`5` 个事件
- `ETH`: `518` trades，`2` 个事件
- `HYPE`: `315` trades，`1` 个事件
- `SOL / DOGE / WIF`: 0 个事件
- `PEPE`: `recentTrades` 在本轮多次返回 500，未获得稳定样本，未纳入正面证据

聚合结果（所有事件）：
- `1m` gross mean：`-1.43 bps`
- `1m` net mean：maker `-3.43 bps` / mixed `-6.43 bps` / taker `-9.43 bps`
- `3m` gross mean：`-7.05 bps`
- `3m` net mean：maker `-9.05 bps` / mixed `-12.05 bps` / taker `-15.05 bps`
- `5m` gross mean：`-10.93 bps`
- `5m` net mean：maker `-12.93 bps` / mixed `-15.93 bps` / taker `-18.93 bps`
- `15m`：本轮无足够成熟事件，未形成可用 pocket 证据

单币也没有留下可迁移 after-cost pocket：
- `BTC 1m` gross mean 虽有 `+1.44 bps`，但 maker 后已到 `-0.56 bps`，更别说 mixed / taker；`3m/5m` 更差
- `ETH` 的 `1m/3m` 都是负 net
- `HYPE 5m` gross 只有 `+0.55 bps`，maker 后也为 `-1.45 bps`

## 为什么本轮直接回 background/P0
这次 follow-up 已经回答了 survivor 唯一该回答的问题，而且答案是否定的：
1. 把 repo 叙事改写成 coin-normalized event 定义后，事件并不提供稳定 continuation 厚度；
2. 少数看起来勉强为正的 gross pocket（如 `BTC 1m`、`HYPE 5m`）一进现实成本就消失；
3. 本轮公共样本里，真正满足 `distinct wallets >= 2` 的事件本来就稀疏，且没有显示出值得升到 `P2` 的可迁移 after-cost edge；
4. 因此这条线当前更像“身份流叙事成立，但可交易厚度不足”的对象，不应继续占用 survivor / P2 前排预算。

## 本轮改变系统认知的一句话
`Rank 278` 的唯一 survivor clean-room replication 已完成：在 Hyperliquid 公共 tape 上，把它改写成 `coin-specific q99 whale shock + 300s 同向 distinct wallets >= 2` 后，`1m/3m/5m` 聚合 gross 都不够厚，maker / mixed / taker 成本后没有留下任何可迁移 pocket，因此本轮直接 `drop_to_background/P0`。
