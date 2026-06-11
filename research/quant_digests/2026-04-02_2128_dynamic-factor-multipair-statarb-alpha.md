# 别把这篇 2021 *Decisions in Economics and Finance* 论文只读成共同因子解释：对 short-cycle desk，更该先测的是「市场因子剥离 × stationary-factor 多对轮换」这条 relative-value raw alpha

- 主题类型：raw alpha
- 基础 alpha：**先用动态因子模型把 crypto 篮子的共同市场因子剥掉，再根据“第二个平稳因子”对各币的相对高低估做多空轮换**；翻成人话，就是“不是盯单一 pair 的 z-score，而是先去掉市场共振，再做 top-half short / bottom-half long 的多对 relative-value 回归”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-02 21:28 UTC
- 类型：2021 *Decisions in Economics and Finance* 开放获取全文（Springer article text）+ Crossref metadata
- 主题标签：raw-alpha/relative-value/stat-arb/multiple-pairs/dynamic-factor/cointegration/market-neutral/factor-stripping/stationarity-gate/factor-correlation-gate/forecast-ranking/15m/5m/3m/1m/paper/public-data/cost
- 证据类型：paper-based（全文可读，策略规则完整，可直接改写成 short-cycle 最小实验）

## 1. 这次看了什么
这轮主看的是一篇 **2021 年、但还没被 digest 池系统 intake 的多对 market-neutral stat-arb 论文**：它不是再讲“某一对 coin 有 cointegration”，而是先把一篮子币压成 **1 个市场因子 + 1 个可交易的 stationary factor**，再用后者去驱动 **多对轮换式 long-short**。对我们当前 desk，更值钱的点不是“dynamic factor model”这几个字，而是它给了一套 **可独立复现、且自带 regime gate 的 raw alpha 壳子**。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 很清楚：relative-value / stat-arb / multi-pair mean reversion。**

更精确一点说：

> **先把每个币按市场因子 loading 做缩放，令 pair spread 主要只剩第二个平稳因子在驱动；再根据下一期 forecasted scaled-price 排名，做“高估腿空、低估腿多”的 market-neutral 多对轮换。**

所以它不是解释型综述，也不是纯 filter。
它本身就是一条 **能闭环到 entry / exit / sizing / risk / cost** 的 raw alpha。

---

## 3. 为什么这轮值得写它
最近 digest 池里已经有不少：
- 单 pair cointegration / copula / z-score
- PCA residual / OU s-score
- funding / basis / carry
- microstructure lead-lag

但 **“先做共同市场因子剥离，再做多对 ranked spread rotation，并且只在 stationary-factor 成立时交易”** 这条线，反而没有被单独拆开写清楚。

它值得 intake 的原因有 4 个：

1. **它是 raw alpha，不是 gate 冒充 alpha。**
   - 开仓逻辑就是预测的相对错价本身；
2. **它提供的是 multi-pair 壳子，不是只会挑一对 coin。**
   - 这对我们 desk 扩 `relative value / stat-arb` 素材池更实用；
3. **它自带 honest regime gate。**
   - 第二因子不平稳、或两个因子相关性过高时，就不交易；
4. **它对 `15m / 5m` 的 transfer 很自然。**
   - 日频论文的 one-step-ahead 结构，可以直接改成 `15m -> next 1 bar / 2 bars` 的短周期版本。

如果问：“它为什么比继续补一篇 filter 更值得？”
答案很直接：
**因为它自己就是一条完整 raw alpha，而且还能顺手带来一层很诚实的 stationarity / independence gate。**

---

## 4. 主来源与文献信息

### 4.1 主来源（paper）
- **Authors / Year**: Gianna Figá-Talamanca, Sergio Focardi, Marco Patacca / 2021
- **Title**: *Common dynamic factors for cryptocurrencies and multiple pair-trading statistical arbitrages*
- **Venue**: *Decisions in Economics and Finance*
- **DOI**: `10.1007/s10203-021-00318-x`
- **Readable URL**: <https://link.springer.com/article/10.1007/s10203-021-00318-x>
- **Repo URL**: N/A

### 4.2 方法地基（文中直接依赖）
- **Johansen (1991)** cointegration test：`10.2307/2938278`
- **Avellaneda & Lee (2010)** stat-arb / market-neutral framework：`10.1080/14697680903124632`

---

## 5. 论文里真正能交易的那条东西，不是“共同因子解释”，而是 factor-stripped 多对轮换
这篇论文的数据篮子不大：
- **BTC / ETH / LTC / XMR**
- 日频价格
- 样本：**2016-01-01 到 2019-11-30**
- 其中前 3 年主要用于估计，**2019-01 到 2019-11** 用来检验策略

作者先确认：
- 四个价格序列都是 `I(1)`；
- 但在 basket 层面存在 cointegration；
- 因此可以用 dynamic factor model 来拆出共同驱动。

最后他们拟合出的关键信息是：
- **第一因子近似就是市场 / BTC 因子**；
- **第二因子才是决定相对错价是否可交易的那个成分**。

文中直接给出了一个很重要的数值对：
- 第一因子：`λ1 = 0.9962`，ADF `p = 0.2712` → **非平稳 / integrated**
- 第二因子：`λ2 = 0.9823`，ADF `p = 0.00564` → **平稳 / stationary**

翻成人话：
**市场大方向本来就不该拿去做均值回归；真正该拿来做 relative-value 交易的，是剥离市场后剩下那个会回的第二因子。**

---

## 6. 代码/公式层面，策略闭环长什么样
这篇 paper 虽然不是 repo，但规则其实写得很完整，完全够翻成策略。

### 6.1 第一步：动态因子分解价格
作者建模的是：
- 每个币价格 = 常数项 + `β_i1 * f1` + `β_i2 * f2` + idiosyncratic error
- 其中 `f1` 是 integrated 市场因子
- `f2` 是 stationary 相对价值因子

然后把每个价格都除以自己对市场因子的 loading `β_i1`，得到 scaled price：

`p*_i = p_i / β_i1`

这一步的意义非常大：
**把最主要的市场共振先拿掉。**

### 6.2 第二步：任意两币 spread，理论上只剩 stationary factor 在驱动
文中公式推导后得到：
- 任意 pair 的 scaled spread `d_ik`，主要由第二因子 `f2` 和小误差项决定；
- 也就是说，只要 `f2` 仍然平稳，这种 spread 差值就具备均值回归基础。

这和“直接拿 coin A - coin B 做 z-score”最大的不同在于：
**它先做了市场因子中性化，再来讨论 pair spread。**

### 6.3 第三步：做 one-step-ahead 预测，按 forecast 排名组多空
作者不是盯单一 pair，而是：
1. 在时间 `τ` 用 rolling 窗口估计模型；
2. 预测 `τ+1` 的 scaled prices；
3. 将 forecasted scaled prices 从高到低排序；
4. **short 预测值较高的一半资产，long 预测值较低的一半资产**；
5. 形成一个 multiple pair trading portfolio。

这一步很像：
- 不是固定 pair；
- 而是每一期都根据 relative mispricing ranking 来决定哪几条腿该做空、哪几条腿该做多。

对 short-cycle desk 很重要的一点是：
**这条 alpha 本质上更接近“factor-neutral cross-sectional rotation”，而不是传统静态 pair spread。**

---

## 7. 这条策略为什么可以直接落地成完整 raw alpha
因为论文把最核心的交易细节都给出来了。

### 7.1 Entry / direction
作者定义组合当前价值 `v_τ`，再算下一期 forecasted expected value `g_{τ+1}`。

交易规则是：
- 若 `g_{τ+1} > v_τ + cσ^v_τ` → **做多** multiple-pair portfolio
- 若 `g_{τ+1} < v_τ - cσ^v_τ` → **做空** multiple-pair portfolio
- 否则 **不交易 / 持有当前仓位**

这里：
- `σ^v_τ` 是组合价值的波动尺度；
- `c` 是 admission threshold。

翻成人话：
**只有 forecast 偏离当前组合价值足够多，才值得付出交易成本去做这次轮换。**

### 7.2 Exit
论文的动态设定很直接：
- 每次在新时点重新估计模型；
- 每个当期 portfolio 在下一期被重新评估 / 结算；
- 本质上是一个 **rolling one-step strategy**。

对我们 short-cycle 迁移时，可直接映射成：
- `15m` 上每根 bar 重估；
- 持有 `1 bar` 为 baseline；
- 再做 `2 / 4 bars` 的扩展对照。

### 7.3 Sizing
论文原文更像固定规则组合：
- 按预测高低估排序分配多空腿；
- 不是复杂动态仓位优化。

这对 desk 是好事：
**先验证 alpha 本体，再谈 fancy sizing。**

### 7.4 Risk / cost
作者没有假装 friction 不存在，反而明确做了：
- **0.10% 交易费**（对照 Coinbase maker fee）
- 不同 `c` 阈值下的累计收益与净收益比较

结果是：
- **成本前**：`c = 0` 交易最频、累计收益最高；
- **成本后**：**`c = 0.20` 的净累计收益最好**。

这就是 short-cycle 研究里最该学的一件事：
> **admission threshold 不是装饰品，它决定了 gross edge 能不能活到 net。**

---

## 8. 这篇 paper 最值钱的，不是 factor 模型本身，而是它给了一条 honest regime gate
很多 mean-reversion / pairs 论文的问题是：
- 默认永远可交易；
- 信号失效也继续硬上；
- 最后策略坏了，却不知道是 alpha 坏了还是 regime 换了。

这篇 paper 相对诚实得多。

作者明确要求：
1. 第一因子和第二因子的相关性不能太高；
2. 第二因子必须维持 stationary；
3. 如果 moving window 里已经变成 **两个 integrated factor**，就别再做这条策略。

他们在实证里用了一个非常具体的 gate：
- **只有当两因子相关性低于 `0.18` 时才交易**。

而到了 **2019-08-20 之后**：
- moving window 结果显示 **两个因子都更像 integrated**；
- 两因子相关性也上升；
- 因而 **9 月之后基本停止交易**。

这件事对 desk 很关键：
**别把“stationary residual alpha”当 always-on；它天然就该是有启停条件的。**

---

## 9. 和当前 digest 池里的 pairs / stat-arb 线相比，它的新东西在哪
我觉得它最有价值的 3 个新点是：

### 9.1 它不是“先挑 pair 再看 spread”，而是“先去市场因子，再做多对轮换”
这让它比普通 pair 更像：
- 市场中性
- 多标的联合比较
- 可扩 universe

### 9.2 它不是“看 z-score 大小”，而是“看下一期 forecasted relative ranking”
也就是：
- 你不是被动等 spread 偏离；
- 你是在因子模型下主动预测“哪一半相对贵、哪一半相对便宜”。

### 9.3 它天然自带 stationarity / correlation veto
这比很多 repo 里“永远开机”的 coint/pairs 框架更诚实。

所以如果要给它一个最准确的 desk 定位，我会写成：
**raw alpha / relative-value / stat-arb / factor-stripped multi-pair rotation**。

---

## 10. 对 short-cycle desk，怎么把它翻成 `15m / 5m / 3m / 1m` 最小实验
论文是日频，但迁移路径其实很清楚。

### 10.1 Universe
第一轮不要用太大 universe，先用高流动永续：
- `BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LTC`
- 后续再扩到 top10 / top12 liquid perps

### 10.2 Data
- 发现层：`15m`
- 快速版：`5m`
- `3m / 1m` 暂时只当执行细化层，不先拿来做发现层

### 10.3 因子估计
paper 用 state-space dynamic factor model；
在最小实验里可以先做两版：

1. **paper-faithful 近似版**：
   - 对 log price levels 做 two-factor state-space / dynamic factor estimation；
2. **desk proxy 版**：
   - 用 rolling PCA / Kalman-like approximation 先近似出 `f1 / f2`；
   - 核心不是形式最优，而是先验证“one integrated-like market factor + one stationary-like relative factor”能否出现。

### 10.4 交易规则（先做最小可复现版）
在每个 `15m` bar：
1. rolling 估计两因子；
2. 计算每个币的 scaled price 与 next-bar forecast；
3. forecast 排序；
4. short top half，long bottom half；
5. 若 `g_{t+1} > v_t + cσ_t` 或 `< v_t - cσ_t` 才换仓；
6. 若 `ADF(f2)` 不通过，或 `corr(f1,f2) > threshold`，则不交易。

### 10.5 持有期
因为论文是 one-step-ahead，所以 short-cycle 最合理的 baseline 是：
- `15m` 发现 → 持有 `1 bar`
- 再扩展：持有 `2 / 4 bars`
- `5m` 版本同理

不要一上来做长 hold；先确认 alpha 是不是真的只在“下一步回归”里。

### 10.6 成本
至少做三档：
- maker optimistic
- hybrid realistic
- taker pessimistic

因为这条线跟所有 stat-arb 一样：
**最大的敌人不是没有 gross，而是 turnover 太高。**

---

## 11. 我认为对 desk 最值得拿走的，不是作者原始四币组合，而是下面这 4 个改写点

### 11.1 把“factor stationarity”从论文条件，改成正式 research gate
也就是每轮回测都记录：
- `ADF p-value(f2)`
- `corr(f1,f2)`
- trade / no-trade 比例

这样以后别的 pairs / stat-arb 壳子，也可以共用这层 honest gate。

### 11.2 把 top-half / bottom-half 改成 sparse version
原文是半篮子轮换；
对短周期更实际的做法是：
- 只做 **forecast 最极端的 top-2 / bottom-2**；
- 或只做 top / bottom quantile。

这样更容易活过成本。

### 11.3 把 `c` 当成核心调参，不是边角料
论文已经给出明确信号：
- **成本前** 最优 admission 不等于 **成本后** 最优 admission。

所以第一轮网格就该扫：
- `c = 0, 0.10, 0.15, 0.20, 0.25`

### 11.4 别急着把它下放到 `1m`
如果 `15m` 都还不能稳定找到“平稳第二因子 + 低相关因子”结构，
那 `1m` 只会更吵。

所以最合理顺序是：
- 先 `15m`
- 有戏再做 `5m`
- `3m / 1m` 只做 execution refinement

---

## 12. 这条 alpha 最容易失败在哪

### 12.1 根本不存在稳定的第二因子
如果 basket 只有一个大 market mode，
剩下全是噪音，
那这条线就没法交易。

### 12.2 因子估计太频繁，导致 turnover 爆炸
短周期里滚动估计若太敏感，会出现：
- 排名频繁翻转
- 交易腿不断切换
- cost 比信号快

### 12.3 把 regime gate 当装饰
这篇 paper 最不该删掉的，就是“不满足结构假设就停手”。
删掉这层，策略会看起来更 busy，但不会更赚钱。

### 12.4 universe 太杂
小币、跳价大、资金费率极端、盘口薄的标的，会让第二因子变得非常不稳。
第一轮必须先用流动性最好的一组。

---

## 13. 一句话结论
如果只带走一句话，我会带走这句：

**别把这篇 2021 论文只读成“共同因子解释”；对 short-cycle desk，更值得快检的是「市场因子剥离后、由 stationary 第二因子驱动的多对轮换」这条 relative-value raw alpha。**

它最值钱的地方不是又多了一个 stat-arb 名词，
而是：
- alpha 本体清楚；
- 交易规则完整；
- 成本阈值有明确角色；
- 还有一层很诚实的 stationarity / correlation gate。

---

## 14. 下一步怎么测（直接执行版）
1. **先做 `15m` 最小实验**：8~10 个高流动 USDT perpetual，rolling two-factor model，跑 next-1-bar multiple-pair rotation。
2. **把 gate 写死进回测**：只有当 `f2` 的 ADF p-value 过关、且 `corr(f1,f2) < 0.15~0.20` 才允许交易。
3. **把半篮子版本和 sparse 版本同时跑**：
   - baseline：top-half short / bottom-half long
   - desk 版：top-2 short / bottom-2 long
4. **重点扫 admission 阈值 `c`**：`0 / 0.10 / 0.15 / 0.20 / 0.25`，比较 gross 与 net 的最优点是否错位。
5. **持有期只先测短的**：`1 / 2 / 4 bars`，先确认它是不是标准 one-step reversion。
6. **确认 15m 有戏后再下放到 5m**；如果 5m turnover 爆炸，就把 `3m / 1m` 留给 execution 和 re-entry，而不是主 alpha 发现层。

---

## 15. 文件信息
- 文件路径：`research/quant_digests/2026-04-02_2128_dynamic-factor-multipair-statarb-alpha.md`
- 站点相对 URL：`/reading/quant_digests/2026-04-02_2128_dynamic-factor-multipair-statarb-alpha.html`
