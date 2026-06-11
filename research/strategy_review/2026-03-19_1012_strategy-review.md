# 2026-03-19 10:12 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 当前应从 `Rank 84` 的已 park 残影彻底切换到 **`Rank 86 / SignalPro penetration×ATR admission`**，并且只再给它 **1 次 truly verdict-changing 的 Light Stability Pack（默认时间稳定性）**：过则升 `P2`，不过则直接 `park` 并回到 fresh intake。

## 本轮先检查了什么
- repo 状态：`git status --short --branch` 显示 `master` 工作区仍有大量既存脏文件（tracked + untracked）；本轮只做 `docs/TODO.md` 顶部作战板的最小必要写回、strategy review 记录、首页 index 刷新与邮件，不混改无关文件。
- 最近 optimization logs（本轮重点核对）：
  - `2026-03-19_0937_rank84-clean-replication-park.md`
  - `2026-03-19_0940_rank86-signalpro-intake.md`
  - `2026-03-19_1011_rank86-clean-replication-keep-p1.md`
- 最近 strategy review：
  - `2026-03-19_0908_strategy-review.md`
  - `2026-03-19_0828_strategy-review.md`
  - `2026-03-19_0740_strategy-review.md`
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
- `P3 narrow paper` 托管状态：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T09:39:59Z`
  - `new_closed_trades_appended = 0`
  - 当前 `Rank 2 / 17 / 29 / 32b` 没有新的 status-changing event 需要 bot3 抢主资源

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 说明：这不是“因为懒得做才等待”，而是 guardrail 明确显示当前没有新的 `due-now / overdue` lane；因此 bot3 仍必须转去 `Scout Seat > tiny-live plumbing > 其他维护`，不能把整桌误判成停摆。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 86` 当前只到 **`P1 keep / worth one Light Stability Pack check`**，还没走到 `P2 -> P3 -> P4`；
  2. `Rank 84 / Rank 85 / Rank 83` 都已给出 **`park / evidence_pool`**，不应回头再包装成 live challenger；
  3. `Rank 82 / Rank 80 / Rank 81` 继续只是 **`P1 evidence_pool`**；
  4. `Rank 78 / 17 / 2 / 29 / 32b` 是 `P3 narrow paper continuity` 托管位，不是新的 live 候选。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：**
  - `Rank 86 / SignalPro penetration×ATR admission`
- **当前紧邻后备：**
  - `fresh paper/repo intake`（按 `7.10` 从 `docs/RECENT_PAPER_SEEDS.md`、`research/quant_digests/INDEX.md`、`reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md` 再认领 1 条新的 `5m / 15m crypto` source）
- **当前 backlog 示例，但不预占下一席：**
  - `breakout-candle compression reclaim`
- **当前只保留在证据池、不再默认占主资源：**
  - `Rank 84 / volume-price interaction admission layer`
  - `Rank 85 / fresh pullback → reclaim re-arm gate`
  - `Rank 83 / Fib trend-strength admission layer`
  - `Rank 82 / ETF lead regime gate`
  - `Rank 80 / first-30m impulse quality gate`
  - `Rank 81 / RS+/RS- asymmetry gate`
- **明确不应误写成新 seat 的托管位：**
  - `Rank 78 / 17 / 2 / 29 / 32b`（均属 `P3 narrow paper continuity`）

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 86 / SignalPro penetration×ATR admission = P1`**（`minimal clean replication done / keep_P1 / 仅剩 1 次 truly verdict-changing 的 Light Stability Pack`）
- **`fresh paper/repo intake pool = P0`**（`source intake next`）
- **`breakout-candle compression reclaim = P0`**（`fresh repo backlog`）
- **`Rank 84 / volume-price interaction admission layer = P0`**（`park / evidence_pool`）
- **`Rank 85 / fresh pullback → reclaim re-arm gate = P0`**（`park / evidence_pool`）
- **`Rank 83 / Fib trend-strength admission layer = P0`**（`park / evidence_pool`）
- **`Rank 82 / ETF lead regime gate = P1`**（`minimal clean replication done / keep_P1 / evidence_pool`）
- **`Rank 80 / first-30m impulse quality gate = P1`**（`cheap honest check 已用 / keep_P1 / evidence_pool`）
- **`Rank 81 / RS+/RS- asymmetry gate = P1`**（`minimal clean replication done / keep_P1 / evidence_pool`）
- **`Rank 78 / adaptive no-trade band = P3`**（`narrow paper pilot / EMA-only suppression overlay`）
- **`Rank 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / low-frequency hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得伪造 refresh，也不得空转。
2. **`Run 2 = Rank 86 / SignalPro penetration×ATR admission` 的 1 次 truly verdict-changing `Light Stability Pack`**
   - 默认先做 **时间稳定性**；做完必须直接回答 `promote_to_P2 / park`。
3. **`Run 3 = 若 Rank 86 未过关则直接回到 fresh paper/repo intake；若过关则升到 P2 / paper candidate pool`**
   - fresh intake 默认按 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 顺序再认领 1 条新的 `5m / 15m crypto` source；`P3 continuity` 继续只算 low-frequency sidecar，不得默认抢占 Scout 主资源。

## Active Scout 边际价值比较（本轮显式重排）
1. **`Rank 86 / SignalPro penetration×ATR admission`**
   - 当前排第一，因为它已经完成 `source intake -> clean replication`，只差 1 次真正会改变层级判断的最小检查；比回头补 `Rank 84 / 85 / 83` 的 closeout 说明，或者继续给 `Rank 82 / 80 / 81` 续命，都更能减少真实 gate。
2. **`fresh paper/repo intake（7.10 pool）`**
   - 当前排第二，而不是 `breakout-candle compression reclaim` 直接锁定第二席。原因是：`Rank 86` 若失败，按 desk 纪律应优先回到 fresh source 池重新比较边际价值，而不是默认沿一个较旧 backlog 机械往下排。
3. **`breakout-candle compression reclaim`**
   - 只保留为 backlog 示例，不预占下一席；当前不该在 `Rank 86` 还未出最终 `P2/park` 前并开。
4. **`Rank 82 / Rank 80 / Rank 81`**
   - 继续只保留在 `P1 evidence_pool`；它们都已经用掉了那次便宜检查或最小 clean replication，当前继续磨大概率只会增加文案，不会减少真实 gate。
5. **`Rank 78 / 17 / 2 / 29 / 32b`**
   - 继续只算 `P3` 托管位；本轮没有新的状态变化，不该插队。

## 当前 strongest evidence
1. **EMA guardrail 继续清楚显示 `waiting_not_due`**：这轮没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 86` 已完成 `source intake -> clean replication` 两步，且 clean replication 没有直接判死**：`pen_plus_atr` 在 `6bps/side` 下已从 `baseline mean_total_return=-6.65%` 改善到 `+0.22%`，`positive_asset_ratio=2/3`，足以留下 1 次真正 verdict-changing 的稳定性检查预算。
3. **`Rank 84` 已在最小 clean replication 后 park，减少了误分配风险**：当前不再存在“Rank 84 可能继续吃 fast-lane 预算”的模糊带。
4. **P3 托管层当前无新异常**：`manual_narrow_paper_last_run_summary.json` 继续 `new_closed_trades_appended=0`，因此没有理由让 `Rank 2 / 17 / 29 / 32b` 抢回主资源。

## 当前 weakest / should-park lines
- **`Rank 84 / volume-price interaction admission layer`**：已经给完最小 clean replication，hard verdict 明确是 **park**。
- **`Rank 85 / fresh pullback → reclaim re-arm gate`**：已经给完那次最小 clean replication，hard verdict 也是 **park**。
- **`Rank 83 / Fib trend-strength admission layer`**：已经做完成本稳定性检查并在更诚实 friction 下翻负，继续应视为 **park**。
- **`Rank 82 / Rank 80 / Rank 81`**：都只应保留在 `P1 evidence_pool`；继续默认认领它们，大概率只会增加说明，不会减少真实 gate。

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 10:12 UTC（bot2 desk review）` 补充；
  - 明确当前 `Scout Seat` 已切到 `Rank 86`，而不是仍停留在 `Rank 84` 的旧判断；
  - 明确当前分级为 `Rank 86 = P1`、`Rank 84 / 85 / 83 = P0 park`、`P2/P4 仍空`；
  - 明确当前 `Run 3` 若 `Rank 86` 失败，应回到 **fresh paper/repo intake**，而不是默认沿旧 backlog 机械往下排。
- **本轮不改 cron**。
- **reader-facing 判断**：当前以 `TODO 顶板 + Rank 86 clean-replication 页面 + 本轮 strategy review` 作为可见落点已经足够；本轮无需再扩写额外 closure/report 页面。

## 风险与不确定性
- `Rank 86` 当前仍只到 `P1`，不是升格结论；它下一手必须是最小 Light Stability Pack，而不是继续补 intake wording 或多开并行候选。
- 当前 repo 工作区依旧非常脏；本轮继续避免混改，只做最小局部更新。
- `fresh paper/repo intake` 池仍可能在下一轮重新洗牌；因此 `breakout-candle compression reclaim` 目前只保留 backlog 身份，不预先写死成下一席。
