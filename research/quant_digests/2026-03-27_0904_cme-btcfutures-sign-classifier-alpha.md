# 别把这篇 2021 CME Bitcoin futures 论文只读成黑箱：对 desk 更该先测的是「next-bar sign classifier + 高阈值 abstain」raw alpha
- 时间：2026-03-27 09:04 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：最近若干根 bar 的收益、波动与主动买卖失衡里，存在可学习的下一根方向 edge；交易上不是根根都做，而是只做高置信度那一小撮。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/directional/next-bar/sign-classification/abstain/taker-imbalance/btc/futures/5m/15m/paper/external-data
- 证据类型：论文证据 + 公共数据最小快检

## 1. 这次看了什么
Erdinç Akyıldırım、Oğuzhan Çepni、Samuel Corbet、Gazi Uddin 在 2021 年《Annals of Operations Research》里的 **Forecasting mid-price movement of Bitcoin futures using machine learning**。论文用 CME Bitcoin futures 的 `1M~5M` 合约、`5/10/15/30/60m` 频率，检验“下一根中间价方向”是否可预测。

## 2. 核心结论
- **base alpha 很明确**：不是“机器学习很厉害”，而是 **next-bar sign prediction 本身就是 raw alpha**；ML 只是把这个 edge 从高频特征里读出来。
- 论文样本为 `2020-01-02 ~ 2020-09-10` 的 CME BTC futures；作者比较了 kNN、Logit、Naive Bayes、RF、SVM、XGBoost 与 ARIMA / random walk。
- 论文里最强的不是平均收益率吹得多高，而是 **方向命中率稳定高于 50%**：摘要给出的最好结果是 **SVM 平均 OOS 约 56%，个别 case 最高到 71%**；强势 case 更集中在 **更长久期合约、较慢 bar**。
- 我用 Binance Futures 公共 kline（OHLCV + taker buy volume）做了一个 desk 化最小迁移：最近约 `2,975` 根 bar 上，`15m` RF 的 OOS accuracy 约 **52.3%**；但若按 `0.55/0.45` 阈值做 next-bar long/short，trade rate 约 **22.4%**，扣 **4 bps** 换手成本后仍是 **-1.05 bps/bar**。
- 这说明它**不是没有 edge**，而是当前最粗 public 版还不够：它更像需要 **高阈值 abstain + 更细特征 + 更便宜执行** 才可能活的方向型 raw alpha。

## 3. 为什么和当前项目有关
- 最近 intake 很多是 `pairs / XS reversal / relative value`，这篇正好补 **single-asset directional raw alpha** 这一桶。
- 它和 desk 默认周期直接对上：论文本身就覆盖 `5m/15m/30m/60m`，不是硬把日频东西往短周期上搬。
- 数据公开、实验很快：先用 Binance/Bybit 公共 futures kline 做 weak proxy，若值得再升到 `aggTrades + bookTicker` 或 L2。
- 它还能自然拆成完整策略：`signal probability → abstain threshold → 持有 1~3 bars → maker/taker cost gate`，很适合 first verdict。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 方向型 raw alpha
- 基础 alpha：最近数根 bar 的 return/range/taker-flow 对下一根方向存在可学习 edge
- regime：优先 `15m`、高流动性主合约、低显性成本窗口；次优再看 quarterlies / longer-dated futures
- filter / veto：只在 `p(up) >= 0.55` 或 `<= 0.45` 时开仓；`p` 靠近 0.5 一律放弃
- risk / sizing / execution overlay：仓位按 `|p-0.5|` 分层；默认持有 1 bar，最多 3 bars；若 spread/fee > 预期 edge，直接 veto

## 4. 可复刻的最小实验
- **研究假设**：短周期 BTC futures 的下一根方向不是纯随机；edge 在 `15m` 和较长久期合约上比 `5m` 永续更干净。
- **数据源**：Binance Futures 公共 `klines`（含 `taker_buy_base`），后续可升级到 `aggTrades/bookTicker`；完全公开可拿。
- **最小口径**：`BTCUSDT perp` 与 `BTCUSDT_260626`，`5m/15m`；特征只先用过去 `6` 根的 return、body、range、signed taker imbalance、volume z-score。
- **交易规则**：walk-forward 训练方向分类器；若 `p>=0.55` 做多、`p<=0.45` 做空，否则空仓；默认持有 1 bar，bar close 平仓；round-trip 先按 `4 bps`。
- **我这轮快检结果**：
  - `BTCUSDT perp 15m`：RF OOS accuracy **52.3%**；`0.55` 阈值 trade rate **22.4%**，hit when trade **56.5%**，但净值仍约 **-1.05 bps/bar**。
  - `BTCUSDT perp 5m`：Logit OOS accuracy 只有 **50.1%**，基本不足以做 taker。
  - `BTCUSDT_260626 5m`：Logit OOS accuracy **51.8%**；`0.55` 阈值 hit when trade **55.9%**，但 trade rate 仅 **5.9%**，净值仍约 **-0.31 bps/bar**。

## 5. 风险与边界
- 论文主样本是 **2020 COVID 冲击期的 CME futures**，可迁移性不能默认成立。
- 论文里最亮眼的高命中率集中在部分长久期 / 小 hold-out case，不能直接按 headline 接受。
- 我这轮 public 迁移只用了 kline 级 proxy，离真正 microstructure 特征还差一层；当前结果更像“**有弱 edge，但 taker 先不过线**”。

## 6. 下一步怎么测
1. 升级特征：把 `aggTrades` 的 signed volume、VWAP gap、trade count shock 加进来，不再只看 kline。
2. 做 **maker/taker 双成本梯度**：`1/2/4/6 bps`，确认它究竟是 maker alpha 还是根本没 edge。
3. 做 **probability decile**：只保留最极端 `top/bottom 10%` 置信度，看 net edge 是否跳变。
4. 把同一框架平移到 `ETHUSDT` 与 `BTC quarterlies → perp`，确认是不是只在 BTC 主合约有效。

## 7. 来源
- Akyıldırım, E.; Çepni, O.; Corbet, S.; Uddin, G. (2021). *Forecasting mid-price movement of Bitcoin futures using machine learning*. **Annals of Operations Research**. DOI: `10.1007/s10479-021-04205-x`
- Readable URL: https://link.springer.com/article/10.1007/s10479-021-04205-x
- PMC full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC8296834/
- DOI URL: https://doi.org/10.1007/s10479-021-04205-x
- Repo URL：未见官方 repo
