# 别把这份 2026 market-making repo 只读成 textbook HJB：对 short-cycle desk，更该先测的是「OFI-EWMA reservation-price skew × inventory-bounded maker spread capture」
- 时间：2026-04-07 08:52 UTC
- 类型：GitHub 仓库 / `README.md` source audit
- 主题类型：raw alpha
- 基础 alpha：`1s~1m` 上用 `OFI` 预测极短期漂移，把预测漂移写进 reservation price，再做 inventory-bounded maker spread capture
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：maker / market-making / microstructure / order-flow / OFI / reservation-price / inventory-risk / spread-capture / binance / BTCUSDT / 1s / 1m / 3m / repo / public-data / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
看的是 2026 新仓库 `Yaskoi/Optimal-Market-Making-on-Crypto-Markets` 的 `README.md`。它不是单纯复述 Avellaneda-Stoikov / Cartea-Jaimungal 教材，而是把 **BTC/USDT Binance `1s` 数据 + OFI(alpha) + inventory risk + frictions** 串成了一条完整 maker 策略壳。最值钱的地方不是“做市”三个字，而是它把 **base alpha** 说清楚了：**短到秒级的 order-flow imbalance 对下一小段价格漂移有预测力，所以你的双边报价不该总围着静态 mid，而应围着带 alpha 偏置的 reservation price。**

## 2. 核心结论
- 这篇东西的 base alpha 很清楚：**OFI 的短半衰期预测力**，不是 filter，不是纯 execution infra。maker 只是交易壳，alpha 本体是 `OFI -> next short-horizon drift`。
- repo 给了三个层级：`AS pure`（无 alpha）、`CJ + EWMA(OFI)`、`CJ + OU-Jumps`。按 README 报告的 `2025-12` OOS 结果，`AS pure` **净 P&L -$428 / Sharpe -1.85**，而 `CJ + EWMA` **净 P&L +$15,281 / Sharpe +3.79**，`CJ + OU-Jumps` **+ $8,745 / Sharpe +2.34**。说明“有没有 alpha 偏置”不是小修小补，而是生死线。
- 作者没有把 friction 藏起来：`CJ + EWMA` 平均每 session 还要吃 **$9.1 commission + $66.3 slippage + $56.5 adverse selection**。一句人话：**maker 看着像吃 spread，但真正把钱咬掉的，往往是延迟成交后的坏价格和被更聪明的 taker 选边打。**
- 一个很有迁移价值的数据点是 signal half-life 只有 **0.35 秒**，EWMA 最优 span 只有 **2 秒**。这意味着它更适合作为 `1m/3m` 的高强度 microstructure alpha，或者给 `5m/15m` 主策略做 child execution / quote skew，而不是硬抬成逐根 `15m` 主信号。
- 一句话核心结论：**值得抄的不是“开双边单就能赚 spread”，而是“当 OFI 明显偏一侧时，把 reservation price 往那边挪，并用 inventory 上限约束仓位暴露”。**
- 一句话证明方式：**repo 直接用 `2025-07 ~ 2025-11` IS、`2025-12` OOS 的 1 秒级回测，对比无 alpha / EWMA alpha / OU-jump alpha 三套模型，并显式列出成本分解。**

## 3. 为什么和当前项目有关
这条线虽然比 `5m/15m` 更快，但它不是“偏题的 execution 综述”，而是一条能独立成立的 **maker raw alpha**。对当前 desk 的价值有两层：
1. **直接扩 raw alpha 池**：如果我们接受 `1m/3m` 的高强度 alpha，这条线本身就能单独进研究池；
2. **给慢频策略补 child execution**：如果未来某条 `5m/15m` directional / RV 策略要以 maker 方式进场，这个 repo 提供了一个很清楚的 quote-skew 思路：不是被动挂死，而是按短期 flow 预期偏置买卖价。

## 3.5 策略拆解（必填）
- 方向属性：做市 / microstructure / spread capture
- 基础 alpha：OFI 对未来极短 horizon 漂移的预测力，驱动 reservation price skew
- regime：高流动、可持续双边挂单、OFI 自相关尚未塌掉的时段
- filter / veto：inventory bound、session end、alpha 信号过弱、极端 adverse-selection 环境
- risk / sizing / execution overlay：最优 spread、库存惩罚项 `q·γ·σ²(T-t)`、maker fee、执行延迟、slippage、adverse selection 成本

## 4. 可复刻的最小实验
- 研究假设：**在 Binance `BTCUSDT` 的 `1s` 数据上，短窗 OFI-EWMA 足以改善 maker quote placement，使成本后收益显著优于无 alpha 的对称双边报价。**
- 一个可计算定义：
  - `OFI_t = (buy_vol - sell_vol) / (buy_vol + sell_vol)`（可由 Binance `1s` kline 的 taker buy / total volume 还原）
  - `alpha_t = EWMA(OFI_t, span=2s)`
  - `reservation_price = mid + alpha_bias - inventory_penalty`
  - 仅当 `|alpha_t|` 超过过去滚动分位阈值时放大单边 skew，否则回到近对称报价
- 最小回测切口：先只跑 `BTCUSDT`，样本先取最近 `60~90d` Binance `1s` 或聚合成 `5s`；主策略层面先看 `1m` child engine，随后测试是否能给 `3m` 的 directional signal 降低冲击成本。
- 最该先看 2 个指标：
  1. **净 capture / adverse-selection ratio**（赚到的 spread 有多少没被回吐）
  2. **inventory excursion / session-level drawdown**

## 5. 风险与保留意见
- 当前证据主要来自 repo `README` 自报结果，且 fill model 仍是研究级近似，不是交易所 queue-level 真回放；所以 **alpha 有意思，不等于收益数值可直接照抄**。
- `OFI` 半衰期只有秒级，任何网络延迟、撮合优先级、排队位置误差，都可能把 paper edge 吃光。
- 这条线很可能只在 **BTC/ETH 这类深流动品种** 上还有生存空间；搬到中小币，adverse selection 和 inventory tail risk 会迅速变坏。
- 如果 desk 当前没有稳定的 maker infra，这条线应先作为 **research shell / child execution alpha**，不要直接当 production-ready bot。

## 6. 来源
- Yaskoi. (2026). *Optimal-Market-Making-on-Crypto-Markets*. GitHub repository.
  - Readable URL：`https://github.com/Yaskoi/Optimal-Market-Making-on-Crypto-Markets`
  - Repo URL：`https://github.com/Yaskoi/Optimal-Market-Making-on-Crypto-Markets`
  - README：`https://raw.githubusercontent.com/Yaskoi/Optimal-Market-Making-on-Crypto-Markets/main/README.md`
- 数据源（公开可得）：Binance Data Portal `BTCUSDT / ETHUSDT 1s klines`
  - `https://data.binance.vision/?prefix=data/spot/monthly/klines/BTCUSDT/1s`
- 理论地基：
  - Avellaneda, M., & Stoikov, S. (2008). *High-frequency trading in a limit order book*. *Quantitative Finance*.
  - Cartea, Á., & Jaimungal, S. (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press.
  - Cont, R., Kukanov, A., & Stoikov, S. (2014). *The price impact of order book events*. *Journal of Financial Econometrics*.
