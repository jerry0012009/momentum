# 2026-04-17 21:01 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-17_2032_rank28_freshintake_background_p0_residual_absorbed.md`
  - `2026-04-17_1952_rank33_freshintake_background_p0_failurehint_overlap.md`
  - `2026-04-17_1917_rank83_freshintake_background_p0_strongconfirm_overlap.md`
  - `2026-04-17_1904_rank56_freshintake_background_p0_public_cluster_timing.md`
  - `2026-04-17_1846_rank71_extremeonly_freshintake_background_p0_vwap_anchor_overlap.md`
  - `2026-04-17_1810_rank89_freshintake_background_p0_failurefamily_overlap.md`
- Recent strategy review:
  - `2026-04-17_1955_strategy-review.md`
  - `2026-04-17_1850_strategy-review.md`
  - `2026-04-17_1801_strategy-review.md`
- Park-reframe sources consulted for this rewrite:
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`
  - `research/park_reframe/2026-03-25_0457_rank101-park-reframe.md`
  - `research/park_reframe/2026-04-11_1550_rank57-park-reframe.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`Rank 5 / direct session-tail intraday TSMOM`。**
   - 原因：`Rank 28` 已在 20:32 UTC 的 first verdict 中直接收口 `background/P0`，且没有形成新的 survivor / P2；按当前顺位，fresh intake 前排自然切到原 cycle_plan 的 conditional item2，也就是 `research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `Rank 28`；其 residual 已被既有 `Rank 28b` 与更快的 `BTC shock / leader-basket / cross-venue catch-up` 宿主吸收，直接 first verdict 收口 `background/P0`，没有拿到新的 `keep_P1`，因此 survivor 槽位继续保持空。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 one-time `P2->P1 re-scope`，但它已退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 本轮前排对象里不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需分配新 `Rank`。

## 关键判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor 要收口。
- 因此本轮只能回到新的 fresh intake。
- `Rank 28` 已完成 first verdict 并直接回收背景池，所以前排必须切到下一个具体对象，而不能继续复读 `Rank 28` 的 survivor guardrail。
- `Rank 5` 仍是合法、具体、且尚未被当前 runtime 消费的新前排对象；它的问题也足够清楚：只回答旧 `direct session-tail` 残余压成 `same-clock / session-pocket residual` 后，是否还保留独立 queue-facing 主语，还是早已被 `Rank 5b` 与现有 `NYSE-open / pseudo-session / same-clock recurring-pocket` 家族吸收。
- 尾部预算继续保留两个具体 conditional intake：
  - `Rank 101`：只看 `long-side hold-quality residual note` 能否脱离共享 quality note 身份；
  - `Rank 57`：只看旧 squeeze/compression residual 是否还能脱离 breakout-family-local compression admission 宿主。
- 这样排比继续在 `Rank 28 / 33 / 56 / 83` 这些刚收口对象上打转更诚实，也符合“已有前排都收口后才切回 fresh intake”的默认顺序。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- 保持 `status = open_pending_first_verdict`
- `current_target = research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`
- `latest_result` 改写为：`Rank 28` 已直接收口 `background/P0`，因此 fresh intake 前排切到 `Rank 5`
- `source_record` 保持 `Rank 5`

### Surviving candidate slot
- 保持 `none`

### Active P2 slot
- 保持 `none`

### cycle_plan
1. `Rank 5` fresh intake first-verdict
2. `Rank 101` conditional fresh intake
3. `Rank 57` conditional fresh intake
4. `Rank 5` conditional survivor guardrail（仅当 item1=`keep_P1` 时触发）

## 为什么本轮这样排
- policy 明确要求：只要存在 `P3 / P2 / P1` 前排动作，就不得把新的 intake 排到前面；当前这些槽位都为空，因此 fresh intake 是唯一合法主线。
- 同时，切回 fresh intake 后必须直接指定至少 1 个具体对象，不能写“回到 intake”这种空话。
- `Rank 5` 之所以在第一位，不是因为它更有希望升层，而是因为它是**当前前排唯一合法、尚未被本轮 runtime 消费的具体对象**。
- `Rank 101` 与 `Rank 57` 被压在后面，是诚实的预算尾部：只有在 `Rank 5` first verdict 完整收口且仍无 survivor / P2 时，才继续按顺位补它们。
- 第 4 项只为防止如果 `Rank 5` 意外拿到 `keep_P1`，下一轮又被拖成开放式研究；若 item1 直接 `background/P0`，本项自然跳过。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明应直升 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-17_2101_strategy-review.md`

## Tail steps
- homepage 刷新：按要求单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若因 `/var/www` 权限、preflight 或 `SIGKILL` 失败，按 policy 记为非阻断尾部失败。
- 邮件通知：无论 publish 是否成功，均继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank28收口后切到Rank5 intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-17_2101_strategy-review.md`。
