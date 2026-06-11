# Rank 431 / cointegration maker-first + hard time-stop pairs — P2 admission 出口决策次轮 -> promote_P3

- 时间：2026-04-21 13:06 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：1
- target: `Rank 431 / cointegration maker-first + hard time-stop pairs`

## 本轮只执行的动作
按 state 中 item1 的要求，仅做最后决策检查：围绕唯一 blocker `cross-pair durability`，在 recent slice + 成本梯度 + pair overlap realism 下回答是否仍有至少两对同向 after-cost pocket，并据此直接给出 `promote_P3 / P2->P1 / background` 三选一出口。

## 使用证据
- `reports/artifacts/quant_digests/rank431_survivor_followup_proxy_trades_2026-04-21.csv`
- 本轮最小补充汇总：`reports/artifacts/quant_digests/rank431_p2_exit_round2_recent7d_crosspair_realism_2026-04-21.csv`

## 最小检查结果（会改变层级）
以最近 7 天切片（`2026-04-14 05:30` 到 `2026-04-21 05:30` UTC）统计：

- `AVAXUSDT-SUIUSDT`：`trades=13`，`net_mean_8/12/16 ≈ +32.19/+28.19/+24.19 bps`
- `NEARUSDT-ATOMUSDT`：`trades=11`，`net_mean_8/12/16 ≈ +19.63/+15.63/+11.63 bps`

两对都在统一 `8/12/16bps` 梯度下同向为正，且不是只在单一 pair 上成立。

### honesty / execution realism（本轮唯一子检查）
做最小 pair overlap realism：统计两对同时在场重叠占比。
- `AVAX-SUI` 的 13 笔中有 10 笔与 `NEAR-ATOM` 时间重叠（overlap ratio ≈ `76.9%`）。
- 这反映的是并行持仓现实（资金分配问题），但两对不共享同一资产腿，未构成“单一 pair 幻觉”或“同资产重复暴露伪分散”。

## 出口结论
`promote_P3`。

原因：按本轮 success_criterion，recent slice 下已经重新满足“至少两对通过成本梯度并同向为正”；且最小 overlap realism 未揭示单一 decisive blocker，因此不再保留在 P2。

## runtime 写回要点
- `Active P2 slot`: `Rank 431` 退出（完成 admission 出口）
- `Paper launch queue`: 新增 `current_target = Rank 431 / cointegration maker-first + hard time-stop pairs`（进入 handoff/launch wiring 队列）
- `cycle_plan` item1: `status=done`，`result` 写为本轮已直接 `promote_P3`

## 一句话结果（写回 state）
`Rank 431` 的 P2 出口次轮已收口：在 recent 7d + 统一 `8/12/16bps` + 最小 overlap realism 下，`AVAX-SUI` 与 `NEAR-ATOM` 均保留同向 after-cost 边际，`cross-pair durability` blocker 解除，因此本轮直接 `promote_P3` 并进入 `Paper launch queue`。