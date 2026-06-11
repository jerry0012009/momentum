# 别把这份 2026 Deribit analyzer 继续只读成 hard no-arb 扫描器：对 short-cycle desk，更该先测的是「same-strike IV term-structure inversion × delta/liquidity gate」这条 options relative-value raw alpha

- 时间：2026-04-04 13:35 UTC
- 类型：2026 GitHub 新 repo source audit（`src/analysis/calendar_spread.rs` + `calendar_arb.rs` + `opportunity.rs`）+ Deribit BTC options 公共 live snapshot sanity check + Crossref metadata grounding
- 主题类型：raw alpha
- 基础 alpha：**同 strike、同类型（call/put）的近月/远月 implied vol term structure 偏离，会向更正常的期限结构回归；交易壳是 delta-aware calendar spread，而不是裸方向赌 BTC。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/options/relative-value/stat-arb/calendar-spread/implied-volatility/term-structure/delta-aware/liquidity-gate/deribit/btc/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 源码证据 + 交易所公共 live 数据

## 1. 先回答一句：base alpha 是什么？

**base alpha = same-strike / same-type 的近月-远月 IV term structure 偏离回归。**

这不是 shared gate，也不是纯解释。
它本体就是一条 **options relative-value / stat-arb raw alpha**：
- 做的是同一条 strike-term slice 的相对错价；
- 收益来自 **IV term structure 回归**，不是 BTC 单边方向；
- 执行形式天然更接近 `1m/3m/5m/15m` 的**事件扫描 + 分钟级挂单/吃单**，而不是日频慢信号。

## 2. 为什么这轮选它，而不是继续在 breakout / perp reversal 上内循环？

因为最近 intake 已经连续补了不少：
- cross-sectional ranker
- TSMOM / trend shell
- pairs / cluster relative value

这轮更值得补一条**没在索引里单独展开过**、但仍属于 raw alpha 的新分支：
**BTC options 期限结构相对价值。**

而且这次我不是照抄 repo 最醒目的 box / parity / hard no-arb headline，而是按你这轮的新规则，主动挑了一个**更适合 desk 最小实验**的旁支：

> **hard calendar arb 现在 live 上几乎没有；但 softer 的 IV calendar spread 信号还在，而且可直接转成分钟级扫描策略。**

这比继续写一篇“又一个形态确认”更能扩充素材池。

## 3. 这份 repo 真正给了什么？

主材料是 **dada63924 (2026), `deribit-analyzer`**。
其中最值得拿走的不是 UI / 报警器，而是 `calendar_spread.rs` 里已经写明的一条完整思路：

1. 先按 **(strike, option_type)** 分组；
2. 对相邻到期的 near / far 合约，读取 `mark_iv`、bid/ask、vega、underlying；
3. 若 `|IV_near - IV_far| > threshold`，就建一笔 **calendar spread**：
   - `near IV > far IV` → 卖近买远；
   - `near IV < far IV` → 买近卖远；
4. 用 `vega_near + vega_far` 估一个“收敛一半”时的收益；
5. 扣两腿期权费率，得到 repo-like `expected_profit`。

也就是说，repo 已经把这条线写成了：
- **entry 条件**
- **方向判别**
- **收益近似**
- **风险等级**

这就足够支持一篇 raw-alpha digest，而不是只把它当成“期权监控器”。

## 4. 先做 live honesty check：当前 Deribit 公共快照告诉了我们什么？

我用 Deribit BTC options 公共接口，对当前全市场做了一次最小快检（`2026-04-04 13:35 UTC`）：

### 4.1 hard calendar arb：**当前几乎没有**

按 repo `calendar_arb.rs` 的硬约束口径：
- 检查了 **677** 个相邻到期、同 strike、同类型的 near/far 组合；
- 条件是 `near_bid > far_ask`（扣两腿 fee 后仍为正）；
- **命中数 = 0**。

这很关键：
**如果把这份 repo 只读成 hard no-arb calendar scanner，这一轮其实没什么可做。**

### 4.2 soft IV calendar spread：**信号还在，但大多在翼部**

改用 `calendar_spread.rs` 的 softer 口径后：
- `|IV_near - IV_far| > 15 vol pts` 的组合有 **31** 个；
- call / put 基本对半：**15** 个 call，**16** 个 put；
- 但若加最粗的 moneyness 过滤：
  - `0.7 ~ 1.3` 只剩 **3** 个；
  - `0.8 ~ 1.2` 只剩 **1** 个；
  - `0.9 ~ 1.1` 是 **0** 个。

这说明什么？

> **headline 信号数不少，但绝大多数都不是“可直接放心交易的中间区域 term-structure 错价”，而是远翼报价扭曲。**

### 4.3 当前最极端的 live 信号长什么样？

当前 top signal 是：
- `BTC-24APR26-120000-C` vs `BTC-26JUN26-120000-C`
- `near IV = 85.93`，`far IV = 52.77`
- `IV diff = 33.16 vol pts`
- repo-like 粗估收益约 **$183.8**
- 但它的平均 moneyness 约 **1.78**，near delta 只有 **0.0025**

翻成人话：
**看起来很肥，但本质是远 OTM 翼部 quote。**

所以这条 alpha 现在最诚实的读法不是“有 31 个机会”，而是：

> **有一堆 tail quotes 在喊价差，但真正值得 first verdict 的，只能是加过 delta / moneyness / liquidity gate 之后的那一小撮。**

## 5. 对 desk 来说，应该怎么把它改写成完整策略？

## 5.1 Entry

第一轮别直接照 repo 的 `abs(iv_diff) > threshold` 裸跑。
应至少改成四层门槛：

1. **term-structure trigger**
   - `IV_near - IV_far > 12~18 vol pts`，做 `sell near / buy far`
   - `IV_near - IV_far < -12~-18 vol pts`，做反向

2. **delta gate**
   - 只做 `|delta|` 在 `0.10 ~ 0.40` 或 `0.60 ~ 0.90` 的腿
   - 直接剔除 `|delta| < 0.05` 的纯翼部报价噪音

3. **liquidity gate**
   - 两腿都有正 bid/ask
   - spread 不超过某个上限
   - 至少一腿有可接受的挂单量 / OI / 近时段成交痕迹

4. **same-expiry neighbor only**
   - 先只做相邻到期 near/far
   - 别一上来跨太多期限，避免把 term-structure 变成 macro vol bet

## 5.2 Exit

先用最朴素的三种退出：
- `IV diff` 回到 `5 vol pts` 内；
- 到达最大持有时间（例如 `6h / 12h / 24h`）；
- 任一腿报价消失或 spread 恶化到不可平。

## 5.3 Sizing

这条线不要按名义资金等权。
更合理的是：
- **vega-neutral 或近似 vega-balanced sizing**；
- 单笔风险不超过组合可承受 vega 的 `5%~10%`；
- 第一轮只做最小 size，先确认 signal persistence，不急着做容量。

## 5.4 Cost / Risk

至少显式记三类成本：
- 两腿手续费；
- 半个 spread / 一个 spread / 1.5 个 spread 三档；
- 由于腿不完全同 delta / 同 gamma 带来的方向暴露。

真正的主风险不是“term structure 不回归”，而是：
- 你其实买到了 **illiquid wing quote**；
- 或 near leg 的 theta / gamma 太快，把“IV 回归”还没兑现前先磨死。

## 6. 所以这条线当前最诚实的 verdict 是什么？

**Verdict：值得进研究池，但必须从“calendar IV spread + practical gate”读，不该从“裸 IV diff / 裸 no-arb”读。**

更直白一点：
- **hard arb 版本：当前 live 不成立；**
- **soft IV spread 版本：有信号，但大多集中在极端翼部；**
- **真正可测版本：加 delta / moneyness / liquidity gate 后，去看分钟级 persistence 和收敛速度。**

这正符合你这轮允许的“从 repo 里拆一个更适合 desk 的旁支想法”：
**headline 不是我们最该抄的，真正该抄的是更可移植的 branch。**

## 7. 下一步怎么测（直接排最小实验）

### 实验 A：先做 7 天分钟级 snapshot persistence

每 `1m` 或 `5m` 抓一帧 Deribit BTC options：
- 对相邻到期 same-strike same-type 计算 `IV_near - IV_far`
- 只保留 `|delta| ∈ [0.10, 0.40] ∪ [0.60, 0.90]`
- 记录 signal 出现频率、持续时长、回归半衰期

先回答最核心的问题：
**这条 edge 是“偶尔报价毛刺”，还是“能持续几分钟到几十分钟的真 pocket”？**

### 实验 B：做 delta-aware executable backtest shell

对每次触发事件：
- `entry`：signal 连续 `2` 帧仍在；
- `exit`：IV diff 回到 `5` vol pts 内 / 超时 / 流动性丢失；
- `cost`：`0.5x / 1.0x / 1.5x spread` 三档；
- `sizing`：vega-balanced。

目标不是先追最优收益，而是先确认：
**cost 后还剩不剩。**

### 实验 C：用 hard-vs-soft 双轨避免自欺

并行记录两套口径：
- **hard**：`near_bid > far_ask`
- **soft**：`abs(iv_diff) > threshold`

如果最后发现：
- hard 永远为零；
- soft 只在尾翼短闪；

那就该降级，不要硬留在素材池里。

## 8. 风险与保留意见

- 这条线**当前证据强在“源码定义完整 + live 结构清楚”**，不强在“已经证明能净赚钱”；
- repo 的收益估法是 **vega × IV convergence** 的近似，不是完整 Greeks PnL；
- BTC options 的翼部报价很容易给出漂亮但不可交易的假信号；
- 所以第一轮研究重点不该是回测利润，而该是：
  1. signal persistence
  2. delta/liquidity 过滤后剩多少
  3. cost 后是否还活

## 9. 来源

1. **dada63924 (2026). _deribit-analyzer_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/dada63924/deribit-analyzer`  
   - Repo URL: `https://github.com/dada63924/deribit-analyzer`

2. **Repo source files used in this digest**  
   - Calendar spread analyzer: `https://raw.githubusercontent.com/dada63924/deribit-analyzer/main/src/analysis/calendar_spread.rs`  
   - Hard calendar arbitrage analyzer: `https://raw.githubusercontent.com/dada63924/deribit-analyzer/main/src/analysis/calendar_arb.rs`  
   - Opportunity model: `https://raw.githubusercontent.com/dada63924/deribit-analyzer/main/src/analysis/opportunity.rs`

3. **Zulfiqar, N., & Gulzar, S. (2021). _Implied volatility estimation of bitcoin options and the stylized facts of option pricing_. Financial Innovation.**  
   - DOI: `https://doi.org/10.1186/s40854-021-00280-y`  
   - Readable URL: `https://doi.org/10.1186/s40854-021-00280-y`

4. **Chen, T., Deng, J., & Nie, J. (2024). _Implied volatility slopes and jumps in bitcoin options market_. Operations Research Letters.**  
   - DOI: `https://doi.org/10.1016/j.orl.2024.107135`  
   - Readable URL: `https://doi.org/10.1016/j.orl.2024.107135`

5. **Bloch, D. (2013). _From Implied Volatility Surface to Quantitative Options Relative Value Trading_. Wilmott.**  
   - DOI: `https://doi.org/10.1002/wilm.10216`  
   - Readable URL: `https://doi.org/10.1002/wilm.10216`

6. **Deribit API Documentation.**  
   - Readable URL: `https://docs.deribit.com/`

## 10. 本地 artifacts

- `reports/artifacts/quant_digests/deribit_iv_calendar_spread_20260404/summary.json`
- `reports/artifacts/quant_digests/deribit_iv_calendar_spread_20260404/top_soft_signals.csv`

一句话收尾：**这轮真正值得拿走的不是“Deribit 上出现了很多 calendar spread 机会”，而是“hard arb 已经很干净，但 delta-filtered IV term-structure pockets 可能还活着，值得做分钟级 persistence first verdict”。**
