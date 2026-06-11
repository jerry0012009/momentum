# Strategy Review (bot2)

- Time (UTC): 2026-03-21 22:59
- Repo: `/root/clawd/jerry/momentum`

## 1) Repo status
- Branch: `master`
- Working tree: **DIRTY** (大量 `docs/` + `reports/` + `scripts/` + `research/` 产物变更；见 `git status -sb`)
- Note: 本轮 bot2 未主动新增任何代码/文档改动；仅做巡检+记录+刷新首页+邮件。

## 2) Recent activity
### `research/optimization_loop/` (latest)
- `2026-03-21_2235_rank139-thr06-08-scorecard-promoteP3.md`
- `2026-03-21_2222_rank139-thr06-08-scorecard.md`
- `2026-03-21_2155_rank139-thr06-08-scorecard.md`
- `2026-03-21_2142_rank139-thr06-08-scorecard.md`
- `2026-03-21_2129_rank139-cusum-min-cleanrep.md`

### `research/strategy_review/` (latest)
- `2026-03-21_2219_strategy-review.md`
- `2026-03-21_2135_strategy-review.md`
- `2026-03-21_2055_strategy-review.md`

## 3) TRADING DESK BOARD — current interpretation (from `docs/TODO.md`)
### Paper: primary anchor + hosted lanes
- **Primary anchor:** `rank32b`（P3 hosted lane / paper lane）
- **Hosted lanes (P3):**
  - `rank2`
  - `rank17`
  - `rank29`
  - `rank32b`（host）

### Live seat
- **Live seat:** 空（`empty`）

### Active Scout / 复刻对象
- **Active Scout:** `Rank139`（CUSUM event bar confirm / veto family）

## 4) Candidate tiers (P0~P4)
> 目标：给 bot3 下一步“先做谁、后做谁”的明确分档。

- **P4 (park / keep parked)**
  - `Rank138` funding+OI crowding breadth（先 park）
  - `Rank127` ATR-delta phase confirm（非 shared，先 park）

- **P3 (hosted lanes / keep warm / sidecar)**
  - Hosted lanes: `Rank2 / Rank17 / Rank29 / Rank32b`
  - Sidecar watch: `Rank122` ATR compression ROC ignition short rearm（倾向保持 P3 sidecar）

- **P2 (active scout focus)**
  - `Rank139`（继续 clean-rep + threshold stability + promote/park 决策闭环）

- **P1 (next scout candidates)**
  - `Rank125` range location veto（已有 clean-rep；作为 veto 层候选）
  - `Rank112` basis dislocation short veto
  - `Rank111` event clock

- **P0 (暂不投入 / backlog / 明确不急)**
  - 其余未在 desk board / active scout / hosted lane 的条目：先不抢占 bot3 时隙（除非 Run1/2/3 明确需要）。

## 5) Next 3 bot3 runs (from board)
- Run1: `Scout Seat — Rank139`（继续推进）
- Run2: `Hosted lane refresh`（rank2/rank17/rank29/rank32b：按 board 指令）
- Run3: `Breakout short follow-up / V3 final-verdict`（如 board 仍指向该线）

## 6) Cron health (summary)
- `bot2-strategy-review-40m`: running / ok
- `momentum-narrow-paper-lanes-20m`: last ok
- `bot3-momentum-auto-opt-13m`: **ERROR**
  - error: tries to read `/root/clawd/docs/TODO.md` (ENOENT)
  - implication: bot3 当前会持续失败，无法执行 desk board。
  - suggested fix (do later): 把 bot3 job prompt 的 TODO 路径改为绝对路径 `/root/clawd/jerry/momentum/docs/TODO.md`，或确保工具读取使用正确 cwd。
- `bot7-quant-digest-30m`: **ERROR** (DNS / timeout)
- `bot6-park-reframe-2h`: **ERROR** (Unexpected end of JSON input)

## 7) Actions taken this run
- Created this log: `research/strategy_review/2026-03-21_2259_strategy-review.md`
- Next: refresh homepage index + send email (body = this log)
