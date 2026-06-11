# 别把 funding carry 继续只写成“阈值够高就上”：这篇 2026 Zenodo + GitHub 更该先测的是「basis relaxation × regime-sized funding carry」这条完整 raw alpha
- 时间：2026-04-06 04:58 UTC
- 类型：2026 Zenodo 预印本 + 同名 GitHub repo source audit（`README.md` + `strategy/backtest_v2.py` + `strategy/signals.py` + `strategy/regime.py`）
- 主题类型：raw alpha
- 基础 alpha：**delta-neutral carry / basis mean reversion**；当 perp 相对 spot 出现可交易的 `funding + basis` 偏离时，做 `long spot / short perp`（或反向 `short spot / long perp`），靠 **已锁定的 funding 收益 + basis 向锚回归** 赚钱；文中的 thermodynamic 变量主要服务于 **什么时候敢放大、什么时候必须缩小**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/delta-neutral/stat-arb/basis-mean-reversion/relaxation-ratio/entropy-rate/je-health/regime-sizing/binance/spot-perp/8h-anchor/1m/5m/15m/repo/paper/public-data/cost/risk
- 证据类型：预印本摘要 + repo README + 关键策略源码

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = `funding carry + basis convergence`，不是 Jarzynski 公式本身。**
> 说人话：真正赚钱的还是 **perp 太贵/太便宜时的 delta-neutral carry**；“physics” 这层更像一个可复现的 **regime / sizing engine**，决定这笔 carry 值不值得放大做。

## 1. 这次看了什么，为什么这轮值得写它
这轮主看 3 份材料：

1. **Ethan Khoo Chuen Lee (2026). _Non-Equilibrium Thermodynamics of Cryptocurrency Perpetual Futures: Jarzynski Equality, Regime Classification, and Physics-Informed Trading_. Zenodo preprint.**
   - Venue：Zenodo
   - DOI：`10.5281/zenodo.19046564`
   - Readable URL：`https://doi.org/10.5281/zenodo.19046564`
   - 关键信息：作者把 perp funding 机制写成一个 **basis 被外力驱动、但又会回到锚点的过程**，并在 `2020-01 ~ 2026-03` 的 Binance 数据上做了 **19,697 个 funding cycles / 156,896 个 hourly basis observations** 的实证。
2. **Ethan Khoo Chuen Lee (2026). _fluctuation-theorem-perps_. GitHub repository.**
   - Repo URL：`https://github.com/ElvianElvy/fluctuation-theorem-perps`
   - Readable URL：`https://github.com/ElvianElvy/fluctuation-theorem-perps`
   - 关键信息：repo 不只是论文附件，里面直接给了：
     - `signals.py`：4 个 causal signals
     - `regime.py`：3 态 regime classifier
     - `backtest_v2.py`：带 **signed funding + basis MTM + fees** 的 realistic PnL
3. **GitHub README（同 repo）**
   - Raw README：`https://raw.githubusercontent.com/ElvianElvy/fluctuation-theorem-perps/main/README.md`
   - 关键信息：README 把最重要的策略信息写得很实：
     - fees 按 **16 bps round-trip**
     - 走 **360-cycle train / 90-cycle test** 的 walk-forward
     - regime sizing：`EQUILIBRIUM=100%`、`WARM=60%`、`NESS=25%`
     - V2 不是只收 funding，而是显式计入 **basis 变化带来的 mark-to-market**

这轮值得写它，不是因为“物理学很酷”，而是因为它刚好补到我们现在最缺的一块：

- 过去几轮已经把 `funding tail carry`、`funding persistence`、`spot-perp / cross-venue carry` 这些 **base alpha 壳** 补了不少；
- 但 carry 家族真正最难、也最容易在实盘里把纸面 alpha 吃没的，是：
  **什么时候该满仓收、什么时候该缩仓、什么时候其实在拿 basis 风险而不是拿 carry。**

这篇材料的价值就在于：

> **它没有换掉 carry 这个 base alpha；它是在 carry 之上补了一个能直接复现的 regime-sized shell。**

这对 desk 来说，比再看一篇“funding 高就空”的新壳更有边际价值。

## 2. 一句话核心结论 + 它是怎么证明的
### 一句话核心结论
**别把 delta-neutral funding carry 做成固定阈值 + 固定仓位。更值得先测的是：用 `basis relaxation ratio + temperature z-score + entropy rate + JE health` 这 4 个 causal 信号，把相同的 carry 壳分成 `可放大 / 正常 / 只保留最小 exposure` 三种状态。**

### 一句话它怎么证明
- 论文 / README 报告：在 `BTC / ETH / SOL` 上，作者用 `6.2 years` 数据构造了 4 个 physics-derived signals；
- 然后不是拿来预测方向，而是把它们塞进 **3-state regime classifier**，决定 position multiplier；
- 最后用 realistic PnL（signed funding + basis change - fees）回测，报告：
  - **BTC：V2 Sharpe 5.89 vs naive 4.73**
  - **ETH：V2 Sharpe 5.07 vs naive 4.53**
  - **SOL：V2 Sharpe 0.73 vs naive -0.25**
- 同时 README 还特别提醒：高 Sharpe 主要是因为 **一年有 1095 个 8h settlements 的年化放大效应**，绝对收益只是 **约 2%~3% annualized**，这反而让结果更可信。

## 3. 这篇东西真正该怎么读：别把“physics”误读成 alpha 本体
### 3.1 alpha 本体仍然是 carry / basis convergence
从 `backtest_v2.py` 可以直接读出，作者真正交易的不是“热力学因子方向预测”，而是一个很朴素的 delta-neutral 账本：

- 对 **short basis**（`long spot + short perp`）：
  - `funding_pnl = notional × F`
  - `basis_pnl = -notional × Δbasis/100`
- 对 **long basis**（`short spot + long perp`）：
  - funding 收益符号相反
  - basis widening 才赚钱

也就是说，这里最重要的仍是：

1. 你拿没拿到 funding；
2. basis 是往中间回，还是继续扩；
3. 扣完 fee/slippage 后还剩多少。

所以这篇 digest 必须被归成 **raw alpha**，不是单纯 filter：
- **raw alpha = carry + basis 回归**；
- **filter / regime / overlay = 4 个 thermodynamic signals 决定仓位大小和是否降档。**

### 3.2 这正好适合我们 desk 的读法：不是替换旧 carry，而是升级旧 carry
对当前 desk 来说，最自然的读法不是“再引入一套高深学术符号”，而是：

- 保留我们已经熟悉的 `funding / basis / spread / OI / liquidity` 世界；
- 把这篇 repo 提供的 4 个信号，当成一组 **比简单阈值更有结构的 state variables**；
- 用它们去升级已有的 carry 壳，而不是另起炉灶。

这就解释了它为什么比继续补一个同质化 funding headline 更值得：

> **它不是新讲一个 carry 故事，而是给 carry 家族补“position governance”这块缺口。**

## 4. repo 里最值得抄的 4 个信号，到底在说什么
`strategy/signals.py` 里把 4 个信号写得很清楚，而且都可以 causal 计算。

### 4.1 Relaxation Ratio：basis 回归速度，能不能赶在下一次 funding 前修复
定义本质上是：

`r = τ_relax / τ_funding`

其中：
- `τ_relax = 1 / κ`
- `τ_funding` 对 Binance perp 默认就是 `8h`

repo 的解释很直白：
- `r < 1`：basis 在一次 funding 周期内就能大体回归，适合做 carry；
- `r > 1`：basis 过慢，说明你更像是在扛一笔 persistent dislocation。

README 给出的关键数字：
- **BTC：τ_relax ≈ 7.6h，ratio ≈ 0.96**
- **ETH：τ_relax ≈ 7.1h，ratio ≈ 0.89**
- **SOL：τ_relax ≈ 12.3h，ratio ≈ 1.53**

这组数字对 desk 的翻译几乎可以直接做规则：
- **BTC/ETH 更像“收 carry + 等 basis 回”**；
- **SOL 更像“有时 funding 在付你，但 basis 风险没回完”，所以需要明显降仓。**

### 4.2 Temperature Z-score：不是预测方向，而是量市场现在冷不冷、稳不稳
repo 把它定义成当前 `β` 相对历史分布的 z-score：
- 正值：更冷、更稳定、basis 波动更可控；
- 负值：更热、更不稳定、basis 更容易失控。

翻成人话：
- 不是问“接下来涨还是跌”；
- 而是问“现在这笔 carry 的 path risk 大不大”。

这正好是 carry 最需要、但很多 funding 策略根本没显式建模的一层。

### 4.3 Entropy Rate：funding 机制到底是在修复错价，还是已经失灵
`entropy_rate > 0`：更像 dissipative market，funding 机制在工作；  
`entropy_rate < 0`：更像 non-equilibrium steady state，说明市场并没有顺着“贵的回落、便宜的回升”那套逻辑走。

对 desk 而言，这个量的最直接价值不是“解释市场”，而是：

> **当 entropy rate 太差时，不要继续把高 funding 误读成更好的 carry。**

### 4.4 JE Health：不是拿来做学术检验，而是当“这套物理近似还靠谱吗”的健康度表
repo 用 `|E[e^{-βσ}] - 1|` 去看当前市场离“thermodynamic-like”有多远。

对交易最实用的读法是：
- 越接近 0，说明当前这套 `funding 驱动 basis 回锚` 的叙事更成立；
- 偏离越大，说明你不该再把这笔 carry 当成“稳定的机械性收益”。

这很像一个 **model trust score**。

## 5. repo 最有价值的，不是信号本身，而是它们被怎样塞进完整策略
### 5.1 先做 alpha，再做 regime sizing —— 次序是对的
`backtest_v2.py` 里最值得肯定的一点，是作者没有把信号做成“预测涨跌再决定买卖”的 ML 花活，而是：

1. 默认承认 **carry 这条 alpha 本身长期存在**；
2. 然后让 regime 只负责 **调 exposure**；
3. 最后用 realistic PnL 去看，这种调 exposure 是否真的比 naive carry 更好。

这比很多“先训个模型，再说它会赚钱”的 repo 诚实很多。

### 5.2 3-state classifier 很 desk-friendly
`strategy/regime.py` 里：
- `EQUILIBRIUM = 100% exposure`
- `WARM = 60% exposure`
- `NESS = 25% exposure`

而且阈值不是写死的绝对值，而是：
- `entropy` 用 rolling percentile；
- `JE health` 用 rolling percentile；
- `relaxation ratio` 用危险/安全阈值；
- `temperature z-score` 用简单状态判别。

这很适合我们 desk，因为它天生就支持：
- 做多标的时横向统一；
- 不需要精确校准每个币都一样的硬阈值；
- 可以很快落地到 `BTC/ETH/SOL majors first` 的第一版实验。

### 5.3 V2 PnL 建模比很多 funding repo 真实
README 和代码都明确写了 3 个关键修正：

1. **signed funding**：不是永远收 funding，方向错了也会付；
2. **basis risk MTM**：持仓期间 basis 继续恶化，账面会亏；
3. **fees/slippage**：按 **16 bps round-trip** 扣成本。

这几个点非常关键。因为很多 funding 策略一上来就会犯 3 个错：
- 只记 funding，不记 basis path risk；
- 只记结算，不记持仓过程 drawdown；
- 低估调仓成本。

这篇材料在这三点上都比一般 repo 更实盘友好。

## 6. 对 1m / 3m / 5m / 15m desk，该怎么落地，不要硬装成逐根主信号
这里必须说清楚：

- 这条 alpha 的 **经济结算时钟** 仍然是 `funding cycle`；
- 它不是原教旨的“每根 1m bar 预测未来 5m 收益”；
- 但它完全可以被映射成 **short-cycle 执行 / sizing / hold governance**。

最合理的映射方式是：

### 6.1 8h 是 payoff anchor，1m/5m/15m 是 state / execution clock
- `1m`：刷新 mark-index basis、spot-perp basis、book spread、depth、OI proxy；
- `5m`：主执行频率，决定是否建立 / 续持 / 缩仓 carry；
- `15m`：低 churn 版本，用于更稳的 desk 壳；
- `8h funding boundary`：真正兑现 carry，并评估上一 funding 周期的 basis 修复质量。

### 6.2 不要伪装成“逐根主信号”，要诚实写成“carry alpha + short-cycle execution shell”
这点很重要。我们不该把它硬说成“5m raw directional alpha”，而应该准确地写：

> **raw alpha 仍是 carry / basis convergence；`1m/5m/15m` 负责的是更快的 admission、hold、de-risk 和 execution。**

这并不降级它，反而让策略定义更清楚。

## 7. 适合当前 desk 的最小可复现实验
这是我认为最该先做的一版，不求完美，但求一周内能出结果。

### 7.1 交易对象
优先：`BTCUSDT / ETHUSDT / SOLUSDT` 这 3 个 Binance perp 对应 spot。

原因：
- 原文就是这 3 个；
- 都有公开 funding / mark / index / spot 数据；
- 也方便跟 repo 原结果做弱对照。

### 7.2 数据源与公开性
**公开可得，且不需要 key 的最小口径：**
- Binance Futures funding history
- Binance Futures mark/index price
- Binance Spot klines 或 best bid/ask proxy

如果第一版只求最小复现，甚至可以先：
- 用 `mark - index` 当 basis proxy；
- spot 腿先不做逐笔成交仿真，而用 conservative fee / slippage bucket 吸收。

### 7.3 第一版信号
保留 repo 的结构，但先简化成 desk 版规则：

1. `relaxation_ratio`
2. `temperature_zscore`
3. `entropy_rate`
4. `je_health`
5. 再额外拼我们已有的：
   - `spread percentile`
   - `depth percentile`
   - `OI change`
   - `funding sign flip risk`

### 7.4 第一版 entry / exit / sizing
#### Entry
只做最容易的一侧：
- `funding > 0`
- `basis > 0`
- `relaxation_ratio < 1.05`
- `temperature_zscore > -0.5`
- `entropy_rate` 高于过去 `40% percentile`
- `je_health` 不在过去 `90%` 最坏分位
- `spread/depth` 过门槛

然后开：
- `long spot / short perp`

#### Exit
任一满足就走：
1. 到下一次 funding 结算后强平估值；
2. `basis` 回到 rolling median 附近；
3. `funding` sign flip；
4. regime 从 `EQUILIBRIUM/WARM` 跳到 `NESS`；
5. 最长只拿 `1~2 funding cycles`。

#### Sizing
沿用 repo 的思路先做最朴素版：
- `EQUILIBRIUM = 1.0x`
- `WARM = 0.6x`
- `NESS = 0.25x`

### 7.5 成本设定
第一版直接做 3 档：
- 乐观：`8 bps round-trip`
- 中性：`16 bps round-trip`（贴近 repo）
- 保守：`25 bps round-trip`

同时报告：
- only funding PnL
- funding + basis PnL
- net after fees

这样能一眼看出，这条策略到底是在赚 funding，还是其实在吃 basis 偶然回撤。

## 8. 我最想先验证的，不是“物理对不对”，而是 3 个交易问题
### 8.1 relaxation ratio 是否真的决定 carry 的可持有性
这是最值得先打的 first test：
- 把样本按 `relaxation_ratio` 分桶；
- 比较每桶的：
  - next funding-cycle net PnL
  - max adverse basis excursion
  - hit rate

如果这一步成立，这篇 digest 就值回票价。

### 8.2 regime sizing 是否比“extreme funding only”更稳
对照组至少要有：
1. `Naive always-on short basis`
2. `Extreme funding threshold only`
3. `Physics regime-sized carry`

重点不是只看 Sharpe，应该优先看：
- worst cycle drawdown
- basis excursion tail
- turnover
- fee-to-gross-PnL ratio

### 8.3 SOL 那种“funding 在付，但 market 仍在非平衡态”是否能在更多 alt 上复现
README 里最有意思的结果不是 BTC/ETH，而是：
- **SOL naive funding arb 是负的**；
- 但 regime-sized 之后转正。

这很像 alt-perp 市场最真实的故事：
- carry 看起来肥；
- 但实际是 persistent dislocation + thin-liquidity path risk；
- 所以问题不在“有没有 alpha”，而在“仓位该不该降得足够狠”。

如果这点在别的中高流动 alt 上也成立，那这篇材料对 desk 的价值会很高。

## 9. 一句话总结
**这篇 2026 Zenodo + GitHub 材料最该带给我们的，不是“市场像热力学系统”这句漂亮话，而是一个更实用的结论：`funding carry` 这条 raw alpha 可以继续做，但不要再用固定阈值 + 固定仓位去做；更该先测的是「basis 回归速度 × regime-sized exposure」这层完整策略升级。**

## 10. 下一步怎么测
### 最小实验（优先级最高）
1. 拉 `BTC/ETH/SOL` 的 Binance：
   - funding history
   - mark/index
   - spot or spot proxy
2. 先复现 **只做正 funding 一侧** 的 `long spot / short perp`。
3. 用 `8h` funding cycle 做 payoff anchor，`5m` 做执行频率，`1m` 做状态更新。
4. 先只测 3 套策略：
   - naive always-on
   - extreme-funding-only
   - regime-sized carry
5. 报 6 个核心指标：
   - net annual return
   - Sharpe
   - max drawdown
   - fee / gross ratio
   - next-cycle hit rate
   - max adverse basis excursion

### 第二步实验（如果第一步成立）
- 把 repo 的 4 个 signals 做 **ablation**：
  - 只用 `relaxation_ratio`
  - `relaxation_ratio + entropy_rate`
  - 4 signals 全开
- 看真正值钱的是哪一个，不要默认全都要。

### 第三步实验（更贴近 desk）
- 把 `5m` 与 `15m` 两个 child execution 版本并跑：
  - `5m` 看更高响应、更高 churn
  - `15m` 看更低噪音、更低 fees
- 再加我们已有的 `spread/depth/OI/liquidation` veto，检查是不是能进一步压掉 alt-perp 的 path risk。

## Sources
1. Ethan Khoo Chuen Lee (2026), _Non-Equilibrium Thermodynamics of Cryptocurrency Perpetual Futures: Jarzynski Equality, Regime Classification, and Physics-Informed Trading_, Zenodo preprint, DOI: `10.5281/zenodo.19046564`  
   Readable URL: `https://doi.org/10.5281/zenodo.19046564`
2. Ethan Khoo Chuen Lee (2026), _fluctuation-theorem-perps_, GitHub repository  
   Repo URL: `https://github.com/ElvianElvy/fluctuation-theorem-perps`
3. GitHub raw files used in this digest:  
   - `https://raw.githubusercontent.com/ElvianElvy/fluctuation-theorem-perps/main/README.md`  
   - `https://raw.githubusercontent.com/ElvianElvy/fluctuation-theorem-perps/main/strategy/backtest_v2.py`  
   - `https://raw.githubusercontent.com/ElvianElvy/fluctuation-theorem-perps/main/strategy/signals.py`  
   - `https://raw.githubusercontent.com/ElvianElvy/fluctuation-theorem-perps/main/strategy/regime.py`
