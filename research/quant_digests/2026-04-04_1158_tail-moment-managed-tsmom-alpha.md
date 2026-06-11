# 别把这篇 2021 IRFA 论文只读成“趋势也会反转”的风险提醒：对 short-cycle desk，更该先测的是「TSM trend-state × UPM/LPM tail quadrant router」这条完整 raw alpha

- 时间：2026-04-04 11:58 UTC
- 类型：2021 *International Review of Financial Analysis* 接收稿全文 PDF（University of Reading accepted manuscript）+ Crossref / OpenAlex metadata
- 主题类型：raw alpha
- 基础 alpha：**先用过去 `J` 根累计收益的符号定义 time-series momentum 方向，再用近 `n` 根正收益平方和/负收益平方和构成的 `UPM/LPM` 四象限状态机，决定该 bar 是继续顺势、直接平仓，还是反手做 reversal。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/time-series-momentum/tail-risk/upper-partial-moment/lower-partial-moment/quadrant-router/reversal-aware/vol-targeting/signal-routing/single-asset/futures/crypto/15m/5m/3m/1m/paper/public-data/cost/risk
- 证据类型：论文全文证据 + 元数据 grounding

## 1. 这次为什么选它
先按这轮要求回答一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：base alpha 很清楚，就是 time-series momentum / trend-following。**
>
> 它不是单纯 filter，也不是纯 overlay；论文真正给的，是一条**可独立运行的“趋势本体 + 尾部反转路由器”完整策略**。

这轮选它有三个原因：

1. `docs/RECENT_PAPER_SEEDS.md` 里它本来就是主线候选，而且目前 `research/quant_digests/INDEX.md` 里还没有同题 digest；
2. 当前学习进展里，`trend/choppy gate`、`risk-on/off gate` 已经知道“有用但别再围绕 baseline 炼丹”，下一步更值得补的是**把趋势本体和 reversal 管理揉成同一条 raw alpha**；
3. 最近 intake 已经补了很多 carry / pairs / maker / microstructure / mean-reversion，新研究池里并不缺“再来一个单独 filter”，反而更缺这种：

> **趋势信号本体清楚、又明确告诉你何时该 flat、何时该 reverse 的可复现策略壳。**

所以这篇 paper 对当前 desk 的价值，不是“又一篇说 tail risk 很重要”，而是：

> **它把 trend raw alpha 从二元 `long/short`，升级成了一个四状态 action map。**

## 2. 先把 base alpha 讲清楚
这条策略的原始骨架非常简单：

1. 看过去 `J` 根累计收益；
2. 若为正，就做多；若为负，就做空；
3. 再按 ex-ante 波动率做 volatility scaling。

也就是经典 TSM：

- `sign(sum_{j=0}^{J-1} r_{t-j})) > 0` → long
- `< 0` → short

论文没有停在这里，而是继续问：

> **同样都是“过去 J 根是上涨趋势”，下一根真的都该继续追吗？**

作者的回答是：不该只看均值，还该看最近更短窗口里，**正收益平方和**和**负收益平方和**的非对称结构。

他们定义：

- `UPM` = 最近 `n` 根里正收益平方和的平均值
- `LPM` = 最近 `n` 根里负收益平方和的平均值

然后用 `UPM/LPM` 的联合分布把当前 bar 放进四个区域，决定：

- 继续顺势
- 平仓观望
- 直接反手

这就让它不再只是“趋势 + 一个 veto”，而是一条完整 raw alpha：

> **方向来源是 trend state，交易动作来源是 trend state × tail-moment quadrant。**

## 3. 论文真正做了什么

### 3.1 数据与 baseline
作者研究的是 **31 个中国商品期货合约**，主样本大致覆盖：

- `2008-01 ~ 2019-12`
- 再单独补做 `2019-12 ~ 2020-05` 的 COVID crash robustness

baseline TSM 的关键口径：

- lookback `J ∈ {20, 30, 40, 60, 90, 120, 250}` trading days
- 默认展示重点是 `J = 30`
- holding period：`1` day
- volatility target：`40% annualized`
- ex-ante volatility：EWMA std

这里先记两个硬点：

1. 原始 TSM 在样本里本来就是有效的，不是“无效 baseline 硬救”；
2. 他们优化的不是仓位分配细节，而是**long/short/flat/reverse 的动作路由**。

### 3.2 UPM / LPM 怎么定义
论文用最近 `5` 个交易日的 daily return 来算 partial moments：

- `UPM_t = (1/n) * Σ r^2 * I(r>0)`
- `LPM_t = (1/n) * Σ r^2 * I(r<0)`
- 这里 `n = 5`

直觉非常好懂：

- `UPM` 高 = 最近短窗里“上涨冲击”很强
- `LPM` 高 = 最近短窗里“下跌冲击”很强

对趋势交易者来说，这两个量不是对称噪音，而是：

- 上涨趋势里，`LPM` 突然抬高，可能意味着 **slump risk**；
- 下跌趋势里，`UPM` 突然抬高，可能意味着 **rebound risk**。

### 3.3 四象限状态机：这条 raw alpha 的核心
作者把 `(UPM, LPM)` 放在二维坐标里，再用历史联合分布的递归 `(80%, 80%)` 分位点作为参考点，把平面切成 4 个区：

- **Region 1**：`UPM` 高，`LPM` 高
- **Region 2**：`UPM` 低，`LPM` 高
- **Region 3**：`UPM` 低，`LPM` 低
- **Region 4**：`UPM` 高，`LPM` 低

其中：

- **Region 3**：最像“正常趋势”，继续做原始 TSM；
- **Region 1**：上下两边 tail 都很高，最安全的做法是直接 flat；
- **Region 2 / 4**：是最值钱的地方，因为它们不是简单 veto，而是**方向路由**。

作者设计了两种 MTSM 版本：

### 3.4 MTSM-S1 与 MTSM-S2 的动作表

#### MTSM-S1
- Region 1：`flat`
- Region 2：`reverse`
- Region 3：`follow momentum`
- Region 4：`reverse`

更具体地说：
- 原本该 long 的，在 Region 2 改成 short；
- 原本该 short 的，在 Region 4 改成 long。

#### MTSM-S2
- Region 1：`flat`
- Region 2：与 S1 相反方向路由
- Region 3：`follow momentum`
- Region 4：与 S1 相反方向路由

这不是花哨的文字游戏，而是很直接的交易含义：

> **当短窗 tail structure 告诉你“这更像上行趋势里的下砸”或“下行趋势里的反弹”时，你不是只减仓，而是可以直接切换到反手书。**

这正是我把它定性成 `raw alpha` 而不是 `filter` 的原因。

## 4. 论文里的关键结果

### 4.1 原始 TSM 本来就有 edge
在 `J = 30`、1-day hold 的 baseline 下：

- **2008-2012**：TSM 年化收益约 `26.29%`，Sharpe `1.10`，最大回撤 `28.71%`
- **2013-2019**：TSM 年化收益约 `15.93%`，Sharpe `1.04`，最大回撤 `18.73%`

也就是说，这不是“烂策略被 filter 救活”，而是：

> **本来就有效的 trend alpha，被 partial-moment router 做了 drawdown 与 reversal 管理。**

### 4.2 第一阶段更适合 S1
在 **2008-2012** 子样本：

- `TSM Sharpe = 1.10`
- `MTSM-S1 Sharpe = 1.25`
- `TSM MDD = 28.71%`
- `MTSM-S1 MDD = 25.62%`

也就是说：

- 收益略降（`26.29% → 25.11%`）
- 但风险收益比更好
- 最大回撤更浅

这更像 desk 会接受的 trade-off：

> **不是拼命榨收益，而是让 trend alpha 在 reversal 段少被打穿。**

### 4.3 第二阶段更适合 S2
在 **2013-2019** 子样本：

- `TSM Sharpe = 1.04`
- `MTSM-S2 Sharpe = 1.25`
- `TSM MDD = 18.73%`
- `MTSM-S2 MDD = 11.13%`

这个结果更漂亮：

- 年化收益只从 `15.93%` 轻微降到 `14.30%`
- Sharpe 提升约 `20%`
- MDD 直接从 `18.73%` 压到 `11.13%`

这说明 partial-moment router 不只是“少交易一点”，而是真的更会避开 reversal 伤害。

### 4.4 不只是某一个 lookback 偶然有效
他们把 `J` 从 `20` 一直测到 `250` 天，结果是：

- 第一子样本里，`MTSM-S1` 在大多数 lookback 上都优于原始 TSM；
- 第二子样本里，`MTSM-S2` 在大多数 lookback 上都优于原始 TSM；
- 作者总结为：**Sharpe 平均大约提升 20% 左右**。

这点对我们 desk 很重要，因为它更像一个**结构性动作层**，不是只依赖某个神奇参数。

### 4.5 极端行情里更像 drawdown router
COVID crash 那段（`2019-12 ~ 2020-05`）里，`J=30` 的结果：

- `TSM Sharpe = 1.39`
- `MTSM-S2 Sharpe = 1.79`
- `TSM MDD = 8.51%`
- `MTSM-S2 MDD = 4.81%`

也就是：

> **大波动段里，它更像“趋势单什么时候该先别硬扛”的系统化回答。**

## 5. 这条主题和当前 desk 的直接关系

### 5.1 为什么它比再补一个独立 filter 更值
当前项目的学习与 backlog 已经很清楚：

- 趋势家族：已经学过 `multi_tf_momentum`、`ema_donchian_breakout`；
- gate 家族：`trend/choppy`、`risk-on/off` 都做过 first baseline；
- 当前缺的不是“再证一次 filter 有用”，而是：

> **有没有一条更像 production 组件的趋势原型，能把 entry、本体、reversal 管理、flat 机制一次讲清。**

这篇 paper 刚好补的是这一块。

### 5.2 它服务的是 short-cycle 趋势家族，不是泛用 overlay
这条线最适合服务：

- trend / momentum
- breakout continuation
- open-drive / impulse continuation
- 更慢一些的 intraday carry 延续腿

不太适合直接服务：

- maker spread capture
- pure pairs/stat-arb
- strict market-neutral carry

因为它的核心逻辑是：

> **判断原有趋势状态是否正在进入“该 flat / 该 reverse”的尾部区。**

所以它首先是趋势 raw alpha 家族的成员，而不是跨家族共享 filter。

## 5.5 策略拆解（必填）
- 方向属性：trend / momentum / reversal-aware routing
- 基础 alpha：**rolling cumulative-return sign 的 TSM**
- regime：`UPM/LPM` 四象限
- filter / veto：Region 1 直接 `flat`
- 反手条件：Region 2 / 4 触发时，按 S1 或 S2 规则 `reverse`
- sizing / risk：EWMA vol scaling；可进一步叠加 intraday vol target / cap
- cost / execution：按 next-bar open 或 next-bar VWAP 执行；必须显式扣手续费、滑点、funding

## 6. 怎么把它映射到 `1m / 3m / 5m / 15m`

### 6.1 不要机械照抄“30天 + 5天”
这篇 paper 的 daily 参数不能生搬到 intraday。真正该保留的是**结构比例**：

- 趋势时钟 `J`
- tail-moment 时钟 `n`
- 二者比例大约是 `6:1`

也就是说，短周期移植时要保**相对层次**，不是保天数。

### 6.2 `15m` 第一版最自然
我会优先从 `15m` 开始做，因为它最接近“有趋势记忆，又没快到全是噪音”的层级。

第一版参数网格可以直接这样开：

- trend lookback `J = 24 / 32 / 48` bars（约 `6h / 8h / 12h`）
- tail-moment window `n = 4 / 6 / 8` bars（约 `1h / 1.5h / 2h`）
- percentile cutoff：`(75,75) / (80,80) / (85,85)`
- hold：`1 / 2 / 3` bars

这样保住的其实就是 paper 的骨架：

> **慢时钟定趋势，快时钟抓 reversal 风险。**

### 6.3 `5m` 可以做，但更像第二阶段
`5m` 更适合在 `15m` 先确认结构后再下探。

第一版可以用：

- `J = 72 / 96 / 144`
- `n = 12 / 16 / 24`
- hold `1 / 2 / 3` bars

原因很简单：如果你在 `5m` 上还用很短的 `J/n`，那测出来的就不再是“趋势 × reversal router”，而更像噪音均值回复。

### 6.4 `1m / 3m` 当前不要直接当主战场
`1m / 3m` 不是不能做，而是更适合：

- 当 `15m`/`5m` router 已确认有效后，作为更细执行层；
- 或者只拿来做 `entry refinement / better fill / faster exit`；
- 不建议现在直接把它当第一版主 alpha 时钟。

## 7. 最小实验怎么做

### 7.1 数据口径
优先用公开可得、且和实盘更接近的 perp 数据：

- Binance USDⓈ-M / Bybit / Hyperliquid 公共 `5m/15m` K 线
- 先从 `BTCUSDT / ETHUSDT / SOLUSDT` 开始
- 如有条件，再补 funding 与 taker imbalance 只做诊断，不先混入主信号

### 7.2 先做 4 个版本，不要一上来就炼丹
对每个标的、每个 timeframe，同时跑：

1. **Baseline TSM**：只按 `sign(rolling return)` 顺势
2. **Flat-only router**：Region 1 flat，其余仍 follow trend
3. **MTSM-S1 port**
4. **MTSM-S2 port**

这样能先回答最关键的问题：

> **crypto intraday 里，真正有价值的是 flat，还是 reverse？是 S1 型，还是 S2 型？**

### 7.3 先看 6 个指标
第一轮不要急着只盯 Sharpe，至少看：

- net return
- Sharpe
- max drawdown
- turnover
- average hold time
- `R2/R4` 触发后下一段是否真的更容易逆 base trend

最后一个尤其重要，因为它直接衡量：

> **四象限 router 到底有没有抓到“趋势要出问题”的时刻。**

### 7.4 成本口径必须诚实
建议 round-trip 至少跑：

- `4 bps`
- `8 bps`
- `12 bps`

若在更快周期，还应补：

- next-open fill
- next-VWAP fill
- 半个 spread haircut

不然很容易把“减少回撤”误读成“可交易 alpha”。

### 7.5 第一版通过条件
我会把第一版通过条件写得很克制：

1. 相比 baseline TSM，**net Sharpe 提升 ≥ 10%**；或
2. **MDD 收窄 ≥ 15%**，且 net return 没有明显塌陷；或
3. `R2/R4` 事件段的 reversal 命中明显高于无条件基线。

只要满足其中一条，这条线就值得进入下一轮更细复现。

## 8. 风险与保留意见

### 8.1 最大风险：S1/S2 的样本后见之明
这篇 paper 最值得抄的地方，也是最该警惕的地方：

- `2008-2012` 更像 `S1`
- `2013-2019` 更像 `S2`

这说明：

> **router 自己也可能有 regime drift。**

如果在 crypto 上直接事后挑“哪个版本更好”，很容易过拟合。

所以 desk 化时，必须：

- walk-forward 选 S1 / S2 / flat-only
- 或者再做一个更小的 meta-rule 决定当前使用哪个 router

### 8.2 商品日频到 crypto intraday 不是一键迁移
原论文是：

- 中国商品期货
- 日频
- 1-day hold

而我们要的是：

- crypto perp
- `5m / 15m`
- 更高成本、更快反应、更强噪音

所以不能把论文里的数值结论直接当 production truth，只能把它当：

> **非常清晰、且适合做最小实验的结构模板。**

### 8.3 `(80,80)` 不一定是 crypto 的最优切点
这类联合分位阈值在 crypto 上可能：

- 太稀，导致触发太少；
- 或太密，导致本来只是正常波动也被判成 reversal 区。

所以第一轮最好把 `(75,75)/(80,80)/(85,85)` 一起测，而不是盲抄。

## 9. 我对这条材料的结论

### 9.1 值得 intake 吗？
**值得，而且我会把它归到 raw alpha 候选，而不是 filter 候选。**

### 9.2 它最准确的 desk 定位是什么？
> **一条“趋势本体 + reversal router”合体的 raw alpha 壳。**

它最适合补进我们当前的：

- trend / breakout continuation 素材池
- 以及趋势策略的 `flat/reverse` 风险管理组件库

### 9.3 现在就能直接上 production 吗？
**不能。**

但它已经足够清楚，值得立刻做最小复现，因为它回答的是一个很实战的问题：

> **趋势单不是只问“追不追”，还要问“什么时候先别追、甚至该反手”。**

## 10. 下一步怎么测
1. **先在 `BTC/ETH/SOL` 的 `15m` 上做 port**：`J=24/32/48`，`n=4/6/8`，hold `1/2/3` bars。
2. **四版本并跑**：baseline / flat-only / S1 / S2。
3. **先只测方向层，不混别的 gate**：不要一上来就叠 funding、OI、EMA、ADX。
4. **若 `15m` 有结构性改善，再下探到 `5m`**。
5. **若 S1/S2 都不稳，但 flat-only 有用**，就把它降级为 trend family 的 reversal veto，而不是硬保 raw alpha 身份。

## 11. 来源
1. **Liu, Z., Lu, S., & Wang, S. (2021). _Asymmetry, tail risk and time series momentum_. International Review of Financial Analysis, 78, 101938.**
   - Authors / Year / Title / Venue：Zhenya Liu, Shanglin Lu, Shixuan Wang / 2021 / *Asymmetry, tail risk and time series momentum* / *International Review of Financial Analysis*
   - DOI：<https://doi.org/10.1016/j.irfa.2021.101938>
   - Readable URL：<https://www.sciencedirect.com/science/article/pii/S1057521921002458>
   - Accepted-manuscript landing page：<https://centaur.reading.ac.uk/100824/>
   - Accepted-manuscript PDF：<https://centaur.reading.ac.uk/100824/1/FINANA-D-21-00329-R1.pdf>
   - Repo URL：N/A

2. **Crossref metadata**
   - URL：<https://api.crossref.org/works/10.1016/j.irfa.2021.101938>

3. **OpenAlex metadata**
   - URL：<https://api.openalex.org/works/W3209757220>

## 12. 文件与页面
- Markdown：`research/quant_digests/2026-04-04_1158_tail-moment-managed-tsmom-alpha.md`
- 预计页面：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-04_1158_tail-moment-managed-tsmom-alpha.html`
