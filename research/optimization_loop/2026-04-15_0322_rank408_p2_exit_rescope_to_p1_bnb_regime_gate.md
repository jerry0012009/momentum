# Rank 408｜P2 admission 出口决策：one-time P2->P1 re-scope（BNB-only + session/regime gate）
- 时间：2026-04-15 03:22 UTC
- 执行对象：`Rank 408 / BB expansion breakout × pullback reversal continuation shell`
- cycle_plan 小点：#1（P2 admission 出口决策轮）

## 本轮执行
仅执行当前前排 pending 小点：在既有 `BTC+BNB` 通过域上补齐 `effectiveness / cross-asset / time / parameter` 四轴最小验证，并补 1 个最小 honesty 子检查（BB expansion + pullback 触发是否存在 lookahead / 收盘后确认泄漏）。

数据源：
- `reports/artifacts/quant_digests/bbexpansion_pullback_probe_trades_2026-04-14.csv`

本轮新增产物：
- `reports/artifacts/optimization_loop/rank408_p2_admission_cost_time_crossasset_2026-04-15.csv`
- `reports/artifacts/optimization_loop/rank408_p2_admission_honesty_2026-04-15.csv`
- `reports/artifacts/optimization_loop/rank408_p2_admission_monthly_2026-04-15.csv`

## 结果（四轴 + honesty）
### 1) effectiveness（费后均值）
- `BTC+BNB`：
  - 4 bps：`avg_net_bps = +5.54`
  - 6 bps：`avg_net_bps = +3.54`
  - 8 bps：`avg_net_bps = +1.54`
- 结论：有效性在 4/6/8 bps 下仍为正，但边际并不厚。

### 2) cross-asset stability
- `BNBUSDT`：4/6/8 bps 均为正（`+8.83/+6.83/+4.83`）
- `BTCUSDT`：4/6 bps 为正（`+3.44/+1.44`），8 bps 转负（`-0.56`）
- 结论：跨资产并非一致稳健，更像 BNB 主导 pocket。

### 3) time stability
- 周度：`BTC+BNB` 在 4/6/8 bps 的 `positive_week_ratio` 都是 `0.625`（16 周中 10 周为正）
- 月度（6 bps）：
  - 2026-01：`avg_net_bps = -7.70`
  - 2026-02：`avg_net_bps = +22.80`
  - 2026-03：`avg_net_bps = +9.63`
  - 2026-04：`avg_net_bps = -10.73`
- 结论：存在明显双月负漂移，时间稳定性不足以直接进入 paper launch。

### 4) parameter stability（最小成本参数轴）
- 在统一执行映射下把 roundtrip friction 从 4 -> 6 -> 8 bps 推进，组合均值保持正但快速衰减，`BTC` 子腿在 8 bps 已失效。
- 结论：参数轴只显示“有限韧性”，未达到可直接接线 P3 的稳健阈值。

### 5) honesty / execution realism（最小 blocker 检查）
- `setup->entry`：`min=max=5m`，`strict_next_bar_ratio=1.0`
- `non_positive_lag_count=0`
- `setup_not_5min_aligned_count=0`，`entry_not_5min_aligned_count=0`
- `exit_before_entry_count=0`
- 结论：未发现 lookahead、收盘后确认泄漏或不可成交映射；本轮不存在 decisive honesty blocker。

## 出口判定
- `promote_P3`：否（time stability 未过）
- `drop_to_background/P0`：否（仍保留可收敛 pocket）
- **`one-time P2->P1 re-scope`：是**

唯一明确 re-scope 方向：
- 将对象从 `BTC+BNB` admission 壳收敛为 **`BNB-only + session/regime gate`**，优先过滤掉已显著负漂移时段，再重开 P1 级单次验证。

## 一句话结论（写回 runtime）
`Rank 408` 在 honesty 维度未见泄漏，但 admission 时间稳定性不足以直升 P3；本轮按出口规则收口为 one-time `P2->P1 re-scope`，限定到 `BNB-only + session/regime gate`。