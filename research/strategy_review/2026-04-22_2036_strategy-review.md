# 2026-04-22 20:36 UTC strategy review（bot2，40m desk review）

## 输入与约束确认
- 已读取：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 已核对 repo 现状：`git status --short --branch` 与最近 `research/optimization_loop/`、`research/strategy_review/` 记录
- 本轮只改写 runtime state：`docs/BOT2_BOT3_STATE.md`
- rank 完整性检查：当前前排对象不存在无 rank 情况；`Paper launch queue.current_target = none`，`Surviving candidate = none`，`Active P2 = none`

## 四个问题（严格按要求）
1) `Paper launch queue` 是否非空？
- **否（就待执行 queue 而言为空）。**
- 说明：`connected_runner_live` 列表非空，但 `current_target = none`；当前没有仍待 bot3 补 runner / scheduler / first verified run 的 `P3` 前排对象。

2) 本轮 `fresh intake` 是什么？
- **`research/quant_digests/2026-04-22_0828_xs-momentum-crashgate-portability-verdict.md`**
- 理由：上一轮 `cycle_plan` 前两条 fresh intake（`OFI/Kalman maker skew`、`partial-corr lag catch-up`）都已完成并收口 `background/P0`，当前排到最前且尚未消费的是第 3 条 `xs-momentum-crashgate-portability-verdict`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **不值得。**
- 上一条 fresh intake 是 `research/quant_digests/2026-04-22_1533_partialcorr-lagcatchup-thresholdcalibration-alpha.md`。
- 最新 first verdict 已将它诚实收口为 `background/P0`：`15m` 基线 gross 仅约 `+4.88bps/event`，不足以覆盖最小双腿成本；唯一较亮的 `5m` pocket 也只剩 `10` 笔极小样本，且 pair 主语仍落在已 live `Rank 424 / 431` 的 pairs family 内，没有留下值得耗费唯一 survivor follow-up 的独立新增价值。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 哪个出口最近？
- **当前不存在明确 `Active P2`。**
- 最近一个 `Active P2` 仍是 `Rank 434 / newlisting early-short bubble fade`，且已经由 bot2 兜底 `promote_P3` 后完成 launch wiring，当前不再停留在 `P2`。

## 本轮裁决
- 不需要新的 `P2 -> P3` 兜底动作：当前没有 `Active P2`。
- 不存在 survivor 锁槽对象：`Surviving candidate.current_target = none`。
- 不存在无 rank 前排对象：无需补号。
- 因此前排链条已经诚实收口，本轮默认切回 `fresh intake`。

## cycle_plan 重写理由
按 policy 默认顺序扫描：
1. `P3 handoff / launch wiring`：无 pending 对象；`Rank 434` 已完成 runner + scheduler + first verified run。
2. `P2 / Active P2`：当前为 `none`，无 admission / promote / park 动作。
3. `P1 / Surviving candidate`：当前为 `none`，无唯一 follow-up 动作。
4. 因此前排链条全部收口，本轮预算回到具体 fresh intake；同时把上一轮已完成的前两条 stale pending 从默认执行前排中移除。

## 本轮写回的 cycle_plan
1. `research/quant_digests/2026-04-22_1945_xs-fundingcarry-breakout-shell.md`
2. `research/quant_digests/2026-04-22_0828_xs-momentum-crashgate-portability-verdict.md`
3. `research/quant_digests/2026-04-22_0622_xs24h-loserwinner-voltarget-shell.md`
4. `research/quant_digests/2026-04-22_1026_segmented-signature-pairfade-shell.md`

## 为什么这样排
- `#1` 是当前最新且尚未消费的新 repo fresh intake；它补的是 `8h funding carry continuation` 这一条和现有 basis / pairs / fade 家族不同的横截面 carry 主语，值得优先先做 first verdict。
- `#2` 是当前最前的既有未完成 fresh intake，必须先诚实回答：若 raw top-N 动量本体先天费后偏弱，crash gate 是否还配占一个独立前排对象。
- `#3` 是当前最像可能留下 `keep_P1` 的 majors8 relative-value sleeve，但也必须先用最小成本 / distinctness blocker 做 first verdict，避免把 broad basket 壳错判成 survivor。
- `#4` 把 pairs 家族里较新的 `segmented-signature admission` 放在后位：它不是为了自动拉老 pair 家族回前排，而是要先回答这层非线性 admission 是否相对已 live `Rank 424 / 431` 留下独立新增价值。

## 状态改写摘要
- `Fresh intake slot.current_target`：改为 `research/quant_digests/2026-04-22_0828_xs-momentum-crashgate-portability-verdict.md`
- `Fresh intake slot.source_record`：同步改为该对象
- `Fresh intake slot.latest_result` / `latest_result_record`：保留刚完成的 `partial-corr lag catch-up -> background/P0` 收口
- `Active P2 slot.latest_result_record`：更新为本轮 review `research/strategy_review/2026-04-22_2036_strategy-review.md`
- `cycle_plan`：移除已 done 的前两条 stale pending，重写为 4 条新的具体 pending fresh intake

## repo / recent evidence 摘要
- 最近 `optimization_loop` 最新完成：
  - `2026-04-22_1451_rank434_p3_launch_wiring_connected_runner_live.md`
  - `2026-04-22_2010_ofi_kalman_maker_skew_freshintake_background_p0.md`
  - `2026-04-22_2027_partialcorr_lagcatchup_freshintake_background_p0.md`
- 最近 `strategy_review` 最新一条为 `2026-04-22_1921_strategy-review.md`，其中前两条 intake 已完成，不应继续维持为旧 pending。
- repo 工作树仍有大量历史未跟踪临时文件，但不改变本轮 runtime 调度结论。

## 尾部执行回执（非阻断）
- homepage 刷新：已按独立命令执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若因 `/var/www` 写入或 build 被杀而失败，按规则只记为非阻断尾部失败，不回滚本轮 state / review log。
- 邮件摘要：已按独立命令执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 切回 funding carry 与三条 fresh intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-22_2036_strategy-review.md`；若失败，只记尾部通知失败，不回滚本轮 state / review log。
