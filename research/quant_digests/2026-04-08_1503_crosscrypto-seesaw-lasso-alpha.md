# 别把这篇 2023 JEF 论文只读成“lead-lag”：对 short-cycle desk，更该先测的是「rolling LASSO spillover rank × top-bottom long-short」这条 raw alpha
- 时间：2026-04-08 15:03 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：滚动估计“别的币这一根的收益 → 该币下一根收益”的跨币 spillover，再按预测收益做横截面多空排序
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / relative-value / lead-lag / negative-spillover / LASSO / market-neutral / 5m / 15m
- 证据类型：论文证据 + 本地 public-data portability probe

## 1. 这次看了什么
看的是 **Yuecheng Jia, Yangru Wu, Shu Yan, Yuzheng Liu (2023), _A seesaw effect in the cryptocurrency market: Understanding the return cross predictability of cryptocurrencies_, Journal of Empirical Finance**。这篇不是在讲“BTC 领涨，其他币跟涨”，而是在讲更反直觉的一件事：**crypto 的币间 intraday 传导，经常更像跷跷板，而不是同向扩散**。

## 2. 核心结论
- 论文核心发现是 **negative lead-lag / seesaw effect**：大币这一根的收益，往往对其他币下一根收益有**负向**预测，而不是像股票行业扩散那样正向带动。
- 这种效应主要是 **large → other coins**，反方向（small → large）明显弱得多。文中经验样本覆盖 **2018-01-01 ~ 2021-07-30**、交易所主要是 **Bitfinex / Huobi**，large coins 重点看 **BTC / ETH / XRP / LTC / EOS**。
- 作者不是停在相关性，而是直接做了 **rolling LASSO 的横截面交易策略**；文中页面片段给出的口径是：考虑现实交易成本后，组合年化收益大约仍有 **21.08% / 94.56%**，平均每 `5m` 组合收益约 **0.07–0.08 bps（Bitfinex）**、**0.02–0.09 bps（Huobi）**。
- 但这条 alpha 不能被粗暴简化成“BTC 涨了就空山寨”。我用 Binance USDⓈ-M 近 **35 天 5m** 的 top-liquid perp 做了一个**naive quick probe**：把 `BTC+ETH` 当 large basket、其余 6 个币当 small basket，结果 **top decile large shock 后，next-bar `small-large` 反而约 +0.176 bps**；若直接做 `long large / short small` 的 next-bar 事件书，约 **-0.236 bps/次**。说明**论文里的可迁移点是“全横截面 spillover ranker”**，不是单条大币冲击后的机械反手。

## 3. 为什么和当前项目有关
这条东西和 desk 当前最相关的地方在于：它给的不是 breakout/filter，而是一条**能独立成策略的横截面 raw alpha**。而且它天然适合补我们素材池里最需要持续 intake 的那一类：
- 不是单币形态，而是 **cross-sectional / relative-value**；
- 不是只讲 regime，而是直接给出 **tradeable ranking signal**；
- 不是只能日频迁移，论文本身就站在 **intraday** 口径上。

一句话核心结论：**crypto 币间短周期传导更像“强者吸血、弱者让位”，所以应该做跨币相对收益排序，而不是默认做同向跟随。**

一句话证明方式：**作者直接在高频币种收益网络上估计滚动 LASSO spillover，并把预测收益做成真实多空组合，随后再扣现实交易成本。**

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / market-neutral
- 基础 alpha：`pred_i,t+1 = f(r_{-i,t})` 的 rolling spillover rank；做 `long top bucket / short bottom bucket`
- regime：大币主导、注意力/流动性向 majors 集中时更可能强
- filter / veto：只在预测分差足够大、横截面离散度够高、盘口成本不过线时开仓
- risk / sizing / execution overlay：等权 top-bottom，控制 gross exposure 与 turnover；优先 15m 降频或 5m 但加 signal-gap/cost gate

## 4. 可复刻的最小实验
- 研究假设：`5m/15m` 下，**全横截面** contemporaneous return spillover 对 next-bar relative return 仍有可交易信息；但 **naive major-vs-small 单因子简化会丢信号**。
- 可计算定义：对 top `8~12` liquid perps，滚动用过去 `20~30` 天样本，分别对每个币做 `next_ret_i ~ LASSO(other_coins_current_ret)`，得到 `pred_ret_i`；每根按 `pred_ret_i` 排名，做 `long top 2 / short bottom 2`，持有 `1 bar` 与 `3 bars` 两版。
- 最小回测切口：Binance / OKX top-liquid perps；先做 `5m`，再看 `15m` 降 turnover 版；样本先取近 `180` 天。
- 最该先看 2 个指标：**post-cost expectancy / rebalance**、**turnover / fee drag**。第三个再看 `beta-neutrality` 或 `major-coin dependence`。

## 5. 风险与保留意见
- 当前我拿到的是 **ScienceDirect 摘要页/结果片段 + RePEc 摘要**，不是出版社全文 PDF；结论可用，但仍建议后续补全文或工作论文版。
- 这条 alpha **极度依赖实现口径**：是否做全横截面、是否 rolling refit、是否 market-neutral、是否只在高 signal-gap 时交易，都会决定它是 alpha 还是噪音。
- 本地 quick probe 已经说明：**把它误读成“BTC 涨了就空 alt”会很容易做错方向。**
- 预期这类策略的真正敌人不是“有没有信号”，而是 **换手、费率、滑点、杠杆融资与同步成交约束**。

## 6. 来源
- Yuecheng Jia, Yangru Wu, Shu Yan, Yuzheng Liu. (2023). *A seesaw effect in the cryptocurrency market: Understanding the return cross predictability of cryptocurrencies*. *Journal of Empirical Finance*.
- DOI: `10.1016/j.jempfin.2023.101428`
- Readable URL: `https://doi.org/10.1016/j.jempfin.2023.101428`
- RePEc / IDEAS abstract page: `https://ideas.repec.org/a/eee/empfin/v74y2023ics0927539823000956.html`
- ScienceDirect article page: `https://www.sciencedirect.com/science/article/abs/pii/S0927539823000956`
- Earlier working-paper lineage: `https://doi.org/10.2139/ssrn.3465924`
