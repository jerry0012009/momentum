# 别把这份 2023 GitHub same-hour repo 只读成 seasonality notebook：对 short-cycle desk，更该先测的是「hour-of-week 条件化 XS long-short blend」这条完整 raw alpha
- 时间：2026-04-01 20:45 UTC
- 类型：2023 GitHub repo source audit（`Project.ipynb`）+ 2022 *The North American Journal of Economics and Finance* 摘要/Introduction + 2024 *Review of Quantitative Finance and Accounting* 引言/结果段落
- 主题类型：raw alpha
- 基础 alpha：按 hour-of-week 条件切换的横截面 long-short——weekday after-hours 做 same-hour 短窗 reversal，weekday regular-hours 做 same-hour 中窗 momentum
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/time-of-day/hour-of-week/momentum/reversal/market-neutral/same-hour/binance/1h/15m/5m/3m/1m/repo/paper/public-data/cost
- 证据类型：工程经验 + 论文证据

## 1. 这次看了什么
看的是 GitHub 仓库 **MateoPedro/StatArb** 的 `Project.ipynb`：作者用 Binance 10 个主流币的 1h 数据，把“同一个小时在过去若干天的平均收益”做成横截面 rank-demean 权重，再按不同 hour bucket 分开检验 reversal 和 momentum。辅助证据来自 **Wen, Bouri, Xu, Zhao (2022)** 对 crypto intraday momentum/reversal 的论文，以及 **Brauneis, Mestel, Theissen (2024)** 对全球 CEX 时间分布、流动性与波动共性的研究。

## 2. 核心结论
- 这份 repo 真正可交易的不是“24 小时固定季节性”，而是 **按 hour-of-week 切换方向** 的 market-neutral raw alpha。
- 样本内（约 2020-01-01 到 2022-06-30）先扫 1~30 天 lookback：作者发现 **same-hour 1~2 天偏 reversal，9~21 天偏 momentum**，且 weekday / after-hours 与 weekday / regular-hours 的口袋最清楚。
- 样本外回测（约 2022-06-30 到 2023-07-15）保留了两条腿：**H1 = weekday after-hours 的 1~2d reversal**，**H3 = weekday regular-hours 的 9~21d momentum**；周末 regular-hours 那条 H2 被作者主动丢弃。
- 仓位不是拍脑门：先做 **横截面 rank → demean → L1 归一** 保证 dollar-neutral，再把不同 lookback sleeve 用 **Sharpe-style 权重** 合成。
- repo 虽然加了 **20 bps** 简单交易成本后仍说“没把策略打死”，但成本模型太粗；真正 first verdict 必须改成 **turnover-aware fee+spread+impact**。

## 3. 为什么和当前项目有关
最近 intake 已经补了很多 pairs / carry / microstructure，但 **“时钟条件化的横截面相对价值”** 还没有作为完整策略单独入池。这个主题的好处是：
- 它不是单币固定 bias，而是 **market-neutral XS alpha**；
- 不依赖私有数据，Binance 公开 k 线就能先做最小实验；
- 能自然映射到 `15m/5m`：信号仍用 `1h` 生成，执行改成子 bar 分批进出；
- 如果 raw alpha 不够强，2024 那篇时间分布论文还能反过来提供 **哪些 UTC 时段更值得交易/更该降仓** 的 regime 解释。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / market-neutral
- 基础 alpha：同一 UTC 小时过去 `d` 天平均收益的横截面排序；after-hours weekday 取反做 reversal，regular-hours weekday 顺着做 momentum
- regime：先只保留 weekday；再拆 regular-hours vs after-hours；周末与弱 pocket 先禁用
- filter / veto：仅做流动性前 N；要求该小时历史 pocket 在 train 内为正 Sharpe；弱币/低成交额/高 funding 扰动时段先剔除
- risk / sizing / execution overlay：rank-demean 权重、book-level gross cap、sleeve Sharpe 权重、子 bar TWAP 入场、小时末或下一目标小时平仓、turnover/cost cap

## 4. 可复刻的最小实验
- 研究假设：crypto 的 intraday predictability 不只体现在单币方向，还能转成 **按 hour-of-week 切换的 XS long-short**。
- 数据：Binance spot 或 perp 主流 20~30 币，先取 `1h` klines；执行层再下采样到 `15m/5m`。
- 信号：
  1. 对每个 UTC 小时分别维护过去 `d` 天该小时收益均值；
  2. 横截面排名后 demean，并除以绝对值和；
  3. `d∈{1,2}` 在 weekday after-hours 反向交易；`d∈{9..21}` 在 weekday regular-hours 顺向交易。
- 入场/出场：目标小时开盘后第一个 `5m/15m` 子 bar 进场，持有到该小时结束；先别拉长持有。
- 成本：先做 `5/10/15/20 bps` friction ladder，再补 turnover × spread proxy；没有成本梯度就不算过第一关。
- 验证：看 OOS Sharpe、正收益小时占比、币种覆盖率、turnover、对子 bar 执行后是否仍保留 edge。

## 5. 先测什么，不先测什么
先测 **H1 + H3 两条可定义清楚的腿**，不要一上来把 24 个小时、7 天、几十个 lookback 全部一起优化。尤其别先卷“哪个 UTC 小时最好”——先回答：**这条 alpha 在 costs 后到底还能不能活**。

## 6. 风险与误区
- repo 只覆盖 10 个币，容易有幸存者与大币偏置。
- 20 bps 处理方式过粗，没显式扣 turnover；对子 bar 执行后 edge 可能明显变薄。
- time-of-day 效应很容易被交易所制度、欧洲/美股时段重叠、资金费率结算点污染；必须做按年份/按交易所/按币种稳定性拆分。
- 这类信号更像 **clock-conditioned cross-sectional scheduler**，不是 24/7 always-on 引擎。

## 7. 来源与复现线索
- Repo：MateoPedro (GitHub, 2023), *StatArb* — <https://github.com/MateoPedro/StatArb>
- Raw notebook：`Project.ipynb` — <https://raw.githubusercontent.com/MateoPedro/StatArb/main/Project%20.ipynb>
- Wen, Zhuzhu; Bouri, Elie; Xu, Yahua; Zhao, Yang (2022), *Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both*, *The North American Journal of Economics and Finance*, DOI: <https://doi.org/10.1016/j.najef.2022.101733>, readable URL: <https://www.sciencedirect.com/science/article/pii/S1062940822000833>
- Brauneis, Alexander; Mestel, Roland; Theissen, Erik (2024/2025), *The crypto world trades at tea time: intraday evidence from centralized exchanges across the globe*, *Review of Quantitative Finance and Accounting*, DOI: <https://doi.org/10.1007/s11156-024-01304-1>, readable URL: <https://link.springer.com/article/10.1007/s11156-024-01304-1>

## 8. 一句话带走
如果要把这份材料变成 desk 可测策略，我会把它定义成：**“只在特定 hour-of-week 开机的横截面 long-short 调度器”，而不是又一篇泛泛的 intraday seasonality 读书笔记。**
