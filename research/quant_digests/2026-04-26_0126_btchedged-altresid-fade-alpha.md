# 别把这个 2025 小 repo 只读成“小时级均值回复作业”：对 short-cycle crypto desk，更该先拆的是「BTC 对冲后的 alt 残差反打」这条 raw alpha

- 时间：2026-04-26 01:26 UTC
- 类型：GitHub repo source audit（`datas/fetch_hourly_data.py` + `portfolios/btc_hedged_portfolios.py` + `statistic_tests/autoCorrelsEMAThreshold.py` + `strategy/basic_mean_reversion.py`）+ Binance USDⓈ-M public-data portability probe（`BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK/AVAX/LTC`，近 `90d`，`15m` + `1h`）
- 主题类型：**raw alpha**
- 基础 alpha：**先把每个 alt 的市场 beta 用 `BTC` 对冲掉；若剩下的 idiosyncratic residual 刚刚冲得过头，下一小段更容易反打，而不是继续单边延伸。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**否，repo 只有 alpha 壳，缺正式成本/仓位/止损/组合约束。**
- 主题标签：raw-alpha / relative-value / stat-arb / btc-hedged / residual / mean-reversion / cross-asset / 1h / 15m / repo / public-data / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
这轮看的是 GitHub repo **`Dastrial/crypto_strat`**（2025-06 更新，仓库描述直接写着 *Cryptocurrency perpetual futures mean-reversion*）。它表面上很朴素，但对 desk 真正有价值的不是“均值回复”这四个字，而是它先做了一个很明确的动作：

1. 先用 `BTC` 给每个 alt 做 beta 对冲；
2. 再只交易那个 **`alt_return - beta * btc_return`** 的残差；
3. 最后用最简单的规则验证：**上一根残差什么方向，下一根先反着做。**

也就是说，它不是在赌“全市场跌多了就反弹”，而是在赌：**某个币相对 BTC 的短时错位会回归。** 这比再写一篇泛泛的单资产超跌反弹，更贴近我们现在想补的 `relative value / stat-arb` 素材池。

## 2. 一句话核心结论
**这份 repo 最值得 desk 保留的，不是它的脚本写法，而是一个很容易最小复现的 raw alpha 壳：`BTC-hedged alt residual fade`；近 `90d` 的 Binance USDⓈ-M 快检显示 gross edge 还在，但厚度明显不够硬扛 taker 成本，更像 `1h parent / 15m child` 的相对价值 router，而不是裸做的主系统。**

## 3. 它是怎么证明这件事的
repo 的逻辑非常直白：
- `fetch_hourly_data.py` 拉 `1h` perpetual 数据；
- `btc_hedged_portfolios.py` 对每个 alt 估一个 `beta = cov(alt, BTC) / var(BTC)`；
- 然后构造 `alt - beta*BTC` 的市场中性组合；
- `autoCorrelsEMAThreshold.py` 再去看“大残差之后，后续自相关是不是更偏负”；
- `basic_mean_reversion.py` 最终直接跑 `-sign(residual_{t-1}) * residual_t`。

所以它给我们的不是完整实盘系统，而是一句很清楚的研究命题：
> **如果某个 alt 这一小段相对 BTC 冲太快，下一段是否更容易回到均值？**

## 4. 为什么和当前项目有关
这条线和当前 desk 的关系很直接：
- 它补的是 **raw alpha**，不是纯 filter；
- 它属于我们现在应该持续补的 **relative-value / stat-arb** 分支，而不是继续围绕单一 breakout 形态内循环；
- 它的最小实验门槛很低：只要 `BTC + alt` 公共 K 线就能先做 first verdict；
- 即便最终主结论是“太薄、不能直接打”，它仍然能沉淀成一个共享组件：`BTC beta hedge + residual z-score admission`。

## 4.5 这轮 portability 快检
我补了一个 Binance USDⓈ-M 公共数据快检，标的为 `BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK/AVAX/LTC`，近 `90d` `15m` 数据；先用前 `70%` 样本估 beta，再看后 `30%` 样本。

### A. repo 原生读法：`1h` residual 每小时反打
把 `15m` 聚成 `1h` 后，`XRP / DOGE / ADA / SOL` 这几条 residual 的 gross 仍然最好：
- `XRP`：平均约 **+2.32 bps/小时**，胜率约 **53.7%**；
- `DOGE`：约 **+1.94 bps/小时**；
- `ADA`：约 **+1.76 bps/小时**；
- `SOL`：约 **+1.73 bps/小时**。

但问题也很直接：这套 repo-native 规则几乎 **每小时都在翻向**，按 round-trip `8 bps` 粗扣后，最好的 `XRP` 也变成约 **-5.68 bps/笔**。所以 repo headline 更适合被读成“残差会回”，而不是“这份脚本能直接交易”。

### B. desk 化读法：`15m` 直接做 residual fade，并加极值门槛
若把同样想法下沉到 `15m`，只在前一根 residual z-score 够极端时才开：
- `|z| >= 1.25` 时，`11106` 笔信号，平均 gross 约 **+1.11 bps/笔**，胜率约 **54.8%**；
- `|z| >= 1.00` 时，`16645` 笔，平均 gross 约 **+0.85 bps/笔**；
- 不加门槛时虽然样本很多，但 gross 只有 **+0.32 bps/笔**。

这说明一个挺重要的事：**残差反打本体没死，但 edge 很薄，必须承认它更像“极值时才值得碰”的 admission / router。**

## 5. 策略拆解（必填）
- 方向属性：relative value / BTC-neutral / mean reversion
- 基础 alpha：`alt_return - beta * btc_return` 的短时偏离回归
- regime：单币 idiosyncratic 冲击、而 BTC 主导方向没有同步放大时更友好
- filter / veto：残差 `|z|` 极值、事件黑名单、funding/basis 同向拥挤 veto
- risk / sizing / execution overlay：按 `beta` 做腿权重；限制同时持有的 alt 数；优先 maker / queue-first，否则 taker 成本几乎必吃光

## 6. 可复刻的最小实验
### 最小实验 A：先做最诚实的 alpha 本体
- 标的：`XRP / DOGE / ADA / SOL` vs `BTC`
- 周期：`1h` parent，`15m` child execution
- 定义：前一 `1h` residual z-score 达到 `0.75 / 1.0 / 1.25` 时，下一 `15m~60m` 反向做 residual fade
- 先看：`gross bps/trade`、`net bps/trade`、`hit rate`、`trade count`

### 最小实验 B：再问能不能厚一点
- 不改 base alpha，只叠加：
  1. `funding / basis` 不与 residual 方向冲突；
  2. 只做 `quote volume` 更高时段；
  3. 只做 `residual z-score` 极值后的前 `1~2` 根。
- 目标不是把它包装成新 alpha，而是看能否把 **gross ~1bps** 抬到 **可覆盖真实摩擦** 的级别。

## 7. 风险与保留意见
1. **repo 太简化**：没有正式成本、没有持仓冲突处理、没有 stop / timeout 设计。
2. **当前 edge 过薄**：这轮 public probe 下，gross 还在，但离 taker 可做差得很远。
3. **beta 不是常数**：若市场从“BTC 带队”切到“alt 自主行情”，固定 beta 容易失真。
4. **更像 shared component，不像独立主系统**：短周期上最现实的用途，可能是把它变成 `BTC-neutral mispricing veto / router`，而不是 always-on 主策略。

## 8. 我对这条线的判断
这轮值得留下来的，是一句更窄也更诚实的话：

> **先把 `BTC-hedged alt residual fade` 当 raw alpha 壳收进池子；但当前更像“有统计味道的薄边素材”，下一步必须围绕 admission、成本和执行做厚度筛查，别把 repo 的零成本反手脚本误当成完整策略。**

它仍然值得做，因为它补的是我们当前最缺的那一类：**可快速复现的 BTC-neutral relative-value raw alpha**。

## 9. 文件与页面
- 研究笔记：`research/quant_digests/2026-04-26_0126_btchedged-altresid-fade-alpha.md`
- Probe script：`reports/artifacts/quant_digests/2026-04-26_btc_hedged_residual_reversion_probe.py`
- Probe summary：`reports/artifacts/quant_digests/2026-04-26_btc_hedged_residual_native1h_summary.csv`
- Probe summary：`reports/artifacts/quant_digests/2026-04-26_btc_hedged_residual_direct15m_summary.csv`
- Probe trades：`reports/artifacts/quant_digests/2026-04-26_btc_hedged_residual_direct15m_trades.csv`
- 预期页面（发布后）：<https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-26_0126_btchedged-altresid-fade-alpha.html>
- 索引页：<https://jp.jerrypsy.top/momentum/reading/quant_digests/report.html>

## 10. 来源
1. **Dastrial / EsaieB. (2025). _crypto_strat_. GitHub.**
   - Repo URL: <https://github.com/Dastrial/crypto_strat>
   - 仓库描述：*Cryptocurrency perpetual futures mean-reversion*
   - Source files audited:
     - <https://github.com/Dastrial/crypto_strat/blob/master/datas/fetch_hourly_data.py>
     - <https://github.com/Dastrial/crypto_strat/blob/master/portfolios/btc_hedged_portfolios.py>
     - <https://github.com/Dastrial/crypto_strat/blob/master/statistic_tests/autoCorrelsEMAThreshold.py>
     - <https://github.com/Dastrial/crypto_strat/blob/master/strategy/basic_mean_reversion.py>

2. **Binance USDⓈ-M Futures public klines**
   - API docs: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
   - This digest portability probe used recent public `15m` klines for `BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT / XRPUSDT / ADAUSDT / DOGEUSDT / LINKUSDT / AVAXUSDT / LTCUSDT`.
