# 2026-03-19 07:40 UTC bot2 strategy review

## 本轮先检查了什么
- repo 状态：`git status --short --branch` 显示 `master` 上仍有大量既存脏文件；本轮只做 `docs/TODO.md` 顶部 desk-board 最小必要写回、strategy review 记录、首页 index 刷新与邮件，不混改无关文件。
- 最近 optimization logs（本轮重点核对）：
  - `2026-03-19_0706_rank82-etf-lead-source-intake.md`
  - `2026-03-19_0730_rank82-etf-lead-clean-replication-keep-p1.md`
- 最近 strategy review：
  - `2026-03-19_0646_strategy-review.md`
  - `2026-03-19_0604_strategy-review.md`
  - `2026-03-19_0504_strategy-review.md`
- 当前 cron：
  - `bot2-strategy-review-40m` enabled / 本轮正在运行
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled（本轮最近又补进 `07:36 UTC` 的 fresh repo digest）
  - `bot6-park-reframe-2h` enabled
  - 本轮不需要改 cron
- `Paper Seat` guardrail：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 显示当前仍无 `due-now / overdue`；最近 due 已滚到：
  - `美股 1d+1wk -> 2026-03-19 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-20 00:00 UTC`
  - `A股三条 lane -> 2026-03-20 07:00 UTC`
  结论：`Paper Seat = EMA / running paper / waiting_not_due`。
- `P3 narrow paper` 托管状态：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T07:13:40Z` 显示 `new_closed_trades_appended=0`；当前 `Rank 2 / 17 / 29 / 32b` 没有新的 status-changing event 需要 bot3 抢主资源处理。

## 这轮为什么要把 07:28 的排班再收紧一次
`07:28 UTC` 的 bot3 已把 `Rank 82 / ETF lead regime gate` 的那次最小 clean replication 用掉，并给出更诚实的 hard verdict：**`keep_P1 / evidence_pool`**。

关键不是 ETF 完全没信息，而是它已经满足了当前 desk 对 `P1` 的那次便宜诚实检查预算：
- strict filter 虽明显减亏，但 `trade_count_retention` 只剩约 `20.6%`，过严；
- sizing 版虽略有改善，但 `early_fail` 没有下降，且改善主要集中在 `breakout_short`，会继续稀释 `ema_psar_long / fib_retest_long`；
- 因此它更像 shared gating 线索，而不是值得继续默认续命的 active fast-lane 候选。

按当前 desk 纪律，`Rank 82` 既然已经停在 `P1 keep`，本轮更诚实的动作就不是再给它加一轮模糊“verdict-changing”预算，而是：
1. 保持 `Paper Seat = EMA / waiting_not_due`；
2. `Live Seat` 继续允许为空；
3. `Scout Seat` 立刻切回新的 fresh paper/repo intake，并只保留 `1 个主点 + 1 个紧邻子点`。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA / PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 说明：最新 guardrail 已明确下一批 due 不在眼前；但这不等于桌面空闲，只说明 bot3 应继续按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 82 / ETF lead regime gate` 已做完最小 clean replication，结果仍只是 **`keep_P1 / evidence_pool`**；
  2. `Rank 80 / first-30m impulse quality gate`、`Rank 81 / RS+/RS- asymmetry gate` 也都已经停在 **`P1 keep / evidence_pool`**；
  3. `Rank 78 / 17 / 2 / 29 / 32b` 属于 `P3 narrow paper` 托管层，不应误写成新的 live promotion 候选；
  4. 当前没有任何候选已经走到 `clean replication + Light Stability Pack` 足以支撑 live 升格。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：**
  - `Rank 83 / Fib trend-strength admission layer`
- **当前紧邻后备：**
  - `Rank 85 / fresh pullback → reclaim re-arm gate`
- **当前下一层 fresh paper source：**
  - `Rank 84 / volume-price interaction admission layer`
- **当前只保留在证据池、不再默认占主资源：**
  - `Rank 82 / ETF lead regime gate`
  - `Rank 80 / first-30m impulse quality gate`
  - `Rank 81 / RS+/RS- asymmetry gate`
- **明确不应误写成新 seat 的托管位：**
  - `Rank 78 / 17 / 2 / 29 / 32b`（均属 `P3` narrow paper continuity）

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 83 / Fib trend-strength admission layer = P0`**（`source intake next`）
- **`Rank 85 / fresh pullback → reclaim re-arm gate = P0`**（`fresh repo intake / 邻近后备`）
- **`Rank 84 / volume-price interaction admission layer = P0`**（`fresh paper source pool`）
- **`Rank 82 / ETF lead regime gate = P1`**（`minimal clean replication done / keep_P1 / evidence_pool`）
- **`Rank 80 / first-30m impulse quality gate = P1`**（`cheap honest check 已用 / keep_P1 / evidence_pool`）
- **`Rank 81 / RS+/RS- asymmetry gate = P1`**（`minimal clean replication done / keep_P1 / evidence_pool`）
- **`Rank 78 / adaptive no-trade band = P3`**（`narrow paper pilot / EMA-only suppression overlay`）
- **`Rank 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / 低频托管位`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得伪造 refresh，也不得空转。
2. **`Run 2 = Rank 83 / Fib trend-strength admission layer source intake + 两条轻量诚实守门`**
   - 只冻结 `trade on / trade off` 与 `no-lookahead / no-repaint / no-leakage`，不并开其他候选。
3. **`Run 3 = 若 Rank 83 guard-passed，则只给它 1 次最小 clean replication；若 Rank 83 在守门阶段硬 fail，则立刻切到 Rank 85 / fresh pullback → reclaim re-arm gate source intake`**
   - `Rank 84 / volume-price interaction admission layer` 保留在下一层 fresh paper source；
   - `P3 continuity` 继续只算 low-frequency sidecar，不得默认抢占 Scout 主资源。

## Active Scout 边际价值比较（本轮显式重排）
1. **`Rank 83 / Fib trend-strength admission layer`**
   - 当前排第一，不是因为证据最厚，而是因为它已经在板上排到邻近后备、且还没消耗那次最便宜的 fresh intake 预算；在 `Rank 82` 已明确停在 `P1 keep` 后，先把这条 cheap intake 跑完最诚实。
2. **`Rank 85 / fresh pullback → reclaim re-arm gate`**
   - 当前排第二，因为它是 repo-based 的 shared re-arm state machine，直接服务 `breakout-short / Fib / EMA-PSAR` 三条线共同的“何时算重新上膛”缺口，比更抽象的 feature 论文更容易冻结成可复刻规则。
3. **`Rank 84 / volume-price interaction admission layer`**
   - 仍值得保留，但当前更像 `admission/filter` 线索；在 `Rank 83 / Rank 85` 这层还没用完之前，不应抢默认主资源。
4. **`Rank 82 / Rank 80 / Rank 81`**
   - 当前都只应留在 `P1 evidence_pool`；继续认领它们，大概率只会增加说明，不会减少真实 gate。
5. **`Rank 78 / 17 / 2 / 29 / 32b`**
   - 继续只算 `P3` 托管位；本轮 `manual_narrow_paper_last_run_summary.json` 已回到 `new_closed_trades_appended=0`，没有新的插队理由。

## 对 TODO 顶板的动作
- **本轮已做最小必要写回。**
- 在 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 增加了 `2026-03-19 07:40 UTC（bot2 desk review）` 补充，明确：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Rank 82 / Rank 80 / Rank 81` 全部留在 `P1 evidence_pool`，不再默认续命
  - `Scout Seat` 当前顺位已切成 `Rank 83 > Rank 85 > Rank 84`
  - `Next 3 bot3 runs` 已收紧为 `EMA due-check -> Rank 83 source intake -> Rank 83 clean replication / Rank 85 source intake`
- 本轮未改 cron、未改其他 brief/prompt。

## 结论
- **Paper Seat：EMA，keep**
- **Live Seat：继续暂空**
- **Scout Seat：切回 fresh paper/repo intake；当前由 `Rank 83 / Fib trend-strength admission layer` 领跑，`Rank 85 / fresh pullback → reclaim re-arm gate` 为紧邻后备，`Rank 84 / volume-price interaction admission layer` 为下一层 fresh paper source**
- **P2：空；P4：空**
- **Rank 82 / 80 / 81：都留在 `P1 keep / evidence_pool`，默认不再继续磨**
- **P3 continuity：当前无异常，不重新占主资源**
