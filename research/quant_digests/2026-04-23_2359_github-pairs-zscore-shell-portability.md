# 别把这个 GitHub pairs repo 只读成“又一篇配对教材”：对 short-cycle crypto desk，更值得先拆的是「Engle-Granger admission × spread z-score fade × 明确 entry/exit/risk/cost」这条完整 raw alpha 壳——但最近 Binance perp taker 口径下还没过线

- 时间：2026-04-23 23:59 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `backtester.py` + `cointegration_test.py` + `optimize_params.py`）+ Binance USDⓈ-M public-data portability probe（8 liquid majors，`15m/5m`）
- 主题类型：raw alpha
- 基础 alpha：**先筛出价格联动较稳定的一对币，用线性组合残差代表“相对偏离”；当这个 spread 偏离自己的滚动均值过远时，做均值回归：spread 太高就 short spread，太低就 long spread，等它回到中间平仓。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/cointegration/engle-granger/spread-zscore/mean-reversion/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：repo source + public API portability probe

## 1) 为什么这次还值得看一个 pairs repo
先把一句最重要的话说清楚：

> **这份材料真正有价值的，不只是“pairs 会回归”这句老话，而是它把一个可直接落地的完整策略壳写得比较完整：pair admission、spread 构造、entry/exit、止损、参数搜索、回测框架都给了。**

对我们现在的 desk，更重要的问题不是“pairs 这个概念新不新”，而是：
- 有没有一个**可直接复现**的策略壳；
- 能不能映射到 `15m/5m`；
- 在公开数据和现实成本下，到底还能不能活。

这份 repo 刚好适合做这件事。

## 2) 本轮看了什么
### 2.1 来源
- **Author / Owner：** `seans-alt`
- **Year：** 2026（repo 活跃更新到 2026-02）
- **Title：** *crypto-pairs-arbitrage*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/seans-alt/crypto-pairs-arbitrage>
- **Repo URL：** <https://github.com/seans-alt/crypto-pairs-arbitrage>
- **Raw README：** <https://raw.githubusercontent.com/seans-alt/crypto-pairs-arbitrage/main/README.md>
- **Raw source：**
  - <https://raw.githubusercontent.com/seans-alt/crypto-pairs-arbitrage/main/backtester.py>
  - <https://raw.githubusercontent.com/seans-alt/crypto-pairs-arbitrage/main/cointegration_test.py>
  - <https://raw.githubusercontent.com/seans-alt/crypto-pairs-arbitrage/main/optimize_params.py>

### 2.2 repo 的 base alpha 是什么
翻成人话，就是：

1. 先找两只经常一起动的币；
2. 用回归把它们压成一个相对价差 `spread = y - βx`；
3. 如果这个 spread 暂时被拉得很开，赌它会往中间收；
4. 不是赌单边涨跌，而是赌**相对价格关系回归**。

这就是标准的 `relative value / stat-arb / mean reversion` raw alpha。

## 3) repo 里真正该带走的策略骨架
### 3.1 Admission：先筛 pair，再交易
repo 不是见两条线像就直接做，而是先做 pair admission：
- `cointegration_test.py` 里有 `engle_granger_test`
- 用 ADF/cointegration 检验 pair 是否更像“可回归关系”，而不是两条随机线

这点对 desk 很重要，因为它把 pairs 从“图形上像”升级成“先过 admission”。

### 3.2 Signal：spread z-score
repo 的核心信号是：
- 先算 spread
- 再算 rolling mean / rolling std
- 得到 `z-score`

直觉上很简单：
- `z` 很高：spread 太宽，做空 spread
- `z` 很低：spread 太窄，做多 spread
- `z` 回到中间：平仓

这比很多“神秘 ML 配对”更适合快速复现，因为信号本体非常清楚。

### 3.3 Exit / Risk：不是只有入场，没有出场
repo 提供了比“只会发 entry 信号”的材料更完整的壳：
- `z_entry`
- `z_exit`
- `z_stop`
- 基本交易成本参数
- 参数搜索脚本 `optimize_params.py`

也就是说，这不是“alpha 方向有了，剩下你自己补”；
而是已经给出了一个**完整策略最小闭环**：
`admission -> spread construction -> entry -> exit -> stop -> cost -> param scan`。

## 4) 为什么这条线仍然适合 short-cycle desk
虽然 pairs/stat-arb 听起来偏中频，但这份 repo 对短周期 desk 仍然有价值，原因是：

1. **它天然是 market-neutral / relative-value 壳**
   - 可直接补 raw alpha 素材池，不依赖单腿方向；
2. **它能直接映射到 `15m/5m`**
   - pair admission 可以更慢；
   - 真正开平仓与风险控制可以放到更快 bar；
3. **它的失败也很有价值**
   - 如果最近 taker 成本下活不下来，我们就知道该往 maker-first、更严 admission、或更低换手方向改，而不是继续拍脑袋。

## 5) 本轮最小 public-data portability probe
### 5.1 数据与口径
为了做一个最小、能快速复现的 desk probe，我用了：
- 数据源：Binance USDⓈ-M public klines `https://fapi.binance.com/fapi/v1/klines`
- universe：
  - `BTCUSDT`
  - `ETHUSDT`
  - `BNBUSDT`
  - `SOLUSDT`
  - `XRPUSDT`
  - `ADAUSDT`
  - `DOGEUSDT`
  - `LINKUSDT`
- 周期：
  - `15m`：约 `4000` bars
  - `5m`：约 `3000` bars
- 基本回测参数：
  - `window=24`（15m） / `72`（5m）
  - `z_entry=2.0`
  - `z_exit=0.5`
  - `z_stop=3.0`
  - `tc=6 bps` per turn proxy

说明：
- 本地环境缺 `statsmodels`，所以这轮 portability probe 没把 ADF/Engle-Granger 完整复刻到本地 backtest 流里；
- 但 repo 的 pair-admission 思路仍然保留，probe 阶段先用**回归残差 + half-life + z-score 回测**做最小 sanity check。

### 5.2 产物文件
本轮产物落在：
- `reports/artifacts/quant_digests/2026-04-23_pairs_zscore_probe/`

关键文件：
- `pair_scan_summary.csv`
- `pair_scan_15m.csv`
- `pair_scan_5m.csv`
- `focused_param_scan.csv`
- `summary.json`

## 6) probe 里最值得记住的结果
### 6.1 先看“有没有看起来像 pair 的东西”
在这组 liquid majors 里，几组 pair 的同步性还算像样：
- `ADAUSDT-DOGEUSDT`：
  - `15m return corr ≈ 0.84`
  - `5m return corr ≈ 0.82`
- `XRPUSDT-LINKUSDT`：
  - `15m return corr ≈ 0.83`
  - `5m return corr ≈ 0.79`
- `ETHUSDT-SOLUSDT`：
  - `15m return corr ≈ 0.88`
  - `5m return corr ≈ 0.83`

也就是说，pair 候选不是没有。

### 6.2 但最关键的坏消息：最近 taker 成本下，净值没过线
用 repo 风格的 z-score fade 壳，在这轮 `6 bps` 成本 proxy 下，主要 pair 的结果都偏弱，甚至明显负：

- `ADA-DOGE` `15m`，较保守 `z_entry=2.5 / z_exit=0.5`
  - `total return ≈ -5.0%`
  - `Sharpe ≈ -5.74`
  - `maxDD ≈ -6.5%`
- `XRP-LINK` `5m`，`z_entry=2.5 / z_exit=0.5`
  - `total return ≈ -0.7%`
  - `Sharpe ≈ -3.22`
- `ETH-SOL` `15m`，`z_entry=2.5 / z_exit=0.5`
  - `total return ≈ -9.6%`
  - `Sharpe ≈ -7.69`

翻成人话：

> **repo 这条 raw alpha 壳是清楚的，但“直接照搬成最近 Binance perp taker 策略”这件事，目前证据并不支持。**

### 6.3 这不代表它没价值，代表它更像“完整策略骨架 + 成本生存待修”
这份材料最有价值的地方变成：
- 策略结构是完整的；
- raw alpha 本体是清楚的；
- 但最近样本告诉我们：
  - 纯 bar-close taker 化执行很可能把 edge 吃掉；
  - 不更严格做 admission / half-life / 成本建模，就容易死在换手里。

## 7) 对 desk 来说，这篇该怎么定位
### 结论一句话
> **它是合格的 raw alpha 候选，也是合格的完整策略壳；但当前更像“pairs shell for further refinement”，而不是已经能直接上线的现成答案。**

### 为什么还值得收进池子
因为它给的是一条可以继续迭代的明确主线：
- 不需要先发明 alpha 定义；
- 不需要先补 entry/exit/risk；
- 直接从 `admission -> spread -> zscore -> stop -> cost` 这条链开始优化。

这比“只会说 pair 可能均值回归”的材料有价值得多。

## 8) 和 `1m / 3m / 5m / 15m` 的关系
这条线最合理的 desk 用法不是“把 pair admission 也做成每分钟重跑”，而是：

- **较慢层（30m / 1h / 4h）**：
  - 更新 pair admission
  - 更新 hedge ratio
  - 更新 half-life / spread stability
- **执行层（15m / 5m，必要时 1m / 3m）**：
  - 用更快 bar 执行 z-score entry
  - 用更快 bar 做 stop / take-profit / early exit
  - 观察 microstructure 是否适合 maker-first

也就是：
> **alpha 本体是 pair spread reversion，但真正能不能活，取决于更快执行层能否把成本压下来。**

## 9) 这条线当前最该补什么，不该补什么
### 先补的
1. **更严格 admission**
   - 不只看相关性；
   - 真做 walk-forward Engle-Granger / ADF / half-life 筛选；
2. **更现实的 cost ladder**
   - `2 / 4 / 6 / 8 bps` 分层；
3. **maker-first / partial rebalance**
   - 不要默认双腿都 bar close taker；
4. **更少、更稳的 pair 池**
   - 不追求 pair 多，而是追求 spread 更稳定。

### 暂时别急着补的
- 先别上复杂 ML；
- 先别把它包装成“全市场通用 stat-arb 引擎”；
- 先把最朴素的 pairs shell 在现实 friction 下能不能过线搞清楚。

## 10) 下一步怎么测
按优先级建议这样排：

### A. 先做真正的 walk-forward pair admission
- 频率：每周 / 每 3 天重选 pair
- 条件：
  - Engle-Granger p-value 过滤
  - half-life 过滤
  - spread volatility / stability 过滤
- 输出：只保留少数高质量 pair

### B. 再做 15m / 5m 双层执行
- `15m`：主 signal
- `5m`：child execution / early exit
- 核心问题：
  - `5m` 是否能降低回撤与成本；
  - 还是只是加快噪声、增加 turnover。

### C. 最后才加 microstructure veto
如果前两步还有正毛边，再接：
- quote imbalance veto
- spread widening veto
- low-liquidity veto

否则就没必要把一个本体没过线的东西继续堆复杂度。

## 11) 最终判断
如果只保留一句结论：

> **`seans-alt/crypto-pairs-arbitrage` 值得收进素材池，不是因为“pairs 这个题材新”，而是因为它把 stat-arb raw alpha 的完整闭环写得够清楚；但最近 Binance perp 的 `15m/5m` taker 口径 probe 显示，这个壳目前更像待优化骨架，而不是直接可上线的现成 edge。**
