# bot3 optimization loop — 2026-04-12 16:14 UTC

## 执行小点
- target: `Rank 390 / passivbot EMA forager bounce`
- action: survivor 唯一一次 follow-up（`maker fill honesty haircut + slippage stress` 最小 decisive 检查）

## 本轮最小证据
数据源：`reports/artifacts/literature/passivbot_forager_alt_probe_2026-04-12_detail.csv`

对各 variant 统一复算 `net_ret = gross_ret - roundtrip_cost - tp_hit_penalty`：
1. `stress_12bps`（roundtrip 成本 12bps）
2. `stress_16bps`（roundtrip 成本 16bps）
3. `haircut_tp25_+6bps`（12bps + 每笔 TP 额外 6bps 成交惩罚）
4. `haircut_tp40_+8bps`（12bps + 每笔 TP 额外 8bps 成交惩罚）

关键结果（平均 bps/笔）：
- `alt4_balanced`: `-7.19 / -11.19 / -10.47 / -11.56`
- `alt4_extreme`: `+1.66 / -2.34 / -1.99 / -3.20`
- `alt4_extreme_top2vol`: `+7.90 / +3.90 / +3.55 / +2.10`

结论：只有 **`alt4_extreme_top2vol`** 在保守成交惩罚下仍保持成本后正边际；其余口径在 honesty haircut 后转负。

## 结论（会改变系统认知）
`Rank 390` 的 survivor follow-up 已收口：该策略并非广义可行，但在明确可执行窄域（`volatile-alt + deep stretch + top2 vol gating`）下经最小成交诚实压力后仍保留正边际，满足 `promote_P2` 条件；唯一可接受作用域同步收窄为 `extreme_top2vol`，后续需在 P2 立即做一次出口决策。

## 运行态落库
- 层级迁移：`Surviving candidate -> Active P2`
- survivor follow-up budget：`1 -> 0（已用尽）`
- Active P2 current target：`Rank 390`
- P2 入口约束：仅保留 `extreme_top2vol` 作用域，禁止回到宽口径 alt4/balanced 叙事
