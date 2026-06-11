# 别把这份 2026 cross-sectional crypto momentum 仓只读成“风险控制补丁”：对 short-cycle desk，更该先保留的是「横截面 relative-strength 排名」这条 base alpha，再把 `BTC realized vol / dispersion` 当成 veto 或 size-down 层

- 时间：2026-04-17 04:39 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `main1.tex` + `macro_state_test.py` + `coordination_overlay_test.py` + `build_implementation_feasibility_report.py`）
- 主题类型：raw alpha
- 基础 alpha：**对可交易 crypto 横截面做 relative-strength 排名，做多近期更强的一组、做空近期更弱的一组；repo 的 regime-aware 部分不是 alpha 本体，而是给这条横截面动量/relative-value 书加 `BTC realized vol` 或 cross-sectional dispersion 的 exposure scaling。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / momentum / relative-value / long-short / regime-aware / btc-realized-vol / dispersion / exposure-scaling / coordination-overlay / coingecko / yahoo-finance / coinmetrics / google-trends / repo / cost / risk / 1m / 3m / 5m / 15m
- 证据类型：GitHub repo + 内嵌 paper draft + 实现脚本 + 成本/可实现性说明

## 1. 这次看了什么
主材料是一个刚发布不久的 GitHub 仓：

- **Authors / Maintainer：** Olorato MacDonald Makgolo
- **Year：** 2026
- **Title：** *Regime-Aware Exposure Scaling in Cross-Sectional Relative Momentum Cryptocurrency Strategies*
- **Venue：** GitHub research repo / working-paper draft（`main1.tex`）
- **DOI：** N/A
- **Readable URL：** <https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies>
- **Repo URL：** <https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies>
- **Paper-draft URL：** <https://raw.githubusercontent.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies/main/main1.tex>

先把一句话说清楚：

> **这份东西的 base alpha，不是“vol overlay 很聪明”，而是最传统那条 cross-sectional relative momentum：横截面里最近更强的币，接下来更可能继续相对更强；最近更弱的币，更可能继续相对更弱。**

overlay 只是第二层：
- 当 **BTC realized vol 太高**、市场进入 stress regime 时，给这本 long-short 书 **降杠杆 / 降暴露**；
- 当 **cross-sectional dispersion 压扁**、大家一起同涨同跌时，也别把 relative-value 书当成独立 alpha 乱开大。

这正好符合我们这轮的优先级：
1. 先确认 **raw alpha 是什么**；
2. 再看 regime / filter / overlay 有没有 desk 价值。

## 2. 核心结论
### 2.1 一句话结论

> **最该 intake 的不是“BTC-vol overlay”本身，而是这份 repo 把一条很清楚的 base alpha 和两个很清楚的风险层拆开了：alpha 本体是 `cross-sectional relative momentum`，而 `BTC realized vol / dispersion` 更像 raw alpha 的 shared veto / size-down 模块。**

### 2.2 为什么我认为它值得进研究池
因为它比“泛泛讲 regime-aware”要具体得多：
- 有 **明确 alpha 本体**：横截面相对强弱排序；
- 有 **明确 overlay 变量**：BTC realized volatility、cross-sectional dispersion；
- 有 **明确实现摩擦意识**：代码里单独建了 turnover、long/short trade cost、short-leg frictions、funding carry cost 等成本块；
- 还有 **可实现性降级版**：从理论上的全横截面 long-short，退到 `long-only top quintile` 和 `long top quintile / short BTC-ETH` 两个更贴近现实的版本。

换成人话：

> **这不是“又一个看起来很聪明但落不了地的因子故事”，而是一份已经把“alpha 本体 / 风险层 / 成本层 / 可实现降级版”分拆得比较清楚的研究骨架。**

## 3. repo 里最值钱的 3 层结构

### 3.1 第一层：base alpha = 横截面 momentum / relative-value
repo 在 `main1.tex` 里把基础信号写得很直白：
- 对每个币算过去一段窗口的累计收益（代码默认 `k_lookback = 20`）；
- 在横截面里按这个 relative strength 排序；
- 强者分配更高权重，弱者分配更低或负权重；
- 组合收益来自 **币与币之间的相对强弱延续**，而不是单纯赌 BTC 大盘方向。

一句话理解：

> **它本质上是在做“买相对强、卖相对弱”的 crypto relative-value 书。**

这对我们 desk 很重要，因为最近几轮 digest 里虽然也有不少 cross-sectional / relative-value 题材，但很多更偏：
- loser-bounce
- pairs spread fade
- basis / funding carry
- event-driven lead-lag

而这份材料补的是另一块更基础的积木：

> **“plain vanilla 的横截面 continuation 到底还能不能做，以及该用什么 risk layer 才不会在 stress 段被一锅端。”**

### 3.2 第二层：overlay = BTC realized vol / dispersion，不是 alpha 本体
repo 最核心的研究问题其实不是“如何发明更好的 signal”，而是：
- **什么时候这本书容易死？**
- **死的时候，能不能提前缩表？**

它给出的答案有两类：

1. **BTC realized volatility overlay**
   - 当 BTC 波动显著走高，说明市场更像 panic / deleveraging / one-factor tape；
   - 这时 alt 间相对排序容易被大盘单一冲击淹没；
   - 所以应该给横截面 momentum 书降暴露。

2. **Cross-sectional dispersion overlay**
   - 当横截面分散度太低，说明“强弱差”本来就不够大；
   - relative-value 书这时天然没什么肉；
   - 所以不是继续加码，而是减仓甚至不做。

这也是我这轮最认同它的一点：

> **它没有把 overlay 伪装成新 alpha，而是老老实实承认：alpha 还是那条 alpha，overlay 只是决定“什么时候别把它当万能钥匙”。**

### 3.3 第三层：implementation downgrade，比纯论文口径更有用
repo 不是只停在理想 long-short。
它还专门加了：
- `long_only_top_quintile`
- `long_top_quintile_short_btc_eth`

也就是：
- 如果你不想全市场做空一堆山寨，可以只做多 top quintile；
- 或者只把 short leg 收缩到 **BTC/ETH** 这类流动性最好、最容易借/最容易上 perp 的对象上。

这非常 desk-friendly，因为现实里最难的常常不是“发现 alpha”，而是：
- short leg 交易摩擦太高；
- 小币借不到、滑点大、资金费率不稳定；
- 理论上的 market-neutral 组合，落地后变成执行灾难。

## 4. repo 给出的关键数字
### 4.1 paper draft headline
`main1.tex` 里给出的总表很值得记：

- **Baseline XSM：** annual return `21.7%`，annual vol `49.3%`，Sharpe `0.44`，max drawdown `-85.9%`
- **Regime-Aware XSM：** annual return `16.7%`，annual vol `32.8%`，Sharpe `0.51`，max drawdown `-66.4%`

这组数的正确读法不是“overlay 提高了收益”，而是：

> **overlay 明显更像 risk-shaping：收益少一点，但波动和回撤压得更多，结果 Sharpe 反而改善。**

repo 还在文稿里明确写了一个 stress 机制结论：
- 当 **Bitcoin realized volatility 超过历史 `80th percentile`** 时，momentum strength 与未来收益的交互项显著转负；
- 也就是说，**市场越乱，原本看起来顺的 cross-sectional continuation 越容易失灵。**

### 4.2 implementation feasibility：最贴近 desk 的部分
`build_implementation_feasibility_report.py` 里最有用的不是学术 headline，而是两个降级版：

#### A) long-only top-quintile
- **BTC scaling** 把 long-only absolute Sharpe 从 **`0.241 -> 0.294`**（full sample）
- post-2020 进一步从 **`0.447 -> 0.478`**
- 同一份报告还直接说：**dispersion scaling 在 long-only 版本里反而变差**

这很像 production 世界会发生的事：
- 当你的书天然带较强 market beta，
- 用 **BTC-vol 这种 market-level overlay** 往往比“横截面 dispersion”更对症。

#### B) long top quintile / short BTC-ETH
- full sample absolute Sharpe：**`-0.475 -> -0.458`**（BTC scaling 后仍差，但有改善）
- post-2020 absolute Sharpe：**`-0.259 -> -0.111`**
- overlay delta active Sharpe 还能到：**`0.394`（full sample）/ `0.574`（post-2020）**

这说明一件很朴素的事：

> **把 short leg 收缩到 BTC/ETH 确实更可实现，但它还不是“已经很好”的完整策略；它更像一个工程上能站住脚的过渡版本。**

### 4.3 成本意识：这份 repo 没装傻
`macro_state_test.py` 里直接把成本拆出来了：
- `long_trade_cost_bps = 10`
- `short_trade_cost_bps = 20`
- 还单列 `funding_carry_cost`
- 并做 short-trade-cost sensitivity / zero-fee comparison / turnover summary

这比很多“只讲 Sharpe 不讲怎么成交”的 repo 强不少。
但它也很诚实：
- 报告自己写了，**短腿版本的 funding / borrow scarcity / margin frictions 仍不完整**；
- 所以不能把当前结果吹成 production-ready。

## 5. 对我们 desk 的正确读法
### 5.1 这轮为什么我仍把它归到 `raw alpha`
因为用户这轮明确要求：
- 先回答 **base alpha 是什么**；
- 若答不清，只能降级为 `filter / regime / overlay`。

而这份 repo 的 base alpha 是清楚的：

> **横截面 relative-strength continuation。**

所以它不是纯 overlay 题。
只是它最有 desk 价值的部分，不是“继续信仰这条 alpha 永远有效”，而是：
- 把这条 alpha 和它的死法拆开；
- 把能共用到别的书上的风险层拆出来。

### 5.2 和当前 short-cycle desk 的关系
repo 本身主频还是 **daily / weekly research frame**。
所以不能硬说它就是 `5m` production 信号。
更合理的映射是：

- **slow alpha layer：** 谁强谁弱的横截面排序
- **short-cycle execution layer：** 在 `15m / 5m / 3m / 1m` 上做入场切片、冲击控制、盘口 veto
- **shared regime layer：** BTC realized vol、cross-sectional dispersion、market-wide liquidation stress

换句话说：

> **它最适合进入我们素材池的身份，不是“15m 直接追涨模型”，而是“cross-sectional continuation 母板 + 可共用的 market-stress veto 模块”。**

### 5.3 它服务于哪些 raw alpha
这份 repo 的 overlay 不只服务它自己的 XSM。
如果做得对，它至少还能服务：

1. **cross-sectional momentum / continuation**
2. **loser-bounce / winner-cooldown** 一类横截面反转书
3. **pairs / stat-arb / basis** 这种依赖相对价差而怕单因子暴冲的书

也就是说，`BTC vol / dispersion` 更像 **shared gate**，但之所以值得 intake，是因为它挂靠在一条足够清楚的 raw alpha 上。

## 6. 策略拆解（必填）
- **方向属性：** cross-sectional / relative-value / long-short（可降级为 long-only 或 long-alt / short BTC-ETH）
- **基础 alpha：** 最近相对更强的币继续相对更强，最近相对更弱的币继续相对更弱
- **regime：** BTC realized vol 高位、市场一体化上升、cross-sectional dispersion 收缩时，alpha 失效率上升
- **filter / veto：** BTC realized vol percentile、cross-sectional dispersion、可能再叠加我们自己已有的 funding / liquidation stress 状态
- **risk / sizing / execution overlay：** exposure scaling、long/short legs 分开成本建模、short-leg 收缩到 BTC/ETH、child-order execution

## 7. 可复刻的最小实验
### 7.1 数据源、公开性、更新频率
如果把这份 repo desk 化到短周期，最小实验其实不需要 top-500 全宇宙：

- **价格数据：** Binance USDⓈ-M / Spot public klines（公开可得）
- **更新频率：** `15m` 起步，必要时细化到 `5m/1m`
- **额外状态变量：**
  - BTC realized vol：用 Binance public kline 就能自己算
  - cross-sectional dispersion：同一批币横截面收益分散度自己算
- **最小资产池：** `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/LTC/AVAX` 这类 liquid majors 就够先做 first verdict

### 7.2 最小可复现实验口径
我建议第一版不要直接追求“大而全回测”，而是先做这 3 个极小实验：

#### 实验 A：15m 横截面 continuation baseline
- 每 `15m` 更新一次信号，但只在每 `4h` 或 `1d` 重排一次横截面，避免 turnover 爆炸
- lookback 可先试：`1d / 3d / 5d`
- 做法：long top `20%`，short bottom `20%`，或 long top `20%` / short BTC-ETH basket
- 先看 gross、再上成本梯度

#### 实验 B：BTC realized-vol gate on/off
- 用 BTC 最近 `96` 根 `15m`（约 1d）或 `288` 根 `5m`（约 1d）算 realized vol
- 当 vol percentile 进入历史高位区间时，把 gross exposure 从 `1.0x` 降到 `0.5x` 或 `0x`
- 对照：不加 gate 的同一条横截面 alpha

#### 实验 C：dispersion gate on/off
- 横截面里计算最近 `N` 根收益标准差 / MAD / top-bottom spread
- 当 dispersion 太低时，不做或减半仓
- 看它究竟是改善 Sharpe，还是只是把收益一起砍掉

### 7.3 下一步怎么测
这轮最关键，不是继续读 paper，而是尽快做以下 5 个 A/B：

1. **`1d/3d/5d` lookback 对 `15m` 执行的 rank monotonicity**
   - 先确认 liquid-major perp 上还有没有“强者续强 / 弱者续弱”的基本排序斜率。

2. **`long-short full basket` vs `long top / short BTC-ETH`**
   - 看 short leg 收缩后，是否虽然收益变低，但 net Sharpe / implementability 反而更好。

3. **BTC vol gate on/off**
   - 这是 repo 最像能快速迁到 desk 的部分，优先级应高于再抠信号花样。

4. **dispersion gate on/off**
   - 如果它只在日频 broad universe 上有用、在 liquid-major 短周期上没用，就不要神化它。

5. **成本敏感性分腿看**
   - long leg taker / maker、short leg taker / maker、funding / borrow proxy 分开看，别只报一个总成本数。

## 8. 我对这份材料的最终判断
### 8.1 值得保留的部分
我会把下面两块都保留进素材池：

1. **base alpha 母板：cross-sectional relative momentum / continuation**
2. **shared overlay 候选：BTC realized vol gate / dispersion gate**

### 8.2 不该过度乐观的部分
但也要说清楚它现在还不是“可直接落地完整策略”：
- 样本主框架偏 daily，不是原生 short-cycle；
- broad-universe 研究结果不等于 liquid-major perp 现在还活；
- repo 自己都承认短腿 funding / borrow / margin friction 还没补齐；
- overlay 提升更多体现在 **回撤压缩 / 风险整形**，不等于 alpha 本体更强。

### 8.3 一句话 verdict

> **这份 repo 值得 intake，不是因为它证明了“BTC-vol overlay 无敌”，而是因为它把一条还能继续深挖的 raw alpha（横截面 relative-strength）和两个很适合 desk 共用的 veto / size-down 模块（BTC vol、dispersion）拆得足够清楚。**

## 9. 来源
1. Makgolo, O. M. (2026). *Regime-Aware Exposure Scaling in Cross-Sectional Relative Momentum Cryptocurrency Strategies*.
   - Repo: <https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies>
   - Draft source: <https://raw.githubusercontent.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies/main/main1.tex>
2. Repo source files reviewed:
   - `README.md`
   - `macro_state_test.py`
   - `coordination_overlay_test.py`
   - `build_implementation_feasibility_report.py`
