# 2026-04-17 21:41 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-17_2132_rank101_freshintake_background_p0_holdquality_note_absorbed.md`
  - `2026-04-17_2109_rank5_freshintake_background_p0_sameclock_residual_absorbed.md`
  - `2026-04-17_2032_rank28_freshintake_background_p0_residual_absorbed.md`
  - `2026-04-17_1952_rank33_freshintake_background_p0_failurehint_overlap.md`
  - `2026-04-17_1917_rank83_freshintake_background_p0_strongconfirm_overlap.md`
  - `2026-04-17_1904_rank56_freshintake_background_p0_public_cluster_timing.md`
  - `2026-04-17_1846_rank71_extremeonly_freshintake_background_p0_vwap_anchor_overlap.md`
  - `2026-04-17_1810_rank89_freshintake_background_p0_failurefamily_overlap.md`
  - `2026-04-17_1756_rank27_conditional_freshintake_blocked_stale_replay.md`
- Recent strategy review:
  - `2026-04-17_2101_strategy-review.md`
  - `2026-04-17_1955_strategy-review.md`
  - `2026-04-17_1850_strategy-review.md`
- Park-reframe sources consulted for this rewrite:
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-04-11_1550_rank57-park-reframe.md`
  - `research/park_reframe/2026-03-22_1633_rank14-park-reframe.md`
  - `research/park_reframe/2026-03-23_0256_rank25-park-reframe.md`
  - `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`Rank 57 / squeeze-compression residual`。**
   - 原因：`Rank 5` 与 `Rank 101` 已在 21:09 / 21:32 UTC 的 first verdict 中按顺序直接收口 `background/P0`，且没有形成新的 survivor / P2；按当前 runtime 前排顺位，fresh intake 自然切到 `research/park_reframe/2026-04-11_1550_rank57-park-reframe.md`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `Rank 101`；它的 long-side hold-quality residual 仍只是 shared quality note，distinctness 不足以独立排队，已直接 first verdict 收口 `background/P0`，没有拿到新的 `keep_P1`，因此 survivor 槽位继续保持空。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 one-time `P2->P1 re-scope`，但它已退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 本轮前排对象里不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需分配新 `Rank`。

## 关键判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor 要收口。
- 因此本轮仍只能回到新的 fresh intake。
- `Rank 57` 必须排在第一位，因为它是当前前排唯一合法、尚未被 runtime 消费的具体对象；而且它的问题很窄：只回答旧 `TTM squeeze release` 的 residual 在 `Rank 57b` 已表达、且 2026-04-08 first verdict 已收口后，是否还残留独立 queue-facing 主语。
- `Rank 57` 之后，不应继续保留已经失效的 `Rank 5` survivor 占位；预算尾部应直接改成新的、具体的 park-reframe intake。
- 在当前仍未被今日 runtime 消费的 park-reframe 候选里，更值得接在后面的，是更明确的 `derived_hypothesis_drafted` / `soft_reframe_candidate`：
  - `Rank 14b`：`directional breadth coherence` 作为 long-side continuation veto；
  - `Rank 25c`：`EMA context-only + Donchian breakout primary trigger`；
  - `Rank 4`：pairs 主题是否还留有旧 rank 可诚实窄救的一刀，还是已经整体上移到新的 full-stack stat-arb family。
- 这样排比继续在 `Rank 5 / 101` 的已完成对象上挂 survivor guardrail 更诚实，也符合“已有前排都收口后才继续补新的 fresh intake”的默认顺序。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- 保持 `status = open_pending_first_verdict`
- `current_target = research/park_reframe/2026-04-11_1550_rank57-park-reframe.md`
- `latest_result` 维持：`Rank 101` 已直接收口 `background/P0`，fresh intake 已切到 `Rank 57`
- `source_record` 保持 `Rank 57`

### Surviving candidate slot
- 保持 `none`

### Active P2 slot
- 保持 `none`

### cycle_plan
1. `Rank 57` fresh intake first-verdict
2. `Rank 14b` conditional fresh intake
3. `Rank 25c` conditional fresh intake
4. `Rank 4` conditional fresh intake

## 为什么本轮这样排
- policy 明确要求：只要存在 `P3 / P2 / P1` 前排动作，就不得把新的 intake 排到前面；当前这些槽位都为空，因此 fresh intake 是唯一合法主线。
- 同时，切回 fresh intake 后必须直接指定至少 1 个具体对象，不能写抽象句。
- `Rank 57` 第一位，不是因为它更可能升级，而是因为它是**当前前排唯一合法、尚未被 runtime 消费的具体对象**。
- `Rank 14b / 25c / 4` 被放在后面，是诚实的预算尾部：只有当 `Rank 57` 已直接收口、且仍无 survivor / P2 时，才继续顺排。
- 这三条后续对象都比继续复读今天已消费的 `Rank 5 / 101 / 28 / 33 / 56 / 83 / 89 / 71` 更合法：
  - `Rank 14b` 与 `Rank 25c` 是仍未被 runtime 消费的明确 derived-hypothesis；
  - `Rank 4` 虽仍大概率会被压回 `background/P0`，但至少它的问题是具体且不同于今天已消费的 overlap / family-absorbed 残余。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明应直升 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-17_2141_strategy-review.md`

## Tail steps
- homepage 刷新：按要求单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若因 `/var/www` 权限、preflight 或 `SIGKILL` 失败，按规则记为非阻断尾部失败。
- 邮件通知：无论 publish 是否成功，均继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank101收口后切到Rank57 intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-17_2141_strategy-review.md`。
