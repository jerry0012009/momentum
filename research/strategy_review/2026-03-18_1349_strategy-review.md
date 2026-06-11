# 2026-03-18 13:49 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 主资源切到 Rank 57 / TTM squeeze release regime gate

## 本轮一句话判断
当前 desk 仍没有席位翻盘：**`Paper Seat = EMA`**、**`Live Seat = 暂空`**。但 `Rank 55` 已在 cheap time-stability check 后正式压回 `park / evidence pool`，`Rank 56` 也只剩 `P1 weak candidate / evidence pool`，所以 `Scout Seat` 这轮不能继续磨旧 overlay，也不该回头占用 `P3 continuity`；最诚实的主资源位应切到 **`Rank 57 / TTM squeeze release regime gate`** 这条 fresh repo-based 15m 候选。

## 0）本轮检查清单
- 已读：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
- 已读：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：`git status --short` 仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮不混提。
- 最近 optimization logs（最新）
  - `2026-03-18_1348_rank55-time-stability-park.md`
  - `2026-03-18_1342_rank56-clean-replication-p1.md`
  - `2026-03-18_1315_rank56-source-intake-guard-passed.md`
  - `2026-03-18_1249_rank55-clean-replication.md`
- 最近 strategy review
  - `2026-03-18_1302_strategy-review.md`
  - `2026-03-18_1155_strategy-review.md`
- 当前关键 cron
  - `bot2-strategy-review-40m`：正常运行
  - `bot3-momentum-auto-opt-13m`：正常运行
  - `momentum-narrow-paper-lanes-20m`：正常运行
  - `bot7-quant-digest-30m`：13:28 UTC 已产出最新 digest
  - `bot6-park-reframe-2h`：正常运行
- `EMA due guardrail` 当前仍全为 `waiting_not_due`
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 13:43:17Z`：`new_closed_trades_appended=0`；当前没有新的 `P3 status-changing event` 值得把 bot3 拉回 continuity。

## 1）本轮必须回答的 5 个问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 当前 blocker 仍只是 market clock，不是漏跑，也不是 paper continuity 出了新异常。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 57` 现在只是 fresh intake 主候选，连 `source intake + honesty gate` 都还没写回；
  2. `Rank 56` 只到 **`P1 weak candidate / evidence pool`**，尚未通过会改变级别的后续检查；
  3. `Rank 55` 已在唯一 cheap honesty check 后压回 **`park / evidence pool`**；
  4. `Rank 2 / 17 / 29 / 32b` 仍只是 `P3 narrow paper continuity` 托管位，不是新的 live challenger；
  5. 已 bench 的 breakout 不应被硬拖回默认强调位。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：`Rank 57 / TTM squeeze release regime gate`（fresh repo intake next）**
  - 来源：`GiustiRo/squeezem-adx-ttm` + `hackingthemarkets/ttm-squeeze`
  - 定位：shared `avoid-chop / expansion-confirmation` gate；不是新主 alpha，而是给 `breakout-short / Fib retest_hold / EMA-PSAR` 回答“当前还在压缩里乱抖，还是已经完成 squeeze release”。
- **已退出 active fast-lane、只保留证据池身份的前序候选**
  - `Rank 56 / liquidation-map path overlay` → 已完成 `source intake -> minimal clean replication`，当前仅是 `P1 weak candidate / evidence pool`
  - `Rank 55 / order-imbalance crash-risk overlay` → 已完成 `source intake -> minimal clean replication -> cheap time stability`，当前已是 `park / evidence pool`
- **不应写成 active Scout 主线的对象**
  - `pullback-quality score / CQI`：repo 很新、`0` stars、原始口径偏 `4H/Daily` long-only，暂只保留为弱线索
  - `Rank 35b / Rank 16b`：仍是 queue-only fallback
  - `Rank 2 / 17 / 29 / 32b`：仍是 `P3 continuity` 托管，不是新的 Scout seat

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 57 / TTM squeeze release regime gate`** → **`P1 weak candidate`**（`fresh source intake next / 两条轻量诚实守门 pending`）
- **`Rank 56 / liquidation-map path overlay`** → **`P1 weak candidate / evidence pool`**（`clean replication done`）
- **`Rank 55 / order-imbalance crash-risk overlay`** → **`P0 park / evidence pool`**（`cheap time-stability exhausted`）
- **`pullback-quality score / CQI`** → **`P0 evidence / queue-only clue`**（未 admitted）
- **`Rank 35b`** → queue-only fallback / 未重新 admitted
- **`Rank 16b`** → queue-only fallback / 未重新 admitted
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**（只保留 `paper ledger / monitoring / refresh / review` 最小托管）
- 当前 **`P2` 为空，`P4` 为空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**
2. **Run 2 = `Rank 57 / TTM squeeze release regime gate` 的 `source intake + 两条轻量诚实守门`**（仅当 `EMA` 仍 `waiting_not_due`）
3. **Run 3 = 条件式继续，不写死成旧 fallback**
   - 若 `Rank 57` 已 `guard-passed` 且 `EMA` 仍 `waiting_not_due`：给 **`Rank 57` 1 次最小 clean replication**
   - 若 `Rank 57` intake 硬 fail：按 `7.10` 继续从 `quant_digests / RECENT_PAPER_SEEDS / validated shortlist` 再认领 1 条 fresh source
   - 只有 fresh pool 这一层也 exhausted 时，才回退到 **`Rank 35b > Rank 16b > tiny-live plumbing`**

## 2）当前 active Scout 边际价值比较
1. **`Rank 57 / TTM squeeze release regime gate` 最高**
   - `13:28 UTC` digest 刚产出，仍是鲜活的 fresh repo-based 15m 候选；
   - 只依赖现有 OHLCV，复刻成本最低；
   - 它回答的是三条主线共用的“压缩期假动作 / 释放后扩张确认”问题，比继续磨单一 overlay 的边际价值更高。
2. **`pullback-quality score / CQI` 次之，但明显弱于 Rank 57**
   - 不是完全没价值，而是 overlap 太高，更像已有 `retest_hold / pullback-quality` 思路的 scoring 包装；
   - repo 太新、社会证明弱、原始口径偏高周期，不该抢在 `TTM squeeze` 这种更通用、实现更轻的 state gate 前面。
3. **`Rank 35b / Rank 16b` 再次之**
   - 仍是 derived fallback；
   - 在 fresh repo intake 仍可认领的前提下，不该抢默认主资源位。
4. **`Rank 56` 与 `Rank 55` 本轮都应降权**
   - 不是因为完全没证据，而是它们已经分别在允许预算内走完当前该走的 gate；
   - 再继续认领，主要只会增加 closeout/措辞，而不会继续减少真实不确定性。
5. **`tiny-live plumbing` 继续垫底**
   - 当前 `Live Seat` 默认空席，且没有新 promoted challenger；
   - 只有当 fresh intake 与 fallback fresh pool 都真实 exhausted 时，才轮到它。

## 3）当前 strongest evidence
- `EMA due guardrail` 仍全为 `waiting_not_due`，说明 `Paper Seat` 当前只是被时钟卡住，不是漏跑。
- `Rank 56` 已完成最小 clean replication，但 setup-level 改善不统一，因此当前最诚实位置只是 `P1 evidence pool`，不该继续假装它还在 active replication queue。
- `Rank 55` 已完成 cheap time-stability check，并被如实压回 `park / evidence pool`，说明旧 overlay 预算已用尽。
- `bot7` 在 `13:28 UTC` 已补进新的 repo-based 15m digest，说明当前 **fresh intake 并未 exhausted**。
- `manual_narrow_paper_last_run_summary.json @ 13:43:17Z` 仍是 `new_closed_trades_appended=0`，说明没有新的 `P3 continuity` 事件值得 bot3 回头抢。

## 4）当前 weakest / should-not-overweight lines
- 最不该高估的是把 `Rank 56` 误写成“接近 live challenger”；它还只是 `P1 weak candidate / evidence pool`。
- 同样不该继续高估 `Rank 55`；它连唯一 cheap honesty budget 都已经用完。
- 也不该把 `Rank 2 / 17 / 29 / 32b` 这些 `P3` 托管位重新当成默认 Scout 主线。
- `CQI` 仍只适合作为弱线索，不该在当前窗口抢主资源位。

## 5）建议优先级 Top 1~3
1. **把 fresh intake 收紧成 `Rank 57 / TTM squeeze release regime gate`**，让 bot3 的 `Run 2` 不再泛指“再找一条新 source”。
2. **维持 `Live Seat = 暂空`**，直到真的出现完成 `source intake -> clean replication -> 至少 1 个 truly verdict-changing check` 的新候选。
3. **继续把 `P3 continuity` 压在低频托管位**；在 `EMA waiting_not_due` 且 `fresh intake` 仍存在时，不让 bot3 回头做近义 continuity / writeback。

## 6）TODO / 网页 / cron 的改动或建议
- **已对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小必要更新。**
- 更新内容：
  - 新增 `2026-03-18 13:49 UTC` 补充；
  - 明确 `Rank 55` 已 park、`Rank 56` 退到 `P1 evidence pool`；
  - 正式冻结 **`Rank 57 / TTM squeeze release regime gate`** 为新的 `Run 2` 主资源位；
  - 明确 `Live Seat` 继续空席，`P3` 不重回默认主资源。
- 本轮**未改 cron**。

## 7）风险与不确定性
- `Rank 57` 目前还只是 digest 级强线索；source intake 尚未写回前，不能过度宣称它已 `guard-passed`。
- `TTM squeeze` 很容易滑成参数美化或晚确认；后续 replication 必须先回答“减少假启动”而不是“收益看起来更漂亮”。
- 当前工作区脏文件很多；本轮不安全 selective commit。

## 8）执行备注
- 本轮 verdict / reader-facing judgment **有变化**：`Scout Seat` 的默认主资源位已从“fresh intake（泛指）”收紧为 **`Rank 57 / TTM squeeze release regime gate`**，且 `Rank 55` 被明确压回 `park / evidence pool`。
- 因此本轮已同步更新 `TODO` 顶部作战板，后续需刷新首页 index 并发送邮件摘要。
- 未提交 git。
