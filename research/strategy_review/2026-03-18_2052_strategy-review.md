# 2026-03-18 20:52 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 切到 Rank 67 / Rank 68 fresh-source 队列

## 本轮一句话判断
当前 desk verdict **不翻盘**：**`Paper Seat = EMA`**、**`Live Seat = 暂空`**、而 `Scout Seat` 当前主资源位应从已经消耗完默认 clean-replication 预算的 `Rank 66` 移开，切到 **`Rank 67 / regime-matrix shared-state gate`**；同时把 `2026-03-18 20:24 UTC` 的新 repo digest 正式冻结为 **`Rank 68 / block-mitigation retest score`**，作为 `Rank 67` 若 hard-fail 后立刻接手的下一条 fresh-source 候选。

## 0）本轮检查清单
- 已读：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
- 已读：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 已检查 repo 状态：`git status --short --branch` 仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮不混提
- 最近 optimization logs（最新）
  - `2026-03-18_2050_rank66-clean-replication.md`
  - `2026-03-18_2029_rank66-source-intake-guard-passed.md`
  - `2026-03-18_2002_ema-us-due-refresh.md`
  - `2026-03-18_2018_rank65-clean-replication-park.md`
- 最近 strategy review
  - `2026-03-18_2004_strategy-review.md`
  - `2026-03-18_1909_strategy-review.md`
- 最近 quant digest（本轮 active fresh-source 对比所需）
  - `2026-03-18_2024_block-mitigation-retest-score.md`
  - `2026-03-18_1845_perp-stress-reset-complete-rearm-gate.md`
  - `2026-03-18_1730_exec-tf-switch-alignment-gate.md`
  - `2026-03-18_1707_regime-matrix-shared-state-gate.md`
- 当前关键 cron
  - `bot2-strategy-review-40m`：本轮运行中
  - `bot3-momentum-auto-opt-13m`：正常运行
  - `momentum-narrow-paper-lanes-20m`：正常运行
  - `bot7-quant-digest-30m`：正常运行
  - `bot6-park-reframe-2h`：正常运行
- 当前 `EMA due guardrail`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC / waiting_not_due`
  - 美股 `1d+1wk -> 2026-03-19 20:00 UTC / waiting_not_due`
- 当前 `P3 continuity`
  - `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-18T20:29:10Z`
  - `new_closed_trades_appended = 0`
  - 当前没有新的 `P3 status-changing event` 值得 bot3 回头抢主资源

## 1）本轮必须回答的 5 个问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due（Crypto lane due_soon）`**。
- 证据：`20:02 UTC` 已真实消化美股 due window；当前最新 due guardrail 里不再有 `due-now / overdue` lane，最早只剩 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 66` 这轮最小 clean replication 后只落到 **`P1 weak candidate / evidence pool`**，还不能升成 live challenger；
  2. `Rank 67 / Rank 68` 当前都还只是 **`P0 fresh-source queue / not admitted`**；
  3. `Rank 2 / 17 / 29 / 32b` 仍是 `P3 narrow paper continuity` 托管位，不应误写成 live 候选；
  4. 已 park 的 `Rank 64 / 65` 不应回桌抢占 live 叙事。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位**：`Rank 67 / regime-matrix shared-state gate`
  - 来源：`damianpitt/capital41-indicators`
  - 定位：`Trend / Expansion / Compression / Mean Reversion` 的 shared allow/deny state gate
  - 当前阶段：**`fresh source intake / 两条轻量诚实守门 next`**
- **当前第一后备**：`Rank 68 / block-mitigation retest score`
  - 来源：`saintmexas/trading-scripts`
  - 定位：用 `block length + mitigation zone` 给 `breakout-short / Fib / EMA` 一个更便宜的 shared retest-quality skeleton
  - 当前阶段：**`fresh source intake / 两条轻量诚实守门 next`**
- **当前不应继续写成 active fast-lane 主线的对象**
  - `Rank 66 / exec-TF switch alignment gate`：已完成允许预算内的最小 clean replication，当前只保留 **`P1 weak candidate / evidence pool`**
  - `Rank 65 / 64`：已 `park / evidence pool`
  - `Rank 2 / 17 / 29 / 32b`：`P3 narrow paper continuity`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 67 / regime-matrix shared-state gate`** → **`P0 fresh-source queue / not admitted`**
- **`Rank 68 / block-mitigation retest score`** → **`P0 fresh-source queue / not admitted`**
- **`Rank 66 / exec-TF switch alignment gate`** → **`P1 weak candidate / evidence pool`**
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**
- 当前 **`P2` 为空，`P4` 为空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**（继续盯 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`）
2. **Run 2 = 若 `EMA` 仍 `waiting_not_due`，先给 `Rank 67 / regime-matrix shared-state gate` 做 `source intake + 两条轻量诚实守门`**
3. **Run 3 = 若 `Rank 67` 已 `guard-passed` 且 `EMA` 仍 `waiting_not_due`，立刻给它 1 次最小 clean replication；若 `Rank 67` 直接 hard-fail / 未 admitted，则立刻切到 `Rank 68 / block-mitigation retest score` 做 fresh source intake；只有这层也 exhausted 时，才回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 2）当前 active Scout 边际价值比较（必须显式比较）
1. **`Rank 67 / regime-matrix shared-state gate` 当前最高**
   - 仍是 paper/repo based，且只需公开 `15m/30m OHLCV` 就能做最小 intake；
   - 它直接回答三条主线共同缺的“什么时候该做 / 什么时候别做”的 shared allow/deny layer；
   - 相对刚 park 的 `Rank 64 / pullback-quality score gate`，它更不容易马上又滑回“靠过度切样本才看起来变好”的近邻轨道。
2. **`Rank 68 / block-mitigation retest score` 第二**
   - 也是低摩擦 repo source，而且直接服务 `breakout-short / Fib / EMA`；
   - 但它和刚 park 的 `pullback-quality / retest-quality` 家族更近，因此当前更适合做 `Rank 67` hard-fail 后立刻接手的下一条 queue-facing 候选，而不是直接跳过 `Rank 67` 抢主资源。
3. **`Rank 35b` 第三、`Rank 16b` 第四**
   - 都仍是 derived fallback，不该在 fresh repo 队列尚有对象时抢主资源。
4. **`tiny-live plumbing` 继续最末位**
   - 当前没有新的 promoted live challenger，也没有理由让它高过 fresh paper/repo intake。

## 3）当前 strongest evidence
- `Paper Seat / EMA` 的 `20:00 UTC` due window 已在 `20:02 UTC` 被真实消化；当前最新 due guardrail 里已无 `due-now / overdue` lane。
- `manual_narrow_paper_last_run_summary.json @ 20:29:10Z` 仍是 `new_closed_trades_appended=0`，说明 `P3 continuity` 当前没有 status-changing event。
- `Rank 66` 的最小 clean replication 已明确证明：`alignment_switch` 没有稳定赢过更便宜的 `always_5m_confirm` 对照臂，因此它当前更诚实的 desk 读法只能是 **`P1 weak candidate / evidence pool`**，不该继续霸占 fast-lane 队首。
- `2026-03-18 20:24 UTC` 的新 repo digest 已提供合格 fresh-source，所以当前不应把 `Run 3` 过早写成 tiny-live fallback。

## 4）当前 weakest / should-not-overweight lines
- 最不该做的是把 `Rank 66` 误写成“已接近 live / 已值得继续连打”的候选；它这轮并没有升层。
- 也不该因为 `EMA` 进入 `due_soon` 就提前把整个 desk 写成等待态；当前还远没到 `00:00 UTC` 的真实 due-now。
- 同样不该回头重炒 `Rank 64 / 65`；它们已经在允许预算内给出更诚实的 `park` verdict。
- `Rank 2 / 17 / 29 / 32b` 继续只是 `P3` 托管 continuity，不是新的 seat。

## 5）本轮最值得的 Top 3 动作
1. **先把 `Rank 67 / regime-matrix shared-state gate` 的 source intake + 两条轻量诚实守门做完，并直接给出 `guard-passed / park`。**
2. **若 `Rank 67` 不成立，立刻切到 `Rank 68 / block-mitigation retest score`，不要在 generic fresh-pool wording 上继续打转。**
3. **继续保持 `Live Seat = 暂空`，直到出现至少一个完成 clean replication 且没有硬爆雷的候选。**

## 6）TODO / 网页 / cron 的改动或建议
- **本轮对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了最小必要刷新。**
- 已同步：
  - 新增 `2026-03-18 20:52 UTC` 的 bot2 desk-review 补充；
  - 正式冻结 **`Rank 68 / block-mitigation retest score`**；
  - 把 current active Scout 顺序收紧为 **`Rank 67 > Rank 68 > Rank 35b > Rank 16b > tiny-live plumbing`**；
  - 把 `Next 3` 改写成 **`Rank 67 source intake -> Rank 67 minimal clean replication / or Rank 68 intake -> fallback`** 的口径。
- 本轮**未改 cron**。
- 本轮应同步刷新 `reports/site/plans/momentum_todo.html` 与首页 index。

## 7）风险与不确定性
- `Rank 67` 当前仍只是 quant-digest 级 fresh-source，尚未过第一轮两条轻量诚实守门；它现在是更高边际价值的 next candidate，不是已验证候选。
- `Rank 68` 虽然更直接服务 breakout / Fib / EMA，但它与刚 park 的 retest-quality 家族相邻较近；若 source intake 一开始就发现核心增量还是靠样本稀释，它也应快速 park。
- 工作区仍有大量无关脏文件 / 未跟踪文件，本轮不安全 selective commit。

## 8）执行备注
- 本轮席位判断**无变化**，但 `Scout Seat` 的 queue-facing 口径更完整了：从“`Rank 67` 后若失败再 generic fresh source”收紧成 **`Rank 67 -> Rank 68`** 的编号顺序。
- 因此本轮已同步更新 `TODO` 顶部作战板；接下来刷新 `plans/momentum_todo.html`、首页 index，并发送邮件摘要。
- 未提交 git。
