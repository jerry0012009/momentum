# 2026-03-20 10:58 UTC bot2 strategy review

## 本轮一句话判断
当前 desk **继续不换座**：`Paper Seat` 仍是 **EMA / 创业板ETF 1d active_primary**，且全 desk 继续 `waiting_not_due`；`Live Seat` 继续暂空；`Scout Seat` 当前最该拿主资源的仍是 **`Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate`**，因为它刚完成 `source intake + 两条轻量诚实守门`，还没用掉那唯一一次最小 `clean replication` 预算；反过来，`Rank 112 / 111` 已经是 `P1 / evidence_pool / budget used`，不该再抢默认主位。

## 本轮先检查了什么
- repo status：`master`，工作区仍很脏：`dirty_total=1765`（`tracked=79`，`untracked=1686`），不适合混提。
- 最近 optimization logs：
  - `10:52 Rank 118 source intake`
  - `10:39 Rank 117 source intake -> park`
  - `10:12 Rank 116 clean replication -> park`
  - `09:47 Rank 116 source intake`
- 最近 strategy review：上一条是 `10:13 UTC`。
- 当前 cron：`bot2 40m`、`bot3 13m`、`momentum-narrow-paper-lanes 20m`、`bot7 30m`、`bot6 2h`、`Rank32b live maintenance` 都仍在跑；当前没有需要 bot2 立刻改频或改 prompt 的明显漂移。
- `ema_paper_trading_due_guardrail_snapshot.csv`：当前全 desk 继续无 `due-now / overdue`，最近 due 仍是：
  - `美股 1d+1wk -> 2026-03-20 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-21 00:00 UTC`
  - `创业板ETF 1d -> 2026-03-23 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T10:46:43Z`：`new_closed_trades_appended=0`，说明 hosted `P3` narrow-paper lanes 这轮也没有新的 `status-changing event`。

## 直接回答本轮 5 个问题

### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 家族内当前继续运行的 hosted / backstop lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d`（`shadow_watch`）
- 独立 hosted `P3 / narrow paper continuity` lanes：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
- 这些 hosted paper lanes 当前都只是**托管续写层**，不是新的主 seat；而且本轮没有 `closed-trade append / receipt refs / weekly-review row` 之类的新事件，所以不该抢 bot3 主资源。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 当前没有任何候选配得上升格：
  - `Rank 118` 还只是在 **`P1 / guard-passed / clean replication next`**；
  - `Rank 112 / 111` 都是 **`P1 / evidence_pool / budget used`**；
  - `Rank 117 / 116 / 115 / 114 / 113` 都已回到 **`P0 / park / evidence pool`**；
  - 当前 **`P2` 为空、`P4` 为空**。
- 因此这轮最诚实的 live judgment 仍是：**宁可空着，也不硬抬旧候选。**

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前真正处在“继续复刻 / clean replication next”的主点只有 1 条：**
  - `Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate`
- 当前只是后备或证据池、而不是默认主复刻位的候选：
  - `Rank 119 / PSAR trailing role fail-safe`（fresh intake reserve）
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
  - `Rank 117 / ADX<18 range handoff`
  - 以及更早已 park 的 `Rank 116 / 115 / 114 / 113`
- 所以这轮不要把 `Scout Seat` 误读成“并行复刻很多条”；当前 desk 口径仍应是：**`1 个主点 = Rank 118`，`1 个紧邻子点 = Rank 119 reserve`。**

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate` = **`P1`**（`source intake done / guard-passed / clean replication next`）
- `Rank 119 / PSAR trailing role fail-safe` = **`P0`**（`fresh intake reserve / not started`）
- `Rank 112 / basis dislocation short veto` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`evidence_pool / budget used`）
- `Rank 117 / ADX<18 range handoff` = **`P0`**（`source intake direct-park / evidence pool`）
- `Rank 116 / EMA respect memory score` = **`P0`**（`clean replication done / park / evidence pool`）
- `Rank 115 / same-clock intraday RVOL volume gate` = **`P0`**（`clean replication done / park / evidence pool`）
- `Rank 114 / pullback -> two-sided breakout window verdict` = **`P0`**（`park / evidence pool`）
- `Rank 113 / alpha-beta abstain / profit-window` = **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- 当前 **`P2` 为空，`P4` 为空**。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check only**
   - 继续先跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
   - 若仍是 `waiting_not_due`，立刻离开 `Paper Seat`，不要空转，也不要转去 `P3 continuity`。
2. **Run 2 = Rank 118 的 1 次最小 clean replication**
   - 固定只挂 `1` 条 archetype；
   - 统一到 `signal 当根及之前数据 + next-bar open + no-overlap`；
   - 比较 `baseline / sign_gate_only / sign_gate_plus_blackout`；
   - 重点盯 `trade_retention` 和 `false-follow / false-hold` 是否真的更诚实，而不是只是样本变少。
3. **Run 3 = 真正会改变级别的唯一后手**
   - 若 `Rank 118` clean replication 显示 honest uplift 且无 decisive fail：只补 **1 个最小 `Light Stability Pack`**（默认优先 `成本 / 交易数稳定性`），然后直接给出 **`P2 / park`** 判断；
   - 若 `Rank 118` clean replication hard-fail / exhausted：切 **`Rank 119 / PSAR trailing role fail-safe`** 做 fresh intake；
   - 只有 `Rank 119` 这一层也拿不到合格 source 时，才允许回退到 `tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 118` = 当前最高边际价值**
   - 原因不是它已经最像下一条 paper candidate，而是它正好卡在最该花那 `1` 次便宜诚实检查的点上：两条轻量守门已过，但还没进入 clean replication verdict。
2. **`Rank 119` = 次高，但仍只是 reserve，不该抢跑**
   - 它的价值在于：如果 `118` 这轮 hard-fail，可以无缝接 fresh intake；
   - 但只要 `118` 还没用掉 clean replication 预算，就不该并开 `119`。
3. **`Rank 112 / 111` = 继续保留证据，不该抢默认主位**
   - 两条都已经是 `P1 / budget used`；继续给预算，大概率只是把 evidence pool 伪装成 active scout。
4. **`P3 continuity` = 当前只做低频托管，不该再让 bot3 接盘**
   - narrow-paper 专属 cron 已在跑；本轮又没有新事件，所以它们不该被误写成新的 `Scout` 主位。

## strongest evidence
- `ema_paper_trading_due_guardrail_snapshot.csv` 明确显示当前全 desk 继续 `waiting_not_due`。
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T10:46:43Z = new_closed_trades_appended=0`，说明 hosted `P3` 没有新事件。
- `10:52 Rank 118 source intake` 已把最新 fresh source 收紧成一个明确的 `P1 / clean replication next` 候选，因此当前最值钱的动作不再是“再找一条”，而是先把 `118` 做出 hard verdict。

## weakest / should-not-do
- 不应因为 `Paper Seat` 当前在等，就把 bot3 又导回 `P3 hosted continuity`。
- 不应把 `Rank 112 / 111` 重新包装成“默认主 scout”。
- 不应因为 `Live Seat` 为空，就硬把 `Rank 118` 或任何旧 `P1` 提前抬上去。
- 不应同时打开 `Rank 118 + Rank 119` 两条线；这会把 `Scout Seat` 又滑回泛研究入口。

## TODO / 网页 / cron
- **本轮不改 `docs/TODO.md`。** 原因：`10:52 UTC` 顶板写回已经与当前 desk judgment 一致——`Scout Seat = Rank 118 / clean replication next`，`Run 3` 也已收紧成 `118 升格-or-park` 与 `119 reserve` 的二选一路径。
- **本轮不改网页落点。** `Rank 118` 的 source-intake 页已在，当前还没出现新的 verdict 变化值得额外同步。
- **本轮不改 cron。** 当前编排仍与 desk 状态一致。

## 风险与不确定性
- `Rank 118` 很容易演化成“过滤后交易更少，看起来更干净”的样子；下一轮 clean replication 必须优先盯 `retention`，不能只看收益数字外观。
- 论文口径偏 `5m -> hour`，映射到 desk 的纯 `15m` 实现后，sign pocket 结构可能显著变形。
- 若 `Rank 118` clean replication 只是靠 blackout / sign gate 大幅砍样本，不应犹豫，直接 `park`，不要拖成模糊 `P1/P2`。

## 结论（一句话）
当前最诚实的桌面读法是：**EMA 继续稳坐 `Paper Seat`，`Live Seat` 继续空着；`Scout Seat` 这轮应把那唯一一次便宜诚实检查明确给 `Rank 118`，而不是回头给旧 `P1` 续命，也不是提前并开 `Rank 119`。**
