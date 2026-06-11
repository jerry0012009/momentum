# 别把 NSGA-II 只当“配对优化器”：对 short-cycle desk，更该先测的是「Pareto pair admission × spread shell」这条 pairs raw alpha

- 主题类型：raw alpha
- 基础 alpha：**高协同 / 近似协整币对的 spread 均值回归**；NSGA-II 不是 alpha 本体，而是把“该交易哪些 pair、组多少 bucket”从单指标排序升级成多目标 Pareto admission。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/nsga-ii/pareto/pair-admission/bucket-selection/risk-return/multiobjective/5m/15m/3m/1m/paper/public-data/cost

> 先回答一句：这篇东西的 **base alpha** 是什么？
>
> **就是 pair spread 的均值回归。**
> 不是“遗传算法本身能赚钱”，也不是纯 filter。NSGA-II 在这里更像 **pair admission / bucket construction layer**：从一堆可做 MR 的 pair 里，筛出“收益-风险更均衡、放到一起更像样”的那一篮子。

## 1. 为什么这轮值得写

最近库里 pairs 已经很多：`distance / cointegration / Hurst / dynamic beta / graph matching / threshold selection / basket allocator` 都有了。继续再写一篇“spread 偏了就回归”当然没错，但边际增量会越来越低。

这篇 2025 新论文的增量点比较明确：**不是再发明一个新 spread，而是把“pair admission”正式写成多目标优化问题。** 这对 desk 很实用，因为我们现在真正容易卡住的，往往不是“有没有均值回复壳”，而是：

1. 候选 pair 太多；
2. 单看 `p-value / Sharpe / half-life` 容易偏；
3. 训练期最赚钱的 pair，常常是 OOS 最不稳定的那批；
4. 多个 pair 一起上时，组合层风险会放大，而单条回测看不出来。

所以这篇 paper 最该 intake 的，不是“NSGA-II 很高级”，而是：**把 pair 入选层从单目标排序，改成 Pareto 前沿筛选。**

## 2. 公开可确认到的论文信息

### 主论文
1. **Mai, Linh My; Ko, Po-Chang; Lin, Ping-Chen; Do, Hoang-Thu; Kuo, Yuan-Heng (2025). _Pairs trading in the cryptocurrency market: a novel approach utilizing NSGA-II_. Applied Economics.**  
   - Venue: *Applied Economics*  
   - DOI: `10.1080/00036846.2025.2512152`  
   - Readable URL: <https://www.tandfonline.com/doi/full/10.1080/00036846.2025.2512152>  
   - Repo URL: **未找到公开官方 repo**  
   - 当前可公开抓到的摘要片段明确提到：  
     - 加密价格高波动为 pairs trading 提供稳定获利机会；  
     - 论文提出 **original NSGA-II-based approach**；  
     - 目标是让候选 pair **同时满足多目标**，核心方向是 **maximizing returns and minimizing risks**。

### 辅助 grounding
2. **Ko, Po-Chang; Lin, Ping-Chen; Chen, Wen-Hsien, et al. (2023). _Pairs Trading Strategies in Cryptocurrency Markets: A Comparative Study between Statistical Methods and Evolutionary Algorithms_. IEEE ICEIB / Engineering Proceedings.**  
   - DOI: `10.3390/engproc2023038074`  
   - Readable URL: <https://www.semanticscholar.org/paper/Pairs-Trading-Strategies-in-Cryptocurrency-Markets%3A-Ko-Lin/9dcaa9aa06ea9a315b37792c027d8470b602da36>  
   - 价值：说明同一作者线此前就在比较 **statistical methods vs evolutionary algorithms**，所以 2025 这篇不是突兀换题，而像是把进化式 pair selection 正式推到 crypto pairs 主线里。

3. **Fil, M.; Kristoufek, L. (2020). _Pairs Trading in Cryptocurrency Markets_. IEEE Access, 8, 172644–172658.**  
   - DOI: `10.1109/ACCESS.2020.3024619`  
   - Readable URL: <https://arxiv.org/abs/2009.13692>  
   - 价值：给 short-cycle grounding——作者在 Binance 26 个液态币上比较后发现，**均值回复在 intraday（5m / 1h）更明显，而日频不明显**。这正好支持我们把 NSGA-II 读成 **短周期 pair admission upgrade**，而不是日频资产配置论文。

> 说明：主论文正文当前站点有验证墙，我这里只冻结 **公开可确认** 的信息；不伪造论文里没有抓到的阈值或超参。对 desk 来说，这已经足够定义一个最小实验。

## 3. 这篇东西该怎么读成 desk 语言

### 3.1 不要读成“遗传算法预测涨跌”

错的读法：
- 用 NSGA-II 猜下一根谁涨谁跌；
- 把 NSGA-II 当单资产方向模型；
- 觉得它只是一个很重的研究花活。

更对的读法：
- **raw alpha 仍然是 spread mean reversion**；
- NSGA-II 负责的是 **pair selection / bucket selection**；
- 它解决的是“同样是可做 MR 的 pair，哪几条更值得给仓位”。

### 3.2 它最适合接在我们现有哪条线上

最自然的接法不是替换我们已有的所有信号，而是接在现有 pairs 壳的前面：

`候选池生成`  
→ `pair 特征打分`  
→ **`NSGA-II 选 Pareto-front pairs / buckets`**  
→ `spread z / percentile / OU / innovation interval 进出场`  
→ `组合层风控`

也就是说，**它服务于多个已有 raw alpha 壳**：
- cointegration spread fade
- percentile entry pairs
- OU half-life wideband
- dynamic beta / Kalman spread
- multi-pair basket MR

这就是它对当前 desk 的真实价值：**不是替代 alpha，而是提高 alpha admission 的质量。**

## 4. 我建议冻结成哪条完整策略骨架

### 4.1 Universe
- 交易所：Binance / Hyperliquid perp（先从 Binance public kline 做）
- 标的：`Top 20~30` 个高流动永续
- 频率：主跑 `5m`，并平行留 `15m`；更激进时再下钻 `3m/1m`

### 4.2 候选 pair 生成
先用便宜方法做第一层筛选，别一上来就让 NSGA-II 在全宇宙乱搜：
- 相关性前 `N`
- rolling cointegration / ADF shortlist
- half-life 上限
- 最低成交额 / 最低开仓容量

### 4.3 NSGA-II admission 层
把每条 pair 在训练窗里的表现压成多目标问题。最小可落地版本我建议直接做 3 目标：

1. **最大化净收益代理**  
   - 例如 `train net pnl` 或 `train sharpe_after_cost`
2. **最小化风险**  
   - 例如 `max drawdown` 或 `return volatility`
3. **最小化摩擦 / 脆弱性**  
   - 例如 `turnover`、`average holding time too short`、`capacity penalty`

如果想先更贴近 paper 公共摘要，就先只做 2 目标：
- maximize returns
- minimize risks

然后从 Pareto front 里再二次选：
- 保留 `5~10` 条 pair
- 去掉共用资产过多的 pair
- 组合层按 risk parity / inverse vol 分配

### 4.4 交易壳（先用最便宜的）
为了让 admission 层的价值被看清，执行壳不要一开始就搞太花：

- hedge ratio：rolling OLS beta
- spread：`s_t = y_t - β_t x_t`
- signal：rolling z-score
- entry：`|z| >= 1.8 ~ 2.2`
- exit：`|z| <= 0.4 ~ 0.6`
- stop：`|z| >= 3.5 ~ 4.0`
- max hold：`12~24 bars`
- cooldown：平仓后 `2~4 bars`

换句话说：**先固定交易壳，再看 admission 层有没有真实增量。**

### 4.5 Sizing / risk / cost
- 单 pair 风险预算：按 spread vol 反比缩放
- 组合 gross 上限：`150%~250%`
- 单资产集中度上限：`<= 35% gross`
- 成本：先按 `4~6 bps taker round-turn` 做悲观测试；如果走 maker 再单独复核
- veto：极端 funding / 极端 basis / news spike 时禁开新仓

## 5. 为什么这条线对 1m / 3m / 5m / 15m 有意义

### 15m
- 最容易先看清 OOS 稳定性；
- 交易笔数不会太爆，适合先验证 admission 层是否真的优于单指标排序。

### 5m
- 我认为这是最值得先测的主战场。  
  因为 pairs MR 在 crypto intraday 更容易出现，但成本也开始变得真实；NSGA-II 若真有价值，应该首先体现在 **5m 下“少做错 pair”**。

### 3m / 1m
- 只适合第二阶段。  
  admission 层本身不会替你解决微观结构噪音；如果 5m 都没有净增量，压到更细只会更像 overfit。

## 6. 这篇 paper 真正补的是哪块素材池

不是再补一个“新 signal”；而是补一张很缺的卡：

> **单条 pair raw alpha 已经够多时，怎么把 candidate set 变成一篮子更能活过风险与成本的 tradeable pair book？**

这件事对我们现在很重要，因为当前库里已经有：
- pair selection 的很多单指标版本；
- entry trigger 的很多版本；
- 但 **“组合 admission” 仍然偏弱**。

所以这篇更像：
- `shared admission layer for pairs raw alpha`
- 但因为 base alpha 仍然是 spread MR，且可单独落地完整策略，**我仍把它归到 raw alpha digest，而不是纯 overlay**。

## 7. 最小实验怎么做

### 实验 A：只测 admission 层有没有增量
- 频率：`5m`
- universe：Top 20 perp
- formation：滚动 `45d`
- trading：滚动 `7d`
- pair 壳：固定 `OLS beta + z-score shell`
- 对照组：
  1. `corr 排序 top-K`
  2. `cointegration p-value 排序 top-K`
  3. **`NSGA-II Pareto top-K`**
- 比较：
  - OOS net Sharpe
  - hit rate
  - median hold
  - max DD
  - turnover
  - 共用资产集中度

### 实验 B：看 admission 层是否跨 signal 壳稳定
把 pair 壳换成三种：
1. `z-score`
2. `percentile entry`
3. `OU half-life`

如果 NSGA-II 只在某一个壳上有用，那它更像“壳内调参器”；
如果三个壳都更稳，那它才像真正的 **shared admission upgrade**。

### 实验 C：5m 通过后再下钻 3m
- 不改 admission 方法
- 只改交易频率与成本假设
- 看净边是否仍存在

## 8. 我当前的判断

### 值得做的原因
1. **raw alpha 很清楚**：就是 pairs mean reversion；
2. **不是又一篇老 cointegration 复读**：新意在 pair admission 的多目标化；
3. **和现有素材池拼接性很强**：可直接插在我们现有 pairs engine 前面；
4. **最小实验成本低**：不用新数据、也不用新执行通道。

### 需要警惕的地方
1. **最容易过拟合。**  
   admission 层如果直接吃训练期 pnl，很容易把噪音当 edge。
2. **目标函数写错就会把“高换手高摩擦”误当高收益。**
3. **Pareto front 不自动等于可交易 front。**  
   还要加容量、共用资产、成本、持仓长度这些 desk 约束。

## 9. 下一步先怎么测

**不要先复刻论文全部细节。先做这个最小版：**

1. 复用我们现有 `pairs candidate` 管线，先产出 `30~80` 条候选 pair；
2. 在 `5m`、`45d train + 7d test` 上，为每条 pair 计算：
   - net pnl after cost
   - max drawdown
   - turnover
   - median holding bars
3. 用 `pymoo` 或自写简版 NSGA-II 做 Pareto admission；
4. 从 Pareto front 里选 `5~10` 条 pair，限制共用资产暴露；
5. 用固定 `z-score shell` OOS 跑；
6. 与 `corr top-K / coint top-K` 做 head-to-head。

**一句话版 next step：先验证“Pareto pair admission”是否比单指标 top-K 更稳，而不是先纠结 NSGA-II 超参。**

## 10. 参考资料

1. **Mai, L. M., Ko, P.-C., Lin, P.-C., Do, H.-T., & Kuo, Y.-H. (2025). _Pairs trading in the cryptocurrency market: a novel approach utilizing NSGA-II_. Applied Economics.**  
   DOI: <https://doi.org/10.1080/00036846.2025.2512152>  
   Readable URL: <https://www.tandfonline.com/doi/full/10.1080/00036846.2025.2512152>

2. **Ko, P.-C., Lin, P.-C., Chen, W.-H., et al. (2023). _Pairs Trading Strategies in Cryptocurrency Markets: A Comparative Study between Statistical Methods and Evolutionary Algorithms_.**  
   DOI: <https://doi.org/10.3390/engproc2023038074>  
   Readable URL: <https://www.semanticscholar.org/paper/Pairs-Trading-Strategies-in-Cryptocurrency-Markets%3A-Ko-Lin/9dcaa9aa06ea9a315b37792c027d8470b602da36>

3. **Fil, M., & Kristoufek, L. (2020). _Pairs Trading in Cryptocurrency Markets_. IEEE Access, 8, 172644–172658.**  
   DOI: <https://doi.org/10.1109/ACCESS.2020.3024619>  
   Readable URL: <https://arxiv.org/abs/2009.13692>

---

- 研究笔记路径：`research/quant_digests/2026-04-03_1135_nsga2-pair-admission-alpha.md`
- 页面 URL（build/publish 后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-03_1135_nsga2-pair-admission-alpha.html`
