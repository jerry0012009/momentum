# RECENT_PAPER_SEEDS

> 用途：给定时研究任务提供“无需搜索 API 也能开工”的论文种子清单。
> 原则：优先最近 5 年、尽量提供 DOI + 可读 URL、优先能直接获取全文 / PDF、尽量贴近当前学习阶段（基础 alpha 优先）。

## 使用优先级规则（新增）

- 若某个种子同时满足：近期 / 靠谱来源 / 有公开代码或仓库 / 能拿全文，则优先级最高；
- 若只能拿到摘要或标题页，则默认只作为候选线索，不应直接进入高优先级 digest / deep dive / replication shortlist。

## A. 结构 / 价格形态 / 技术分析

### Jiang, Kelly, Xiu (2023)
- Title: *(Re-)Imag(in)ing Price Trends*
- Venue: Journal of Finance
- DOI: <https://doi.org/10.1111/jofi.13268>
- Readable URL: <https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13268>
- Why seed:
  - 更贴近“价格结构还能抽出什么趋势信息”
  - 适合衔接结构/通道/图形思路

### Svogun, Bazán-Palomino (2022)
- Title: *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?*
- Venue: Journal of International Financial Markets, Institutions and Money
- DOI: <https://doi.org/10.1016/j.intfin.2022.101601>
- Readable URL: <https://www.sciencedirect.com/science/article/pii/S1042443122000130>
- Why seed:
  - 直接落到 crypto
  - 可以帮助判断技术规则扣掉成本后还剩多少

## B. Time-Series Momentum / Trend Following

### Liu, Lu, Wang (2021)
- Title: *Asymmetry, tail risk and time series momentum*
- Venue: International Review of Financial Analysis
- DOI: <https://doi.org/10.1016/j.irfa.2021.101938>
- Readable URL: <https://www.sciencedirect.com/science/article/pii/S1057521921002458>
- Why seed:
  - 更偏风险分布与尾部风险
  - 适合从“效应是否可用”走向“效应长什么样”

### Pitkäjärvi (2022)
- Title: *A Limited Attention Theory of Time Series Momentum*
- Venue: SSRN working paper
- DOI: <https://doi.org/10.2139/ssrn.4168092>
- Readable URL: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4168092>
- Why seed:
  - 偏机制解释
  - 适合补“为什么可能有效”这一层

### Xu, Li, Singh, Li (2023/2024 working paper)
- Title: *Cross-Market Intraday Time-Series Momentum*
- Venue: SSRN / working paper
- DOI: <https://doi.org/10.2139/ssrn.4651331>
- Readable URL: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4651331>
- Why seed:
  - 更贴近 intraday / cross-market
  - 和 5m / 15m 主线最接近

## C. 经典但可回退的地基论文

### Moskowitz, Ooi, Pedersen (2012)
- Title: *Time Series Momentum*
- Venue: Journal of Financial Economics
- DOI: <https://doi.org/10.1016/j.jfineco.2011.11.003>
- Readable URL: <https://www.sciencedirect.com/science/article/pii/S0304405X11002613>

### Lo, Mamaysky, Wang (2000)
- Title: *Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation*
- Venue: NBER Working Paper / Journal of Finance version exists
- DOI: <https://doi.org/10.3386/w7613>
- Readable URL: <https://www.nber.org/papers/w7613>

## 使用规则
- 定时任务优先从本文件与 `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md` 里选题。
- 如果这里已经足够支持一篇 digest，就不要为了“搜索”而搜索。
- 只有当这些种子不能覆盖当前学习阶段的缺口时，才额外使用 `web_search`。
- 若 `web_search` 不可用，继续使用本文件 + `web_fetch` 完成任务，不要中止。
