# 别把这篇 2025 JIFMIM 论文只读成“国际股市开盘会看美股脸色”：对 desk 更该先测的是「US close impulse → crypto synthetic open catch-up」跨时段 raw alpha
- 时间：2026-03-28 00:57 UTC
- 类型：2025 *Journal of International Financial Markets, Institutions and Money* 论文摘要 + ScienceDirect section snippets + Crossref 元数据
- 主题类型：raw alpha
- 基础 alpha：**leader 市场收盘前最后一段收益，会在存在“等待空窗”的 follower 市场下一次可交易窗口里延续出来；对 crypto desk，可 desk 化成 `US cash close 最后 15m/30m` → `BTC/ETH/ALT 在下一个 synthetic session open 的 1m/3m/5m/15m catch-up`。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-asset/session-boundary/overnight/spillover/us-close/synthetic-open/lead-lag/momentum/btc/eth/alt/1m/3m/5m/15m/paper/external-data
- 证据类型：论文摘要证据（含 section snippets）

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = “leader close → follower next-open continuation” 本身。**
> 不是纯 filter，不是解释性宏观相关性；它可以直接写成带 entry / exit / sizing / risk / cost 的事件驱动 raw alpha。

## 1) 这次到底 intake 了什么
这次主看：

1. **Xu, D., Li, B., Singh, T., Chen, X., & Li, J. (2025). _Cross-market overnight time-series momentum_. Journal of International Financial Markets, Institutions and Money, 105, 102239.**
   - DOI: `10.1016/j.intfin.2025.102239`
   - DOI URL: `https://doi.org/10.1016/j.intfin.2025.102239`
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1042443125001295`
   - Crossref: `https://api.crossref.org/works/10.1016/j.intfin.2025.102239`
   - Repo URL: 未见官方公开代码仓库
2. 论文直接接在前序 intraday momentum 文献之后，尤其是：
   - **Li, Z., Sakkas, A., Shen, Y., & Tessaromatis, N. (2022). _Intraday time series momentum: Global evidence and links to market characteristics_. International Review of Financial Analysis, 80, 102008.**

这篇 paper 的 headline 是国际股票市场：**前一日美股最后半小时收益，可以预测其他市场次日开盘后第一半小时收益。**

但对我们现在这个 short-cycle crypto desk，更值钱的不是“国际股市有跨夜动量”这句结论，而是它给了一个**很清晰、可以直接迁移到 24/7 crypto 的 raw alpha 模板**：

- **leader 明确**：US close impulse
- **gap 明确**：中间存在不可交易或不主做的等待空窗
- **follower window 明确**：下一个 synthetic open / liquidity reset / session handoff
- **动作明确**：做 continuation，而不是随便把它降级成 regime gate

## 2) 论文最值钱的结论（人话版）
### 一句话结论
**前一日美股临收盘最后半小时的方向，不会只停留在美股本地；它会跨过 overnight gap，在其他市场下一次开盘最初半小时继续释放。**

### 一句话 desk 化
对 crypto 来说，最可迁移的读法不是“美股和 crypto 长期相关”，而是：

> **把美股 cash close 看成一个“外部 session boundary shock”，然后去交易 crypto 在下一个 synthetic session open 的 delayed catch-up。**

这比继续把它写成 overlap 时段的即时跟随更有意思，因为它测试的是：
- 不是同步共振，
- 而是**跨时段、带等待 gap 的延续信息**。

## 3) 3 个关键数据点
1. **统计预测力不是只在样本内好看。**
   论文摘要与引言 section snippets 明确写到：作者对 **15 个非美国发达市场** 的“次日首半小时收益”做 time-series predictive regressions，发现 **前一日美国市场最后半小时收益具有显著的 in-sample 与 out-of-sample 预测力**。

2. **策略层面不是纸上显著性，而是可交易。**
   作者构造的 **COTSM（cross-market overnight time-series momentum）** 策略，直接用 **US 最后半小时 return** 作为信号，在次日各国际市场最初半小时做多/做空；结果是：
   - **12 个市场** 取得显著正收益；
   - **11 个市场** 的 Sharpe ratio 超过被动 buy-and-hold benchmark。

3. **扣了更真实的交易摩擦后，edge 没有整体蒸发。**
   论文用 **可交易 ETF 代理** 做 robustness check，并纳入“reasonable transaction costs”；结果是：
   - **超过半数市场** 在成本后仍保留 excess returns；
   - 策略在 **更低 spread** 或 **更高信息不确定性** 的市场更稳。

这 3 个点对我们很重要，因为它说明：
- 这不是单纯解释 paper；
- 不是只有 beta 相关；
- 也不是“一加成本就死”的那种最脆弱 anomaly。

## 4) 为什么它和当前 desk 直接相关
### 4.1 它补的不是旧的 overlap 跟随，而是“等待 gap 后的延续”
我们最近已经积了不少：
- overlap 内的 cross-asset follow-through
- crypto 内部 lead-lag
- pairs / basis / funding / microstructure

但 **“外部 leader 已经收盘 / 信息已定格 / follower 在下一个可交易边界补动”** 这一类，仍然是素材池里相对稀缺的一块。

这类 alpha 的好处是：
1. **entry clock 很干净**：不是全天候扫信号，而是 session boundary event-driven。
2. **解释更稳定**：靠的是信息扩散与跨时区配置调整，不是纯粹 bar 噪声。
3. **天然适合 1m/3m/5m/15m**：因为执行发生在 boundary 后的前几根 bar，不需要持仓很久。

### 4.2 它不是纯外部 filter，而是可写成完整策略
很多“外部市场影响 crypto”的材料，最后都只剩一个 vague risk-on/risk-off gate。

这篇不一样：它给的是**明确动作链**：
- 看 leader close 的方向和强度；
- 在 follower next-open 立刻开仓；
- 持有一个短而固定的窗口；
- 成本后评估是否保留。

这就是 raw alpha，不是只配角化成 filter。

## 5) desk 化后的最小策略草图
## 5.1 信号定义：先别硬抄“国际股市开盘”，要改成 crypto 的 synthetic session open
由于 crypto `24/7` 没有官方开收盘，我们需要**人为定义 synthetic boundary**。最自然的第一版：

- **leader**：`QQQ` / `SPY` / `NVDA` 在 US cash close 前最后 `15m` 或 `30m` 的 return
- **boundary**：`20:00 UTC`（美股现金收盘，DST 视情况换算）
- **follower**：`BTCUSDT`、`ETHUSDT`、高流动 alt basket
- **synthetic open 候选**：
  1. `20:00 UTC` 之后的前 `15m/30m/60m`（零等待版）
  2. `00:00 UTC` 之后前 `15m/30m`（带数小时 gap 的“准跨夜版”）
  3. `08:00 UTC` 或 `13:30 UTC` 之前后（亚洲/欧洲/美股重启边界版）

如果要更接近论文的“close → next-open”结构，**优先测 `00:00 UTC` synthetic open**：
- `signal`：US close 最后 `15m/30m` return
- `trade window`：BTC/ETH 在 `00:00 UTC` 后前 `15m~60m`

## 5.2 最小 raw alpha 版本（可直接回测）
### 版本 A：single-asset directional
- 频率：`15m` 起步，向下细化到 `5m`
- Long：若 `QQQ` 与 `NVDA` 的 US close 末段收益都 > rolling same-clock `q80`
- Short：若二者都 < rolling same-clock `q20`
- Entry：`00:00 UTC` 第一根 `5m/15m` 开盘
- Exit：固定持有 `1~4` 根 bar，或遇到反向 threshold 提前平仓

### 版本 B：leader/follower basket
- Long：US close risk-on shock 后，做多 `ETH + high-beta alt basket`，空 `BTC` 或空 funding-rich crowding basket
- Short：US close risk-off shock 后，做空 `ETH + alt basket`，多 `BTC` 或多防御腿
- 目标：把它从单边 directional 进一步变成 **cross-sectional / relative-value** 结构，减少市场 beta 噪音

## 5.3 sizing / risk / cost
- **sizing**：
  - 初版 `size ∝ shock_strength`，例如 leader close return 的 same-clock percentile 或 z-score
  - 组合内先按 inverse-vol 做 BTC/ETH/ALT 配重
- **risk**：
  - 只在外部 leader shock 足够大时出手，弱信号直接 abstain
  - 宏观大事件夜（FOMC / CPI / NFP / NVDA earnings）单独分 bucket
  - 若 crypto 在 `US close → synthetic open` 之间已提前走完同方向大部分波幅，则 veto
- **cost**：
  - 第一轮就按 `4 / 6 / 8 / 10 bps` round-trip 压力测试
  - 若只在最弱摩擦下成立，不进主池

## 6) 这篇 paper 最值得 desk 偷的“旁支想法”
这轮不必死抄 headline。对我们最值钱的旁支其实有两个：

### 旁支 1：**等待 gap 本身可能是 alpha 放大器**
很多人会默认“有 edge 就该立刻 trade”。
但这篇 paper 的隐含启发是：
- 某些信息不是在同步时段立刻 fully priced；
- 反而会在**下一次市场重启 / 流动性重置 / 参与者换班**时继续释放。

这对 crypto 很重要，因为我们也有很多“伪开盘”：
- `00:00 UTC`
- `08:00 UTC`
- `13:30 UTC`
- funding reset 前后
- 主要地区交易员切换班次

### 旁支 2：**更低 spread / 更高 uncertainty 的 pocket 更好**
论文对国际股市的截面分析说明：
- spread 低的市场更适合做；
- 信息不确定性高的市场 edge 更强。

crypto desk 化后可以直接翻译为：
- 优先做 **大币 / 深流动** 的 execution shell；
- 把 alpha expression 放在 **高 beta、对外部 risk signal 更敏感** 的腿上；
- 或反过来用 `BTC` 做 hedge，把 `ETH/ALT` 当主要收益腿。

## 7) 风险与保留意见
1. **论文原生不是 crypto。**
   这是最大的保留：从国际股票“开盘半小时”迁移到 crypto synthetic open，不能默认一比一成立。

2. **crypto 没有天然 open。**
   你得自己定义 session boundary，而不同 boundary 可能差很多。若 boundary 定错，alpha 可能直接消失。

3. **它可能只在 event day 很强。**
   若 edge 主要来自 CPI / FOMC / 财报夜，那它更像 event overlay，不是常规日常 raw alpha。

4. **与已有 overlap alpha 需要去重。**
   如果它其实只是我们已有 `US cash overlap` 跟随的延迟版，那么应作为同一家族 pocket，而不是重复计算独立 alpha 数量。

## 8) 下一步怎么测（明确动作）
按优先级直接做：

1. **先验证最小 transfer，不碰复杂组合。**
   - leader：`QQQ`、`NVDA`
   - follower：`BTCUSDT`、`ETHUSDT`
   - signal：US close 最后 `15m/30m` return percentile
   - trade：`00:00 UTC` 后前 `15m/30m/60m`
   - 指标：mean return、hit-rate、Sharpe、t-stat、cost 后 pnl/trade

2. **做 boundary sweep。**
   把 `20:00 / 00:00 / 08:00 / 13:30 UTC` 都测一遍，确认 edge 是“close 后立即释放”，还是“隔几个小时在下一次流动性切换时释放”。

3. **做 holding sweep。**
   在 `1m/3m/5m/15m` 上分别测持有 `1/2/4/8` 根 bar，找真实 half-life。

4. **做单边 vs 相对价值。**
   - 单边：BTC / ETH direct long-short
   - 相对价值：long ETH / short BTC，long alt basket / short BTC
   看 alpha 更像 market beta 还是 high-beta spillover。

5. **做 event-day 剔除。**
   把 FOMC、CPI、NFP、NVDA earnings night 单独移除后重跑。若移除后大幅塌陷，则把它降级成 event-conditional alpha。

6. **做成本 cliff。**
   至少跑 `4 / 6 / 8 / 10 bps`；只要在 `8 bps` 以上全面转负，就别急着进优先复现池。

> **最该先跑的正式版本：**
> `QQQ + NVDA US close last-30m shock -> BTC/ETH at 00:00 UTC synthetic open for next 15m~60m`，先用公开 `15m/5m` 数据做一版，再决定是否下钻到 `1m/3m`。

## 9) 为什么这轮它值得排在前面
因为它虽然不是 crypto 原生论文，但它满足我们当前 intake 的几个关键点：
- **base alpha 清楚**：close-to-next-open continuation
- **可独立复现**：公开行情就能做
- **可直接落成完整策略**：entry/exit/sizing/risk/cost 都能写
- **能补素材池的空白**：不是又一篇 funding / pairs / generic ML
- **天然适配短周期**：执行窗口就是 next `1m/3m/5m/15m`

所以它比“再写一篇纯解释型外部相关性”更值得进池。

## 10) 文件与页面
- 研究笔记：`research/quant_digests/2026-03-28_0057_us-close-crypto-synthetic-open-spillover-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-28_0057_us-close-crypto-synthetic-open-spillover-alpha.html`

## Sources
1. **Xu, D., Li, B., Singh, T., Chen, X., & Li, J. (2025). _Cross-market overnight time-series momentum_. Journal of International Financial Markets, Institutions and Money, 105, 102239.**
   - DOI: `10.1016/j.intfin.2025.102239`
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1042443125001295`
   - DOI URL: `https://doi.org/10.1016/j.intfin.2025.102239`
   - Crossref URL: `https://api.crossref.org/works/10.1016/j.intfin.2025.102239`
   - Repo URL: 未见官方公开仓库
2. **ScienceDirect abstract / section snippets**（用于提取摘要、方法与 robustness 描述）
   - `https://www.sciencedirect.com/science/article/abs/pii/S1042443125001295`
3. **Li, Z., Sakkas, A., Shen, Y., & Tessaromatis, N. (2022). _Intraday time series momentum: Global evidence and links to market characteristics_. International Review of Financial Analysis, 80, 102008.**
   - 作为该文直接前序文献，用于理解 intraday → overnight spillover 的研究链条
