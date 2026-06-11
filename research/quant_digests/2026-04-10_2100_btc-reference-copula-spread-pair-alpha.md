# 别把 copula pairs 只当分布学花活：这篇 2025《Financial Innovation》更该先复现的是「BTC reference spread-pair conditional mispricing」完整 raw alpha
- 时间：2026-04-10 21:00 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：`relative-value / pairs mean reversion` —— 不是直接赌两条币价线回归，而是赌**两条 BTC 对冲后的相对价值 spread**在“联合分布条件失衡”后回到常态依赖结构
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / copula / cointegration / BTC-reference / conditional-mispricing / market-neutral / binance / perpetual / 5m / 15m / paper
- 证据类型：开放获取论文全文 + 表格原文 + Binance USDⓈ-M 公共数据 portability probe

## 1. 这次看了什么
我这次选的是 **Masood Tadi, Jiří Witzany (2025), _Copula-based trading of cointegrated cryptocurrency Pairs_, Financial Innovation**。

这篇值得 intake，不是因为“copula 听起来高级”，而是因为它给的是一条**相对完整、可直接交易的 crypto pairs 骨架**：
- 先用 **BTCUSDT** 当 reference asset；
- 把每个 alt 改写成 `BTC - β_i * alt_i` 的**参考资产 spread**；
- 在 formation window 里先做 **cointegration + τ 排序**选出本周最值得交易的两条 spread；
- 再用 copula 条件概率判断谁相对贵、谁相对便宜；
- 最后映射回真实下单腿：**short β1·P1 / long β2·P2** 或反过来。

所以这不是“pairs 外面再糊一层统计术语”，而是把 **选对、定价、entry/exit、手续费、周度换对** 都写进去了。对当前 desk 来说，它补的是一条**完整 stat-arb / relative-value raw alpha**，而不是又一篇只能当 filter 的材料。

## 2. 先回答：这篇东西的 base alpha 是什么？
一句话：
**base alpha 就是“BTC 对冲后的 alt-relative-value 均值回归”。**

更细一点：
1. 先把每个 alt 的大盘共性暴露，用 `BTC - β_i * alt_i` 剥掉；
2. 再看两条这类 spread 的**联合依赖关系**；
3. 当条件分布告诉你：`spread1` 明显偏低、`spread2` 明显偏高（或相反）时，做一组 market-neutral long/short；
4. 赌的是它们会往“平时的联合关系”收敛，而不是赌单边趋势。

所以它本质上是：
- `raw alpha`：是
- 类型归属：**pairs / stat-arb / relative-value / mean reversion**
- 不是 filter，不是 overlay，也不是纯解释文。

## 3. 论文里最有价值的几件事
### 3.1 它不是直接拿 coin1-vs-coin2 做传统 z-score
论文最值钱的设计，是先把每个 alt 都改写成：
- `S_i = BTCUSDT - β_i * P_i`

然后交易的对象不是“币价对”，而是**两条 BTC-reference spreads 的相对错位**。
这比传统 `P1 - βP2` pairs 多了一层含义：
- 先把两条 alt 都投影到“相对 BTC 的偏离”；
- 再比较哪条 spread 在联合状态里更贵 / 更便宜；
- 这样更像在抓 **alt-vs-alt 的相对价值**，而不是把 BTC 大盘摆动误当作单对 alpha。

### 3.2 论文给了明确交易规则，不是只有“可解释性”
原文 Table 3 / 4 给的规则很清楚：
- 若 `h1|2 < α1` 且 `h2|1 > 1-α1`：
  - 开 `long S1 / short S2`
  - 映射到真实腿就是：**long β2·P2, short β1·P1**
- 若 `h1|2 > 1-α1` 且 `h2|1 < α1`：
  - 开 `short S1 / long S2`
  - 映射到真实腿就是：**short β2·P2, long β1·P1**
- 若两边都回到 `0.5` 附近：
  - 平仓

这里 `h1|2`、`h2|1` 本质上就是 copula 条件概率，作者把它解释成**相对误价概率**。

### 3.3 它连 formation / trading schedule 都给了
论文不是“想到就做多空”那种散点想法，而是完整周度流程：
- **3 周 formation + 1 周 trading**
- 总共 **104 个滚动周期**
- 样本：**20 个 Binance USDT-M futures 合约**
- 数据频率：**hourly + 5-min**
- 样本期：**2021-01-22 ~ 2023-01-19**
- 费用：明确按 Binance USDT-M **maker 2bps / taker 4bps** 讨论，并用 market order 成本记账

这就意味着：
它不是只能写成“研究备忘录”，而是本来就可以被 desk 直接改装成策略原型。

## 4. 论文原始结果里，最值得记住的数据点
### 4.1 5-min、EG test、`α1=0.20` 是文中最亮的主结果
原文 Table 6 给出的最佳 5-min 结果（reference-asset-based copula approach with EG test）：
- **Total net return：`205.9%`**
- **Annualized net return：`75.2%`**
- **Annualized Sharpe：`3.77`**
- **Maximum drawdown：`-30.5%`**
- **Transactions：`266`**

这说明它不是“理论上可行”；至少在作者的历史样本里，它是**能活成一个完整策略**的。

### 4.2 传统 baseline 在成本后明显更差
同篇 Table 7 很关键：
- 传统 **cointegration z-score** 在 5-min / EG 下：
  - **Total gross return：`121.4%`**
  - 但 **Transaction cost：`-681.2%`**
  - 最终 **Total net return：`-559.8%`**
- 传统 **return-based copula** 在 5-min / EG 下：
  - **Total gross return：`249.6%`**
  - 但 **Transaction cost：`-1388.4%`**
  - 最终 **Total net return：`-1138.9%`**
- 相对稳一点的 **level-based copula** 在 5-min / EG 下：
  - **Total net return：`17.9%`**
  - **Annualized Sharpe：`0.96`**

而作者自己的 reference-asset-based 版本在同样 5-min / EG 下能做到 **`205.9%` net / `3.77` Sharpe**。

翻成人话就是：
**这篇 paper 的 edge 不只是“copula 比 z-score 更 fancy”，而是它确实在“高频 crypto pairs 容易被手续费打死”这件事上，给出了一条成本后仍能活的结构。**

## 5. 为什么它和当前项目直接相关
当前 digest 池里已经有不少：
- 直接价差 z-score pairs
- Hurst / anti-persistence pairs
- dynamic-factor / Kalman / beta-gap
- 单资产均值回归

这篇的新增价值在于：
### 5.1 它补的是一种**不同的 pairs 建模视角**
不是：
- “先选两条长得像的线，再看 spread”

而是：
- “先把每个 alt 变成 BTC-reference spread，再对 spread-pair 做条件误价判断”

也就是把 `alt-vs-alt` 的 relative value，先投影到 `vs BTC` 的坐标系里再交易。

### 5.2 它天然适合 short-cycle desk
原因很简单：
- 论文原生就做 **5-min / hourly**
- 费用显式纳入
- 周度 formation / trade 容易工程化
- 是真正的 **market-neutral two-leg alpha**，不必依赖方向行情

### 5.3 它服务的是 raw alpha 素材池，不是只当附属 veto
这条线单独就能成立：
- 有 formation
- 有 pair selection
- 有 entry/exit
- 有 sizing 映射
- 有 cost 假设
- 有 benchmark 对照

所以它不是“等某个 breakout 主信号出现后再帮你确认”的那类材料；它自己就是一个**完整 relative-value sleeve**。

## 5.5 策略拆解（必填）
- 方向属性：**双向 / market-neutral / 相对价值回归**
- 基础 alpha：**BTC-reference spread-pair conditional mispricing 会向常态联合依赖结构回归**
- regime：周度 formation 后，是否能找到足够稳定的 BTC-cointegrated 候选；以及 copula dependency 是否稳定
- filter / veto：
  - formation 周里 cointegration 不成立则跳过
  - τ 太弱 / dependency 太弱则不交易
  - 条件概率没进入极端带则不进场
- risk / sizing / execution overlay：
  - 仓位按 `β1 / β2` 映射到真实腿
  - 周末或换周强平
  - 成本至少按 taker `4bps`/side 测
  - 后续可加 maker 化、流动性上限、单周最大开仓数、事件禁做窗

## 6. 我做的 portability probe：先看这条思想能不能压到当前 Binance perp
### 6.1 快检口径
我没有做 paper 的 full faithful replication，而是做了一个**对 desk 更快可复现**的 transfer probe：
- 数据：Binance USDⓈ-M 公共 close 数据
- 资产：`BTC + ETH/BNB/SOL/XRP/ADA/DOGE/LINK/LTC/BCH/ETC`
- 周期：`15m` 与 `5m`
- formation / trading：沿用论文结构，**21 天 formation + 7 天 trading**
- 候选选择：
  - 对每个 alt 先构造 `BTC - β_i * alt_i`
  - 对 formation window 做 ADF，保留 `p < 0.10` 的 BTC-cointegrated spreads
  - 在保留集合里选 **|Kendall τ| 最高** 的 spread-pair 作为本周交易对象
- copula 简化：
  - 论文原版是多家族 copula + AIC 选模
  - 我的 portability probe 为了快，改成 **经验边际分布 + Gaussian copula proxy**
- 交易阈值：沿用文中最亮的那档，`α1 = 0.20`, `α2 = 0.10`
- 成本：按 **taker `4bps`/side** 记换手成本
- 对照：同一周、同一对币，做一个**传统直接价差 z-score baseline**（entry `±2` / exit `±1`）

### 6.2 结果：15m 和 5m 都是正的，而且明显优于直接价差 baseline
#### `15m` portability probe（近 `84d`）
- active cycles：**`8 / 9`**
- copula 版总 net return：**`+27.7%`**
- 成本拖累累计约：**`1.12%`**
- 关闭交易数：**`14` 笔**
- 每笔平均 net return：约 **`+1.82%`**
- 同期直接价差 z-score baseline：**`+4.6%`**

#### `5m` portability probe（近 `49d`）
- active cycles：**`4 / 4`**
- copula 版总 net return：**`+11.6%`**
- 成本拖累累计约：**`0.72%`**
- 关闭交易数：**`9` 笔**
- 每笔平均 net return：约 **`+1.28%`**
- 同期直接价差 z-score baseline：**`+2.1%`**

### 6.3 这版快检里，重复被选中的 pair 也有信息量
在这版简化迁移里，比较常出现的组合有：
- `ETH-SOL`
- `ETC-LTC`
- `ADA-LINK`
- `DOGE-ETC`

这说明这条线不是“什么 pair 都行”；它更像是：
**在某些相对价值关系更稳定、同时又保留可交易波动的 pair 上，BTC-reference 表达法更容易跑出来。**

### 6.4 这条 portability probe 最重要的判断
它最值得保留的不是绝对收益数字本身，而是下面这句：

**同一批 short-cycle perp，reference-spread + conditional-mispricing 这套表达，明显比“直接价差 z-score”更像一条能活下来的 pairs skeleton。**

## 7. 这篇 paper 真正适合 desk 先偷的，不是“copula 全家桶”，而是这 3 件事
### 7.1 先偷“reference asset representation”
很多 crypto pairs 一上来就直接：
- `P1 - βP2`

这篇更值得先偷的是：
- `BTC - β1 P1`
- `BTC - β2 P2`
- 再比较这两条 spread 的相对失衡

也就是先统一对 BTC 去大盘暴露，再做 alt-vs-alt 的相对价值判断。

### 7.2 再偷“周度重选对 + 周内交易”
这篇不是永远抱着一对不放。
它告诉你：
- pairs 更像**周度 roster**，不是长期婚姻；
- formation 和 trading 应拆开；
- 找不到合格 pair 的周，可以空仓。

这对 live trading 很重要，因为它天然内置了**不交易也是决策**。

### 7.3 最后才是“copula probability bands”
对 desk 来说，copula 家族本身不是第一优先级。
第一优先级其实是：
- 你是否真的抓住了**条件误价**，而不是只看单条 spread 偏离；
- 你是否能把这种误价表达成稳定、低换手、成本后还能活的 long/short 规则。

所以工程实现顺序应该是：
1. reference-spread universe
2. 周度 pair funnel
3. 条件误价带进出场
4. 最后再升级 copula 家族选模

## 8. 风险与保留意见
- 我这次 portability probe **不是论文 full replication**：
  - 我用的是 `Gaussian copula proxy`
  - 不是作者原文那套多家族 copula + AIC 最优选模
- 论文里关于 Kendall’s τ 的具体 ranking 表述有一点文字歧义；
  - 我在 portability probe 里采用的是：**在 BTC-cointegrated spread 候选里，选 |τ| 最高的 spread-pair**
- 我只用了一小部分 liquid majors；
  - 论文原始样本是 **20 个 Binance USDT-M 合约**，且有 `EOS/TRX/XLM/ONT/IOTA/BAT` 等币
- 当前 probe 只看 close-to-close，不含盘口 / 滑点 / funding / 强平链式冲击
- 这条线本质仍是 pairs / stat-arb；
  - 一旦遇到单边结构性 re-pricing、共识切换或流动性断层，历史依赖结构可能会突然失效

## 9. 下一步怎么测
### 9.1 先做 faithful replication
优先把论文原版关键部件补齐：
- 20 币 universe 对齐 paper Table 1
- hourly + 5m 全样本重跑
- EG / KSS 都跑
- `α1 = 0.10 / 0.15 / 0.20` 全扫
- 明确复刻 Table 6 / 7 的核心数字区间

### 9.2 再做 desk 版减法
如果 full replication 成立，下一步不是立刻上最复杂 copula，而是做一个 desk-friendly 版本：
- `15m` 主版，`5m` 只做确认 / finer execution
- 保留 reference-spread 架构
- 条件概率可先用：
  - Gaussian copula
  - 或经验 copula / rank-based conditional bands
- 强制加：
  - 单周最大交易次数
  - 事件前后禁做窗
  - maker/taker 分层
  - 每周 pair stability veto

### 9.3 最该先看哪几个 admission 指标
1. **post-cost expectancy / trade**
2. **周度 active-cycle 占比**（经常找不到 pair，则 live 频率不够）
3. **pair turnover 稳定性**（是否总在少数 pair 上有效）
4. **换手 / 成本占 gross 的比例**
5. **大波动周的 drawdown clustering**

## 10. 来源
- Masood Tadi, Jiří Witzany. (2025). *Copula-based trading of cointegrated cryptocurrency Pairs*. *Financial Innovation*.
- DOI: `10.1186/s40854-024-00702-7`
- Readable URL: `https://doi.org/10.1186/s40854-024-00702-7`
- Full HTML: `https://link.springer.com/article/10.1186/s40854-024-00702-7`
- Table 1 universe: `https://link.springer.com/article/10.1186/s40854-024-00702-7/tables/1`
- Table 6 results: `https://link.springer.com/article/10.1186/s40854-024-00702-7/tables/6`
- Table 7 baselines: `https://link.springer.com/article/10.1186/s40854-024-00702-7/tables/7`
- Repo URL: **未见作者公开研究仓库**

## 11. 一句话带走
**这篇最值得 desk 先复现的，不是“copula 很高级”，而是：把 alt-pairs 先改写成 BTC-reference spreads，再用条件误价带做进出场，确实比直接价差 z-score 更像一条 short-cycle 可活的完整 stat-arb 骨架。**
