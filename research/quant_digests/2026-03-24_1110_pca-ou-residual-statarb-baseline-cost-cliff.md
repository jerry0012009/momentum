# 别把 stat-arb 默认做复杂图模型：这份 2026 新仓库更该先复现的是「PCA residual + OU s-score」裸骨架与成本断崖
- 时间：2026-03-24 11:10 UTC
- 类型：2026 GitHub 新仓库 + 本地 Binance 公共数据最小快检 + 论文地基
- 主题类型：raw alpha
- 基础 alpha：先剥离共同因子（PCA）后，交易 idiosyncratic residual 的均值回归（OU s-score 触发）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/stat-arb/relative-value/cross-sectional/mean-reversion/pca/ou/s-score/cost/crypto/1m/3m/5m/15m/repo
- 证据类型：工程证据 + 论文证据（地基）+ abstract-only 近年线索

## 1. 这次看了什么
先回答 base alpha：**不是趋势过滤，不是风险开关，而是“去共同因子后的残差回归”本体**。

主看 2026 新仓库 `sophie-lan/crypto-pca-statarb`：代码把策略主链路写得很直白（`PCA -> residual regression -> OU param -> s-score -> threshold position -> backtest`）。相比我们最近几篇偏“多层增强”的 stat-arb，这篇更像一个可复现、可审计、可做 clean-room 对照的**基线 raw alpha**。

## 2. 核心结论
- 一句话核心结论：**在 short-cycle stat-arb 里，先把 `PCA residual + OU s-score` 这条裸骨架跑通，比一上来叠复杂图结构更有研发产出比。**
- 一句话证明方式：**仓库直接给了可执行模块化实现；我用 Binance 永续 15m 做最小快检，看到“毛利有边、净利被成本打穿”的典型断崖，说明这条线值得进素材池，但必须先过成本生存线。**
- 本地最小快检（10 个高流动永续，约 46.8 天，15m）：`gross Sharpe = 0.51`，`gross cum = +1.32%`。
- 同口径下，若按 one-way 4 bps 估算执行摩擦：`net Sharpe = -3.45`，`net cum = -14.09%`。
- 反推 break-even 成本约 `0.65 bps(one-way)`，远低于常见 taker 成本，说明**这条 alpha 的第一问题是交易摩擦，不是信号是否存在**。

## 3. 为什么和当前项目有关
- 它直接补的是 raw alpha 素材池（mean reversion / relative value / stat-arb），不是再做 breakout/retest 的内循环。
- 它非常适合当前 desk 的“快验证”目标：结构简单、可解释强、可快速做 first verdict。
- 我们近期已做过“加复杂层（聚类/图）”方向，这条基线可作为对照：先回答“简单骨架是否有净边”，再决定复杂层是否值得。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 均值回归
- 基础 alpha：对资产收益做 PCA 去共同因子后，交易 residual 偏离向均值回归
- regime：横截面离散度高、单边趋势不过热时更友好
- filter / veto：残差平稳性不足、流动性不足、重大事件窗口、成本超阈值时 veto
- risk / sizing / execution overlay：市场中性约束、换手上限、分层成本闸门（maker/taker/滑点）

## 4. 可复刻的最小实验（下一步怎么测）
**研究假设**：`PCA residual + OU s-score` 在 `15m` 可能有毛边，但能否进入可交易区间主要取决于换手治理与成本压缩。

**数据源与可得性**：
- 数据源：Binance USDⓈ-M Futures 公共 Klines（REST）
- 公开性：公开可得，无私钥
- 更新频率：支持 `1m/3m/5m/15m`

**最小口径**：
1. Universe：Top 20 流动性永续（先 15m，再下钻 5m/3m）
2. 滚动窗：PCA/回归/Ou 先用 `480` bars（15m≈5天）
3. 入场/出场：沿用仓库 s-score 阈值（`s_bo/s_so=1.25`，`s_bc=0.75`，`s_sc=1.0`）
4. 成本阶梯：`0.5 / 1.0 / 2.0 / 4.0 bps one-way`
5. 先看指标：`net Sharpe`、`net bps/turnover`、`break-even bps`

**下一步优先动作**：
- 先做“低换手版”对照（信号分桶+冷却+最小持有期），再决定是否引入更复杂的聚类层。

## 5. 风险与保留意见
- 当前快检样本短（约 1.5 个月）且为代理执行，不可直接外推实盘容量。
- OU 假设在突发行情下容易失稳，需要结合状态门控与熔断。
- 若成本口径不精确（maker 占比、冲击、资金费率），会高估可交易性。

## 6. 来源
1. **sophie-lan. (2026). _crypto-pca-statarb_. GitHub repository.**
   - Repo URL: `https://github.com/sophie-lan/crypto-pca-statarb`
   - Readable URL: `https://github.com/sophie-lan/crypto-pca-statarb`
2. **Avellaneda, M., & Lee, J.-H. (2010). _Statistical arbitrage in the US equities market_. Quantitative Finance, 10(7), 761–782.**
   - DOI: `10.1080/14697680903124632`
   - Readable URL: `https://doi.org/10.1080/14697680903124632`
3. **Jung, J. (2025). _Statistical Arbitrage within Crypto Markets using PCA_. SSRN Electronic Journal.**（abstract-only / weak-evidence）
   - DOI: `10.2139/ssrn.5263475`
   - Readable URL: `https://doi.org/10.2139/ssrn.5263475`
4. **Binance USDⓈ-M Futures API Docs (Kline/Candlestick Data).**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 7. 本地快检产物
- `reports/artifacts/quant_digests/pca_ou_statarb_probe_20260324_1103/summary.csv`
- `reports/artifacts/quant_digests/pca_ou_statarb_probe_20260324_1103/meta.txt`
- `reports/artifacts/quant_digests/pca_ou_statarb_probe_20260324_1103/gross_returns.csv`
- `reports/artifacts/quant_digests/pca_ou_statarb_probe_20260324_1103/net_returns_4bps_oneway.csv`
- `reports/artifacts/quant_digests/pca_ou_statarb_probe_20260324_1103/turnover.csv`
- `reports/artifacts/quant_digests/pca_ou_statarb_probe_20260324_1103/positions_tail.csv`
- `reports/artifacts/quant_digests/pca_ou_statarb_probe_20260324_1103/signal_activity.csv`
