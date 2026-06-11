# Rank 379 — survivor follow-up（friction realism）并升级 P2

- 时间：2026-04-11 08:23 UTC
- 对象：`Rank 379 / intraday entropy-ratio XS reversal`
- 执行动作：执行 survivor 唯一一次 follow-up；做最小 two-leg friction realism 检查并给出出口决策
- 结论：`promote_P2`

## 本轮改变系统认知的一句话
`Rank 379` 在 session-to-session 横截面多空口径下，gross edge（`+9.14~+10.84 bps/day`）经最小成本阶梯后仍保留可交易净边际（15m 输入在 `6 bps` 下仍约 `+4.84 bps/day`），因此 survivor follow-up 收口并上推到 `Active P2`，不再停留 P1。

## 最小证据（仅覆盖 decisive blocker：friction realism）
数据源：`reports/artifacts/literature/intraday_entropy_probe_summary_2026-04-11.csv`

- 5m `low_Entr_minus_high_Entr`：gross `+9.141 bps/day`
  - net@2bps = `+7.141`
  - net@4bps = `+5.141`
  - net@6bps = `+3.141`
- 15m `low_Entr_minus_high_Entr`：gross `+10.841 bps/day`
  - net@2bps = `+8.841`
  - net@4bps = `+6.841`
  - net@6bps = `+4.841`

解读（two-leg 成本口径）：
- 若以 `4~6 bps/day` 作为最小可交易成本带，5m 输入在 6bps 档位下净边际偏薄；
- 15m 输入在 6bps 档位下仍维持接近 `+4.8 bps/day`，可支撑进入下一层 admission 决策，而非直接打回 background。

## 三选一出口决策
- `promote_P2` ✅
- `drop_to_background(P0)` ❌（并非成本后全面失效）
- `one-time P2->P1 re-scope` ❌（当前不存在比“进入 P2 admission 出口轮”更优且唯一的重定义方向）

## alpha 在净成本后是否仍成立
成立（以 session-level XS long-short、优先 15m entropy 输入为主）；不建议把 5m 高摩擦版本当核心承载。

## 是否仍存在单一 decisive honesty/execution blocker
存在且仅剩一个：`P2 admission 出口轮` 需一次性收口 effectiveness / cross-asset / time / parameter 的最小联合结论，并补 1 个 honesty/execution 最小 blocker 验证后直接给出 `P3/P0/P1-rescope` 三选一。

## runtime 写回
- Surviving candidate（Rank 379）唯一 follow-up 已消耗并完成；
- 对象层级：`P1 -> P2`；
- `Active P2 slot` 切换为 `Rank 379`，等待下一小点执行 admission 出口决策。
