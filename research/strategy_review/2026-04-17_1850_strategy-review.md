# 2026-04-17 18:50 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-17_1846_rank71_extremeonly_freshintake_background_p0_vwap_anchor_overlap.md`
  - `2026-04-17_1810_rank89_freshintake_background_p0_failurefamily_overlap.md`
  - `2026-04-17_1756_rank27_conditional_freshintake_blocked_stale_replay.md`
  - `2026-04-17_1744_rank60_freshintake_blocked_stale_absorbed_by_rank378.md`
  - `2026-04-17_1713_cycle_plan_no_pending_guard.md`
  - `2026-04-17_1700_rank74_fallback_freshintake_background_p0.md`
- Recent strategy review:
  - `2026-04-17_1801_strategy-review.md`
  - `2026-04-17_1721_strategy-review.md`
  - `2026-04-17_1455_strategy-review.md`
- Park-reframe sources consulted for this rewrite:
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-04-07_0302_rank56-park-reframe.md`
  - `research/park_reframe/2026-04-06_1313_rank83-park-reframe.md`
  - `research/park_reframe/2026-04-07_2055_rank33-park-reframe.md`
  - `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
  - `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
  - `research/park_reframe/2026-04-11_1550_rank57-park-reframe.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 非空，但这些对象都已完成 runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**切到 `Rank 56 / liquidation-map path overlay -> public trigger-cluster approach continuation`。**
   - 原因：`Rank 89 / 71 / 74` 已按顺序收口为 `background/P0`；`Rank 60 / 27` 又被最新 runtime 明确打成 stale replay；当前必须改写成新的合法前排对象，而不是继续复读旧 residual。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得，因为上一条 fresh intake 没有留下新的 `keep_P1`。**
   - 最近实际执行的 fresh-intake 链条是 `Rank 89 -> Rank 71 -> Rank 74`：三者都直接 first verdict 收口 `background/P0`，没有任何对象拿到 survivor 配额。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 one-time `P2->P1 re-scope`，但它已退出 active 槽位，不构成本轮待判对象。

## Rank 合规检查
- 本轮前排对象里不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需补新 `Rank`。

## 关键判断
- 本轮没有待接线 `P3`；也没有 `Active P2` 或 survivor 要收口。
- 因此按 policy，当前必须回到 fresh intake。
- 但 fresh intake 不能继续拿已消费或已被吸收的对象充数：
  - `Rank 60` 已被 `Rank 378` 吸收并接入 `connected_runner_live`；
  - `Rank 27` 已被既有 first verdict 收口，不再是合法未决对象；
  - `Rank 57` 的唯一诚实修改轴已被 `Rank 57b` 消费并回到 `background/P0`；
  - `Rank 28` 当前也没有比既有 `Rank 28b` 更诚实的新一刀，不适合再伪装成新 intake。
- 在剩余可用对象里，`Rank 56` 最具体：主语已经明确压成“旧 15m shared overlay 失败后，只剩 `1m/3m public trigger-cluster approach continuation` 这一个 residual 方向”，比 `Rank 83 / 33` 更像当前应先回答的 fresh intake。
- `Rank 83` 与 `Rank 33` 仍有最小但具体的 residual，可作为预算尾部 conditional intake / fallback；这样既符合默认顺序，也避免把前排重新污染成 stale replay。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- `status = open_pending_first_verdict`
- `current_target = research/park_reframe/2026-04-07_0302_rank56-park-reframe.md`
- `source_record` 同步切到 `Rank 56`
- `latest_result` 明确写回：`Rank 89 / 71 / 74` 本轮已诚实收口，因此当前必须切到新的合法 intake

### Surviving candidate slot
- 保持 `none`

### Active P2 slot
- 保持 `none`

### cycle_plan
1. `Rank 56` fresh intake first-verdict
2. `Rank 83` conditional fresh intake
3. `Rank 33` conditional cheap fallback fresh intake
4. `Rank 56` conditional survivor guardrail（仅当 item1=`keep_P1` 时触发）

## 为什么本轮这样排
- policy 明确要求：只有在 `P3 / P2 / P1` 前排链条都诚实收口后，才切回新的 fresh intake；当前这一前提成立。
- 同时，policy 也明确要求：新的 intake 必须是**具体对象**，不能写抽象模板。
- `Rank 56` 比 `Rank 83 / 33` 更前，是因为它的 residual 主语最具体、最接近一个真正可判的 queue-facing first verdict；而 `Rank 83 / 33` 目前更像 distinctness 检查题，适合作为条件尾部预算。
- 第 4 项不新开对象，只预钉 `Rank 56` 如果首判 `keep_P1` 时的唯一 survivor follow-up 边界，防止下一轮再把它拖成开放式研究。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明应直升 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Tail steps
- homepage 刷新：按要求作为独立命令 best-effort 执行；失败视为非阻断尾部失败。
- 邮件通知：无论 publish 是否成功，均继续单独执行中文邮件摘要发送。
