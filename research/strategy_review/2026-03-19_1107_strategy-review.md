# 2026-03-19 11:07 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 当前已从 `Rank 86` 的已 park 残影切到 **`Rank 87 / volume-clock + CS spread interaction gate`**，下一手只应给它 **1 次最小 clean replication**，做完直接回答 `keep_P1 / promote_to_P2 / park`。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1385`，工作区仍有大量既有脏文件；本轮只做 `docs/TODO.md` 顶部 desk board 的最小必要写回、strategy review 记录、首页 index 刷新与邮件，不混改无关文件。
- 最近 optimization logs（本轮重点核对）：
  - `2026-03-19_0937_rank84-clean-replication-park.md`
  - `2026-03-19_0940_rank86-signalpro-intake.md`
  - `2026-03-19_1011_rank86-clean-replication-keep-p1.md`
  - `2026-03-19_1037_rank86-time-stability-park.md`
  - `2026-03-19_1102_rank87-volume-clock-intake.md`
- 最近 strategy review：
  - `2026-03-19_1012_strategy-review.md`
  - `2026-03-19_0908_strategy-review.md`
  - `2026-03-19_0828_strategy-review.md`
- 当前 cron（`cron.list`）重点核对：
  - `bot2-strategy-review-40m` enabled
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
  - 本轮不需要改 cron
- `Paper Seat` guardrail：已实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前全 desk 仍无 `due-now / overdue` lane
  - 最近 due 点为：
    - `美股 1d+1wk -> 约 8.8h`
    - `Crypto 1d+1wk -> 约 12.8h`
    - `创业板ETF 1d -> 约 19.8h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T10:43:40Z`
  - `new_closed_trades_appended = 0`
  - 当前 `Rank 78 / 17 / 2 / 29 / 32b` 没有新的 status-changing event 需要 bot3 抢主资源

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是 guardrail 明确显示的真 waiting，不是整个 desk 停摆；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 87` 当前只到 **`P1 / source intake guard-passed / minimal clean replication next`**；
  2. `Rank 86 / 85 / 84 / 83` 已全部落到 **`park / evidence_pool`**；
  3. `Rank 82 / 80 / 81` 继续只是 **`P1 evidence_pool`**；
  4. `Rank 78 / 17 / 2 / 29 / 32b` 仍是 `P3 narrow paper continuity` 托管位，不应误写成新的 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：**
  - `Rank 87 / volume-clock + CS spread interaction gate`
- **当前紧邻 fresh backlog：**
  - `outside-close -> back-inside-close` failure verdict
  - `close-range compression` asymmetry
- **当前只留在证据池、不再默认占主资源：**
  - `Rank 82 / ETF lead regime gate`
  - `Rank 80 / first-30m impulse quality gate`
  - `Rank 81 / RS+/RS- asymmetry gate`
  - `Rank 86 / SignalPro penetration×ATR admission`
  - `Rank 85 / fresh pullback -> reclaim re-arm gate`
  - `Rank 84 / volume-price interaction admission layer`
  - `Rank 83 / Fib trend-strength admission layer`
- **明确不应误写成新 seat 的托管位：**
  - `Rank 78 / 17 / 2 / 29 / 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 87 / volume-clock + CS spread interaction gate = P1`**（`source intake / 两条轻量诚实守门已过；minimal clean replication next`）
- **`outside-close -> back-inside-close` failure verdict = P0**（`fresh digest backlog / source intake pending`）
- **`close-range compression` asymmetry = P0**（`fresh digest backlog / source intake pending`）
- **`Rank 82 / ETF lead regime gate = P1`**（`evidence_pool / 不再默认续命`）
- **`Rank 80 / first-30m impulse quality gate = P1`**（`cheap honest check 已用 / evidence_pool`）
- **`Rank 81 / RS+/RS- asymmetry gate = P1`**（`minimal clean replication 已用 / evidence_pool`）
- **`Rank 86 / 85 / 84 / 83 = P0`**（`park / evidence_pool`）
- **`Rank 78 / 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / low-frequency hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得伪造 refresh，也不得空转。
2. **`Run 2 = Rank 87 / volume-clock + CS spread interaction gate minimal clean replication`**
   - 固定 `BTC/ETH/SOL 5m->15m` cache；只比较 `baseline / fixed-clock gate / volume-clock+spread gate`；统一 `signal 当根及之前数据 + next-bar open + no-overlap`；做完直接回答 `keep_P1 / promote_to_P2 / park`。
3. **`Run 3 = 若 Rank 87 clean replication 直接 hard-fail / park，则回到 fresh paper/repo intake；只有 fresh intake 也 exhausted，才回退到更 breakout-centric backlog > Rank 82 / 80 / 81 evidence_pool > tiny-live plumbing`**
   - `P3 continuity` 继续只算 low-frequency sidecar，不得默认抢占 Scout 主资源。

## Active Scout 边际价值比较（本轮显式重排）
1. **`Rank 87 / volume-clock + CS spread interaction gate`**
   - 当前排第一，因为它已经完成 `source intake + 两条轻量诚实守门`，并且更贴当前 `EMA waiting_not_due` 下的 shared continuation / liquidity gate 主线，不需要重新放大 breakout 叙事。
2. **两条更 breakout-centric 的 fresh digest backlog**
   - 继续保留第二层，但不能在 `Rank 87` 还没拿到 minimal clean replication 结果前并开抢跑。
3. **`Rank 82 / Rank 80 / Rank 81`**
   - 继续只保留在 `P1 evidence_pool`；它们都已经用掉了便宜检查或最小 clean replication，当前继续磨大概率只会增加说明，不会减少真实 gate。
4. **`Rank 78 / 17 / 2 / 29 / 32b`**
   - 继续只算 `P3` 托管位；本轮没有新的状态变化，不该插队。

## 当前 strongest evidence
1. **EMA guardrail 继续清楚显示 `waiting_not_due`**：这轮没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 86` 已在时间稳定性检查后明确 park**：减少了继续误分配 fast-lane 预算的风险。
3. **`Rank 87` 已完成 source intake + honesty gate**：当前已从 fresh queue 升到 **`P1 / minimal clean replication next`**，是当前最靠近能改变层级判断的一条线。
4. **P3 托管层当前无新异常**：`manual_narrow_paper_last_run_summary.json` 继续 `new_closed_trades_appended=0`，因此没有理由让 `Rank 78 / 17 / 2 / 29 / 32b` 抢回主资源。

## 当前 weakest / should-park lines
- **`Rank 86 / SignalPro penetration×ATR admission`**：已经给完那 1 次 truly verdict-changing 的时间稳定性检查，hard verdict 明确是 **park**。
- **`Rank 85 / fresh pullback -> reclaim re-arm gate`**：已经给完最小 clean replication，hard verdict 也是 **park**。
- **`Rank 84 / volume-price interaction admission layer`**：最小 clean replication 未证明 shared interaction 方案能稳定优于 baseline，继续应视为 **park**。
- **`Rank 83 / Fib trend-strength admission layer`**：已经在更诚实 friction 下翻负，继续应视为 **park**。

## TODO / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 11:07 UTC（bot2 desk review）` 补充；
  - 明确当前 `Scout Seat` 已切到 `Rank 87`；
  - 明确当前分级为 `Rank 87 = P1`、`Rank 86 / 85 / 84 / 83 = P0 park`、`P2 / P4 仍空`。
- **本轮不改 cron。**
- **reader-facing 判断**：当前以 `TODO 顶板 + Rank 87 source-intake 页面 + 本轮 strategy review` 作为可见落点已经足够；本轮无需额外扩写 closure 页。

## 风险与不确定性
- `Rank 87` 当前仍只到 `P1`，不是升格结论；它下一手必须是最小 clean replication，而不是继续补 intake wording 或多开并行候选。
- 当前 repo 工作区依旧很脏；本轮继续避免混改，只做最小局部更新。
- 两条 breakout-centric fresh digest backlog 只保留 backlog 身份，不应被预先写死成下一席。 
