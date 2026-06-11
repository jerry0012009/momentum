# 别把这份 stat-arb repo 只读成“作者自称有 alpha”：对 short-cycle crypto desk，更该先拆的是「fee-aware same-symbol cross-venue spot gap × inventory/maker-first deployment shell」
- 时间：2026-04-22 04:58 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `arbitrage/pure_arb_simulator.py`）+ public live quote sanity probe（Binance Spot / Bitstamp BTC，约 `40s`）
- 主题类型：raw alpha
- 基础 alpha：同一标的在不同交易 venue 的可执行买一/卖一出现足够大的瞬时价差时，买便宜 venue、卖贵 venue，赌同标的跨 venue 价差向 law-of-one-price 收敛
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / stat-arb / cross-venue / same-symbol / spot / law-of-one-price / fee-aware / slippage / inventory-funded / maker-first / btc / 1m / 3m / 5m / repo / public-data
- 证据类型：工程实现 + repo 策略壳 + public live probe

## 1. 这次看了什么
这次主看的是 **Atrone / stat_arb_crypto**。这个 repo 里其实混了几条线：一条是带 ESRNN 预测和 funding 条件的方向分支，另一条更干净、也更适合 desk intake 的，是 `arbitrage/pure_arb_simulator.py` 里的 **same-symbol cross-venue gap capture**。

它最值得保留的地方，不是“跨所套利”这四个字，而是把一条很老但仍然重要的 raw alpha 壳写成了可检查的流程：
- 先抓两边同标的价格；
- 再显式扣掉 **双边 slippage + 双边 taker fee**；
- 只有净利润 `> arbitrage_threshold` 才记为可做机会；
- 方向上同时检查 `A买/B卖` 和 `B买/A卖` 两边。

翻成人话：**不是看到价差就兴奋，而是先问“扣完摩擦后还剩几口肉”。**

## 2. 一句话核心结论
这篇东西最值钱的不是“又一次提醒你跨所会有价差”，而是：

> **same-symbol cross-venue gap 当然是 raw alpha，但在今天的主流 BTC 现货里，taker 化通常不够厚；它更像一条必须依赖 inventory、maker-first、超低延迟和严成本门槛的 deployment shell。**

## 3. 它是怎么证明这点的
核心证据来自 `pure_arb_simulator.py` 的逻辑，而不是 README 口号：

- `fetch_data(...)`：从交易所拉同标的 OHLCV / close；
- `estimate_slippage(...)`：对买卖两边分别估计冲击；
- `get_exchange_fees(...)`：显式取双边 fee；
- `simulate_arbitrage(...)`：
  1. 对两个 venue 同时算 `A买/B卖` 与 `B买/A卖`；
  2. 用 `adjusted_buy_price = price * (1 + slippage)`、`adjusted_sell_price = price * (1 - slippage)` 先把“理论价差”压成“成交后价差”；
  3. 再扣 fee，得到 `net_profit_usd`；
  4. 只有 `net_profit_usd > arbitrage_threshold` 才记为一笔机会。

也就是说，这个 repo 至少把 **alpha 本体** 和 **摩擦现实** 放在同一个判定口径里，而不是只看裸 spread。

## 4. base alpha 到底是什么
先说清边界：

- **base alpha 不是** “低延迟基础设施”；
- **base alpha 不是** “maker rebate”；
- **base alpha 也不是** “slippage 模型”；

这篇东西的 **base alpha** 是：

> **同一标的跨 venue 的瞬时错误定价 / 价差偏离，会在足够短时间内向统一价格回归。**

其余这些都只是把它从“纸面套利”变成“可落地系统”的必要二层组件：
- fee gate
- slippage gate
- inventory 预铺货
- maker-first / hedge venue
- latency / stale-quote veto

所以它符合本轮优先级：**这是 raw alpha，而且能自然写成完整策略壳。**

## 5. 这轮 public live probe 看到了什么
我额外做了一个很轻的 live sanity check：
- 标的：`BTC`
- venue：Binance Spot `BTCUSDT` vs Bitstamp `BTCUSD`
- 口径：每 `5s` 采 1 次，共 `8` 次，近似看“买最便宜、卖最贵”的即时可执行 gap
- 结果：
  - 可执行 gap 范围约 **`2.18 ~ 2.98 bps`**
  - 均值约 **`2.45 bps`**
  - 最高报价大多出现在 Bitstamp、最低报价大多出现在 Binance

这组数的含义很直接：

> **主流 BTC 现货的表面 gap 确实存在，但肉非常薄。**

如果你用普通 taker×2 去打，别说再加提现、转账、库存占用和 API 延迟，单看显性手续费，很多时候就已经把这 `2~3 bps` 吃没了。

## 6. 对 short-cycle desk 真正有用的，不是“去搬砖”，而是三件事
### 6.1 把它当相对价值 alpha 壳，而不是稳赚神话
这条边不是没有，但默认不该被写成“稳定无风险套利”。对 desk 更诚实的说法是：
- **alpha 本体**：same-symbol venue dislocation close
- **能否活下来**：取决于 fee tier、maker 命中率、库存预铺和 quote freshness

### 6.2 最适合映射到 `1m/3m`，其次才是 `5m`
这条 edge 天生更接近 **event-time / top-of-book**，不是慢 bar 因子。
最小实验应是：
- `1s~5s` 级 quote 采样；
- 聚合成 `1m` 的 dislocation count / max gap / dwell time；
- 再判断 `1m/3m/5m` 上是否还有可交易残留，而不是反过来先做 `15m` K 线。

### 6.3 更适合 inventory-funded / maker-first，不适合裸 taker 扫单
当前 probe 已经很说明问题：如果公开可见 gap 只剩 `2~3 bps`，那这条边更像：
- 在薄 venue 先挂 maker；
- 深 venue 做快速 hedge；
- 或者双边都已有库存，只吃短暂偏离；
而不是“看到 gap 就两边 taker”。

## 7. 下一步怎么测
1. **做真实 quote-level 采集**：至少抓 `1s` 级 bid/ask，而不是 close；连续采 `BTC/ETH/SOL`，先跑 `3~7d`。
2. **统一 quote 货币**：别把 `USD` / `USDT` 混在一起直接比；先补稳定币偏离修正。
3. **先做 friction ladder**：`gross gap -> minus fee -> minus half-spread -> minus hedge delay`，别直接谈年化。
4. **分三档 execution 假设**：`taker/taker`、`maker/taker`、`inventory-funded maker/taker`，看哪一档才可能过线。
5. **只保留 sparse shell 的预期**：如果 `BTC` 太薄，就把它迁到更分散的 alt / 区域性 venue 组合，而不是继续在最卷的主流对上幻想无脑套利。

## 8. 来源
1. **Atrone (2025). _stat_arb_crypto_. GitHub Repository.**  
   - Repo URL: <https://github.com/Atrone/stat_arb_crypto>  
   - Readable URL: <https://github.com/Atrone/stat_arb_crypto>  
   - 关键文件：`README.md`、`arbitrage/pure_arb_simulator.py`
2. **Binance Spot public book ticker API**  
   - <https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT>
3. **Bitstamp public ticker API**  
   - <https://www.bitstamp.net/api/v2/ticker/btcusd/>
