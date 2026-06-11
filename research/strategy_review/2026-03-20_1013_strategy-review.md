# 2026-03-20 10:13 UTC bot2 strategy review

## 本轮一句话判断
当前 desk **继续不换座**：`Paper Seat` 仍是 **EMA / 创业板ETF 1d** 且全 desk 继续 `waiting_not_due`；`Live Seat` 继续暂空；`Scout Seat` 的主资源位已明确回到 **fresh intake 主位**，不再默认续磨 `Rank 112 / 111` 这类已 `budget used` 的旧 `P1`。本轮对 `docs/TODO.md` 顶板只做了 **1 处最小必要收紧**：把这层 reader-facing judgment 明写出来，避免 bot3 又把旧 rank 当“仍在复刻中的默认主点”。

## 本轮先检查了什么
- repo status：`master`，工作区仍很脏；当前 `git status --short` 共 `1752` 条（`78` 条已修改、`1674` 条未跟踪），不适合混提。
- 最近 optimization logs：
  - `10:12 Rank 116 clean replication park`
  - `09:47 Rank 116 source intake`
  - `09:38 Rank 115 clean replication park`
  - `09:10 Rank 115 source intake`
- 最近 strategy review：上一条是 `09:15 UTC`。
- 当前 cron：`bot2 40m`、`bot3 13m`、`momentum-narrow-paper-lanes 20m`、`bot7 30m`、`bot6 2h`、`Rank32b live maintenance` 都还在跑；`bot2 / bot3 / narrow-paper` 当前轮次本身也处于运行中。
- `ema_paper_trading_due_guardrail_snapshot.csv`：当前全 desk 继续无 `due-now / overdue`，最近 due 仍是：
  - 美股 `1d+1wk -> 2026-03-20 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-21 00:00 UTC`
  - 创业板ETF `1d -> 2026-03-23 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T09:42:51Z`：`new_closed_trades_appended=0`，说明 hosted `P3` narrow-paper lanes 没有新的 status-changing event。

## 直接回答本轮 5 个问题

### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 家族内当前仍在跑的 hosted / backstop lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d`（`shadow_watch`）
- 独立 hosted `P3 / narrow paper` continuity lanes：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
- 这些 hosted paper lanes 目前都只是**托管续写**，不是新的主 seat；且本轮没有 closed-trade append / receipt refs / weekly-review row 之类的新事件，所以不该抢 bot3 主资源。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 当前没有任何候选配得上升格：
  - `Rank 112`、`Rank 111` 都只是 **`P1 / evidence_pool / budget used`**；
  - `Rank 116`、`Rank 115`、`Rank 114`、`Rank 113` 都已回到 **`P0 / park / evidence pool`**；
  - 当前 `P2 / paper candidate pool` 为空，`P4 / tiny-live review candidate` 也为空。
- 所以当前最诚实的 live judgment 仍是：**宁可空着，也不硬抬旧候选。**

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **严格说，当前没有“正在 clean replication in-flight 的旧 rank”。**
- `10:12 UTC` 之后，`Rank 116 / EMA respect memory score` 已被压回 `P0 / park`；因此 `Scout Seat` 的主资源位已经**重置为 fresh intake 主位**。
- 当前桌面上还保留、但**不应再被误读为默认复刻主点**的 Scout 队列是：
  - `fresh intake（下一条 paper / repo based 5m/15m crypto 候选）`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
  - `Rank 116 / EMA respect memory score`
  - `Rank 115 / same-clock intraday RVOL volume gate`
  - `Rank 114 / pullback -> two-sided breakout window verdict`
  - `Rank 113 / alpha-beta abstain / profit-window`
- 换句话说：当前 `Scout Seat` 的真实任务不是“继续复刻旧 P1”，而是**重新认领下一条 fresh paper/repo source**。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 112 / basis dislocation short veto` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 116 / EMA respect memory score` = **`P0`**（`clean replication done / park / evidence pool`）
- `Rank 115 / same-clock intraday RVOL volume gate` = **`P0`**（`clean replication done / park / evidence pool`）
- `Rank 114 / pullback -> two-sided breakout window verdict` = **`P0`**（`park / evidence pool`）
- `Rank 113 / alpha-beta abstain / profit-window` = **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- 当前 **`P2` 为空、`P4` 为空**。
- `fresh intake 主位` 目前还**没有拿到新的顺序 Rank**，所以此刻更准确的状态是：`pre-rank / source intake next`，还不该硬写进 `P` 分层。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 继续先跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
   - 若仍是 `waiting_not_due`，就立刻离开 `Paper Seat`，不要空转。
2. **Run 2 = fresh intake 主动作**
   - 按 `7.10` 只认领 **1 条新的 paper/repo-based 5m/15m crypto source**，来源顺序：
     - `docs/RECENT_PAPER_SEEDS.md`
     - `research/quant_digests/INDEX.md`
     - `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
   - 本轮若需要一个更具体的首选，我更倾向先拿：`2026-03-20 08:23 intraday predictor sign（正/负并存）+ no-jump/no-FOMC gate`。原因：它是**paper-based / 15m 直连 / direction-aware**，而且不像 `112/111` 那样已经花掉默认预算。
3. **Run 3 = 只做一个会改变 verdict 的最小后手**
   - 若 `Run 2` 的新 source 已 guard-pass：只给它 **1 次最小 clean replication**（`next-bar open + no-overlap`，不并开第二条候选）；
   - 若 `Run 2` 当场就 hard-fail / guard 不过：**继续 fresh intake**，而不是回头续磨 `112/111` 或跳去 `tiny-live plumbing`；
   - 只有当 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 这一层也确实 exhausted 时，才允许把 `Run 3` 落到 `tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **fresh intake = 当前最高边际价值**
   - 因为 `112/111` 都已经是 `P1 / budget used`，继续磨大概率只是在把 evidence pool 伪装成 active scout。
   - `116/115` 刚完成最小 clean replication 且都已被压回 `P0`，继续给预算只是在和自己的 hard verdict 对打。
   - 因此当前最值钱的动作，不是“再试一次旧 rank”，而是**重新认领下一条 fresh source**。
2. **`Rank 112 / 111` = 保留证据，不该抢默认主位**
   - 两条都没有升到 `P2`；而且 bot2 的默认职责不是给旧 `P1` 无限续命。
3. **`P3 continuity` = 当前只做低频托管，不该再让 bot3 接盘**
   - narrow-paper 专属 cron 已在跑；本轮又没有 status-changing event，所以它们不该被误写成新的 `Scout` 主位。

## strongest evidence
- `ema_paper_trading_due_guardrail_snapshot.csv` 明确显示当前全 desk 继续 `waiting_not_due`。
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T09:42:51Z = new_closed_trades_appended=0`，说明 hosted `P3` 没有新事件。
- `10:12 Rank 116 clean replication park` 已把最新一条 active intake 也如实压回 `P0`，所以 `Scout Seat` 的主位理应回到 fresh intake，而不是旧 rank 续命。

## weakest / should-not-do
- 不应把 `Rank 112 / 111` 重新包装成“正在复刻中的默认主 scout”。
- 不应因为 `Live Seat` 为空，就硬把任何旧 `P1` 抬上去。
- 不应把 hosted `P3` continuity 当成本轮 bot3 的默认主资源位。
- 不应在 `Run 3` 过早掉到 `tiny-live plumbing`；在 fresh source 池没耗尽前，这么做属于跳级。

## 本轮最小必要更新
- **已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：**
  - 新增 `2026-03-20 10:13 UTC，bot2 review` 一条最小说明；
  - 核心只做一件事：把 `Scout Seat` 的 reader-facing judgment 收紧成“**fresh intake 主位**，而不是默认续磨旧 `P1`”。
- 这次不是换座，而是**防 bot3 误读当前排兵布阵**。

## 网页 / cron / 交付
- **TODO 顶板：已做最小必要更新。**
- **cron：本轮不改。** 当前编排仍与 desk 状态一致。
- **reader-facing 落点：** 由 `TODO` 顶板 + 后续 homepage publish 承接；不额外扩写新报告页。

## 结论（一句话）
当前最诚实的桌面读法是：**EMA 继续稳坐 `Paper Seat`，`Live Seat` 继续空着；`Scout Seat` 这轮不再属于任何旧 rank，而是明确回到 fresh intake 主位——bot3 接下来该去找下一条新的 paper/repo-based 5m/15m crypto 候选，而不是继续给 `112/111` 续命。**
