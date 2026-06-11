# 别把这篇 2025 intraday lottery 论文只读成行为金融解释：对 short-cycle desk，更该先测的是「past-1h MAX 极值 × next-1h 横截面反转」这条 raw alpha
- 时间：2026-04-16 12:46 UTC
- 类型：论文（Crossref 元数据 + 摘要）+ Binance USDⓈ-M `5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：过去 1 小时内出现更极端 `MAX`（5m 子收益最大值）的币，在下一小时横截面上更容易跑输；做多 low-MAX，做空 high-MAX
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（先落 baseline，再做执行优化）
- 主题标签：raw-alpha/cross-sectional/mean-reversion/lottery-demand/MAX-effect/intraday/5m/15m/1m/3m/perpetual/cost
- 证据类型：论文证据（摘要级）+ public-data fast probe

**先回答 base alpha：**这篇东西的 base alpha 不是“情绪解释”，而是很具体的 **intraday 横截面反转**：`MAX` 越高，下一小时预期收益越低。

## 1. 这次看了什么
看了 2025 年 *Studies in Economics and Finance* 论文 **Intraday lottery demands in cryptocurrency market**（作者 Manisha Yadav）。可直接拿到 Crossref 结构化摘要：论文把 Bali et al. 的 MAX 指标改成 **过去 1h 的 5m returns**，预测 **下一小时收益**，并与 IVOL / skewness 做了横截面检验。

## 2. 核心结论
- 论文主结论可以直接写成交易语句：**high-MAX 组下一小时跑输，low-MAX 组跑赢（跨币横截面）**。
- 关键量化点（论文给出）：`MAX` 每上升 1 个标准差，后续收益约下降 `0.043%`（约 `4.3 bps`）。
- 这条线是 raw alpha，不是 filter：它本体就是可交易的 long-short 排名规则。
- 我用 Binance USDⓈ-M `5m` 做了 fast portability probe（40d、小时调仓、low-vs-high quintile）：
  - gross 平均约 `+2.35 bps/小时`，gross 命中率约 `53.9%`；
  - 但加 `2bps` roundtrip 成本后，均值变为 `-1.65 bps/小时`；
  - `8bps` 下明显失活（约 `-13.65 bps/小时`）。
- 含义很直接：**信号有形状，但执行摩擦是生死线**。这更像“可复现 raw alpha + 强执行约束”的候选。

## 3. 为什么和当前项目有关
- 它直接补充了 desk 当前最需要的 **cross-sectional / relative-value / mean-reversion** 素材池，不是又一篇泛趋势讨论。
- 指标定义轻量，能快速映射到 `1m/3m/5m/15m`：
  - `5m`：过去 12 根求 MAX，预测下一小时；
  - `1m`：过去 60 根求 MAX，预测未来 15~60 分钟；
  - `15m`：过去 4 根求 MAX，预测下一根或下一小时。
- 与现有“rolling-MAX 续强”类结果形成互补：本题强调的是 **short-horizon 横截面反转口袋**，不是无条件 continuation。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 均值回复（market-neutral）
- 基础 alpha：high past-1h MAX underperforms, low MAX outperforms in next 1h
- regime：仅在横截面离散度足够高（如 MAX dispersion 超分位）启用
- filter / veto：重大事件窗（宏观公布前后）、盘口过薄币种、异常跳点时 veto
- risk / sizing / execution overlay：波动率缩放仓位、单腿权重上限、最大持有 1h、成本阈值（先过 `2/4/8 bps` 梯度）

## 4. 可复刻的最小实验（下一步怎么测）
1. **Universe**：Binance USDⓈ-M 流动性前 `N=20~40` 永续；剔除新上线与异常符号。
2. **Signal**：每小时计算 `MAX_i = max(r_{i,t-11:t})`（`r` 为 5m log return）。
3. **Portfolio**：long bottom quintile / short top quintile，等权，持有 1h。
4. **Exit**：固定 `1h` 到期平仓（不做路径依赖）。
5. **Cost ladder**：`0/2/4/8 bps`，先看 `net bps/小时` 与 `capacity proxy（换手）`。
6. **稳健性**：改 `formation window`（30m/1h/2h）与 `holding`（30m/1h/2h），检查符号是否翻转。

## 5. 风险与保留意见
- 当前论文证据是摘要级（Emerald 页面受限），不宜过度外推到“全市场全阶段恒成立”。
- fast probe 对样本与交易成本高度敏感，且本轮 Binance REST 后段触发了限频；需要后续用稳定数据管线重跑。
- 该线天然高换手，若不把执行摩擦（maker 占比、冲击成本）纳入，极易把 gross edge 全吃掉。

## 6. 本轮产物与来源
### 本轮产物
- `reports/artifacts/quant_digests/2026-04-16_intraday_max_lottery_probe.py`
- `reports/artifacts/quant_digests/2026-04-16_intraday_max_lottery_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-16_intraday_max_lottery_probe_regime.csv`

### 来源
1. **Yadav, M. (2025). Intraday lottery demands in cryptocurrency market. Studies in Economics and Finance.**
   - DOI：<https://doi.org/10.1108/sef-07-2024-0461>
   - Crossref：<https://api.crossref.org/works/10.1108/sef-07-2024-0461>
   - Readable URL（publisher landing）：<http://www.emerald.com/sef/article/42/4/799-835/1256079>
2. **Bali, Cakici, Whitelaw (2011). Maxing out: stocks as lotteries and the cross-section of expected returns.**
   - DOI：<https://doi.org/10.1016/j.jfineco.2010.08.014>
