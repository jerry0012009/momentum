# Tether 跳变 × BTC 事后漂移：别把 stablecoin shock 只当风险提示，它本身可以是 event-driven raw alpha

- 时间：2026-04-16 06:18 UTC
- 类型：论文 + public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：`USDT/USD 出现“统计意义上的上跳”且过去 24h 仍偏强时，BTC 在后续 15m~120m 存在可交易的方向漂移`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（baseline 版）
- 主题标签：event-driven / cross-asset / stablecoin / jump / momentum / btc / 5m / 15m / 60m
- 证据类型：论文证据 + 工程快检

## 1. 这次看了什么
主看 Finance Research Letters 论文 **When Tether says “JUMP!” Bitcoin asks “How low?”**（Aharon & Demir, 2021/2022），核心问题是：`USDT` 的跳变，是否会传导到 `BTC` 后续收益。然后我把它改写成更贴近 desk 的 `5m` 事件策略壳，并用 Bitfinex 公共 K 线做了最小可复现实验。

## 2. 核心结论
- 论文原结论（小时/日频语境）是：`USDT` 的正跳 + 前一日 `USDT` 上涨，会显著预测 **BTC 次日下跌**；文中给出的量级约 `-3.65% ~ -8.49%`（daily）。
- 我们在 `5m` 迁移版上看到的 first verdict 与论文方向**相反**：在 `2025-02-20 ~ 2026-04-16`，`jump_stat>12` 且 `USDT 24h ret>=+10bps` 的事件，后续 `60m` 的 BTC 平均 gross 约 `+28.03 bps`（相对全样本 `-0.14 bps`，lift 约 `+28.18 bps`）。
- 用非重叠执行（60m 持有、4bps round-trip）做最小策略壳：共 `57` 笔，long BTC 平均 net `+14.88 bps/笔`、累计 net 约 `+8.70%`；反向 short 平均 net `-22.88 bps/笔`、累计约 `-12.36%`。这说明这条线在 recent regime 更像 **shock 后顺势漂移**，不是日频反打。

## 3. 为什么和当前项目有关
- 这是一条独立的 event-driven raw alpha，不依赖已有 breakout/retest 形态。  
- 数据公开且高频可拿：Bitfinex `tUSTUSD` + `tBTCUSD` 分钟级即可复现。  
- 它天然可接到 `1m/3m/5m/15m`：信号在 `5m` 触发，执行和持有窗口可缩放，不需要等低频宏观发布。

## 3.5 策略拆解（必填）
- 方向属性：事件驱动 + 单资产方向（long 偏置）
- 基础 alpha：`USDT` 正跳事件后的 BTC 事后漂移
- regime：`USDT` 近 24h 为正（`ust_24h_ret >= +10bps`）
- filter / veto：`jump_stat > 12`（bipower-variation proxy），可再加 `BTC 近 1h 波动上限 veto`
- risk / sizing / execution overlay：
  - entry：信号 bar 后一根开仓（避免同 bar 未来函数）
  - exit：固定 `60m`（12 根 `5m`）强制平仓
  - sizing：每笔固定风险预算（如 25bps VaR）或波动缩放
  - cost：先用 round-trip `4bps`；上线前必须做 `4/6/8bps` 梯度
  - kill-switch：同方向连续亏损 `N` 笔或当日累计回撤超阈值时停机

## 4. 可复刻的最小实验
- 研究假设：`USDT` 正跳不是噪声，而是可交易的风险偏好冲击；在当前样本里更偏向 BTC 短时延续。  
- 可计算定义：
  - `jump_stat_t = r_t^2 / BV_t`，`BV_t = (π/2) * rolling_mean(|r_t||r_{t-1}|, 288)`
  - 事件：`ust_ret_t > 0` 且 `jump_stat_t > 12` 且 `ust_24h_ret_t >= 0.001`
- 最小回测切口：Bitfinex `tUSTUSD + tBTCUSD`，`5m`，近 `420d`。  
- 最先看 2 个指标：
  1) 事件后 `15/30/60/120m` 相对全样本的 return lift（bps）  
  2) 执行壳 net bps/笔 在 `4/6/8bps` 成本梯度下是否仍为正

## 5. 风险与保留意见
- 论文的日频结论与我们 `5m` 结果方向不一致，说明**强烈依赖时间尺度与市场阶段**，不能直接照抄论文方向。
- 信号稀疏（当前非重叠仅 `57` 笔），容易被少数极端事件主导，需要 rolling-window 稳定性检验。
- 实盘里 `USDT/USD` 报价深度、成交偏差、跨 venue 执行延迟会显著影响可得收益；必须补 execution realism。

## 6. 来源
1. **Aharon, D. Y., & Demir, E. (2021/2022). _When Tether says “JUMP!” Bitcoin asks “How low?”_ Finance Research Letters.**  
   - DOI: `10.1016/j.frl.2021.102644`  
   - Readable URL: `https://doi.org/10.1016/j.frl.2021.102644`  
   - OpenAlex metadata: `https://api.openalex.org/works/https://doi.org/10.1016/j.frl.2021.102644`  
   - Repo URL: `N/A (paper-only)`
2. **Bitfinex Public REST API (candles)**  
   - URL: `https://api-pub.bitfinex.com/v2/candles/trade:5m:tUSTUSD/hist`  
   - URL: `https://api-pub.bitfinex.com/v2/candles/trade:5m:tBTCUSD/hist`
3. **本轮 probe artifact**  
   - Script: `reports/artifacts/quant_digests/2026-04-16_tether_jump_btc_probe.py`  
   - Summary: `reports/artifacts/quant_digests/2026-04-16_tether_jump_btc_probe_summary.json`
