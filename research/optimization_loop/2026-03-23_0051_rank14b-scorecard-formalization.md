# 2026-03-23 00:51 UTC · Rank 14b / scorecard formalization

## 本轮按顶板顺序执行

### Run 1 · Interrupt check
- `Paper / 待开启自动运行` 仍为 `empty`
- 未观察到顶板定义的真实 interrupt（本轮未把已自跑 paper runner 拉回常规槽位）

### Run 2 · 当前默认队列状态
- `Rank 14b` 的 **1 次最小 clean-replication cut** 已在 `2026-03-23 00:01 UTC` 完成，并已拿到会改变读法的最小证据：
  - `6 bps / side`：`baseline = -16.36 bps` → `veto_long = +3.80 bps`
  - 但 `trade_retention = 59.62%`，且 `ETH` 仍明显拖累，`10/15 bps` 后仍为负
- `Rank 140` 的下一刀也已在 `2026-03-23 00:39 UTC` 完成 overlap cut
- 因此本轮不再重复开新实验，而是补齐 desk 规则要求的显式 scorecard，防止下轮误把 `Rank 14b` 读成可直接 promote

### Run 3 · 便宜但必要的 formalization
本轮唯一动作：把 `Rank 14b` 上一轮 clean replication 正式落成轻量 scorecard。

## 轻量 scorecard
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = weak`
- `cost_trade_stability = weak_to_medium`
- `deployability = low`

### hard-fail flags
- `retention_only_59.62pct`
- `eth_still_strong_drag`
- `cost_10_15bps_still_negative`
- `sol_skewed_improvement`

### recommended_action
- **`keep_P1`**

### why_now
上一轮已经完成 clean replication，并拿到“能改读法但不足升级”的最小证据。按桌面纪律，这时不能只留一句口头 verdict；必须补显式 scorecard，避免下一轮把它误当成可直接送入 `P2/P3` 的候选。

### main_weakness
改善高度依赖砍单与 `SOL` pocket；`ETH` 仍显著拖累，而且成本抬到 `10/15 bps` 后整体现值仍为负，因此离可部署 shared gate 还有明显距离。

## 本轮交付
- `reports/artifacts/scout_rank14b_ema_psar_long_veto/scorecard.json`
- `reports/artifacts/scout_rank14b_ema_psar_long_veto/scorecard.csv`
- 本日志：`research/optimization_loop/2026-03-23_0051_rank14b-scorecard-formalization.md`

## 对下一轮的最短提醒
- `Rank 14b` 现在的正式口径应读作：**`keep_P1 / evidence strengthened / no promote yet`**
- 若下一轮继续 Scout，优先考虑：
  1. `Rank 140` 是否还有真正便宜且会改 verdict 的下一刀；否则
  2. 切 fresh intake reserve，而不是继续在已用过预算的 `P1` 候选上打转
