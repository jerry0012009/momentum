# 2026-04-10 16:07 UTC · Rank 377 fresh intake first verdict（liquid staking basis mean reversion）

## 执行动作
- 对象：`research/quant_digests/2026-04-10_1422_liquid-staking-basis-meanreversion-alpha.md`
- 任务类型：fresh intake frozen-spec first verdict（distinctness + post-cost/execution realism）

## 关键检查
1. **Family distinctness（是否仅是既有 funding/basis carry 改写）**
   - 既有家族（如 `basis-funding gap convergence`、`synthetic futures carry substitution`）主要是 **perp/futures carry leg 之间的年化差值收敛**。
   - 本对象信号是 **现货对 `WBETHETH` 单 pair 的 rolling z-score 偏离回归**，不依赖 funding leg、到期结构或跨 venue carry 定价。
   - 结论：属于 `liquid-staking basis single-pair MR`，与既有 funding/basis carry 家族 **可区分**，不是同义改写。

2. **Post-cost + execution realism（15m 主口径）**
   - 依据 artifact：`reports/artifacts/literature/liquid_staking_basis_probe_summary_2026-04-10.csv`
   - 关键壳：`15m, entry |z|>=3, max_hold=32`
     - trades=`100`，gross mean=`+5.0078 bps/笔`，win_rate=`86%`
     - net（round-trip）
       - `4 bps`：`+1.0078 bps/笔`（仍为正）
       - `8 bps`：`-2.9922 bps/笔`（转负）
   - execution realism 结论：该 alpha 对摩擦敏感，只有在可实现成本接近 `<=4 bps rt`（偏 maker/被动成交）时才保留净边际；若落入偏 taker 的 `8 bps rt` 场景则失效。

## 本轮 verdict
- 分配新 rank：**Rank 377**（next unused integer）。
- fresh intake first verdict：**`keep_P1`**。
- 一句话结论：`Rank 377` distinctness 审计通过，且在 `15m |z|>=3` 壳下对 `4 bps rt` 仍有正净边际；但对高摩擦高度敏感，后续 survivor 唯一 follow-up 应锁定为成交实现度/容量约束。

## 对 runtime 的直接影响
- `Fresh intake slot` 更新为 `Rank 377 keep_P1`。
- `Surviving candidate slot` 由 `none` 切换为 `Rank 377`，follow-up budget 置为 `1`。
- `cycle_plan` 第 2 小点标记为 `done` 并写入可改变系统认知的结果句。