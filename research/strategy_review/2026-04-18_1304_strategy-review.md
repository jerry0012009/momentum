# 2026-04-18 13:04 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仅见大量既有未跟踪临时/研究文件噪声；未发现需要按 policy 进入前排的 rankless `P1/P2/P3` 对象）
- Recent optimization loop:
  - `2026-04-18_1300_headline_sentiment_freshintake_background_p0_sample_latency.md`
  - `2026-04-18_1217_partialmoment_overlay_freshintake_background_p0_veto_only.md`
  - `2026-04-18_1157_mexc_pump_crosssection_freshintake_background_p0_naked_continuation.md`
  - `2026-04-18_1143_cvd_nonconfirm_freshintake_background_p0_child_execution_blocker.md`
  - `2026-04-18_1022_funding4h_context_freshintake_background_p0_overlay_only.md`
  - `2026-04-18_0910_multiquote_spreadfade_freshintake_background_p0_makerfirst_only.md`
- Recent strategy review:
  - `2026-04-18_1152_strategy-review.md`
  - `2026-04-18_1105_strategy-review.md`
  - `2026-04-18_0948_strategy-review.md`
  - `2026-04-18_0819_strategy-review.md`
- New intake / fallback materials checked for this rewrite:
  - `research/quant_digests/2026-04-18_1220_tradeflow-imbalance-router-alpha.md`
  - `research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`
  - `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - 运行态里 `current_target = none`；`connected_runner_live` 列表都是已经完成 dedicated runner + scheduler + first verified run 的已接线对象，不存在待补 wiring 的 queue 前排。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`research/quant_digests/2026-04-18_1220_tradeflow-imbalance-router-alpha.md`**。
   - 理由：上一条 fresh intake `headline polarity × next-few-bar drift` 已在 `2026-04-18_1300_headline_sentiment_freshintake_background_p0_sample_latency.md` 诚实收口 `background/P0`；当前没有 survivor、没有 active P2、也没有待接线 P3，因此按 policy 默认顺序切到最近新的具体 repo/paper/alpha 报告，队首应切到 `tradeflow imbalance router`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `research/quant_digests/2026-04-18_1003_headline-sentiment-stepin-alpha.md`。
   - 决定性 blocker 已足够：repo 自带样本只有 `48` 个事件，`bearish` 仅 `4` 条；同时 next `1m/5m/15m` signed drift 总体为负，且 headline 抓取/分类 live latency 只会继续削弱边际，不值得占用 survivor 唯一 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`。最近一次 active P2 仍是 `Rank 417`，但它已在 `2026-04-16_0309_rank417_p2_exit_rescope_to_p1_noeth_pairs.md` 执行完 `one-time P2->P1 re-scope` 并退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前 `Paper launch queue / Surviving candidate / Active P2` 均无 rankless front object。
- 当前新的 `fresh intake` 仍未得到 `keep_P1 / P2 / P3` verdict。
- 本轮无需补新 `Rank`。

## 排班判断
- 当前没有 `P3 launch wiring` 动作、没有 `Active P2`、没有 survivor；因此本轮默认全部回到具体 `fresh intake`。
- 队首 fresh intake 直接切到最近尚未消费的 `tradeflow imbalance router`。
- 其后剩余预算才允许补具体 fallback intake；按 policy 优先从 `research/park_reframe/INDEX.md` 的 `derived_hypothesis_drafted` 中选具体对象，而不是写空泛“继续 intake”。
- 结合索引里仍明确标记为 `derived_hypothesis_drafted` 的对象，本轮顺序重写为：
  1. `tradeflow imbalance router`
  2. `Rank 60 / retest-window impulse re-break confirmation`
  3. `Rank 27 / breakout-bar taker-imbalance confirmation`
  4. `Rank 57 / breakout-family-local pre-break compression admission`
- 其中 item2~4 都是 **conditional fresh intake**：只有 item1 以及前序项已诚实收口、且当前仍没有 survivor / P2 / P3 前排动作时，才进入下一项。

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`，因此不存在 bot2 必须兜底直升 `P3 / Paper launch queue` 的对象。
- 当前 `Paper launch queue.current_target = none`，也不存在 queue 内待补 wiring 的对象。
- 结论：**本轮无需**直接把任何对象写入 `P3 / Paper launch queue` 或 handoff 路径。

## State rewrite
已写回 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot.current_target -> research/quant_digests/2026-04-18_1220_tradeflow-imbalance-router-alpha.md`
- `Fresh intake slot.source_record -> research/quant_digests/2026-04-18_1220_tradeflow-imbalance-router-alpha.md`
- `Fresh intake slot.latest_result` 维持刚完成的 `headline -> background/P0` 收口结论
- `cycle_plan` 重写为 4 项真实 pending 动作，且都带具体对象，不保留抽象模板句子

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_1304_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
2. 中文邮件摘要（无论 publish 成败都继续尝试）：
   - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 切到tradeflow并补三条派生 intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_1304_strategy-review.md`
