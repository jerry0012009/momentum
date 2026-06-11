# 别把这篇 2025 LUT thesis 只读成“pairs 方法比较”：对 short-cycle desk，更该先测的是「percentile-entry cointegration pairs」这条 3m/5m/15m raw alpha

- 时间：2026-04-02 18:04 UTC
- 类型：2025 LUT 学位论文全文 PDF + LUT landing page + Crossref 元数据交叉
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/engle-granger/percentile-entry/distribution-aware-threshold/binance/3m/5m/15m/paper/public-data/cost
- 证据类型：paper-based（全文 PDF 为主，landing page 与 Crossref 为辅）

- 主题类型：raw alpha
- 基础 alpha：**cointegrated crypto pair spread mean reversion**；先用 `Engle-Granger + ADF` 找可交易 pair，再对 spread 极端偏离做 `long cheap / short rich`，赌其回到均值附近。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
### 一句话核心结论
**这轮真正值得 intake 的，不是“distance vs cointegration 谁更好”这种课堂式结论，而是 thesis 里那条可以直接搬去 desk 做最小实验的 raw alpha：`先用 cointegration 选 pair，再用 pair-specific percentile extreme 做入场、均值穿越做离场`。**

### 为什么这轮比继续找一个泛 filter 更值得
因为它直接补的是当前 desk 最想要的东西：
- **raw alpha 很清楚**：不是 regime，不是 overlay，就是 `pairs / stat-arb / relative value / mean reversion`；
- **直接命中我们关心的频率**：作者不是用日线，而是直接比较了 Binance `3m / 5m / 15m`；
- **不是只给结论**：pair formation、entry、exit、sizing、cost 都写了；
- **还有一个很适合 desk 的旁支细节**：作者没有死守 pairs 文献常见的 `±2σ` 入场，而是改成 **每个 pair 自己 spread 分布的 top/bottom 0.5% 极值入场**，这比继续堆抽象“cointegration 有效”更像可直接测的 admission rule。

### 最关键的硬数据
这篇 thesis 里，最值得先记住的是这几组数字：
- 样本来自 **Binance 公共历史数据**，时间是 **`2023-07-07` 到 `2024-11-18`**；
- 可做空 universe 有 **`378` 个币**，每个频率理论上形成 **`71,253` 个 pair**；
- 研究直接比较了 `3m / 5m / 15m` 三个短周期；
- cointegration 方法的平均净收益分别约为 **`9.94% / 13.19% / 14.38%`**；
- distance 方法对应大约是 **`10.60% / 11.29% / 10.99%`**；
- cointegration 的平均持仓时长大约 **`12 / 15 / 17` 天**，说明它虽然用短周期 bar 触发，但本质上更像 **中短持有的 stat-arb sleeve**，不是 1m scalp。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这轮 **base alpha 很清楚**：

> **历史上一起走的两个币，短时偏离过头时，做多便宜腿、做空昂贵腿，赌 spread 回归。**

更具体地说：
1. 用 `Engle-Granger + ADF` 先挑出 spread 更稳定、更像均值回复过程的 pair；
2. 当该 pair 的 spread 进入自己历史分布的极端尾部时开仓；
3. 当 spread 回到均值附近时平仓。

所以它不是：
- breakout；
- trend following；
- 风控壳；
- 纯解释型综述。

它就是一条可以独立落地的 **pairs raw alpha**。

## 3. 来源信息
### 3.1 主来源
- **Author**：Micke Metsälä
- **Year**：2025
- **Title**：*Pairs trading performance in cryptocurrency markets*
- **Venue**：Lappeenranta–Lahti University of Technology LUT, Bachelor’s thesis
- **DOI**：无
- **Readable URL**：<https://lutpub.lut.fi/handle/10024/168939>
- **PDF URL**：<https://lutpub.lut.fi/bitstream/handle/10024/168939/bachelorsthesis_Metsala_Micke.pdf?sequence=3>
- **Repo URL**：N/A（论文未提供配套公开 repo）

### 3.2 方法脉络锚点（thesis 内引用，Crossref 校验）
- **Fil, M. & Kristoufek, L. (2020)**, *Pairs Trading in Cryptocurrency Markets*, **IEEE Access**, DOI: <https://doi.org/10.1109/ACCESS.2020.3024619>
- **Leung, T. & Nguyen, H. (2019)**, *Constructing cointegrated cryptocurrency portfolios for statistical arbitrage*, **Studies in Economics and Finance**, DOI: <https://doi.org/10.1108/SEF-08-2018-0264>

这两篇不是本轮主 digest，但它们说明：
**Metsälä 这篇 2025 thesis 不是凭空发明一条新花样，而是在已有 crypto pairs 文献上，把问题直接压到了 `3m/5m/15m`。**

## 4. 论文到底做了什么
## 4.1 数据与 universe
thesis 的数据口径很直接：
- **交易所**：Binance
- **报价货币**：USDT
- **可交易 universe**：满足保证金/可做空条件的币种，共 **`378` 个**
- **频率**：`3m / 5m / 15m`
- **样本期**：`2023-07-07 ~ 2024-11-18`
- **观测数**：约 **`240,001`（3m）/ `144,000`（5m）/ `48,000`（15m）**

这点很值钱，因为它不是拿“老股票 pairs 文献”硬移植，而是真的在 crypto 数据上做了短周期比较。

## 4.2 pair formation
作者比较两套 pair formation：

### A. Distance approach
- 对归一化后的价格路径计算 **SSD（sum of squared deviations）**；
- 每个频率选 **`25` 对 SSD 最小**的 pair 进入交易池。

### B. Cointegration approach
- 用 **Engle-Granger 两步法**；
- 先 OLS 回归拿残差；
- 再对残差做 **ADF** 检验；
- 在显著性水平 **`1%`** 下筛选可接受 pair；
- 每个频率选 **`25` 对 ADF 统计量最强**的 pair 进入交易池。

翻成人话：
- distance 看的是“历史上像不像一起走”；
- cointegration 看的是“它们的偏离是不是更像能回来的平稳 spread”。

对 desk 来说，这就对应两个可直接并排的 pair discovery baseline。

## 4.3 交易规则
这篇 thesis 最值钱的地方，不只是“cointegration 更好”，而是它把交易卡写出来了。

### 入场
作者没有使用传统 pairs 文献里常见的 `±2σ` spread band，而是改成：
- 对每个 pair 的 spread 分布，取 **最上面的 `0.5%`** 和 **最下面的 `0.5%`**；
- 合起来就是 **top/bottom `1%` 极端值** 作为入场阈值。

这个改法的逻辑是：
- spread 分布可能偏斜、肥尾，不一定适合硬套标准差；
- percentile threshold 对 outlier 更鲁棒；
- 每个 pair 用自己的分布决定阈值，更像 pair-specific admission，而不是全市场统一带宽。

### 离场
- 不是看 `z=0` 或零轴穿越；
- 而是 **spread 回到该 pair 的平均值附近就平仓**。

### 仓位
- 每笔交易使用 **`1000` 单位资金**；
- 两条腿按 hedge ratio 做分配；
- 是标准 long-short 配对，不用杠杆花活。

### 成本
- thesis 明写 **每笔交易成本 `0.1%`**；
- 这是 Binance 典型手续费口径的简化处理；
- 成本已纳入交易模拟。

### 风控
- **没有 stop-loss**；
- 也没有复杂 regime / veto / portfolio heat。

所以它是一个 **完整但朴素** 的 raw alpha 策略卡：
- 有 pair selection；
- 有 entry/exit；
- 有 sizing；
- 有 cost；
- 但 risk layer 还非常基础。

## 5. 最值得 desk 拿走的，不是“cointegration 赢了”，而是 percentile-entry 这层 admission logic
如果只把这篇 thesis 总结成“cointegration 全面优于 distance”，价值其实有限，因为这件事在 crypto pairs 文献里已经不算特别新。

**真正值得拿走的，是作者把 admission layer 改成了 pair-specific percentile extremes。**

对 short-cycle desk，这有三个直接好处：
1. **比统一 `±2σ` 更贴近 crypto 的肥尾现实**；
2. **能直接做 transfer check**：同一套 pair、同一套 exit，只比较 percentile vs z-score，立刻知道 admission 层到底值不值；
3. **适合和我们已有的 pairs 管线拼接**：无论前面是 static beta、dynamic beta、Kalman、graph matching、Hurst gate，最后都可以接一层“pair 自己的尾部分位开仓”。

所以这轮最应该被记成：
**不是“又一篇 pairs 论文”，而是“crypto short-cycle pairs 里一个可以马上做 ablation 的入场层假设”。**

## 6. 结果里哪些数字最值得记
## 6.1 频率层比较
作者的总表结论很直接：

### Cointegration
- **3m**：平均净收益约 **`9.94%`**
- **5m**：平均净收益约 **`13.19%`**
- **15m**：平均净收益约 **`14.38%`**

### Distance
- **3m**：平均净收益约 **`10.60%`**
- **5m**：平均净收益约 **`11.29%`**
- **15m**：平均净收益约 **`10.99%`**

也就是说，
- distance 没有明显随 bar 变慢而改善；
- cointegration 则是 **bar 越慢，平均结果越稳、越强**。

这跟 desk 直觉是对得上的：
**真正稳定的 pairs raw alpha，通常不是靠更快 bar 硬挤出来，而是靠更稳定的 spread 关系活下来。**

## 6.2 风险与持仓时长
cointegration 方法下：
- 平均持仓时长大约 **`12` 天（3m）/ `15` 天（5m）/ `17` 天（15m）**；
- 平均最大回撤并不大，文中总结里提到 **最大平均 drawdown 约 `-1.45%`**，出现在 3m；
- 15m 平均收益最高，但持仓也最长。

distance 方法下：
- 5m 是它最像样的一档，平均约 **`11.29%`**；
- 但总体 drawdown 与收益稳定性仍弱于 cointegration；
- thesis 结论层给出的 distance overall 平均收益约 **`10.96%`**，cointegration overall 约 **`12.5%`**。

这组数字对 desk 的真正提醒是：
**别因为用了 `3m/5m/15m` bar，就误以为这一定是超快 alpha。它更像“短周期监控 + 中短周期持有”的 stat-arb。**

## 6.3 pair-level 例子
文中举出的高表现 pair 包括：
- **3m cointegration**：`RVNUSDT-KMDUSDT`，收益约 **`23.27%`**，波动约 **`1.94%`**，持仓约 **`12` 天**；
- **5m cointegration**：`RVNUSDT-KMDUSDT`，平均收益约 **`27.12%`**，波动约 **`2.32%`**；
- **15m cointegration**：`DYMUSDT-OMNIUSDT`，平均收益约 **`26.53%`**；
- 包装资产对如 `WBTCUSDT-BTCUSDT` 往往收益接近零，说明“关系太紧”不等于“可赚”。

当然，这些具体小票 pair 不应直接照抄；
但 thesis 至少给了一个很明确的工程启发：
**真正能赚钱的 pair，未必是最 obvious 的同资产镜像，而常常是叙事/流动性接近、但短时错位更常发生的次主流币对。**

## 7. 这轮对当前 desk 的直接意义
## 7.1 它和最近研究积累怎么衔接
项目最近已经积累了不少 pairs / stat-arb 主题：
- anti-persistence gate；
- graph matching pair book；
- dynamic boundary RL；
- graduation / throttle 操作系统；
- half-life / Hurst / Kalman 等动态层。

**这篇 thesis 的增量，不在于再证明“pairs 可以做”，而在于它把入场层换成了更适合 crypto 分布的 percentile rule，并且直接在 `3m/5m/15m` 上给了结果对比。**

所以它更像是：
- 给现有 pairs 管线补一个 **admission-layer ablation**；
- 而不是新开一条完全无关的研究支线。

## 7.2 它为什么比继续补一个 generic filter 更值得
因为这轮主题能直接服务：
- **raw alpha 素材池**；
- **pairs / stat-arb 复现 backlog**；
- **完整策略卡拆解**；
- **短周期 bar 选择**。

如果写一个宏观 gate 或情绪 filter，也许也有价值；
但和这篇 thesis 相比，它们对当前 desk 的“马上能回测”帮助反而更弱。

## 8. 对 `1m / 3m / 5m / 15m` 的正确读法
## 8.1 这条 alpha 不是 1m 主信号型，而是“慢关系 + 快触发”
这篇 thesis 最容易被误读的点是：
- 频率用了 `3m / 5m / 15m`；
- 但平均持仓竟然还是十几天。

这说明：
**短周期 bar 在这里主要是拿来更早看见 spread 偏离，而不是要求你高频翻单。**

更适合 desk 的映射方式是：
- **15m**：做主回测、主 admission、主收益评估；
- **5m**：做更灵敏的触发 refinement；
- **3m**：做 stress test 或更快 admission；
- **1m**：只拿来做执行，不建议直接做 pair discovery。

## 8.2 它更像“完整 stat-arb sleeve”的胚胎
如果 desk 真的要拿它落地，最合理的读法不是：
- “找一个最好的 3m pair 明天就实盘”；

而是：
1. 先搭稳定的 pair formation；
2. 再比较 percentile vs z-score admission；
3. 再加真实成本和 portfolio risk；
4. 最后再决定 5m/3m 是否值得压缩。

## 9. 这篇 thesis 的局限，必须先说清
这轮虽然值得 intake，但不能神化。

### 9.1 风控层太薄
- 没有 stop-loss；
- 没有 cointegration-break veto；
- 没有 portfolio heat cap；
- 没有事件窗口禁入。

所以它更像 **alpha 骨架**，不是可直接实盘的终稿。

### 9.2 样本里有不少小票 pair
像 `RVN/KMD`、`DYM/OMNI` 这类 pair，
如果直接平移到今天的 live trading，可能会碰到：
- 流动性差；
- 冲击成本高；
- 币种生命周期短；
- 叙事切换太快。

### 9.3 成本模型还不够 desk 化
thesis 用的是简化的 **`0.1%` 每笔交易成本**。
对我们来说，这既可能：
- **高估** perp-maker 情形的成本；
- 也可能 **低估** 双腿成交不同步与滑点的真实损耗。

所以这篇 thesis 最适合做：
**研究起点**，不是收益预言。

## 10. 可复刻的最小实验
### 实验 A：先复 thesis 的核心对比
- **Universe**：`20~40` 个最液态 USDT perpetual 或 spot-margin 可做空币
- **Bars**：`3m / 5m / 15m`
- **Formation**：滚动 `120~200` 天
- **Selection**：
  1. Distance（SSD）
  2. Cointegration（Engle-Granger + ADF）
- **Admission**：
  1. thesis 版：spread 分布 top/bottom `0.5%`
  2. baseline：rolling z-score `±2.0 / ±2.5`
- **Exit**：mean crossing / `z -> 0`
- **Sizing**：beta-neutral 或 thesis 式 hedge-ratio allocation
- **Cost**：至少跑三档 pair round-trip friction
  - `12 bps`
  - `20 bps`
  - `30 bps`

这一步先回答：
**在今天更可交易的主流币 universe 里，percentile-entry 还能不能保住 thesis 里的相对优势。**

### 实验 B：只改 admission，不改 pair
固定同一批 cointegration pair，做下面的 ablation：
1. `±2σ` entry
2. percentile entry（0.5%/0.5%）
3. percentile entry + max-hold

这一步最关键，因为它能单独验证：
**这轮 intake 的真正新增值，到底是 cointegration 本身，还是 percentile admission。**

### 实验 C：把 risk layer 补齐
在 thesis 骨架上补三层最简单的实盘保护：
- **max-hold**：`5 / 10 / 20` 天
- **cointegration-break veto**：ADF/p-value 失效即禁新仓
- **pair DD stop**：spread 继续恶化到更高分位时退出

### 实验 D：从 15m 往 5m/3m 压缩，而不是反过来
顺序建议：
1. 先跑 `15m`
2. 再压到 `5m`
3. `3m` 最后再看

因为 thesis 自己的结果已经在提醒我们：
**越快不等于越强，先确认 `15m` 活着，再去看更快频率是否只是放大成本。**

## 11. 下一步怎么测
1. **先复现 cointegration + percentile-entry 这条最小骨架。** 不要一上来就加太多 fancy gate。
2. **用主流高流动性币重跑。** thesis 里很多高收益 pair 很可能是小票效应，不适合直接照抄。
3. **把 admission 层单独做 ablation。** 这轮最该验证的不是“pairs 有无 alpha”，而是 `percentile vs z-score`。
4. **先以 15m 作为稳健主频。** 若 15m after-cost 不成立，3m/5m 大概率不会更好。
5. **把双腿执行成本显式写进回测。** 不然 pairs 很容易回测漂亮、实盘窒息。

## 12. 一句话给当前项目的结论
**这篇 2025 LUT thesis 值得进池，不是因为它又证明了一遍 cointegration pairs，而是因为它把一条很适合 short-cycle desk 立刻去测的假设说清了：在 crypto 的肥尾 spread 分布下，`pair-specific percentile extremes` 可能比传统 `±2σ` 更适合作为 pairs raw alpha 的 admission layer。**

## 13. 来源链接
- LUT landing page：<https://lutpub.lut.fi/handle/10024/168939>
- Thesis PDF：<https://lutpub.lut.fi/bitstream/handle/10024/168939/bachelorsthesis_Metsala_Micke.pdf?sequence=3>
- Fil & Kristoufek (2020) DOI：<https://doi.org/10.1109/ACCESS.2020.3024619>
- Leung & Nguyen (2019) DOI：<https://doi.org/10.1108/SEF-08-2018-0264>
