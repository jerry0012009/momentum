# Rank 248 / dynamic-coint spread forecast × percentile trigger × PIW gate：survivor follow-up 后回到 background/P0

- 时间：2026-03-30 07:34 UTC
- 对象：`Rank 248 / dynamic-coint spread forecast × percentile trigger × PIW gate`
- 轮次类型：bot3 auto optimization
- 结论：`survivor follow-up failed -> background/P0`

## 这轮做了什么
按当前 `cycle_plan` 执行唯一合法的 survivor follow-up：在同一批 liquid majors pair（`BTC/ETH`、`ETH/SOL`、`BTC/SOL`）、同一 `15m` 主时钟、同一 rolling spread normalization / after-cost 假设下，正面对照三版：

1. `plain current z-score threshold`
2. `forecast-score percentile trigger`
3. `forecast-score percentile trigger + PIW width veto`

这轮的目标不是证明深度学习模型名有多高级，而是只回答两件事：
- `forecast timing` 是否比裸 `z-score` 留下独立净增益；
- `PIW uncertainty gate` 是否在此基础上再留下独立净增益。

## 最小实现口径（诚实版）
- 数据：复用本地已有 `reports/artifacts/scout_tau_band_breakout_15m/cache/` 中的 `BTCUSDT/ETHUSDT/SOLUSDT 120d 15m` 缓存。
- pair：`BTCUSDT/ETHUSDT`、`ETHUSDT/SOLUSDT`、`BTCUSDT/SOLUSDT`。
- spread：rolling `96-bar` beta 下的 log-price residual spread。
- baseline：`plain_z` 用 prior-bar `z-score` 超过 `±2.0` 开仓，回到 `±0.25` 内平仓，`max_hold=16 bars`。
- forecast layer：用 rolling AR(1)-style `Δz = α + φ z_{t-1}` 生成 next-step forecast，把 forecast 绝对值是否突破 rolling `90%` 分位作为入场条件。
- PIW gate：用 rolling residual std 构造 `PIW proxy`，只保留宽度落在 rolling `70%` 分位以内的信号。
- 执行：全部使用 prior-bar signal、next-bar open 执行；单边 `6bps`、双腿 roundtrip `24bps`。

## 结果
### 分 pair 对照
| pair | plain_z 累计净收益 | forecast_q 累计净收益 | forecast_q_piw 累计净收益 |
|---|---:|---:|---:|
| BTC/ETH | -16.99% | -11.35% | -5.61% |
| ETH/SOL | -17.97% | -17.77% | -13.28% |
| BTC/SOL | -11.14% | -8.70% | -2.84% |

### 总结
- `plain_z`：3/3 pairs 全负，累计净收益和约 `-46.10%`。
- `forecast_q`：3/3 pairs 仍全负，累计净收益和约 `-37.83%`。
- `forecast_q_piw`：3/3 pairs 仍全负，累计净收益和约 `-21.73%`。
- `PIW gate` 的确让损失变浅、交易数下降（206 -> 160 -> 102），但没有把任何 pair 拉到成本后为正。
- 最好的 pair 仍只是 `BTC/SOL`，在 `forecast_q_piw` 下也只有 `-2.84%`，没有形成可说服的 surviving positive pocket。

## 本轮判断
结论不是 `promote_P2`。

原因：
1. **forecast timing 有“减亏”但没有“转正”。** `forecast_q` 相比 `plain_z` 在两组 pair 上确实让亏损收浅，但 3/3 pairs 仍全部为负，说明当前看到的主要是弱过滤效果，而不是足以支撑前排升级的独立净增益。
2. **PIW gate 也只是继续减亏，不是 decisive blocker 的解决。** 加上 `PIW` 后最差 pocket 被压浅，交易数也明显减少，但仍没留下任何成本后正收益 pair；这更像“少做一点就少亏一点”，还不够构成独立 alpha 组件通过证伪。
3. **唯一 survivor follow-up 已经用完。** policy 下，这条对象现在必须收口，而不是继续拖去补模型、调阈值、扩 pair 或换时钟。

## 会改变系统认知的话
`Rank 248 / dynamic-coint spread forecast × percentile trigger × PIW gate` 的 forecast timing 与 PIW uncertainty gate 在同口径下都只表现为“减亏但不转正”；3 组 liquid majors pair 在 after-cost 下仍然全部为负，因此这条 survivor follow-up 不支持升 `P2`，应当用完唯一 follow-up 后回到 `background/P0`。

## 产物
- `reports/artifacts/rank248_dynamic_coint_followup/variant_summary.csv`
- `reports/artifacts/rank248_dynamic_coint_followup/pair_compare_pivot.csv`
- `reports/artifacts/rank248_dynamic_coint_followup/overall_compare.csv`
- `reports/artifacts/rank248_dynamic_coint_followup/trade_log.csv`
