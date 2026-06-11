# 2026-03-19 03:20 UTC strategy review

## 轮次定位
- 时间：2026-03-19 03:20 UTC
- 任务：bot2 交易 desk 统揽 / 排兵布阵巡检
- 目标：维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，明确当前 `Paper / Live / Scout` 三席与接下来 `Next 3 bot3 runs`

## 开始前检查
### 1) repo 状态
- `git status --short --branch`：当前仍在 `master`
- `git status --short | wc -l`：当前约 **1245** 条脏文件/未跟踪项，绝大多数与本轮无关
- 本轮继续只做最小必要改动：`docs/TODO.md` 顶部 desk board、strategy review 记录、首页 index 刷新、邮件摘要发送

### 2) 最近 optimization logs / fresh evidence
- `2026-03-19_0258_rank76-clean-replication.md`
  - `Rank 76 / intraday clock polarity + event blackout gate` 已给出 **`park / evidence pool`**
- `2026-03-19_0315_rank77-alt-btc-rs-intake.md`
  - `Rank 77 / alt-vs-BTC RS breadth shared gate` 已完成 `source intake + 两条轻量诚实守门`，当前是 **`guard-passed / admit_to_clean_replication_queue`**
- `2026-03-19_0316_trendln-paired-channel-breach-gate.md`
  - 这是一条可读的 repo-based 证据补充，但当前与已 `park` 的 `Rank 30 / trendln paired-channel breach / corridor breakout gate` 语义高度重合；在没有明确不同 `trade on / trade off` 与 clean-room 口径之前，不应误写成新的 active Scout seat

### 3) 最近 strategy review
- 最近 bot2 review：
  - `2026-03-19_0226_strategy-review.md`
  - `2026-03-19_0146_strategy-review.md`
- 与上一轮相比，本轮核心席位判断**不变**：`Paper Seat = EMA`、`Live Seat = 暂空`
- 本轮真正要收紧的，是 `Scout Seat` 的预算纪律：`Rank 77` 已经走到 `P1 / guard-passed`，默认应先给它那 1 次最小 clean replication，而不是又切回新的 fresh intake

### 4) 当前 cron 列表（与 desk 直接相关）
- `bot2-strategy-review-40m`：启用，当前运行中
- `bot3-momentum-auto-opt-13m`：启用，上一轮 `ok`
- `momentum-narrow-paper-lanes-20m`：启用，上一轮 `ok`
- `bot7-quant-digest-30m`：启用，上一轮 `ok`
- `bot6-park-reframe-2h`：启用，上一轮 `ok`
- 结论：当前排兵布阵不需要改 cron；仍按现有 cron 结构执行即可

## 当前关键证据
### Paper Seat / market clock
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 当前全 desk 仍无 `due-now / overdue` lane
  - 最近 due 点：`A股三条 lane -> 2026-03-19 07:00 UTC`
  - 之后是：`美股 1d+1wk -> 2026-03-19 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-20 00:00 UTC`
- 结论：`EMA` 当前是**真实 `running paper / waiting_not_due`**，不是 desk 空闲

### P3 continuity
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T02:46:36Z`
  - `new_closed_trades_appended = 0`
- 结论：当前没有新的 `P3 status-changing event`；`Rank 2 / 17 / 29 / 32b` 继续只是托管位，不应抢占 bot3 默认主资源

### Active Scout 候选边际价值重排
本轮显式比较当前仍有意义的 active Scout 候选：
1. **`Rank 77 / alt-vs-BTC RS breadth shared gate`**
   - 已到 `P1 / guard-passed`
   - 离真实升降级判断最近
   - 同时服务 `breakout-short / Fib retest_hold / EMA-PSAR`
2. **`adaptive no-trade band / EMA cost survival`**
   - 仍有价值，但更偏 `EMA / PSAR` 单线成本生存层
   - 当前只算 `P0 fresh-paper queue / not admitted`
3. **`one-regime-per-session overlay`**
   - 更像 desk-level allocation overlay
   - 当前只算 `P0 evidence / backlog`
4. `Rank 35b`
5. `Rank 16b`
6. `tiny-live plumbing`

额外说明：
- `2026-03-19 03:16 UTC / trendln paired-channel breach + reclaim-hold` digest 当前**不重开** fast lane；它更像对已 `park` 的 `Rank 30` 补证，不应误写成新的 active Scout 候选

## 本轮 desk verdict
### 1. 谁坐 `Paper Seat`？
- **`EMA` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 口径：最近 due 点仍是 `A股 07:00 UTC`，所以这是 `market clock blocked`，不是 desk 空闲

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 77` 还没做最小 clean replication，更没有完成 `Light Stability Pack`
  2. `Rank 76 / 75 / 74 / 73 / 72 / 30` 都已是 **`P0 park / evidence pool`**
  3. `Rank 2 / 17 / 29 / 32b` 仍只是 `P3 narrow paper continuity` 托管位，不应误写成 live challenger

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 active queue-facing 主资源位**：
  - `Rank 77 / alt-vs-BTC RS breadth shared gate`
- **当前保留为下一手 fresh paper 线索 / backlog**：
  - `adaptive no-trade band / EMA cost survival`
  - `one-regime-per-session overlay`
- **只作证据补充、不自动重开 active seat**：
  - `trendln paired-channel breach + reclaim-hold` digest（与已 `park` 的 `Rank 30` 高度重合）
- **只有 fresh source 也 exhausted 时才允许回退**：
  - `Rank 35b`
  - `Rank 16b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 77 / alt-vs-BTC RS breadth shared gate` → **`P1`**（`guard-passed / minimal clean replication next`）
- `adaptive no-trade band / EMA cost survival` → **`P0`**（`fresh-paper queue / not admitted`）
- `one-regime-per-session overlay` → **`P0`**（`evidence / backlog`）
- `Rank 76 / 75 / 74 / 73 / 72 / 30` → **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` → **`P3`**（`narrow paper continuity / low-frequency health check only`）
- 当前 **`P2` 暂空、`P4` 暂空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check only**
   - 继续盯 due guardrail；若仍 `waiting_not_due`，不得空转
2. **Run 2 = 若 EMA 仍 waiting_not_due，则给 `Rank 77 / alt-vs-BTC RS breadth shared gate` 做 1 次最小 clean replication**
   - 默认优先比较 `24h vs 8h breadth` 变体
   - 统一保持 `signal 当根及之前数据 + next-bar open + no-overlap`
3. **Run 3 = 若 `Rank 77` clean replication 没有出现 decisive fail，则只再给它 1 个 truly verdict-changing 的 `Light Stability Pack`（默认优先时间稳定性），并直接做 `P2 / park` 判断；若 `Rank 77` 直接 park，则回到 `adaptive no-trade band > one-regime-per-session overlay > fresh pool 其他 source`；只有 fresh source 这一层也 exhausted 时，才允许回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 为什么这轮要这样收紧
- `Rank 77` 已经走到 `P1 / guard-passed`，按当前预算纪律，默认不该再让 fresh intake 插队；应先用那 1 次便宜诚实检查把它推向 **`P2 / paper candidate` 或 `park`**
- `trendln` 新 digest 虽然可读，但当前更像对 `Rank 30` 的补证，而不是新 seat；若把它当成新 active 候选，会稀释当前 queue-facing 主资源位
- `Paper Seat` 当前没有真实 due-now 动作，`P3` 也没有 status-changing event，所以 bot3 仍应继续优先服务 `Scout Seat`

## 对 TODO 顶部作战板的最小必要更新
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
1. 新增 `2026-03-19 03:20 UTC` 的 bot2 desk-review 补充
2. 明确 `trendln paired-channel breach + reclaim-hold` 目前只算对 `Rank 30` 的证据补充，不自动重开 active Scout seat
3. 把 `Run 3` 收紧成：若 `Rank 77` 未 hard-fail，则优先做 1 个真正会改变 verdict 的 `Light Stability Pack`，直接逼出 `P2 / park` 判断

## Reader-facing / publish
- 本轮 verdict 大方向未翻桌，但 **reader-facing judgment 有收紧**：
  - `Scout Seat` 继续由 `Rank 77` 占 queue-facing 主资源位
  - `Run 3` 不再默认立刻切回 fresh intake，而是优先用 1 个真正会改变 verdict 的检查逼出 `Rank 77` 的 `P2 / park` 判断
  - `trendln 03:16 digest` 明确不重开已 `park` 的 `Rank 30`
- 因此本轮已同步写回 `docs/TODO.md` 顶板，并将刷新首页 index

## 提交
- 未提交
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，避免混提
