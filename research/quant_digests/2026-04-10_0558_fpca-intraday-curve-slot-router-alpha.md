# 别把这篇 FPCA 论文只读成“函数型时间序列统计”：对 short-cycle desk，更该先测「rolling intraday-curve PC × fixed-slot sign router」
- 时间：2026-04-10 05:58 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：最近一段时间的**日内收益曲线形状**可以压缩成少数几个主成分；这些 latent intraday-shape factor 的滚动预测，对下一天**固定时段**的 15m/1h 方向有可交易信息。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / intraday / time-series / single-asset / BTC / FPCA / PCA / time-of-day / slot-router / 15m / 1h
- 证据类型：论文证据 + 本地 public-data portability probe

## 1. 这次看了什么
Jasiak, Joann & Zhong, Cheng（2025）arXiv working paper《Intraday Functional PCA Forecasting of Cryptocurrency Returns》。论文把 BTC 的日内 return curve 当成函数对象，而不是逐根 bar 独立看；先用 FPCA / KL dynamic factor 把“这一天的日内形状”压成少数主成分，再滚动预测下一天的曲线。

## 2. 核心结论
- **一句话核心结论**：这篇东西最值得记住的，不是“PCA 能预测价格”，而是**日内收益的形状本身有可重复的固定时段信息**，更像 `slot router`，不一定适合直接做全天候逐 bar 方向书。
- **一句话证明方式**：作者用 BTC 的 hourly / 15-minute return function 做 rolling FPCA 预测，再把预测曲线落回固定时点，与 OLS / Ridge / LASSO / ARMA / SVM / NN 做方向与误差比较。
- 论文里最硬的一组结果来自 **hourly one-step rolling forecast**：`Ridge OLS` 的 sign 命中率约 `62.5%`，`OLS` 约 `59.0%`，明显高于 `ARMA` 约 `50.2%`、`LASSO` 约 `47.9%`、`NN` 约 `52.1%`。
- 它更像在说：**可预测的不是“整天每一根 bar 都有边”，而是某些固定 clock-time 的 return shape 更可预测**。
- 我用 Binance USDⓈ-M `BTCUSDT 15m` 近约 `219` 个完整 UTC 日做最小 portability probe：若直接把 rolling-FPCA 预测曲线翻成“下一天 96 个 15m 槽位全做 sign book”，结果很弱，all-slot shell 仅约 `49.4%` sign、gross 约 `-0.31 bps/bar`；说明**不能把论文生搬成全天候 15m 连续翻仓策略**。
- 但若只看固定时段的描述性 pocket，局部确实出现和论文一致的“same-clock predictability”：例如 `01:00 UTC` 槽位在样本里约 `63.8%` sign、gross 约 `+3.92 bps`，`02:15 UTC` 约 `57.5%` sign、gross 约 `+2.64 bps`。这更支持把它读成**时间槽位筛选器 / router**，而不是整天都开的单币方向壳。

## 3. 为什么和当前项目有关
这篇最有价值的地方，是给 short-cycle desk 补了一类之前没系统拆过的 raw alpha：
不是 breakout、不是 pairs、也不是 funding，而是**“日内曲线形状因子” → 固定时段方向预测**。
它直接服务于 `15m`：
- 可先只做 `BTC` 单币；
- 可把输出喂给已有 momentum / reversal 壳，决定**哪些 UTC 槽位值得开机**；
- 也可扩展成 `BTC lead curve -> ETH/SOL fixed-slot follower` 的 cross-market 版本。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 单资产日内方向预测
- 基础 alpha：rolling FPCA 预测的 next-day fixed-slot return sign
- regime：可后接 realized vol / event-day / session pocket 分层
- filter / veto：只保留历史稳定槽位、只做 `|forecast|` 高分位、重大事件前后 veto
- risk / sizing / execution overlay：按预测幅度分层仓位；单槽位 time-stop=1 bar；必须单独过 taker/maker friction ladder

## 4. 可复刻的最小实验
- 研究假设：最近 `30~60` 个 UTC 日的 intraday return curve，经 FPCA 压缩后，能预测下一 UTC 日若干固定 15m 槽位方向。
- 一个可计算定义：对 `BTCUSDT 15m`，每天形成 `96` 维 return curve；滚动窗口做 PCA，保留前 `2~5` 个 PC；对 PC score 做 AR(1) / ridge forecast；得到 next-day `96` 槽位预测收益。
- 最小回测切口：`BTCUSDT` 永续，先做 `2025-09` 以来的 `15m`；比较三种书：`all-slot sign book`、`top-|forecast| quartile`、`固定 6~10 个训练期稳定槽位`。
- 最该先看：`(1) 每个 UTC 槽位的 sign hit / gross bps`，`(2) 成本后 pnl 是否只集中在少数 slot`。

## 5. 风险与保留意见
- 论文证明的是**预测精度优势**，不是成本后 production alpha 已成立。
- 我这次 `15m` perp portability probe 已经说明：**全时段硬上会失真**。
- 局部强槽位很可能漂移，必须做 rolling slot-stability 检验，不能拿 ex-post 最强时段直接上实盘。
- 若要迁移到 `5m`，维度会从 `96` 槽位膨胀到 `288`，更容易过拟合；先别急着全市场横向扩展。

## 6. 来源
- Jasiak, J., & Zhong, C. (2025). *Intraday Functional PCA Forecasting of Cryptocurrency Returns*. arXiv working paper.
- DOI: `10.48550/arXiv.2505.20508`
- Readable URL: `https://arxiv.org/abs/2505.20508`
- HTML: `https://arxiv.org/html/2505.20508`
- Local artifacts:
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/fpca_intraday_curve_probe_summary_2026-04-10.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/fpca_intraday_curve_probe_detail_2026-04-10.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/fpca_intraday_curve_probe_slot_summary_2026-04-10.csv`
