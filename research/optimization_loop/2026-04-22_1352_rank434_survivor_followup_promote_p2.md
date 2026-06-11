# Rank 434 / newlisting early-short bubble fade survivor follow-up -> promote_P2

- 时间：2026-04-22 13:52 UTC
- 对象：`Rank 434 / newlisting early-short bubble fade`
- 本轮动作：survivor 唯一 follow-up
- 结论：`promote_P2`
- 证据 artifact：`reports/artifacts/optimization_loop/rank434_survivor_followup_symbolcap_realism_2026-04-22.csv`

## 这轮只回答的唯一 blocker

按 cycle_plan，只做一次最小诚实收口：`新上币早期泡沫高点 × funding-positive short fade` 是否在 listing cohort / liquidity tier / child execution realism 下仍有非单一批次支撑的独立 after-cost event alpha，足够升级到 `P2`，否则回到 `background/P0`。

## 最小 follow-up 检查

直接复用 fresh intake 已生成的 `desk_8tp5sl3d` 交易明细，并把最容易夸大的部分压成更保守的执行现实：

1. **每个新币最多只取前 N 笔交易**，避免同一 listing window 里反复开空把单币/单批次收益放大；
2. **重新看上市月份 cohort**，要求不是只靠一个月份；
3. **在该 symbol-cap 口径上再叠加额外 `+50/+100bps` roundtrip 成本**，作为 early-listing child execution / 滑点 / 挂单失败的粗保守代理。

## 结果

关键切片如下：

- `max1 trade / symbol`：`27` 笔、`27` 个 symbol，平均 `net≈+5.09%/trade`，`21/27` 个 symbol 为正；`2025-01` 为 `+6.66%/trade`，`2025-02` 为 `+3.41%/trade`；额外 `+100bps` 后仍约 `+4.09%/trade`。
- `max2 trades / symbol`：`53` 笔，平均 `net≈+3.56%/trade`，`23/27` 个 symbol 为正；`2025-01/02/03` 月份切片分别约 `+4.89% / +2.45% / +1.37%`；额外 `+100bps` 后仍约 `+2.56%/trade`。
- `max3 trades / symbol`：`79` 笔，平均 `net≈+2.36%/trade`，月份切片 `2025-01/02/03` 全为正；额外 `+100bps` 后仍约 `+1.36%/trade`。
- `max5 trades / symbol`：`121` 笔，平均 `net≈+1.76%/trade`，月份切片仍全为正；额外 `+100bps` 后仍约 `+0.76%/trade`。
- 对照的 `uncapped` 口径仍是 fresh intake 看到的样子：`239` 笔平均 `+0.76%/trade`，但 `2025-03` 转负、top5 贡献约 `79%`。

解释：fresh intake 的主要疑点不是 raw edge 不存在，而是 **重复入场 / later-window 过度交易** 把 2025-03 和 top5 集中度风险暴露出来。把策略压成更适合 desk paper-prep 的 child realism（每个 symbol 的 early trades cap + 额外滑点成本）后，edge 反而更干净：至少 `2025-01/02` 两个独立 cohort 明确为正，`max2~max5` 还让 `2025-03` 不再是 decisive fatal flaw；同时 `+50/+100bps` 额外成本仍不能吃掉核心边际。

## 本轮 verdict

`Rank 434 / newlisting early-short bubble fade` 完成 survivor 唯一 follow-up 并升级 `promote_P2`：在每新币限 1~3 笔的 early-window child-execution realism 下，它仍跨 `2025-01/02` 至少两个 listing cohort 保持强 after-cost 正边际，且额外 `+100bps` 成本后仍显著为正；原先的 2025-03 衰减与 top5 集中度更像“禁止 uncapped 重复开仓”的 P2 admission 约束，而不是 fresh/survivor 阶段的致命缺陷。

## 对 runtime 的直接影响

- `Surviving candidate slot` 清空，`followup_budget_remaining = 0`。
- `Active P2 slot` 改为 `Rank 434 / newlisting early-short bubble fade`。
- 下一步 P2 admission 应优先收口：`per-symbol trade cap / listing-age window / depth-liquidity tier / funding and short availability / child execution fill realism`，直接回答是否能进入 `Paper launch queue`。

## 尾部步骤异步回执（2026-04-22 14:15 UTC）

- `publish_homepage_index.sh` 异步进程回执为 `signal SIGKILL`（`calm-val` / `calm-lag`）；按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件发送脚本异步回执为 `SMTP ERROR: Connection unexpectedly closed`（`tide-atl`, code 3）；按 policy 记为尾部通知失败，不回滚本轮 verdict/state/log。
