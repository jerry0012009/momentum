# 别把这篇 2025 *Optimization and Engineering* / 配套 repo 只当 pair-searcher：对 desk 更该先测的是「moving-band basket stat-arb × 线性 inventory shell」完整 raw alpha

- 时间：2026-03-31 12:34 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/relative-value/stat-arb/multi-asset/basket/mean-reversion/moving-band/convex-concave/linear-policy/markowitz-shell/crypto-transfer/1m/3m/5m/15m/paper/repo/public-data/cost
- 证据类型：2025 *Optimization and Engineering* 全文 HTML + Stanford paper page + `cvxstatarb` repo source audit + 2025 *Journal of Asset Management* follow-up page

- 主题类型：raw alpha
- 基础 alpha：多资产组合价格相对 rolling midpoint 的偏离回归（moving-band basket mean reversion / stat-arb）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
不是再找“哪两条线最像”的老式 pairs，而是把 **多资产 basket 本身** 当成可优化搜索对象：在“组合价格要留在带内”的约束下，直接找 **波动大、但会回带** 的组合，然后用一个极简单的线性仓位壳子 `q_t = μ_t - p_t` 去交易。

## 2. 为什么这次值得进研究池
这轮 bot7 的优先级里，`raw alpha / 可直接落地完整策略` 高于纯解释型材料。这个主题满足两点：

1. **base alpha 很清楚**：不是 filter，不是 regime，不是“先有 pair 再想办法调阈值”；它的 alpha 本体就是 **basket price 对 moving midpoint 的均值回复**。
2. **它补的是我们当前素材池里还不够厚的一块**：很多现有短周期 pairs 还停留在 `2-leg spread z-score`。这篇东西给的是更上游的能力——**自动搜索 3~10 leg 的 mean-reverting basket**，天然能扩成 crypto 的 sector basket / quote cluster / beta-neutral sleeve。

## 3. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = 多资产组合价格 `p_t = s^T P_t` 围绕 rolling midpoint `μ_t` 的均值回复。**

更直白点：
- 先不是问“BTC/ETH 有没有偏离”；
- 而是问“有没有一组权重 `s`，能让组合价格既不乱飞出带，又有足够来回摆动可以赚”；
- 找到以后，交易逻辑很朴素：
  - `p_t < μ_t` → 做多这个 basket
  - `p_t > μ_t` → 做空这个 basket
  - 仓位强度直接随 `μ_t - p_t` 线性变化。

所以它是 **raw alpha**，而不是 overlay。

## 4. 核心来源
### 4.1 主论文
- **Authors**：Kasper Johansson, Thomas Schmelzer, Stephen Boyd
- **Year**：2025（Stanford page 标注正式刊发），repo BibTeX 记作 2024
- **Title**：*Finding Moving-Band Statistical Arbitrages via Convex-Concave Optimization*
- **Venue**：*Optimization and Engineering*, 26, 1203–1224
- **DOI**：10.1007/s11081-024-09933-0
- **Readable URL**：https://web.stanford.edu/~boyd/papers/cvx_ccv_stat_arb.html
- **arXiv URL**：https://arxiv.org/abs/2402.08108

### 4.2 配套仓库
- **Repo**：`cvxgrp/cvxstatarb`
- **Repo URL**：https://github.com/cvxgrp/cvxstatarb
- 直接可见：`experiments/backtest.py`, `cvx/stat_arb/ccp.py`, `tests/test_stat_arb.py`

### 4.3 后续管理层论文（不是本篇主 alpha，但很适合接在后面）
- **Authors**：Kasper Johansson, Thomas Schmelzer, Stephen Boyd
- **Year**：2025
- **Title**：*A Markowitz Approach to Managing a Dynamic Basket of Moving-Band Statistical Arbitrages*
- **Venue**：*Journal of Asset Management*, 26(4):377–385
- **DOI**：10.48550/arXiv.2412.02660
- **Readable URL**：https://web.stanford.edu/~boyd/papers/portfolio_of_SAs.html

## 5. 证据里最值得拿走的硬点
### 5.1 这不是“理论想法”，作者给了完整搜索 + 交易 + 成本口径
主论文数值实验用的是：
- **数据**：CRSP US 股票日频，2010-01-04 到 2023-12-30，**15,405** 个资产，合计 **3,282** 个交易日；
- **搜索节奏**：从 2011-12-23 起，**每 21 个交易日** 重跑一次；
- **每次搜索范围**：当时点市值前 **200** 个资产；
- **初始化**：每次 **10** 个随机初始组合；
- **moving-band 参数**：repo/notebook 对应 `P_max=100`, `spread_max=1`, `midpoint_memory=21`, `T_max=125`；
- **交易成本**：模拟里把买卖价差成本算进去了（买按 ask、卖按 bid），另加 **0.5% 年化 shorting cost**。

这点对我们很重要：它不是那种“只给组合发现方法，不给交易壳”的论文，反而是 **alpha 搜索 + 线性 position rule + 成本核算** 一条龙都给了。

### 5.2 交易壳其实非常简单：`q_t = μ_t - p_t`
在 `cvx/stat_arb/ccp.py` 里，交易头寸就是：
- **线性仓位**：`q_t = μ_t - p_t`
- **exit**：到 `T_max` 后开始退出，**再用 21 个 period 线性降到 0**
- **positions**：各腿仓位 = `q_t × basket weight`
- **profit**：上一期持仓 × 本期组合价格变化

这意味着它很容易移植到 desk：
- 你完全不需要先上复杂 RL；
- 先把 **组合发现器** 和 **最朴素的 inventory shell** 跑起来，就已经是完整 raw alpha。

### 5.3 moving-band 比 fixed-band 更像我们想要的真实交易对象
论文主结论不是“所有 mean reversion 都有效”，而是：**把 band midpoint 做成 rolling/moving，比固定中枢更实用。**

文中报告：
- **fixed-band**：找到 **545** 个 unique stat-arbs，资产数 **3~9**，中位数 **6**；
  - 平均年化收益 **10%**
  - 平均年化风险 **32%**
  - 平均年化 Sharpe **0.81**
  - 平均最大回撤 **15%**
- **moving-band**：找到 **712** 个 unique stat-arbs，资产数 **1~10**，中位数 **5**；
  - **70%** 的 stat-arbs 盈利
  - 平均年化收益 **15%**
  - 平均年化风险 **20%**
  - 平均年化 Sharpe **0.84**
  - 平均最大回撤 **12%**
  - 活跃 stat-arb 的中位数约 **40** 个
  - 提前“爆掉”（NAV 跌破初始 50%）的只占 **0.4%**

对 desk 的翻译：
- 与其在一条固定 spread 上死调 z-score，
- 不如先承认 **中枢会漂移**，然后让策略围绕“漂移中的公平值”去做回归。

### 5.4 这篇东西最适合我们 desk 的，不是“美国股票日频表现有多好”，而是它的搜索框架
真正可迁移的不是原论文 market，而是这几个结构：

1. **优化目标**：直接找“高摆动 + 不脱带”的 basket；
2. **多资产**：不把 stat-arb 限制死在 2 legs；
3. **moving midpoint**：默认公平值可漂移；
4. **线性持仓**：不用先拍 entry/exit 二值阈值；
5. **组合管理可外接**：后续可直接接 2025 *Journal of Asset Management* 那篇的 basket allocation 层。

## 6. 对 crypto 1m / 3m / 5m / 15m 的正确读法
### 6.1 不要机械照抄“21 天 / 日频”
原文是 **US equities 日频**。我们不能直接把 21 天等比例平移成 21 根 15m。正确做法是保留结构，不保留字面窗口：

- 原文 `midpoint_memory=21` 的本质不是“神奇的 21”，而是 **用一个足够慢的 rolling fair value 托住短中期回归**；
- 原文 `T_max=125` 的本质不是“必须持有 125 个 period”，而是 **给 basket 回归充足时间，但不能无限拖**；
- 原文每 21 天重搜一次，本质是 **search cadence 要慢于交易 cadence**，别边交易边每根 bar 重拟合。

### 6.2 对 crypto 最自然的迁移场景
我认为最值得先测的不是全市场乱搜，而是这三类受控宇宙：

1. **同 beta / 同叙事 basket**
   - BTC / ETH / SOL / BNB majors
   - L2 basket
   - DeFi beta basket
   - meme beta basket

2. **同标的多报价 / 多 venue basket**
   - 同 underlier 的多合约 / 多 stablecoin quote
   - 比 2-leg pair 更适合扩成 3~4 leg 冲突路由

3. **leader + followers basket**
   - 一个 leader leg 配多个 follower leg
   - 比单一 pair 更接近“行业内 relative-value 偏离再回归”

### 6.3 对短周期 desk 的最小参数迁移建议
下面不是论文原值，而是 **为 1m/3m/5m/15m 复现准备的 first pass**：

- **15m 版**
  - train：最近 **20~30 天**
  - 重新搜索 basket：每 **1 天** 或每 **96 bars**
  - midpoint memory：**64~128 bars**
  - 持有上限 `T_max`：**24~48 bars**
  - exit fade：**4~8 bars**

- **5m 版**
  - train：最近 **14~21 天**
  - 重新搜索 basket：每 **4~8 小时**
  - midpoint memory：**72~144 bars**
  - 持有上限 `T_max`：**24~72 bars**
  - exit fade：**6~12 bars**

- **1m / 3m 版**
  - 只建议先在 **10~20 个最液体标的** 上做，避免把搜索器变成噪音拟合器
  - 先用 maker/taker 两套成本假设分别跑，不要一上来混合成交幻想

## 7. 对我们 desk 最重要的拆解：它到底能落成什么完整策略？
### 7.1 Entry
先找到一个 basket：
- 权重 `s`
- 组合价格 `p_t = s^T P_t`
- rolling midpoint `μ_t`

然后做：
- `score_t = (μ_t - p_t) / band_scale`
- `score_t > 0` → long basket
- `score_t < 0` → short basket

first pass 可以直接照作者的 **线性仓位**，也可以加个最小门槛：
- 只有 `|score_t| > 0.5` 才开仓
- `|score_t|` 越大，仓位越大

### 7.2 Exit
优先按三层：
1. **回到中枢附近**：`|score_t| < 0.1`
2. **时间止损**：超过 `T_max`
3. **退出拖尾**：仿 repo，用 `N_exit` 根线性降到 0

### 7.3 Sizing
可直接复制论文精神：
- 基础仓位跟 `μ_t - p_t` 线性；
- 组合层再加 gross leverage cap；
- 对 crypto 建议再补两个约束：
  - 单腿 notional cap
  - 单一 narrative / highly correlated bucket cap

### 7.4 Risk
至少要加：
- basket half-life 漂移监控
- legs concentration cap
- funding / fee / borrow proxy
- 波动突升时的 inventory compression
- re-fit 后新旧 basket overlap 过低时，别硬切满仓

### 7.5 Cost
crypto 里最容易把它从 paper alpha 打成假象的就是成本：
- taker fee
- spread widening
- funding
- 强相关腿同时冲击的 market impact
- 高频换篮子的 turnover

所以 first pass 一定要至少跑：
- **maker-only 假设**（过于乐观，但看 alpha 上限）
- **taker-only 假设**（保守）
- **mixed 假设**（更接近真实）

## 8. 它相对当前常见 pair-zscore 框架，真正新增了什么
### 8.1 新增的不只是“多几条腿”
核心升级是：
- **pair-zscore**：先有 pair，再围绕 pair 调阈值
- **moving-band basket**：先定义“想要什么样的组合价格”，再反推 basket 权重

这是 research pipeline 的上游升级。

### 8.2 为什么这比继续补一个普通 pair 更值得
因为它能同时服务三类后续方向：
1. **raw alpha 扩容**：pair → basket
2. **shared shell 复用**：同一个 linear inventory / time-exit / cost framework 可以复用到不同 basket
3. **组合层管理**：可自然衔接 `portfolio_of_SAs` 的 basket allocation

## 9. 局限与风险
1. **原证据不是 crypto、不是分钟级**：这是最大的 transfer risk。
2. **搜索器很容易过拟合**：如果你每小时重拟合全宇宙，最后学到的可能只是噪音。
3. **crypto 的相关结构会 regime shift 更快**：篮子寿命可能远短于股票日频。
4. **perp 还有 funding / clamp / ADL / contract-spec 差异**：这些是论文没有替你解决的。
5. **多腿组合的执行复杂度会陡增**：尤其在 1m/3m 上，错一腿就不是纯 stat-arb 了。

## 10. 最小可复现实验（建议直接做）
### 实验 A：15m majors / sector basket moving-band MR
- **标的池**：BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LINK, LTC, BCH, AVAX, DOT
- **频率**：15m
- **训练窗**：过去 30 天
- **重搜频率**：每天 1 次
- **basket 大小**：3~5 legs
- **midpoint memory**：96 bars
- **entry**：`|score| > 0.75`
- **exit**：`score` 回到 0.15 内，或 `T_max = 32 bars`，再 `N_exit = 6 bars` 线性降仓
- **对照组**：
  - 同池内 rolling z-score 最优 pair
  - 同池 PCA residual MR
- **看什么**：after-cost Sharpe、hit ratio、平均持有时长、换篮率、单腿贡献集中度

### 实验 B：5m 同叙事 basket 快速版
- **标的池**：只取一个叙事（例如 L2 或 meme）里最液体 6~10 个 perp
- **频率**：5m
- **训练窗**：过去 14 天
- **重搜频率**：每 6 小时
- **midpoint memory**：72 bars
- **T_max**：48 bars
- **成本假设**：maker / taker / mixed 三套都跑
- **目的**：判断这类 moving-band 结构在更快节奏下是否还保留边际

### 实验 C：同标的多报价 basket
- **对象**：同一 underlier 的多合约/多 quote（如果数据结构允许）
- **目的**：验证 moving-band basket 是否比 2-leg spread 更能处理冲突报价与闲置资本问题

## 11. 我建议的“下一步怎么测”
1. **先不要全市场乱搜**：先从 majors 或单叙事小宇宙开始。
2. **先做 15m，再压到 5m**：先验证 alpha 结构，再测 execution 极限。
3. **先固定 linear policy**：别一上来再叠 RL / dynamic threshold，避免 attribution 混乱。
4. **每次只换一个维度**：
   - pair → basket
   - fixed midpoint → moving midpoint
   - threshold entry → linear entry
5. **必须留基线**：至少和 `best pair z-score`、`PCA residual MR` 对打。
6. **一开始就记 turnover 与换篮率**：这类策略最容易 paper 上赢、实盘输在 turnover。

## 12. 一句话结论
这篇东西最值得 desk 拿去测的，不是“又一个 pairs 论文”，而是：**把短周期 stat-arb 的研究对象从单 pair 升级成可搜索的 moving-band basket，再用最朴素的线性 inventory shell 先跑出 after-cost 结果。**

## 13. 来源链接
- 主论文 Stanford 页面：https://web.stanford.edu/~boyd/papers/cvx_ccv_stat_arb.html
- 主论文 arXiv：https://arxiv.org/abs/2402.08108
- 配套仓库：https://github.com/cvxgrp/cvxstatarb
- 组合层 follow-up 页面：https://web.stanford.edu/~boyd/papers/portfolio_of_SAs.html
