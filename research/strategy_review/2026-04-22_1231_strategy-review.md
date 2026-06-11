# 2026-04-22 12:31 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-22_1217_rank434_newlisting_earlyshort_freshintake_keep_p1.md`
  - `research/optimization_loop/2026-04-22_1129_segmented_signature_pairfade_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-22_1049_macd_feetrap_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-22_1015_perp_perp_funding_diff_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-22_0958_feeaware_spot_xvenue_gap_freshintake_background_p0.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-22_1136_strategy-review.md`
  - `research/strategy_review/2026-04-22_1054_strategy-review.md`
  - `research/strategy_review/2026-04-22_1005_strategy-review.md`
- Fresh-intake source evidence:
  - `research/quant_digests/2026-04-22_1215_refasset-copula-pairfade-alpha.md`
  - `research/quant_digests/2026-04-22_1115_newlisting-early-short-bubblefade-shell.md`
  - `research/quant_digests/2026-04-22_0545_polymarket-streak-pricehurdle-binary-alpha.md`
  - `research/quant_digests/2026-04-22_0353_deribit-okx-option-quote-gap-shell.md`

## 仅回答 4 个问题

1. `Paper launch queue` 是否非空？
- 否。
- `current_target = none`；已连接 runner 的 P3 队列包含 Rank 200/201/213/229/342/368/370/376/378/379/381/382/389/397/401/402/405/422/423/424/427/431，但当前没有待接线对象。

2. 本轮 `fresh intake` 是什么？
- 当前前排首先不是 fresh intake，而是 `Rank 434 / newlisting early-short bubble fade` 的 survivor 唯一 follow-up。
- 在该 survivor 已诚实排入后，本轮可用剩余预算切到新的 fresh intake：`research/quant_digests/2026-04-22_1215_refasset-copula-pairfade-alpha.md`（`BTC 参考资产残差 × copula 条件失衡 × alt-alt pair fade`）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，而且已经合法进入 survivor。
- `research/optimization_loop/2026-04-22_1217_rank434_newlisting_earlyshort_freshintake_keep_p1.md` 给出 `keep_P1`：`2025-01/02` 两个独立入场月份保持正 after-cost，额外 `+20/+50bps` roundtrip 摩擦后平均仍为正；但 `2025-03` 转负且 top5 symbol 贡献约 `79%`，所以它只值得唯一 survivor follow-up，不应直接升 P2。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 因无 active P2，本轮不存在 P3/P1/P0 出口距离判断对象。

## Rank 完整性检查
- `Rank 434` 已在 fresh intake 首判 `keep_P1` 时获得正式 rank，并已写入 survivor slot。
- `Paper launch queue / Active P2` 当前无待补 rank 对象。
- 本轮新增 fresh intake `refasset-copula-pairfade` 尚未产生 `keep_P1 / P2 / P3` verdict，因此暂不分配 rank。

## P2 -> P3 兜底判断
- 本轮无 `Active P2`。
- 最近 evidence 没有出现“已清楚值得 paper trade / paper launch、但 bot3 未升级”的 active P2，因此 bot2 无需兜底直推 P3。

## State rewrite
已按 policy 重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
1. `Rank 434 / newlisting early-short bubble fade` survivor follow-up：直答 `promote_P2` 或 `background/P0`。
2. `research/quant_digests/2026-04-22_1215_refasset-copula-pairfade-alpha.md` fresh intake first verdict。
3. `research/quant_digests/2026-04-22_0545_polymarket-streak-pricehurdle-binary-alpha.md` conditional fresh intake。
4. `research/quant_digests/2026-04-22_0353_deribit-okx-option-quote-gap-shell.md` conditional fresh intake。

没有改写 policy / brief / operating card / cron prompt；没有把 background pool 旧候选拉回前排；`Background pool guard` 仅作为隐式护栏满足，未单独占用 cycle_plan。

## Tail status
- homepage index publish：待独立执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`。
- email summary：待独立执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank434 survivor follow-up" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-22_1231_strategy-review.md`。
