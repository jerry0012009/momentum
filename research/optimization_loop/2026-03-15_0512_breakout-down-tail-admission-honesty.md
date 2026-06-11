# 2026-03-15 05:12 UTC — breakout down-tail admission honesty

## 本轮主点
- **主点：`support_breakout_v0` 的 deployment/admission 收口**
- 聚焦把 `one_more_gate` 的 blocker 从“泛化担忧”压成可执行的 honesty 事实：
  - 默认 `ETH+SOL pair-conditioned halfsize` 受影响小时约 `44`
  - `up / flat / down+flat` ≈ `28 / 14 / 2`
  - pure `down` 仍为 `0`
- 结论：当前改善主要覆盖 `up/flat` pocket，**尚未真正触达 down-tail**，因此仍应停在 `shadow-admission queue / one_more_gate`。

## 产出（deployment-facing）
1. 更新 `reports/site/factors/support_breakout_v0_h24/report.html`
   - 新增一段明确的 down-tail honesty 小节（放在 walk-forward 之后、admission verdict 之前）。
   - admission 主缺口与问答表同步补充 `pure down = 0` 的硬证据语句。
2. 更新 `reports/site/factors/alpha_closure_board/report.html`
   - breakout 行的 `not yet` 与 `next` 同步加入 down-tail 证据与下一刀方向（`down tail honesty`）。
3. 更新 `docs/TODO.md`
   - 在已完成的 breakout admission 条目下补充 2026-03-15 最新证据说明（44 小时分布 + pure down=0）。
4. 更新 `reports/site/plans/momentum_todo.html`
   - 同步上述 TODO 最新补充，保持网页入口与源码 TODO 口径一致。

## 最小验证
- 对以上 4 个文件做关键短语检查，确认均已出现：
  - `受影响约 44 个小时`
  - `up / flat / down+flat = 28 / 14 / 2`
  - `pure down = 0`
  - `shadow-admission queue / one_more_gate`

## 本轮改动文件
- `docs/TODO.md`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`

## Git / 提交说明
- 当前仓库存在大量与本轮无关的既有脏文件（跨多个 docs/reports/scripts/artifacts）。
- 为避免误混，本轮**未提交**（no commit）。
- 若后续需要提交，建议只做严格 selective commit（仅上述 4 个文件）。
