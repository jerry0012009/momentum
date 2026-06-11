# 2026-03-18 15:11 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 主资源保持 Rank 58 / event-anchored VWAP

## 本轮一句话判断
当前 desk 没有席位翻盘：**`Paper Seat = EMA`**、**`Live Seat = 暂空`**。`Scout Seat` 的主资源位已在 `15:05 UTC` 切到 **`Rank 58 / event-anchored VWAP hold-reclaim spine`**，而且这条线刚完成 `source intake + 两条轻量诚实守门`、当前状态是 **`guard-passed / admit_to_clean_replication_queue`**。因此这轮最诚实的 bot3 排兵不是继续回头磨 `Rank 55/56/57`，也不是挤占 `P3 continuity`，而是：**先继续 `EMA due-check`，若仍 `waiting_not_due`，就立刻给 `Rank 58` 那 1 次最小 clean replication。**

## 0）本轮检查清单
- 已读：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
- 已读：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：`git status --short --branch` 仍有大量与本轮无关的既有脏文件；本轮不混提。
- 最近 optimization logs（最新）
  - `2026-03-18_1505_rank58-source-intake.md`
  - `2026-03-18_1451_rank57-clean-replication-park.md`
  - `2026-03-18_1432_rank57-source-intake.md`
  - `2026-03-18_1348_rank55-time-stability-park.md`
  - `2026-03-18_1342_rank56-clean-replication-p1.md`
- 最近 strategy review
  - `2026-03-18_1349_strategy-review.md`
  - `2026-03-18_1302_strategy-review.md`
  - `2026-03-18_1155_strategy-review.md`
- 当前关键 cron
  - `bot2-strategy-review-40m`：运行中（上一轮 error 但本轮已正常接手巡检）
  - `bot3-momentum-auto-opt-13m`：正常运行
  - `momentum-narrow-paper-lanes-20m`：正常运行
  - `bot7-quant-digest-30m`：15:00 UTC 已补进新的 AVWAP repo digest
  - `bot6-park-reframe-2h`：运行中
- `EMA due guardrail` 当前仍全为 `waiting_not_due`
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-18T14:55:38Z`：`new_closed_trades_appended=0`；当前没有新的 `P3 status-changing event` 值得把 bot3 拉回 continuity。

## 1）本轮必须回答的 5 个问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- blocker 仍只是 market clock，不是漏跑，也不是 narrow-paper continuity 出了新异常。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 58` 现在只是 **`guard-passed / admit_to_clean_replication_queue`**，还没完成最小 clean replication，更没到 `P2 / P3 / P4`；
  2. `Rank 56` 只到 **`P1 weak candidate / evidence pool`**；
  3. `Rank 55` 与 `Rank 57` 都已压回 **`park / evidence pool`**；
  4. `Rank 2 / 17 / 29 / 32b` 仍只是 `P3 narrow paper continuity` 托管位，不是新 live challenger；
  5. 已 bench 的 breakout 仍不应被硬拖回默认强调位。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：`Rank 58 / event-anchored VWAP hold-reclaim spine`**
  - 来源：`s-kust/anchored_vwaps` + `ShabbirHasan1/Anchored_Volume_Weighted_Average_Price`
  - 定位：shared `hold / reclaim` confirmation spine；不是新独立 alpha，而是给 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 回答“这段事件锚定后的新库存成本线有没有被真正守住 / 重新站回”。
- **当前仍在 fresh pool 中、但还没 admitted 的次级候选**
  - `continuation fail-fast overlay`
  - `pullback-quality score / CQI`
- **不应再写成 active Scout 主线的旧候选**
  - `Rank 56 / liquidation-map path overlay` → `P1 weak candidate / evidence pool`
  - `Rank 55 / order-imbalance crash-risk overlay` → `park / evidence pool`
  - `Rank 57 / TTM squeeze release regime gate` → `park / evidence pool`
- **仍不算 Scout 主线的对象**
  - `Rank 2 / 17 / 29 / 32b`：`P3 narrow paper continuity`
  - `Rank 35b / Rank 16b`：queue-only fallback

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 58 / event-anchored VWAP hold-reclaim spine`** → **`P1 weak candidate`**（`guard-passed / clean replication next`）
- **`continuation fail-fast overlay`** → **`P0 evidence / fresh-source queue`**（尚未 admitted）
- **`pullback-quality score / CQI`** → **`P0 evidence / queue-only clue`**（未 admitted）
- **`Rank 56 / liquidation-map path overlay`** → **`P1 weak candidate / evidence pool`**（`clean replication done`）
- **`Rank 55 / order-imbalance crash-risk overlay`** → **`P0 park / evidence pool`**
- **`Rank 57 / TTM squeeze release regime gate`** → **`P0 park / evidence pool`**
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**（只保留 `paper ledger / monitoring / refresh / review` 最小托管）
- 当前 **`P2` 为空，`P4` 为空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**
2. **Run 2 = `Rank 58 / event-anchored VWAP hold-reclaim spine` 的 1 次最小 clean replication**（仅当 `EMA` 仍 `waiting_not_due`）
3. **Run 3 = 条件式继续，不回头默认磨旧线**
   - 若 `Rank 58` clean replication 后仍未给出更高层 verdict：按当前 fresh pool 边际价值继续比较 **`continuation fail-fast overlay > pullback-quality / CQI > fresh pool 其他 source`**
   - 只有 fresh pool 这一层也 exhausted 时，才回退到 **`Rank 35b > Rank 16b > tiny-live plumbing`**

## 2）当前 active Scout 边际价值比较
1. **`Rank 58 / event-anchored VWAP hold-reclaim spine` 最高**
   - 它直接修正了 `Rank 51 / session VWAP` 在 24/7 crypto 上暴露出的 session 任意性；
   - 能同时服务 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 三条主线；
   - 规则已能清楚冻结为 `trade on / trade off`，也没有一眼可判死刑的 `lookahead / repaint / leakage`。
2. **`continuation fail-fast overlay` 次之**
   - 也是 fresh repo clue，但更偏 `exit / distribution shaping`；
   - 当前还没完成 source-intake writeback，因此不该抢在已 guard-passed 的 `Rank 58` 前面。
3. **`pullback-quality score / CQI` 再次之**
   - overlap 较高，更像已有 `retest_hold / pullback-quality` 思路的 scoring 包装；
   - repo 很新、社会证明弱、原始口径偏 `4H/Daily` long-only。
4. **`Rank 56 / 55 / 57` 都应降权**
   - 它们已经在当前允许预算内给出 hard verdict；
   - 再认领这些线，主要只会新增 closeout/措辞，不会继续减少真实 gate。
5. **`tiny-live plumbing` 继续垫底**
   - `Live Seat` 默认空席，且没有新 promoted challenger；
   - 只有 fresh source 这一层也 exhausted 时才轮到它。

## 3）当前 strongest evidence
- `EMA due guardrail` 仍全为 `waiting_not_due`，说明 `Paper Seat` 当前只是被 market clock 卡住，不是漏跑。
- `manual_narrow_paper_last_run_summary.json @ 14:55:38Z` 仍是 `new_closed_trades_appended=0`，说明没有新的 `P3 continuity` 状态变化值得 bot3 回头抢。
- `Rank 58` 已完成 `source intake + 两条轻量诚实守门`，并且其 desk 迁移时最关键的诚实约束（**anchor 类别提前冻结 + signal 当根及之前数据 + next-bar open + no-overlap**）已经写死。
- `Rank 55 / 56 / 57` 已分别落到 `park / evidence pool` 或 `P1 weak candidate / evidence pool`，说明当前 Scout 默认主资源位确实应该前移到新的 fresh source，而不是继续磨旧线。

## 4）当前 weakest / should-not-overweight lines
- 最不该高估的是把 `Rank 58` 过早写成 live challenger；它现在还只是 **`P1 / clean replication next`**。
- 同样不该回头继续磨 `Rank 55 / 56 / 57` 的近义 writeback；这些线当前已经没有最高边际价值。
- 也不该把 `Rank 2 / 17 / 29 / 32b` 这些 `P3` 托管位重新写成新的 Scout seat。

## 5）本轮最值得的 Top 3 动作
1. **维持 `Paper Seat = EMA`，并继续把 `waiting_not_due` 诚实读成“整桌不等、只让 Paper 等”**。
2. **把 bot3 下一手明确钉死到 `Rank 58 minimal clean replication`**，不要再让它自由漂到旧 evidence pool。
3. **继续保持 `Live Seat = 暂空`**，直到真的出现至少完成 `clean replication` 且能继续向 `P2 / P3 / P4` 推进的新候选。

## 6）TODO / 网页 / cron 的改动或建议
- **本轮对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了 1 处最小必要刷新。**
- 改动原因：`Next 3 bot3 runs` 标题下的“当前窗口排班”段落仍停留在 `2026-03-18 06:32 UTC` 的旧窗口文案，容易让 bot3 继续看到早上已过期的排班说明。
- 已更新为当前真实顺序：
  - `Run 1 = EMA due-check only`
  - `Run 2 = Rank 58 minimal clean replication`
  - `Run 3 = continuation fail-fast overlay > pullback-quality / CQI > fresh pool 其他 source；仅在 fresh pool exhausted 时才回退 Rank 35b > Rank 16b > tiny-live plumbing`
- 其余 seat verdict **不变**；本轮**未改 cron**。

## 7）风险与不确定性
- `Rank 58` 当前仍只是 `guard-passed`，clean replication 还没完成；不能过度宣称它已经是 `paper candidate`。
- event-anchored VWAP 最大风险不是公式本身，而是 **anchor 选择自由度**；下一轮 replication 必须优先回答“它是不是只是另一种砍样本的美化器”。
- 当前工作区脏文件很多；本轮不安全 selective commit。

## 8）执行备注
- 本轮核心 seat judgment 与 `15:05 UTC` 相比**没有翻盘**；变化只在于把 TODO 顶板里明显过期的“当前窗口排班”刷新成现在真实顺序，避免 reader-facing / operator-facing 文案继续滞后。
- 后续需刷新首页 index 并发送邮件摘要。
- 未提交 git。
