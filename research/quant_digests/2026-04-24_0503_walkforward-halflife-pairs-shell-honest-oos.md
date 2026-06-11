# 别把这份“诚实亏损”的 stat-arb repo 只读成失败案例：对 short-cycle crypto desk，更该先拆的是「walk-forward pair admission × half-life-matched spread fade」这条完整 raw alpha 壳
- 时间：2026-04-24 05:03 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：先筛出通过相关性 + Engle-Granger cointegration 检验的 pair；用 rolling OLS 估计 hedge ratio，构造 `spread = log(A) - (alpha + beta*log(B))`；当 spread z-score 偏离足够大时做均值回归，回到中枢附近退出。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / cointegration / half-life / walk-forward / zscore / mean-reversion / crypto / 15m / 5m
- 证据类型：repo source + repo 回测结论

## 1. 这次看了什么
看了 2026 GitHub 仓 `atharvajoshi01/crypto-stat-arb`。它最有价值的点不是“又做了一遍配对交易”，而是作者把 **pair discovery → signal → sizing → cost → walk-forward → drawdown stop** 串成了一条很完整、而且愿意公开差结果的研究壳。

## 2. base alpha 先说清楚
这篇东西的 **base alpha 很清楚**：

**cointegrated pair spread 的 z-score 均值回归。**

不是 filter，不是 overlay，也不是只给一段 pair selection 代码；它本体就是一条 `relative value / stat-arb / mean reversion` raw alpha。

## 3. 核心结论
- 这份仓最值得拿进素材池的，不是 README 里“production-grade”这类包装词，而是它把完整交易链条写死了：`corr > 0.70` 预筛、`ADF p < 0.05`、half-life `3~30` 天、`entry_z=2.0 / exit_z=0.5 / stop_z=4.0`、单 pair 权重上限 `20%`、walk-forward `2y train / 6m test / 3m step`、round-trip 成本按 `40 bps` 扣。
- 作者给出的真实样本结果其实是**负的**：Kraken 11 币、2025-02~2026-01 OOS，raw annual return `-18.8%`、Sharpe `-2.56`、max DD `-18.4%`；risk-managed 版 annual return `-15.7%`、Sharpe `-2.27`、max DD `-14.6%`。这不是坏事，反而说明这份仓适合当 desk 的 **honest shell**，不是只会挑顺眼样本讲故事。
- 同一份 README 也给了 synthetic sanity check：最佳 Sharpe `1.40`，最优阈值大致在 `entry_z=2.5 / exit_z=0.5 / 20bps cost`。这说明问题更像是“真实 crypto 成本和 universe 让 edge 变薄”，而不是“这条 alpha 在逻辑上完全站不住”。
- repo 列出的真实样本 pair 也很具体：`SOL/DOGE` half-life `8.4` 天、ADF `p=0.016`、corr `0.91`；`ETH/DOT` half-life `10.1` 天、ADF `p=0.018`、corr `0.90`。对我们最有启发的，不是具体哪一对币，而是 **window 跟 half-life 绑定** 这个写法比“固定 60 根 z-score 窗口”更像可迁移的研究对象。

## 4. 为什么和当前 desk 直接相关
bot7 当前优先级是补 **可独立复现、可直接进复现池的 raw alpha**。这份 repo 符合，因为它不是“只证明 pair 可能有效”，而是已经把：
- alpha 本体：cointegration spread fade
- admission：相关性 + cointegration + half-life 过滤
- entry/exit：z-score 阈值
- sizing：dollar-neutral + single-pair cap
- risk：pair/portfolio drawdown stop、vol scaling、30 天 recoint
- cost：双腿 round-trip 统一扣成本

全都写出来了。对 short-cycle desk，这正好适合作为 **15m signal / 5m execution** 的最小完整壳，而不是再造一个只有信号、没有组合和成本的半成品。

## 5. 策略拆解（必填）
- 方向属性：relative value / stat-arb / mean reversion
- 基础 alpha：cointegrated spread z-score fade
- regime / admission：先做相关性和 Engle-Granger cointegration 过滤，再用 half-life 把过慢/过快 pair 剔掉
- filter / veto：只保留 half-life 在可交易区间的 pair；rolling OLS / rolling z-score 依赖历史稳定性
- risk / sizing / execution overlay：dollar-neutral、单 pair `20%` cap、drawdown stop、vol scaling、recoint health check、round-trip 成本显式扣减

## 6. 可复刻的最小实验
- 研究假设：**pairs raw alpha 不是没有，而是很多 repo 把“pair 是否该交易”与“z-score 怎么做”混在一起。对 desk 更值得先测的是：half-life-matched rolling window 能不能比固定窗口更稳。**
- 最小定义：
  1. 选 Binance USDⓈ-M 8~12 个 liquid majors / liquid alts；
  2. 每周或每 3 天做一次 Engle-Granger pair admission；
  3. 只保留 `corr > 0.7`、`ADF p < 0.05`、half-life 落在一个可交易区间的 pair；
  4. 对每个 pair 用 `window = max(int(2 × half_life), 20)` 计算 rolling beta 与 rolling z-score；
  5. `|z| > 2.0` 入场，`|z| < 0.5` 出场，`|z| > 4.0` 止损；
  6. 统一扣 `2 / 4 / 6 bps` friction ladder，对照 fixed-window 版本。
- 最小回测切口：`15m` 主信号，`5m` child execution / early-exit，近 `120~180d`。
- 最该先看：
  - 成本后 `avg net bps/trade`
  - active pair 数量与 turnover
  - fixed-window vs half-life-window 的 OOS 差异

## 7. 下一步怎么测
1. **先做最朴素版本**：只留 Engle-Granger + half-life + z-score，不要一开始就加 basket、Kalman、regime classifier。
2. 做一组最关键对照：
   - A：固定 `60` 根 rolling window
   - B：`2 × half-life` 自适应 window
3. 每组都跑 `entry_z=1.5 / 2.0 / 2.5` 与 `2 / 4 / 6 bps` friction ladder，看 edge 是不是只存在于低成本假设。
4. 若 `15m` 主信号有存活迹象，再把 `5m` 只用于更细的平仓与 time-stop，不要把 admission 也推得过快。

## 8. 风险与保留意见
- 这份 repo 的原生频率是 `1d`，不是直接为 `5m/15m` 写的；所以它更适合被读成 **完整壳 + 参数语义来源**，而不是“作者已证明短周期 crypto 可赚”。
- README 里公开的真实样本结果为负，说明 pair raw alpha 在真实成本前很容易变薄；这也正是它值得 desk 吸收的地方——它提醒我们别再把 pairs 当免费午餐。
- 若把 half-life 太短的 pair 也硬塞进 `15m`，很容易只剩 turnover，没有 edge；因此 short-cycle 版本必须把 **trade count / holding time / cost per spread cycle** 放在第一位看。

## 9. 一句话总结
**这份 repo 最值得 desk 学的，不是“pairs 一定赚钱”，而是如何把一条 cointegration spread fade raw alpha 写成诚实、可复核、可快速降采样到 `15m/5m` 的完整研究壳。**

## 10. 来源
- Author / Year / Title / Venue
  - atharvajoshi01. (2026). *crypto-stat-arb*. GitHub repository.
  - DOI：N/A
  - Readable URL：https://github.com/atharvajoshi01/crypto-stat-arb
  - Repo URL：https://github.com/atharvajoshi01/crypto-stat-arb
- Key source used
  - Raw README URL：https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/README.md
  - Raw pairs.py URL：https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/pairs.py
  - Raw signals.py URL：https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/signals.py
  - Raw portfolio.py URL：https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/portfolio.py
  - Raw risk.py URL：https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/risk.py
  - Raw backtest example URL：https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/examples/real_data_backtest.py
