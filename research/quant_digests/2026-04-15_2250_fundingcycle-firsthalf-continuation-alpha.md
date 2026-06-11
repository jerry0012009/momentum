# funding 周期前半段方向 × 后半段延续：把 intraday momentum 改写成 perp `8h` 可执行壳
- 时间：2026-04-15 22:50 UTC
- 类型：GitHub / 论文 grounding / public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：`8h funding 周期前半段（0~4h）收益方向，会在后半段（4~8h）继续延续`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw alpha / trend / momentum / intraday / funding-cycle / time-series / regime-gate / Binance USDⓈ-M / 15m
- 证据类型：工程经验 + 论文证据 + repo 策略卡

## 1. 这次看了什么
这次主材料不是再找一篇“又一个日频动量论文”，而是抓 2026 GitHub 策略库 **RexRenatus / The-Art-of-Finance** 里一条更适合 short-cycle desk 的分支：`trend/funding-momentum.md`。它把经典 intraday momentum 直接映射到 crypto perp 的 **`8h funding` 天然 session**：看 funding 周期前半段涨跌，去做后半段 continuation，并在 funding 边界强制平仓。

## 2. 核心结论
- **一句话核心结论：** 这条策略真正值钱的，不是“crypto 也有日内动量”这句老话，而是可以把它改写成一个很清楚的 `trade on / trade off` 壳：`前 4h 看方向，后 4h 做延续，funding 边界硬退出`。
- **一句话证明方式：** repo 给了清晰的 session 化策略骨架；我再用 Binance USDⓈ-M `15m` 公开数据把 plain 版和 corr-gated 版各跑一遍，看它在 BTC/ETH/SOL 上是否真能活过最小成本门槛。
- repo 里的 base alpha 很清楚：**不是 funding 本身，也不是时钟效应本身，而是 funding 周期内部的 return autocorrelation / intraday momentum**。
- 我做的 recent portability probe（`2025-10-01 ~ 2026-04-15`，`BTC/ETH/SOL`，`15m`）显示：**plain 版并不稳**。无 gate、每个 8h 周期都做时，BTC 平均 gross 约 `+6.27 bps/笔`，ETH 约 `+0.58`，SOL 约 `+1.73`；按 `4 bps` round-trip 后，只剩 BTC 还勉强为正。
- 但把 repo 的“session 内 continuation”再 desk 化成 **`|前 4h 收益| >= 10 bps` + 最近 `30` 个周期 `corr(first_half, second_half) >= 0.05`** 后，结果明显改善：BTC/ETH/SOL 的平均 **net** 约升到 `+8.51 / +18.27 / +9.42 bps/笔`，交易数降到 `190 / 158 / 119`。
- 这说明更合理的读法不是“8h 里任何方向都追”，而是：**只有当前 funding-cycle 的前半段冲击够明显，而且近期 half1→half2 相关性真的在，才开 second-half continuation。**

## 3. 为什么和当前项目有关
这条线和 desk 当前素材池直接相关，因为它补的是一条**真正独立的 raw alpha**，不是给现有策略打补丁：
- 它属于 `trend / time-series momentum`，但不是普通 N-bar breakout，而是 **event-time / session-time momentum**；
- 它天然适配 `5m / 15m`，因为 `8h` funding 周期本身就是 perp 市场的原生时钟；
- 它还能顺手长出一个 shared gate：最近若 `first-half -> second-half` 的滚动相关性转负，就直接不做，这比“永远追涨杀跌”更像可实盘的 desk 版本。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / time-series momentum
- 基础 alpha：`sign(return_{0~4h}) -> sign(return_{4~8h})`
- regime：最近 `N=30` 个 funding 周期里，`corr(first_half_return, second_half_return)` 为正且高于阈值
- filter / veto：`|first_half_return|` 必须超过最小门槛（如 `10 bps`）；只在第二半周期开仓；cooldown 禁止连续重入
- risk / sizing / execution overlay：按钱包百分比限仓；`8h` funding 边界强制平仓；实盘先按 `4 bps` round-trip 做成本门槛

## 4. 可复刻的最小实验
- **研究假设：** perp funding 周期前半段的价格方向，能预测同一 funding 周期后半段的方向；但这个效应不是全天候，而是 regime-dependent。
- **可计算定义：** 对每个 `8h` 周期（`00-08 / 08-16 / 16-24 UTC`），先算 `r1 = return(0~4h)`，再算 `r2 = return(4~8h)`；若 `|r1| >= 10 bps` 且过去 `30` 个周期 `corr(r1, r2) >= 0.05`，则在后半段开始时按 `sign(r1)` 入场，周期结束平仓。
- **最小回测切口：** Binance USDⓈ-M `BTC/ETH/SOL`，先做 `15m`，样本先看近 `180d`；若成立，再下钻 `5m` 看入场 timing 能否更好。
- **最先看 2 个指标：**
  1. `avg net bps/trade`（先看成本后单笔边际是不是还活着）
  2. `trade count`（别把它优化成一年只做几次的假 edge）
- **这轮 artifact：**
  - `reports/artifacts/quant_digests/2026-04-15_funding_momentum_probe_grid.csv`
  - `reports/artifacts/quant_digests/2026-04-15_funding_momentum_probe_epochs.csv`
  - `reports/artifacts/quant_digests/2026-04-15_funding_momentum_probe_summary.json`

## 5. 风险与保留意见
- repo 目前更像**策略卡片库**，不是单条策略的完整 production 回测；它给了骨架，但没有把 fee/slippage/default params 讲满，所以我把它判成“可独立复现，但还不是完整可上线壳”。
- 这里最大的 overfit 风险是：`8h funding` 恰好是 perp 特有时钟，**同一效应未必能平移到现货或别的 venue**。
- 我这轮 probe 也提示 plain 版很弱：**不加 gate 时，ETH/SOL 在 `4 bps` 成本下都不过线**。所以这条线更像 `raw alpha + regime gate`，不是“见涨就追”的万能动量书。
- 下一步别先调更多参数；先做两件事：
  1. 把 `entry` 从后半段开头细化到 `5m`，测试 `0~30m` 的最佳入场延迟；
  2. 加一个简单的 `funding-sign / realized-vol` veto，看 continuation 是不是只在某些 funding-cycle 状态里成立。

## 6. 来源
- RexRenatus. (2026). *The-Art-of-Finance* — `trend/funding-momentum.md`.
  - Repo URL: `https://github.com/RexRenatus/The-Art-of-Finance`
  - Readable URL: `https://github.com/RexRenatus/The-Art-of-Finance/blob/master/trend/funding-momentum.md`
- Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). *Market Intraday Momentum*. *Journal of Financial Economics*, 129(2), 394-414.
  - DOI: `10.1016/j.jfineco.2018.05.009`
  - Readable URL: `https://doi.org/10.1016/j.jfineco.2018.05.009`
- Shen, D., Urquhart, A., & Wang, P. (2022). *Bitcoin Intraday Time Series Momentum*. *Financial Review*, 57(2), 319-344.
  - DOI: `10.1111/fire.12290`
  - Readable URL: `https://doi.org/10.1111/fire.12290`
- Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). *Intraday Return Predictability in the Cryptocurrency Markets: Momentum, Reversal, or Both*. *The North American Journal of Economics and Finance*, 62.
  - DOI: `10.1016/j.najef.2022.101733`
  - Readable URL: `https://doi.org/10.1016/j.najef.2022.101733`
