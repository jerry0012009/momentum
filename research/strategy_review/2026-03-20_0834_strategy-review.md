# 2026-03-20 08:34 UTC bot2 strategy review

## 本轮一句话判断
当前 desk **不换座**：`Paper Seat` 继续是 **EMA / 创业板ETF 1d** 且仍处于 `waiting_not_due`；`Live Seat` 继续留空；`Scout Seat` 这轮更诚实的主位已经从 **已 exhausted 的 Rank 113** 切到 **Rank 114 / pullback → two-sided breakout window verdict** 的 `source intake next`。

## 本轮先检查了什么
- repo status：`master`
- 当前工作区脏文件很多（>1700），不适合混提
- 最近 optimization logs：`08:27 Rank113 clean replication park`、`07:47 Rank113 intake`、`07:35 Rank112 clean replication`、`07:15 Rank112 intake`
- 最近 strategy review：`07:52`、`07:06`
- 当前 cron：`bot2 40m`、`bot3 13m`、`narrow-paper-lanes 20m`、`bot7 30m`、`bot6 2h` 都仍启用
- `ema_paper_trading_due_guardrail_snapshot.csv`：当前全 desk 仍无 `due-now / overdue`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T07:59:18Z`：`new_closed_trades_appended=1`

## 直接回答本轮 5 个问题

### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 体系内仍在跑的 hosted/backstop lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d`（`shadow_watch`）
- 独立 hosted `P3 / narrow paper` continuity lanes：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
- 当前 hosted sidecar 没有异常到需要抢主资源：最新只看到 `07:59` 有 `1` 笔 closed-trade append；其中 `Rank 17` 仍留有 open paper positions，`Rank 32b` 有新 closed append，但都还不构成改写主排班的 blocker。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  - `Rank 114` 还只在 `source intake next`，连 clean replication 都没做；
  - `Rank 112` 已做完那 1 次便宜诚实检查，只剩 `P1 evidence_pool / budget used`；
  - `Rank 111` 同样停在 `P1 evidence_pool / budget used`；
  - `Rank 113` 已被这轮 clean replication 直接压回 `park / evidence pool`。
- 所以当前没有任何候选够资格抢 `Live Seat`。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主点**：`Rank 114 / pullback → two-sided breakout window verdict`
  - 来源：`2026-03-20 07:42` 的 repo digest
  - 定位：更像一个可复用的 `post-trigger execution skeleton`
  - 当前阶段：`source intake next`
- **当前证据池但不该再默认占主资源的候选**：
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
  - `Rank 113 / alpha-beta abstain / profit-window`（已 park）

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 114 / pullback → two-sided breakout window verdict` = **`P0`**（`source intake next / repo-based reserve`）
- `Rank 112 / basis dislocation short veto` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 113 / alpha-beta abstain / profit-window` = **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- 当前 **`P2` 为空，`P4` 也为空**。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 若出现真实 `due-now / overdue`，先做 guarded refresh；否则不能把 `waiting_not_due` 误读成整桌等待。
2. **Run 2 = 若 EMA 仍 waiting_not_due，则优先认领 `Rank 114 / pullback → two-sided breakout window verdict` 的 source intake**
   - 只做 `trade on / trade off` 与 `no lookahead / no repaint / no leakage` 两条轻量诚实守门。
3. **Run 3 = 若 Rank 114 guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则回 fresh intake**
   - fresh intake 顺序：`docs/RECENT_PAPER_SEEDS.md` → `research/quant_digests/INDEX.md` → `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
   - 只有这一层也 exhausted 后，才允许退回 `tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **Rank 114 最高**：因为它是当前唯一还没花掉默认预算、且明显贴合 `paper/repo based + 5m/15m crypto + post-trigger verdict skeleton` 的 fresh candidate。现在最值钱的不是继续修补旧 P1，而是先回答它能不能诚实进队列。
2. **Rank 112 次之但不该续命**：basis 极端本身有一点 honest veto 味道，但 clean replication 已经回答了最关键问题；继续磨它，边际价值低。
3. **Rank 111 同理**：已经是 `P1 evidence_pool / budget used`，默认不该回头再给主资源。
4. **Rank 113 已应降级**：这轮 clean replication 已证明改善主要来自砍样本，不是带来 desk 级 honest uplift；默认就该 park，而不是再延长模糊研究态。

## strongest evidence
- `EMA` 当前全 desk 仍明确 `waiting_not_due`，所以 bot3 不能假装“Paper Seat blocked = 整桌等待”。
- `Rank 113` 已被最小 clean replication 直接压回 `park / evidence pool`，说明当前 scout 资源必须从它身上移开。
- `Rank 114` 已有清楚 repo digest，且更像 shared execution skeleton，而不是又一个散碎 filter。

## weakest / should-park lines
- 任何还想把 `Rank 113` 继续包装成主 scout 的动作，都属于低杠杆续命。
- 任何试图让 `Rank 112 / Rank 111` 继续抢默认主资源的动作，也都低于 fresh intake 的边际价值。
- `Live Seat` 若此刻硬塞候选，只会回到“为了桌上看起来有 live challenger 而硬撑弱线”的老问题。

## Top 1~3 priority
1. `EMA due-check first`
2. `Rank 114 source intake + 两条轻量诚实守门`
3. `若 Rank 114 guard-pass，则做 1 次最小 clean replication；否则立刻切 fresh intake，不回头磨旧 P1`

## TODO / web / cron
- **TODO 顶板：本轮不改。** 原因：`08:27 UTC` 顶板已经把 `Rank 113 -> park`、`Rank 114 -> next main point`、以及新的 `Next 3` 如实写回；当前没有新的 verdict 变化值得再补一层局部编辑。
- **网页可见落点：本轮不额外改。** 原因：reader-facing verdict 变化（`Rank 113 park`）已经在上一轮同步到 `TODO` 与相关 report 页面；本轮属于无变更巡检。
- **cron：本轮不改。** 当前 cron 方向仍与 desk 主线一致。

## 风险与不确定性
- `Rank 114` 现在还只是 `P0 / source intake next`，不要提前讲成新 alpha，更不要抢 `Live Seat`。
- hosted `P3` sidecar 已有 `closed-trade append`，但若没有异常 open-position / receipt / ledger mismatch，就不该让它们重新吞掉 bot3 主资源。
- 当前工作区脏文件太多，继续做 selective commit 风险高；本轮只保留 review 记录、首页刷新、邮件摘要。

## 结论（一句话）
当前最诚实的 desk 读法是：**EMA 继续坐稳 `Paper Seat`，`Live Seat` 继续空着，Scout 主资源从已 exhausted 的 `Rank 113` 切到 `Rank 114` 的 fresh repo intake；bot3 下一拍别再回头磨旧 P1。**
