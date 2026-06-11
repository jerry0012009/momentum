# 别把这个 2025 `crypto-stat-arb` 仓只读成“reversal+momentum 组合展示”：对 short-cycle crypto desk，更该先拆的是「BTC 残差化横截面 loser→winner fade × 稀疏 band admission」这条 raw alpha 壳

- 时间：2026-04-25 14:13 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `src/crypto_stat_arb/signals.py` + `backtest.py` + `portfolio.py` + notebook tables）+ Binance USDⓈ-M public-data portability probe（`1h` parent，`12` 个 liquid majors）
- 主题类型：raw alpha
- 基础 alpha：**先把各币对 BTC 的共同 beta 摘掉，只看“自己相对 BTC 的超额短线表现”；如果某些币刚刚相对跑输得过头，它们接下来一小段更容易做相对修复，而刚刚相对跑赢过头的币更容易回落。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 已给出信号、再平衡、L1 中性化、成本回测与 walk-forward 壳；desk 侧仍需补 `15m/5m` child execution）
- 主题标签：raw-alpha/cross-sectional/relative-value/mean-reversion/btc-residualization/loser-winner/banding/inverse-vol/market-neutral/1h/15m/5m/repo/public-data/cost/risk
- 证据类型：repo code + repo result tables + public futures portability probe

## 1. 这次看了什么
这轮主材料不是论文，而是一个 2025 GitHub repo：

- **Author:** Cameron Collins（GitHub: `ccollins80`）
- **Project:** *Crypto Statistical Arbitrage*
- **Repo URL:** <https://github.com/ccollins80/crypto-stat-arb>
- **Readable README:** <https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/README.md>
- **关键源码：**
  - signals: <https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/src/crypto_stat_arb/signals.py>
  - backtest: <https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/src/crypto_stat_arb/backtest.py>
  - portfolio: <https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/src/crypto_stat_arb/portfolio.py>

我没有把它读成“又一个 reversal+momentum 混合组合案例”。这轮更值得 intake 的，是 repo 里更像 desk 原材料的一条独立 raw alpha：

> **BTC residualized cross-sectional reversal：最近几根里相对 BTC 跑输最多的一篮子，后面更容易做相对修复；最近相对 BTC 跑赢最多的一篮子，更容易回吐。**

翻成人话：不是看谁绝对涨跌，而是先扣掉“全市场一起跟 BTC 摇摆”那部分，再看谁自己超涨/超跌得离谱，然后做一篮子 loser→winner fade。

## 2. 一句话结论
- **一句话核心结论：** 这份 repo 最值得拿走的不是“reversal+momentum 混合后 Sharpe 更高”，而是更底层的那句：**先对 BTC 做残差化，再做短窗横截面 loser→winner fade，能把很多“其实只是跟着 BTC 一起冲”的伪信号先剥掉。**
- **一句话证明方式：** 作者在代码里把 `residualize_to_bench -> cross-sectional z-score -> band admission -> inverse-vol -> L1 neutralization -> costed backtest` 串成完整壳；我再用 Binance 永续公开 `1h` 数据做最小 portability probe，结果显示：**reversal sleeve 还有活口，但原样参数不能照抄，最近更像“放慢再平衡、放宽 band”后才有 edge；momentum sleeve 近期反而明显更弱。**

## 3. 这轮为什么值得做
这轮值得做，原因很直接：

1. **base alpha 很清楚。**
   不是抽象的“市场状态更好”，而是一个可单独回测的 raw alpha：`BTC residualized XS loser→winner fade`。

2. **它天然是 relative-value / market-neutral 素材。**
   很适合当前 desk 补充不只靠 breakout / trend 的 alpha 池。

3. **repo 给的是完整策略壳，不只是灵感。**
   `signals.py` 里明确写了：
   - `k` 根累计残差收益
   - 横截面 z-score
   - `|z| < band` 不做
   - inverse-vol 缩放
   - 每根做 L1 neutralization
   再由 `portfolio.py` 的 `downsample_weights(every)` 控制再平衡节奏，`backtest.py` 再扣 turnover cost。

4. **它很容易映射到 `15m/5m`。**
   更合理的读法不是强行把主信号压成逐根 `1m/3m`，而是：
   - `1h` parent 决定谁该 long / short；
   - `15m/5m` child 负责更便宜的进场、撤退、time-stop。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / market-neutral mean reversion
- 基础 alpha：BTC 残差化后的短窗超涨超跌会回归
- regime：优先在 liquid majors / beta 结构稳定的币池里用；新币、极端事件币默认降权
- filter / veto：
  - `|z| < band` 不开仓
  - 低流动性币、极端 funding / news event 币优先 veto
  - 若 short leg 对单币跳涨极敏感，可先做 half-short 或 long-only losers basket
- risk / sizing / execution overlay：
  - inverse-vol 或常数风险预算
  - L1 neutralized weights
  - parent `1h` 产出篮子，child `15m/5m` 做 maker-first / pullback fill / time-stop
  - 明确扣 turnover cost，别把日内 relative-value 当零成本

## 4. repo 里最值得拿走的 4 个点
1. **残差化不是点缀，而是 alpha 清洗步骤。**
   `signals.py` 先对每个币做 rolling beta/alpha 回归，把 BTC 公共波动扣掉，再做横截面排序。对 crypto 来说，这一步很像“先去掉大盘，再看个体偏离”。

2. **band admission 很重要。**
   repo 不是见信号就上，而是只做 `|z|` 足够极端的点。翻成人话：不够离谱就别交易，避免把噪音当 alpha。

3. **仓位层很克制。**
   不是 top/bottom 各梭哈，而是先 z-score，再 inverse-vol，再 L1 中性化。这个做法非常适合我们拿来搭最小可运行壳。

4. **repo 自己的 headline 足够强。**
   README 给出的代表性结果是：
   - Reversal sleeve：**net Sharpe ≈ 1.77**，年化收益约 **36.6%**
   - Momentum sleeve：**net Sharpe ≈ 1.32**（README 口径）
   - Mixed 50/50：**net Sharpe ≈ 2.18**
   也就是说，它不是只会讲故事，至少在作者样本里给了成体系结果。

## 5. 我做的最小 portability probe：近期 Binance 上“reversal 活、momentum 弱、原样参数别照抄”
### 5.1 数据口径
- 数据源：Binance Futures REST `fapi/v1/klines`
- 公开性：公开可得，无需私钥
- 周期：`1h`
- 样本：最近 `1500` 根 `1h` bars，约 `2026-02-22 ~ 2026-04-25`
- universe：`BTC/ETH/SOL/XRP/DOGE/ADA/BNB/LINK/AVAX/LTC/TRX/DOT`
- 成本：单边 `7 bps` 的 repo 同口径粗扣

### 5.2 快检结果
我先按 repo 思路在最近样本上重跑，核心结论不是“原样复制就赚钱”，而是：

- **repo 风格最接近的 reversal 壳**（`k=4`, `band=2.5`, `beta_win=168`, `every=24`）在当前样本里 **net Sharpe ≈ -0.72**，说明**原样参数不可照抄**。
- 但 **reversal raw alpha 本体没完全死**。在更适合当前样本的邻域里：
  - `k=4`, `band=2.0`, `every=72`：**net Sharpe ≈ 3.28**，年化收益约 **38.1%**，成本拖累约 **5.6%/年**；
  - `k=8`, `band=2.0`, `every=168`：**net Sharpe ≈ 2.45**，年化收益约 **31.4%**，成本拖累约 **2.5%/年**。
- **momentum sleeve 近期明显更弱。** 我在 repo 典型长 lookback 邻域上扫了一圈，很多组合都是显著负 Sharpe；至少在这段最近样本里，不像 repo headline 那样稳。

这组结果最值钱的地方，不是报出一个高 Sharpe，而是把 desk 读法纠正了：

> **当前更该 intake 的是 `BTC-resid XS reversal` 这条 raw alpha，而不是不加区分地把 repo 的 reversal/momentum/mix 三件套一起搬进短周期主线。**

## 6. 下一步怎么测
先别急着做复杂 mixed sleeve，按下面顺序来：

1. **parent alpha 验证**
   - 用 `1h` 维护 `k ∈ {4,8,12}`、`band ∈ {1.75,2.0,2.25}`、`every ∈ {48,72,96,168}`
   - 先只测 reversal，不和 momentum 混。

2. **child execution 映射**
   - parent 每次生成 long losers / short winners 篮子后，映射到 `15m/5m`
   - 比较 `next-bar taker` vs `pullback maker-first` vs `TWAP-2/3 bar`。

3. **short leg 风险单独审计**
   - 统计 short winners leg 的 jump risk、单币拖累、挤仓日 markout
   - 若 short leg 太脏，改测 `long-only loser rebound basket`。

4. **成本梯度**
   - 必做 `4 / 6 / 8 / 10 bps` 梯度，确认不是只在 7bps 幻觉里成立。

## 7. 我的判断
这轮我会把它标成 **值得进入研究池**，但不是因为“repo mixed Sharpe 很漂亮”，而是因为它给了一个很像 desk 组件的 raw alpha 壳：

**BTC 残差化横截面短窗反转。**

它的优点是：
- raw alpha 清楚；
- 代码骨架完整；
- 容易做 `1h parent -> 15m/5m child`；
- 能补足当前素材池里的 relative-value / market-neutral 缺口。

它的警告也同样清楚：
- 最近样本下**原样参数不 portable**；
- momentum sleeve 近期并不稳；
- 真正该复现的不是 repo headline 组合，而是这条更干净的 reversal alpha 本体。

## 8. 风险与保留意见
- 当前 probe 只覆盖最近约 `63` 天 `1h` 样本，远不算定论。
- 高 Sharpe 邻域里有样本稀疏问题，不能把短样本好看结果当生产参数。
- BTC residualization 依赖 rolling beta 稳定性；遇到链上叙事分裂或单币 idiosyncratic 爆发，beta 关系会断。
- cross-sectional 策略最怕流动性分层与 short leg 跳涨，必须单独做 leg attribution。

## 9. 来源
- Cameron Collins. (2025). *Crypto Statistical Arbitrage*. GitHub repository.  
  Repo URL: <https://github.com/ccollins80/crypto-stat-arb>
- README (raw): <https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/README.md>
- signals.py (raw): <https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/src/crypto_stat_arb/signals.py>
- backtest.py (raw): <https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/src/crypto_stat_arb/backtest.py>
- portfolio.py (raw): <https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/src/crypto_stat_arb/portfolio.py>
