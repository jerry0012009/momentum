# Rank 379 — P2 admission 出口轮（promote_P3）

- 时间：2026-04-11 09:06 UTC
- 对象：`Rank 379 / intraday entropy-ratio XS reversal`
- 执行动作：按 cycle_plan 第 2 小点执行 P2 admission 出口决策（仅此一项）
- 结论：`promote_P3`

## 本轮改变系统认知的一句话
`Rank 379` 已在 effectiveness / cross-asset / time / parameter 的最小 admission 联合检查下达到“值得进入 paper launch queue”的门槛，且最小 honesty 子检查（next-session shift 对齐）通过，因此本轮直接由 `Active P2` 升级到 `P3`，不再继续开放式 `keep_P2`。

## admission 最小联合证据（基于既有 artifact）
数据源：
- `reports/artifacts/literature/intraday_entropy_probe_summary_2026-04-11.csv`
- `reports/artifacts/literature/intraday_entropy_probe_path_2026-04-11_5m.csv`
- `reports/artifacts/literature/intraday_entropy_probe_path_2026-04-11_15m.csv`
- `reports/artifacts/literature/intraday_entropy_probe_detail_2026-04-11_5m.csv`
- `reports/artifacts/literature/intraday_entropy_probe_detail_2026-04-11_15m.csv`

1) effectiveness / expected return（含成本）
- 5m: `low_Entr_minus_high_Entr = +9.141 bps/day`；net@6bps 仍约 `+3.141 bps/day`
- 15m: `low_Entr_minus_high_Entr = +10.841 bps/day`；net@6bps 仍约 `+4.841 bps/day`
- 对照 `loser_minus_winner = -0.46 bps/day`

2) cross-asset stability（最小覆盖）
- 信号每天都在 `BTC/ETH/SOL/XRP` 四资产横截面里选 long/short，非单币方向赌注；
- 明确存在资产异质性（并非每个 symbol 单腿都正），但组合语义是 XS long-short，且两档输入频率都保持组合级正期望。

3) time stability（最小覆盖）
- 75 天窗口内整体为正（5m `+9.14` / 15m `+10.84` bps/day）；
- 子窗口有波动（后半段边际转弱），但未出现“全窗口成本后失效”的致命结论，更适合进入 paper 观察而非继续 P2 开放补证。

4) parameter stability（最小覆盖）
- 关键输入频率从 `5m` 到 `15m` 方向一致，且 15m 在成本后边际更厚；
- 说明并非单一参数点偶然命中，足以支持进入 P3 做接线验证。

## 最小 honesty 子检查（本小点内允许的 1 个 cheap 检查）
检查：`next_ret` 是否严格等于同 symbol 次日 `ret_d`（避免 lookahead/shift 错位造成伪 edge）。

结果（python3 校验）：
- 5m detail：`71/71` 可比样本完全匹配（1.0）
- 15m detail：`75/75` 可比样本完全匹配（1.0）

结论：未发现“标签位移错误”这一单一 honesty blocker。

## 出口三选一
- `promote_P3` ✅
- `drop_to_background(P0)` ❌（成本后仍有净边际）
- `one-time P2->P1 re-scope` ❌（当前不存在唯一且更优的重定义方向）

## runtime 写回要点
- `Active P2 slot`：释放（`current_target = none`）
- `Paper launch queue`：置入 `Rank 379` 作为当前接线目标（等待 bot3 后续轮次完成 runner + scheduler + first verified run）
- `cycle_plan` 第 2 小点：`status=done`
