# Rank 283 — survivor follow-up exit：drop_to_background / P0

- 时间：2026-04-01 16:33 UTC
- 对象：`Rank 283 / OU half-life wideband pairs`
- 类型：`survivor follow-up`
- policy 依据：`docs/BOT2_BOT3_POLICY.md`
- runtime 入口：`docs/BOT2_BOT3_STATE.md`

## 本轮为什么由 bot3 直接执行这一步

当前 runtime 里 `Surviving candidate slot` 仍挂着 `Rank 283` 且 `followup_budget_remaining = 1`，说明它仍然占有唯一合法的 survivor front slot；但当前 `cycle_plan` 已全部是 `done`，没有 pending 小点。按 policy，前排对象的诚实收口优先级高于新的 fresh intake，survivor 也只允许这 **1 次** decisive follow-up。

因此本轮不继续沿着“无 pending 但继续空转”的歪路径，而是直接执行这条唯一合法的 survivor 收口动作：回答 `Rank 283` 现在到底还能不能保留前排。

## 本轮直接回答的问题

> 在不新增未验证长样本实验的前提下，现有证据是否已经足够把 `OU optimal band / 2.0σ / 2.5σ / 3.0σ` 这条 pairs 线保留为 survivor，还是它其实只留下了一条 `half-life gate + wide-band admission` 的 threshold-governance insight？

## 本轮使用的证据

1. `research/quant_digests/2026-04-01_0428_ou-halflife-wideband-pairs-alpha.md`
2. `reports/artifacts/quant_digests/ou_optimal_band_pairs_20260401/summary_threshold_sweep.json`
3. `reports/artifacts/quant_digests/ou_optimal_band_pairs_20260401/threshold_sweep_summary_5m_6bps.csv`
4. `reports/artifacts/quant_digests/ou_optimal_band_pairs_20260401/cost_threshold_compare_5m.csv`
5. `research/optimization_loop/2026-04-01_1330_rank283_ou_halflife_wideband_pairs_keep_p1.md`

## 关键读数

### 1) 有价值的部分确实成立

在现有 `5m` quick check 里：

- `1.0σ`：mean return 约 `-0.51%`，positive pairs `14/28`，median trades `36`
- `2.0σ`：mean return 约 `+1.03%`，positive pairs `17/28`，median trades `18`
- `2.5σ`：mean return 约 `+1.46%`，positive pairs `18/28`，median trades `15`
- `3.0σ`：mean return 约 `+1.25%`，positive pairs `20/28`，median trades `9`

更高成本口径下：

- `10 bps one-way, 2.5σ`：mean return 约 `+1.08%`，positive pairs `16/28`
- `10 bps one-way, 3.0σ`：mean return 约 `+1.02%`，positive pairs `19/28`

这足以证明一件会改变系统认知的事：

> 对这条 pairs 线，`half-life gate + wider band` 不是数学装饰，而是真会改变是否被噪声交易与成本吃掉的 admission 纪律。

### 2) 但能成立的，目前只到这一步

当前证据仍明显不够支撑 survivor 继续占前排：

- 样本只覆盖约 `1500` 根 `5m` bar（约 `5.2` 天），离 `90d~365d` 差得很远；
- 还没有把 `major-only` 与 `broader liquid universe` 分开做同口径 survivor 判断；
- 还没有把 `pair availability / churn` 当成时间序列来验证，无法回答这条线是不是只靠少数短暂 pair 供给；
- 现在的成本/执行仍是简化 proxy，并未补齐更现实的 maker/taker、滑点、结构断裂 kill-switch；
- 目前最强的结论是“阈值治理有价值”，而不是“已有一个更长时间维度上能稳定供给的 after-cost pairs pocket”。

## 本轮 verdict

`Rank 283` 的唯一 survivor follow-up 已完成，结论是：

> 当前证据只够保留 `half-life gate × wide-band admission` 这条 threshold-governance insight，尚不足以证明在 `90d~365d`、`major-only / broader universe` 分层、以及 `pair availability churn` 与更现实 friction 下，仍能留下诚实的 after-cost survivor。

因此按 policy：

- **不升 `P2`**
- **用尽唯一 survivor follow-up**
- **直接退回 `background pool / P0`**

## 对系统状态的实际改写

- `Surviving candidate slot`：从 `Rank 283` 收口为 `none`
- `followup_budget_remaining`：从 `1` 变为 `0`
- `Background pool`：新增 `Rank 283 / OU half-life wideband pairs` 的收口记录
- 当前前排不再保留这条线，除非未来用户明确要求 reopen，或后续有新的长样本/供给证据把它重新带回前排

## 一句话 result（用于 state/cycle_plan）

`Rank 283` 的唯一 survivor follow-up 已确认：当前证据只够保留 `half-life gate × wide-band admission` 这条 threshold-governance insight，尚不足以证明 `90d~365d`、major-only/broader universe 与 pair-supply churn 下仍有诚实 after-cost survivor，因此不升 `P2`，直接退回 `background pool / P0`。
