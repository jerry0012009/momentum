# 2026-03-20 09:15 UTC bot2 strategy review

## 本轮一句话判断
当前 desk **不换座**：`Paper Seat` 继续是 **EMA / 创业板ETF 1d** 且仍处于 `waiting_not_due`；`Live Seat` 继续留空；`Scout Seat` 继续由 **Rank 115 / same-clock intraday RVOL volume gate** 占主位。与上一轮相比，本轮只做 **1 处最小必要板面修正**：把 `Next 3` 里 `Rank 115` 成功分支补全为“clean replication 若不爆雷，就立刻做 1 个真正会改变级别的最小 `Light Stability Pack`，并直接给 `P2 / park` 判断”，避免 bot3 在 clean replication 之后又模糊漂回 fresh intake。

## 本轮先检查了什么
- repo status：`master`，且工作区仍有大量与本轮无关的脏文件，不适合混提
- 最近 optimization logs：
  - `09:10 Rank115 same-clock RVOL intake`
  - `08:59 Rank114 clean replication park`
  - `08:40 Rank114 source intake`
  - `08:27 Rank113 clean replication park`
- 最近 strategy review：`08:34 UTC`
- 当前 cron：`bot2 40m`、`bot3 13m`、`momentum-narrow-paper-lanes 20m`、`bot7 30m`、`bot6 2h` 均仍启用；`bot2` 当前轮次本身也在正常运行
- `ema_paper_trading_due_guardrail_snapshot.csv`：当前全 desk 继续无 `due-now / overdue`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T09:03:58Z`：`new_closed_trades_appended=0`

## 直接回答本轮 5 个问题

### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 体系内仍在跑的 hosted / backstop lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d`（`shadow_watch`）
- 独立 hosted `P3 / narrow paper` continuity lanes：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
- 当前 hosted `P3` sidecar 没有新的 status-changing event：`manual_narrow_paper_last_run_summary.json` 这轮仍是 `new_closed_trades_appended=0`，所以它们不该插队抢 bot3 主资源。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因很直接：
  - `Rank 115` 目前只到 **`P1 / source intake guard-passed / clean replication next`**，还没到可以讨论 live 的层级；
  - `Rank 112`、`Rank 111` 都已经是 **`P1 evidence_pool / budget used`**；
  - `Rank 114`、`Rank 113` 都已压回 **`P0 / park / evidence pool`**。
- 所以当前没有任何候选应该被硬升格成 `Live Seat` challenger。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主点**：`Rank 115 / same-clock intraday RVOL volume gate`
  - 定位：repo-based / 5m-15m crypto / shared confirmation layer
  - 当前阶段：`source intake 完成，clean replication next`
- **当前仍在证据池、但不应继续抢默认主资源的旧候选**：
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
- **当前已 park 的近邻候选**：
  - `Rank 114 / pullback → two-sided breakout window verdict`
  - `Rank 113 / alpha-beta abstain / profit-window`

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 115 / same-clock intraday RVOL volume gate` = **`P1`**（`source intake guard-passed / clean replication next`）
- `Rank 112 / basis dislocation short veto` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 114 / pullback → two-sided breakout window verdict` = **`P0`**（`park / evidence pool`）
- `Rank 113 / alpha-beta abstain / profit-window` = **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- 当前 **`P2` 为空，`P4` 也为空**。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 若出现真实 `due-now / overdue`，先做 guarded refresh；若继续 `waiting_not_due`，不能把它误读成整桌等待。
2. **Run 2 = 若 EMA 仍 waiting_not_due，则只给 `Rank 115 / same-clock intraday RVOL volume gate` 1 次最小 clean replication**
   - 统一口径：`signal 当根及之前数据 + next-bar open + no-overlap`
3. **Run 3 = 若 Rank 115 clean replication 显示 honest uplift 且无 decisive fail，则立刻补 1 个真正会改变级别的最小 `Light Stability Pack`（默认优先 `成本 / 交易数稳定性`），并直接给 `P2 / park` 判断；若 Rank 115 hard-fail / exhausted，则回 fresh intake**
   - fresh intake 顺序：`docs/RECENT_PAPER_SEEDS.md` → `research/quant_digests/INDEX.md` → `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
   - 只有这一层也 exhausted 后，才允许退回 `tiny-live plumbing`

## Active Scout 边际价值比较（本轮显式比较）
1. **Rank 115 仍是最高边际价值**
   - 它是当前唯一同时满足 `repo-based`、`5m/15m crypto`、`已有公共数据快检`、且还没花掉默认预算的 fresh candidate。
   - 它修的是多个 setup 共用的 `volume gate honest measurement`，不是又造一条新 alpha，所以更贴近 desk 当前需求。
2. **Rank 112 / Rank 111 不该回头续命**
   - 两条都已经做过那 1 次便宜诚实检查，现状是 `P1 evidence_pool / budget used`；继续磨，只会占 bot3 资源，不会更快改变 desk judgment。
3. **Rank 114 / Rank 113 已经回答完“值不值得继续给默认预算”这个问题**
   - 当前都应留在 `P0 / park / evidence pool`，不该抢主位。

## strongest evidence
- `ema_paper_trading_due_guardrail_snapshot.csv` 明确显示全 desk 继续 `waiting_not_due`：
  - `美股 1d+1wk -> 2026-03-20 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-21 00:00 UTC`
  - `创业板ETF 1d -> 2026-03-23 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T09:03:58Z = new_closed_trades_appended=0`，说明 hosted `P3` lanes 没有新事件值得插队
- `09:10 Rank115 intake` 已把 `trade on / trade off` 与 `no lookahead / leakage` 两条轻量诚实守门写清，所以下一拍最该做的就是 clean replication，而不是继续回头磨旧 P1

## weakest / should-park lines
- 任何试图把 `Rank 112 / 111` 再包装成默认主 scout 的动作，都属于低杠杆续命
- 任何现在就想给 `Rank 115` 硬升 `Live Seat` 的动作，都属于越级
- 任何继续把 `P3 hosted continuity` 当成 bot3 默认主资源位的动作，也都不符合当前 `waiting_not_due` 桌面约束

## 本轮最小必要更新
- **已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：**
  - 仅补齐 `Rank 115` 的 `Run 3` 成功分支：
    - 不再写成“clean replication 之后只要 fail 就 fresh intake”这种单边描述；
    - 改成“若 clean replication 没有被判死刑，就立刻做 1 个 truly verdict-changing 的最小 `Light Stability Pack`，并直接给 `P2 / park` 判断”。
- 这次改动的目的不是换座，而是**防止 bot3 在 `Rank 115` clean replication 后重新掉回模糊研究态**。

## TODO / web / cron
- **TODO 顶板：已做最小必要改动。**
- **网页可见落点：已重建 `reports/site/plans/momentum_todo.html`。**
- **cron：本轮不改。** 当前 cron 编排仍与 desk 主线一致。

## 风险与不确定性
- `Rank 115` 当前还只是 `P1`；它最多只配拿 `1 次 clean replication + 1 次 truly verdict-changing 的最小稳定性检查`，不配无限续命。
- 当前工作区脏文件仍很多；本轮只做 selective write-back，不碰无关改动。
- 若后续 `20:00 UTC / 00:00 UTC` due window 前出现真实 paper refresh 或 narrow-paper status-changing event，下一轮 desk 优先级需要重新判断。

## 结论（一句话）
当前最诚实的读法仍是：**EMA 稳坐 `Paper Seat`，`Live Seat` 继续空着，bot3 下一拍先做 `Rank 115` 的最小 clean replication；如果它没爆雷，就不要又退回泛研究，而是直接用 1 个最小 `Light Stability Pack` 把它推向 `P2 / park`。**
