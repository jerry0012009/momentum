# 2026-03-18 11:55 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 仍由 Rank 55 拿主资源

## 本轮一句话判断
当前 desk **没有席位翻盘**：**`Paper Seat = EMA`**、**`Live Seat = 暂空`**、**`Scout Seat = Rank 55 / order-imbalance crash-risk overlay`**。这轮最重要的不是再改板，而是维持当前权威判断：`EMA` 仍是 `waiting_not_due`，所以 bot3 下一手应继续按 **`Rank 55 最小 clean replication`** 往前推；若 replication 不爆雷，再给它 **1 个 truly verdict-changing 的 `Light Stability Pack`**，否则再回退到 `Rank 35b > Rank 16b > tiny-live plumbing`。

## 0）本轮状态检查
- 已读：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
- 已读：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：`git status --short --branch` 仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮不做混提。
- 最近 optimization logs：
  - `2026-03-18_1142_rank55-crash-risk-intake.md`
  - `2026-03-18_1135_rank54-clean-replication-park.md`
  - `2026-03-18_1104_rank54-source-intake-guard-passed.md`
  - `2026-03-18_1102_rank53-clean-replication-park.md`
- 最近 strategy review：
  - `2026-03-18_1108_strategy-review.md`
  - `2026-03-18_1021_strategy-review.md`
  - `2026-03-18_0925_strategy-review.md`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：正常运行
  - `bot3-momentum-auto-opt-13m`：正常运行
  - `bot7-quant-digest-30m`：正常运行
  - `momentum-narrow-paper-lanes-20m`：正常运行
  - `bot6-park-reframe-2h`：正常运行
- `EMA due guardrail` 当前仍全是 `waiting_not_due`：
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 11:39:48Z`：`new_closed_trades_appended=0`；当前没有新的 `P3 status-changing event` 值得把 bot3 拉回 continuity。

## 1）本轮必须回答的 5 个问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 这意味着 bot3 的 `Run 1` 仍只能是 **`due-check only`**，不能伪造 refresh，也不能把 desk 一起拖进等待。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 55` 目前只到 **`P1 weak candidate（guard-passed / admit_to_clean_replication_queue）`**，还没走完 `clean replication`；
  2. `Rank 54 / 53 / 52 / 51 / 50` 都已在允许预算内给出 hard verdict 并压回 `park / evidence pool`；
  3. `Rank 2 / 17 / 29 / 32b` 虽属 `P3 narrow paper continuity`，但不是当前可直接升为 tiny-live challenger 的新 seat。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前唯一 active Scout 候选是：`Rank 55 / order-imbalance crash-risk overlay`。**
- 它来自 fresh paper source：`Koutmos & Wei (2023) / Nowcasting bitcoin’s crash risk with order imbalance`。
- 当前不是多条并行 replication：
  - `Rank 55` 拿主资源位；
  - `Rank 35b`、`Rank 16b` 仅保留 queue-only fallback；
  - `Rank 2 / 17 / 29 / 32b` 继续只算 `P3 continuity` 托管，不抢当前 Scout seat。

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 55 / order-imbalance crash-risk overlay`** → **`P1 weak candidate`**（`guard-passed / admit_to_clean_replication_queue`）
- **`Rank 35b`** → queue-only fallback / 未重新 admitted
- **`Rank 16b`** → queue-only fallback / 未重新 admitted
- **`Rank 54 / 53 / 52 / 51 / 50`** → **`P0 park / evidence pool`**
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**（仅保留 `paper ledger / monitoring / refresh / review` 最小托管）
- 当前 **`P2` 为空，`P4` 为空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**
2. **Run 2 = `Rank 55 / order-imbalance crash-risk overlay` 的最小 clean replication**（仅当 `EMA` 仍 `waiting_not_due`）
3. **Run 3 = 条件式继续，不预先写死成纯 fallback**
   - 若 `Rank 55` clean replication **没被判死刑**：只给它 **1 个 truly verdict-changing 的 `Light Stability Pack`**（默认优先 `时间稳定性`，并直接做 `P2 / park` 判断）
   - 若 `Rank 55` clean replication **失败 / exhausted**：再回退到 **`Rank 35b > Rank 16b > tiny-live plumbing`**

## 2）当前 active Scout 边际价值比较
- **`Rank 55` 最高**：fresh paper-based、shared risk overlay、直接服务 `breakout-short / Fib retest_hold / EMA-PSAR` 三条主线，而且比继续磨 `Rank 35b / 16b` 更像真正会改变 desk judgment 的新 gate。
- **`Rank 35b` 次之**：只是 derived fallback，不该在 fresh paper 主资源位仍活着时抢前排。
- **`Rank 16b` 再次之**：同样是 fallback，而且和近期已被证明更像 sample-cut / execution veto 的轴更相邻。
- **`tiny-live plumbing` 最后**：当前 `Live Seat` 仍空，且没有新 promoted challenger，不该抢在 fresh Scout 前面。

## 3）strongest evidence
- `EMA due guardrail` 仍全为 `waiting_not_due`，证明 `Paper Seat` 当前只是被 market clock 卡住，而不是漏跑。
- `Rank 55` 已通过两条轻量诚实守门：`trade on / trade off` 能冻结，且已明确它只是 shared risk overlay，不是偷换成 15m 逐根主 alpha。
- `manual_narrow_paper_last_run_summary.json @ 11:39:48Z` 仍是 `new_closed_trades_appended=0`，说明本轮没有真实 `P3 continuity` 事件值得 bot3 抢回去做。

## 4）weakest / should-park lines
- 最不该再高估的是把 `Rank 54 / 53 / 52 / 51 / 50` 假装写成还在 active queue 的候选；它们都已给出 hard verdict。
- 同样不该误写的是把 `Rank 2 / 17 / 29 / 32b` 这些 `P3` 托管位重新当成默认 Scout 主资源。

## 5）建议优先级 Top 1~3
1. **先维持 `Run 1 = EMA due-check only` 的纪律**，不要伪造 paper continuation。
2. **给 `Rank 55` 仅 1 次最小 clean replication**，先回答它能否以 shared crash-risk overlay 方式改善成本后表现 / 回撤 / false-hold，而不是继续 intake 讲故事。
3. **若 `Rank 55` 存活，就立刻做 1 个最小 `Light Stability Pack`；若不存活，就快速回退 `Rank 35b > Rank 16b > tiny-live plumbing`**，不要停在模糊研究态。

## 6）TODO / roadmap / web / cron 的改动或建议
- **这轮未改 `docs/TODO.md`**。
- 原因：`TRADING DESK BOARD` 顶部在 `2026-03-18 11:42 UTC` 的写回仍然是当前最诚实、且已覆盖本轮 judgment 的 authoritative 版本；当前没有新的 seat flip、没有新的 active candidate 变化，也没有新的 reader-facing verdict 需要再追加一次近义补丁。
- **这轮未改 cron**。

## 7）风险与不确定性
- `Rank 55` 论文主问题是 BTC crash nowcast，不是 15m 逐根入场；clean replication 时必须坚持它只是 overlay / gate，不得偷换成新主 alpha。
- 若 `Rank 55` 的改善主要来自极端砍样本或只对单一币种有效，就应快速压回 `park / evidence pool`。
- 当前工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，因此本轮不安全 selective commit。

## 8）执行备注
- 本轮属于**无变更巡检**：席位判断与顶板排班保持不变。
- 已产出本轮 `strategy_review` 记录；下一步仅刷新首页 index 并发送邮件摘要。
- 未提交 git。
