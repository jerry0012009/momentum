# 2026-04-17 19:55 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-17_1952_rank33_freshintake_background_p0_failurehint_overlap.md`
  - `2026-04-17_1917_rank83_freshintake_background_p0_strongconfirm_overlap.md`
  - `2026-04-17_1904_rank56_freshintake_background_p0_public_cluster_timing.md`
  - `2026-04-17_1846_rank71_extremeonly_freshintake_background_p0_vwap_anchor_overlap.md`
  - `2026-04-17_1810_rank89_freshintake_background_p0_failurefamily_overlap.md`
  - `2026-04-17_1756_rank27_conditional_freshintake_blocked_stale_replay.md`
- Recent strategy review:
  - `2026-04-17_1850_strategy-review.md`
  - `2026-04-17_1801_strategy-review.md`
  - `2026-04-17_1721_strategy-review.md`
- Park-reframe sources consulted for this rewrite:
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
  - `research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`
  - `research/park_reframe/2026-03-25_0457_rank101-park-reframe.md`
  - `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
  - `research/park_reframe/2026-04-11_1550_rank57-park-reframe.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**切到 `Rank 28 / cross-market intraday leader-laggard`。**
   - 原因：`Rank 56 / 83 / 33` 已在本轮前半段按顺序诚实收口为 `background/P0`，当前前排没有 `P3 / P2 / survivor` 待收口对象；按 policy 必须回到 fresh intake，而 `Rank 28` 是目前仍未被当前 runtime 消费、且在 `park_reframe/INDEX.md` 里保留为 `soft_reframe_candidate` 的具体对象。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 最近实际执行的 fresh-intake 链条是 `Rank 56 -> Rank 83 -> Rank 33`，三者全部 first verdict 直接收口 `background/P0`，没有任何对象拿到新的 `keep_P1`，因此 survivor 槽位保持空。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 one-time `P2->P1 re-scope`，但它已退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 本轮前排对象里不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需分配新 `Rank`。

## 关键判断
- 本轮没有待接线 `P3`；没有 `Active P2`；也没有 survivor 需要收口。
- 因此只能回到新的 fresh intake。
- 但 fresh intake 不能继续复读今天已消费或已被既有 family 吸收的对象：`Rank 56 / 83 / 33 / 71 / 89 / 74` 已全部完成诚实收口；`Rank 27` 还在 `latest_blocked_record` 里明确挂着 stale replay 风险，不适合再伪装成“新对象”。
- 在当前仍可诚实使用的 park-reframe 候选中，`Rank 28` 最适合排在第一位：
  - 它仍是 `soft_reframe_candidate`，而不是已经被 runtime 吃掉的旧 residual；
  - 它的问题也非常明确：必须直接回答“旧 `15m direct lag-trade` 的残余，是否还配占一个 queue-facing对象位，还是已被更快的 `BTC shock / major-lead / cross-venue catch-up` family 吸收”。
- 预算尾部保留两个具体 conditional intake：
  - `Rank 5`：只看 session-pocket residual 是否还能从现有 session-clock raw-alpha family 里拉开；
  - `Rank 101`：只看它是否仍只是 shared hold-quality note，而不是独立 alpha 主语。
- 这样做比继续绕回已消费对象更诚实，也符合 “derived_hypothesis_drafted / soft_reframe_candidate 优先” 的 intake 顺序。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- `status = open_pending_first_verdict`
- `current_target = research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
- `source_record` 同步切到 `Rank 28`
- `latest_result` 明确写回：`Rank 56 / 83 / 33` 已按顺序完成本轮收口，因此当前必须切到新的合法 intake

### Surviving candidate slot
- 保持 `none`

### Active P2 slot
- 保持 `none`

### cycle_plan
1. `Rank 28` fresh intake first-verdict
2. `Rank 5` conditional fresh intake
3. `Rank 101` conditional cheap fallback fresh intake
4. `Rank 28` conditional survivor guardrail（仅当 item1=`keep_P1` 时触发）

## 为什么本轮这样排
- policy 明确要求：前排 `P3 / P2 / P1` 链条都诚实收口后，才允许切回新的 fresh intake；当前这一前提成立。
- 同时，切回 fresh intake 后必须直接指定具体对象，不能写抽象句。
- `Rank 28` 优先于 `Rank 5 / 101`，因为它仍是较新的、尚未被 runtime 消费的 `soft_reframe_candidate`，且 verdict 问题足够清晰，最适合放在当前轮 front slot。
- `Rank 5 / 101` 被压在后面，是因为它们更像 tail-budget 条目：若 `Rank 28` 已直接收口、且仍无 survivor / P2，再诚实补它们；否则不应反客为主。
- 第 4 项不新开对象，只预钉 `Rank 28` 若首判 `keep_P1` 时的唯一 survivor follow-up 边界，防止下一轮又被拖成开放式研究。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明应直升 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-17_1955_strategy-review.md`

## Tail steps
- homepage 刷新：已单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；该进程后续以 `SIGKILL` 结束，按规则记为**非阻断尾部失败**，不影响本轮 review / state rewrite / log 结论。
- 邮件通知：已单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 前排清空后切换 Rank28 intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-17_1955_strategy-review.md`，发送成功。
