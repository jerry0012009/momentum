# 别把这份 2026 RSI repo 只读成“4h 追涨回测”：对 short-cycle desk，更该先测的是「Wilder-RSI breakout × ADX/EMA regime × ATR trail」这条完整 raw alpha 壳——但 15m 也只有低摩擦口袋才勉强能活

- 时间：2026-04-13 05:58 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `rsi_momentum_backtest_v5.py` + `PRODUCTION_REPORT_V5.md` + `OPTIMIZATION_REPORT_V4.md`）+ Binance USDⓈ-M `15m/5m` public-data portability probe
- 主题标签：raw-alpha/trend/momentum/rsi/wilder/adx/ema/atr/volume/trailing-stop/long-only/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：repo source audit + public-data portability probe

- 主题类型：raw alpha
- 基础 alpha：**当价格已经站在长均线之上、ADX 说明市场不是乱震、且 RSI 上穿高阈值并伴随放量时，后面往往还有一段可交易的趋势惯性；策略不是赌“RSI 超买反转”，而是赌“强势突破后还会继续走一段”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = 趋势延续。**
> 不是“RSI 高了就反转”，而是 **`RSI 上穿高阈值 × EMA200 上方 × ADX>20 × 成交量放大`** 共同出现时，价格继续沿原方向跑一段的概率更高；然后用 **宽 ATR 追踪止损 + 结构破坏退出** 去拿那一段惯性。

翻成人话：
- RSI 在这里不是抄底工具，而是“趋势已经启动”的加速器；
- ADX 和 EMA200 不是装饰，而是在帮你过滤掉最烦的横盘假突破；
- 真正决定能不能赚钱的，不是入场那一下有多花，而是 **能不能给趋势留空间，同时把 chop 成本压住**。

所以它不是 filter，也不是纯 overlay，确实是一条 **完整 trend / momentum raw alpha 壳**。

## 2. 这次看了什么

这轮看的是 GitHub 仓库：
- **Author / Owner：** `FarisZnf`
- **Year：** 2026
- **Title：** *Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation>
- **Repo URL：** <https://github.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation>

仓库主张的是一个 **4h、long-only、趋势跟随** 的完整外壳：
1. **入场**：Wilder RSI(14) 上穿 65；若处在更强 bull regime（`close > EMA200` 且 `ADX > 25`），阈值放宽到 60；
2. **过滤**：价格在 EMA200 上方，ADX>20，且 volume > 20-bar SMA；
3. **出场**：4x ATR trailing stop、`close < EMA20 * 0.995` 的 trend exhaustion、以及 `RSI < 30` emergency exit；
4. **风控 / sizing**：按 stop distance 做 risk-based sizing；
5. **成本**：显式写了 fee / slippage / funding；
6. **验证**：README 和报告里还塞了 walk-forward、stress test、bootstrap Monte Carlo 的叙事。

但源码细读后有两个很重要的“诚实注释”：
- **README 说“2% risk/trade”**，但 `rsi_momentum_backtest_v5.py` 实际默认是 **`RISK_PER_TRADE = 0.06`**、`MAX_POSITION_PCT = 3.00`，本质是拿 **3x leverage simulation** 放大了仓位；
- README / 报告里还在讲 **10x ATR take-profit**，但 v5 核心 loop 里 `tp_hit` 实际没有被触发逻辑更新，等于 **真实主出场还是 trailing stop / trend exhaustion / RSI emergency**。

也就是说：
> **这份 repo 可以当完整策略壳看，但复现时应该相信源码，不要无脑照 README 文案抄。**

## 3. 核心结论

- **一句话核心结论：** 这份 2026 新 repo 值得进池，因为它把一条很清楚的 **趋势 raw alpha** 写成了完整壳；但如果你把 4h 逻辑直接压到 `15m/5m`，edge 会迅速被成本和 whipsaw 吃掉。
- **一句话更具体地说：** 对 short-cycle desk，这条线最该先测的不是“RSI 参数再微调”，而是 **`低摩擦资产/时段选择 × maker-first 执行 × 更强 regime admission`** 能不能把 gross edge 留住。
- **一句话 first verdict：** 这条壳在 `15m` 的 **ETH pocket** 还有一点苗头，但若按 repo 里近似 taker-ish 的粗成本去扣，整体并不过线；`5m` 更明显像 whipsaw 机器。

## 4. 我做了一个更贴近 desk 的 `15m/5m` portability probe

### 4.1 数据源、公开性、更新频率、最小复现实验口径
- **数据源：** Binance USDⓈ-M public klines `fapi/v1/klines`
- **公开性：** 公开可得
- **更新频率：** 本轮使用 `15m` 与 `5m`
- **资产：** `BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT`
- **样本：**
  - `15m`：近 **120 天**（`2025-12-14 ~ 2026-04-13`）
  - `5m`：近 **45 天**（`2026-02-27 ~ 2026-04-13`）
- **实验口径：**
  1. 按 repo 逻辑重建 `Wilder RSI / ADX / EMA200 / volume SMA / ATR`；
  2. 仍然只做 **long-only continuation**；
  3. 信号全部 **shift 1 bar**，下一根 open 执行；
  4. 用 **4x ATR trailing stop + EMA20 结构破坏 + RSI<30** 退出；
  5. 为了先看信号壳本身，先用 **unit-notional trade return** 记 gross，再做成本敏感性；
  6. 成本扫了 `8 / 12 / 20 / 30 bps` round-trip，并粗加 repo 同口径 funding（`1 bp / 8h`）。

### 4.2 结果：`15m` 还能看到一点 gross edge，`5m` 基本不行

#### 聚合结果（四个币合并）
- **15m**：共 **248 笔**，平均 **gross 约 `+4.20 bps/trade`**，平均持有约 **`33.4` bar**，gross 胜率约 **`34.7%`**；
  - 若扣 **12 bps round-trip + funding**，平均变成 **`-8.84 bps/trade`**；
  - 若扣 **30 bps round-trip + funding**，平均变成 **`-26.84 bps/trade`**。
- **5m**：共 **257 笔**，平均 **gross 约 `-1.18 bps/trade`**，平均持有约 **`38.8` bar**；
  - 扣 **12 bps round-trip + funding** 后约 **`-13.59 bps/trade`**；
  - 说明 5m 直译版没有先天优势，成本前都没明显站稳。

#### 最好的局部口袋：ETH `15m`
- **ETHUSDT 15m gross 累计约 `+7.03%`**；
- 若只扣 **8 bps round-trip + funding**，还有约 **`+1.25%`**；
- 但扣到 **12 bps** 就掉到约 **`-1.23%`**。

这句最关键：
> **这条壳不是完全没东西，但更像“只在低摩擦 ETH 15m pocket 勉强存活”的候选，而不是可直接照抄到所有 majors 的 taker 策略。**

#### 为什么 5m 更差？
退出结构很说明问题：
- `15m` 上，BTC 的 exit 约 **75%** 来自 trailing stop；ETH 约 **54.8%** 来自 trend exhaustion；
- 但 `5m` 上，各币 **81%~97%** 的 exit 都落在 trailing stop，说明策略大部分时间是在更细粒度噪声里被反复扫掉。

翻成人话：
- 4h 那种“让趋势自己跑”的逻辑，压到 5m 后，很多时候还没跑成趋势，就先被局部回撤洗掉；
- 这会让 long-only continuation 变成“高换手、低胜率、成本前就不厚”的信号壳。

### 4.3 本轮 artifact
- `reports/artifacts/literature/rsi_momentum_repo_portability_2026-04-13/summary_by_symbol_interval.csv`
- `reports/artifacts/literature/rsi_momentum_repo_portability_2026-04-13/aggregate_cost_sensitivity.csv`
- `reports/artifacts/literature/rsi_momentum_repo_portability_2026-04-13/trade_log.csv`
- 同目录下还缓存了本轮使用的 Binance `5m/15m` K 线 CSV

## 5. 为什么和当前项目有关

最近研究池里 relative-value / pairs / carry 已经补得不少，这轮值得补一篇 **趋势 raw alpha 壳**，原因很直接：
- 它的 **base alpha 清楚**，不是拿 RSI 当神秘按钮；
- 它的 **entry / exit / sizing / cost** 是完整的，不是只给一个 feature；
- 它还能给 desk 一个很实用的提醒：
  > **很多“4h 看起来很干净”的趋势策略，压到 15m/5m 后，真正的瓶颈不是信号定义，而是成本和噪声。**

这对我们后续做 `1m/3m/5m/15m` 研发很有用，因为它可以直接衍生出三类后续实验：
1. **更强 admission**：不是所有 `RSI+ADX` 触发都做，只做最顺的那部分；
2. **更低摩擦执行**：maker-first / queue-aware，尽量别用粗 taker 假设；
3. **横截面路由**：把它从“单币 always-on”改成“只在最干净的 1~2 个币上开”。

## 5.5 策略拆解（必填）
- **方向属性：** single-asset / trend-following / momentum continuation
- **基础 alpha：** `RSI 上穿高阈值` 代表趋势加速，若同时处在 `EMA200 上方 + ADX>20 + 放量` 的状态，后续延续段有正期望
- **regime：** `close > EMA200`、`ADX > 20`，bull pocket 里阈值可从 65 放宽到 60
- **filter / veto：** volume 未放大不做、EMA200 下方不做、ADX 不够不做
- **risk / sizing / execution overlay：** 4x ATR trailing stop、EMA20 结构破坏退出、risk-based sizing、成本/滑点/funding 粗扣

## 6. 可复刻的最小实验 / 下一步怎么测

### 实验 A：先做真正有 desk 意义的低摩擦版 `15m`
**假设：** 这条壳不是没 edge，而是需要更低 all-in friction 才活得下来。

- 资产：先 `ETHUSDT / BTCUSDT`
- 周期：`15m`
- admission：保留当前 `EMA200 + ADX + volume`，再加一层 **只在 ADX 分位数较高时启用**
- 执行：maker-first，统计真实 queue 不成交率；同时做 `8 / 10 / 12 bps` 生存线
- 先看指标：`post-cost bps/trade`、`fill rate`、`trail stop 占比`

### 实验 B：把它从单币 always-on 改成横截面路由
**假设：** 真正该做的不是每个币都跑，而是每个时点只做 **trend-quality 最高** 的那一两个币。

- 资产：`BTC / ETH / BNB / SOL / XRP / DOGE`
- 排序键：`ADX`、近 `n` bar realized trend efficiency、成交额
- 交易：每根 bar 只允许 top-1 / top-2 资产开仓
- 先看指标：trade 数是否下降、gross / net 是否抬升

### 实验 C：别急着上 `5m`，先测更强 veto
**假设：** `5m` 失败主要因为 chop 太多，不是 alpha 完全不存在。

- 加的 veto：
  1. 只在 `15m` 同方向趋势状态下开 `5m` 单；
  2. 只做美股开盘后 / 欧盘活跃时段；
  3. `ATR / close` 太低或太高都不做（避开死水和过热）。
- 先看指标：`5m` 的 trailing-stop 比例能否从 `80%+` 压下来

## 7. 风险与保留意见

1. **repo 自述与源码不完全一致**：尤其是 risk-per-trade 和 take-profit 描述，复现必须以代码为准。
2. **本轮 probe 是 transfer check，不是原仓 4h 逐表复刻**：我测的是它在 short-cycle 上能不能搬运，不是帮 repo 验证原始大收益声明。
3. **当前只做了 long-only**：若要上 desk，还应评估是否需要对称 short 侧，或者只保留 long side。
4. **成本极敏感**：ETH 15m 在 `8 bps` 和 `12 bps` 之间就从微正变负，说明执行质量是生死线。
5. **`5m` 噪声太重**：若没有更强上级 regime / execution gate，直接压频大概率只是多交手续费。

## 8. 一句话结论

> **这份 2026 RSI repo 值得进池，因为它给的是一条“规则讲得清、壳也完整”的趋势 raw alpha；但对 short-cycle desk，第一落点不是照抄 4h 追涨，而是把它改造成“低摩擦 15m selective momentum shell”，否则 5m/15m 大概率先被 whipsaw 和成本吃掉。**

## 9. 来源

1. **FarisZnf (2026). _Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation_. GitHub repository.**
   - Readable URL / Repo URL: <https://github.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation>
   - README: <https://raw.githubusercontent.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation/main/README.md>
   - Core code: <https://raw.githubusercontent.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation/main/Cypto_Trading_Wilder%27s%20SmoothingRSI/rsi_momentum_backtest_v5.py>
   - Production report: <https://raw.githubusercontent.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation/main/Cypto_Trading_Wilder%27s%20SmoothingRSI/PRODUCTION_REPORT_V5.md>
   - Optimization report: <https://raw.githubusercontent.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation/main/Cypto_Trading_Wilder%27s%20SmoothingRSI/OPTIMIZATION_REPORT_V4.md>

2. **Wilder, J. W. Jr. (1978). _New Concepts in Technical Trading Systems_.**
   - Wilder RSI / ATR 的方法论地基

3. **Binance USDⓈ-M Public API**
   - Klines endpoint: <https://fapi.binance.com/fapi/v1/klines>
