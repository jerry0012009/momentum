# 2026-04-14 05:40 UTC — Rank 403 fresh intake first verdict（top-half-liquidity XS loser-bounce shell）

## 本轮执行小点
- `cycle_plan` 第 3 项（首个 pending）：
  - target: `research/quant_digests/2026-04-13_1428_tophalf-liquidity-xs-loserbounce-shell.md`
  - action: fresh intake first-verdict + 1 条最小 honesty/execution realism 检查

## 最小证据（仅为本小点）
1. 现成 digest 与 probe 结果显示：
   - 15m/5m 下该壳体 gross 仍有正值，但 taker 成本后（4~8bps）净值转负，换手压力显著。
   - 参考：
     - `research/quant_digests/2026-04-13_1428_tophalf-liquidity-xs-loserbounce-shell.md`
     - `reports/artifacts/quant_digests/xs_liquidity_reversal_probe_summary_2026-04-13.json`
2. 最小 honesty 检查（execution realism / lookahead）：
   - `reversal_score = -(rets.rolling(H).sum())`，信号来自历史滚动窗；
   - 回测执行使用 `w_lag = w.shift(1)`（1-bar lag）后与当期收益相乘，避免同窗持仓-收益对齐前视；
   - 参考源码：`https://raw.githubusercontent.com/Jamestilfords/statarb-crypto/main/src/crypto_statarb.py`。

## 本轮结论（改变系统认知）
- 该对象不具备直接升级 `P2/P3` 的净后条件（taker 口径被成本压穿），但作为完整 raw alpha 壳仍具继续价值，且未见决定性同窗前视问题；
- 因此 fresh intake first verdict 收口为：`keep_P1`；并分配正式编号：`Rank 403`。

## 槽位/状态回写
- Fresh intake slot 更新为当前对象并标记 `done`。
- Surviving candidate slot 由 `none` 更新为：`Rank 403`，`followup_budget_remaining = 1`。
- 唯一 survivor follow-up blocker：
  - 在更宽横截面（30~50 liquid alts）下验证“降频（2/3/4-bar rebalance）能否在保留 gross 的同时显著降 turnover 并实现净后可行”。

## cycle_plan 小点回写
- 第 3 项：`status = done`
- 第 3 项 `result` 已写入 state：`Rank 403 keep_P1` + 唯一 blocker。