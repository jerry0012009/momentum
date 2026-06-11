# 别把这篇 2019 crypto stat-arb 论文直接翻译成今天的 liquid-major perp alpha：对 short-cycle desk，更该先测的是「lag-stack RF × 120m 横截面中位数超额」这条 raw alpha——但当前 majors 版本明显不过成本线
- 时间：2026-04-13 13:46 UTC
- 类型：2019 *Journal of Risk and Financial Management* 论文摘要/元数据（OpenAlex + Crossref）+ GitHub repo source audit（`README.md` + `crypto_forest_example.py` + `feature_generator.py` + `crypto_dataprovider.py` + `kpi_backtest.py`）+ Binance USDⓈ-M `5m/15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：`用多尺度滞后收益去预测“哪几个币会在未来 120 分钟跑赢当下横截面中位数”，然后做 long top-k / short flop-k 的 market-neutral spread`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / relative-value / stat-arb / machine-learning / random-forest / lagged-returns / median-relative-target / 120m / market-neutral / binance-perpetual / 5m / 15m / paper / repo / public-data / cost / risk
- 证据类型：论文摘要 + 开源代码 + 公共数据 portability probe

## 1. 这次看了什么
这次主看 **Thomas Fischer, Christopher Krauß, Alexander Deinert (2019), _Statistical Arbitrage in Cryptocurrency Markets_**，以及作者配套公开的 GitHub 代码仓库。它不是那种“讲一个因子名词就结束”的文章，而是一个很明确的 **横截面 market-neutral 预测壳**：

1. 用分钟级多尺度滞后收益做特征；
2. 预测某个币在未来 `120min` 是否会跑赢当期横截面中位数；
3. 做 **long top-k / short flop-k**；
4. 持有 `120min` 后反手平仓。

这对我们 desk 有价值，因为它补的是 **cross-sectional / relative-value / stat-arb** 方向，而不是再绕回单币 breakout / retest 内循环。

不过，这篇东西最容易被误读成：
- “2018 年 paper 有 alpha，今天 perp 上照抄就行”；或
- “ML 比传统规则强，所以直接把 RF 模型搬上去。”

我这轮更关心的是：**它的 base alpha 到底是不是今天还能落到 `5m/15m` desk 上的 raw alpha？**

## 2. 核心结论
- **一句话核心结论：** 这篇 paper 的 base alpha 很清楚，确实是一条可独立复现的 **横截面 relative-value raw alpha**；但把它压到今天的 Binance liquid majors perpetual 上，**gross 只剩很薄一层，净后基本被成本吃穿**，所以现阶段更像“研究母体 + 宽 universe / 低成本执行候选”，还不适合直接当 taker 主策略上线。
- **论文原始信号长什么样：** OpenAlex 摘要写得很直白——作者在 `40` 个加密货币的 minute-binned 数据上，用 **lagged returns** 训练 random forest，预测未来 `120min` 是否跑赢横截面中位数；然后 **买 top-3、做空 flop-3，持有 120 分钟**。摘要里给出的 out-of-sample 结果是：**2018-06-18 到 2018-09-17，超过 100,000 笔交易，扣掉 `15bps per half-turn` 后，仍有 `7.1bps/day`**。
- **代码层面的可复刻骨架也很清楚：**
  - `crypto_forest_example.py` 里把 `FORECAST_HORIZON = 120`（分钟）；
  - `feature_generator.py` 用的特征是 **过去 `1~20` 分钟收益**，再加上 **`120, 240, ..., 1440` 分钟收益**；
  - `helper.py` 里的目标定义不是“绝对涨跌”，而是 **是否高于当期横截面中位数**；
  - `kpi_backtest.py` 还额外加了 **staleness / volume filter**。
- **但 repo 和摘要不是完全一模一样：** 摘要说的是 `top-3 / flop-3`，而 repo 回测函数里默认 `K=5`。这说明它更像一个研究框架，而不是单一固定参数的“标准答案”。
- **我做的 Binance USDⓈ-M `5m` portability probe（近 `28d`，`10` 个 liquid majors，RF，`120min` 目标，`top2/flop2`）结果是：**
  - 测试样本 `2664` 个组合时点，`9371` 笔单腿交易；
  - **gross 平均仅 `+0.90bps / 120m`**；
  - 若按每条腿 **round-trip `8bps`** 粗扣，**net 变成 `-6.50bps / 120m`**；
  - 净胜率只有 **`33.4%`**；
  - 单腿净均值约 **`-7.40bps`**。
- **`15m` portability probe（近 `60d`，同样 `10` 个 majors，仍看未来 `120min`）更差：**
  - `1901` 个组合时点，`6971` 笔单腿；
  - **gross `-0.81bps / 120m`**；
  - **net `-8.43bps / 120m`**；
  - 即便只保留预测分差较大的时点（`pred_spread >= 0.12`），gross 也只是 **`+3.47bps`**，net 仍约 **`-4.53bps`**。
- **特征重要性倒是有启发：** 两版 probe 里都不是最短 lag 独大，而是 **`ret_24 / ret_36 / ret_48`**（也就是更偏中段的历史收益窗）经常排在最前面。这更像在说：这条线的可交易部分不是“下一根 bar 随手追”，而是 **多尺度 lag 结构里提炼出来的横截面强弱差**。

## 3. 为什么和当前项目有关
虽然这轮 portability 结论偏负面，但它对当前项目依然有直接价值：

### 3.1 它补的是我们明确想补的方向
这不是又一条单币 trend / breakout 线，而是很标准的：
- **cross-sectional**
- **relative-value**
- **stat-arb / market-neutral**

这正好符合这轮 bot7 想主动补的方向。

### 3.2 它把“alpha 本体”和“执行壳”拆得很清楚
这篇 paper/repo 最有价值的地方，不是“random forest”四个字，而是它把 alpha 主体定义得很干净：

> **alpha 本体 = 未来 `120min` 的横截面相对强弱可由过去多尺度 lag return 预测。**

至于：
- 做 `top3` 还是 `top5`
- 要不要加 staleness filter
- 成本假设多大
- 做 spot 还是 perp
- 做 majors 还是更宽 alt universe

这些都是 **壳层 / 执行层**，不是 alpha 定义本身。

### 3.3 它给了一个很重要的负面筛选结论
当前 liquid-major perp 上，这条线的问题不是“完全没有方向感”，而是：
- **gross 有一点点；**
- **但远远不够覆盖 taker 成本。**

这意味着它更可能属于：
1. **更宽 universe 才有用**；
2. **maker-first / rebate / internal-cross / queue 优势** 才有用；
3. 或者要被降级为 **shared rank feature / filter**，而不是单独上线的主策略。

这类“不能直接上，但知道为什么不能上”的结论，对素材池同样有价值——至少能避免我们再把时间花在“liquid majors 上照搬论文壳”这条低胜率路线。

## 3.5 策略拆解（必填）
- 方向属性：`cross-sectional / relative-value / market-neutral`
- 基础 alpha：`过去多尺度 lag return 能预测未来 120 分钟谁会相对横截面中位数更强/更弱`
- raw alpha 本体：`long top-k predicted outperformers / short flop-k predicted underperformers`
- regime：更可能要求 **更宽币池、足够横截面离散度、较低有效费率**，而不是只在 `BTC/ETH/SOL` 这种超拥挤 majors 上做 taker
- filter / veto：
  - `prediction spread` 不够大时不做；
  - `staleness / volume` 不够时不做；
  - 若有效 round-trip 成本 > 预期 gross edge，直接 veto
- risk / sizing / execution overlay：
  - 先做 dollar-neutral 或 beta-neutral；
  - 单时点最多做 `top2~3 / flop2~3`；
  - 先用 maker-first 或低费账户做；
  - 若只能 taker，必须先证明 gross edge 至少明显高于 `6~8bps / leg`

## 4. 可复刻的最小实验
### 4.1 论文最小复刻口径
- **目标定义：** 对每个时点、每个币，预测未来 `120min` 回报是否高于横截面中位数；
- **特征：** 过去 `1~20` 分钟收益 + `120~1440` 分钟多尺度 lag return；
- **组合：** long top-k / short flop-k；
- **持有：** `120min`；
- **评估：** gross / net return、胜率、换手、不同成本桶。

### 4.2 我这轮已经做的最小 portability probe
- **数据源：** Binance USDⓈ-M public klines
- **公开性：** 完全公开可取
- **更新频率：** `5m / 15m`
- **口径：**
  - universe：`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC`
  - target horizon：`120min`
  - train/test：时间切分 `2/3 : 1/3`
  - 模型：`RandomForestClassifier`
  - 组合：`top2 / flop2`
  - 成本：粗扣 **`8bps round-trip / leg`**

### 4.3 下一步最该怎么测
这篇东西**值得继续测**，但不是继续在 10 个 majors 上死磕。最优先是下面 3 步：

1. **把 universe 扩到 `30~50` 个 liquid alts**
   - 这篇 paper 的核心不是“预测 BTC 下一根涨跌”，而是 **横截面分化**。
   - 若横截面太窄，alpha 会天然变薄。

2. **显式做成本分桶：`2 / 4 / 8 / 12bps`**
   - 这条线最大的敌人就是换手；
   - 不做费率分桶，等于不知道它到底是“没有 alpha”，还是“有 alpha 但只属于低费账户 / maker book”。

3. **把它降维成 desk 更易落地的 shared rank feature**
   - 不一定要整套 RF 直接上线；
   - 也可以先把它变成：
     - `xs router`：决定做 continuation 还是 reversal；
     - `pair admission`：只在 rank gap 最大的 pair/basket 上做 spread；
     - `position veto`：当模型分差太小，直接不做。

### 4.4 这轮最该先看的 2 个指标
1. **`post-cost mean bps / rebalance`**（分费率桶看）
2. **`prediction-spread bucket` 下的边际改善**（判断它到底是“需要强分歧过滤”，还是根本没有 edge）

## 5. 风险与保留意见
- 论文摘要给出的结果样本集中在 **2018**，属于 crypto 市场更“野”的早期阶段；直接外推到 2026 年 liquid major perp，很容易高估可移植性。
- 我这轮 probe 只测了 `10` 个 liquid majors，**非常可能低估** 这类横截面策略在更宽 alt universe 上的可用性。
- 当前 probe 的成本假设是偏 desk 现实的 taker 粗口径；若你有更低的费率、maker 优势、内部撮合或更弱流动性的币池，结论可能变化很大。
- repo 示例与摘要参数并不完全一致（`top3/flop3` vs `K=5`），说明“论文 headline 数字”并不是唯一需要复刻的对象；真正要复刻的是 **方法骨架 + 成本边界**。

## 6. 本地 artifacts
- `reports/artifacts/literature/crypto_stat_arb_rf_portability_probe_2026-04-13_summary.json`
- `reports/artifacts/literature/crypto_stat_arb_rf_portability_probe_2026-04-13_portfolio.csv`
- `reports/artifacts/literature/crypto_stat_arb_rf_portability_probe_2026-04-13_trades.csv`
- `reports/artifacts/literature/crypto_stat_arb_rf_portability_probe_15m_2026-04-13_summary.json`
- `reports/artifacts/literature/crypto_stat_arb_rf_portability_probe_15m_2026-04-13_portfolio.csv`
- `reports/artifacts/literature/crypto_stat_arb_rf_portability_probe_15m_2026-04-13_trades.csv`

## 7. 来源
1. **Fischer, T., Krauß, C., & Deinert, A. (2019). _Statistical Arbitrage in Cryptocurrency Markets_. Journal of Risk and Financial Management, 12(1), 31.**
   - DOI: `10.3390/jrfm12010031`
   - DOI URL: `https://doi.org/10.3390/jrfm12010031`
   - Readable URL: `https://www.mdpi.com/1911-8074/12/1/31`
   - Open-access PDF URL: `https://www.mdpi.com/1911-8074/12/1/31/pdf?version=1550193651`
2. **OpenAlex metadata / abstract reconstruction**
   - `https://api.openalex.org/works/https://doi.org/10.3390/jrfm12010031`
3. **Crossref metadata**
   - `https://api.crossref.org/works/10.3390/jrfm12010031`
4. **配套代码仓库**
   - Repo URL: `https://github.com/Exceluser/Statistical-arbitrage-in-cryptocurrency-markets`
   - README: `https://raw.githubusercontent.com/Exceluser/Statistical-arbitrage-in-cryptocurrency-markets/master/README.md`
   - Core files:
     - `crypto_forest_example.py`
     - `feature_generator.py`
     - `crypto_dataprovider.py`
     - `helper.py`
     - `kpi_backtest.py`
5. **Binance USDⓈ-M public market data**
   - Klines: `https://fapi.binance.com/fapi/v1/klines`
