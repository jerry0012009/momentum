# 别把 *Same Returns, Different Risks* 只读成“收益差不多”：对 short-cycle desk，更该先接的是「infrastructure shock volatility veto / size-down overlay」

- 时间：2026-04-13 01:56 UTC
- 类型：2026 working paper + code/data repo source audit
- 主题标签：overlay/regime/event-driven/infrastructure-vs-regulatory/shock-taxonomy/volatility-asymmetry/kill-switch/size-down/mean-reversion-veto/trend-book/binance/1m/3m/5m/15m/paper/repo/public-data
- 证据类型：论文证据 + repo 结构证据

- 主题类型：overlay
- 基础 alpha：**不是独立 raw alpha；它服务于现有 `1m/3m/5m/15m` raw alpha（trend / mean reversion / pairs / stat-arb / carry / funding / OFI），回答的是“同样都是坏消息，基础设施事故和监管打击之后，哪类事件更该立刻降仓/停机”**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha 不存在。** 这篇东西不是方向信号本体，而是一个 **event-type-aware risk overlay**：同样是负面事件，市场在**收益方向**上未必明显区分 infrastructure failure 和 regulatory enforcement，但在**风险/波动通道**上会明显区分，所以 desk 不该用同一种 post-event 风控模板去对待两者。

翻成人话：
- FTX / Terra / hack 这类“系统真的坏了”的事，和 SEC 起诉 / 国家禁令这类“规则变了”的事，
- 价格跌幅看起来不一定差很多；
- 但**后面的乱跳程度、滑点、爆仓链条、流动性塌缩风险**可能完全不是一个量级。
- 所以这篇 paper 最值得 desk 拿走的，不是“做多还是做空”，而是：
  **出现负面 shock 后，先问是哪一类 shock，再决定哪些 alpha 继续跑、哪些先 veto、仓位要砍多少。**

## 2. 这次看了什么

### 主来源（paper）
- **Author：** Murad Farzulla
- **Year：** 2026
- **Title：** *Same Returns, Different Risks: How Cryptocurrency Markets Process Infrastructure vs Regulatory Shocks*
- **Venue：** working paper / arXiv
- **Readable URL：** <https://arxiv.org/abs/2602.07046>
- **HTML URL：** <https://arxiv.org/html/2602.07046v2>
- **DOI：** paper 本体未见正式期刊 DOI；文中配套 data/code archive 见 repo/Zenodo
- **Repo URL：** <https://github.com/studiofarzulla/sentiment-without-structure>
- **Code/Data archive DOI：** <https://doi.org/10.5281/zenodo.18099609>

### 这篇 paper 最重要的读法
这篇 paper headline 很容易被读成：
- “基础设施冲击和监管冲击的收益差别不显著”；
- 那就好像没什么可用信息。

但对 short-cycle desk，这么读太浪费。

更值钱的读法是：

> **如果 return channel 区分不明显，但 variance channel 区分非常明显，那么该落地的不是新 directional alpha，而是 shock-type-aware overlay。**

也就是：
- raw alpha 继续用现有的 trend / MR / pairs / carry / OFI；
- 但 post-event 的 `trade on / trade off / gross scaler / book veto`，要按 shock type 改写。

## 3. 核心结论

### 3.1 论文本体的结论
作者用 2019--2025 年 **31 个事件**、覆盖 **BTC / ETH / SOL / ADA**，比较两类**负面事件**：
- **Infrastructure failures**：交易所故障、hack、崩盘、协议故障
- **Regulatory enforcement**：SEC 起诉、国家禁令、执法动作

在**累计异常收益（CAR）**层面，结果是：
- infrastructure negative：**平均 CAR = `-7.6%`**
- regulatory negative：**平均 CAR = `-11.1%`**
- 差值：**`+3.6 pp`，`p = 0.81`**

也就是说：
> **单看 return，分不出显著差异。**

### 3.2 但真正重要的是这句 companion result
这篇 paper 摘要里明确写了 companion variance analysis 的结论：
- **Infrastructure events 的 conditional variance impact 是 regulatory events 的 `5.7x`，`p = 0.0008`**。

这句话对 desk 的价值远大于 headline 本身。

翻译成交易语言就是：
- 两种坏消息都可能让你方向上受伤；
- 但 **infrastructure shock 更容易把你的 execution、滑点、强平链条、spread、盘口厚度一起打坏**；
- 所以它更像一个**必须提高优先级的 risk regime 切换信号**。

## 4. 关键数据点（这轮最值得记住的 4 个数）

1. **样本：** `31` 个事件，`2019--2025`，资产覆盖 `BTC / ETH / SOL / ADA`
2. **Infrastructure negative mean CAR：** `-7.6%`
3. **Regulatory negative mean CAR：** `-11.1%`
4. **Variance impact ratio（companion result）：** infrastructure ≈ regulatory 的 **`5.7x`**，`p = 0.0008`

这组数拼起来的意思不是“infra 事件更看空”，而是：

> **infra 事件更该让你先担心“还能不能好好交易”**。

## 5. 为什么这轮值得做它，而不是再补一条 raw alpha

先回答用户要求的那句内部问题：
**它为什么比继续补 raw alpha 更值得？**

因为这轮边际价值更高的缺口，不是“再多一条和现有 pairs / funding / stat-arb 很像的 alpha”，而是：

1. **现有 raw alpha 池已经够多，但缺统一 event-risk taxonomy**
   - 我们已经有不少 raw alpha；
   - 但“什么事件出现时，哪些 alpha 先别碰”这层还不够系统。

2. **这篇东西直接服务多个 alpha 家族**
   - mean reversion
   - pairs / stat-arb
   - carry / funding / basis
   - OFI / maker
   - trend / breakout

3. **它能很快做最小实验**
   - 不需要私有 tick；
   - 只要公开事件时间戳 + Binance OHLCV / funding / OI / spread proxy；
   - 就能先验证“不同事件类型下，现有 books 的 drawdown / RV / survival 曲线是不是不一样”。

所以它不是泛风险闲聊，而是**给现有 raw alpha 池补统一的 post-event 处置层**。

## 6. desk 化重写：真正该拿走的不是 headline，而是一张 shock-type 风控表

### 6.1 对不同 alpha 家族的直觉影响

#### A. mean reversion / pairs / stat-arb
这类书最怕的是：
- 相关性断裂
- spread 扩张后继续扩张
- 盘口变薄导致你“以为是回归、其实是掉坑”

所以在 **negative infrastructure shock** 后，第一反应不该是“跌多了可以捞”。
更合理的是：
- 先停新开仓，
- 等 realized vol / spread / book depth 恢复到阈值以内，
- 再恢复 fade / convergence 类策略。

#### B. carry / funding / basis
这类书在基础设施事故后也可能出现“看起来更肥”的 carry，
但那往往同时伴随：
- 资金费率极端
- 盘口恶化
- 清算瀑布
- 交易对手风险抬升

所以 infra shock 下不该把高 carry 直接当绿灯。

#### C. trend / breakout
trend 类不一定必须停，但也不该无脑照常：
- 方向可以继续做，
- 但 gross 要降，
- 且必须提高 execution / slippage / gap-risk 约束。

### 6.2 第一版 desk overlay 规则（建议）

下面这张表不是 paper 原文直接给的，是基于 paper 结论做的 **desk hypothesis**：

| 事件类型 | 0~12h | 12~48h | 优先 veto 的策略 | 可保留策略 |
|---|---|---|---|---|
| negative infrastructure | `gross = 0.25~0.50x`；暂停新开 fade/pairs/carry | 直到 `15m RV` 回落到 pre-event 的 `<= 2x` 再恢复 | MR / pairs / convergence / maker-tight-quote | trend / breakout / directional only（但降仓） |
| negative regulatory | `gross = 0.60~0.80x`；保留更高阈值 | `12~24h` 后可逐步恢复 | 高换手 MR / 薄盘口小币 | major-only trend / selective carry / slower pairs |

它回答的不是“做多还是做空”，而是：
> **shock 出现后，哪些书先关、哪些书只降仓、哪些还能继续跑。**

## 7. 可复刻的最小实验

### 7.1 研究假设
- **H1：** negative infrastructure 事件后的 `15m` realized vol / intrabar range / drawdown hazard，高于 negative regulatory 事件；
- **H2：** mean-reversion / pairs / carry 书在 infrastructure 事件后的 survival 明显更差；
- **H3：** trend / breakout 书不一定收益更高，但 survival 可能相对更好。

### 7.2 最小可复现实验口径
**数据源**
1. paper/repo 给出的事件清单与分类（public）
2. Binance public OHLCV（`1m/5m/15m`）
3. 若可得，再补 Binance public funding / OI / taker flow proxy

**公开性**
- 事件时间戳：公开新闻 / 监管公告 / repo data
- 市场数据：Binance 公共接口可得

**更新频率**
- 事件数据：低频、事件驱动
- K 线 / funding / OI：分钟级或更低延迟的公开更新

**最小实验**
1. 选两组事件：`infra_negative` vs `reg_negative`
2. 对每个事件对齐 `t0`
3. 观察窗口拆成：`0~6h`、`6~24h`、`24~72h`
4. 在每个窗口计算：
   - `15m RV`
   - high-low range / gap frequency
   - funding shock / OI shock（若可取）
   - 若接入现有策略：现有 raw alpha books 的 post-event PnL / max DD / stop-out ratio

### 7.3 第一版 go/no-go 判定
- 若 `infra_negative` 事件后 `15m RV_median >= 2x reg_negative`，则对 MR / pairs / carry 默认启用 veto
- 若某条策略在 `infra_negative` 事件后的 `24h max DD` 显著恶化，而在 `reg_negative` 没有同等恶化，则把这条策略标记为 **infra-fragile**
- 若 trend 书在 infra 事件后仍有正 survival，但滑点显著恶化，则只允许 `major-only + reduced gross`

## 8. 对当前 `1m / 3m / 5m / 15m` desk 的直接关系

### 它不是逐根 alpha，但它会改变这些 alpha 的 live 行为：
- `1m/3m`：主要影响 ultra-short MR / OFI / maker
- `5m`：影响 pairs / funding fade / fast trend continuation
- `15m`：影响 slower trend / carry / regime router

更具体地说：
- **1m/3m** 最该防 infrastructure shock 后的 execution 崩坏；
- **5m** 最该防 spread continue widening 还去做 fade；
- **15m** 最适合拿它做 gross scaler / live-shadow veto。

## 9. 风险与保留意见

- 这篇 paper 本体比较的是 **daily event-study CAR**，不是直接比较 `15m` 交易可执行性；我们做的是**从事件研究往短周期风控层迁移**。
- 31 个事件不算大样本，paper 自己也把结果定位为 hypothesis-generating。
- return 无显著差异，不代表所有资产/所有时段都一样；因此 desk 端必须再做 `1m/5m/15m` portability 检验。
- 事件分类也可能带主观性；第一版应该优先复用作者的公开分类，不要自己先引入太多二次分类噪音。

## 10. 下一步怎么测

1. 从 repo / paper 的负面事件清单里先抽 `infra_negative` 与 `reg_negative` 各 `5~8` 个事件。  
2. 用 Binance 公共 `15m` 数据先跑一个最小脚本，只比较 post-event 的 `RV / high-low range / gap frequency`。  
3. 再把当前 2~3 条代表性 raw alpha 接进去：
   - 1 条 mean reversion / pairs
   - 1 条 carry / funding
   - 1 条 trend / breakout
4. 输出一张统一表：`post-event PnL / max DD / stop-out ratio / realized vol multiplier / recommended gross scaler`。  
5. 若结果支持 infra 事件更脆弱，就把它正式写进 desk 的 `shock veto` 规则，而不是继续停留在 paper 摘要层。  

## 11. 来源

1. **Farzulla, Murad. (2026).** *Same Returns, Different Risks: How Cryptocurrency Markets Process Infrastructure vs Regulatory Shocks*. Working paper / arXiv.  
   - Readable URL: <https://arxiv.org/abs/2602.07046>  
   - HTML URL: <https://arxiv.org/html/2602.07046v2>

2. **studiofarzulla/sentiment-without-structure.** GitHub repository for code/data companion.  
   - Repo URL: <https://github.com/studiofarzulla/sentiment-without-structure>  
   - Archive DOI: <https://doi.org/10.5281/zenodo.18099609>

3. Repo page summary / paper abstract关键信息（本轮使用）：  
   - 事件样本：`31` events，`2019--2025`  
   - 资产：`BTC / ETH / SOL / ADA`  
   - Return result：infra `-7.6%` vs reg `-11.1%`，difference `+3.6 pp`，`p = 0.81`  
   - Companion variance result：infrastructure shocks produce `5.7x` larger volatility impacts，`p = 0.0008`
