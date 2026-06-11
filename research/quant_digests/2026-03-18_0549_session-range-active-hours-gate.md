# Crypto 虽然 24/7，15m 信号别 24h 同权：session range + 活跃时段 gate，更像三条收口线共用过滤层
- 时间：2026-03-18 05:49 UTC
- 类型：GitHub + 论文
- 主题标签：breakout-short/retest-hold/ema/psar/session-range/time-of-day/filter/crypto/15m
- 证据类型：repo 规则拆解 + 论文摘要佐证 + 公开时间戳可复现实验

## 1. 这次看了什么
这轮主看的是 Astralchemist 在 2025-05 发布的 Pine 仓库 `Session-Range-Advanced-Analysis-Tools`，外加 Joann Jasiak 与 Cheng Zhong 在 2024 年发表的论文 *Intraday and daily dynamics of cryptocurrency* 作为旁证。前者把 **session high/low、session VWAP、volume、ADX、HTF trend、structure break、candle close confirm** 写成了明确规则；后者则提醒我们：**crypto 虽然 24/7，但收益、成交量、波动并不是全天同分布，原生币与 tokens 的 intraday periodicity 会被 NYSE / LSE / Hang Seng 的运行时段牵引。**

**一句话核心结论：** 对当前 desk，最值得先测的不是再补一条新指标，而是把 `15m breakout-short / Fib retest_hold / EMA-PSAR continuation` 统一先过一层 **active-hours / session-range gate**：只在更有参与度的时段、围绕更有结构含义的 session 高低点去看 continuation 或 retest。

## 2. 核心结论
- 这条 source 最值钱的地方，不是“session box” 这件事本身，而是它把一个常被忽略的现实写死了：**15m 信号不该在 24 小时里被同权对待。**
- 论文摘要给出的关键信息很直接：Jasiak & Zhong（2024）在 Bitstamp 的 hourly / daily 样本上发现，**native cryptocurrencies 与 tokens 存在由 NYSE、LSE、Hang Seng 运行时间决定的共同 intraday periodicity**。这至少说明“全天统一阈值、统一信号密度、统一持仓权重”的读法并不自然。
- repo 则把这个想法落成了可执行骨架，而且参数口径对 15m 很友好：
  - 多时段默认划分是 `Asian 00:00-08:00`、`London 08:00-16:00`、`NY 13:00-22:00`；
  - `volume` 过滤不是玄学，而是 `volume > SMA20(volume) × 1.3`；
  - chop 过滤直接写成 `ADX > 20`；
  - 结构确认不是模糊“看起来突破了”，而是最近 `10` 根内出现过 `swing high/low` 的 structure break；
  - 还额外要求 `candle close confirm`、`HTF EMA50` 对齐、`min_confluence_score >= 70`。
- 对我们更有启发的读法不是照抄这个大而全 confluence 分数，而是把它压缩成一句更实用的话：**先问这根 15m bar 发生在不发生得起事的时段里吗，再问它是不是有 continuation / retest 价值。**
- 这很适合当前 desk，因为我们最近刚把 `OI participation gate` 与 `EMA-ADX-VOL skeleton` 都更诚实地压回了 `evidence pool / park`：现在继续堆新指标，不一定比先补一层更便宜、更可迁移的时段过滤更有价值。
- 如果这层 gate 有用，它最可能改善的不是峰值收益，而是：
  1. `dead-hour chop`；
  2. `break 后 2~4 bar 迅速回抽失败`；
  3. 扣成本后的 `median expectancy`；
  4. `trade count` 在不同 session bucket 的质量分布。

## 3. 为什么和当前项目有关
这轮优先认领它，比继续发散去找一条新的孤立 alpha 更值，因为它能同时服务三条当前收口线：
- 对 `V3 final-verdict / breakout-short follow-up`：它提供的是 **breakdown 发生时段 + session low/high 结构位 + retest 是否有量/有确认** 的共同过滤层，尤其适合区分 `continuation` 和 `dead-on-arrival`。
- 对 `Fibonacci confirmation / retest_hold`：Fib 本来就更像位置许可层；如果回踩发生在低参与度死时段，或者离最近有效 session 结构太远，它的 `hold` 质量就值得怀疑。也就是说，**session gate 可以给 Fib 再补一个“这次回踩发生在该发生的时候吗”** 的问题。
- 对 `EMA / PSAR raw alpha focus`：如果 EMA / PSAR 继续被要求全天 24h 持续开火，它大概率还是会被死时段 whipsaw 磨掉；而如果先把它降级成 **active-hours only / overlap overweight / dead-hours underweight** 的执行模板，它才像真的在做成本后能活下来的测试。

如果一定要回答“为什么这题比继续死磕三条线更值得”，答案是：**它不是偏离三条线，而是在给三条线补一个共用、便宜、今天就能复现的 veto / sizing layer。**

## 4. 可复刻的最小实验
- **研究假设**：在 `BTC / ETH / SOL` 的 `15m` perpetual 上，很多 continuation / retest 失败，不是价格结构本身错，而是信号出现在低参与度时段；把信号限制在更活跃的 session bucket，或要求它围绕 session 高低点完成 break + retest，能减少假动作并改善成本后表现。
- **数据源**：
  - 现有 `15m` OHLCV；
  - 如需补数据，可直接用公开交易所 K 线（Binance / Bybit 之类的公开 REST Klines 即可）；
  - session bucket 完全由 bar 的 UTC 时间戳派生，不依赖额外付费数据。
- **最小时段定义**：
  - `Asia = 00:00-08:00 UTC`
  - `London = 08:00-16:00 UTC`
  - `NY = 13:00-22:00 UTC`
  - 额外单独拆 `London-NY overlap = 13:00-16:00 UTC`
- **第一轮不要发明新 entry，只给现有三条线加 gate：**
  1. `raw_all_day`：原始 `breakout-short` / `Fib retest_hold` / `EMA+PSAR` 规则，全时段；
  2. `active_hours_only`：只允许 `London / NY / overlap`；
  3. `session_structure_gate`：信号必须发生在最近 session high/low 被突破后 `1~4` 根内的 retest / continuation；
  4. `+ volume_gate`：再要求 `volume > SMA20(volume) × 1.3`；
  5. `+ trend_or_chop_gate`：再要求 `ADX > 20`，并与 `HTF EMA50` 同向。
- **最先看的 5 个指标**：
  1. `4 / 8 / 12 bar follow-through`；
  2. `2~4 bar fail rate`（break 后立刻反抽回 session 区间，或 retest 后很快跌回/站回失效侧）；
  3. `post-cost expectancy @ 6 / 10 / 15 bps per side`；
  4. `trade_count_retention`；
  5. `session-bucket contribution`（收益和亏损分别主要来自哪个时段）。
- **一条更诚实的 sizing 试法**：
  - 不要一开始就 hard veto；
  - 先试 `overlap = 1.0x`、`London/NY 非 overlap = 0.75x`、`Asia = 0.5x`、`dead hours = 0x`；
  - 如果 sizing 版已经显著优于 all-day，说明它更像 **risk overlay**；如果只有 hard gate 才有效，说明它更像 **execution veto**。

## 5. 风险与保留意见
- repo 的社会证明很弱：当前只有 `1` star、`1` fork，不能把它当成“已经被市场验证”。
- 这份 repo 本身是“大杂烩脚本”，里面同时塞了 session、VWAP、RSI、liquidity sweep、FVG、order block；真正值得我们拿走的不是整锅端，而是 **session gate + structure/volume/chop veto** 这一小块。
- 论文证据目前更适合被当成 **periodicity / regime 提示**，而不是直接拿来证明某个 `15m` 进场规则已成立。它研究的是 Bitstamp 上 hourly / daily 的 intraday/intraweek patterns，不是直接为我们回测过 `15m breakout-short`。
- `active hours` 可能只是 `realized vol` 或 `volume percentile` 的替身，因此第一轮一定要做对照：**时段 gate** 是否真的优于简单的 `volume / volatility gate`？
- crypto 没有统一官方开盘收盘；如果 session 定义太机械，可能把“流动性”偷换成“人类习惯时间”。所以 `Asia / London / NY` 要允许做 `±1h` 漂移鲁棒性测试，别卡死单一切分。

## 6. 来源
- Astralchemist. (2025). *Session-Range-Advanced-Analysis-Tools*.
- Venue：GitHub
- DOI：N/A
- Readable URL：`https://github.com/Astralchemist/Session-Range-Advanced-Analysis-Tools`
- Repo URL：`https://github.com/Astralchemist/Session-Range-Advanced-Analysis-Tools`
- Raw script：`https://raw.githubusercontent.com/Astralchemist/Session-Range-Advanced-Analysis-Tools/main/session_range_liquidity.pine`
- Repo metadata：created `2025-05-28`, pushed `2025-11-16`, public repo, stars `1`, forks `1`

- Joann Jasiak, Cheng Zhong. (2024). *Intraday and daily dynamics of cryptocurrency*.
- Venue：International Review of Economics & Finance
- DOI：`10.1016/j.iref.2024.103658`
- Readable URL：`https://doi.org/10.1016/j.iref.2024.103658`
- Landing URL：`https://www.sciencedirect.com/science/article/pii/S1059056024006506`
- Repo URL：N/A
- 可读要点（来自公开摘要 / OpenAlex 索引）：native cryptocurrencies 与 tokens 的 intraday periodicity 与 `NYSE / LSE / Hang Seng` 运行时段相关；stablecoins 的动态显著不同。

## 7. 下一步怎么测
先别再造新指标，直接拿 `BTC / ETH / SOL` 最近 `120~365` 天 `15m`，对现有 `breakout-short`、`Fib retest_hold`、`EMA/PSAR` 三个 base setup 各跑一遍 `raw_all_day vs active_hours_only vs session_structure_gate vs +volume vs +ADX/HTF`。只要其中任意一条线能在 **不过度砍掉样本** 的前提下，稳定压低 `2~4 bar fail rate` 并改善 `post-cost expectancy`，这层 `session/time-of-day` 过滤就值得升格为当前 desk 的通用 overlay。