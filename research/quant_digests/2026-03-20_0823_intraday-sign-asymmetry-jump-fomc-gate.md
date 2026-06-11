# 别把 15m follow-up 默认成“只做延续”：`intraday predictor sign（正/负并存）+ no-jump/no-FOMC` 更像 breakout-short / Fib / EMA-PSAR 的 direction-aware gate
- 时间：2026-03-20 08:23 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/intraday-predictability/momentum-reversal/sign-asymmetry/jump/fomc/regime-gate/filter/crypto/5m/15m
- 证据类型：论文证据

## 1. 这次看了什么
这次看的是 **Wen, Bouri, Xu, Zhao (2022)**：*Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both*。这篇最值得我们 desk 借的，不是“又确认了动量存在”，而是它明确给出：**同一套日内预测关系里，既有正向延续，也有负向反转；而且在 no-jump / no-FOMC / low-liquidity 条件下更稳定。**

## 2. 核心结论
- **一句话核心结论**：对 Crypto 5m/15m，`follow-up` 不该默认等于“继续追原方向”；更像要先过一个 **direction-aware（正/负号）+ regime-aware（jump/FOMC）** 的门。
- **一句话证明方式**：论文用 BTC 高频数据（5m 构造小时收益）做全日内时段对的 IS/OOS 可预测性筛选，并做策略经济价值评估，再在 ETH/LTC/XRP 与其他平台做稳健性复核。
- 关键数据点 1：主实验基于 **5 分钟 BTC 数据构造小时收益**，不是日线或周线口径。
- 关键数据点 2：结果汇报口径只保留 **IS 显著 + OOS R²为正** 的“有效预测对”，避免只看 in-sample 好看配对。
- 关键数据点 3：作者明确报告：crypto 的日内预测关系**不只正号（continuation）**，也存在**负号（reversal）**；并且在 **no-jump / no-FOMC / low-liquidity** 子样本中更强。
- 经济含义：基于有效 predictor 的 timing 策略，相比基准策略有更高经济价值（文内给出“substantially higher profits”结论）。

## 3. 为什么和当前项目有关
这篇和三条收口线是直接相关的，而且是“低侵入改造”：不改你现有 trigger，本质上是给它加一个更诚实的后验门。

- `V3 final-verdict / breakout-short follow-up`
  - 现在很多 follow-up 默认“破了就追”。
  - 这篇提示我们：先看当前时段关系是 **正号还是负号**。若该窗口偏负号（易反转），就把 follow-up 降级为 veto 或减仓。

- `Fibonacci confirmation / retest_hold`
  - retest 后是否继续顺势，不该只看“回踩到位”。
  - 可加 `sign gate`：若当前 predictor 对后续收益符号是负，`retest_hold` 只做观察不做放行。

- `EMA / PSAR raw alpha focus`
  - EMA/PSAR raw trigger 可以保留为 `scan`。
  - 真正入场由 `raw trigger × intraday sign × regime(no-jump/no-FOMC)` 决定，优先把它定位成 admission/veto 层，而不是再堆新指标本体。

## 4. 可复刻的最小实验（先做这个）
### 研究假设
在 15m 上，`direction-aware + no-jump/no-event` gate 能降低假延续率（false-follow），优于“统一按 continuation 追价”。

### 最小实现
1. **数据源（公开可得）**
   - 价格：Binance 公共 K 线 API（5m/15m，公开、近实时更新）。
   - 事件：FOMC 日程（Federal Reserve 官网公开日历，低频更新，年内固定发布时间表）。
2. **信号构造**
   - 用 rolling 90 天估计若干日内 predictor 对（先从 15m→后续 15m/30m 收益开始）。
   - 仅保留 `IS 显著 + OOS R² > 0` 的 predictor，并记录符号（+1 continuation / -1 reversal）。
3. **接入三条线**
   - baseline：现有 breakout-short / Fib / EMA-PSAR 规则。
   - gate 版：仅当 `predictor_sign` 与候选方向一致且处于 `no-jump/no-FOMC-window` 时放行；否则 veto 或 0.5x 仓位。
4. **最先看的指标**
   - `post-cost expectancy`
   - `false-follow rate（入场后 N=4~8 bars 快速反向）`

### 低频外部数据定位说明
FOMC 本质是低频公开日程数据，**只应作为 regime gate / risk overlay**，不应伪装成逐根 15m 主信号。

## 5. 风险与保留意见
- 论文主频率是“5m 构造小时收益”，映射到纯 15m 时，预测对结构可能变化，必须做滚动 OOS。
- 文中“无跳跃/无 FOMC 更强”是子样本结论，落地时要防止过度条件化导致样本过稀。
- 交易摩擦、资金费率和滑点在 perp 里更敏感，若不加成本，结果会偏乐观。

## 6. 来源
1. Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). *Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both*. **The North American Journal of Economics and Finance**.
   - DOI: `10.1016/j.najef.2022.101733`
   - Readable URL: `https://doi.org/10.1016/j.najef.2022.101733`
   - Article URL: `https://www.sciencedirect.com/science/article/pii/S1062940822000833`
   - Repo URL: `N/A (paper did not provide official code repository)`
2. Board of Governors of the Federal Reserve System. *FOMC Calendars and Information*.
   - URL: `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`
   - 公开性：公开网页
   - 更新频率：低频（按年度/会议计划更新）
