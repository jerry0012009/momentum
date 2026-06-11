# 别先把 DNN 当主角：这篇 2026 pairs 论文里更值钱的是 dynamic co-integration spread 这条 raw alpha 骨架
- 时间：2026-03-23 09:58 UTC
- 类型：近 5 年论文 + 开源复现仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：cross-asset relative-value / pairs mean reversion（动态均衡价差回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs/stat-arb/relative-value/mean-reversion/dynamic-cointegration/zscore/dnn/lstm/repo/paper/crypto/5m/15m
- 证据类型：论文证据 + 工程证据 + 本地快检（可复现）

## 1. 这次看了什么
这次主看 **Tsoku, Makatjane (2026)** 的 *Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs*，以及对应的开源复现仓库。对我们 desk 来说，最值得先偷的不是 “DNN/LSTM 预测器” 本身，而是更底层、也更容易先复现的 **dynamic co-integration spread → z-score 回归** 这条 `raw alpha` 骨架。

## 2. 核心结论
- **一句话核心结论：** 这篇东西真正适合我们现在拿来做最小实验的 base alpha，不是“深度学习会算”，而是 **跨币动态均衡偏离后，做 market-neutral 的价差回归**。
- **一句话证明方式：** 论文先用 rolling Johansen 找会随时间变化的均衡关系，再用 DNN/LSTM/DWE 预测 spread；仓库还把 look-ahead、退出状态机和 hedge-ratio turnover 问题补得更诚实。
- 论文摘要的关键信号不是“所有相关币都能做”，而是：**只有动态关系仍然 coherent 的 pair，mean reversion 才值得交易**。
- 仓库里最值钱的工程细节有 3 个：**expanding percentile 防偷看未来**、**进入后持有到回归/超时的 finite-state exit**、**对 hedge ratio 做 EWM smoothing 以压 turnover**；最后一个在仓库里把 hedge-ratio 换手压了约 **72%**。
- 对我们 desk 最重要的启发：**先把 pairs/stat-arb 作为独立 raw alpha 家族补进素材池**，不要继续只在 breakout / retest / trend filter 上内循环。

本地 15m 最小快检（Binance perp，2026-02-04 → 2026-03-23，rolling beta + spread z-score，`entry=|z|>2`，`exit=|z|<0.25 or timeout=24 bars`，双边成本粗估 `6bps`）结果：
- `ETH~BTC`：`42` 笔，`mean gross ≈ +3.48bps/trade`，`mean net ≈ -8.52bps/trade`
- `SOL~ETH`：`43` 笔，`mean gross ≈ +0.32bps/trade`，`mean net ≈ -11.68bps/trade`

读法要诚实：**raw alpha 方向是对的，但“把日频论文直接压成 15m naive z-score 交易”还不够过成本。** 这反而说明下一步该优先补的是 pair selection / regime / turnover control，而不是先堆更复杂模型。

## 3. 为什么和当前项目直接相关
- 它补的是我们当前明显稀缺的 **raw alpha 家族**：`pairs / stat-arb / relative value / mean reversion`，不是又一个 filter。
- 它天然是 **完整策略骨架**：有 entry、exit、仓位配比、超时、成本与换手问题，不需要先依附 breakout/EMA 才能存在。
- 即使最后 DNN/LSTM 不上生产，`dynamic spread + z-score + beta smoothing + state exit` 这套骨架也能直接进入 `5m/15m` 的 first-verdict 阶段。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / market-neutral mean reversion
- 基础 alpha：`spread_t = log(y_t) - beta_t * log(x_t)` 偏离 rolling equilibrium 后向均值回归
- regime：仅在 rolling cointegration / ADF / half-life 稳定、且 funding/波动不极端时开机
- filter / veto：pair 失稳、结构断裂、成交额不足、重大事件时段、spread 过宽但 liquidity 不足
- risk / sizing / execution overlay：beta-neutral 或 dollar-neutral 配比、EWM 平滑 hedge ratio、time stop、gross leverage cap、双边成本和 funding 明确计入

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** 在 `1m/3m/5m/15m`，不是所有主流币 pair 都有可交易回归；但对“关系稳定 + 换手可控”的 pair，dynamic spread mean reversion 可能成为独立 raw alpha。
- **最小定义：**
  - 候选池：`BTC/ETH/SOL/BNB` 两两成对
  - `beta_t`：rolling OLS 或 rolling Johansen（先从 OLS 开始）
  - `z_t`：对 spread 做 rolling z-score
  - 入场：`|z_t| > 2.0`
  - 出场：`|z_t| < 0.5` 或 `max_hold` 到期
  - 仓位：按 `1 : beta_t` 做 beta-neutral，并对 `beta_t` 做 EWM smoothing
- **最小回测切口：** 先跑 `ETH/BTC、SOL/ETH、BNB/ETH` 的 `15m`，样本 60~90 天；若有希望，再下钻 `5m/3m`。
- **先看 4 个指标：** `post_cost_expectancy`、`turnover/day`、`mean-reversion hit ratio`、`timeout exit ratio`。

## 5. 风险与保留意见
- 论文主体是 **日频** 设定，不能把它的表现直接偷渡成 15m 结论。
- pair trading 最容易死在 **关系断裂 + 成本 + 高频重平衡**，不是死在“信号不会回归”。
- DNN/LSTM 在我们当前阶段不是第一优先；若 raw spread 本体过不了 first verdict，先别让模型复杂度掩盖问题。
- 本地快检目前只说明“naive 15m 直接移植不够”，不说明这条 raw alpha 应该放弃。

## 6. 来源
1. **Tsoku, J. T., & Makatjane, K. (2026). _Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs_. Frontiers in Applied Mathematics and Statistics.**
   - DOI: `10.3389/fams.2026.1749337`
   - Readable URL: https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/full
2. **M-man2591. (2026). _deep-learning-crypto-pairs-trading_. GitHub repository.**
   - Repo URL: https://github.com/M-man2591/deep-learning-crypto-pairs-trading
   - Readable URL: https://github.com/M-man2591/deep-learning-crypto-pairs-trading

## 7. 本地复现产物
- `reports/artifacts/quant_digests/dynamic_pairs_proxy_20260323/summary_normalized.csv`
- `reports/artifacts/quant_digests/dynamic_pairs_proxy_20260323/trades_15m_ETHUSDT_BTCUSDT.csv`
- `reports/artifacts/quant_digests/dynamic_pairs_proxy_20260323/trades_15m_SOLUSDT_ETHUSDT.csv`
- `reports/artifacts/quant_digests/dynamic_pairs_proxy_20260323/BTCUSDT_15m.csv`
- `reports/artifacts/quant_digests/dynamic_pairs_proxy_20260323/ETHUSDT_15m.csv`
- `reports/artifacts/quant_digests/dynamic_pairs_proxy_20260323/SOLUSDT_15m.csv`
