# 2026-04-12 21:07 UTC — Rank 74 survivor follow-up（样本厚度 + execution realism）

## 执行小点
- 来自 `cycle_plan` 第 1 项：
  - target: `Rank 74 / Fib-family-local ER-only veto-admission residual`
  - action: survivor 唯一一次 follow-up（时间分段稳定性 + 交易密度下限 + 信号到可成交时点对齐）

## 本轮最小核验实现
- 数据源：`reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/*feature_frame.csv` + `signals_*_fib_retest_long_er_only.csv`
- 口径固定：`BTC/ETH/SOL`，`entry=open(t+1)`，`exit=open(t+1+8)`，`8bps round-trip`
- 产物：
  - `reports/artifacts/rank74_survivor_followup_trade_log_20260412_2107.csv`
  - `reports/artifacts/rank74_survivor_followup_summary_20260412_2107.csv`

## 结果
1. **execution realism（signal -> tradable）通过**：9/9 笔均满足 `entry_idx = signal_idx + 1`，且 `signal_to_trade_min = 15` 分钟，无 delayed-confirmation 美化。
2. **时间分段稳定性不足**：按样本期等分 3 个窗口后，窗口净收益为 `W1 +3.05%`、`W2 -0.27%`、`W3 +3.62%`，中段已转负。
3. **样本厚度未过下限**：总计仅 9 笔（BTC 3 / ETH 4 / SOL 2），且 `W1/W2` 各只有 2 笔；该边际仍主要依赖稀薄样本，不足以支撑 `promote_P2`。

## 本轮结论（必须二选一收口）
- verdict: **`drop_to_background`**
- 单一 decisive blocker: **交易密度过低导致分段稳定性不可验证（低样本驱动）**。
- 因已用完 survivor 唯一 follow-up 且未达 admission 强度，`Rank 74` 不再保留前排槽位。
