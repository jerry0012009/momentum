# 别把这份 2026 repo 只读成“动量+反转拼盘作业”：对 short-cycle desk，更该先测的是「low-volume XS loser-bounce × high-volume TSMOM router」
- 时间：2026-04-07 18:30 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `crypto-stat-arb.py` + GitHub repo metadata）
- 主题类型：raw alpha
- 基础 alpha：低量环境下，横截面短窗 loser-bounce / winner-fade；放量时再把同一批币切回顺势 TSMOM
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / mean reversion / momentum / volume / router / market-neutral / top-liquid-universe
- 证据类型：工程经验

## 1. 这次看了什么
看的是 Parnell Thrower 在 2026-04-04 创建的 GitHub repo `PThrower/crypto-start-arb`。它表面上是在做“TS momentum + XS reversal”双书组合，但对我们 desk 更值钱的不是“多策略混搭”四个字，而是一个很朴素、可立刻搬到 `15m / 5m` 的判断：**同样是过去一段时间涨跌，安静盘口更容易走回补，放量盘口才更容易走延续。**

## 2. 核心结论
- 一句话核心结论：**不要把短窗收益信号固定解释成动量或反转；先看量，低量更像均值回复，高量更像顺势延续。**
- 一句话证明方式：repo 直接把 15 个大币的收益信号与 `volume z-score` 连起来做两本交易书，并给出成本后结果：`Momentum Sharpe 1.50`、`Reversal Sharpe 3.68`、组合后 `Sharpe 2.10`、`Max DD -5.07%`、`beta vs BTC 0.011`、年化交易成本约 `0.16%`。
- 代码不是二元开关，而是用 `tanh(vol_z)` 做连续路由：量越大，越偏向 momentum；量越弱，越偏向 reversal，这比“硬阈值切 regime”更适合后续搬到短周期。
- repo 里的 reversal 书本质是**横截面 loser-bounce / winner-fade**：按短窗相对收益排序，做多相对落后、做空相对领先，天然更像我们现在需要补的 raw alpha 素材，而不是又一个 breakout 过滤器。

## 3. 为什么和当前项目有关
- 它直接扩充的是 **raw alpha 素材池**，而且同时覆盖 `cross-sectional mean reversion` 与 `time-series momentum` 两条线，不依赖某个固定图形。
- 它给了一个很容易迁移的 shared component：`volume z-score router`。这个 router 不只服务这篇 repo，也能拿去给 breakout、lead-lag、pairs 做同样的“安静/热闹”分流。
- 对 short-cycle desk 来说，最值钱的不是原 repo 的 `4h` 结果本身，而是它把“收益信号解释权”交给了量：**先判断这波 move 是在拥挤追价，还是在冷清回补。**

## 3.5 策略拆解（必填）
- 方向属性：横截面 + 时间序列混合；其中更值得先独立测的是横截面逆势
- 基础 alpha：低量环境下的 XS loser-bounce / winner-fade
- regime：`vol_z = sqrt(short) * (vol_short_mean - vol_long_mean) / vol_long_std`
- filter / veto：`tanh(vol_z)` 连续缩放；高量偏向 momentum，低量偏向 reversal
- risk / sizing / execution overlay：横截面书做 dollar-neutral 归一化，TS 书用 `tanh(signal)` 限幅；repo 再按各币历史 Sharpe 做 capital allocation，交易成本假设 `20 bps`

## 4. 可复刻的最小实验
- 研究假设：在 `15m / 5m` 上，**过去 24h 相对最弱的一篮子币，在低量环境下更容易反弹；一旦量能抬起来，同样的短窗收益差更可能继续扩散而不是回补。**
- 一个可计算定义：
  - universe：Binance 永续或现货前 `15~20` 个高流动币
  - `ret_24h_rank`：过去 `24h` 收益横截面排序（`15m` 可用 `96` bars；`5m` 可用 `288` bars）
  - `xs_rev_w`：做多 bottom 20%，做空 top 20%，权重按绝对值归一到 1
  - `vol_z`：`24h` 平均成交量相对 `30d` 基线的 z-score（`15m` = `96 vs 2880` bars；`5m` = `288 vs 8640` bars）
  - 头寸：`w = xs_rev_w * max(0, -tanh(vol_z))`；可选再并联 `tsmom_w * max(0, tanh(vol_z))`
- 最小回测切口：先跑 `2024-01-01 ~ 2026-03-31` 的 `15m`；交易在下一根开盘执行，持仓每根再平衡；费用先用 `6~10 bps` 单边，再做 `10/15/20 bps` friction ladder。`5m` 只做稳健性复查，不先上满宇宙。
- 最该先看哪 1~2 个指标：`post-cost Sharpe`、`turnover-adjusted return`；补一个 `positive-month ratio` 看是不是只靠少数极端窗口赚钱。

## 5. 风险与保留意见
- 这份 repo 的原始实验是 `Binance US + 4h`，直接平移到全球主流所的 `5m / 15m` 不会自动成立，尤其成本和容量完全不是一个量级。
- `volume z-score` 既可能代表“信息流入”，也可能只是“波动放大”；如果不把量和 realized vol 分开，容易把高波动错当高质量趋势。
- 原 repo 的组合结果很好，但真实可迁移的未必是“组合后 Sharpe 2.10”，更可能只是其中那条 **低量 XS reversal** 的方向性判断；所以第一轮别急着抄整套 allocation，先测 raw alpha 本体。

## 6. 来源
- Parnell Thrower. (2026). *Cryptocurrency Statistical Arbitrage*. GitHub repository.
- Repo URL: `https://github.com/PThrower/crypto-start-arb`
- README URL: `https://github.com/PThrower/crypto-start-arb/blob/main/README.md`
- Code URL: `https://github.com/PThrower/crypto-start-arb/blob/main/crypto-stat-arb.py`
