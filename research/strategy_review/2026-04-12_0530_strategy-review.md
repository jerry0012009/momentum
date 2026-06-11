# 2026-04-12 05:30 UTC strategy review（bot2）

## 读取范围（按约束顺序）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo / 最近记录
   - `git status --short`
   - 最近 `research/optimization_loop/`
   - 最近 `research/strategy_review/`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- **否（待接线队列为空）**：`current_target: none`。
- 注：`connected_runner_live` 非空，但这些对象都已完成 wiring，不构成本轮待执行 `P3 launch wiring`。

2. 本轮 `fresh intake` 是什么？
- `research/quant_digests/2026-04-11_2058_smallcap-crossvenue-perp-dislocation-alpha.md`（当前 fresh intake 槽位的 pending 对象）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **是，值得且已锁定**。
- 上一条 fresh intake 为 `Rank 386 / SOL retail-more-short-than-top divergence`，首判为 `keep_P1`，且 `followup_budget_remaining: 1`，因此本轮应优先执行其唯一 survivor follow-up，不得被新 intake 覆盖。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前 `Active P2 = none`。
- 因无 active P2，本轮不存在 bot2 需触发的 `P2 -> P3` 兜底直推场景。

## rank 合规检查
- 前排对象检查：
  - `Surviving candidate` = `Rank 386`（已有正式 rank）
  - `Paper launch queue.current_target` = `none`
  - `Active P2.current_target` = `none`
- 未发现“前排对象无 rank”违规，无需补号。

## cycle_plan 重排（已写回 state）
按 policy 默认顺序：`P3 wiring > P2 admission/exit > P1 survivor follow-up > fresh intake > P0`。

本轮重写为 4 项，前排收口优先且均为具体对象：
1. `Rank 386` survivor 唯一 follow-up（出口直接回答 `promote_P2` 或 `background/P0`）
2. `2026-04-11_2058_smallcap-crossvenue-perp-dislocation-alpha.md` fresh intake first-verdict
3. `research/park_reframe/2026-04-10_1516_rank74-park-reframe.md` conditional fresh intake
4. `tmp_2026-04-12_0518_deribit-okx-longdated-wing-quotegap-alpha_email.txt` fresh intake first-verdict

并满足格式约束：
- 每项仅含 `target / action / success_criterion / result / status`
- 新生成项 `result = none`
- 新生成项 `status = pending`

## 约束核对
- 本轮仅更新：`docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动拉回 background pool 旧候选
- `TODO.md` 未作为排班依据
- 无需执行 `P2 -> P3` 兜底强推（当前无 Active P2）

## 尾部执行
- publish homepage index：已尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，进程无输出且长时间未退出，本轮按“非阻断尾部失败”处理，未回滚 state/log。
- 中文邮件摘要：已执行
  - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank386 survivor优先与本轮排班更新" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-12_0530_strategy-review.md`
  - 结果：发送成功。
