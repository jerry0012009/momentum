# 2026-03-20 11:51 UTC bot2 strategy review

## 本轮一句话判断
当前 desk **继续不换座**：`Paper Seat` 仍是 **EMA / 创业板ETF 1d active_primary**，且全 desk 继续 `waiting_not_due`；`Live Seat` 继续暂空；`Scout Seat` 在 `Rank 118 / 119` 连续 park 之后，当前最诚实的读法不是“还有旧 rank 在 clean replication 中”，而是**回到 fresh intake 主位**，并把下一手收紧成 **`Rank 120 / strict BMS impulse quality gate` 主点** + **`Rank 121 / PSAR trailing role fail-safe` 紧邻 reserve**。

## 本轮先检查了什么
- repo status：`master`，`git status --short` 约 `1790` 条，工作区很脏，不适合混提
- 最近 optimization logs：
  - `11:49 Rank 119 clean replication -> park`
  - `11:28 Rank 119 source intake`
  - `11:20 Rank 118 clean replication -> park`
  - `10:52 Rank 118 source intake`
- 最近 strategy review：最新一条是 `10:58 UTC`
- 当前 cron：`bot2 40m`、`bot3 13m`、`momentum-narrow-paper-lanes 20m`、`bot6 2h`、`bot7 30m`、`Rank32b live maintenance` 仍都在跑；本轮无需改 prompt / 改频
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：全 desk 继续 **`waiting_not_due`**；最近 due 仍是：
  - `美股 1d+1wk -> 2026-03-20 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-21 00:00 UTC`
  - `创业板ETF 1d -> 2026-03-23 07:00 UTC`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-20T11:23:37Z`：`new_closed_trades_appended=0`

## 直接回答本轮 5 个问题

### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 家族内当前 hosted / backstop lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d`（`shadow_watch`）
- 独立 hosted `P3 / narrow paper continuity` lanes：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
- 这些 hosted lanes 当前都只是**托管续写层**，不是新的主 seat；且 `new_closed_trades_appended=0`，所以本轮不该抢 bot3 主资源。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 当前没有候选配得上升格：
  - `Rank 120 / 121` 还只是 fresh intake / source-intake 级别；
  - `Rank 112 / 111` 仍是 **`P1 / evidence_pool / budget used`**；
  - `Rank 119 / 118 / 117` 都已回到 **`P0 / park / evidence pool`**；
  - 当前 **`P2` 为空、`P4` 为空**。
- 因此这轮最诚实的 live judgment 仍是：**宁可空着，也不硬抬旧 rank。**

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **严格说，当前没有“正在 clean replication 中”的存活旧候选。** `Rank 118 / 119` 都已在允许预算内给出 hard verdict 并 park。
- 当前 `Scout Seat` 的真实读法是：**fresh intake 主位**，但已经收紧成 `1 个主点 + 1 个紧邻 reserve`：
  1. **`Rank 120 / strict BMS impulse quality gate`**（主点）
  2. **`Rank 121 / PSAR trailing role fail-safe`**（紧邻 reserve）
- 旧 `Rank 112 / 111` 只保留证据池身份，不再当默认主复刻位。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 120 / strict BMS impulse quality gate` = **`P1`**（`fresh source intake next / 两条轻量诚实守门 pending`）
- `Rank 121 / PSAR trailing role fail-safe` = **`P1`**（`fresh source intake reserve / exit-role clarifier only`）
- `Rank 112 / basis dislocation short veto` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`evidence_pool / budget used`）
- `Rank 119 / confirmed swing + HTF alignment long-side context` = **`P0`**（`clean replication done / park / evidence pool`）
- `Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate` = **`P0`**（`clean replication done / park / evidence pool`）
- `Rank 117 / ADX<18 range handoff` = **`P0`**（`source intake direct-park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- 当前 **`P2` 为空，`P4` 为空**。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 继续先跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 若仍 `waiting_not_due`，立刻离开 `Paper Seat`
2. **Run 2 = Rank 120 / strict BMS impulse quality gate source intake + 两条轻量诚实守门**
   - 只做一件事：把它收紧成“到底只是 `high-conviction subset / long-side bucket / conditional veto`，还是连这层都不诚实”
   - 不允许直接把它写成 breakout-short / Fib / EMA-PSAR 的 shared gate
3. **Run 3 = 唯一真正会改变 dispatch 的后手**
   - 若 `Rank 120` 守门通过：只给 **1 次最小 clean replication**
   - 若 `Rank 120` 当场 hard-fail / 过稀疏 / 守门不过：切 **`Rank 121 / PSAR trailing role fail-safe`** 做 source intake
   - 只有这两层都 exhausted 后，才允许回到 `tiny-live plumbing`

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 120` = 当前最高边际价值**
   - `11:32 UTC` digest 已经把问题压到很窄：它是 fresh repo-based 15m crypto 候选；
   - 最值钱的不是“它可能是新神因子”，而是它能用一次很便宜的 honesty gate，快速回答“该不该直接 park 掉 strict BMS 这种高稀疏门”；
   - 这比继续给 `112/111` 续命，更可能更快改变 desk judgment。
2. **`Rank 121` = 次高，但只配当 reserve**
   - `PSAR trailing role` 的价值主要在 exit / fail-safe 角色澄清；
   - 当前 desk 更缺 entry/follow-up 侧的 fresh filter verdict，所以它排在 `Rank 120` 后面。
3. **`Rank 112 / 111` = 继续保留证据，不该抢默认主位**
   - 两条都已经是 `P1 / budget used`；继续磨更像把 evidence pool 伪装成 active scout。
4. **`P3 continuity` = 当前只做低频托管，不该再让 bot3 接盘**
   - narrow-paper 专属 cron 已在跑；本轮又没有新 append / receipt / weekly-review 事件。

## strongest evidence
- due guardrail 明确显示全 desk 继续 `waiting_not_due`
- `manual_narrow_paper_last_run_summary.json @ 11:23:37Z = new_closed_trades_appended=0`
- 最新两条 bot3 logs 已把 `Rank 118 / 119` 连续压回 `park`
- `11:32 UTC` 的 strict BMS repo digest 已经足够给出一个 cheap-honesty-gate 候选，不必再泛泛“继续 fresh intake”

## weakest / should-not-do
- 不应再把 `Rank 112 / 111` 包装成“默认主 scout”
- 不应因为 `Live Seat` 为空，就提前硬抬任何 fresh intake
- 不应把 `P3 hosted continuity` 写成新的 Scout 主位
- 不应在 `Rank 120 / 121` 还没走完最小诚实守门前，就重新滑到泛研究

## 本轮最小必要更新
- 已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 核心只做一件事：把 generic `fresh intake` 收紧成 **`Rank 120` 主点 + `Rank 121` reserve**，避免 bot3 下一轮又回到模糊排班
- 本轮不改 cron

## 结论（一句话）
当前最诚实的桌面读法是：**EMA 继续稳坐 `Paper Seat`，`Live Seat` 继续空着；`Scout Seat` 在 `118/119` 连续 park 之后，应该明确切成 `Rank 120 / strict BMS impulse` 主点、`Rank 121 / PSAR trailing role` reserve，而不是继续给旧 `P1` 续命。**
