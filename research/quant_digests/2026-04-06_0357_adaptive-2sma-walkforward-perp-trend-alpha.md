# 别把 2025 自适应双均线论文只读成老派 MA crossover：对 short-cycle desk，更该先测的是「walk-forward 2-SMA perp trend × slow-window bias」完整 raw alpha
- 时间：2026-04-06 03:57 UTC
- 类型：2025 *Mathematics* 论文摘要/元数据（Crossref + OpenAlex）+ Hyperliquid public `5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：单资产趋势延续；用快慢均线相对位置定义方向，用 walk-forward 参数更新控制趋势信号失效
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/single-asset/dual-moving-average/2sma/walk-forward/adaptive-optimization/slow-window-bias/perpetual/btcusdt/hyperliquid/5m/15m/paper/public-data/cost/risk
- 证据类型：论文证据（摘要/元数据）+ 公开行情快检（自建 toy backtest）

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = `trend / momentum continuation`。**
> 不是 filter，不是 overlay；它本体就是一条可以独立跑起来的单资产 perp 趋势策略：**快均线上穿慢均线就顺势持仓，反向穿越就翻向/离场，再用 walk-forward 重选参数。**

## 1. 这次看了什么
这轮主看：

1. **Romo, A., Soto, R., Vega, E., Crawford, B., Salinas, A., & Becerra-Rozas, M. (2025). _Adaptive Optimization of a Dual Moving Average Strategy for Automated Cryptocurrency Trading_. Mathematics, 13(16), 2629.**
   - DOI：`10.3390/math13162629`
   - DOI URL：`https://doi.org/10.3390/math13162629`
   - Readable URL：`https://www.mdpi.com/2227-7390/13/16/2629`
   - PDF URL：`https://www.mdpi.com/2227-7390/13/16/2629/pdf`
   - Venue：*Mathematics*
   - Repo URL：**未见公开仓库**
2. **本轮 desk 化 portability probe（公开数据）**
   - 数据源：Hyperliquid public API `candleSnapshot`
   - 数据公开性：公开可得、无需 key
   - 更新频率：分钟级 / 可取 `5m` bar
   - 本地实验产物：
     - `reports/artifacts/quant_digests/adaptive_2sma_20260406/hl_btc_5m_last90d.csv`
     - `reports/artifacts/quant_digests/adaptive_2sma_20260406/grid_results_5m.csv`
     - `reports/artifacts/quant_digests/adaptive_2sma_20260406/grid_results_5m_split6d.csv`

这轮值得写它，不是因为“均线金叉死叉很新”，而是因为它刚好补当前素材池里一个很实用但不该缺位的东西：
- 最近几篇 intake 偏 **pairs / microstructure / shared gate**；
- 这篇则是**单资产、低依赖、完整可落地**的 perp raw alpha；
- 而且 paper 直接把 **交易成本 + walk-forward 训练/测试切分 + benchmark 对照** 都写进去了，很适合当 desk 的基础控制组。

## 2. 一句话核心结论 + 它是怎么证明的
### 一句话核心结论
**别把这篇 paper 只读成“把老双均线调了调参”；它真正适合 short-cycle desk 的点，是把 `2-SMA 趋势方向` 包装成一条能直接做最小实验的完整策略，并且明确告诉你：参数必须 walk-forward，窗口别太快。**

### 一句话它怎么证明
按论文摘要可得，作者：
- 用 **Binance 平台的 `BTCUSDT` futures 历史数据**；
- 做了 **34 个 overlapping 60-day train/test splits**；
- 在**计入真实交易费用**的条件下，LB2 自适应优化后的 `2-SMA` 策略在 unseen test 上达到：
  - **平均 ROI `7.9%`**
  - **最佳 ROI `17.2%`**
- 并且用 **Wilcoxon Signed-Rank Test** 证明其显著优于：
  - Buy & Hold
  - Random Walk
  - 非优化版 `2-SMA`

翻成人话：
> 这篇 paper 想说的不是“均线还能用”这种废话，而是 **crypto perp 上确实可以把简单趋势骨架做成可复现策略，但前提是别把窗口固定死、也别假装参数永远稳定。**

## 3. 这篇东西最值钱的，不是均线本身，而是它给了 desk 一条便宜、清晰、能快速否证的完整策略壳
### 3.1 它是完整 raw alpha，不是解释型材料
这条线很完整：
1. **entry / flip**：快均线 vs 慢均线；
2. **direction**：`fast > slow` 持多，`fast < slow` 持空；
3. **retraining**：滚动训练窗里更新参数；
4. **cost-aware evaluation**：交易费直接进净收益；
5. **benchmarking**：和最朴素的持有/随机/固定参数版直接比。

对 desk 来说，这种材料的价值很高，因为它不是“一个想法”，而是一条**可以当天就写成回测脚本**的策略骨架。

### 3.2 真正该借的，是 walk-forward，不是神化某组 window
paper 里真正值钱的结论不是“短均线用几根、长均线用几根”，而是：
- 参数会漂移；
- crypto perp 的最优窗口不是静态的；
- 如果你用一次性全样本调参，很容易把噪声错当 alpha。

这对 `1m/3m/5m/15m` desk 特别关键，因为：
- 越短周期，**换手越高、参数越不稳**；
- 越容易出现“训练期漂亮、上线就死”的问题；
- 所以这篇 paper 更像在提醒我们：**先搭一条能频繁重估、并且把 costs 放进去的 trend baseline。**

### 3.3 它很适合做“主信号控制组”
当前研究池里，复杂结构已经不少：
- spread MR
- pairs / relative value
- order-book imbalance
- event impulse
- regime / overlay

但越是这样，越需要一条非常朴素、可解释、能快速复刻的**单资产趋势控制组**。`2-SMA` 的意义恰好在这里：
- 如果连这种最基础的趋势壳在某个市场/频段都活不下来，复杂策略的上线预期也该降温；
- 如果它能活，复杂 alpha 至少有一个可以对照的 baseline，而不是每次都在黑箱里互相比烂。

## 4. desk 化拆解：直接翻成 entry / exit / sizing / risk / cost
## 4.1 策略骨架（最小版）
- **Universe**：先单资产 `BTC` perpetual；第二步再扩到 `ETH` 与高流动大币
- **频率**：优先 `15m` 主实验，`5m` 做压力测试；若做更快，只建议当 stress bucket
- **Signal**：`fast_ma(close) - slow_ma(close)`
- **Entry / Flip**：
  - `fast > slow` → long
  - `fast < slow` → short
- **Exit**：基础版直接反向翻仓；加强版可加 ATR stop 或 time stop
- **Sizing**：先固定名义敞口 / vol target 二选一；第一轮别上复杂 sizing
- **Risk**：限制单日最大翻仓次数，避免 chop 环境过度来回打脸
- **Cost**：至少显式跑 `maker/taker` 两档，第一轮可先按 taker-only 压力测试

## 4.2 这条线最适合 desk 的哪种角色
它更像：
- **完整 raw alpha 候选**；
- 也是后续更复杂趋势框架的**base layer**；
- 还能给现有 breakout / fresh-high / trend basket 系列提供一个**更便宜、更简单的对照组**。

换句话说，它不是最终答案，但非常适合做“**别让复杂研究没有朴素 baseline**”的那条底线策略。

## 5. 本轮公开数据快检：Hyperliquid `BTC` `5m` toy probe 给出的 desk 结论
> 说明：论文主数据是 Binance `BTCUSDT` futures；当前主机直接打 Binance futures REST 受限，所以 portability probe 用 **Hyperliquid 公开 `5m` candles** 做 proxy 检查。目的不是 faithful replication，而是回答：**这条 raw alpha 现在还能不能先做最小实验？**

### 5.1 数据口径
- 数据源：Hyperliquid public API `candleSnapshot`
- 标的：`BTC`
- 频率：`5m`
- 样本：`2026-03-19 19:00 UTC` ~ `2026-04-06 03:55 UTC`
- bar 数：`5004`
- 成本假设：**每次仓位变化按 `1.5 bps` / side 扣费**（toy 压力口径）
- 参数网格：
  - `fast ∈ {4,8,12,16,24,32,48}`
  - `slow ∈ {48,72,96,144,192,288,384}`
  - 且 `fast < slow`

### 5.2 快检结果里最值钱的 3 个观察
#### 观察 1：最亮眼的 in-sample 快窗口，OOS 很容易坏掉
按 `train = 前 12 天 / test = 后 6 天` 的 toy split：
- `12/96` 在训练窗里：
  - **train cumret `+8.24%`**
  - **train Sharpe `5.41`**
- 但到测试窗：
  - **test cumret `-3.04%`**
  - **test Sharpe `-4.74`**

这和 paper 强调 walk-forward 的方向是一致的：
> **短窗口、快翻仓，在短样本里很容易看起来会赚钱；但一上 OOS 就容易被 chop 和成本打回原形。**

#### 观察 2：更慢的窗口组合，反而更像 short-cycle desk 可迁移的版本
同一 toy probe 里，OOS 更稳的反而是偏慢组合：
- `48/192`：
  - **test cumret `+2.52%`**
  - **test Sharpe `4.74`**
  - **test trades `11`**
- `32/192`：
  - **test cumret `+0.82%`**
  - **test Sharpe `1.66`**
  - **test trades `15`**

这意味着 desk 版第一轮没必要从超快均线开搞，反而更该优先：
- 用**更慢的 slow leg** 控制翻仓；
- 让 `5m` 只是承载更平滑的趋势状态，而不是追求每小时多次切换方向。

#### 观察 3：这条 alpha 可以先做，但必须把“慢窗口偏置”写进实验设计
如果只看这轮快检，最合理的实验假设不是“均线越快越灵”，而是：
- `5m` 上也许能做趋势；
- 但真正活下来的，更可能是 **`slow >= 144` bar` 的低换手版本**；
- 快窗口应该被当成**stress / falsification bucket**，不是默认主配方。

## 6. 为什么这篇东西和当前 desk 直接相关
它直接补了 3 个当前很需要的东西：

1. **单资产 perp 趋势 baseline**
   - 不依赖配对、不依赖横截面、不依赖外部事件；
   - 当天就能复刻。
2. **walk-forward 训练框架**
   - 可以直接复用到其他趋势、breakout、fresh-high 题材上；
   - 不只服务于 `2-SMA` 本身。
3. **成本先验**
   - 这条线天然提醒你：参数越快、翻仓越勤，越容易被 cost 吃掉；
   - 很适合拿来当 `1m/3m/5m` 研发时的反过拟合教材。

## 7. 下一步怎么测（这轮最重要）
### 7.1 先做哪 3 个版本
直接跑三层递进：
1. **A = 固定参数 2-SMA**
   - `15m` 主频；`5m` 压力频
2. **B = walk-forward 2-SMA**
   - `train 30d / test 7d`
   - 训练窗按 net Sharpe 选参数
3. **C = B + simple veto**
   - 加一个很轻的 chop veto：例如 `ATR / price` 太低或过去 `N` 根交叉过密时不交易

### 7.2 最小可复现实验口径
- **数据**：Hyperliquid / Binance perpetual 公开 OHLCV
- **标的**：先 `BTC`，再扩 `ETH`
- **频率**：
  - 主实验：`15m`
  - 压力测试：`5m`
- **参数网格建议**：
  - `fast = 4, 8, 12, 16, 24, 32`
  - `slow = 48, 72, 96, 144, 192, 288`
- **成本**：至少 `1.5 / 3 / 6 bps` 每 side 三档
- **输出**：gross/net return、Sharpe、turnover、trades/day、持仓方向占比、最长连续亏损段

### 7.3 第一轮最该回答的 4 个问题
1. `15m` 上，walk-forward 是否稳定优于固定参数？
2. `5m` 上，`slow >= 144` 的慢窗口是否明显优于快窗口？
3. 成本从 `1.5bps -> 6bps` 时，哪类窗口最先失效？
4. 加一个很轻的 chop veto 后，收益下降还是 Sharpe / MDD 改善更明显？

## 8. 先别自嗨的风险
1. **这篇 intake 目前基于摘要/元数据，而非全文逐段审计。** 所以 paper 内部的精确超参数、交易规则细节，仍需二次核对。
2. **只有单资产 `BTCUSDT` 证据。** 先别把它自动推广成多资产 basket 结论。
3. **双均线是极易过拟合的家族。** 如果没有严格 walk-forward，几乎必然会挑到噪声参数。
4. **短周期下成本是第一风险，不是附注。** 越快的窗口越容易被交易费和 chop 同时击穿。

## 9. 这轮最值得记住的 desk 化结论
如果只记一句：

> **这篇 2025 论文真正适合 intake 的，不是“2-SMA 还能用”这句老话，而是把 `walk-forward parameter refresh` 正式拉进了单资产 perp 趋势策略的核心。**

再补一句更贴当前 desk：

> **第一轮别从超快均线开搞；先用 `15m` 和 `5m` 上的慢窗口版本做 baseline，再把快窗口当 falsification bucket。**

## 10. 来源
1. **Romo, A., Soto, R., Vega, E., Crawford, B., Salinas, A., & Becerra-Rozas, M. (2025). _Adaptive Optimization of a Dual Moving Average Strategy for Automated Cryptocurrency Trading_. Mathematics, 13(16), 2629.**
   - DOI：`10.3390/math13162629`
   - DOI URL：`https://doi.org/10.3390/math13162629`
   - Readable URL：`https://www.mdpi.com/2227-7390/13/16/2629`
   - PDF URL：`https://www.mdpi.com/2227-7390/13/16/2629/pdf`
2. **Crossref metadata for `10.3390/math13162629`**
   - URL：`https://api.crossref.org/works/10.3390/math13162629`
3. **OpenAlex metadata for `10.3390/math13162629`**
   - URL：`https://api.openalex.org/works/https://doi.org/10.3390/math13162629`
4. **Hyperliquid API docs / public market data**
   - API host：`https://api.hyperliquid.xyz/info`
   - Docs：`https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint`
   - 本轮实验产物：`reports/artifacts/quant_digests/adaptive_2sma_20260406/`
