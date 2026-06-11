# 别把这篇 DLSA 只读成美股机器学习大工程：对 crypto short-cycle desk，更该先测的是「conditional latent-factor residual portfolio × conv-transformer trading policy」这条 cross-sectional raw alpha
- 时间：2026-04-03 08:48 UTC
- 类型：2021/2022 working paper（arXiv / SSRN）+ 官方 GitHub repo source audit（`README.md` + `configs/cnntransformer-full.yaml` + `preprocess.py` + `models/CNNTransformer.py` + `train_test.py` + `run_train_test.py`）
- 主题类型：raw alpha
- 基础 alpha：先把市场共同因子剥掉，只交易**条件潜在因子残差组合**里的短周期错配；alpha 本体是 **cross-sectional / relative-value / stat-arb 的 residual mispricing**，不是 Transformer 本身。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/stat-arb/latent-factor/residual-portfolio/convolutional-transformer/trading-policy/cost-aware/continuous-weights/binance-perp/hyperliquid/1m/3m/5m/15m/paper/repo/public-data
- 证据类型：论文摘要/项目摘要（主框架证据）+ 官方 repo 策略与训练代码（工程骨架证据）

**先回答 base alpha：这篇东西的 base alpha 是清楚的——不是“AI 会自己找机会”，而是“把公共因子剥掉以后，剩下的 residual portfolio 里仍有可交易的局部 trend / reversion 结构”；模型只是负责把这些 residual 信号映射成 after-cost 的连续权重。**

## 1) 这次看了什么
我这次主要看的是两类材料：

### 论文 / 项目摘要
- Jorge Guijarro-Ordonez, Markus Pelger, Greg Zanotti. **Deep Learning Statistical Arbitrage**.
- arXiv 摘要页
- NBER-NSF 2021 workshop 项目摘要页

### 官方代码仓库
- `gregzanotti/dlsa-public`
- `README.md`
- `configs/cnntransformer-full.yaml`
- `preprocess.py`
- `models/CNNTransformer.py`
- `train_test.py`
- `run_train_test.py`

这套材料最值钱的地方，不是 headline 的“deep learning”，而是它把一条**面板式 stat-arb raw alpha**拆成了完整流水线：

> **因子剥离 → residual panel → 时序特征提取 → 连续权重分配 → after-cost Sharpe 目标训练**

## 2) 一句话核心结论（给 desk 的版本）
- **一句话结论**：如果我们不想继续只在“单 pair / 单币 / 单一价差”里内卷，这篇 DLSA 更值得先拿来做的是一套**panel-level raw alpha 生成器**：先从整个 perp 宇宙里抽 residual portfolio，再让模型只在 residual 上学局部 continuation / mean-reversion 结构。
- **为什么它和当前 desk 有关**：最近 intake 已经积累了不少 `pairs / basis / premium / loser-bounce / trend` 的单条 alpha 壳；这篇补的是更上游的一层——**怎么把 20~50 个币的一整个横截面，压成一组可交易 residual alpha 组合**。
- **它最适合我们的读法**：不是照搬美股 daily 数据，而是把它读成：
  - `factor stripping` = 把市场 beta / sector / funding / basis / OI 这些共同驱动先剥掉；
  - `residual timing` = 只在剩余偏离里找短周期 edge；
  - `continuous allocation` = 不做二元开关，而做连续仓位分配。

## 3) 为什么这轮值得写
### 3.1 它不是又一个“再补一条 pair”
最近 digest 已经有很多：
- `dynamic coint spread`
- `same-underlier premium fade`
- `cross-venue basis`
- `top-N loser bounce`
- `realized-skewness cross-section fade`

这些都好用，但多数还是**一条 alpha = 一套规则**。DLSA 更值得进池的原因是：

**它提供的是“alpha 工厂”而不是单一招式。**

也就是：
- 不是先定某个 pair，再做 z-score；
- 而是先在整个宇宙里提 residual portfolio；
- 再把 residual 序列交给统一模型做 long/short 分配。

### 3.2 它补的是 desk 当前相对缺的“panelized stat-arb”层
当前 short-cycle 研究池里，单币趋势 / 单 pair 回归 / same-underlier 偏离已经不少；
但**横截面 residual 组合**这一层仍然偏少。

这篇正好补三块：
1. **cross-sectional raw alpha**：不是单标的，而是整池分配；
2. **relative-value / stat-arb**：先剥共同因子，再赌残差错配；
3. **完整策略骨架**：信号、仓位、成本、short hold cost 都写进训练目标。

### 3.3 为什么它比继续补一个普通 raw alpha 更值
因为它不是替代现有 raw alpha，而是能把现有 raw alpha 家族往上抽象成一个统一框架：
- `pairs / stat-arb`
- `cross-sectional reversal`
- `market-neutral momentum`
- `basis / funding / OI residualization`

都可以往这套 residual-portfolio 逻辑里塞。

## 4) 来源信息
### 论文
- **Authors：** Jorge Guijarro-Ordonez, Markus Pelger, Greg Zanotti
- **Year：** 2021（arXiv v1）/ 2022（arXiv v2）
- **Title：** *Deep Learning Statistical Arbitrage*
- **Venue：** working paper / arXiv / SSRN
- **DOI：** <https://doi.org/10.48550/arXiv.2106.04028>
- **Readable URL：** <https://arxiv.org/abs/2106.04028>
- **SSRN URL：** <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3862004>
- **Project summary URL：** <https://nber-nsf2021.rice.edu/deep-learning-statistical-arbitrage/>

### 官方仓库
- **Repo owner：** `gregzanotti`
- **Repo：** `dlsa-public`
- **Repo URL：** <https://github.com/gregzanotti/dlsa-public>
- **GitHub API metadata：** <https://api.github.com/repos/gregzanotti/dlsa-public>
- **README：** <https://raw.githubusercontent.com/gregzanotti/dlsa-public/main/README.md>
- **CNN config：** <https://raw.githubusercontent.com/gregzanotti/dlsa-public/main/configs/cnntransformer-full.yaml>
- **Preprocess：** <https://raw.githubusercontent.com/gregzanotti/dlsa-public/main/preprocess.py>
- **Model：** <https://raw.githubusercontent.com/gregzanotti/dlsa-public/main/models/CNNTransformer.py>
- **Train/Test：** <https://raw.githubusercontent.com/gregzanotti/dlsa-public/main/train_test.py>
- **Runner：** <https://raw.githubusercontent.com/gregzanotti/dlsa-public/main/run_train_test.py>

## 5) 这篇东西真正可迁移的策略骨架
### 5.1 第一步不是找形态，而是先做 residual portfolio
论文摘要把框架写得很直白：
1. 先从**conditional latent asset pricing factors** 里构造 residual portfolios；
2. 再从这些 residual portfolios 的时间序列里提信号；
3. 最后形成满足约束的最优 trading policy。

翻成人话：
**先把“大家一起涨跌”的那部分去掉，再去赌“本不该这么偏”的那部分。**

这点很适合 crypto desk，因为我们的共同因子天然更多：
- 市场总 beta（BTC / ETH 风险偏好）
- sector beta（L1 / meme / AI / DeFi）
- funding / basis crowding
- OI / volume shock
- venue-specific microstructure 噪音

如果这些不先剥掉，很多看起来像 alpha 的东西，其实只是共振 beta。

### 5.2 第二步只看 residual 时间序列，不直接看原始价格
repo 的 `preprocess.py` 里，默认预处理是：
- 对 residual returns 做 `cumsum` 窗口；
- `lookback = 30`；
- 只保留窗口内无缺失的序列；
- 然后把这段 residual cumulative-return path 交给模型。

这说明它学的不是“下一根 K 线涨跌”，而是：

> **一段 residual path 长什么样，后面更像 continuation、mean reversion，还是该少做。**

对短周期 desk，这个思路比“直接喂一堆 OHLCV 因子”更干净，因为：
- 先 residualize，降低共振噪音；
- 再在 residual 路径形状上做分类/回归/权重分配。

### 5.3 第三步不是二元开仓，而是连续权重分配
`models/CNNTransformer.py` 的输出不是“买/卖/平”三分类，而是**连续权重**。
随后 `train_test.py` 会：
- 把权重做 L1 归一化；
- 直接乘到 residual return 上；
- 再扣交易成本与 short hold cost；
- 以 Sharpe / mean-var / sqrtMeanSharpe 作为目标函数训练。

这很关键。因为它告诉我们：

**这不是“发现信号后再手写 sizing”的框架，而是把 sizing 本身并入了 alpha 学习。**

也就是说，base alpha 是 residual mispricing；
但最后落地成交易时，它已经内生变成：
- 哪些 residual 该做；
- 做多大；
- 换仓多频；
- short exposure 要不要压低。

### 5.4 成本不是事后补丁，而是训练目标的一部分
`train_test.py` 里直接把：
- `trans_cost`
- `hold_cost`
- `turnover`
- `short_proportion`

放进回报计算和日志输出里。

这对 crypto 非常重要，因为我们 desk 现在最怕的不是“没有信号”，而是：
**信号看起来都对，但一上真实费率、滑点、funding，就被吃没了。**

DLSA 至少在框架上做对了两件事：
1. **训练时就罚换手**；
2. **允许对 short 持仓加 hold cost**。

把它迁到 perp，很自然就能把 `hold_cost` 改写成：
- funding carry cost
- borrow / inventory cost
- venue-specific short-side friction

## 6) repo 里最值得记住的 6 个硬数据点
1. **官方 repo 星标：** 当前 GitHub metadata 显示约 **258 stars**，不是随手扔的玩具脚本。
2. **默认 signal lookback：** `30`。
3. **默认 rolling training window：** `1000` 个交易日。
4. **默认 retrain frequency：** `125`。
5. **默认 factor family：** 同时跑 `IPCA / PCA / FamaFrench`，各自先测 `5 factors`。
6. **默认目标：** `objective = sharpe`，且支持显式 `trans_cost` / `hold_cost`。

再补两条对 desk 更有用的：
- 模型族不是只有一个：repo 同时提供 `RawFFN / FourierFFN / OUFFN / CNNTransformer`，说明它不是“非 Transformer 不可”。
- `use_residual_weights = True` 时，仓位和换手是在**底层资产空间**里算，而不是只在抽象 residual 空间自嗨。

## 7) 给 crypto 1m / 3m / 5m / 15m 的最小可复现实验
### 7.1 先做最小 honest 版，不要直接抄美股 daily
这篇原始样本是 daily U.S. equities，而且 repo 也明确说**原始资产收益与特征数据因授权问题不能放出**。

所以对我们最现实的读法不是“1:1 复刻论文结果”，而是：

> **复刻这套 raw alpha 生成框架到公开 crypto panel 数据上。**

### 7.2 数据源（公开可得）
先用公开 perpetual / spot 数据就够：
- **Binance / Bybit / Hyperliquid public API**
- `OHLCV`
- `funding history`
- `open interest`
- `basis / mark-vs-index premium`
- `volume / trades / taker flow proxy`

更新频率：
- 可下采样到 `1m / 3m / 5m / 15m`

### 7.3 先定义 crypto 版共同因子
先别追求 fancy IPCA；先做一版简单但 honest 的：
- 市场因子：BTC、ETH perp return
- sector 因子：按 `L1 / meme / AI / DeFi / CEX / infra` 分桶
- 拥挤度因子：funding、OI change、basis
- 微观流动性因子：volume shock、spread proxy

然后对每个币的 bar return 做 rolling regression / PCA residualization，得到：
- `residual_return_{i,t}`
- 或 `residual_portfolio_t`

### 7.4 信号层怎么先做
先不要上完整论文重度训练，先做 3 层 ablation：

#### A. 最简单 baseline
- residual z-score cross-section
- long bottom decile / short top decile
- 持有 `1 / 3 / 6 / 12` bars

#### B. path-based MLP / OU baseline
- 输入：过去 `96 / 192 / 288` bars residual cumsum path
- 输出：连续权重
- 目标：after-cost Sharpe

#### C. CNNTransformer（DLSA 主体）
- 输入同上
- 卷积抓局部 pattern
- Transformer 抓长一点的残差结构关系
- 输出连续权重后做 L1 归一化

### 7.5 先测哪些周期
我的建议顺序：
1. **15m**：最先做，噪音更低，训练和成本也更诚实；
2. **5m**：确认模型是否真的比简单 residual z-score 有增益；
3. **3m / 1m**：只在 liquid majors 上开，因为 turnover 会陡增。

### 7.6 最小实验的具体卡片
- **资产池：** 20~40 个流动性足够的 perp
- **bar：** `15m` 起步
- **residual lookback：** `20d / 40d / 60d` rolling
- **signal lookback：** `96 / 192 / 288` bars
- **训练目标：** after-cost Sharpe
- **成本：**
  - taker-only：`6 / 8 / 10 bps round-trip`
  - maker-taker hybrid：`3 / 5 / 7 bps`
  - `hold_cost` 里加入 funding
- **约束：**
  - gross leverage cap
  - single-name weight cap
  - turnover cap
  - funding shock veto

## 8) 它服务于哪类 raw alpha
这篇不是只能服务一类策略。它至少能服务这几类：
1. **cross-sectional residual reversal**
2. **market-neutral residual momentum**
3. **same-sector relative-value spread allocation**
4. **basis / funding / OI 因子剥离后的纯价差信号**

所以它最值钱的地方不是某个 headline signal，而是：

> **把多条 stat-arb / relative-value alpha 放进同一个可训练、可扣成本、可做连续仓位的容器里。**

## 9) 风险与局限
1. **原论文原样本不能 1:1 精确复刻。** repo 明说原始美股特征数据受授权限制。
2. **daily equity → intraday crypto 有域迁移风险。** 不能因为论文有效，就默认 5m perp 也有效。
3. **latent factor / residualization 这层本身会过拟合。** 如果 universe 太小、因子太多，残差会变成噪音放大器。
4. **最怕 turnover 爆炸。** 这种 panel 模型一旦输出太敏感，很容易“聪明地交手续费”。
5. **别把 Transformer 当 alpha 本体。** 真正的 alpha 还是 residual mispricing；模型只是更灵活的 mapping。

## 10) 我对 desk 的结论
如果今天要再加 1 篇真正能扩充 raw alpha 素材池的 intake，我愿意把这篇记成：

> **`latent-factor residual portfolio × cost-aware continuous allocation`**

它的价值不在“再多一个单点信号”，而在：
- 把 raw alpha 从单条规则升级成 panel 引擎；
- 直接兼容 `cross-sectional / relative-value / stat-arb`；
- 天然能把成本、换手、short carry 纳入同一个训练目标；
- 对 `1m/3m/5m/15m` 都能做最小实验，只是优先级不同。

## 11) 下一步怎么测
1. **先拉 20~40 个 liquid perp 的 `15m` 公共数据**：OHLCV + funding + OI + basis。
2. **先做一版简单 residualization**：市场 beta + sector bucket + funding/OI 因子，得到 residual return panel。
3. **跑 3 个模型层级**：
   - residual z-score top/bottom baseline
   - OUFFN / RawFFN
   - CNNTransformer
4. **统一成本口径**：至少测 `5 / 10 / 15 bps round-trip + funding hold cost`。
5. **先看 4 个指标**：
   - after-cost Sharpe
   - pnl / turnover
   - single-name concentration
   - funding / basis 冲击日的回撤
6. **只有当 panel residual 模型稳定优于简单 baseline**，才值得把它下沉到 `5m`，更不用急着上 `1m`。

## 12) 这轮最值得带走的一句话
**别再把 stat-arb 只理解成“挑一对、算 z-score、等回归”。DLSA 真正给 desk 的东西，是一条更通用的 raw alpha 路：先把共同因子剥掉，再在 residual panel 上做 after-cost 连续分配。**
