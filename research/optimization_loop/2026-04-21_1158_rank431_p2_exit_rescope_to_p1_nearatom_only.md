# Rank 431 / cointegration maker-first + hard time-stop pairs — P2 exit：one-time P2->P1 re-scope（NEAR-ATOM only）

- 时间：2026-04-21 11:58 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：1
- target: `Rank 431 / cointegration maker-first + hard time-stop pairs`

## 本轮只执行的动作
按当前 `cycle_plan` 的出口决策要求，只围绕已收敛出的唯一 blocker `cross-pair durability` 做最后收口，并补 1 个最小 honesty / execution realism 子检查：
- 用现成 `rank431_survivor_followup_proxy_trades_2026-04-21.csv` 做 `recent month slice (2026-04)` + `8/12/16bps` 成本梯度复核；
- 再加 1 个最小 `pair turnover / overlap realism` 检查：如果多 pair 交易高度重叠，确认在单仓位/不重叠执行下是否还能保留两个可执行 pair pocket。

## 使用证据
- `reports/artifacts/quant_digests/rank431_survivor_followup_proxy_summary_2026-04-21.csv`
- `reports/artifacts/quant_digests/rank431_survivor_followup_proxy_trades_2026-04-21.csv`
- `reports/artifacts/quant_digests/rank431_p2_exit_recentmonth_overlap_summary_2026-04-21.csv`
- `reports/artifacts/quant_digests/rank431_p2_exit_oneposition_summary_2026-04-21.csv`
- 上一轮 admission 结论：`research/optimization_loop/2026-04-21_1148_rank431_p2_admission_round1_keep_p2_single_durable_pair_blocker.md`

## 关键结果
### A) recent month slice + 成本梯度
`rank431_p2_exit_recentmonth_overlap_summary_2026-04-21.csv` 显示，当前 recent `2026-04` 全样本下：
- `NEARUSDT-ATOMUSDT`：`net_mean_8/12/16 ≈ +60.45 / +56.45 / +52.45bps`，三档同向为正；
- `AVAXUSDT-SUIUSDT`：`net_mean_8/12/16 ≈ +7.94 / +3.94 / -0.06bps`，到 `16bps` 已失守；
- 其余 pair 在 `8bps` 起就已不再保留正 net。

=> 在“至少两对 recent pair 同时通过 `8/12/16bps` 梯度”的口径下，并没有闭合成双-pair durable admission，主宿主仍只有 `NEAR-ATOM`。

### B) pair turnover / overlap realism（本轮唯一 honesty 子检查）
- 五个主要 pair 的 `any_overlap_frac` 基本都在 `0.95~1.00`；也就是几乎每一笔都会与其他 pair 的持仓窗口重叠，不能把它们直接当作独立并行 sleeve 线性相加。
- 进一步做最小单仓位 greedy 去重后，保留下来的 `AVAX-SUI` 子集在 `16bps` 仍可为正，但这并没有推翻上轮已经收敛出的决定性事实：它在完整 recent 月份样本与日度集中压力下仍是脆弱次优对，而不是稳定第二宿主。

=> overlap realism 说明“多 pair 同时堆叠的广谱性”没有想象中强；即使做最乐观单仓位去重，也不足以把 `AVAX-SUI` 从“脆弱次优对”升级成可与 `NEAR-ATOM` 并列的第二 durable pair。

### C) 与上一轮 blocker 合并后的最终判断
上一轮已经确认：
- `AVAX-SUI` 去掉 top3 贡献日后，剩余样本 `net8 ≈ -17.89bps`；
- `NEAR-ATOM` 去掉 top3 贡献日后，剩余样本 `net8 ≈ +22.86bps`。

把这个结论与本轮 `recent month + overlap realism` 合并后，系统当前能诚实落下的 runtime truth 是：
- `Rank 431` 不是“至少两对 durable pair 已闭合、足以直接进 P3”的 pair basket；
- 但它也不是完全失效，因为 `NEAR-ATOM` 已经形成唯一明确、可执行、可单独复核的新 spec。

## 出口决策
`one-time P2->P1 re-scope`，明确收窄为：
- **`NEAR-ATOM only`**
- 保留 `rolling admission + maker-first + hard time-stop`
- 不再宣称是多-pair basket alpha

## 为什么不是 promote_P3
`promote_P3` 需要至少两对 recent pair 在统一成本梯度与最小 execution realism 下都能诚实保住 durable pocket；当前只有 `NEAR-ATOM` 满足，第二对并未闭合。

## 为什么不是直接 background/P0
policy 允许 `P2->P1` 仅在存在唯一明确 re-scope 方向时发生；当前确实存在，而且方向唯一：从“multi-pair basket”收窄成“`NEAR-ATOM only` 单对 spread-fade sleeve”。因此本轮不直接丢回 `P0`，而执行一次性明确 `P2->P1 re-scope`。

## runtime 写回
- `Active P2 slot.current_target -> none`
- `Active P2 latest_result` 更新为 `one-time P2->P1 re-scope (NEAR-ATOM only)`
- `cycle_plan` item1：`status -> done`
- `cycle_plan` item1.result：写成 rescope 结论
- `Background pool.latest_parked` 追加：`Rank 431` 已按槽位约束移入 background，等待后续仅按 `NEAR-ATOM only` 新 spec 人工/后续 fresh reopen

## 一句话结果（写回 state）
`Rank 431 / cointegration maker-first + hard time-stop pairs` 的 P2 出口决策已完成：recent month + `8/12/16bps` 梯度与 pair-overlap realism 合并上一轮日度集中检查后，只有 `NEAR-ATOM` 仍是 durable host、第二对未闭合，因此本轮不升 `P3`，执行一次性 `P2->P1 re-scope` 为 `NEAR-ATOM only`，并按槽位约束移入 background 等待按新 spec 重新 fresh intake。

## 尾部执行状态（非阻断）
- homepage publish：待本轮尾部命令执行。
- 邮件通知：待本轮尾部命令执行。
