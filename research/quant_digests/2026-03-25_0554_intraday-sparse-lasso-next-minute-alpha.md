# 别把分钟级预测只做成黑箱 ML：这篇 2021 论文更值得先复现的是「rolling LASSO 稀疏一分钟 raw alpha」
- 时间：2026-03-25 05:54 UTC
- 类型：2021 论文 + ScienceOpen 摘要页 + Binance Futures 公共 1m K 线最小快检
- 主题类型：raw alpha
- 基础 alpha：用分钟级价格/成交/主动买卖不平衡/close-vs-VWAP 偏离等特征做 `rolling LASSO` 稀疏筛选，直接预测下一分钟收益；当预测值足够大时按方向做 `1m` 持有或跨币横截面 long-short
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/intraday/1m/3m/time-series/cross-sectional/lasso/sparse-signals/short-lived-predictors/taker-imbalance/vwap-gap/volume/binance/perpetual/paper
- 证据类型：论文证据 + 本地公共数据快检

> 先回答 base alpha：**不是 filter，不是“模型框架综述”。base alpha 就是“分钟级短寿命特征 → 下一分钟收益”的 directional raw alpha；LASSO 只是把可交易的那几根针从一大堆草里挑出来。**

## 1. 这次看了什么
主线材料是：
- **Vaibhav Lalwani, Vedprakash Meshram (2021), _Predicting Intraday cryptocurrency returns – A Sparse Signals approach_**，*The Journal of Prediction Markets*
- 可读页：ScienceOpen 文章页 / DOI 落地页

这轮我不把它读成“又一个机器学习论文”，而是把它拎成更适合我们 desk 的读法：

**分钟级、短持有、可直接阈值化交易的 sparse raw alpha。**

这条线的关键价值不在于“LASSO 很学术”，而在于它给了一个非常实用的 research posture：
1. 先把分钟级候选特征库铺开；
2. 允许信号只在很短的局部窗口活着；
3. 不追求单一永恒因子，而是接受“稀疏 + 短寿命 + 滚动重估”；
4. 最后直接把预测值变成可交易的 next-bar alpha。

这和我们当前 desk 的目标是对齐的：
- 优先找 **可独立复现** 的主信号；
- 允许它是 `1m / 3m` 高强度 raw alpha，而不必强行伪装成 `15m` 慢因子；
- 如果边际只在部分币种/部分状态存在，也照样值得进入素材池。

## 2. 核心结论
- 一句话核心结论：**这篇 2021 论文真正值得先复现的，不是“LASSO 打败 benchmark”这句口号，而是“分钟级 alpha 应该被当成稀疏、短寿命、滚动筛选的问题”——这本身就是可落地的 raw alpha 框架。**
- 一句话证明方式：**论文明确写的是 `minute-by-minute` 数据、`1-minute ahead out-of-sample return forecasts`、覆盖 `ten major cryptocurrencies`，并且 LASSO 预测优于 benchmark；我又用 Binance Futures 公共 `1m` K 线做了最小 proxy 快检，确认“稀疏分钟级信号”在一部分大币/高 beta 山寨上仍能留下可见边。**

关键数据点（论文原文/摘要能直接确认的）：
1. **预测目标**：`1-minute ahead` 的样本外收益预测，不是日频，不是周频。
2. **资产范围**：**10 个主要加密货币**，不是只测 BTC 单币。
3. **方法论核心**：在一大组线性 + 非线性 predictors 上做 **LASSO 稀疏筛选**，而且作者明确强调被选中的 predictors 是 **sparse and quite short lived**。

关键数据点（我做的本地最小快检；公开 Binance UM Futures `1m` K 线，2024-01-10 ~ 2024-01-24，训练 11 天 / 测试 4 天，仅作 proxy，不是 faithful replication）：
1. **DOGEUSDT**：LASSO 对下一分钟收益的测试集相关系数约 **0.0573**，略强于同特征全量线性回归的 **0.0484**；按训练集 `p10/p90` 阈值触发，long 平均约 **+0.318 bps**，short 平均约 **+0.605 bps**。
2. **XRPUSDT**：仍有弱正边，测试相关系数约 **0.0107**；说明这条线不是只在 memecoin 上成立，但边明显收缩。
3. **横截面 top1-bottom1**（BTC/ETH/SOL/XRP/DOGE/LTC 六币，每分钟按预测值做多最强、做空最弱，持有 1 分钟）：全样本平均毛收益约 **+0.015 bps/min**；只做预测分差高于中位数的“更确信”一半分钟，平均毛收益约 **+0.112 bps/min**，命中率约 **50.8%**。
4. **异质性非常强**：BTC 基本接近零，SOL 在该样本窗为负，LTC 甚至被 LASSO 直接稀疏到 **0 个有效特征**。这反而很重要：它说明这条 edge 更像 **局部/状态依赖 alpha**，而不是“全市场无差别一分钟圣杯”。

## 3. 为什么和当前项目直接相关
这条线和我们现在的短周期研发直接相关，原因有四个：

1. **它是 raw alpha，不是 filter。**
   预测对象就是下一分钟收益本身。
2. **它天然适配 `1m / 3m`。**
   不需要硬把低频变量拉扯成高频；原论文就是分钟级。
3. **它能同时服务单币和横截面。**
   单币可以做 sign/threshold 入场；横截面可以做 top-vs-bottom market-neutral。
4. **它给了“研究流程模板”而不是只给一个指标。**
   对我们更值钱的是：以后新来的 flow / OI / VWAP / basis / liquidation 特征，也都能塞进同一套 sparse-screening 框架里做分钟级快检。

## 3.5 策略拆解（必填）
- 方向属性：单币时间序列 + 可扩展到横截面的分钟级 directional raw alpha
- 基础 alpha：
  - 过去 `1~5` 分钟收益滞后项
  - candle body / range
  - volume / trade count z-score
  - taker buy ratio / taker imbalance
  - close-vs-VWAP gap
  - 短窗 realized vol
  - 若干交互项（如 `ret × volume_z`）
  - 通过 `rolling LASSO` 只保留当下仍活着的少数特征，预测 `r_{t+1m}`
- entry：
  - **单币版**：`pred > q90` 做多，`pred < q10` 做空
  - **横截面版**：每分钟 long 预测最高的 1~2 个币，short 最低的 1~2 个币
- exit：
  - 默认持有 `1m`
  - 扩展测试 `2m / 3m`
  - 若中途要做更高频执行版，可在 bar 内看到预测翻符号就提前平仓
- sizing：
  - 初版固定 notional
  - 二版按 `|pred| / rolling_vol` 或 `pred_rank` 分层仓位
- risk：
  - 每分钟最大换手限制
  - 连续亏损停机
  - 只在 top liquidity bucket 交易
  - news / funding settlement / 大幅跳变分钟可先 veto
- cost：
  - 必须显式计入 taker fee + spread + 低流动币冲击
  - `1m` raw alpha 很容易在看起来有边时被成本吃掉，不能只看 gross

## 4. 对 desk 最有价值的，不是“预测强不强”，而是“怎么把它变成可持续 intake 模板”
如果只把这篇论文读成“LASSO 比 benchmark 强”，价值其实有限。

真正能被我们拿走的是这套框架：

### A. 把分钟级 raw alpha 当成“短寿命稀疏信号”来研究
这很符合 crypto 的现实：
- 结构变得快；
- 币种差异大；
- 同一个 predictor 不会一直有边；
- 但在某些时段、某些币上会突然变得很有用。

所以比起追求一条固定规则，更现实的是：
- 做一个 **候选特征库**；
- 做 **滚动稀疏筛选**；
- 接受 edge 会轮换；
- 然后只交易“当前活着的那部分”。

### B. 它能作为新特征 intake 的统一骨架
后面不管我们往里加的是：
- funding / basis
- liquidation / OI
- order-flow proxy
- cross-asset lead-lag
- session / clock 特征

都可以先问同一个问题：

**“把它塞进 rolling sparse model 以后，能不能在 next 1m / 3m return 上留下额外信息？”**

如果答案是能，这个新特征就不是纯解释，而是真的进了 raw alpha 池。

### C. 它更适合 alt bucket，而不是默认押在 BTC 上
这次本地 proxy 快检最有意思的一点，不是“平均有边”，而是：
- DOGE 有点像可以继续挖；
- XRP 勉强留痕；
- BTC 很弱；
- SOL 在样本窗里反而反向；
- LTC 干脆被稀疏掉。

这说明如果真做下一轮最小复现，**优先级不该是 BTC first**，而应该是：
- 先分 liquidity / retail participation bucket；
- 再看 sparse minute alpha 到底更偏哪一类币。

## 5. 可复刻的最小实验（下一步怎么测）
**研究假设**：
`rolling sparse feature selection` 能在一部分 crypto perp 上形成可交易的 `1m` directional alpha，但收益高度依赖币种分层、阈值稀释和交易成本。

**数据源与公开性**：
- 数据源：Binance Data Vision，UM Futures 公共 `1m` K 线
- 公开性：公开可得，无私钥
- 更新频率：`1m`
- 最小可复现实验口径：下载 `1m` daily zip 即可

**最小实验设计**：
1. **标的分层**：
   - core：`BTC / ETH`
   - liquid beta：`SOL / XRP`
   - retail beta：`DOGE / PEPE / WIF`（若数据可得）
2. **样本切法**：
   - walk-forward：`train 14d / test 3d`
   - 连续滚动至少 8~12 个窗口
3. **特征库**：
   - ret lags
   - volume / trade-count z-score
   - taker imbalance
   - close-vs-VWAP gap
   - realized vol
   - session/time-of-day
   - 允许加入 `funding/basis/OI` 做增量 A/B test
4. **持有期网格**：`1m / 2m / 3m`
5. **阈值网格**：按训练集预测分位数做 `80 / 90 / 95 / 97.5` 分位触发
6. **成本阶梯**：
   - `fee only`
   - `fee + 0.5 tick`
   - `fee + 1 tick`
   - `fee + spread proxy + impact haircut`

**最先看 5 个指标**：
- `IC(pred, next_ret)`
- `avg bps/trigger`
- `turnover / triggers per day`
- `post-cost pnl`
- `nonzero feature stability`（每个窗口被选中的特征是否持续）

**这条线最应该先做的 3 个实验**：
1. **bucket test**：按 liquidity / trade-count / retail-beta 分组，看 sparse edge 是否显著集中在某一类币
2. **feature survival map**：记录每个滚动窗里被选中的特征，判断哪些是真正“偶尔复活”的分钟级 edge
3. **time-series vs cross-sectional**：同一组预测值，比较“单币阈值交易”和“横截面 top-bottom 配对”哪个更抗成本

## 6. 风险与保留意见
- 原论文强调的是“稀疏且短寿命”，这本身就意味着 **不稳定是 feature，不是 bug**；如果要求单一特征长期稳定，反而会错杀这类 alpha。
- 我做的本地快检只用了 **公开 1m K 线 proxy**，还没上更细的 trade/book 数据，所以目前更像 **研究可行性证明**，不是 faithful replication。
- `1m` alpha 很容易被手续费、spread、冲击吃掉；当前看到的几组毛边，不能自动外推出净边。
- 若后续加入更多外部变量（funding / OI / basis），要特别小心数据对齐和 lookahead。

## 7. 一句话结论
**这篇东西值得进研究池，不是因为“LASSO 很高级”，而是因为它把 `1m` crypto alpha 讲成了一个非常诚实的命题：信号是短寿命、稀疏、币种异质、需要滚动筛选的。对我们 desk 来说，这比再找一个固定阈值规则更有扩展性。**

## 8. 来源
1. **Lalwani, V., & Meshram, V. (2021). _Predicting Intraday cryptocurrency returns – A Sparse Signals approach_. The Journal of Prediction Markets, 15(1).**
   - DOI: `10.5750/jpm.v15i1.1840`
   - Readable URL: `https://www.scienceopen.com/document?vid=d8260931-fd27-431c-a910-e94015198a8a`
   - DOI URL: `https://doi.org/10.5750/jpm.v15i1.1840`
   - Journal page: `http://ubplj.org/index.php/jpm/article/view/1840`
2. **ScienceOpen article metadata / abstract page**
   - URL: `https://www.scienceopen.com/document?vid=d8260931-fd27-431c-a910-e94015198a8a`
3. **Binance Data Vision, UM Futures public 1m klines**
   - URL: `https://data.binance.vision/`

## 9. 本地快检产物
- `reports/artifacts/quant_digests/sparse_lasso_intraday_probe_20260325/symbol_summary.csv`
- `reports/artifacts/quant_digests/sparse_lasso_intraday_probe_20260325/top_coefficients.csv`
- `reports/artifacts/quant_digests/sparse_lasso_intraday_probe_20260325/predictions_head.csv`
- `reports/artifacts/quant_digests/sparse_lasso_intraday_probe_20260325/xs_top1_bottom1.csv`
- `reports/artifacts/quant_digests/sparse_lasso_intraday_probe_20260325/xs_summary.csv`
