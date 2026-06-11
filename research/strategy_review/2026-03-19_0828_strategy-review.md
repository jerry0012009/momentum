# 2026-03-19 08:28 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续保持**暂空**；`Rank 83` 在成本稳定性后已正式压回 `park / evidence_pool`，因此 `Scout Seat` 当前应明确切到 **`Rank 85 / fresh pullback → reclaim re-arm gate`**，`Rank 84 / volume-price interaction admission layer` 作为紧邻后备。

## 本轮先检查了什么
- repo 状态：`git status --short` 显示工作区仍有大量既存脏文件；本轮只做 `docs/TODO.md` 顶部 desk-board 最小必要写回、strategy review 记录、首页 index 刷新与邮件，不混改无关文件。
- 最近 optimization logs（本轮重点核对）：
  - `2026-03-19_0750_rank83-fib-trend-strength-intake.md`
  - `2026-03-19_0805_rank83-fib-trend-strength-clean-replication.md`
  - `2026-03-19_0826_rank83-cost-stability-park.md`
- 最近 strategy review：
  - `2026-03-19_0740_strategy-review.md`
  - `2026-03-19_0646_strategy-review.md`
  - `2026-03-19_0604_strategy-review.md`
- 当前 cron（tool `cron.list`）：
  - `bot2-strategy-review-40m` enabled
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
  - 本轮不需要改 cron
- `Paper Seat` guardrail：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 显示当前全 desk 仍无 `due-now / overdue` lane；最近 due 点为：
  - `美股 1d+1wk -> 2026-03-19 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-20 00:00 UTC`
  - `A股三条 lane -> 2026-03-20 07:00 UTC`
  结论：`Paper Seat = EMA / running paper / waiting_not_due`。
- `P3 narrow paper` 托管状态：`manual_narrow_paper_last_run_summary.json @ 2026-03-19T07:55:34Z` 显示 `new_closed_trades_appended=0`；当前 `Rank 2 / 17 / 29 / 32b` 没有新的 status-changing event 需要 bot3 抢主资源。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA / PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 说明：现在是真 waiting，不是假装 waiting；因此 bot3 必须继续按 `Scout Seat > tiny-live plumbing > 其他维护` 导流，不能把整桌误判成停摆。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 83` 已从 `keep_P1` 收口为 **`park / evidence_pool`**；
  2. `Rank 82 / Rank 80 / Rank 81` 也都停在 **`P1 evidence_pool`**；
  3. `Rank 78 / 17 / 2 / 29 / 32b` 属于 `P3 narrow paper` 托管位，不应误写成新的 live challenger；
  4. 当前没有任何候选已经走到足以争夺 `tiny-live review` 的 `P2 -> P3 -> P4` 路径。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：**
  - `Rank 85 / fresh pullback → reclaim re-arm gate`
- **当前紧邻后备：**
  - `Rank 84 / volume-price interaction admission layer`
- **当前下一层 fresh source（暂不入板扩写）：**
  - 其他 fresh paper/repo 线索（包括新 digest，但当前不应在 `Rank 85 / Rank 84` 之前抢跑）
- **当前只保留在证据池、不再默认占主资源：**
  - `Rank 83 / Fib trend-strength admission layer`
  - `Rank 82 / ETF lead regime gate`
  - `Rank 80 / first-30m impulse quality gate`
  - `Rank 81 / RS+/RS- asymmetry gate`
- **明确不应误写成新 seat 的托管位：**
  - `Rank 78 / 17 / 2 / 29 / 32b`（均属 `P3` narrow paper continuity）

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 85 / fresh pullback → reclaim re-arm gate = P0`**（`source intake next / 当前默认主资源位`）
- **`Rank 84 / volume-price interaction admission layer = P0`**（`fresh paper source / 邻近后备`）
- **`Rank 83 / Fib trend-strength admission layer = P0`**（`park / evidence pool`）
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
2. **`Run 2 = Rank 85 / fresh pullback → reclaim re-arm gate source intake + 两条轻量诚实守门`**
   - 只冻结 `trade on / trade off` 与 `no-lookahead / no-repaint / no-leakage`，不并开其他候选。
3. **`Run 3 = 若 Rank 85 guard-passed，则只给它 1 次最小 clean replication；若 Rank 85 也不合格，再切 Rank 84 / volume-price interaction admission layer`**
   - `P3 continuity` 继续只算 low-frequency sidecar，不得默认抢占 Scout 主资源。

## 当前 strongest evidence
1. **EMA guardrail 仍清楚显示 `waiting_not_due`**：这轮没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **Rank 83 已经完成了该给的最小预算并给出 hard verdict**：
   - `08:05 UTC` clean replication：`strength_filter / strength_sizing` 在 `6bps/side` 下有改善；
   - `08:26 UTC` cost stability：`strength_sizing` 到 `15bps/side` 变成 `0/3` 全负；
   - 结论已经从“可能升格”收口到 **`park / evidence_pool`**，不再需要继续讲故事。
3. **P3 托管层当前无新异常**：`manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended=0`，因此没有理由让 `Rank 2 / 17 / 29 / 32b` 抢回主资源。

## 当前 weakest / should-park lines
- **`Rank 83 / Fib trend-strength admission layer`**：已经完成 `source intake -> clean replication -> 1 次 truly verdict-changing 检查`，且成本梯度下明显翻负；当前应明确视为 **park**，而不是继续留在模糊 `P1`。
- **`Rank 82 / Rank 80 / Rank 81`**：都只应保留在 `P1 evidence_pool`；继续默认认领它们，大概率只会增加说明，不会减少真实 gate。

## Active Scout 边际价值比较（本轮显式重排）
1. **`Rank 85 / fresh pullback → reclaim re-arm gate`**
   - 当前排第一，不是因为证据最厚，而是因为它给出了比 `Rank 84` 更清楚的 **armed -> reclaim -> reset** 状态机；
   - 这条线直接回答三条主线共同缺的“何时算 re-armed，可以再打一枪”，比继续磨旧 `P1` 或继续给 `Rank 83` 续命更有边际价值。
2. **`Rank 84 / volume-price interaction admission layer`**
   - 仍有共享价值，但当前更像 admission/filter 抽象层；
   - 在 `Rank 85` 还没用掉那次最便宜的 source-intake 预算前，不应抢默认主资源位。
3. **其他 fresh paper/repo source**
   - 保持在第三顺位；只有 `Rank 85 / Rank 84` 这层拿不到合格对象，才继续向后扩。
4. **`Rank 83 / Rank 82 / Rank 80 / Rank 81`**
   - 当前都不该再占默认 fast-lane：`Rank 83` 已 park，`Rank 82 / 80 / 81` 已停在 `P1 evidence_pool`。
5. **`Rank 78 / 17 / 2 / 29 / 32b`**
   - 继续只算 `P3` 托管位；这轮没有新的插队理由。

## 建议优先级 Top 1~3
1. **守住 `Paper Seat = EMA / waiting_not_due` 的 due-check 纪律**，不要伪造 refresh。
2. **把 `Scout Seat` 明确切到 `Rank 85`**，先做 `source intake + 两条轻量诚实守门`。
3. **若 `Rank 85` 不能 guard-pass，就立刻切 `Rank 84`**；不要回头继续磨 `Rank 83 / 82 / 80 / 81`。

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 08:28 UTC（bot2 desk review）` 补充；
  - 明确 `Rank 83` 已 `park / evidence_pool`；
  - 明确当前 `Scout Seat` 顺位已切到 `Rank 85 > Rank 84 > 其他 fresh source`。
- **本轮不改 cron**。
- **网页/表达建议**：当前 reader-facing 主判断已经足够清楚，继续以 `TODO 顶板 + strategy review + 首页 Recent Activity` 作为可见落点即可；不需要额外改 closure/report 页面。

## 风险与不确定性
- `Rank 85 / Rank 84` 目前都还停在 fresh-source 层，本轮不是升格结论，只是更诚实的排兵布阵。
- `08:08 UTC` 的新 digest 也是新鲜线索，但当前不应把 active Scout 队列再扩成三四条并行；先把 `Rank 85 / Rank 84` 这层预算走完更符合 desk 纪律。
- repo 工作区仍有大量既存脏文件 / 未跟踪文件；本轮避免混改，只做最小局部更新。
