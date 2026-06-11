# 别把这份 2026 新 stat-arb repo 只读成“pairs dashboard”：对 short-cycle desk，更该先抄的是「cointegrated spread raw alpha × half-life/Hurst admission × z-score/time-stop shell」
- 时间：2026-04-03 18:27 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `backend/api/services/backtest_engine.py` + `backend/api/services/cointegration_service.py` + `tests/test_backtest_engine_unit.py`）+ Binance Futures 公共 `15m/5m` 最小便携性快检
- 主题类型：raw alpha
- 基础 alpha：**配对后 spread 偏离均衡会向均值回归**；repo 里真正适合我们 desk 先拿来复现的，不只是 `z-score entry`，而是 `half-life/Hurst admission + time-stop` 这套“先筛会回来的 pair，再做 spread fade”的完整壳
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / cointegration / half-life / hurst / admission-layer / zscore / time-stop / binance-perp / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo（完整策略壳）+ 代码参数细读 + 本地 public-data proxy scan

**先回答 base alpha：这篇东西的 base alpha 很清楚，不是“多做几种统计检验就更科学”，而是 `spread mean reversion`。如果两条腿走散后不会回来，后面再漂亮的 score 都没用；如果会回来，真正决定 short-cycle 可交易性的就是：`回归速度够不够快`、`Hurst 是否真的偏均值回复`、以及 `time stop / cost` 会不会把纸上 alpha 吃掉。**

## 1) 这次看了什么
这轮主看的是一个很新的开源 repo：

1. **`ayush108108/hedgevision`（GitHub, 2026）**  
   - 标题：**HedgeVision — Open-source stat-arb engine**  
   - Venue：GitHub repository  
   - Authors：`ayush108108`（GitHub owner）  
   - Repo URL：<https://github.com/ayush108108/hedgevision>  
   - GitHub API metadata 显示：**创建于 `2026-03-31`，最新 push 在 `2026-04-03`**  
   - 这次重点看的文件：
     - `backend/api/services/backtest_engine.py`
     - `backend/api/services/cointegration_service.py`
     - `backend/api/services/backtest_service.py`
     - `tests/test_backtest_engine_unit.py`

2. **本地最小快检（不是复现 repo 收益，只是验证它对 crypto short-cycle 的可迁移性）**  
   - 数据：Binance USDⓈ-M Futures 公共 klines  
   - `15m` 扫描：`BTC/ETH/SOL/XRP/ADA/DOGE/LTC/BCH/LINK` 共 `9` 个主流 perp、`36` 个 pair、最近约 `31d`  
   - `5m` 聚焦：把 `15m` 扫描里最像“会回来的”3 组 pair 再拉到 `5m` 做短周期 proxy
   - 结果文件：
     - `reports/artifacts/quant_digests/2026-04-03_hedgevision_15m_pairs_proxy_scan.csv`
     - `reports/artifacts/quant_digests/2026-04-03_hedgevision_5m_focus_pairs_proxy_scan.csv`

为什么这条线现在值得写？因为我们最近 pairs 素材很多，但**大部分材料更偏“论文思路”或“复杂选对器”**；而这份 repo 的优势恰恰是：它把 **entry / exit / stop / cost / half-life / Hurst / candidate scoring** 都写成了能直接搬进 desk 的代码壳。

## 2) 这份 repo 真正值钱的，不是“pairs 又来了”，而是它把 raw alpha 和 admission layer 写在了一起
repo 的核心不是发明新 alpha，而是把一个**可立即移植的 pairs 母板**摆得很清楚：

- `alpha 本体`：cointegrated spread / residual spread **均值回复**
- `admission`：先看 correlation、EG/Johansen/ADF/PP/KPSS、OU half-life、Hurst
- `entry/exit`：再做 `|z|` 偏离入场、回归退出
- `risk`：加入 stop-loss、time stop、成本扣减

翻成人话：

> 这份 repo 最适合 desk 抄的，不是“再写一份 pairs backtester”，而是把研究顺序改成：**先筛“会回来而且回得够快”的 pair，再谈 z-score band。**

这很重要，因为我们最近已经反复看到：
- 高相关 ≠ 可交易 pair；
- 能协整 ≠ short-cycle 能活；
- `5m` 上看着很热闹的 pair，很多最后只是**拖到 time exit**。

所以这篇更值得当成一个 **raw alpha + admission layer** 素材卡，而不是又一篇泛泛的 pairs 摘要。

## 3) 代码里有哪些硬参数，可以直接拿走
### 3.1 `backtest_engine.py` 给出的 baseline 交易壳非常明确
`BacktestConfig` 里直接写了：

- `initial_capital = 10,000`
- `position_size = 1.0`
- `transaction_cost = 0.001`（约 `10bps`）
- `slippage = 0.0005`（约 `5bps`）
- `entry_threshold = 2.0`
- `exit_threshold = 0.5`
- `stop_loss_threshold = 3.0`
- `max_holding_period = None`（可配置）

`PairBacktester` 的交易逻辑也很朴素：
- `z >= +2`：做空 spread
- `z <= -2`：做多 spread
- `short spread` 在 `z <= +0.5` 止盈，在 `z >= +3` 止损
- `long spread` 在 `z >= -0.5` 止盈，在 `z <= -3` 止损
- 若设置了 `max_holding_period`，则触发 `time_exit`
- 每笔 round-trip 默认**先扣掉 `15bps` 成本 proxy**

这说明它不是“只有信号没有壳”的 repo，而是**完整到能直接迁移成 desk baseline**。

### 3.2 `cointegration_service.py` 里最有 desk 价值的，其实是 pair admission 而不是 entry band
这个文件做的事情非常全：

- 相关性：Pearson / Spearman / Kendall
- 协整：Engle-Granger + Johansen
- 残差平稳性：ADF / Phillips-Perron / KPSS
- 对冲比率：OLS beta / alpha
- 均值回复：OU half-life、mean-reversion speed、Hurst exponent
- spread / z-score 统计
- signal quality score / overall score / risk level

其中对 desk 最值钱的三件事是：

1. **half-life** 直接按 OU 过程估  
   `hl = ln(2) / lambda`；如果 `lambda <= 0`，直接视为“不均值回复”。

2. **Hurst exponent** 明确作为可交易性判断  
   文件里写得很直白：`H < 0.5` 更像 mean-reverting，`H > 0.5` 更像 trending。

3. **overall score** 不是只看 p-value**  
   它把 EG、Johansen、ADF、相关性、half-life/Hurst、signal quality 拼成一个总分；也就是说，repo 作者默认就不是“过个 cointegration test 就开做”，而是要先做候选排序。

这对我们 desk 的正确翻译是：

> **pairs 的 alpha 本体还是 spread fade，但真正决定 5m/15m 能不能做的，是 admission layer。**

## 4) Binance 公共 `15m/5m` 快检：repo 这套壳迁到 short-cycle 后，最大的现实问题不是 entry，而是“回归速度不够快”
先强调口径：下面只是 **public close proxy**，不是盘口级、不是可执行 mid/bid/ask，也没加 funding 和真实撮合逻辑，所以只能当**最小便携性快检**，不能当 production PnL。

### 4.1 `15m` 宇宙扫描：top pocket 还算像 raw alpha
我把 `9` 个主流 Binance perp 两两配对，按 repo 风格做了一个粗壳：
- rolling z-score 窗口：`288 bars`
- `entry = |z| >= 2`
- `exit = |z| <= 0.5`
- `stop = |z| >= 3.5`
- `time stop = 16 bars`（约 `4h`）

在这组很粗的 `15m` proxy 里，最像“能拿进下一轮正式实验”的 pocket 有三组：

1. **DOGEUSDT / LINKUSDT**
   - `corr = 0.921`
   - `half-life ≈ 59.3 bars ≈ 14.8h`
   - `Hurst ≈ 0.434`
   - 近 `31d` 触发 `41` 笔
   - `win rate ≈ 68.3%`
   - `avg pnl ≈ 38.3 bps proxy`
   - `median hold = 12 bars = 3h`

2. **SOLUSDT / ADAUSDT**
   - `corr = 0.923`
   - `half-life ≈ 96.0 bars ≈ 24.0h`
   - `Hurst ≈ 0.328`
   - `44` 笔
   - `win rate ≈ 65.9%`
   - `avg pnl ≈ 34.2 bps proxy`

3. **SOLUSDT / LTCUSDT**
   - `corr = 0.946`
   - `half-life ≈ 48.9 bars ≈ 12.2h`
   - `Hurst ≈ 0.341`
   - `37` 笔
   - `win rate ≈ 67.6%`
   - `avg pnl ≈ 33.0 bps proxy`

这组结果最值得记住的不是“哪组最好”，而是：

> **在 `15m` 上，repo 这套“先看回复性，再做 z-score fade”的逻辑，至少还像一条诚实的 raw alpha 候选。**

### 4.2 一压到 `5m`，问题立刻暴露：time exit 占比很高
我再把上面三组 pair 拉到 `5m`，用同一套思路做近 `13.8d` proxy：
- `entry = |z| >= 2`
- `exit = |z| <= 0.5`
- `stop = |z| >= 3.5`
- `time stop = 48 bars`（约 `4h`）

结果明显变“没那么顺”了：

1. **SOLUSDT / ADAUSDT**
   - `32` 笔
   - `win rate ≈ 56.3%`
   - `avg pnl ≈ 11.39 bps proxy`
   - `median hold = 240 min`
   - **`time exit share ≈ 59.4%`**

2. **DOGEUSDT / LINKUSDT**
   - `44` 笔
   - `win rate ≈ 52.3%`
   - `avg pnl ≈ 11.05 bps proxy`
   - `median hold = 125 min`
   - **`stop-loss share ≈ 40.9%`**

3. **SOLUSDT / LTCUSDT**
   - `46` 笔
   - `win rate ≈ 45.7%`
   - `avg pnl ≈ 10.26 bps proxy`
   - `median hold = 142.5 min`
   - **`stop-loss + time-exit` 占比过半**

这组数字说明了一个非常关键的 desk 结论：

> **pairs raw alpha 不是不能往 `5m` 压，但 repo 里的 baseline 不能无脑下采样。真正需要先调的，不是 entry band，而是 admission / half-life / time-stop。**

换句话说，repo 给我们的最大启发不是“2/0.5/3 这组阈值神奇有效”，而是：
- `15m` 先做 primary signal 更诚实；
- `5m` 更适合做 finer execution / early exit / stop 管理；
- 如果 pair 的 half-life 本来就偏长，硬塞进 `5m` 只会变成**拖时间的伪短周期 alpha**。

## 5) 这条线对当前 short-cycle desk 的正确翻译
### 5.1 策略拆解（必填）
- 方向属性：market-neutral / relative-value / pairs stat-arb
- 基础 alpha：**spread 偏离均衡后的均值回复**
- raw alpha 主体：`zscore(spread)` 极端偏离 → 回归均值
- regime：只在 `Hurst < 0.45~0.50`、`half-life` 有限且不太慢、rolling beta 稳定时启用
- filter / veto：
  - funding 单边过大时 veto
  - 重大事件币 / 上下架 / 解锁窗口 veto
  - pair 两腿相关性或 beta 急变 veto
- sizing / risk：
  - 等风险或 beta-neutral 配平
  - 按 residual vol / expected half-life 缩放仓位
  - 单 pair notional cap + 同叙事 pair 数量上限
- entry：`|z| >= 2.0` 先做 baseline
- exit：`|z| <= 0.5` 或 `z -> 0`
- stop：`|z| >= 3.0~3.5`
- time stop：`min(4h, 1.0~1.5 × expected half-life window)`
- cost：必须显式测 maker/taker、资金费、滑点、以及两腿同时成交失败风险

### 5.2 对 `5m / 15m` 的建议，不要平均用力
如果按这轮快检结果，我会这样落地：

- **`15m`**：优先做主信号层  
  因为 raw alpha 的回归速度和噪声比，在这个频段更像“能被解释”的均值回复。

- **`5m`**：优先做管理层  
  用来做：
  - finer execution
  - 提前减仓 / 分批止盈
  - 波动突然放大时提前 veto

- **不要把 `5m` 硬伪装成主 alpha 频段**  
  如果大部分 trade 最后都靠 `time_exit` 结束，那这不是高频 edge，只是“更频繁地观察一个本来更适合 15m/1h 管理的 pair”。

## 6) 为什么这篇现在比继续补一个 generic breakout 更值得
因为它补的是一张**可立即开工的 market-neutral 母板**：

1. **base alpha 清楚**：spread mean reversion，不是滤镜伪装成 alpha；
2. **代码够完整**：entry / exit / stop / time stop / cost 都有；
3. **研究顺序正确**：先 admission，再 z-score；
4. **对素材池有直接价值**：以后可以继续接上
   - same-underlier cross-venue pairs
   - funding / basis gate
   - sector-neutral cluster pairs
   - execution veto / maker-first routing

也就是说，这篇不只是“又多一张 pairs 卡”，而是给了我们一个**可以反复复用的 raw alpha 壳**。

## 7) 下一步怎么测（本篇最重要的部分）
### 实验 A：先做“规则版 HedgeVision admission layer”
**目的**：验证 `pair admission` 是否比“继续调 entry band”更重要。

- universe：Binance / Bybit / Hyperliquid 前 `20~40` 个高流动 perp
- 每日或每 `4h` 计算：
  - correlation
  - OU half-life
  - Hurst
  - zero-cross density
  - rolling beta stability
  - residual vol stability
- 对比两套组合：
  1. `Top corr pairs`
  2. `Top admission-score pairs`
- downstream execution 完全相同

**要看什么：**
- net pnl after cost
- pnl per turn
- median holding bars
- time-exit 占比

### 实验 B：把 `15m` 当主信号、`5m` 当管理层
**目的**：别把 raw alpha 本体和 execution 层混在一起。

- `15m`：产生 entry / exit / stop 主信号
- `5m`：做提前减仓、加严止损、短时冲击 veto
- 比较：
  - 纯 `15m` 管理
  - `15m signal + 5m management`

**关键判断：**
`5m` 是不是提升了 net edge，还是只提升了 turnover 和噪声。

### 实验 C：把 same-underlier / cross-venue 对照也接进来
**目的**：验证 repo 这套壳在 crypto 里到底更适合“跨资产 pair”，还是“同一资产跨 venue pair”。

- 组 1：alt/alt cross-asset pairs
- 组 2：same-underlier cross-venue pairs
- 同样用：
  - half-life/Hurst admission
  - z-score entry
  - time stop

**要看：**
哪类 pair 在 after-cost 口径下更诚实。

### 实验 D：成本压力测试必须单独做
**目的**：避免把 gross spread alpha 误判成 production alpha。

至少分四档：
- maker / maker
- maker / taker
- taker / maker
- taker / taker

并额外叠加：
- funding drag
- 双腿不同步成交
- 单腿滑点放大

如果某组 pair 的 `gross edge < 2x round-trip cost budget`，直接降级，不再当主交易候选。

## 8) 这篇的最终结论
这份 2026 新 repo 真正适合我们 desk 先搬的，不是“再写一个 stat-arb app”，而是下面这句话：

> **pairs 的 raw alpha 仍然是 spread mean reversion；但 short-cycle 能不能做，关键不在 z-score 本身，而在 `half-life/Hurst admission + time-stop discipline`。**

这轮 `15m/5m` public proxy 也给了一个很实用的现实判断：
- `15m` 上，这条线还像一条能认真继续测的 raw alpha；
- 一压到 `5m`，大量 trade 开始依赖 `time exit` 或被 stop 吃掉；
- 所以当前最值得进素材池的，不是“更激进的 band”，而是**更严格的 pair admission**。

## 9) 来源与落地文件
### 主来源（repo）
1. **`ayush108108` (2026), *hedgevision***  
   - Repo URL: <https://github.com/ayush108108/hedgevision>  
   - GitHub API metadata: <https://api.github.com/repos/ayush108108/hedgevision>
2. **Backtest engine**  
   - <https://raw.githubusercontent.com/ayush108108/hedgevision/main/backend/api/services/backtest_engine.py>
3. **Cointegration service**  
   - <https://raw.githubusercontent.com/ayush108108/hedgevision/main/backend/api/services/cointegration_service.py>
4. **Unit tests**  
   - <https://raw.githubusercontent.com/ayush108108/hedgevision/main/tests/test_backtest_engine_unit.py>

### 本地 artifacts
- `reports/artifacts/quant_digests/2026-04-03_hedgevision_15m_pairs_proxy_scan.csv`
- `reports/artifacts/quant_digests/2026-04-03_hedgevision_5m_focus_pairs_proxy_scan.csv`

### 本文路径
- `research/quant_digests/2026-04-03_1827_hedgevision-half-life-pairs-shell.md`
