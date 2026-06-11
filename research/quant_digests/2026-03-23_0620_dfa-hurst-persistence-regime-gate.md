# 别把 breakout / EMA 的坏样本都怪进场形状：这篇 2025 新论文更值钱的是把 `DFA Hurst` 变成 persistence gate
- 时间：2026-03-23 06:20 UTC
- 类型：论文 + 开源实现库
- 主题类型：regime
- 基础 alpha：breakout / ema-psar continuation（既有 setup）
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/hurst/dfa/regime/filter/anti-chop/persistence/paper/repo/crypto/5m/15m
- 证据类型：论文证据 + 开源实现证据

## 1. 这次看了什么
这次看的是 **Noppakaew, Prinyasart, Chaiya & Chaiya (2025)** 的新论文：它研究的不是 crypto，但非常适合我们 desk 当前三条收口线的一个旁支问题——**什么时候根本不该让 trend / breakout 类东西开火**。

## 2. 核心结论
- **一句话核心结论：** 对当前 15m desk，更值得先偷的不是又一层新触发，而是一个便宜的 `persistence gate`：`DFA Hurst` 高时才让 breakout / EMA continuation 认真说话，低时优先当作 whipsaw 区。
- **一句话说明它怎么证明：** 论文把市场按 rolling Hurst regime 分桶，再比较 `EMA10` 驱动的 buy-hold / long-only / short-only / long-short 四类策略表现，结果显示 **高 persistence 明显更利于 active trend-following**，而且 **DFA 比 R/S 更诚实**。
- 论文最值钱的不是“Hurst 很神”，而是 **先校准 estimator 偏差，再拿它做 regime switch**。他们对长度 `64` 的随机游走做 Monte Carlo 后发现：
  - `R/S` 对纯随机过程也会偏高，均值约 `0.6002`；
  - `DFA` 更接近理论值，均值约 `0.5012`。
- 基于这组校准，论文给出 regime 切分：
  - `DFA low < 0.42`
  - `DFA medium = 0.42~0.58`
  - `DFA high > 0.58`
- 在 `DFA high` regime 下，**combined long-short** 的平均 `64-day return = 4.35%`，年化约 `17.13%`；
  但在 `DFA low` regime 下，同一 active 组合平均只剩 `-0.43%`。
- 反过来，`DFA low` 时 **buy-and-hold** 平均 `64-day return = 2.61%`，反而优于 active trend；这很像在提醒我们：**低 persistence 时别硬做 15m continuation，宁可少做，甚至退回被动/空仓。**

## 3. 为什么和当前项目有关
- **`EMA / PSAR raw alpha focus`**：这是最直接的帮助。它给的是“先判这段市场有没有趋势记忆”，而不是继续在噪音段里微调 EMA / PSAR 参数。
- **`V3 final-verdict / breakout-short follow-up`**：它很适合做 `avoid-chop / post-break continuation` 的 shared gate。若 `H_dfa` 落在 low bucket，很多所谓 post-break continuation，本质更可能只是来回抽打。
- **`Fibonacci confirmation / retest_hold`**：Fib 回踩也不是只要碰位就能做。若 backdrop 本身是低 persistence，回踩更像区间噪音回摆，`retest_hold` 应优先降权或 veto。
- 如果问“这轮为什么比继续闷头收某一条线更值得”：因为它是 **一个 price-only、公开可得、理论上能同时给三条线减 whipsaw 的共享 regime gate**，性价比很高。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / continuation 的 regime 过滤层
- 基础 alpha：breakout-short follow-up、Fib retest_hold、EMA continuation skeleton 之一
- regime：rolling `DFA Hurst` persistence state
- filter / veto：`H_dfa` 低于 low threshold 时 veto；中间带谨慎；高于 high threshold 时才放大 trend 解释权
- risk / sizing / execution overlay：也可改成 `low=0x / mid=0.5x / high=1x` 的分档仓位，而不是只做二元 allow/deny

## 4. 可复刻的最小实验
### 研究假设
对 `BTC/ETH/SOL perp 15m`，若只在 `high-persistence` 区间放行 breakout / EMA continuation，成本后表现会优于 baseline；`low-persistence` 区间更像 shared veto 区。

### 一个可计算定义
1. 在 `15m close` 上计算 rolling `DFA Hurst`，先试 `window = 128 / 192 bars`；
2. 对同窗口长度做 Monte Carlo random walk 校准，得到该 estimator 的 `μ, σ`；
3. 用论文同样的规则切桶：
   - `low: H < μ - 0.5σ`
   - `mid: μ - 0.5σ <= H <= μ + 0.5σ`
   - `high: H > μ + 0.5σ`
4. 把它接到现有三条线事件流上，只测试 gate，不改原 entry/exit。

### 最小回测切口
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT` perpetual
- 周期：`15m` 主回测，必要时 `5m` 仅用于执行价
- 样本：近 `180d`
- 对照：
  - `A` = baseline
  - `B` = 仅 `high-H` 放行
  - `C` = `low veto / mid 0.5x / high 1x`

### 第一轮先看
- `post-cost expectancy`
- `false-follow ratio` 或 `2~4 bar` 内反抽失败率
- `trade retention`（别为了变好看只剩极少交易）

## 5. 风险与保留意见
- 论文样本是 **东亚股票日线**，不是 crypto `15m`；可迁移的是“regime-switch 逻辑”，不是阈值直接照抄。
- Hurst 估计对窗口和实现细节敏感；论文已经明确提示 **先做 estimator-specific 校准**，不能直接拿网上某个 `H>0.5` 就上生产。
- 低频 persistence 指标会更像 backdrop/filter，不该伪装成逐根主触发。
- 若加上 gate 后只是大幅减少交易，但成本后优势不稳，那它更可能只是“美化报表”的稀释器，不是真 gate。

## 6. 来源
1. **Noppakaew, P., Prinyasart, T., Chaiya, M., & Chaiya, S. (2025). _Hurst Exponent as a Regime-Switching Indicator for Trend-Following Strategies in East Asian Stock Markets_. Asia-Pacific Journal of Mathematics, 12:109.**
   - DOI: `https://doi.org/10.28924/APJM/12-109`
   - Readable URL: `https://doi.org/10.28924/APJM/12-109`
   - PDF URL: `https://apjm.apacific.org/PDFs/12-109.pdf`
   - 关键信息：`DFA high > 0.58` 时 combined long-short 平均 `64-day return = 4.35%`；`DFA low < 0.42` 时同策略平均 `-0.43%`。

2. **Schölzel, C. (2019). _Nonlinear measures for dynamical systems_ (Version 0.5.2). Zenodo / nolds.**
   - DOI: `https://doi.org/10.5281/zenodo.3814723`
   - Readable URL: `https://pypi.org/project/nolds/`
   - Repo URL: `https://github.com/CSchoel/nolds`
   - 相关实现：`nolds.dfa()` 可直接用于最小实验的 DFA 估计。

3. **Binance USDⓈ-M Futures Market Data API（用于最小实验的数据口径）**
   - 数据源：Binance Developers
   - 公开性：公开可得
   - 更新频率：分钟级
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
