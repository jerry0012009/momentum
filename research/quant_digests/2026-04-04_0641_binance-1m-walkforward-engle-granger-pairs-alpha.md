# 别把这份 2025/2026 Binance 1m Engle-Granger 仓库只当 pairs 作业：对 short-cycle desk，更该先测的是「15d/5d walk-forward pair admission × spread z-score mean reversion」完整 raw alpha

- 时间：2026-04-04 06:41 UTC
- 类型：2025/2026 GitHub repo source audit（GitHub API metadata + `README.md` + `pairs_finder01.py` + `backtesting_01.py` + `pairs_summary.csv` + `trading_bot01.py`）+ Binance USDⓈ-M 公共 `3m/5m/15m` 最小可移植性快检
- 主题类型：raw alpha
- 基础 alpha：**cointegrated pair 的 spread z-score 均值回归**，但更值钱的不是“单次 z-score 开平”，而是 **`15d train / 5d test` 的 walk-forward pair admission + threshold trading** 这条完整链路
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/engle-granger/walk-forward/pair-admission/zscore/binance-futures/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：仓库工程证据 + 公共数据快检

## 1. 这次看了什么
先回答这轮最关键的一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：是 pairs / stat-arb 的 spread 均值回归 raw alpha。**

但这份 repo 真正值得 intake 的，不只是“两个币价差偏离再回归”这句老话，而是它把 **选对、再训练、再下 z-score 单** 这三步串成了一条可复现的短周期骨架：

- `pairs_finder01.py`：在 90+ Binance Futures USDT 合约上做 rolling Engle-Granger 扫描；
- `backtesting_01.py`：用 `15d train + 5d test` 的 walk-forward 方式，生成 spread 与 z-score，并给出 `entry / exit / commission`；
- `trading_bot01.py`：把筛出来的 pair、`alpha/beta`、阈值、风险比例写进实时 bot 配置。

一句话结论：

> **这份仓库最值得 desk 先抄的，不是“又一个 pair z-score”，而是 `walk-forward pair admission → intraday spread trade` 这层完整 raw alpha 操作系统。**

## 2. 核心结论（给 desk 的可执行信息）
### 2.1 为什么它不是普通教学仓
仓库作者 **abbbbbv** 的 repo **`pairs_trading_cointegration-`**（创建于 `2025-11-15`，最近更新 `2026-01-21`）把 4 件平时经常被拆开的事放进一条链：

1. **pair admission**：不是先拍脑袋定 pair，而是 rolling Engle-Granger 扫描全池；
2. **walk-forward refit**：不是一组 `beta` 用到底，而是 `15 天训练 / 5 天测试` 滚动重估；
3. **signal trading**：`|z| > entry` 开仓，`|z| < exit` 平仓；
4. **live bridge**：把最新 `alpha / beta / threshold / risk_pct` 填进 bot。

这和单纯“静态 pair + 固定 z-score 回测”不一样：

> **alpha 本体不是单独某个 pair，而是“pair admission + spread MR execution”联立后的完整 raw alpha。**

### 2.2 仓库里真正有用的参数骨架
`backtesting_01.py` 里给出的核心壳子很清楚：

- 数据：Binance Futures `1m`
- 训练 / 测试：`15d / 5d`
- z-score 窗口：`96`
- 入场：`|z| > 2.0`
- 出场：`|z| < 0.5`
- 手续费：`0.0004`（约 `4 bps`）
- 单次风险：`risk_per_trade = 0.1`

而 `trading_bot01.py` 直接给了 live shortlist：

- `TRBUSDT-FILUSDT`：`alpha=2.4443`，`beta=1.2645`，`entry=2.5`，`exit=0.5`，`risk_pct=0.35`
- `IOTAUSDT-ONEUSDT`：`alpha=2.7384`，`beta=0.9660`，`entry=1.5`，`exit=0.5`，`risk_pct=0.35`

这说明作者自己也不是把所有 pair 用同一门槛硬跑，而是已经在做 **pair-specific thresholding**。

### 2.3 `pairs_summary.csv` 给出的 shortlist 线索
仓库自带的 `pairs_summary.csv` 虽然不是收益表，但它至少给了 **stability + signal density** 两类 admission 信息：

- `REEFUSDT-RVNUSDT`：平均 `p-value ≈ 0.0088`，`15/15` 个窗口 cointegrated，`z_crosses=11,416`
- `TRBUSDT-FILUSDT`：平均 `p-value ≈ 0.0421`，`10/15` 个窗口 cointegrated，`z_crosses=14,109`
- `IOTAUSDT-ONEUSDT`：平均 `p-value ≈ 0.0455`，`12/15` 个窗口 cointegrated，`z_crosses=13,064`

这里最重要的不是“哪一对第一名”，而是：

> **它把 pair ranking 的标准从“看上去像”变成了“训练窗稳定性 + 测试窗激活密度”。**

这正是我们 desk 当前更需要的 admission layer。

## 3. 为什么和当前项目直接相关
当前 bot7 的主目标不是围绕固定形态内循环，而是持续补充 **可独立复现、可直接落地、适合 `1m/3m/5m/15m` 的 raw alpha 素材池**。

这份 repo 值得选，不是因为它“新奇”，而是因为它刚好补了一个很实用的缺口：

- 最近 intake 已经有不少 **single-asset mean reversion / trend**；
- pairs 家族虽然也做过不少，但很多材料停在 **静态 pair / 单次回测 / 缺 live bridge**；
- 这份 repo 给的是 **Binance Futures 1m + walk-forward pair admission + bot bridge**，对 short-cycle desk 更像可以直接拆件复现的工程骨架。

如果要回答“它为什么比继续补一个泛化 filter 更值得”，答案很简单：

> **因为它本身就是 raw alpha，而且是完整策略链，不是二层修饰件。**

## 3.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative-value / mean reversion
- 基础 alpha：cointegrated spread 偏离后的均值回归
- regime：默认无单独宏观 regime；核心 regime 其实是 **pair stability / cointegration persistence**
- filter / veto：
  - rolling cointegration admission
  - pair-specific `entry / exit`
  - 后续可加 liquidity / fee / slippage veto
- risk / sizing / execution overlay：
  - 回测壳默认 `risk_per_trade = 10%`
  - live bot 配置提升到 `35%`，说明仓库作者默认做少对数、重仓化
  - 佣金约 `4 bps`
  - 交易对象是 Binance Futures，天然需要 maker/taker 与 funding 口径复核

## 4. 最小可复现实验（这轮已给到可跑口径）
### 4.1 本轮公共数据快检口径
我额外用 Binance USDⓈ-M 公共 kline，对 repo live bot 里两组 pair 做了一个 **不依赖私有环境** 的最小 portability probe：

- 数据源：Binance USDⓈ-M `fapi/v1/klines`
- pair：`TRBUSDT-FILUSDT`、`IOTAUSDT-ONEUSDT`
- 周期：`15m / 5m / 3m`
- 训练 / 测试：按 repo 口径取最近 `15d train + 5d test`
- 估计：train 段 OLS `alpha/beta`
- 信号：test 段对 spread 做 `rolling zscore(96)`，统计 `|z|` 过门槛频次与 `entry=2 / exit=0.5` 事件

### 4.2 本轮 4 个关键数据点
1. **TRB-FIL 在最近样本里仍是可激活 pair，不只是 repo 旧结果。**
   - `15m`：`beta ≈ 0.704`，spread AR(1) 半衰期约 **87.3 bars**，测试窗 `|z|>=2` 共有 **58** 次，形成 **6** 次入场、**5** 次出场，平均持有约 **31.5 bars**。
2. **IOTA-ONE 在最近样本里的回复更快。**
   - `15m`：`beta ≈ 0.881`，半衰期约 **13.4 bars**，测试窗 `|z|>=2` 共有 **84** 次，形成 **7** 次入场、**6** 次出场，平均持有约 **33.7 bars**。
3. **降到更快周期后，信号密度明显上升。**
   - `TRB-FIL`：`|z|>=2` 次数从 `15m: 58` → `5m: 173` → `3m: 298`
   - `IOTA-ONE`：`15m: 84` → `5m: 223` → `3m: 301`
4. **这不是“越快越好”，反而提示成本断崖。**
   - `3m/5m` 的 event density 很高，但若没有 maker 占比、挂单排队、最小 tick / 最小名义过滤，极可能只是把更多毛信号换成更多手续费。

### 4.3 这轮快检的 desk 解读
最保守的解读应该是：

- **`15m` 适合做 first-verdict 主线**：样本稳定、交易数没那么爆炸；
- **`5m` 适合做 selective extension**：只放最稳定 pair + 更高 entry percentile；
- **`3m` 默认不直接上 production alpha**：除非先证明 maker fill / slippage / cooldown 后仍有净边；
- **`1m` 可以保留为 live execution / monitoring resolution**，但不该先当 admission 主频。

## 5. 下一步怎么测（直接可执行）
1. **先重写成真正的两腿 PnL 回测，而不是 spread synthetic price。**
   - 用美元中性腿：`long y / short beta*x`；
   - 把手续费、funding、借贷/机会成本都放进真实现金流。
2. **把 pair admission 独立成一层。**
   - 不是“先挑两对再回测”，而是每 `5d` 重跑一次：
     - `cointegration persistence`
     - `half-life`
     - `signal density`
     - `top-of-book liquidity`
     - `estimated turnover cost`
3. **做 cost ladder。**
   - 至少跑 `2 / 4 / 8 / 12 bps` 四档；
   - 分开统计 `15m` 和 `5m` 的 break-even signal density。
4. **做 pair-specific threshold bucket。**
   - 不要全市场统一 `entry=2.0`；
   - 对快回复 pair 试 `1.5/0.5`，对慢回复 pair 试 `2.5/0.5`。
5. **加 portfolio shell，但不要急着上多对。**
   - 第一轮先做 `top 3 pairs`；
   - 再测试 pair 之间相关性、同步拥挤和 trade overlap。

## 6. 风险与保留意见
- 这份 repo **没有直接给出可信的 out-of-sample PnL 表**，`pairs_summary.csv` 更多是 admission ranking，不是收益证明。
- top-ranked pair 里有些币对（如 `REEF/RVN`）对今天 desk 未必够流动或够稳，**必须先做 tradability 清洗**。
- `trading_bot01.py` 里的 live 参数是手工 hard-code，若不定期重估 `alpha/beta`，很容易 stale。
- 回测用 `backtesting.py` 把 spread 变成合成价格，这对研究阶段够用，但离真实两腿 PnL 还有一层工程差距。
- live config 用到 `risk_pct=0.35`，对短周期 pairs 来说偏激进；这更像 demo 配置，不应直接照搬。

## 7. 来源
1. **abbbbbv (2025/2026). _pairs_trading_cointegration-_ (GitHub repository).**
   - Repo URL: `https://github.com/abbbbbv/pairs_trading_cointegration-`
   - Readable URL: `https://github.com/abbbbbv/pairs_trading_cointegration-`
   - Created: `2025-11-15`
   - Updated: `2026-01-21`
2. **Engle, Robert F., & Granger, Clive W. J. (1987). _Co-integration and Error Correction: Representation, Estimation, and Testing_. Econometrica.**
   - Venue: *Econometrica*
   - DOI: `10.2307/1913236`
   - Readable URL: `https://www.jstor.org/stable/1913236`
3. **Binance USDⓈ-M Futures API — Kline/Candlestick Data.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
   - Data publicness: 公开可得
   - Update frequency: 交易所实时更新，研究侧可按 `1m/3m/5m/15m` 抽样

## 8. 本地产物
- `reports/artifacts/quant_digests/engle_pairs_20260404_portability.csv`
- `research/quant_digests/2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`
