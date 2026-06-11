# 2026-04-19 02:34 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short --branch`
- Recent optimization loop:
  - `2026-04-19_0209_rank424_cointegration_spreadfade_freshintake_keep_p1.md`
  - `2026-04-19_0154_rank423_survivor_followup_promote_p2_entry_realism.md`
  - `2026-04-19_0130_rank422_p3_connected_runner_live.md`
- Recent strategy review:
  - `2026-04-19_0132_strategy-review.md`
  - `2026-04-19_0043_strategy-review.md`

## Repo status snapshot
- 当前 repo 没有新的 runtime truth 冲突；主要是大量历史 `tmp/` 与工作文件未跟踪，未构成前排排班依据。
- 最近 optimization loop 已明确两件事：
  1. `Rank 423` 已完成 survivor 唯一 follow-up，并从 `P1` 升到 `Active P2`
  2. `Rank 424` 已完成 fresh intake 首判，并锁定 survivor 唯一 follow-up 槽位

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - **是，非空。**
   - 理由：`connected_runner_live` 列表明确非空，且 `Rank 422` 已完成 runner + scheduler + 首跑验证并写回 runtime。

2. 本轮 `fresh intake` 是什么？
   - **`Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`。**
   - 理由：它是当前 `Fresh intake slot` 里的最新对象，并且已经首判为 `keep_P1`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - **值得。**
   - 理由：`Rank 424` 已经把首判的唯一剩余 blocker 收敛到很具体的 `formal pair admission / break-risk`，而不是泛泛“再补点证据”。按 policy，它应享有 survivor 槽位锁定权，直到这唯一一次 follow-up 被诚实消费掉。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - **存在：`Rank 423 / liquidation shock × OI unwind -> 30m exhaustion fade`。**
   - **它当前离 `P3` 最近。**
   - 理由：最近日志已经说明更诚实的 delay / micro-confirm 检查没有打穿核心 pocket，当前最像样的 scope 是 `BTC/SOL/XRP core`，`ETH/ADA` 只需作为 watch / optional。它现在缺的不是再来一轮开放式研究，而是一轮直接回答 `promote_P3 / drop / one-time re-scope` 的 P2 admission / exit decision。

## Rank 合规检查
- `Paper launch queue`、`Fresh intake slot`、`Surviving candidate slot`、`Active P2 slot` 当前对象都已带正式 Rank。
- 本轮未发现前排对象缺 rank，因此无需补号。

## 排班判断
按 policy 默认顺序，本轮前排真实动作应为：
1. **先处理 `Active P2` 的出口决策**：`Rank 423` 已不该继续停在开放式 `keep_P2`；应直接回答是否足够进入 `P3 / Paper launch queue`。当前 desk review 口径下，它明显更接近 `P3`，所以第 1 项必须是 P2 admission / exit decision。
2. **再处理 survivor 唯一 follow-up**：`Rank 424` 已锁定 survivor 槽位，不能被新 intake 覆盖；因此第 2 项必须是它的唯一一次 follow-up。
3. **前排诚实收口后，才切回新 intake**：保留 `intraday extreme return router` 作为主 fresh intake，`retail-chasing proxy` 作为 conditional fresh intake。

## P2 -> P3 兜底裁判检查
- 本轮**暂不直接把 `Rank 423` 改写进 `P3 / Paper launch queue`**。
- 原因不是它不强，而是当前 runtime 证据仍主要来自 survivor follow-up + entry realism；还缺一轮明确的 `P2 admission / exit decision` 来同时回答：
  - `BTC/SOL/XRP core` 的 alpha 是否仍成立
  - 是否还存在单一 decisive honesty / execution blocker
- 但注意：**这已经是出口轮，不是开放式继续研究轮。** 若 bot3 下一轮 admission 结论继续支持当前 core scope，就应直接 `promote_P3`，不得再拖成第三种暧昧状态。

## State rewrite
本轮只重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
1. `Rank 423`：P2 admission / exit decision，直接回答 `promote_P3 / drop / 唯一明确 re-scope`
2. `Rank 424`：survivor 唯一 follow-up，直接回答 `promote_P2 / background`
3. `2026-04-19_0016_intraday-extreme-return-router-alpha.md`：fresh intake
4. `2026-04-18_2328_crypto-retail-chasing-continuation-alpha.md`：conditional fresh intake

这样重排后满足：
- 没有把新的 intake 排到已有前排对象前面
- 没有让新的 `keep_P1` 覆盖 survivor 槽位
- 没有把 background pool 旧候选拉回前排
- 把 `Rank 423` 明确排成**出口决策轮**而不是泛泛 `keep_P2`

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-19_0234_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
2. 中文邮件摘要（独立执行，不与 publish 链式拼接）：
   - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank423转出口轮 Rank424锁定跟进" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-19_0234_strategy-review.md`
