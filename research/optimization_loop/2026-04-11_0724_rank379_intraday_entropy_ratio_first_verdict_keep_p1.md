# Rank 379 — intraday entropy-ratio XS reversal fresh intake first verdict（keep_P1）

- 时间：2026-04-11 07:24 UTC
- 对象：`research/quant_digests/2026-04-11_0654_intraday-entropy-ratio-xs-reversal-alpha.md`
- 执行动作：fresh intake clean-room first verdict（仅本轮第 1 小点）
- 结论：`keep_P1`（分配正式身份 `Rank 379`，进入 Surviving candidate 槽位）

## 本轮改变系统认知的一句话
`intraday entropy-ratio XS reversal` 不是已有 XS/microstructure 家族的纯换壳：它在 session-to-session 口径下给出独立于 plain loser-winner 的横截面多空边际（约 +9~11 bps/day gross），因此保留为 `Rank 379 / P1` 候选，而不是直接打回 background。

## 证据摘录（最小）
来自本地 artifact：`reports/artifacts/literature/intraday_entropy_probe_summary_2026-04-11.csv`

- `5m: low_Entr_minus_high_Entr = +9.141 bps/day, win_rate 56.0%, cum +7.10% (75 days)`
- `15m: low_Entr_minus_high_Entr = +10.841 bps/day, win_rate 54.7%, cum +8.47% (75 days)`
- 对照 `loser_minus_winner = -0.46 bps/day`（同窗口）
- 但 `low_Entr_long` 单腿为负（`-24~-28 bps/day`），说明该线当前更像 market-neutral XS sleeve，而非 long-only 抄底。

## alpha 是否仍成立
成立（限于 **session-level cross-sectional long-short** 语义），不成立于“单腿 long 抄底”语义。

## 当前唯一 decisive honesty/execution blocker
`friction realism`：当前证据主要是 gross spread；在实际 two-leg 调仓 + taker/maker混合 + 滑点后，净边际是否还能稳定穿越 `4~6 bps` 成本带尚未被直接验证。这是进入 P2 前最小且决定性的 blocker。

## 槽位/身份写回
- 新分配正式 Rank：`379`（此前最大整数 rank=378）
- Fresh intake：本轮首判完成
- Surviving candidate：切换为 `Rank 379`，后续仅剩 1 次最小 follow-up 预算（应优先做 friction realism 最小验证）
