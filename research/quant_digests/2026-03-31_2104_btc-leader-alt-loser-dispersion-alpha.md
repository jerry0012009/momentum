# 别把这份 HKU x Avenir 竞赛 repo 只看成 cointegration 框架：更该先测的是「BTC leader × 24h 弱势 alt loser basket」relative-value raw alpha
- 时间：2026-03-31 21:04 UTC
- 类型：GitHub 新仓库源码审阅 + Binance USDⓈ-M Perpetual 公开 `1h/15m` 本地 quick check
- 主题类型：raw alpha
- 基础 alpha：**BTC 相对强势延续 + 过去 24h 弱势 alt 继续跑输**，即 long BTC、short 过去 24h 为负收益的 alt basket，吃的是 **leader-vs-loser dispersion / relative-value continuation**，不是 generic pairs filter
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/cross-sectional/dispersion/btc-vs-alt/loser-basket/24h-lagged-return/continuation/variance-scaling/hourly/15m/5m/1m/3m/repo/public-data/cost
- 证据类型：工程经验 + public-data replication

## 1. 这次看了什么
这次主看的是 2026 GitHub 新仓库 `LevRoz630/hku-avenir-2nd-round`。它是 HKU x Avenir Web3 量化比赛第二轮的实盘/回测框架，README 明写：**12 周 Binance perp 竞赛、全球 1,171 名参赛者、作者队伍拿到 top 11**。repo 里当然有大家更熟悉的 `pairs` / `cointegration` 线，但对当前 desk 来说，真正更值得先收进 raw alpha 池的，其实是那条没那么显眼的 `v1_ls`：

- **long BTC futures**；
- **short 过去 24h 收益为负的 altcoins**；
- alt 权重按 `abs(24h return) / variance` 分配；
- **只保留权重大于 10% 的币**，减少碎仓和手续费；
- **每日再平衡**，另带 ratio-drift 触发；
- position manager 里还有 **15% 单仓亏损 red button** 和 **allocation ramp-up**。

所以这不是一篇“解释 BTC 带 alt”或“再来一个 cross-sectional reversal”材料，而是一条已经把 `entry / exit / sizing / risk / cost shell` 写得比较全的 **relative-value raw alpha**。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：不是 generic market beta，也不是“跌多了就抄底”，而是 **BTC 作为 leader 的相对强势延续 + 弱势 alt 继续跑输**。
- repo 的可贵之处，不是它宣称自己比赛名次高，而是它把 **完整策略骨架** 明确写出来了：
  - **entry**：过去 `24h` 为负收益的 alt 入候选池；
  - **selection**：只留负收益 alt；
  - **sizing**：按 `|24h return| / var(24h return)` 做权重，再过滤掉 `<10%` 的碎权重；
  - **rebalance**：按天重排，外加 BTC/alt ratio 漂移重平衡；
  - **risk**：`15%` 单仓亏损红按钮，仓位线性 ramp-up。
- 更关键的是：这条线 **不是只能照抄 repo 原版方向暴露**。对我们 desk，更值得测的是把它拆成：
  1. **raw alpha 本体**：BTC leader vs alt loser dispersion；
  2. **仓位治理层**：是否做 beta-neutral / gross-neutral / vol-neutral；
  3. **执行层**：`1h` 信号、`15m/5m` 执行。
- **一句话核心结论**：这份 repo 最值得偷的，不是它的 cointegration 外壳，而是这条很朴素但可直接落地的 **BTC-vs-weak-alt relative-value continuation**。
- **一句话证明方式**：我按 repo 公开规则做了 public-data proxy quick check 后发现，哪怕把原版强方向暴露削成更保守的 **beta-neutralized** 版本，边际也没有完全消失，说明它不只是蹭 market direction。

## 3. 为什么和当前项目有关
当前 `momentum` 已经积累了不少：funding / basis / cross-venue carry / pairs / cointegration / lead-lag / single-name MR。但还缺一类很实用的原料：

- **不靠复杂协整，不靠黑箱 ML**；
- 只用公开 OHLCV 就能先做；
- 可以自然映射到 `15m` 执行、`5m` 精细入场；
- 同时又不是纯单边趋势。

这条 BTC-vs-alt loser dispersion 正好卡在这个空档：
- 它是 **relative-value / cross-sectional raw alpha**；
- 信号很简单，公开数据就够；
- 能快速做 honesty check：一看是不是纯 beta，二看成本后是否还活，三看 active-day 占比是否太低。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / cross-sectional dispersion / leader-vs-loser continuation
- 基础 alpha：**BTC 相对强势延续 + 弱势 alt basket 继续跑输**
- regime：更适合 market dispersion 较大的时段；可后续叠加 BTC trend / cross-sectional breadth / vol regime gate
- filter / veto：只留 `24h return < 0` 的 alt；过滤 `<10%` 碎权重；无合格 alt 时空仓
- risk / sizing / execution overlay：`|24h return| / variance` 权重、daily rebalance、ratio drift 重平衡、`15%` 单仓止损、allocation ramp-up、成本按换手收取

## 4. 我先做了什么最小快检
我没有直接信 repo 叙事，而是用 **Binance USDⓈ-M public `1h` / `15m` klines** 做了一个 faithful proxy：

- 样本：`2025-09-01 ~ 2026-03-31`
- 币池：`BTC, ETH, SOL, ADA, XRP, DOGE`
- 信号：`24h` log return
- 权重：`abs(24h return) / var(24h return over 5d)`
- 过滤：保留权重 `>10%`
- 成本：单边 `6 bps` taker-ish on turnover
- 再平衡：按日

### 4.1 repo-like 版本（原版方向暴露）
- 持仓：`+10% BTC`，`-90% alt loser basket`
- `1h` quick check：
  - **总收益约 `+110.1%`**
  - **Sharpe 约 `2.55`**
  - **最大回撤约 `-17.6%`**
  - active days：`150 / 212`
  - 平均每天入选 alt 数：`3.47`
- `15m` transfer check（同逻辑、15m 执行）：
  - **总收益约 `+109.4%`**
  - **Sharpe 约 `2.21`**
  - **最大回撤约 `-22.5%`**

### 4.2 beta-neutralized 版本（更像 desk 可用形态）
我又把它压成更保守的 **gross-neutral-ish** 版本：
- 持仓：`+50% BTC`，`-50% alt loser basket`

结果：
- `1h` quick check：
  - **总收益约 `+19.7%`**
  - **Sharpe 约 `1.93`**
  - **最大回撤约 `-5.5%`**
- `15m` transfer check：
  - **总收益约 `+17.6%`**
  - **Sharpe 约 `1.39`**
  - **最大回撤约 `-9.7%`**

### 4.3 这组快检说明了什么
- 原版 repo-like 结果确实更猛，但它也明显带了 **净空 alt / 净空 beta** 的方向暴露；
- 更重要的是：**把方向性砍掉一大截以后，这条线没有直接死掉**；
- 这说明 raw alpha 不只是“熊市里做空小币”；它至少有一部分，确实来自 **leader-vs-loser 的相对强弱延续**。

## 5. 可复刻的最小实验
如果下一步要把它正式收进研究池，我建议按这个顺序测：

1. **faithful baseline**
   - 完整复刻 repo 版：`1h` 信号、daily rebalance、`BTC+loser basket`、`6/10/15 bps` 三档成本；
   - 先确认仓位/换手/活跃天数是不是诚实。

2. **neutralization layer**
   - 在同一 alpha 上，比较：
     - repo-like `10/90`
     - `50/50 gross-neutral`
     - `beta-matched BTC hedge`
     - `vol-targeted basket hedge`
   - 这一步是为了区分：到底赚的是 **relative-value alpha**，还是纯 market short。

3. **execution transfer 到 `15m/5m`**
   - 信号仍用 `24h` 窗口，但执行时钟改成 `15m`；
   - `5m` 只用于更细入场：例如把 daily rebalance 拆成 `00:00~01:00 UTC` VWAP/TWAP 执行带；
   - 记录执行后 drift 和成交成本，而不是只看 bar-close PnL。

4. **universe 扩张**
   - 从 `BTC/ETH/SOL/ADA/XRP/DOGE` 扩到前 `15~30` 个 perp majors；
   - 但必须保留 **最小流动性门槛**，别让 microcaps 假装 Sharpe。

5. **regime 分层**
   - 按 BTC trend、cross-sectional breadth、realized vol、funding crowding 分 bucket；
   - 看这条线是更像 **risk-off dispersion alpha**，还是普通日常 alpha。

## 6. 下一步怎么测（直接给实验单）
### 实验 A：这条线是不是主要靠熊市 beta
- 指标：对 BTC 小时收益回归后的残差 alpha、down-beta、net exposure
- 判据：如果 neutralized 版本 residual Sharpe 还在 `>1`，就继续；如果掉到接近 0，说明原版主要靠方向

### 实验 B：`15m` 是否比 `1h` 更适合执行
- 做法：信号保持 `24h`，分别用 `1h close`、`15m TWAP window`、`5m TWAP window` 执行
- 判据：比较 post-cost Sharpe、max DD、turnover 和 slippage proxy

### 实验 C：弱势 alt 的定义是否要分叉
- 对比：
  - 只看 `24h return < 0`
  - `24h return` bottom quartile
  - `24h residual return`（先对 BTC beta 残差化）
  - `24h return < 0` 且 funding/oi 不拥挤
- 判据：如果 residual loser 比原始 loser 更稳，就说明真正 alpha 更接近 **idiosyncratic underperformance continuation**

## 7. 风险与保留意见
- 这仍然是 **repo-based competition code**，不是正式论文；比赛名次能说明作者做过实盘迭代，但不等于可直接继承绩效。
- repo 原版的 `+10% BTC / -90% alt basket` 暴露明显偏空，不是标准 market-neutral；如果不做 neutralization，很容易把 beta 当 alpha。
- 我做的 public-data quick check 是 **faithful proxy**，不是原 repo OMS 的逐笔复刻；不能把数值当最终结论，只能当 first verdict。
- 当前样本明显带有阶段性 market regime，active days 只有 `150/212`，说明这条线不是 always-on，空仓占比不低。

## 8. 来源
1. **Lev Rozhkov et al. (2026). _hku-avenir-2nd-round_. GitHub repository.**
   - Venue: GitHub
   - Readable URL: `https://github.com/LevRoz630/hku-avenir-2nd-round`
   - Repo URL: `https://github.com/LevRoz630/hku-avenir-2nd-round.git`

2. **README.md**（比赛背景、top 11 / 1171、策略列表、15m backtester 框架）
   - Readable URL: `https://github.com/LevRoz630/hku-avenir-2nd-round/blob/main/README.md`

3. **`backtester/backtest/strategies/v1_ls.py`**（BTC long / negative-24h alt short 主策略）
   - Readable URL: `https://github.com/LevRoz630/hku-avenir-2nd-round/blob/main/backtester/backtest/strategies/v1_ls.py`

4. **`backtester/backtest/position_managers/v1_ls_pm.py`**（15% red button、allocation ramp-up）
   - Readable URL: `https://github.com/LevRoz630/hku-avenir-2nd-round/blob/main/backtester/backtest/position_managers/v1_ls_pm.py`

5. **`backtester/backtest/v1_ls_bt.py`**（默认 `lookback_days=5`、100 天样本、50 次 permutation test 外壳）
   - Readable URL: `https://github.com/LevRoz630/hku-avenir-2nd-round/blob/main/backtester/backtest/v1_ls_bt.py`

6. **`backtester/src/backtester.py`**（回测与 permutation test 引擎）
   - Readable URL: `https://github.com/LevRoz630/hku-avenir-2nd-round/blob/main/backtester/src/backtester.py`
