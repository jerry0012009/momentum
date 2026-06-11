# 别把山寨币相对 BTC 的偏离只当噪音：这份 2025 新 repo 更适合先复现的是 BTC-neutral residual mean reversion 这条 raw alpha
- 时间：2026-03-23 13:48 UTC
- 类型：2025 GitHub 新仓库 + accompanying article + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：BTC-neutral residual-return mean reversion（先剥离 BTC 市场 beta，再做山寨币 idiosyncratic reversal）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/idiosyncratic/residual/beta-neutral/mean-reversion/binance/perp/crypto/1m/3m/5m/15m
- 证据类型：工程证据 + accompanying writeup + 本地最小快检（可复现）

## 1. 这次看了什么
先回答 base alpha：**这次的基础 alpha 不是 momentum filter，也不是 regime gate，而是“剥掉 BTC 市场因子后的残差回归”本体。**

主看 **Brian Plotnik (2025)** 的新仓库 `briplot/systematic-crypto-strategy` 及其 accompanying article。仓库里虽然同时做了 momentum、volatility filter 和 regime-aware switching，但对当前 desk 最值得单拎出来的，其实是 **BTC-neutral residual mean reversion**：先用 rolling beta 把 alt 的市场暴露对 BTC 做净化，再去抓“相对 BTC 走得过头”的 idiosyncratic 偏离回归。

这条线对我们有价值，因为它不是继续围着 breakout / retest 打补丁，而是在补一条更像 **cross-sectional / relative-value / beta-neutral** 的 raw alpha 家族。

## 2. 核心结论
- **一句话核心结论：** 这份新 repo 里最适合当前 desk 先复现的，不是 headline 的动量分支，而是 **BTC-neutral residual mean reversion** 这条可独立落地的 raw alpha。
- **一句话证明方式：** 源仓库给了完整策略骨架和相对强的历史表现；我再把同一思路压到 Binance `15m` 做代理快检，结果显示“毛边存在，但很薄、而且明显成本敏感”。
- 源 writeup 给出的结果里，**BTC-neutral residual mean reversion Sharpe 约 `2.3`（文中口径为 net-cost）**，而且作者明确说它在 **post-2021** 阶段更强；说明它更像“后牛市、偏震荡/分化市场”的可交易骨架，而不是只能活在单边趋势里。
- 同文还给了一个组合读法：若把 momentum 与 residual mean reversion 做 `50/50` 混合，组合 **Sharpe 约 `1.71`、年化收益约 `56%`、T-stat 约 `4.07`**。对我们的启发不是“必须混合”，而是这条 residual alpha 至少不是附庸，它能独立贡献组合多样性。
- 本地 `15m` 代理快检（Binance USDT perp，近 `1500` 根 `15m`，`ETH/SOL/BNB/XRP/ADA/DOGE/LINK` 相对 `BTC`，rolling beta `96` bars、residual z-score `64` bars，横截面 long 最负 residual-z 两个、short 最正 residual-z 两个）结果：
  - `H=1` bar：**gross `+0.42 bps/rebalance`**，hit rate **`52.7%`**
  - `H=8` bars：**gross `+2.19 bps/rebalance`**，hit rate **`53.6%`**
  - 但若粗扣 **`8 bps`** round-trip 成本，仍然是 **负的**（`-7.58 / -5.81 bps`）
- 单币极值回归也能看到一些 side-specific 毛边：
  - `ETHUSDT` 当 residual `z > 2` 时，下一根 residual 回落命中率约 **`60.6%`**
  - `BNBUSDT` 对应约 **`56.8%`**
  - `XRPUSDT` 对应约 **`63.6%`**
  但负向极值并不对称，`SOL/ADA` 也不稳定，说明这条 alpha **更像“择币 + 择侧 + 择成本”的家族**，不是全市场同权万能公式。

## 3. 为什么和当前项目直接相关
- 它直接补的是 **raw alpha 素材池**，而且属于当前比较缺的那一侧：`relative value / beta-neutral / idiosyncratic mean reversion`。
- 它天然能拆成完整策略：
  - entry：残差 z-score 极值
  - exit：回归到阈内 / 固定持有 / 反向极值
  - sizing：beta-neutral 或 dollar-neutral
  - risk：单币上限、BTC shock veto、相关性坍塌监控
  - cost：maker/taker、滑点、参与率、资金费
- 对 `1m/3m/5m/15m` 也友好。它不是要求你判断“BTC 接下来涨还是跌”，而是看 **alt 相对 BTC 的偏离有没有走过头**；这类信号更容易先在 `15m` 做 first verdict，再下钻到 `5m/3m`。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / beta-neutral mean reversion
- 基础 alpha：对每个 alt 估计相对 BTC 的 rolling beta，构造 `resid_i,t = r_i,t - beta_i,t * r_BTC,t`；当 `resid z-score` 极端偏正时做空该币，极端偏负时做多该币，赌其向自身均值回归
- regime：更适合 BTC 不处在单边暴走、但山寨分化仍明显的阶段；也更适合 cross-sectional idiosyncratic dispersion 不低的时候
- filter / veto：BTC 极端跳变、宏观事件窗口、盘口过薄、资金费异常、beta 估计不稳定、单边 squeeze 资产先 veto
- risk / sizing / execution overlay：beta-neutral 或 dollar-neutral；单币权重上限；优先 maker / 分批成交；把 round-trip fee、滑点、impact、funding 显式入账；必要时先做“单边最极端 residual”而不是全横截面铺满

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** 在 `15m` 甚至 `5m/3m`，alt 相对 BTC 的 residual 极值存在短持有回归，但只有在 `择币 + 择侧 + 成本控制` 后才可能留下净边。
- **最小定义：**
  - 数据：Binance USDT perp 公共 klines（公开可得，`15m` 起步；后续下钻 `5m/3m`）
  - 标的：先用 `BTC + 15~20` 个高流动山寨币
  - beta：rolling `96 / 192` bars
  - 信号：rolling residual z-score（先测 `64 / 96` bars）
  - 入场：`z > 1.5 / 2.0` 做空、`z < -1.5 / -2.0` 做多
  - 出场：`|z| < 0.5`、或固定持有 `H = 1 / 4 / 8` bars、或 `max_hold`
- **最小回测切口：**
  1. 先跑 `15m`：`beta_window × z_window × threshold × hold` 网格；
  2. 再做 `sign asymmetry`（只做正残差回归 or 只做负残差回归）；
  3. 再做 `symbol subset`（只保留 ETH/BNB/XRP 这类更像有边的资产）；
  4. 最后再下钻 `5m/3m` 看 alpha 是放大还是被噪音/成本吞掉。
- **先看 4 个指标：** `post-cost bps/rebalance`、`turnover/day`、`sign-asymmetry hit rate`、`capacity@participation cap`。
- **当前最具体的 first verdict：** 不要一上来做“全市场双边全开”。从本地快检看，更值得先测的是：**`15m`、`H=1~8`、只做正残差极值回归、聚焦 ETH/BNB/XRP 这类更稳定的 short-overreaction leg。**

## 5. 风险与保留意见
- 这条 alpha 当前最明显的问题不是“完全没信号”，而是 **信号太薄，容易死在成本**。
- 源仓库主要是日频研究口径；我们压到 `15m` 后，beta 稳定性、盘口冲击、funding 时点、交易费率都会变成一等公民。
- 本地快检只用了最近一段 Binance perp 数据，且成本还是粗口径；它只能证明“值得进入 first verdict”，不能证明“已经 ready for live”。
- residual mean reversion 很容易在 BTC 单边加速、山寨币同步 beta 扩张时失效，所以它后续大概率需要一个 **BTC shock veto / dispersion gate**，但这些是第二阶段，不该先喧宾夺主。

## 6. 来源
1. **Plotnik, B. (2025). _systematic-crypto-strategy_. GitHub repository.**
   - Repo URL: https://github.com/briplot/systematic-crypto-strategy
   - Readable URL: https://github.com/briplot/systematic-crypto-strategy
2. **Plotnik, B. (2025). _Systematic Crypto Trading Strategies: Momentum, Mean Reversion & Volatility Filtering_. Medium.**
   - Readable URL: https://medium.com/@briplotnik/systematic-crypto-trading-strategies-momentum-mean-reversion-volatility-filtering-8d7da06d60ed
3. **Liu, Y., Tsyvinski, A., & Wu, X. (2022). _Common Risk Factors in Cryptocurrency_. Journal of Finance, 77(2), 1133–1177.**
   - DOI: `10.1111/jofi.13119`
   - Readable URL: https://doi.org/10.1111/jofi.13119
   - Working paper URL: https://www.nber.org/papers/w25882

## 7. 本地复现产物
- `reports/artifacts/quant_digests/btc_neutral_resid_mr_20260323/summary.csv`
- `reports/artifacts/quant_digests/btc_neutral_resid_mr_20260323/single_asset_extremes.csv`
- `reports/artifacts/quant_digests/btc_neutral_resid_mr_20260323/trade_proxy_H1.csv`
- `reports/artifacts/quant_digests/btc_neutral_resid_mr_20260323/trade_proxy_H4.csv`
- `reports/artifacts/quant_digests/btc_neutral_resid_mr_20260323/trade_proxy_H8.csv`
- `reports/artifacts/quant_digests/btc_neutral_resid_mr_20260323/close_tail_500.csv`
- `reports/artifacts/quant_digests/btc_neutral_resid_mr_20260323/meta.txt`
