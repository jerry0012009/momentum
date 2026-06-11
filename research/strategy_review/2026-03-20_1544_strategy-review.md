# 2026-03-20 15:44 UTC bot2 strategy review

## 本轮一句话判断
当前 desk **不换座，但要把 hosted continuity 和 active Scout 分清**：`Paper Seat` 仍是 **EMA / 创业板ETF 1d active_primary / waiting_not_due**；`Live Seat` 继续**暂空**；`Scout Seat` 当前主复刻位维持 **`Rank 125 / range location veto gate`**，状态是 **`P1 / guard-passed / clean replication next`**。`Rank 29` 虽在 15:41 UTC 的 narrow-paper refresh 中出现新的 closed-trade append，但这仍属于 **`P3 hosted continuity / status sync`**，不应抢走 `Rank 125` 的默认 bot3 主资源位。

## 本轮先检查了什么
- repo status：`master`；`git status --short | wc -l = 1897`，工作区继续很脏，不适合混提
- 最近 optimization logs：
  - `15:35 UTC / Rank 125 source intake -> guard-passed`
  - `15:15 UTC / Rank 124 clean replication -> park`
  - `14:58 UTC / Rank 124 source intake -> guard-passed`
- 最近 strategy review：最新是 `15:04 UTC`
- 当前 cron 列表：`bot2 40m`、`bot3 13m`、`momentum-narrow-paper-lanes 20m`、`bot6 2h`、`bot7 30m`、`Rank32b live maintenance` 等仍在；本轮无需改 cron
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：当前各 EMA lane 仍全部 `waiting_not_due`
  - 美股 `1d+1wk -> 约 13.0 小时后到点`
  - Crypto `1d+1wk -> 约 17.0 小时后到点`
  - 创业板ETF `1d -> 约 3.0 天后到点`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-20T15:41:06Z`：`new_closed_trades_appended=1`
  - 当前可见新增 closed trade append 是：`Rank 29 / ETH-USD / exit_ts=2026-03-20T15:00:00Z`

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
- 当前可见 hosted 运行状态补充：
  - `Rank 17` 当前有 open positions（`ETH-USD long`、`SOL-USD short`）
  - `Rank 32b` 当前有 open positions（`BTC/ETH/SOL`）
  - `Rank 29` 刚新增一笔 `ETH-USD` closed trade append
  - `Rank 2` 当前处于 flat / 托管续跑状态
- 结论：当前 paper 托管层仍是**多 lane 并行**，但主 paper anchor 仍只有 **EMA / 创业板ETF 1d**。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  - `Rank 125` 目前还只到 `P1 / source intake guard-passed`，尚未完成 `clean replication`，更没有任何 `Light Stability Pack` 完成项；
  - `Rank 112 / 111` 都还是 `P1 / evidence_pool / budget used`；
  - `Rank 122` 虽已到 `P3`，但它明确是 **`strict-only / short-side re-arm / paper-only narrow lane`**，不是 live challenger；
  - `Rank 2 / 17 / 29 / 32b` 也都是 **hosted P3 continuity**，不是新 promoted live 候选；
  - 当前仍是 **`P2` 为空、`P4` 为空**。
- 结论：当前没有值得被升格到 `Live Seat` 的对象，空着更诚实。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 queue-facing 主复刻位只该有 1 条：**
  - **`Rank 125 / range location veto gate`**
    - source=`2026-03-20 15:30 UTC` 的论文+repo digest
    - 当前角色：`breakout-short` 的 **no-chase veto**，以及 `Fib retest_hold / EMA-PSAR long` 的 **reclaim-confirm layer**
    - 当前只配验证：`RL_20` 这类 range-location 读数，是否能在不明显砍坏样本的前提下带来 honest veto / confirm uplift
- `Rank 112 / 111` 目前只保留为 `P1 evidence_pool`，不应继续占默认主复刻位。
- `Rank 29` 虽有新的 closed-trade append，但当前只应按 `P3 hosted continuity` 看作 sidecar，不应误写回 `Scout Seat`。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 125 / range location veto gate` = **`P1`**（`source intake / guard-passed / clean replication next`）
- `Rank 112 / basis dislocation short veto` = **`P1`**（`weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`evidence_pool / budget used`）
- `Rank 122 / ATR compression + ROC ignition short re-arm gate` = **`P3`**（`narrow paper pilot approved / strict-only / paper-only / recent-month red-watch`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- `Rank 124 / 123 / 121 / 120 / 119 / 118 / 117` = **`P0`**（`park / evidence pool`）
- 当前 **`P2` 为空、`P4` 为空**。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 继续先跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 若仍 `waiting_not_due`，立刻离开 `Paper Seat`
2. **Run 2 = Rank 125 / range location veto gate 的 1 次最小 clean replication**
   - 统一 `signal 当根及之前数据 + next-bar open + no-overlap`
   - 只回答：`no-chase veto / reclaim-confirm` 是否带来 honest uplift
   - 主看：`post-cost expectancy`、`trade_count_retention`、`false-follow / failure-before-target`、`跨三条 baseline 的可复用性`
3. **Run 3 = 直接给 Rank 125 硬 verdict，不允许继续模糊停在 P1**
   - 若 `Rank 125` clean replication 保留 honest uplift 且没有 decisive fail：**直接升到 `P2 / paper candidate` 或至少 `keep_P1 with explicit next gate`**
   - 若 clean replication 显示改善主要来自过度砍样本、或只是在重命名已有 baseline：**直接压回 `park`**
   - 只有 `Rank 125` 明确 hard-fail / exhausted 后，才回 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 再认领 1 条 fresh intake

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 125` = 当前最高边际价值**
   - 它刚过完两条轻量守门，下一步只差 `1` 次真正会改变级别的 clean replication；
   - 它是 `paper / repo based / 15m crypto` 的新鲜候选；
   - 它回答的是当前 desk 很常见的执行问题：**已经贴着区间边缘时，还该不该追 / 还算不算被接住**。
2. **`Rank 29` 这次 close append = 重要，但仍是 sidecar**
   - 这次确实是 status-changing event；
   - 但 narrow-paper 专属 cron 已完成续写，当前没有迹象说明它需要抢占默认 bot3 主资源；
   - 更诚实的动作是由 bot2 低频记账确认，而不是把它包装回新的 Scout 主位。
3. **`Rank 112 / 111` = 继续保留证据，不该抢主位**
   - 两条都已进入 `budget used` 状态；
   - 继续磨更像把 evidence pool 假装成 active scout。
4. **`Rank 122` = 已托管，不该再占默认 bot3 主资源**
   - 它已经走完 `source intake -> clean replication -> 最小 stability -> promote to P3`；
   - 当前更像 hosted paper continuity，而不是 scout 快筛。

## strongest evidence
- EMA due guardrail 当前明确显示所有 lane 仍 `waiting_not_due`
- `manual_narrow_paper_last_run_summary.json @ 15:41:06Z = new_closed_trades_appended=1`
- 最新一笔 hosted close append 来自 `Rank 29 / ETH-USD / 15:00 UTC`，说明 P3 托管层在正常续跑
- 最新 bot3 结果已把 `Rank 125` 冻结为新的 `P1 / clean replication next`

## weakest / should-not-do
- 不应把 `Rank 29` 这次 close append 包装成新的 `Scout Seat`
- 不应在 `Rank 125` 已 guard-pass 的情况下，回头继续磨 `Rank 112 / 111`
- 不应因为 `Live Seat` 为空，就提前硬抬任何尚未完成 clean replication 的候选
- 不应把 hosted `P3 continuity` 误写成“当前有新 live challenger”

## 建议优先级 Top 1~3
1. **先把 `Rank 125` 做完那 1 次最小 clean replication**
2. **clean replication 结果出来后，本日内就做 `P2 / keep_P1 / park` 的硬写回，不要继续停在 `P1`**
3. **继续把 `Rank 29` 这次 close append 视为 hosted continuity 证据，而不是新的主研究方向**

## TODO / roadmap / web / cron 的改动或建议
- **TODO**：本轮**已最小更新** `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 追加 `15:44 UTC` bot2 review
  - 明确写出 `Rank 29` 的新 closed-trade append 仍属于 hosted sidecar
  - 保持 `Rank 125` 为当前 Scout 主位、`Live Seat` 继续暂空
- **roadmap**：本轮不改
- **web**：不另开新页；本轮 reader-facing 变化已由 `TODO` 顶板承接
- **cron**：本轮不改

## 风险与不确定性
- `Rank 125` 最大风险是：clean replication 可能证明它主要是在更少做单，而不是更诚实地改善 post-cost expectancy
- `Rank 29` 这次 close append 虽属真实状态变化，但目前只看到正常续跑证据，尚不足以触发新的 desk 主资源切换
- `Live Seat` 继续为空虽然诚实，但也意味着接下来几轮更需要 bot3 快速给 `Rank 125` 一个硬 verdict，而不是继续停在 queue-facing 文案层

## 本轮结论（一句话）
当前最诚实的桌面读法仍是：**EMA 继续稳坐 `Paper Seat`，`Live Seat` 继续空着；`Rank 125` 是当前唯一值得 bot3 继续吃预算的 Scout 主点，而 `Rank 29` 的新 close append 只说明 hosted narrow-paper 托管层在正常工作，不构成改座理由。**
