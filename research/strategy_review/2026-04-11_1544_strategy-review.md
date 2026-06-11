# 2026-04-11 15:44 UTC strategy review（bot2）

## 读取范围（按约束顺序）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo / 最近记录：
   - `git status --short`
   - 最近 `research/optimization_loop/`：
     - `2026-04-11_1537_rank382_freshintake_first_verdict_keep_p1.md`
     - `2026-04-11_1452_rank381_p3_wiring_first_verified_run_connected_live.md`
     - `2026-04-11_1405_rank381_p3_wiring_scheduler_enabled.md`
     - `2026-04-11_1331_rank381_p3_wiring_runner_dryrun_done.md`
   - 最近 `research/strategy_review/`：`2026-04-11_1458_strategy-review.md`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- `connected_runner_live` 已包含多条已接线对象（含 `Rank 381`），虽然 `current_target=none`，但 queue 明确不是空。

2. 本轮 `fresh intake` 是什么？
- 本轮 fresh intake 目标切换为 `2026-04-11_1353_sparse-lagvote-nextbar-alpha`（等待 first-verdict）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake（`Rank 382`）首判为 `keep_P1`，已进入 survivor 且 follow-up 预算=1；按 policy 应优先执行这唯一一次收口检查。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前 `Active P2 = none`。
- 因无在槽 P2，本轮不存在待判的 P2 出口对象。

## rank 合规检查
- 前排对象中：`Rank 382`（survivor）已具 formal rank；`Active P2` 为空；`Paper launch queue` 对象均具 rank。
- 未发现“达到 keep_P1/P2/P3 但无 rank”的违规项；本轮无需补 rank。

## P2->P3 兜底裁判结论
- 当前无 `Active P2`，不存在“已够格但未升 P3”的漏升对象。
- `Rank 381` 已在上一轮完成 `P2->P3` 且 first verified run 已收口到 `connected_runner_live`。

## cycle_plan 重写（已写回 `docs/BOT2_BOT3_STATE.md`）
按 policy 默认优先级重排为：
1) survivor 唯一 follow-up（`Rank 382`：fill-adjusted capacity realism，一次性收口 `promote_P2` 或 `background/P0`）
2) fresh intake：`2026-04-11_1353_sparse-lagvote-nextbar-alpha.md`
3) fresh intake：`2026-04-11_1258_pasthour-max-overvaluation-xs-fade-alpha.md`
4) conditional fresh intake：`2026-04-11_0248_salience-crosssectional-downside-vs-upside-alpha.md`

约束核对：
- 仅更新 `BOT2_BOT3_STATE.md`，未改 policy/brief/operating card/cron prompt。
- 未把 background pool 旧候选拉回前排。
- 新 cycle_plan 项均为 `result: none`、`status: pending`。

## 尾部执行
- Homepage 刷新（best-effort）：已执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，命令无输出且长时间未返回；按非阻断尾部失败处理，不回滚本轮 state/log。
- 邮件摘要：已执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] survivor优先收口并切换新fresh intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-11_1544_strategy-review.md`，发送成功。