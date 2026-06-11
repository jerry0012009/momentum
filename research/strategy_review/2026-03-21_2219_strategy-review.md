# Strategy Review (bot2) — 2026-03-21 22:19 UTC

## 0) Checklist (per BOT2_STRATEGY_REVIEW_BRIEF)

### Repo status
- Branch: `master`
- Working tree: **dirty**（大量 `??` 未跟踪产物：`reports/artifacts/*`、`reports/site/*`、`research/*` 等）
  - 结论：本轮 **不做清理/不 commit**，仅记录；避免把产物误混入版本控制。

### Recent: `research/optimization_loop/`
- 2026-03-21 21:57 — `research/optimization_loop/2026-03-21_2155_rank139-thr06-08-scorecard.md`
- 2026-03-21 21:45 — `research/optimization_loop/2026-03-21_2142_rank139-thr06-08-scorecard.md`
- 2026-03-21 21:31 — `research/optimization_loop/2026-03-21_2129_rank139-cusum-min-cleanrep.md`
- 2026-03-21 20:53 — `research/optimization_loop/2026-03-21_2050_rank139-cusum-min-cleanrep.md`

### Recent: `research/strategy_review/`
- 2026-03-21 21:37 — `research/strategy_review/2026-03-21_2135_strategy-review.md`
- 2026-03-21 20:56 — `research/strategy_review/2026-03-21_2055_strategy-review.md`
- 2026-03-21 19:27 — `research/strategy_review/2026-03-21_1924_strategy-review.md`

### Cron list (high-signal)
- `bot2-strategy-review-40m`：running
- `bot3-momentum-auto-opt-13m`：**lastStatus=error**（`Unexpected end of JSON input`）
- `bot6-park-reframe-2h`：**lastStatus=error**（同上）
- `bot7-quant-digest-30m`：**lastStatus=error**（同上）
- `momentum-narrow-paper-lanes-20m`：running
- `Rank32b live maintenance`：ok

> 注：多条 job 出现同类 `Unexpected end of JSON input`，更像 delivery/serialization 层面问题而不是策略逻辑问题；本轮只做 desk 排班记录，不直接介入修复。

---

## 1) TRADING DESK BOARD（摘取 authoritative snapshot）
（来源：`docs/TODO.md` 顶部 TRADING DESK BOARD，未改动）

### Paper Seat
- **Paper primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- 状态：`running paper pilot / waiting_not_due`
- **hosted lanes（family lanes）**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### Hosted P3 lanes（narrow paper sidecar）
- running hosted narrow paper lanes（20m refresh）：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- sidecar but not on 20m refresh：`Rank 122`

### Live Seat
- **Live seat**：`暂空`

### Scout Seat
- **Scout 复刻/推进对象（当前主点）**：`Rank 139 / CUSUM event-bar confirm-veto gate`
  - 当前标注：`P2 / promote_P2 / minimal replication passed`

---

## 2) 候选分档（P0~P4）
（按 desk board 当前 Active Scout + Hosted P3 快照整理；本轮不新增候选）

- **P4（live）**：空
- **P3（paper / hosted lanes）**：
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（hosted narrow paper lanes / sidecar）
  - `Rank 122`（hosted P3 sidecar，低频 monitoring only）
- **P2（主推进 scout）**：
  - `Rank 139 / CUSUM event-bar confirm-veto gate`（promote_P2）
- **P1（evidence pool / weak keep）**：
  - `Rank 125 / range location veto gate`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
- **P0（park / evidence pool）**：
  - `Rank 138 / funding×OI crowding breadth overlay`
  - `Rank 127 / ATR delta confirm gate`
  - `Rank 137 / state expiry latency budget gate`
  - 以及 board 上列出的其它 `park / evidence pool` ranks

---

## 3) Next 3 bot3 runs（排班，authoritative）
（沿用 desk board 当前版本）

1. **Run 1 = EMA due-check first**
   - 若有真实 `due-now / overdue` lane：先做 paper refresh。
2. **Run 2 = 若 EMA 仍 waiting_not_due：推进 Rank 139（P2→可上纸/可 park 的最小决策包）**
   - 固定 baseline（BTC/ETH/SOL 15m），对比 `thr_mult ∈ {0.6, 0.8}`，补 1 页轻量 scorecard（5项 0~3 分 + hard-fail flags）。
3. **Run 3 = Rank 139 硬结论分支（只选 1 个）**
   - 若继续成立：`promote_P3 (narrow paper pilot)` + 写清最小 paper spec/monitoring 接线；
   - 若不稳但无硬伤：`keep_P2` + 指定唯一补洞；
   - 若出现硬伤：`park`，并立刻切 `fresh intake > tiny-live plumbing`。

---

## 4) 本轮结论（给老板/desk 的一句话版）
- **Paper anchor** 继续挂在 `EMA / 创业板ETF 1d`，目前 `waiting_not_due`，不应阻塞整个 desk。
- **Live seat 仍空**（允许暂空）。
- **Scout 主资源继续集中在 `Rank 139`**：把它从“最小 clean replication 过了”推进到“能上纸/能 park”的最小决策包。

