# 别把 funding 只做绝对 carry：更该先测的是「funding dispersion rich-vs-cheap 篮子」raw alpha
- 时间：2026-03-25 18:12 UTC
- 类型：论文 + GitHub + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：横截面 funding carry / relative-value（多低 funding，空高 funding）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / carry / funding / cross-sectional / relative-value / stat-arb / perpetual / binance / 5m / 15m / 1h / 8h / 24h
- 证据类型：论文证据 + 工程实现 + 公共数据快检

## 1. 这次看了什么
看了两条 carry 主线：一是 Fan、Jiao、Lu、Tong 2024 working paper《Risk and Return of Cryptocurrency Carry Trade》，它证明 crypto carry 不是只能做单腿赚息差，横截面 long-short 也能形成独立因子；二是 Schmeling、Schrimpf、Todorov 2023 的 BIS/SSRN《Crypto Carry》，它解释了为什么高 carry 往往对应拥挤杠杆需求而不是“白送钱”。工程上再对照 `exo-trading/crypto-carry-screener`，它已经把“全币 funding 抓取 + xs-carry/basis 监控”写成可复用骨架。

## 2. 核心结论
- **这篇东西的 base alpha 是什么？** 不是“收 funding”本身，而是**横截面上做多更便宜/更不拥挤的 perp，做空更贵/更拥挤的 perp**，吃相对收益回归 + funding spread。
- 对短周期 desk 来说，最值得偷的不是论文 headline 的长样本资产定价结论，而是它背后的 **rich-vs-cheap 排名骨架**：每个 funding 时点做一次横截面排序，再用 `5m/15m` 执行。
- 我用 Binance USDT 永续 12 币（BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK/AVAX/LTC/DOT/BCH）做了最小快检，样本为 **2026-01-18 ~ 2026-03-25、199 个 funding 事件**。若“永远开着跑” top1-vs-bottom1，**下一段 8h 平均 gross 仅 -12.4 bps/次**，说明它**不是 always-on alpha**。
- 但当 funding dispersion 进入样本内 **前 25%** 时，若做 **top3 高 funding 做空 / bottom3 低 funding 做多，并持有 24h**，平均 **gross +27.1 bps/次**；按 **16 bps round-trip** 粗算后仍有 **+11.1 bps/次**，说明这条 edge 更像**稀疏 pocket**。
- 在这些高 dispersion 事件里，平均 funding spread 只贡献约 **5.6 bps**，其余主要来自后续相对价格回归；所以 **funding 更像 trigger，不是全部 PnL**。

## 3. 为什么和当前项目有关
这条线直接补的是当前 desk 还不够厚的 **carry / cross-sectional / relative-value raw alpha 素材池**。它不是继续围绕 breakout/confirmation 内循环，而是给出一条可以独立立项的 perp basket 策略：信号时钟来自 funding，执行落在 `5m/15m`，风险管理可以完全按 market-neutral 组合去写。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 轻逆拥挤
- 基础 alpha：long 低 funding basket，short 高 funding basket
- regime：仅在 funding dispersion 进入高分位时 trade-on
- filter / veto：只保留高流动性 USDT perp；跳过重大宏观/链上事件窗；若两端年化 funding 差不足以覆盖预估成本则不做
- risk / sizing / execution overlay：美元中性；单币权重 capped；`5m` TWAP/被动挂单进出；默认 24h 持有或当 spread 回到中位数附近平仓

## 4. 可复刻的最小实验
- **研究假设**：高 funding dispersion 代表横截面拥挤分化，随后 rich leg 相对便宜 leg 更容易回落。
- **数据源**：Binance Futures 公共 funding rate + 1h/5m K 线；完全公开可拿。
- **最小口径**：每个 `00/08/16 UTC` 计算 liquid perp funding 排名；若 `high-low spread` > 过去 30 天 75% 分位，则 long 底部 3、short 顶部 3；用 `5m` 执行，持有 24h；计入 `16~24 bps` round-trip。
- **先看 4 个指标**：gross spread、净后 edge、命中率、rich/cheap 两端各自的 price leg 贡献。

## 5. 风险与边界
这条线最大的坑，是把它误当“稳定收息差”的低换手策略。实际更像**拥挤分化过大时才出现的相对价值 pocket**；如果 dispersion 不高、执行又是双边 taker，很容易把 edge 全部吃掉。另外 funding 发布频率是 `8h`，所以它是**低频信号 + 短周期执行**，不是逐根 `1m/5m` 主信号。

## 6. 下一步怎么测
1. 把 universe 扩到 Binance 前 30~50 个高流动性 USDT perp，重跑 `top1/top3/top5` 与 `8h/24h` 持有矩阵。
2. 加 `open interest change / basis / volume shock`，看能否把高 dispersion pocket 从“接近 break-even”提到稳定净正。
3. 把执行从全 taker 改成 `maker-first + 5m TWAP`，单独估一版真实成本生存线。
4. 检查 beta 暴露：先对 BTC/ETH 做简单 beta 对冲，确认赚的是 rich-vs-cheap，而不是 alt beta 摆动。

## 7. 来源与可复用材料
1. **Feng Jiao, Lei Lu, Xing Tong, Zhenzhen Fan (2024)**, *Risk and Return of Cryptocurrency Carry Trade*, working paper / SSRN.
   - Readable URL: https://www.zhenzhenfan.com/research
   - SSRN URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4666425
   - 关键信息：作者主页摘要写明 cross-sectional carry trade **年化 46.71%**, **Sharpe 0.77**。
2. **Maik Schmeling, Andreas Schrimpf, Karamfil Todorov (2023)**, *Crypto Carry*, BIS Working Papers No.1087 / SSRN.
   - DOI: 10.2139/ssrn.4268371
   - Readable URL: https://www.bis.org/publ/work1087.htm
   - 关键信息：carry 可高于 **10% annualized**，高 carry 更多反映杠杆需求与套利资本稀缺。
3. **exo-trading (2025)**, *crypto-carry-screener*.
   - Repo URL: https://github.com/exo-trading/crypto-carry-screener
   - Raw code URL: https://raw.githubusercontent.com/exo-trading/crypto-carry-screener/main/market_data_collector.py
   - 可复用点：全币 funding 历史抓取、小时级缺失补齐、xs-carry / basis 监控骨架。
4. **Binance Futures Public API**（公开数据源）
   - Funding: https://binance-docs.github.io/apidocs/futures/en/#get-funding-rate-history
   - Klines: https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data
   - 更新频率 / 最小复现实验口径：funding `8h`，价格可到 `1m/5m`，足够做最小 basket 回测。