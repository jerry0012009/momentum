# 别把这份 2026 repo 只读成“把 trend 和 reversal 拼一起”：对 short-cycle crypto desk，更该先测的是「high-volume 趋势跟随 × low-volume 横截面反转 switch」这条完整 raw alpha 壳

- 时间：2026-04-19 14:05 UTC
- 类型：GitHub repo + Binance USDⓈ-M portability probe
- 主题类型：raw alpha
- 基础 alpha：高成交量时做 time-series momentum，低成交量时做 cross-sectional loser→winner fade；也就是“量大顺势、量小反转”的双母体切换。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：trend / momentum / cross-sectional / mean-reversion / volume-regime / switch / 15m / repo / cost
- 证据类型：GitHub repo 源码 + 本地 public-data portability probe

## 1. 这次看了什么

看的是 Parnell Thrower 2026 GitHub 仓 `PThrower/crypto-start-arb`。仓库不只是“把两个老策略拼盘”，而是给了一个很明确的 desk 化读法：**volume z-score 决定当前更该信趋势，还是更该信横截面反转**。源码核心只有一份 `crypto-stat-arb.py`，逻辑很透明：

- trend sleeve：最近一段收益相对长窗基线更强/更弱时，顺势多/空；
- reversal sleeve：横截面里 recent losers 做多、recent winners 做空；
- switch：`volume_signal > 0` 时偏向 momentum，`volume_signal < 0` 时偏向 reversal；
- 组合：再用每个币历史 Sharpe 做横截面权重。

## 2. 核心结论

- **一句话核心结论：** 这份 repo 最值钱的不是“trend+reversal 混搭”，而是那句很朴素但可测的话——**量大时跟、量小时反**。
- repo 原始口径用 Binance US `4h`、15 个大币，从 2022 年开始回测；作者声称 reversal sleeve Sharpe `3.68`、combined Sharpe `2.10`、max drawdown `-5.07%`。
- 我把它压到 Binance USDⓈ-M `15m`、10 个 liquid majors、近约 `90d` 做 portability probe 后，**switch 组合 gross 仍有正值**：约 `+0.18 bps/bar`、年化样式 Sharpe 约 `1.47`、累计约 `+14.11%`。
- 但这条线当前最大问题不是“没信号”，而是**换手过高**：平均 turnover 约 `16.47x/day`；按 `8bps` roundtrip 粗扣后，switch net 约 `-0.51 bps/bar`、累计约 `-36.93%`。
- 分 sleeve 看更清楚：`15m` 上 **low-volume reversal** gross 约 `+0.14 bps/bar`、Sharpe 约 `5.60`、max drawdown 仅 `-5.71%`，明显比 trend sleeve 更像有 edge；但成本后同样被换手吃掉。

## 3. 为什么和当前项目有关

这篇东西和当前 desk 的关系，不在于它证明了“一个新指标”，而在于它给了一个**可以直接拆件复现**的完整策略骨架：

- `entry`：先判断 volume regime，再决定是开 trend sleeve 还是 reversal sleeve；
- `exit`：下个 rebalance 点重算信号与权重；
- `sizing`：横截面归一化 + Sharpe weight；
- `risk`：多空对冲、控制 beta 暴露；
- `cost`：源码里已经显式扣 trading cost。

对 Jerry 当前阶段更有用的读法是：**别再把 volume 只当确认层**。它也可以是“挑哪类 raw alpha 上场”的 admission switch。

## 3.5 策略拆解（必填）

- 方向属性：顺势 + 横截面反转的 regime switch
- 基础 alpha：high-volume time-series momentum；low-volume cross-sectional loser→winner fade
- regime：用 short-vs-long volume z-score 区分“信息驱动”与“流动性/噪声驱动”时段
- filter / veto：只有 volume regime 与对应 sleeve 一致时才分配权重；成本门槛不过线则整段 veto
- risk / sizing / execution overlay：横截面 gross-normalize + Sharpe weighting；后续应加 turnover cap、child execution、top-k router

## 4. 本地最小实验结果与下一步怎么测

我用 Binance USDⓈ-M 公共 `15m` 数据做了一个 desk 化简版 probe：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`，样本约 `2026-01-19 ~ 2026-04-19`。把 repo 的 `4h 1w vs 6m` 逻辑压缩成 `15m` 的 `1d vs 30d`，reversal 用最近 `24h` 横截面 losers/winners 排名，volume regime 用 `1d vs 20d` quote-volume z-score。

关键数：

- **switch 组合**：gross `+0.18 bps/bar`，Sharpe `1.47`，累计 `+14.11%`；但 turnover `16.47x/day`，扣 `8bps` 后 net `-0.51 bps/bar`。
- **trend sleeve only**：gross 只有 `+0.04 bps/bar`，Sharpe `0.33`，说明 repo 在我们这套 `15m` transfer 上，trend 这半边并不厚。
- **reversal sleeve only**：gross `+0.14 bps/bar`，Sharpe `5.60`，累计 `+12.82%`，是更值得保留的母体；但扣成本后 net 约 `-0.27 bps/bar`。
- volume regime 覆盖上，`high-volume share` 约 `26.99%`，`low-volume share` 约 `50.80%`；也就是说，大部分时段其实更常落在“低量 / 更像反转环境”。

**下一步怎么测：**

1. **别先跑全量横截面**：先把 reversal sleeve 改成 `top1 / top2 loser-winner router`，目标是把 turnover 从 `16x/day` 压到 `<4x/day`。
2. **别每根 bar 都全量再平衡**：改成 `30m/1h` rebalance，但继续用 `15m` 做 signal 形成，测试 gross 是否还保得住。
3. **把 switch 做成 admission 而不是 continuous weight**：例如只有 `|vol_z| >= 1` 才允许切换，否则空仓，避免噪声 regime 来回翻。
4. **先做 low-volume reversal 单腿 pocket**：重点看 `LINK/AVAX/LTC/DOGE` 这类更容易出现 liquidity-driven overshoot 的币，别一开始就用 BTC/ETH 稀释。

Artifact：
- `reports/artifacts/quant_digests/2026-04-19_volume_switch_summary.json`
- `reports/artifacts/quant_digests/2026-04-19_volume_switch_portfolio_tail.csv`
- `reports/artifacts/quant_digests/2026-04-19_volume_switch_weights_tail.csv`

## 5. 风险与保留意见

- 这份 repo 的原始样本是 Binance US `4h`，我们这轮是 Binance perp `15m` 的 transfer check；结论更像“能不能迁移”的 first verdict，不是严格 reproduction。
- 作者给的年化成本 `0.16%` 对 `4h` 低频组合也许还能成立，但放到 `15m` perp taker 环境明显过轻。
- 现在最危险的误读是：看到 gross 正就直接把它当可上线完整策略。对短周期 desk，真正该保留的是 **volume-state switch 这个框架**，不是当前这套高换手实现本身。

## 6. 来源

- Parnell Thrower. (2026). *Cryptocurrency Statistical Arbitrage*. GitHub repository.
- Repo URL: https://github.com/PThrower/crypto-start-arb
- Readable URL: https://github.com/PThrower/crypto-start-arb/blob/main/README.md
- Source URL: https://github.com/PThrower/crypto-start-arb/blob/main/crypto-stat-arb.py
