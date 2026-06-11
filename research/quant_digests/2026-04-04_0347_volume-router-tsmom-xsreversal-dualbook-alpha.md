# 别把这份今天刚创建的 2026 新 repo 只读成 4H 作业：对 short-cycle desk，更该先测的是「vol-z 路由的 TSMOM / XS reversal 双书」完整 raw alpha

- 时间：2026-04-04 03:47 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `crypto-stat-arb.py`）+ Crossref metadata grounding
- 主题类型：raw alpha
- 基础 alpha：**不是成交量本身，而是两个可独立交易的 raw alpha——高参与度时做 own-past continuation（time-series momentum），低参与度/弱参与度时做 loser-minus-winner 的 cross-sectional reversal；`vol_z` 只负责在两本书之间路由与缩放。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/cross-sectional/mean-reversion/relative-value/volume-router/regime-switch/dual-book/sharpe-weighting/binance-us/4h/crypto/15m/5m/3m/1m/repo/public-data/cost/risk
- 证据类型：仓库工程证据 + 文献地基

## 1. 这次看了什么
先回答这轮最关键的一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：base alpha 不是 volume 本身，而是两条 raw alpha——time-series momentum 与 cross-sectional reversal。`volume z-score` 只是决定当前更该放大哪一条、抑制哪一条。**

本次主材料是 **Parnell Thrower (2026)** 今天刚创建并更新的 GitHub 仓库 **`PThrower/crypto-start-arb`**。repo 把 15 个主流币放到同一框架里，给出一条完整双引擎壳：
- 一本书做 **time-series momentum**：看单币近期表现是否显著强于自己的长期基线；
- 一本书做 **cross-sectional reversal**：看横截面里最近 24h 的赢家/输家，做 loser-vs-winner 回归；
- 再用 **成交量 z-score** 给这两本书做切换/缩放；
- 最后再用 **Sharpe-weighting** 做币级与策略级组合。

这轮值得写，不是因为它“发明了新理论”，而是因为它正好补上了我们最近 intake 里更缺的那层：

1. **不是 breakout / retest / 单一结构信号；**
2. **不是又一篇 pairs / cointegration 主题；**
3. **而是一条能同时服务 trend 与 reversal、还能直接拆出 `entry/exit/sizing/risk/cost` 的完整 raw alpha 壳。**

## 2. 核心结论（先给 desk 可执行的信息）
### 2.1 一句话核心结论

> **这份 repo 最值钱的，不是“4H 跑出 2.10 Sharpe”本身，而是它提醒我们：对短周期 desk，可以把 `volume z-score` 从普通 confirmation 升级成“alpha 路由器”——高参与度优先跑 continuation，弱参与度优先跑 reversal。**

### 2.2 一句话证明方式

> **README 给了完整绩效面板，源码又暴露了真正的实现细节；两者合起来后，最适合 desk 偷走的不是 4H 参数，而是 `vol_z router + dual-book shell` 这个结构。**

### 2.3 这份 repo 直接给出的关键数字
- **Momentum sleeve Sharpe：1.50**
- **Reversal sleeve Sharpe：3.68**
- **Combined Sharpe：2.10**
- **Combined max drawdown：-5.07%**
- **Beta vs BTC：0.011**
- **Annual trading cost（repo 口径）：0.16%**

### 2.4 这条线为什么值得进研究池
1. **它是完整策略，不只是“有信号、没壳子”。**
   - signal：TSMOM + XS reversal
   - regime/router：volume z-score
   - sizing：Sharpe-weighting
   - cost：turnover 扣减
   - portfolio：双书组合
2. **它天然可迁移到 `15m/5m/3m/1m`。**
   - 因为它用的都是公开可得数据：价格与成交量；
   - 不依赖难拿的私有订单流或低频宏观外部数据。
3. **它正好补当前 desk 的素材池缺口。**
   - 最近 intake 里 pairs / stat-arb / cross-venue 已经很多；
   - 这条线一次补了 **single-name continuation** 和 **cross-sectional loser-bounce** 两个 raw alpha 家族。

## 3. 真正值得 desk 偷的，不是 README 口号，而是“路由器读法”
repo README 的文字版叙述是：
- momentum 在 **high-volume** 时更该跑；
- reversal 在 **low-volume** 时更该跑。

但源码里的实现其实更细，也更值得审：

```python
volume_filtered_momentum = np.tanh(volume_signal) * momentum
volume_filtered_reversal = np.tanh(volume_signal) * -1 * reversal
```

这说明它并不是“硬门槛二选一”那么简单，而是：
- 用 `tanh(vol_z)` 做**连续缩放**，不是只开/只关；
- 还带有**符号翻转**效应，因此当 `vol_z` 走到负区间时，策略行为会和 README 的自然语言描述出现偏差；
- 也就是说，**直接抄 README 容易，直接照源码也未必最干净**。

对我们 desk 来说，真正有价值的不是争论 repo 作者原意，而是把这里面更“desk 化”的部分提炼出来：

> **把 volume 从“确认信号”升级成 “router / regime selector”。**

也就是：
- **vol_z 高**：优先放行 continuation / TSMOM；
- **vol_z 低或偏冷**：优先放行 cross-sectional reversal；
- 不需要在同一根 bar 上强行让两条腿同时开火。

这比“volume 只是加个过滤条件”更强，因为它直接回答了：

> **同一套价格信号，在什么参与度环境里更像 continuation，什么环境里更像 mean reversion？**

## 4. 为什么它和当前学习进展直接相关
结合当前项目文档，这轮选它比继续补一个普通 filter 更合理：

- `RESEARCH_AUTOMATION_BRIEF.md` 当前第一优先级是 **raw alpha / 可直接落地完整策略**；
- 最近 digest 已经连续 intake 了大量 **pairs / stat-arb / carry / cross-venue**；
- 而这条线能一次补两个更基础、更通用的 alpha 家族：
  - **trend / momentum**
  - **cross-sectional / short-term reversal**

翻成人话：

> **这轮不是再给已有 pairs 骨架加个小滤镜，而是补一条“更适合作为 desk 基础积木”的双书 raw alpha。**

## 4.5 策略拆解（必填）
- 方向属性：trend / momentum + cross-sectional reversal / relative-value
- 基础 alpha：
  - **书 A：** 单币 own-past continuation（近期表现显著强于自身长期基线时顺势）
  - **书 B：** 横截面 loser rebound / winner give-back（短窗赢家回吐、输家反弹）
- regime / router：`volume z-score` 决定当前更偏向 A 还是 B
- filter / veto：
  - `vol_z` 分层；
  - universe 流动性白名单；
  - BTC beta 过高时降 gross；
  - 过度拥挤/过高 turnover 时停机
- risk / sizing / execution overlay：
  - 每本书内部做 inverse-vol 或 rank-normalized sizing；
  - 两本书外层再做 book-level risk budget；
  - 成本前置，先过 `bps hurdle` 再谈扩容

## 5. desk 化后的最小可复现实验（面向 `15m/5m/3m/1m`）
这轮最重要的不是复现 repo 的 4H 数字，而是把它压成一版 **short-cycle first verdict**。

### 5.1 第一版先这样定义
#### Universe
- `20~30` 个高流动 USDT perp（先 majors + 次主流，不要一上来全市场）

#### Router
- `vol_z = zscore(volume_short / volume_long)`
- 第一版先不要连续 `tanh`，直接做更干净的**分桶路由**：
  - `vol_z > +0.5`：只开 **TSMOM book**
  - `vol_z < -0.5`：只开 **XS reversal book**
  - 中间区间：默认不开，或只保留轻仓

#### Book A：TSMOM / continuation
- 信号：
  - `ts_z = (ret_short - ret_long_mean) / ret_long_std`
  - 第一版 desk 化可先简化成：`24h return` vs `30d rolling return mean/std`
- entry：`ts_z > z_entry` 做多，`ts_z < -z_entry` 做空
- exit：
  - `ts_z` 回到中性区；或
  - 固定 time-stop `4/8/12` bars；或
  - 方向反转直接平

#### Book B：XS reversal
- 信号：
  - 对横截面过去 `8h/24h` 收益做排序
  - long bottom quantile / short top quantile
- entry：每个调仓点重排一次
- exit：持有 `4/8/16` bars 或下一次换仓点平掉

#### Sizing / Risk / Cost
- 书内：equal-risk / inverse-vol
- 书间：总 gross 先固定 `1.0`，每书上限 `0.5`
- 单名上限：`5%~10%`
- 成本：先固定跑 `4 / 8 / 12 bps` round-trip ladder
- 风险：记录 BTC beta、净敞口、turnover、最差日 PnL

### 5.2 第一轮先看 6 个指标
1. `post-cost bps/bar`
2. `book A / book B` 各自贡献
3. `router` 触发占比（有多少 bar 真在高量/低量区）
4. `AvgTurnover`
5. `BTC beta`
6. `positive day ratio`

### 5.3 第一轮最值得优先测的 3 组对照
1. **只做 TSMOM** vs **只做 XS reversal** vs **router 双书**
2. **连续 `tanh` 缩放** vs **硬阈值分桶路由**
3. **15m 主线** vs **5m 压缩版**

## 6. 这轮最关键的“下一步怎么测”
1. **先把 README 叙述与源码实现拆开验证。**
   - 不要默认“作者说 high-volume momentum、low-volume reversal，所以代码一定是这么做的”。
   - 先测自然语言版本，再测源码版本。
2. **15m 先做最干净的 router 版本。**
   - `vol_z` 分桶；
   - 高量只跑 continuation；
   - 低量只跑 reversal；
   - 中间区不交易。
3. **再看 5m/3m 是否值得压缩。**
   - 若 `15m` router 版本都留不住成本后净边，默认不下钻 `3m/1m`。
4. **Sharpe-weighting 不要第一步就照抄。**
   - 先用简单 equal-risk / inverse-vol；
   - 等单书 edge 站住后，再加 repo 的 Sharpe-weighting 外壳。
5. **单独做 cost-cliff。**
   - 这条线可能不是“信号错了”，而是“router 对了但换手太高”；
   - 必须把 `4 / 8 / 12 bps` 断崖画出来。
6. **把它沉淀成共享组件。**
   - 即使双书组合最后不如预期，`volume router` 也可能继续服务：
     - 单币趋势壳；
     - 横截面反转壳；
     - breakout / pullback 的 allow-veto。

## 7. 风险与保留意见
- **repo 极新。** GitHub API 显示它创建于 `2026-04-04 01:43 UTC`，目前 star/fork 都是 0，显然还没经过社区验证。
- **README 与源码并不完全等价。** 这类新 repo 最容易出现“文字版故事更顺、代码版实现更粗”的情况。
- **repo 的成本统计口径需要二次审。** 从源码看，它的 turnover / cost 计算更像原型口径，不适合直接当实盘承诺。
- **原始结果来自 Binance US 4H 样本。** 对我们 desk 的真正价值，不是照抄 4H 数字，而是验证这套 `router + dual-book` 结构能不能在 `15m/5m` 留下干净 pocket。

## 8. 来源
1. **Parnell Thrower. (2026). _crypto-start-arb_ (GitHub Repository).**
   - Authors / Year / Title / Venue: Parnell Thrower / 2026 / *crypto-start-arb* / GitHub Repository
   - DOI: N/A
   - Readable URL: `https://github.com/PThrower/crypto-start-arb`
   - Repo URL: `https://github.com/PThrower/crypto-start-arb`
   - Notes: GitHub API metadata shows `created_at = 2026-04-04T01:43:00Z`, `pushed_at = 2026-04-04T01:57:19Z`
2. **Lee, C. M. C., & Swaminathan, B. (2000). _Price Momentum and Trading Volume_. The Journal of Finance.**
   - DOI: `10.1111/0022-1082.00280`
   - Readable URL: `https://doi.org/10.1111/0022-1082.00280`
   - 这篇是“volume 改变 momentum 质量”最重要的经典地基之一。
3. **Yu, J.-R., Wei, C.-H., Lai, C.-J., & Lee, W.-Y. (2023). _Extending the Omega model with momentum and reversal strategies to intraday trading_. PLOS ONE, 18(9), e0291119.**
   - DOI: `10.1371/journal.pone.0291119`
   - Readable URL: `https://doi.org/10.1371/journal.pone.0291119`
   - 它给这条“日内 continuation / reversal 并存”读法一个更近年的方法地基。
4. **Binance Spot / Futures Kline & Volume Data Documentation**
   - Readable URL: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints`
   - 用途：支持 `1m/3m/5m/15m` 最小实验的数据公开性与可获取性说明。

## 9. 本轮结论（给后续 intake / replication 用）
- **结论一句话：** 这轮最值得 desk intake 的，不是 repo 里的某个 4H 最优参数，而是“**volume 不是 confirmation，而是决定 continuation 与 reversal 谁该上场的 router**”。
- **当前归类：** `raw alpha / complete-strategy candidate`
- **推荐优先级：** 高
- **进入下一步的条件：** 只要 `15m` 上能跑出一版成本后不太难看的 `router dual-book` pocket，就值得进入 `first verdict / clean replication`。

## 10. 本地产物
- `research/quant_digests/2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.html`
