# 2026-03-18 13:02 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 主资源切到 Rank 56 liquidation-map path overlay

## 本轮一句话判断
当前 desk 仍然没有席位翻盘：**`Paper Seat = EMA`**、**`Live Seat = 暂空`**。但 `Scout Seat` 不该继续模糊写成“fresh intake”——在 `Rank 55` 已完成 clean replication 且仅剩 `P1` 允许的一次便宜诚实检查后，当前更高边际价值的主资源位应明确切到 **`Rank 56 / liquidation-map path overlay`**；因此 bot3 的下一手不该回头磨旧线，也不该空转，而应按 **`Rank 56 source intake -> 若 guard-passed 则 Rank 56 minimal clean replication；否则用掉 Rank 55 那 1 次时间稳定性检查`** 的顺序推进。

## 0）本轮检查清单
- 已读：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
- 已读：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：`git status --short --branch` 仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮不混提。
- 最近 optimization logs：
  - `2026-03-18_1249_rank55-clean-replication.md`
  - `2026-03-18_1142_rank55-crash-risk-intake.md`
  - `2026-03-18_1135_rank54-clean-replication-park.md`
  - `2026-03-18_1102_rank53-clean-replication-park.md`
- 最近 strategy review：
  - `2026-03-18_1155_strategy-review.md`
  - `2026-03-18_1108_strategy-review.md`
  - `2026-03-18_1021_strategy-review.md`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：正常运行
  - `bot3-momentum-auto-opt-13m`：正常运行
  - `momentum-narrow-paper-lanes-20m`：正常运行
  - `bot7-quant-digest-30m`：当前存在最新 digest（12:55）可供 fresh intake
  - `bot6-park-reframe-2h`：正常运行
- `EMA due guardrail` 当前仍全为 `waiting_not_due`：
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 12:21:57Z`：`new_closed_trades_appended=0`；当前没有新的 `P3 status-changing event` 值得把 bot3 拉回 continuity。

## 1）本轮必须回答的 5 个问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 当前 blocker 仍然只是 market clock，不是漏跑，也不是需要 bot3 停在 continuity 链上反复补文案。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 56` 只是 fresh intake 主候选，连 `source intake + honesty gate` 都还没写回，更不可能直接抢 `Live Seat`；
  2. `Rank 55` 虽已完成最小 clean replication，但当前最诚实 verdict 仍是 **`P1 weak candidate / evidence pool`**，还没到 `P2`；
  3. `Rank 2 / 17 / 29 / 32b` 仍只是 `P3 narrow paper continuity` 托管位，不是新的 live challenger；
  4. 已 bench 的 breakout 不应被硬拖回默认强调位。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：`Rank 56 / liquidation-map path overlay`（fresh repo intake next）**
  - 来源：`aoki-h-jp/py-liquidation-map`
  - 定位：shared path / risk overlay；不是新主 alpha，而是给 `breakout-short / Fib retest_hold / EMA-PSAR` 回答“前方是顺势清算燃料还是逆风清算陷阱更近”。
- **当前 secondary line：`Rank 55 / order-imbalance crash-risk overlay`**
  - 已完成 `source intake -> minimal clean replication`
  - 当前只剩 `P1` 默认允许的 **1 次便宜诚实检查**（优先时间稳定性），用来直接做 `P2 / park`。
- **不应写成 active Scout 主线的对象**：
  - `pullback-quality score / CQI`：repo 很新、`0` stars、原始口径偏 `4H/Daily` long-only，暂只保留为证据池线索；
  - `Rank 35b / Rank 16b`：仍是 queue-only fallback；
  - `Rank 2 / 17 / 29 / 32b`：仍是 `P3 continuity`，不是新的 Scout seat。

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 56 / liquidation-map path overlay`** → **`P1 weak candidate`**（`source intake next / 尚未 guard-passed`）
- **`Rank 55 / order-imbalance crash-risk overlay`** → **`P1 weak candidate`**（`clean replication done / evidence pool / only one cheap honesty check left`）
- **`pullback-quality score / CQI`** → **`P0 evidence / queue-only clue`**（未 admitted）
- **`Rank 35b`** → queue-only fallback / 未重新 admitted
- **`Rank 16b`** → queue-only fallback / 未重新 admitted
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**（只保留 `paper ledger / monitoring / refresh / review` 最小托管）
- 当前 **`P2` 为空，`P4` 为空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**
2. **Run 2 = `Rank 56 / liquidation-map path overlay` 的 `source intake + 两条轻量诚实守门`**（仅当 `EMA` 仍 `waiting_not_due`）
3. **Run 3 = 条件式继续，不写死成旧 fallback**
   - 若 `Rank 56` 已 `guard-passed` 且 `EMA` 仍 `waiting_not_due`：给 **`Rank 56` 1 次最小 clean replication**
   - 若 `Rank 56` intake 硬 fail / exhausted：用掉 **`Rank 55` 那 1 次时间稳定性便宜检查**，直接做 `P2 / park`
   - 只有两者都不成立时，才回退到 **`Rank 35b > Rank 16b > tiny-live plumbing`**

## 2）当前 active Scout 边际价值比较
1. **`Rank 56 / liquidation-map path overlay` 最高**
   - 最新 `12:55` digest 已给出 reader-facing 证据；
   - 公开 `aggTrades` 可快速复刻，不依赖封闭 L2；
   - 它回答的是三条主线共用的“前方路况”问题，比继续在同一种 pullback 打分上加分项更像真正会改 desk judgment 的 shared overlay。
2. **`Rank 55 / order-imbalance crash-risk overlay` 次高**
   - 优点：已过 intake 且做完最小 clean replication；
   - 缺点：setup-level 增量不够统一，当前只够再给 1 次 cheap honesty check，不值得继续长期绑主资源。
3. **`pullback-quality score / CQI` 再次之**
   - 不是完全没价值，而是当前 overlap 太强：它更像已有 `retest_hold / pullback-quality` 思路的 scoring 包装；
   - 同时 repo 太新、社会证明弱、原始口径偏高周期，不该抢在更成熟的 public-data overlay 前面。
4. **`Rank 35b / Rank 16b` 最后**
   - 仍是 derived fallback；
   - 在 fresh repo intake 仍可认领、且 `Rank 55` 也还没完成最终 `P1 -> P2/P0` 分流前，不该抢默认主资源。
5. **`tiny-live plumbing` 继续垫底**
   - 当前 `Live Seat` 默认空席，且没有新 promoted challenger；
   - 只有当 fresh intake 与 existing `P1` 都真 exhausted 时，才轮到它。

## 3）当前 strongest evidence
- `EMA due guardrail` 仍全为 `waiting_not_due`，说明 `Paper Seat` 当前只是被时钟卡住，不是漏跑。
- `Rank 55` 已完成最小 clean replication，并已把自己从 “queue wording” 推进到真正的 `P1 evidence pool`；说明当前不能继续把它写成 source-intake 态。
- `bot7` 在 `12:55 UTC` 已产出新的 repo digest：`liquidation-map path overlay`，说明当前 **fresh intake 并未 exhausted**。
- `manual_narrow_paper_last_run_summary.json @ 12:21:57Z` 仍是 `new_closed_trades_appended=0`，说明当前没有新的 `P3 continuity` 事件值得 bot3 回头抢。

## 4）当前 weakest / should-not-overweight lines
- 最不该高估的是把 `Rank 55` 误写成“已经接近 live challenger”；它还没有跨过 `P1`。
- 同样不该高估的是把 `pullback-quality score / CQI` 直接升级成主资源位；它当前更像弱证据新 repo，而不是现成 fast-lane winner。
- 也不该把 `Rank 2 / 17 / 29 / 32b` 这些 `P3` 托管位重新当成默认 Scout 主线。

## 5）本轮最值得的 Top 3 动作
1. **把 fresh intake 从泛指收紧成 `Rank 56 / liquidation-map path overlay`**，让 bot3 不再在 Run 2 上自由漂移。
2. **保留 `Rank 55` 但只给 1 次便宜诚实检查预算**，并把它明确降成 secondary line，而不是继续绑主资源。
3. **继续维持 `Live Seat = 暂空`**，直到真的有候选走到 `clean replication + 至少一项 truly verdict-changing check` 后再谈升格。

## 6）TODO / 网页 / cron 改动
- **已对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小必要更新。**
- 更新内容：
  - 新增 `2026-03-18 13:02 UTC` 补充；
  - 明确 freeze **`Rank 56 / liquidation-map path overlay`** 为新的 `Run 2` 主资源位；
  - 明确 `Rank 55` 退到 secondary `P1 cheap-check-only`；
  - 明确 `Live Seat` 继续空席。
- 本轮**未改 cron**。

## 7）风险与不确定性
- `Rank 56` 目前还只是 digest 级强线索；source intake 尚未写回前，不能过度宣称它已 `guard-passed`。
- `Rank 55` 下一手若做时间稳定性，必须直接回答 `P2 / park`，不能继续拖在模糊 `P1`。
- 当前工作区脏文件很多；本轮不安全 selective commit。

## 8）执行备注
- 本轮 verdict / reader-facing judgment **有变化**：`Scout Seat` 的默认主资源位已从“泛 fresh intake”收紧为 **`Rank 56`**，且 `Rank 55` 被明确降为 secondary `P1`。
- 因此本轮已同步更新 `TODO` 顶部作战板，后续需刷新首页 index 并发送邮件摘要。
- 未提交 git。
