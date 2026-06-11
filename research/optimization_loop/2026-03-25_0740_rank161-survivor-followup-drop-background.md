# Rank 161 survivor follow-up — EPCM microstructure taker alpha 成本后 pocket 不成立，回落 Background pool

- 时间：2026-03-25 07:40 UTC
- 对象：Rank 161 / EPCM microstructure taker alpha
- 别名：Explainable Patterns in Cryptocurrency Microstructure / `amazingchow/epcm`
- 来源：`research/optimization_loop/2026-03-25_0727_rank161_epcm-microstructure-intake.md`
- 本轮动作：执行 survivor 唯一一次 decisive follow-up；只回答它在 `BTC / ETH / 1 个中小币（ROSE）` 的最小滚动快检中，按保守 taker friction 后是否仍保留稳定正的 `post-cost avg bps/event` pocket
- 本轮结论：`drop_to_background`

## 方法（严格按上一轮 blocker 收口）
- 数据：Binance USDⓈ-M Futures 公共日包 `bookTicker + trades`
- 标的：`BTCUSDT / ETHUSDT / ROSEUSDT`
- 日期：`2024-01-15`（单日最小快检）
- 频率：聚合到 `1s`
- 特征：只保留 intake 指定的 paper 原生骨架：
  - `order_flow_imbalance`
  - `depth_imbalance`
  - `vwap_pressure`
  - `relative_spread`
- 训练/验证：前半天拟合线性 proxy，后半天 out-of-sample 测试
- 扫描：`hold_seconds ∈ {3,5,10}`，`threshold_q ∈ {0.8,0.9,0.95,0.975}`，`cost_bps_rt ∈ {2,4,6}`
- 收口指标：`events`、`gross_avg_bps_event`、`post_cost_avg_bps_event`

产物：
- `reports/artifacts/rank161_epcm_survivor_followup_20260325/survivor_followup_summary.csv`
- `reports/artifacts/rank161_epcm_survivor_followup_20260325/survivor_followup_best_6bps.csv`
- `reports/artifacts/rank161_epcm_survivor_followup_20260325/survivor_followup_coefficients.csv`
- `reports/artifacts/rank161_epcm_survivor_followup_20260325/survivor_followup_predictions_head.csv`

## 核心发现
方向相关性没有消失，但它留下的是**可预测性线索**，不是足够覆盖 taker friction 的可交易 pocket。

### 1) BTC：最佳毛收益也只有 `0.96 bps/event`
最佳 6bps 口径来自 `hold=10s, q=97.5%`：
- `score_corr_next_ret = 0.141`
- `events = 1253`（半天测试段）
- `gross_avg_bps_event = +0.963`
- `post_cost_avg_bps_event = -5.037`

即使把成本降到 `2 bps rt`，同一最佳 pocket 仍只有：
- `post_cost avg = -1.037 bps/event`

### 2) ETH：方向性更强，但毛收益上限仍不足以穿过 taker 成本
最佳 6bps 口径来自 `hold=5s, q=97.5%`：
- `score_corr_next_ret = 0.216`
- `events = 1465`
- `gross_avg_bps_event = +0.855`
- `post_cost_avg_bps_event = -5.145`

即使降到 `2 bps rt`：
- `post_cost avg = -1.145 bps/event`

### 3) ROSE（中小币）：alt 端也没有留下成本后正 pocket
最佳 6bps 口径来自 `hold=3s, q=97.5%`：
- `score_corr_next_ret = 0.127`
- `events = 456`
- `gross_avg_bps_event = +0.981`
- `post_cost_avg_bps_event = -5.019`

即使降到 `2 bps rt`：
- `post_cost avg = -1.019 bps/event`

## 决策为什么必须直接收口为 drop
上一轮 survivor blocker 问的不是“有没有方向信息”，而是：

> 在保守 taker friction 下，这条 `3s` 事件驱动 alpha 是否还保留稳定正的 `post-cost avg bps/event` pocket？

本轮答案已经足够明确：**没有。**

- 三个标的都能看到正的 `score → next_ret` 相关；
- 但所有扫描到的最佳 pocket，毛收益都只落在 `0.8~1.0 bps/event`；
- 按保守 `2/4/6 bps round-trip` friction 全部转为负值；
- 中小币也没有出现“alt-only 例外口袋”。

所以它不适合继续以前排资源进入 `P2` admission。若未来要重开，只能以**完全不同的执行假设或 maker/latency 优势**重新定义 scope，而不是沿当前 taker raw alpha 口径继续补测。

## 本轮 runtime 一句话
`Rank 161 / EPCM microstructure taker alpha` 在 `BTC / ETH / ROSE` 的最小滚动快检里虽然仍有未来几秒方向信息，但最佳毛收益上限仅约 `0.85~0.98 bps/event`，在保守 `2~6 bps` taker friction 下全部转为负值，因此 survivor follow-up 直接收口为 `drop_to_background`，不升 `P2`。