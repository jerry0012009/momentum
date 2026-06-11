# 别把 stablecoin dry powder 硬装成 15m 主信号：这篇 2026 新论文更该先测的是「stablecoin cap impulse → XS momentum / breakout size-up regime」
- 时间：2026-03-25 14:57 UTC
- 类型：2026 arXiv 新论文（全文 HTML 可读）+ 论文自带公开 repo 线索 + DeFiLlama/Binance 公共数据最小快检
- 主题类型：regime
- 基础 alpha：`15m` 横截面动量 / breakout continuation；stablecoin 因子只作为慢变量 risk-on/risk-off gate，不伪装成 bar-by-bar alpha 本体
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：regime/shared-gate/stablecoin/dry-powder/external-data/cross-sectional-momentum/breakout/position-sizing/risk-on-risk-off/defillama/binance/crypto/15m/5m/1m/paper/repo
- 证据类型：论文全文证据 + 论文自带 repo 线索 + 本地公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西本身不是 raw alpha。** 如果硬要问它服务谁，最适合服务的是 **`15m XS momentum / breakout continuation / carry`** 这类顺风吃 beta 与扩散的策略；所以它应该被归类为 **`regime gate / sizing overlay`**，而不是伪装成逐根主信号。

这轮值得 intake，不是因为它告诉你“stablecoin 很重要”这种空话，而是因为它把这个点做成了 **可检验的、带数值的、带组合结果的模型**：
- 用 **stablecoin volume / upside vol / downside vol** 去解释更广义 crypto 市场波动；
- 不只做 in-sample 因果，还做 **OOS forecasting + volatility targeting**；
- 最后给出的是 **“更低 MSE + 更好的 drawdown / Sortino”**，这正适合 desk 拿来做慢变量 gate。

对我们 desk 来说，最可移植的不是论文 headline 里的“日频波动预测器”，而是一个更实用的旁支：
**当 stablecoin 供给/活动在累积时，只把它当作“风险预算是否应该打开”的 shared regime；不要把它硬写成 15m 下一根涨跌预测器。**

## 2. 核心结论
- **一句话核心结论：** 这篇 2026 新论文更值钱的，不是给你一个新的日频 vol model，而是给了一个相当像样的证据链：**stablecoin 的“活动 + 累积”确实领先更广义的 crypto 波动环境，因此它更适合作为短周期 raw alpha 的慢变量 risk-on gate。**
- 论文基本信息：
  - Authors: **Elliot Jones, Toshiko Matsui, William Knottenbelt**
  - Year: **2026**
  - Title: **Stablecoins as Dry Powder: A Copula-Based Risk Analysis of Cryptocurrency Markets**
  - Venue/Source: **arXiv preprint**
  - DOI: **10.48550/arXiv.2603.23480**
- 论文样本与数据：
  - 时间：**2020-01-01 到 2025-01-01**
  - stablecoins：**DAI / USDC / USDT**（文中称 3Pool）
  - cryptocurrencies：**BTC / ETH / BNB / XRP**
  - 频率：**daily**
  - 数据源：**Investing.com OHLCV**
- 方法：
  - **Copula Granger Causality (CGC)** 看非线性因果；
  - **E-GARCH + Copula + XGBoost** 做 OOS volatility forecasting；
  - 最后把预测转成 **volatility targeting** 组合。
- 最硬的几个数：
  - OOS MSE backtest 里，**stablecoin upside vol → crypto upside vol** 的 challenger 相对 benchmark **MSE 降低 9.48%**；
  - **stablecoin volume → crypto downside vol** 相对 benchmark **MSE 降低 4.62%**；
  - **stablecoin downside vol → crypto downside vol** 相对 benchmark **MSE 降低 3.44%**。
- 组合层更关键：
  - 在 **20% vol target** 下，challenger 组合是 **46.6% annual return / 22.3% annual vol / -12.9% max drawdown / 2.77 Sortino**；
  - 对照 benchmark 是 **40.8% / 24.3% / -15.8% / 1.96**；
  - 在 **50% vol target** 下，challenger 是 **100.4% / 44.7% / -24.1% / 3.38**；
  - 对照 benchmark 是 **95.8% / 46.1% / -26.9% / 3.04**，Buy & Hold 是 **89.0% / 51.4% / -33.0% / 2.47**。

翻成人话：**stablecoin 因子更像“市场能不能承受更高风险暴露”的底层流动性温度计，而不是 15m 下一根方向键。**

## 3. 为什么和当前项目直接相关
- 它不是 raw alpha，但它是一个**明显服务多类 raw alpha 的 shared regime**：
  - `XS momentum`
  - `breakout continuation`
  - `carry / basis / funding` 的 size-up 或 veto
- 它比很多“纯解释型 stablecoin 叙事”强的地方在于：
  - 有 **明确样本**；
  - 有 **明确模型**；
  - 有 **明确 OOS 指标**；
  - 有 **组合层 economic value**，不只是统计显著。
- 对短周期 desk 的真实映射是：
  - stablecoin 因子本身更新慢，所以**天然不该做主 trigger**；
  - 但它很适合决定：**今天/这几个小时，是不是值得把 15m 趋势/XS alpha 开满、缩小、还是干脆 veto。**

## 3.5 策略拆解（必填）
- 方向属性：shared regime / sizing overlay
- 基础 alpha：`15m` 横截面动量 或 breakout continuation
- regime：stablecoin dry-powder 处于扩张 / 累积状态时，允许更高风险预算；反之降档或关闭
- filter / veto：当 stablecoin 累积转弱、或“dry-powder proxy”连续回落时，禁做高换手顺势单
- risk / sizing / execution overlay：
  - `gate_on`：正常仓位或加到 `1.0x~1.25x`
  - `gate_off`：降到 `0~0.5x`
  - 只改 **risk budget**，不改 alpha 本身的 entry 逻辑

## 4. 本地最小快检（DeFiLlama + Binance，desk 口径 proxy，不是论文精确复现）
我补了一个很轻的 desk-side probe，只测一句话：
**“stablecoin dry powder” 这类慢变量，拿来当 `15m XS momentum` 的开关，会不会比全天候裸跑更诚实？**

- stablecoin 数据：**DeFiLlama `stablecoincharts/all`**（公开 API）
- 代理变量：**stablecoin total circulating USD**
- 频率：**daily**
- crypto 数据：**Binance USDⓈ-M Futures 公共 `15m` K 线**
- 宇宙：`BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK`
- 样本：**2025-09-06 到 2026-03-25**，共 **19,200 根 15m bar**
- base alpha proxy：
  - 每小时 rebalance 一次；
  - 按过去 **24h return** 做 `15m XS momentum`；
  - **long top-2 / short bottom-2**；
  - 下一小时持有；
  - 成本代理：`0.0006 × turnover`
- gate 定义：
  - `cap_7d_ret > 0`
  - 且 `3d rolling mean(cap_1d_ret) > 0`

### 4.1 结果
结果非常诚实：**它没有把这条粗糙 XS momentum proxy 从负变正，但确实显著减少了“在坏 regime 里硬做”的损失与换手。**

- gate 打开时间占比：**55.7%**
- 不上 gate 时：
  - gross 累计约 **-3387 bps**
  - net 累计约 **-14079 bps**
  - 平均每 bar turnover 约 **0.0928**
- 上 gate 后：
  - gross 累计约 **-1490 bps**
  - net 累计约 **-7397 bps**
  - 平均每 bar turnover 约 **0.0513**
- 相比裸跑：
  - **gross loss 缩小约 56.0%**
  - **net loss 缩小约 47.5%**
  - **turnover 缩小约 44.8%**
- 从“gate 当天 vs 非 gate 当天”的日均读法看：
  - gate-on 日的未加门 alpha 日均 gross 约 **-13.2 bps**
  - gate-off 日约 **-21.6 bps**

翻成人话：**这个 proxy 没能证明 stablecoin 因子能“制造 alpha”，但它很像能帮助你少在不该开火的时候开火。** 这正是 regime gate 应该干的活。

## 5. 外部数据口径（必须写清）
这条线主要依赖外部公开数据，所以必须老实说明：

- 论文原始数据口径：
  - 来源：**Investing.com OHLCV**
  - 资产：`DAI / USDC / USDT` 与 `BTC / ETH / BNB / XRP`
  - 频率：**daily**
  - 用途：做 stablecoin volume / upside vol / downside vol 与 crypto volatility 的关系建模
- desk 最小可复现实验口径：
  - 来源 1：**DeFiLlama `https://stablecoins.llama.fi/stablecoincharts/all`**
  - 公开性：**公开可得，无需私有 key**
  - 更新频率：**daily snapshot 口径足够**
  - 来源 2：**Binance Futures 公共 `15m` K 线**
  - 映射方式：把 daily stablecoin gate **forward-fill 到 `15m`**，只拿来控制仓位/开关，不拿来逐根预测

## 6. 最小可复现实验（面向 15m / 5m）
如果把它正式接到 desk，我建议最小实验从下面这个版本开始：

1. **先固定 base alpha**
   - `15m XS momentum` 或 `15m breakout continuation`
   - 不要同时改 alpha 本体，避免把 gate 评估搞脏
2. **先固定 gate 更新频率**
   - 每天更新一次 stablecoin gate，日内 forward-fill
3. **先做 3 档风险预算**
   - `off = 0x`
   - `half = 0.5x`
   - `on = 1.0x`
4. **最小 gate 候选**
   - `stablecoin total cap 7d change`
   - `stablecoin total cap 3d slope`
   - 后续再补论文更贴近的 `volume / upside vol`
5. **比较口径**
   - raw alpha 裸跑
   - raw alpha + binary gate
   - raw alpha + ternary sizing (`0/0.5/1.0`)
6. **核心指标**
   - post-cost return
   - turnover
   - tail drawdown
   - worst-day / worst-week loss
   - gate-on / gate-off 的 signal quality split

## 7. 下一步怎么测（必须）
1. **不要把它当成“stablecoin 会不会涨”的方向预测题**：只评估它作为 `risk budget gate` 有没有边际价值。  
2. **优先接两条 raw alpha 做 A/B test**：`15m XS momentum` 与 `15m breakout continuation`，看它到底只对 beta-heavy alpha 有用，还是对 breakout 也有用。  
3. **把论文里的 `volume / upside vol` 换成更 desk-friendly 的公开 proxy**：例如 stablecoin 总供给、USDT/USDC 供给变动、稳定币对成交活跃度。  
4. **做 `binary gate` 与 `ternary sizing` 对照**：很多 shared regime 的价值不在“全开/全关”，而在 `1x -> 0.5x` 的 drawdown 缓冲。  
5. **补 `5m execution split`**：若 gate 只改方向暴露，不改执行，下一轮应看它能否减少高换手亏损时段的下单频率。  
6. **若后续证据继续成立，再接 carry / funding / basis 线**：这类慢变量可能对 `carry spread` 的风险预算也更有解释力。

## 8. 风险与保留意见
- **这不是 raw alpha。** 若 desk 当前更缺的是可独立落地的新 raw alpha，本主题只能排在第二梯队。  
- 论文是 **daily**，短周期 desk 只能把它当慢变量；硬把它改写成逐根 15m 主信号，大概率会失真。  
- 我本地快检用的是 **stablecoin total circulating USD** 代理，不是论文原始 `volume + upside vol` 全套口径，所以它只是 portability check。  
- 本地 proxy 里 base alpha 本身是负的，因此当前证据只能说明 **“减少坏交易”**，不能说明 **“创造新收益”**。  
- stablecoin 因子很容易和更广义 risk-on beta 共线，所以后续必须做 **独立增量检验**，不能把市场上涨期都误判成 stablecoin gate 的功劳。

## 9. 来源
1. **Jones, E., Matsui, T., & Knottenbelt, W. (2026). _Stablecoins as Dry Powder: A Copula-Based Risk Analysis of Cryptocurrency Markets_. arXiv.**  
   - Venue: arXiv preprint  
   - DOI: `10.48550/arXiv.2603.23480`  
   - Readable URL: `https://arxiv.org/abs/2603.23480`  
   - HTML URL: `https://arxiv.org/html/2603.23480`  
   - PDF URL: `https://arxiv.org/pdf/2603.23480.pdf`

2. **EllbellCode. _StablecoinAnalysis_.**  
   - Repo URL: `https://github.com/EllbellCode/StablecoinAnalysis`  
   - 说明：论文正文脚注明确写到 code / datasets / plots online at 该仓库。

3. **DeFiLlama Stablecoins API.**  
   - URL: `https://stablecoins.llama.fi/stablecoincharts/all`  
   - 用途：desk 最小实验里的 stablecoin total circulating USD 公开代理数据。

4. **Binance Developers. USDⓈ-M Futures API – Kline/Candlestick Data.**  
   - URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 10. 本地复现产物
- `reports/artifacts/quant_digests/stablecoin_dry_powder_gate_20260325_1455/summary.json`
- `reports/artifacts/quant_digests/stablecoin_dry_powder_gate_20260325_1455/stablecoin_cap_daily.csv`
- `reports/artifacts/quant_digests/stablecoin_dry_powder_gate_20260325_1455/proxy_panel_15m.csv`
- `reports/artifacts/quant_digests/stablecoin_dry_powder_gate_20260325_1455/proxy_daily_summary.csv`
- `reports/artifacts/quant_digests/stablecoin_dry_powder_gate_20260325_1455/probe_notes.txt`
