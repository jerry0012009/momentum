# 2026-03-19 09:08 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Rank 85` 已在最小 clean replication 后压回 `park`，因此 `Scout Seat` 当前应明确切到 **`Rank 84 / volume-price interaction admission layer`**，由它拿下一次最小 clean replication 预算，`SignalPro penetration×ATR admission` 作为紧邻后备。

## 本轮先检查了什么
- repo 状态：`git status --short --branch` 显示工作区仍有大量既存脏文件（tracked + untracked）；本轮只做 `docs/TODO.md` 顶部 desk-board 的最小必要写回、strategy review 记录、首页 index 刷新与邮件，不混改无关文件。
- 最近 optimization logs（本轮重点核对）：
  - `2026-03-19_0826_rank83-cost-stability-park.md`
  - `2026-03-19_0835_rank85-rearm-intake.md`
  - `2026-03-19_0858_rank85-rearm-clean-replication.md`
  - `2026-03-19_0902_rank84-volume-price-intake.md`
- 最近 strategy review：
  - `2026-03-19_0828_strategy-review.md`
  - `2026-03-19_0740_strategy-review.md`
  - `2026-03-19_0646_strategy-review.md`
- 当前 cron（`cron.list`）重点核对：
  - `bot2-strategy-review-40m` enabled
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
  - 本轮不需要改 cron
- `Paper Seat` guardrail：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 当前全 desk 仍无 `due-now / overdue` lane
  - 最近 due 点为：
    - `美股 1d+1wk -> 2026-03-19 20:00 UTC`
    - `Crypto 1d+1wk -> 2026-03-20 00:00 UTC`
    - `A股三条 lane -> 2026-03-20 07:00 UTC`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T09:06:27Z`
  - `new_closed_trades_appended = 0`
  - 当前 `Rank 2 / 17 / 29 / 32b` 没有新的 status-changing event 需要 bot3 抢主资源

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 说明：现在是真 waiting，不是假装 waiting；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流，不能把整桌误判成停摆。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 84` 目前只到 **`P1 / guard-passed / minimal clean replication next`**，还没走到 `P2 -> P3 -> P4`；
  2. `Rank 85` 已在 `08:58 UTC` 的最小 clean replication 后给出 **`park / evidence_pool`**；
  3. `Rank 82 / 80 / 81` 仍都停在 **`P1 evidence_pool`**；
  4. `Rank 78 / 17 / 2 / 29 / 32b` 是 `P3 narrow paper continuity` 托管位，不应误写成新的 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：**
  - `Rank 84 / volume-price interaction admission layer`
- **当前紧邻后备：**
  - `SignalPro penetration×ATR admission`
- **当前下一层 fresh source backlog：**
  - `breakout-candle compression reclaim`
- **当前只保留在证据池、不再默认占主资源：**
  - `Rank 85 / fresh pullback → reclaim re-arm gate`
  - `Rank 83 / Fib trend-strength admission layer`
  - `Rank 82 / ETF lead regime gate`
  - `Rank 80 / first-30m impulse quality gate`
  - `Rank 81 / RS+/RS- asymmetry gate`
- **明确不应误写成新 seat 的托管位：**
  - `Rank 78 / 17 / 2 / 29 / 32b`（均属 `P3 narrow paper continuity`）

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 84 / volume-price interaction admission layer = P1`**（`guard-passed / minimal clean replication next`）
- **`SignalPro penetration×ATR admission = P0`**（`fresh repo intake / 邻近后备`）
- **`breakout-candle compression reclaim = P0`**（`fresh repo backlog`）
- **`Rank 85 / fresh pullback → reclaim re-arm gate = P0`**（`park / evidence_pool`）
- **`Rank 83 / Fib trend-strength admission layer = P0`**（`park / evidence_pool`）
- **`Rank 82 / ETF lead regime gate = P1`**（`minimal clean replication done / keep_P1 / evidence_pool`）
- **`Rank 80 / first-30m impulse quality gate = P1`**（`cheap honest check already spent / keep_P1 / evidence_pool`）
- **`Rank 81 / RS+/RS- asymmetry gate = P1`**（`minimal clean replication done / keep_P1 / evidence_pool`）
- **`Rank 78 / adaptive no-trade band = P3`**（`narrow paper pilot / low-frequency sidecar`）
- **`Rank 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / low-frequency hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得伪造 refresh，也不得空转。
2. **`Run 2 = Rank 84 / volume-price interaction admission layer minimal clean replication`**
   - 只给它 1 次最小 clean replication，统一保持 `signal 当根及之前数据 + next-bar open + no-overlap`；做完直接回答 `keep_P1 / promote_to_P2 / park`。
3. **`Run 3 = 若 Rank 84 clean replication 直接 hard-fail / park，则切 SignalPro penetration×ATR admission source intake；若 Rank 84 未硬 fail 但 verdict 仍不足，则只允许给它 1 个 truly verdict-changing 的最小检查`**
   - `P3 continuity` 继续只算 low-frequency sidecar，不得默认抢占 Scout 主资源。

## Active Scout 边际价值比较（本轮显式重排）
1. **`Rank 84 / volume-price interaction admission layer`**
   - 当前排第一，不是因为材料最厚，而是因为它已经 guard-pass，且是跨三条主线可复用的 shared admission 层；在“默认不再强调 breakout”的约束下，它比 breakout 语义更重的候选更贴当前桌面主线。
2. **`SignalPro penetration×ATR admission`**
   - 保留第二，因为它仍是 paper/repo based fresh source，但 breakout 语义更强；只有 `Rank 84` 这次最小 clean replication 已明确 hard-fail / park，才应正式接手。
3. **`breakout-candle compression reclaim`**
   - 保留第三，仍属于 fresh repo backlog；当前不该与 `Rank 84 / SignalPro` 并开。
4. **`Rank 85 / Rank 83 / Rank 82 / Rank 80 / Rank 81`**
   - 当前都不该再占默认 fast-lane：`Rank 85 / 83` 已 park，`Rank 82 / 80 / 81` 已停在 `P1 evidence_pool`。
5. **`Rank 78 / 17 / 2 / 29 / 32b`**
   - 继续只算 `P3` 托管位；本轮没有新的插队理由。

## 当前 strongest evidence
1. **EMA guardrail 继续清楚显示 `waiting_not_due`**：这轮没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **Rank 85 已完成该给的最小预算并给出 hard verdict**：`08:35 UTC` guard-pass、`08:58 UTC` minimal clean replication 后直接压回 **`park / evidence_pool`**，因此不应再继续讲 `re-arm` 故事。
3. **Rank 84 已完成 source intake + honesty gate**：当前已从 fresh queue 升到 **`P1 / guard-passed / minimal clean replication next`**，这是当前 Scout 最靠近能改变层级判断的一条线。
4. **P3 托管层当前无新异常**：`manual_narrow_paper_last_run_summary.json` 继续 `new_closed_trades_appended=0`，因此没有理由让 `Rank 2 / 17 / 29 / 32b` 抢回主资源。

## 当前 weakest / should-park lines
- **`Rank 85 / fresh pullback → reclaim re-arm gate`**：已完成 `source intake -> clean replication`，且 clean replication 没证明它能诚实地改善三条 archetype；当前应明确视为 **park**。
- **`Rank 83 / Fib trend-strength admission layer`**：已做完 minimal clean replication + 1 次 truly verdict-changing 成本稳定性检查，并在更诚实 friction 下翻负；当前也应继续视为 **park**。
- **`Rank 82 / Rank 80 / Rank 81`**：都只应保留在 `P1 evidence_pool`；继续默认认领它们，大概率只会增加说明，不会减少真实 gate。

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 09:08 UTC（bot2 desk review）` 补充；
  - 明确当前 `Scout Seat` 顺位已切到 `Rank 84 > SignalPro > breakout-candle compression reclaim`；
  - 明确当前分级为 `Rank 84 = P1`、`Rank 85 / 83 = P0 park`、`P2/P4 仍空`。
- **本轮不改 cron**。
- **reader-facing 判断**：当前以 `TODO 顶板 + Rank 84 source-intake 页面 + 本轮 strategy review` 作为可见落点已经足够；本轮无需再扩写额外 closure/report 页面。

## 风险与不确定性
- `Rank 84` 目前仍只到 `P1`，不是升格结论；它下一手必须是最小 clean replication，而不是继续补 intake wording。
- `SignalPro` 与 `breakout-candle compression reclaim` 都还只是 fresh source 层；当前不应把 active Scout 队列再扩成三四条并行。
- repo 工作区仍有大量既存脏文件 / 未跟踪文件；本轮继续避免混改，只做最小局部更新。
