# 别把这份 2025 Binance pairs repo 只读成 Telegram 提醒器：对 short-cycle desk，更该先测的是「全市场 pair admission × spread z-score fade」这条 raw alpha

- 时间：2026-04-13 08:06 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `main.py` + `cointegration.py` + `telegram_message.py` + `zscore_backtest.py` + `total_backtest.py` + `top5_tradingcoin.py` + `top5_cointegrated_pairs.csv`）+ Binance USDⓈ-M `15m/5m` public-data portability probe
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/all-market-pair-admission/cointegration/kalman/hedge-ratio/zscore/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：工程经验 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**先在全市场 liquid perp 里做 pair admission（相关性 / 协整 / 半衰期 / 零轴穿越），再对通过准入的价差做 `z-score` 反转；也就是“不是直接赌单币涨跌，而是赌两条强相关腿之间的价差会回归”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = cointegrated spread mean reversion（配对价差回归）。**

这份 repo 表面上像一个“每小时推送 top5 pair 信号”的 Telegram bot，但真正对我们 desk 有价值的，不是提醒器，而是它背后的 **raw alpha 壳**：

1. 先从 Binance USDT perp 全市场里筛可交易 pair；
2. 再估 hedge ratio，构造 spread；
3. 最后在 spread 偏离均值足够远时做 fade。

翻成人话：
- 不是看 `ADA` 或 `SOL` 单边要涨还是要跌；
- 而是看 **两条腿相对关系** 是否偏太远；
- 偏太远就做“贵的那条空、便宜的那条多”；
- 等价差收回去就平。

所以这不是 `filter / overlay`，它本体就是一条 **可独立交易的 relative-value raw alpha**。

## 2. 这次看了什么

### 主来源（repo）
- **作者：** Janghyuk Choi
- **年份：** 2025
- **项目：** *Binance Statistical Arbitrage Bot with Telegram Integration*
- **Repo URL：** <https://github.com/JanghyukChoi/binance-statistical-arbitrage-bot>
- **关键文件：**
  - README：<https://github.com/JanghyukChoi/binance-statistical-arbitrage-bot/blob/main/README.md>
  - 主扫描脚本：<https://github.com/JanghyukChoi/binance-statistical-arbitrage-bot/blob/main/main.py>
  - 协整 / Kalman 对冲比率：<https://github.com/JanghyukChoi/binance-statistical-arbitrage-bot/blob/main/cointegration.py>
  - 信号推送：<https://github.com/JanghyukChoi/binance-statistical-arbitrage-bot/blob/main/telegram_message.py>
  - pair 排名：<https://github.com/JanghyukChoi/binance-statistical-arbitrage-bot/blob/main/top5_tradingcoin.py>
  - 样例 pair：<https://github.com/JanghyukChoi/binance-statistical-arbitrage-bot/blob/main/top5_cointegrated_pairs.csv>

### 方法地基（paper）
- **Engle, Robert F., & Granger, Clive W. J. (1987).** *Co-integration and Error Correction: Representation, Estimation, and Testing.* *Econometrica*.
- **DOI：** <https://doi.org/10.2307/1913236>
- **Readable URL：** <https://www.jstor.org/stable/1913236>

### 本轮自建 probe
- 脚本：`reports/artifacts/quant_digests/2026-04-13_janghyuk_pairs_probe.py`
- 输出：`reports/artifacts/literature/janghyuk_pairs_portability_probe_2026-04-13.csv`

## 3. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这份 repo 最值得 desk 接的，不是它给出的某个固定 pair，而是“全市场 pair admission → spread z-score fade”这条可复现 raw alpha 流程；但 hedge-ratio / backtest 数学现在还不够干净，必须先重算。**

### 一句话证明方式
> **证明不是靠 README 口号，而是靠源码拆解 + Binance 公共 `15m/5m` 数据快检：我们能看见 admission、entry、exit 的规则骨架，也能看到当前 pair 的 spread 振荡密度足够做 first verdict，但现成导出的 hedge ratio 与当前样本 OLS 结果存在明显漂移。**

## 4. 为什么和当前项目有关

这轮值得写，不是因为“pairs 又来一篇”，而是因为它补的是当前素材池里很需要的一层：

1. **它是双腿 raw alpha，不是单币形态。**
   - 最近池子里已经有很多 single-name trend / reversal / event-driven；
   - 这份 repo 补的是 **relative-value / stat-arb** 这条主线。

2. **它把研究流程拆得很清楚。**
   - universe 先筛；
   - pair 再筛；
   - signal 最后做。
   这对 `momentum` 项目很重要，因为它把“alpha 本体”和“admission 层”分开了。

3. **它足够容易做最小实验。**
   - 公开 Binance K 线就能起步；
   - 先做 `15m / 5m` 的 spread shell，就能很快给出 `first verdict`；
   - 不需要先拿 order book、链上或付费数据。

## 5. 先看 repo 真正提供了什么

### 5.1 它的可复用部分
这份 repo 最值钱的，不是任何一个单独参数，而是这个 3 段式流程：

1. **全市场扫描**
   - `main.py` 取 Binance USDT perpetual universe；
   - 默认先扫前 50 个交易对；
   - `1h / 200 bars` 上做 cointegration check。

2. **pair admission**
   - `cointegration.py` 用 `coint()` 做协整检验；
   - 用 Kalman filter 给 time-varying hedge ratio；
   - 还记录 `zero_crossings` 与最新 z-score。

3. **交易壳**
   - `z > 2`：short 第一腿 / long 第二腿；
   - `z < -2`：long 第一腿 / short 第二腿；
   - `|z| < 0.5`：exit。

这就已经够构成一条 **最小可运行 pairs raw alpha shell**。

### 5.2 它的主要问题
但如果把它当“可直接上线策略”，现在还不行：

1. **backtest 数学不干净**
   - `zscore_backtest.py` 里引用了并不存在的 `calculate_spread`；
   - PnL 里的 hedge ratio 推法也不稳；
   - `total_backtest.py` 甚至是本地随机数 mock，不是严肃实盘前回测口径。

2. **sizing / cost / funding 仍缺失**
   - 没有正式的 beta-neutral notional sizing；
   - 没有双腿手续费 / 滑点 / funding 的统一成本口径；
   - 更没有 pair break / stop / time-stop 的组合层约束。

3. **pair 本身会漂**
   - repo 导出的 top5 pair 不是圣旨；
   - 即使同一对腿，在不同样本上 hedge ratio 也会明显变化。

所以对我们来说，正确读法不是“抄 top5 csv”，而是：

> **抄它的流程，不抄它的结果。**

## 6. public-data portability probe：这条壳能不能落到今天的 `15m/5m`？

我用 repo 给出的 3 个样例 pair（`ADA/SOL`、`DASH/AVAX`、`BAT/SUSHI`）在 Binance USDⓈ-M 上做了一个很轻的 `90d` probe，先不宣称收益，只检查：
- 配对腿有没有足够相关性；
- spread 是否有足够振荡；
- `|z| > 2` 这种触发在 `15m/5m` 上会不会稀到没法做。

### 6.1 结果里最值得记的 3 个数

#### `ADAUSDT / SOLUSDT`
- `15m` 相关性：**`0.9696`**
- `15m` `|z| > 2` 触发：**`242` 次 / 90d`**
- 半衰期（OLS spread 粗估）：**约 `101.4h`**

这说明：
- 振荡密度是够的；
- 但回归太慢，更像“慢 spread”而不是我们最想要的短回转 pocket。

#### `DASHUSDT / AVAXUSDT`
- `15m` 相关性：**`0.9307`**
- `15m` `|z| > 2` 触发：**`277` 次 / 90d`**
- 半衰期：**约 `32.4h`**

这是三组里更像 first test lane 的一组：
- 不算极快，但至少比 `ADA/SOL` 更接近可交易的短周期配对壳；
- 先拿它做 `15m` 执行层验证，比盲扫全市场更省时间。

#### `BATUSDT / SUSHIUSDT`
- `15m` 相关性：**`0.9519`**
- `15m` `|z| > 2` 触发：**`274` 次 / 90d`**
- 半衰期：**约 `110.7h`**

它的问题和 `ADA/SOL` 类似：
- 相关性没问题；
- 但回归速度偏慢，容易被双腿成本和 funding 吃掉。

### 6.2 当前最重要的保留意见
有个很关键的红旗：
- repo 样例里的 `repo_hedge_ratio`，和我们用当前 `90d` 公共数据重算的 `ols_hedge_ratio`，**有明显偏差**；
- 特别是 `DASH/AVAX`、`BAT/SUSHI` 这种差得很离谱。

这说明两件事：
1. **pair admission 必须滚动重估，不能迷信 repo 导出的静态 CSV；**
2. **spread 定义要先统一成同一口径（levels / log levels / rolling OLS / Kalman），否则后面的 z-score 和 sizing 都会漂。**

## 7. 策略拆解（必填）

- 方向属性：**relative value / pairs / market-neutral**
- 基础 alpha：**admitted pair 的 spread z-score fade**
- regime：**高流动性 USDT perpetual；pair 先过相关性 / 协整 / 半衰期 / 零轴穿越筛选**
- filter / veto：**rolling hedge-ratio stability、最小零轴穿越次数、双腿 funding / fee veto、pair break 检查**
- risk / sizing / execution overlay：**beta-neutral 或 inverse-vol sizing；`|z| > 4` stop；`2×half-life` time stop；双腿 round-trip 成本统一计入**

## 8. 下一步怎么测（必须项）

这里不要先做“大而全配对平台”，直接做一个最小但干净的实验：

### 8.1 最小实验
**研究假设**
- 在 Binance USDT-M top `30~50` liquid universe 中，若先在 `1h` 上做 pair admission，再在 `15m` 上执行 spread `z-score` fade，则一小部分 pair 能在双腿成本后保留正的 mean trade edge。

**可计算定义**
1. 每天或每 `4h` 重做一次 admission：
   - `corr > 0.85`
   - Engle-Granger `p < 0.05`
   - half-life `< 48h`
   - zero-crossings `>= N`
2. 对通过的 pair：
   - hedge ratio 用 rolling OLS 或 Kalman，先统一成 log-spread 口径
   - `15m`：`|z| > 2` entry，`|z| < 0.5` exit
   - `|z| > 4` stop
   - `time stop = 2 × half-life`
3. sizing：
   - 先做 beta-neutral equal-risk notional；
   - funding 和 fee 全都按双腿 round-trip 压进去。

**最小回测切口**
- 市场：Binance USDⓈ-M
- 周期：admission `1h`，execution `15m`，必要时用 `5m` 细化 exit
- 样本：最近 `180d`
- 种子 pair：先从 `DASH/AVAX` 开始，再扩到全市场 top `30~50`

**最该先看的 2 个指标**
1. **post-cost mean trade pnl**
2. **positive pair ratio / active-window ratio**

如果这两个先不过线，就别急着上复杂 ML 或动态 portfolio。

## 9. 我对这条线当前的判断

这条线值得进研究池，但优先级应放在：

- **高于** 纯解释型 regime / overlay；
- **低于** 那些已经把 sizing / risk / cost 都写清楚的完整 pairs shell；
- 当前最好把它归为：
  - **raw alpha 候选：是**
  - **可直接上 desk：还不是**

更具体地说：

> **可以抄它的“admission → spread → z-score”骨架，但不能抄它现成 CSV 和回测结论。**

## 10. 来源

### Repo
- **Janghyuk Choi. (2025).** *Binance Statistical Arbitrage Bot with Telegram Integration.* GitHub.  
  URL: <https://github.com/JanghyukChoi/binance-statistical-arbitrage-bot>

### Paper grounding
- **Engle, R. F., & Granger, C. W. J. (1987).** *Co-integration and Error Correction: Representation, Estimation, and Testing.* *Econometrica*.  
  DOI: <https://doi.org/10.2307/1913236>  
  Readable URL: <https://www.jstor.org/stable/1913236>

### Public data
- **Binance USDⓈ-M Futures API**  
  Klines endpoint: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
