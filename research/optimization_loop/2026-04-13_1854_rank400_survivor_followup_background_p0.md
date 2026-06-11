# Rank 400 survivor follow-up（唯一跟进）收口：background/P0

- 时间：2026-04-13 18:54 UTC
- 执行器：bot3
- 对象：`Rank 400 / short-half-life walk-forward pairs alpha (15m portability scoped)`
- 对应 cycle_plan 小点：#1（survivor 唯一 follow-up）

## 本轮执行
按 state 指令先做最小复核与 honesty 子检查，优先读取现有同批 artifact：

- `reports/artifacts/quant_digests/2026-04-13_crypto-stat-arb-15m-transfer/signal_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-13_crypto-stat-arb-15m-transfer/cost_ladder_summary.csv`
- `reports/artifacts/quant_digests/2026-04-13_crypto-stat-arb-15m-transfer/candidate_pairs.csv`
- `reports/artifacts/quant_digests/2026-04-13_crypto-stat-arb-15m-transfer/pair_scan_wide_30d.csv`

## 关键发现（会改变系统认知）
1. 成本后边际仍是“少数低摩擦 pocket”，不是可稳定外推的广谱存活：
   - `signal_probe_summary.csv` 仅 8 对信号样本；
   - `cost_ladder_summary.csv` 下 `8bps` 仅剩极少数组合微正，`12bps` 全灭（与 intake 首判一致）。
2. honesty/execution realism 出现新的可复刻性硬缺口：
   - `candidate_pairs.csv` 为空（0 行），但同批 `signal_probe_summary.csv` 仍有 8 对 pair 的结果；
   - 这意味着“候选准入对象 -> 信号输出对象”的链路在当前 artifact 集合内不可追溯复现，无法支撑本轮要求的滚动再准入可验证性（含 `4h/daily` 再准入触发审计）。

## 出口决策
- 结论：`Rank 400` 本轮 survivor 唯一 follow-up **不晋升 P2**，直接收口到 `background/P0`。
- 原因：
  - 费后边际仍偏“薄且窄”；
  - 同时出现 artifact 对象链路不一致（候选为空但信号非空）的 execution realism blocker，当前不满足 P2 所需的可复刻/可审计标准。

## 状态回写
- `Surviving candidate slot` -> `current_target: none`，`followup_budget_remaining: 0`
- `Background pool.latest_parked` 更新为 `Rank 400`
- `cycle_plan[1]` 写回 `status: done` + 本轮结果句

## 备注
- 本轮严格只执行 cycle_plan 首个 pending 小点，未重排其余小点。
- 后续若需重开该线，必须先补齐“候选准入对象与信号输出对象一一可追溯”的同源 artifact，再谈 P2。