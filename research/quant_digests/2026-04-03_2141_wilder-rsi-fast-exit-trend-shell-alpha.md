# 别把这份 RSI momentum repo 只读成 4h walk-forward 报告：对 crypto short-cycle desk，更该先测的是「Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit」这条完整 raw alpha
- 时间：2026-04-03 21:41 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `Cypto_Trading_Wilder's SmoothingRSI/rsi_momentum_backtest_v5.py` + `PRODUCTION_REPORT_V5.md` + `OPTIMIZATION_RESULTS.md` + `monte_carlo_bootstrap_v6.py`）+ Binance Futures 公共 `5m/15m/3m` 最小便携性快检
- 主题类型：raw alpha
- 基础 alpha：**趋势已成立时，短周期 RSI 向上突破不是“过热就该反手”，而更像一段可继续跟随的 momentum continuation；真正关键不只是 entry，而是用 EMA200 / ADX / volume 做准入，再用 ATR trail + 更快的 RSI 回落阈值把利润收回来。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / trend / momentum / single-asset / wilder-rsi / breakout / ema200 / adx / volume-confirm / atr-trailing-stop / fast-exit / 5m / 15m / 3m / binance-perp / repo / public-data / cost / risk
- 证据类型：完整开源 repo + 明确参数与回测逻辑 + 本地公共数据快检；但 repo 很新、stars 很少，**更适合当可复现候选与策略母板，不该直接当 production 证据**

**先回答 base alpha：这篇东西的 base alpha 是清楚的——不是“walk-forward / bootstrap 工具链”，也不是“统计验证报告”本身，而是一个完整的 trend-momentum raw alpha：`RSI 向上突破 × 上方长均线 × ADX 趋势成立 × 成交量确认`，赌的是顺趋势方向的延续，不是回调均值回复。**

## 1）为什么这条线现在值得 intake
结合当前 `MAINLINE1_STRATEGY_FACTOR_MAP` / `FACTOR_BACKLOG` / `RESEARCH_AUTOMATION_BRIEF` 的优先级，我更在意的是：
- 先补 **raw alpha**，不要继续围着旧 baseline gate 微调；
- 如果是 trend / momentum 线，就要给出**完整壳**，而不是只给一个过滤器；
- 要能快速映射到 `5m / 15m` 做 first verdict。

这份 repo 值得写，不是因为它的 bootstrap 图好看，而是因为它刚好提供了一条**完整 trend raw alpha 母板**：
- entry：`RSI breakout`
- allow：`EMA200 + ADX + volume`
- exit：`ATR trailing stop + RSI exit`
- sizing：`risk-based position sizing`
- cost：`fee + slippage + funding`

翻成人话：

> 这不是“RSI 大于 70 追多”那么粗糙，而是把顺势延续写成了一条完整、可回测、可下放到短周期的交易壳。

更重要的是，它能补我们最近更偏 mean reversion / pairs / maker / carry intake 之外的另一条主线：

> **一个足够简洁、能快速复制到 crypto short-cycle 的单资产趋势延续壳。**

## 2）这次看了什么
### 2.1 主来源
1. **FarisZnf (2026), _Production-Grade RSI Momentum Crypto Trading Strategy with Advanced Statistical Validation_**  
   - Venue：GitHub repository  
   - DOI：N/A  
   - Readable URL：<https://github.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation>  
   - Repo URL：<https://github.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation>

2. 重点核对文件：
   - `README.md`
   - `Cypto_Trading_Wilder's SmoothingRSI/rsi_momentum_backtest_v5.py`
   - `Cypto_Trading_Wilder's SmoothingRSI/PRODUCTION_REPORT_V5.md`
   - `Cypto_Trading_Wilder's SmoothingRSI/OPTIMIZATION_RESULTS.md`
   - `Cypto_Trading_Wilder's SmoothingRSI/monte_carlo_bootstrap_v6.py`

### 2.2 repo 的客观信号
GitHub metadata：
- created：`2026-03-30`
- pushed：`2026-03-30`
- stars：`1`
- forks：`0`

所以要先说实话：

> 这不是一个“社区已经验证过很多轮”的成熟策略库，而是一个**新、轻、可读性强**的研究型 repo。它的价值在于源码透明、策略骨架完整，适合作为 intake 素材，而不是拿 repo headline 回报直接背书 production。

## 3）repo 真正有价值的不是验证框架，而是这条完整趋势壳
### 3.1 原版 entry：Wilder RSI breakout，不做逆势抄底
`rsi_momentum_backtest_v5.py` 里，核心 entry 条件很明确：
- `RSI_PERIOD = 14`
- `RSI_LONG_ENTRY = 65`
- `TREND_EMA_PERIOD = 200`
- `ADX_PERIOD = 14`
- `ADX_THRESHOLD = 20`
- `VOLUME_SMA_PERIOD = 20`

实际信号是：
- `rsi > entry_threshold`
- `rsi_prev <= entry_threshold`
- `close > ema_200`
- `adx > 20`
- `volume > volume_sma`

这条线的核心思想其实很对 short-cycle desk 胃口：

> **只有趋势、方向性和成交量都站在你这边时，才把 RSI 上破当 continuation，而不是把它当 overbought 反转。**

### 3.2 bull filter：repo 最值得 desk 单独拆出来的旁支
repo 里还有一个很值得 intake 的小设计：
- 当 `close > ema_200` 且 `adx > 25` 时，视为 `bull_regime`
- 这时把 entry threshold 从 `65` 下调到 `60`

翻成人话：

> 当市场已经明确进入强趋势时，不必死等更极端的 RSI；可以更早参与 continuation。

这个想法很适合 crypto 短周期，因为很多真正好做的顺势腿，往往不会等 RSI 飙到特别夸张才给第二次上车点。

### 3.3 exit：repo headline 里最容易被忽略，但对短周期最关键
repo 原版出场：
- `ATR_STOP_MULTIPLE = 4.0`
- `ATR_TARGET_MULTIPLE = 10.0`
- `RSI_LONG_EXIT = 30`

这在 `4h` 上是“让赢家多跑一会儿”的典型 trend-following 写法；但搬到 `5m / 15m` 时，**它反而变成最值得先动手改的地方**。

原因很简单：
- `RSI exit = 30` 对短周期来说太慢；
- continuation 腿经常先给你一段利润，再回落到中性；
- 如果等到 RSI 真掉回 `30` 才走，很多 `5m / 15m` 利润已经 round-trip 掉了。

所以这次真正值得 desk intake 的旁支，不是“原封不动抄 repo 参数”，而是：

> **保留它的 trend entry 壳，但把短周期的收割逻辑改成更快的 `RSI-45 exit`。**

### 3.4 sizing / risk / cost：它确实是一条完整策略，不只是信号
repo 里这部分也写得比较全：
- `RISK_PER_TRADE`
- `MAX_POSITION_PCT`
- `TRADING_FEE = 0.001`
- `SLIPPAGE = 0.0005`
- `FUNDING_RATE = 0.0001`

要特别提醒一个源码层面的细节：
- `README` 说的是 **2% risk per trade**；
- `v5` 代码里默认 `RISK_PER_TRADE = 0.06`，并把 `MAX_POSITION_PCT = 3.00`，解释为模拟 `3x leverage`。

这说明：

> repo 的“表现数字”里带有一定风格化的资金使用假设；但这不影响我们 intake 它的**信号壳与结构逻辑**。真正要落地时，先用更保守的仓位上限测 admission，才是对的。

## 4）Binance 公共数据最小便携性快检：真正值得 desk 抄的是 faster-exit 版本
为了避免只转述 README，我用 Binance USDⓈ-M Futures 公共 klines 做了一个最小快检。

### 4.1 快检口径
- 数据源：Binance USDⓈ-M Futures 公共 `klines`
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 区间：`2026-01-01` ~ `2026-04-03`
- 时间框架：`5m / 15m`，外加 `ETH 3m` sidecar
- proxy 逻辑：
  - 保留 repo 的 `RSI breakout + EMA200 + ADX + volume` entry
  - 保留 `bull regime` 下调 entry threshold 的想法
  - 成本沿 repo：`10bps fee + 5bps slippage`；funding 按 bar 长度缩放
  - sizing 采用**更保守**的 `2% risk / trade + 1.5x notional cap`
- artifact：
  - `reports/artifacts/quant_digests/2026-04-03_rsi_momentum_shortcycle_portability_probe.csv`
  - `reports/artifacts/quant_digests/2026-04-03_rsi_momentum_15m_threshold_sweep.csv`
  - `reports/artifacts/quant_digests/2026-04-03_rsi_momentum_5m_faster_exit_probe.csv`

### 4.2 先说坏消息：原版 `RSI exit = 30` 直接搬到短周期，表现很差
按 repo 原版更接近的 exit 逻辑做 quick proxy，结果是：
- `5m`：三币都明显为负，`BTC -48.0% / ETH -41.9% / SOL -43.1%`
- `15m`：虽然没 `5m` 那么差，但仍偏弱，`BTC -12.4% / ETH -12.7% / SOL -4.7%`
- `ETH 3m` sidecar：约 `-63.4%`

这说明一个很关键的事实：

> **repo 的 raw alpha 不是坏在 entry，而是坏在把更高时间框架的“慢退出”硬搬到 short-cycle。**

### 4.3 真正值得 desk intake 的旁支：把 exit 提快到 `RSI-45`
我随后只在 `15m` 上做了一个很小的阈值 sweep，核心发现很明确：
- **`BTC 15m`：entry `55` / exit `45`，proxy 总收益约 `+27.2%`，max DD 约 `-3.65%`，PF `5.97`**
- **`ETH 15m`：entry `60` / exit `45`，proxy 总收益约 `+48.2%`，max DD 约 `-3.94%`，PF `6.55`**
- **`SOL 15m`：entry `65` / exit `45`，proxy 总收益约 `+45.8%`，max DD 约 `-4.65%`，PF `3.59`**

最重要的不是数值本身，而是这个结构结论：

> **对 short-cycle 来说，这条策略的关键不是“把 RSI 做得更激进”，而是“让盈利单更早落袋”。**

### 4.4 `5m` 反而更像这条旁支该去的主战场
在 `5m` 上只保留 `exit = 45`，结果比原版好得非常明显：
- **`ETH 5m`：entry `58` / exit `45`，proxy 总收益约 `+90.8%`，max DD 约 `-4.40%`，PF `3.21`**
- **`SOL 5m`：entry `58` / exit `45`，proxy 总收益约 `+61.2%`，max DD 约 `-8.15%`，PF `2.57`**
- **`BTC 5m`：entry `62` / exit `45`，proxy 总收益约 `+35.1%`，max DD 约 `-7.61%`，PF `1.76`**

所以我对这份 repo 的 desk 版翻译是：

> 它不该被理解成“4h 验证框架”；真正适合当前 desk 的，是把它拆成一条 **`5m/15m fast-exit trend continuation shell`**。

## 5）它和当前 short-cycle desk 的关系该怎么摆
### 5.1 它服务的是哪类 raw alpha
很明确，它属于：
- **single-asset trend / momentum raw alpha**
- 更具体地说，是 **breakout-continuation**，不是 breakout-failure、也不是 mean reversion

### 5.2 它为什么比继续补一个 filter 更值得
因为这次不是在研究“哪个 gate 可能有帮助”，而是在 intake 一条**可独立存在的完整 raw alpha**：
- base alpha 说得清；
- entry/exit/sizing/risk/cost 齐；
- 今天就能在公共数据上做最小实验；
- 还能和现有 `multi_tf_momentum` baseline 做直接 A/B，而不是又加一层模糊 gate。

### 5.3 `1m / 3m / 5m / 15m` 上怎么分工
我会这样排序：
- **`5m`：第一优先主实验层** —— 这次 proxy 看起来最像可继续深挖的主战场
- **`15m`：稳健对照层** —— 更适合看参数是否平滑、是不是只靠高 turnover 撑出来
- **`3m`：暂时只做 sidecar** —— 原版慢退出在 `3m` 上明显太噪，必须先把 exit / cost / execution 处理好
- **`1m`：先不作为第一轮 admission 层** —— 除非同时加入更细的执行模型或 maker/taker 分层

## 6）我对这条线的判断
### 值得保留的核心资产
1. **Wilder RSI breakout 本体**：不是反转，是 continuation
2. **EMA200 / ADX / volume 三重 allow**：让它不至于沦为裸追涨
3. **bull regime entry lowering**：强趋势里更早参与，很适合 crypto
4. **risk-based sizing + ATR trail**：它确实是完整壳，不是只有信号

### 不建议原样照搬的部分
1. **`4h` 原版 exit 口径**：搬到 short-cycle 太慢
2. **README headline performance**：受资金假设影响，不应直接外推
3. **long-only 结构**：对 perp desk 来说，后续最好补 mirror short sleeve

### 当前 verdict
我的判断很直接：

> **值得进入 raw alpha 素材池，而且优先级不低；但值得 intake 的不是 repo headline 里的“4h validated RSI momentum”，而是它被 short-cycle 重写后的旁支：`Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`。**

## 7）下一步怎么测（最重要）
### A. 先做 exact-ish short-cycle replication
在 `momentum` 里先落一个最小原型：
- 标的：`BTC / ETH / SOL`
- 主频段：`5m`
- 对照频段：`15m`
- 信号：
  - `RSI(14)` 向上突破 `58~62`
  - `close > EMA200`
  - `ADX > 20`
  - `volume > SMA20`
  - bull regime 下 entry 再放宽 `5` 点
- 出场：
  - `ATR trail 4x`
  - `RSI fast exit 45`
  - EOD / time-stop 作为附加对照

### B. 明确做三组 A/B
1. **Original repo-ish**：`entry 65/60, exit 30`
2. **Fast-exit branch**：`entry 58~62, exit 45`
3. **Fast-exit + mirrored short sleeve**：
   - long：`RSI 上破 + above EMA200 + ADX + volume`
   - short：`RSI 下破 + below EMA200 + ADX + volume`

要回答的问题是：
- 真正有效的是 continuation 本体，还是 long-only 偏置？
- `5m` 优势是否仍能穿过更真实的成本模型？
- `exit=45` 是只是 sample lucky，还是跨币稳定？

### C. friction ladder 一开始就要加
至少加三档：
- maker-friendly
- mixed
- taker-worst-case

因为这条线 turnover 不低；如果只在理想 friction 下赚钱，production 价值会明显下降。

### D. 再决定它的最终归宿
根据 A/B 结果，分三种：
- **能活**：独立单资产 trend sleeve
- **原始 alpha 一般，但 allow 结构很强**：抽出 `EMA200+ADX+volume+bull-regime` 做共享趋势 admission 层
- **成本后不活**：只保留 `fast exit + trailing stop` 逻辑，给其他 trend 壳复用

## 8）Sources
1. **FarisZnf (2026), _Production-Grade RSI Momentum Crypto Trading Strategy with Advanced Statistical Validation_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation>  
   - Repo URL: <https://github.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation>

2. **Repository README / strategy summary**  
   - Source URL: <https://raw.githubusercontent.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation/main/README.md>

3. **Core strategy implementation (`rsi_momentum_backtest_v5.py`)**  
   - Source URL: <https://raw.githubusercontent.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation/main/Cypto_Trading_Wilder%27s%20SmoothingRSI/rsi_momentum_backtest_v5.py>

4. **Production report / risk-sizing notes (`PRODUCTION_REPORT_V5.md`)**  
   - Source URL: <https://raw.githubusercontent.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation/main/Cypto_Trading_Wilder%27s%20SmoothingRSI/PRODUCTION_REPORT_V5.md>

5. **Optimization and validation notes**  
   - Optimization URL: <https://raw.githubusercontent.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation/main/Cypto_Trading_Wilder%27s%20SmoothingRSI/OPTIMIZATION_RESULTS.md>  
   - Monte Carlo URL: <https://raw.githubusercontent.com/FarisZnf/Production-Grade-RSI-Momentum-Crypto-Trading-Strategy-with-Advanced-Statistical-Validation/main/Cypto_Trading_Wilder%27s%20SmoothingRSI/monte_carlo_bootstrap_v6.py>

6. **This run’s local artifacts**  
   - `reports/artifacts/quant_digests/2026-04-03_rsi_momentum_shortcycle_portability_probe.csv`  
   - `reports/artifacts/quant_digests/2026-04-03_rsi_momentum_15m_threshold_sweep.csv`  
   - `reports/artifacts/quant_digests/2026-04-03_rsi_momentum_5m_faster_exit_probe.csv`
