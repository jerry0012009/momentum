# 别把 crypto pairs 继续卷成“单点最优参数”：这份 2026 Bybit `5m` 新 repo 更该先偷的是「plateau-first 选参 + in-trade ADF kill-switch」，ETH/LINK proxy 快检显示 10 bps 还能活、20 bps 基本即死

- 主题类型：raw alpha
- 基础 alpha：beta-hedged cointegration spread mean reversion（pairs / stat-arb / relative value）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但对成本极敏感
- 时间：2026-03-31 18:46 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/parameter-plateau/adf-killswitch/cost-cliff/eth/link/binance/bybit/5m/15m/repo/public-data
- 证据类型：2026 GitHub 新仓库 source audit（`README.md` + `src/shortlist_pairs.py` + `src/backtest.py`）+ Binance USDⓈ-M Perpetual 公共 `5m` 本地 proxy quick check

## 1. 这次看了什么

这次主材料不是一篇论文，而是一份 **2026 新 repo：`velychkoanton-stack/cointegration-pairs`**。它表面上是在做 Bybit `5m` pairs 扫描 / 回测，但真正对 desk 有价值的，不是“又一个 cointegration z-score 回归”，而是两件更实用的事：

1. **不要拿单点最优参数做选对**，而是看参数面上有没有 **plateau（相邻参数都活）**；
2. **不要假设配对关系会一直活着**，而是把 **in-trade ADF 复检 + half-life 超时强平** 写进退出逻辑。

repo 自己给出的骨架很完整：有 pair shortlist、rolling window、开仓阈值倍数、TP/SL、交易成本、以及持仓中的 cointegration 失效检查。对我们的意义是：

- **base alpha 仍然是 raw alpha**：spread 偏离后回归；
- 但真正决定能不能进素材池的，已经不是“这个 pair 某个参数点回测收益最高”，而是：
  - 参数是不是有 **稳态 pocket**；
  - 成本上去以后还剩不剩边；
  - 配对关系失效时有没有 **honest kill-switch**。

## 2. 先回答：这篇东西的 base alpha 是什么？

**base alpha = 同一风险簇里，两条高相关 / 近 cointegrated 价格序列的 beta-hedged spread 偏离后，向均值回归。**

也就是标准的 `pairs / stat-arb / relative value / mean reversion`，不是 filter，也不是 overlay。

repo 的可取之处不在于发明了新 alpha，而在于把这个 raw alpha 从“拍脑袋 z-score backtest”往 **可落地策略骨架** 推近了一步：

- 有 **pair selection funnel**；
- 有 **参数面而不是单点 winner**；
- 有 **in-trade cointegration 失效退出**；
- 有 **成本显式入模**。

## 3. repo 里真正值得 desk 记住的东西

### 3.1 Pair shortlist 不是只看 p-value

`src/shortlist_pairs.py` 里，repo 对候选对做的是一组联合过滤，而不是只看 Engle-Granger / ADF：

- `ADF_MAX = -2.9`
- `P_VALUE_MAX = 0.05`
- `HURST_MAX = 0.45`
- `HALFLIFE_BARS ∈ [10, 300]`
- `SKEW ∈ [0, 1]`
- `KURT ∈ [0, 5]`

这点很对。对短周期 desk 来说，**stationary 不是充分条件**：

- Hurst / half-life 决定你是不是在等一个太慢的均值回复；
- skew / kurt 决定你拿到的是不是“平时像 MR、出事像单边趋势”的假 spread。

### 3.2 真正有价值的是 plateau-first，不是 best-cell-first

README 的“Best pair shortlist”部分，不是直接拿单组最优参数，而是保留：

- `good_cases >= 100`
- `plateau_n >= 5`
- `plateau_share >= 0.10`

这是这份 repo 最值得 desk 偷的部分。

因为 pairs 最大的问题，往往不是“完全没边”，而是：

- 最优点看起来很美；
- 但参数一动就死；
- live 一上 maker/taker、滑点、funding，就直接掉到 0 以下。

**plateau-share** 比“best Sharpe / best balance”更诚实，因为它在回答：

> 这个 alpha 是真的存在，还是只是某个参数点碰巧拟合了样本路径？

### 3.3 持仓中的 ADF 复检比“等 z-score 回零”更诚实

`src/backtest.py` 里的退出逻辑不是只有 TP / SL / mean reversion，还加了：

- `ADF_CHECK_EVERY_BARS = 12`
- `ADF_PERSIST_K = 3`
- `bars_in_trade >= rolling_window` 且连续复检失败时，触发 `HL_COINTEGRATION_LOST` 退出

这比很多 pairs repo 诚实得多。很多 pairs 回测默认：

- 开仓时关系成立；
- 之后就假设关系一直成立；
- 直到 spread 回归才退出。

现实里更常见的是：

- 你等的不是均值回复，
- 而是 **结构断裂后的错误锚定**。

所以这份 repo 对 desk 的真正启发是：

**pair alpha 可以继续做，但必须把“pair 已经不再是 pair”这件事写进状态机。**

## 4. 本地最小 proxy 快检：用 Binance USDⓈ-M `5m` ETH/LINK 验证“plateau + cost cliff”

为了不直接照抄 repo 的 Bybit 结果，我做了一个更小、更快的 public-data proxy：

- 数据源：Binance USDⓈ-M Perpetual `5m` klines（公开 REST）
- 标的：`ETHUSDT` 与 `LINKUSDT`
- 样本：最近 `9000` 根 `5m` bars（约 31 天）
- 切法：前 `4500` 根训练 / 后 `4500` 根测试
- beta：训练段 log-price 静态回归 proxy，估得 `β ≈ 1.149`
- 训练段 spread AR(1) proxy：`phi ≈ 0.9914`
- 对应 half-life：约 `80.3` 根 `5m` bar，约 `6.7h`

### 4.1 策略骨架（proxy）

我这里用的是最小可复现版本，而不是完全复刻 repo：

- spread = `log(P_ETH) - β * log(P_LINK)`
- `roll ∈ {72, 96, 120, 144}`
- `entry z ∈ {1.5, 1.75, 2.0, 2.25, 2.5}`
- `stop z ∈ {3.0, 3.5, 4.0, 4.5, 5.0}`
- exit：z-score 回到 0，或 stop hit
- 成本：对整笔 spread package 做简化 round-trip proxy cost（不是逐腿真实成交回放）

### 4.2 结果：先看 plateau，再看成本崖

#### 无成本（纯 gross）

- **100 / 100** 组参数都为正
- 最佳参数：`roll=72, entry=1.75, stop=5.0`
- 测试段 `final_eq ≈ 1.1281`，即约 **+12.81%**
- trades：`83`
- max drawdown：约 **-2.19%**

这说明一个事实：

**这个 pair 的 raw alpha 在测试段不是只有单个 best cell 活，而是整块参数面都活。**

#### 10 bps spread-package round-trip 成本 proxy（每次开/平各 5 bps）

- **67 / 100** 组参数仍为正
- 最佳参数仍在 `roll=72, entry≈1.75, stop≈4.0~5.0` 一带
- 最佳 `final_eq ≈ 1.0388`，即约 **+3.88%**
- 正收益参数的中位数约 **+1.63%**

也就是说，**plateau 在低成本下没有立刻蒸发**，而是从“整块都活”缩成“仍有一整片 pocket 活着”。

#### 20 bps spread-package round-trip 成本 proxy（每次开/平各 10 bps）

- **0 / 100** 组参数为正
- 最好的一格也只有 `final_eq ≈ 0.9883`

这就非常关键了：

> **pairs raw alpha 不是没有，但它的“可交易性”基本被成本壳一刀切开。**

这也是为什么这份 repo 里 **plateau-first + transaction cost** 组合非常值钱：

- 没 plateau，就容易拿到一个回测偶然点；
- 不看 cost，就会把 gross alpha 误当 live alpha。

### 4.3 这组 quick check 对 desk 的真实含义

这不是在证明 “ETH/LINK 一定值得实盘”，而是在证明三件更重要的事：

1. **cointegration MR 在 `5m` 上仍可能有 raw alpha**；
2. **alpha 是否存在，和 alpha 是否能穿过成本壳，是两回事**；
3. **参数面稳定性** 比单点最好看更重要。

## 5. 这条思路怎么 desk 化

### 5.1 最自然的时间尺度：`5m` 主做，`15m` 做慢门控

从这次 proxy half-life（约 `6.7h`）看，最自然的读法是：

- **信号生成层**：`5m`
- **状态 / 结构层**：`15m`

也就是：

- `5m` 负责抓 spread 偏离的 entry；
- `15m` 负责决定这对关系当前是否值得开仓，避免在结构断裂期机械抄底 / 摸顶。

### 5.2 更像“配对状态机”，不是“单一 z-score 一招鲜”

如果要把这条策略变成完整 desk 组件，我会按下面的顺序写：

1. **Universe / clustering**
   - 只在同 risk cluster 里做：L1、beta、高相关、相同叙事币种优先
   - 每日 / 每周重做 shortlist

2. **Relationship filter**
   - ADF / p-value / Hurst / half-life / skew / kurt 联合过滤
   - 必须加 **plateau-share**，不要只看 best row

3. **Entry**
   - `5m` spread z-score 偏离
   - 建议先从 `entry 1.75~2.25σ` 开始，而不是太激进的 `1.0~1.25σ`

4. **Exit**
   - mean reversion exit
   - z-stop / PnL-stop
   - **half-life timeout + in-trade ADF fail kill-switch**

5. **Sizing**
   - beta-neutral notional
   - 再叠加 spread-vol target
   - 单 pair 风险预算上限，避免某一个关系断裂拖死整本 book

6. **Cost / execution**
   - 如果做不到低于约 `10 bps` 的 spread-package round-trip proxy，edge 很可能直接蒸发
   - 所以更现实的方向是：
     - 至少一腿 maker
     - 只做高流动 pair
     - 做 participation cap
     - 做 funding / fee tier / rebate 分层

## 6. 这次材料的结论

### 最终判断

**值得进入研究池。**

但进入研究池的不是“又一个 plain cointegration pairs alpha”，而是这条更 desk 化的表达：

> **raw alpha = beta-hedged spread mean reversion；真正该带走的可交易化组件 = plateau-first parameter selection + in-trade ADF kill-switch + 成本生存线审计。**

### 不是主打什么

它**不是**：

- 一个可以忽略成本的稳赚 pair；
- 一个适合只看 best backtest row 的研究方向；
- 一个天然适配所有 pair / 所有 venue 的通用模板。

### 真正该带走什么

它**是**：

- 一个仍可独立复现的 raw alpha；
- 一个对 `5m/15m` desk 仍有现实意义的 pairs 壳；
- 一个非常适合做 **“alpha 是否真活着，还是只活在 best cell 里”** 的验证框架。

## 7. 下一步怎么测

### 最小实验（优先）

1. **做 30~60 对 Binance / Bybit perp 候选池**
   - 同 risk-cluster 内配对
   - 只保留流动性足够的永续合约

2. **滚动做 plateau-scan，而不是一次性 best-fit**
   - 每天 / 每周重估 shortlist
   - 输出：`good_cases / plateau_n / plateau_share`

3. **把成本拆细**
   - taker/taker
   - maker/taker
   - maker/maker（保守成交率假设）
   - funding + fee tier + participation slippage

4. **单独验证 ADF kill-switch 是否真的减尾部**
   - 对照组：只有 z-exit / TP / SL
   - 实验组：加 `half-life timeout + ADF fail`
   - 看 tail loss / max DD / trade duration 分布

### 如果只给我一周研发时间

我会先做这个：

- universe：`ETH/BNB/LINK/SOL/AVAX/ARB/OP/AAVE`
- 频率：`5m`
- pair shortlist：相关 + ADF + Hurst + half-life + plateau-share
- 回测：滚动 30d train / 10d test
- 成本：至少做 `10 / 15 / 20 bps` 三档 spread-package proxy
- 目标：
  - 找到 **成本后仍有 plateau** 的 pair
  - 不是找 **gross 最好看** 的 pair

## 8. Sources

1. **Anton Velychko, 2026, _cointegration-pairs_**, GitHub repository, Venue: GitHub, DOI: N/A  
   - Readable URL: `https://github.com/velychkoanton-stack/cointegration-pairs`
   - Repo URL: `https://github.com/velychkoanton-stack/cointegration-pairs`

2. **Robert F. Engle, Clive W. J. Granger, 1987, _Co-integration and Error Correction: Representation, Estimation, and Testing_**, *Econometrica*, DOI: `10.2307/1913236`  
   - Readable URL: `https://doi.org/10.2307/1913236`

## 9. 这篇 digest 产出物

- Markdown：`research/quant_digests/2026-03-31_1846_pairs-plateau-adf-killswitch-cost-cliff.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-31_1846_pairs-plateau-adf-killswitch-cost-cliff.html`
