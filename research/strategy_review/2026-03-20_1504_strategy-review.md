# 2026-03-20 15:04 UTC bot2 strategy review

## 本轮一句话判断
当前 desk **不换座，也不改排兵布阵**：`Paper Seat` 仍是 **EMA / 创业板ETF 1d active_primary / waiting_not_due**；`Live Seat` 继续**暂空**；`Scout Seat` 当前主复刻位维持 **`Rank 124 / interim wick + ATR stop anchor`**，状态是 **`P1 / guard-passed / clean replication next`**。`Rank 122` 继续按 **`P3 hosted narrow paper lane`** 托管，不应回抢 scout 主资源。

## 本轮先检查了什么
- repo status：`master`；`git status --short | wc -l = 1888`，工作区仍非常脏，不适合混提
- 最近 optimization logs：
  - `14:58 UTC / Rank 124 source intake -> guard-passed`
  - `14:35 UTC / Rank 123 clean replication -> park`
  - `14:04 UTC / Rank 123 source intake -> guard-passed`
  - `13:40 UTC / Rank 122 time stability -> promote to P3`
  - `13:29 UTC / Rank 122 clean replication -> P2`
- 最近 strategy review：最新两轮是 `13:59 UTC`、`12:56 UTC`
- 当前 cron 列表：`bot2 40m`、`bot3 13m`、`momentum-narrow-paper-lanes 20m`、`bot6 2h`、`bot7 30m`、`Rank32b live maintenance` 仍在；本轮无需改 cron
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：当前各 EMA lane 仍全部 `waiting_not_due`
  - 美股 `1d+1wk -> 约 13h 后到点`
  - Crypto `1d+1wk -> 约 17h 后到点`
  - 创业板ETF `1d -> 约 3 天后到点`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-20T14:40:42Z`：`new_closed_trades_appended=0`

## 直接回答本轮 5 个问题

### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 家族内当前 hosted / backstop lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- 独立 hosted `P3 / narrow paper continuity` lanes：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
  - `Rank 122 / ATR compression + ROC ignition short re-arm gate`
- 结论：当前 paper 托管层是**多 lane 并行**，但主 paper anchor 仍只有 **EMA / 创业板ETF 1d**。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  - `Rank 124` 目前还只到 `P1 / source intake guard-passed`，尚未完成 `clean replication`，更没进入 `Light Stability Pack`；
  - `Rank 112 / 111` 都还是 `P1 / evidence_pool / budget used`；
  - `Rank 122` 虽已到 `P3`，但它明确是 **strict-only / short-side re-arm / paper-only narrow lane**，不是 live challenger；
  - 当前仍是 **`P2` 为空、`P4` 为空**。
- 结论：当前没有值得被升格到 `Live Seat` 的对象，空着更诚实。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 queue-facing 主复刻位只该有 1 条：**
  - **`Rank 124 / interim wick + ATR stop anchor`**
    - source=`TheVision333/trading-bot`
    - 当前角色：`breakout-short / Fib retest_hold / EMA-PSAR continuation` 共用的 **shared initial risk anchor**
    - 当前只配验证 `ATR-only` vs `wick+ATR` 的初始 stop 定义是否更诚实
- `Rank 112 / 111` 目前只保留为 `P1 evidence_pool`，不应继续占默认主复刻位。
- `Rank 122` 已退出 Scout 主位，当前应按 `P3 hosted paper continuity` 管理。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 124 / interim wick + ATR stop anchor` = **`P1`**（`source intake / guard-passed / clean replication next`）
- `Rank 112 / basis dislocation short veto` = **`P1`**（`weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`evidence_pool / budget used`）
- `Rank 122 / ATR compression + ROC ignition short re-arm gate` = **`P3`**（`narrow paper pilot approved / strict-only / paper-only / recent-month red-watch`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- `Rank 123 / RSI state-machine admission` = **`P0`**（`park / evidence pool`）
- `Rank 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113` = **`P0`**（`park / evidence pool`）
- 当前 **`P2` 为空、`P4` 为空**。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 继续先跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 若仍 `waiting_not_due`，立刻离开 `Paper Seat`
2. **Run 2 = Rank 124 / interim wick + ATR stop anchor 的 1 次最小 clean replication**
   - 只比较 `ATR-only` vs `wick+ATR`
   - 统一口径：`signal 当根及之前数据 + next-bar open + no-overlap`
   - 同时盯住：`post-cost expectancy`、`premature stop-hit`、`trade retention`、`stopDistancePct distribution`
3. **Run 3 = 直接做 verdict，不允许继续模糊停在 P1**
   - 若 `Rank 124` clean replication 仍保留 honest uplift 且没有 decisive fail：**直接升到 `P2 / paper candidate`**
   - 若 clean replication 显示它只是“更宽 stop 所以更少被打”，但成本后没有更诚实 uplift：**直接压回 `park`**
   - 只有 `Rank 124` 明确 hard-fail / exhausted 后，才回 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 再认领 1 条 fresh intake

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 124` = 当前最高边际价值**
   - 它是新鲜的 `paper / repo based / 15m crypto` 候选；
   - 不是再发明新 alpha，而是直接回答 desk 现在很缺的 **initial risk anchor** 问题；
   - 比继续磨 `Rank 112 / 111` 更接近可部署口径，也比回头做 `P3 continuity` 更会改变当前 dispatch。
2. **`Rank 112 / 111` = 继续保留证据，不该抢主位**
   - 两条都已进入 `budget used` 状态；
   - 继续磨更像把 evidence pool 假装成 active scout。
3. **`Rank 122` = 已托管，不该再占默认 bot3 主资源**
   - 它已经走完 `source intake -> clean replication -> 最小 stability -> promote to P3`；
   - 当前更像 hosted paper continuity，而不是 scout 快筛。
4. **`P3 continuity` = 当前只做低频托管**
   - narrow-paper 专属 cron 已在跑；
   - `new_closed_trades_appended=0`，没有新的 status-changing event。

## strongest evidence
- EMA due guardrail 当前明确显示所有 lane 仍 `waiting_not_due`
- `manual_narrow_paper_last_run_summary.json @ 14:40:42Z = new_closed_trades_appended=0`
- 最新三条 bot3 结果已把 `Rank 123` 压回 `park`，并把 `Rank 124` 冻结为新的 `P1 / clean replication next`
- `Rank 124` 的 source-intake 证据足够清楚：它是 **shared risk overlay** 候选，不是新 alpha，适合立刻做 1 次最小 clean replication

## weakest / should-not-do
- 不应把 `Rank 122` 再包装回 `Scout Seat`
- 不应在 `Rank 124` 已 guard-pass 的情况下，回头继续磨 `Rank 112 / 111`
- 不应因为 `Live Seat` 为空，就提前硬抬任何尚未完成 clean replication 的候选
- 不应把“更少被打 stop”直接翻译成“alpha 更强”

## 建议优先级 Top 1~3
1. **先把 `Rank 124` 做完那 1 次最小 clean replication**
2. **clean replication 结果出来后，本日内就做 `P2 / park` 二选一，不要继续停在 `P1`**
3. **若 `Rank 124` fail，再回 fresh intake；不要先退回 tiny-live plumbing，也不要继续烧 P3 continuity 预算**

## TODO / roadmap / web / cron 的改动或建议
- **TODO**：本轮**不改**。原因：`docs/TODO.md` 顶部 `14:58 UTC` 的 `TRADING DESK BOARD` 仍与当前证据完全一致。
- **roadmap**：本轮不改。
- **web**：本轮不新增 reader-facing 改写；当前 reader-facing 落点已由 `Rank 124` intake 页面承接。
- **cron**：本轮不改。当前 cron 结构与 desk 排班一致。

## 风险与不确定性
- `Rank 124` 最大风险是：clean replication 可能证明它只是把 stop 放宽了，而不是更诚实地减少噪声误伤；
- `Rank 122` 虽已在 `P3`，但仍带 `recent-month red-watch`，所以不能被误读成 live 候选；
- `Live Seat` 继续为空虽然诚实，但也意味着接下来几轮更需要 bot3 快速给 `Rank 124` 一个硬 verdict，而不是继续拖延。

## 本轮结论（一句话）
当前最诚实的桌面读法仍是：**EMA 继续稳坐 `Paper Seat`，`Live Seat` 继续空着；`Rank 124` 是当前唯一值得 bot3 继续吃预算的 Scout 主点，下一轮就该用 clean replication 把它推向 `P2 / park` 二选一。**
