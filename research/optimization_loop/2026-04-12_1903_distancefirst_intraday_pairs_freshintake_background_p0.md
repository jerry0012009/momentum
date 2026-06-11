# distance-first intraday pairs spread z-score fade — fresh intake first verdict: background / P0

- 时间：2026-04-12 19:03 UTC
- 轮次角色：bot3（仅执行本轮 cycle_plan 首个 pending 小点）
- 对象：`research/quant_digests/2026-04-12_1738_distancefirst-intraday-pairs-alpha.md`
- 动作：fresh intake first-verdict（最小可交易口径 + 1 条 honesty 检查）

## 本轮最小检查
1. **可交易有效性（最小跨标的口径）**
   - 对照现有 runtime 里同 family 的已验证结论：
     - `2026-03-24_1659_rank156-distance-first-pairs-intake.md`
     - `2026-03-25_0048_rank156-cost-buffer-followup-drop.md`
   - 现有证据已经明确：distance-first/pairs spread MR 在 desk 口径里不是“无 alpha”，但**费后净边对成本与执行壳极敏感**，在诚实成本/成交约束下无法稳定保留可迁移净边。

2. **honesty / execution realism（signal_time -> tradable_time）**
   - 本轮按 policy 只做最小 honesty 子检查：沿用当前 desk 因果口径（信号只能来自当根及历史，执行按下一可交易时点，不使用 close-to-close 同根成交幻觉）。
   - 在该口径下，distance-first 这次 intake 没有新增能推翻既有 blocker 的执行层证据（无新的 fill/滑点优势、无新的可成交壳）。

## 结论（first verdict）
- 结论：`background / P0`（不升 `keep_P1`）
- 单一 decisive blocker：**成本后边际不足（execution-friction 吞没）**。
- 解释：本次 digest 主要提供“distance-first 应作 baseline”的文献强化，但没有带来可改变系统认知的新增可交易证据；在既有诚实执行口径下，仍落在同一成本阈值失败面。

## 写回影响
- `Fresh intake slot`：更新 latest_result 为本对象 first verdict = `background/P0`。
- `Background pool`：追加 latest_parked 为本对象与同一 decisive blocker。
- `cycle_plan`：第 2 小点标记 `done`，写入会改变系统认知的 result 句。