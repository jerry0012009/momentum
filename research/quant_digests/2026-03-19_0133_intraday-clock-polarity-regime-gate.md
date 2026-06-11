# 别把 15m 当成全天同一套逻辑：Wen et al. (2022) 更像在提醒我们先测 `intraday clock polarity + event blackout` shared gate
- 时间：2026-03-19 01:33 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/intraday/momentum/reversal/regime/filter/event-blackout/crypto/15m
- 证据类型：论文证据（摘要 + section snippets，可复现方法级证据）

## 1. 这次看了什么
这次看的是 **Wen, Bouri, Xu, Zhao (2022)** 关于 crypto 日内可预测性的论文。对我们 desk 最有价值的旁支，不是“又找到一个新 alpha”，而是：**同一天不同时段，后续回报关系有时是顺延续（momentum），有时是反向（reversal）**，因此 15m 不该全天同一个 admission 规则。

## 2. 核心结论
- **一句话核心结论：** 这篇论文更像在说“先判时段极性，再决定放行 continuation 还是 retest”，而不是默认所有 15m 信号都按同一种交易逻辑执行。
- **一句话说明它怎么证明：** 作者用 BTC 的 5-min 数据聚合到 hourly，逐对检验早时段回报对晚时段回报的 IS/OOS 预测关系，只保留 IS 显著且 OOS R² 为正的预测对，并再做经济价值回测。
- 文中明确指出：crypto 的日内预测关系**既有正号也有负号**（不是单向 momentum 世界）。
- 论文还报告：可预测性在 **no-jump / 无 FOMC 公告 / 低流动性** 子样本里更强。
- 结果并非 BTC 单点现象：作者对 **ETH / LTC / XRP** 做了稳健性检查。

## 3. 为什么和当前三条收口线直接相关
- 对 `V3 final-verdict / breakout-short follow-up`：可把“该不该追 follow-up”从图形判断，升级成“当前小时极性是否支持 continuation”。
- 对 `Fibonacci confirmation / retest_hold`：若小时极性偏 reversal，Fib 回踩确认应优先；若偏 momentum，则应收紧 retest 入场。
- 对 `EMA / PSAR raw alpha focus`：可作为 shared allow/deny gate（甚至仓位缩放），减少“全天同权”导致的无效开仓。

## 4. 可复刻的最小实验（5m/15m）
### 研究假设
把 15m 入场映射到“小时极性（continuation vs reversal）”后，成本后期望值会高于 baseline；再叠加事件黑名单（FOMC 窗口）可进一步减少坏单。

### 一个可计算定义
- 用 5m 数据合成 hourly 回报 `r(h,d)`；
- 在 rolling 180d 上估计小时对 `(h -> h+1)` 的相关/回归符号：
  - `polarity_h = sign(corr(r_h, r_h+1))`
  - 仅当 `t-stat > 1.96` 才启用；否则 `neutral`；
- 15m 执行层：
  - `polarity=+1`：放宽 breakout/EMA-PSAR continuation，收紧 Fib；
  - `polarity=-1`：放宽 Fib retest_hold，收紧 breakout follow-up；
  - `neutral`：half-size 或 no-trade。
- 事件黑名单（外部公开数据）：FOMC 公告日程（Federal Reserve 官网，公开可得，低频更新），公告前后 ±2h 默认减仓或禁开新仓。

### 最小回测切口
- 标的：BTC / ETH / SOL perpetual
- 周期：15m
- 样本：近 365d
- 执行：next-bar open，no-overlap
- 成本：6/10/15 bps per side
- 对照：baseline vs polarity gate vs polarity+FOMC blackout

### 第一轮先看
- post-cost expectancy
- continuation→failure rate（4~8 bar）
- retest_hold 生存率
- trade retention（别靠砍单伪改善）

## 5. 风险与保留意见
- 该文全文受限，当前证据来自可读摘要与 section snippets；本轮定位为**方法迁移候选**，不是“已验证可直接上盘”。
- 原论文主频是 hourly；映射到 15m 需重新验证稳定性与成本后表现。
- FOMC 在 crypto 中属于低频外部事件，更适合作为 `regime gate / risk overlay`，不应伪装成逐根 15m 主信号。

## 6. 来源
1. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_. The North American Journal of Economics and Finance, 62, 101733.**
   - DOI: `10.1016/j.najef.2022.101733`
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1062940822000833`
   - Repo URL: `N/A`
2. **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). _Market intraday momentum_. Journal of Financial Economics, 129(2), 394–414.**
   - DOI: `10.1016/j.jfineco.2018.05.009`
   - Readable URL: `https://doi.org/10.1016/j.jfineco.2018.05.009`
   - Repo URL: `N/A`
3. **FOMC Calendar（公开事件数据）**
   - 数据源：Federal Reserve Board（公开可得）
   - 更新频率：低频（会议日程级）
   - URL: `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`
