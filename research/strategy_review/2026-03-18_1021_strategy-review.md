# 2026-03-18 10:21 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 切到 Rank 53 fresh intake

## 0）本轮先做的状态检查（按 desk 规则）
- 先读并遵循：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- repo 状态：`git status --short --branch` 显示当前工作区仍有大量与本轮无关脏文件；本轮只做 `docs/TODO.md` 顶板最小写回，不混提其它内容。
- 最近 strategy review：
  - `research/strategy_review/2026-03-18_0925_strategy-review.md`
  - `research/strategy_review/2026-03-18_0720_strategy-review.md`
  - `research/strategy_review/2026-03-18_0632_strategy-review.md`
- 最近 optimization loop：
  - `2026-03-18_1011_rank52-clean-replication-park.md`
  - `2026-03-18_0950_rank52-trade-flow-intake.md`
  - `2026-03-18_0922_rank51-clean-replication-park.md`
  - `2026-03-18_0845_rank51-vwap-source-intake.md`
- 当前 cron 列表关键项：
  - `bot2-strategy-review-40m`：正常运行中
  - `bot3-momentum-auto-opt-13m`：正常运行中
  - `bot7-quant-digest-30m`：正常运行中；本轮前刚补出 `2026-03-18_1017_close-confirmed-choch-compression-gate.md`
  - `momentum-narrow-paper-lanes-20m`：正常运行中
- `EMA paper due guardrail` 当前仍全是 `waiting_not_due`：
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json`（`09:51:03Z`）显示：`new_closed_trades_appended=0`；当前没有新的 `P3 status-changing event` 值得让 bot3 回头认领。

## 1）这轮先回答 5 个必须问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态不是 due-now，而是 **`running paper / waiting_not_due`**。
- 因此这轮对 bot3 的含义不是“继续伪 refresh”，而是：`Run 1` 只做 `due-check only`，主资源默认导向 `Scout Seat`。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因很直接：当前没有任何 scout 候选在这轮结束后已经走到 `clean replication + 最小诚实门` 之上，更没有谁应被写成新的默认 live challenger。
- `Rank 50 / 51 / 52` 都已在允许预算内完成快筛并压回 `park / evidence pool`；不能因为桌面想“看起来热闹”就强行升格。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **严格地说：当前 fast-lane 上没有存活的 active replication。**
- `Rank 52` 已在 `10:11 UTC` 完成最小 clean replication 并压回 `park / evidence pool`。
- 当前新的主资源位已切到 **fresh intake**：
  - **`Rank 53 / close-confirmed CHoCH compression gate`**（来自 `2026-03-18 10:17 UTC` 新 quant digest；repo=`jcornierfra/TradingView_Indicator_JCO_Swings_Trend_HTF`）
- 其后回退顺序：
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- `Rank 2 / 17 / 29 / 32b` 这些 `P3 narrow paper` 仍只算低频 continuity 托管位，不是当前默认 Scout 主资源位。

### 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 53 / close-confirmed CHoCH compression gate`** → **`P1 weak candidate`**（`fresh source intake / 两条轻量诚实守门 next`）
- **`Rank 35b`** → **`P0-ish queue-only fallback`**（`derived hypothesis drafted / 未重新 admitted，不算 active fast-lane`）
- **`Rank 16b`** → **`P0-ish queue-only fallback`**（`derived hypothesis drafted / 未重新 admitted，且与刚 park 的 session-range 轴重合更高`）
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**（仅保留 `paper ledger / monitoring / refresh / review` 最小接线；本轮 `new_closed_trades_appended=0`，不抢占 seat）
- **`Rank 50 / 51 / 52`** → **`P0 park / evidence pool`**（本轮前的 active scout 已全部给出 hard verdict）

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**
2. **Run 2 = `Rank 53 / close-confirmed CHoCH compression gate` 的 `source intake + 两条轻量诚实守门`**（仅当 `EMA` 仍 `waiting_not_due`）
3. **Run 3 = 若 `Rank 53` 已 `guard-passed` 且 `EMA` 仍 `waiting_not_due`，立刻给它 1 次最小 `clean replication`；若 `Run 2` 硬 fail / exhausted，再比较 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 2）为什么这轮是 `Rank 53 > Rank 35b > Rank 16b > tiny-live plumbing`
- `Rank 53` 是**新的 repo-based 15m 候选**，不是 park 后派生的旧线近义重写。
- 它直接服务当前三条收口线的共同缺口：**别让 wick-only 假破把 15m 方向过早翻面**；这比继续磨 `Rank 35b / Rank 16b` 这种 fallback 更像真正的新 gate。
- 它只依赖现有公开 `15m OHLCV` + `1h resample`，不需要额外付费数据，最适合先过 `trade on / trade off` 与 `no-lookahead / no-repaint / no-leakage` 两条轻门。
- `Rank 35b` 虽然还保留作 fallback，但本质仍是 `park` 后的窄派生；当前既然有新的 repo source，就不该默认先回去磨它。
- `Rank 16b` 也只是 fallback，而且和刚被证明更像 execution / sample-cut template 的 `session-range / active-hours` 轴更相邻，边际价值低于 `Rank 53`。

## 3）本轮对 `docs/TODO.md` 做的最小必要更新
- 在 `TRADING DESK BOARD -> Scout Seat verdict` 下新增 `2026-03-18 10:21 UTC` 补充：
  - 冻结新方向为 **`Rank 53 / close-confirmed CHoCH compression gate`**
  - 明确当前 fast-lane **没有存活的 active P1/P2 replication**，只是 fresh intake 主资源位切到 `Rank 53`
  - 写清当前边际价值比较：`Rank 53 > Rank 35b > Rank 16b > tiny-live plumbing`
- 在 `TRADING DESK BOARD -> Next 3 bot3 runs` 下新增 `2026-03-18 10:21 UTC` 补充：
  - 将默认顺序更新为 `EMA due-check -> Rank 53 source intake -> Rank 53 minimal clean replication / fallback`
- 同步重建站点镜像：
  - `python3 scripts/build_todo_page.py`
  - 产物：`reports/site/plans/momentum_todo.html`

## 4）这轮的 desk verdict（简版）
- **Paper Seat**：`EMA` 继续坐，且当前只是 `waiting_not_due`，不是 due-now。
- **Live Seat**：继续空席。
- **Scout Seat**：当前不是继续磨 `Rank 50/51/52`，而是切到 **`Rank 53` fresh intake**。
- **P3 continuity**：今天这轮仍没有新的 status-changing event，继续低频托管，不抢 seat。

## 5）落地与后续动作
- 已更新：`docs/TODO.md`
- 已更新站点镜像：`reports/site/plans/momentum_todo.html`
- 下一步按 desk 规则，应由 bot3：
  1. 先做 `EMA due-check only`
  2. 若仍 `waiting_not_due`，立即对 `Rank 53` 做 `source intake + 两条轻量诚实守门`
  3. 只有 `Rank 53` guard-passed 后，才允许那 1 次最小 clean replication

## 6）执行备注
- 本轮未改 cron。
- 本轮未做 git commit：当前工作区有大量与本轮无关脏文件，不满足安全 selective commit 条件。
