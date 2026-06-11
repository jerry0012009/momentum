# 2026-03-18 09:25 UTC — bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 `EMA baseline family / EMA-PSAR raw alpha` 占位且当前真实状态仍是 **`running paper / waiting_not_due`**；`Live Seat` 继续空席；`Scout Seat` 当前最诚实的读法是 **fast-lane 上已无存活 active `P1 / P2`**，因此 bot3 不应回头磨 `Rank 50 / 51` 或挤占 `P3 continuity`，而应先回到 **fresh paper / repo based 5m / 15m crypto intake**。

## 本轮先检查了什么

### 1) repo 状态
- `git status --short`
- 结论：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做最小 board writeback、strategy review 记录、网页刷新，不混提别的条目。

### 2) 最近 optimization logs（重点）
- `2026-03-18_0922_rank51-clean-replication-park.md`
  - `Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate` 已完成唯一允许的一手最小 clean replication，并被如实压回 **`park / evidence pool`**。
- 直接影响：当前 fast-lane 上已经没有 surviving active `P1 / P2`；`Run 2` 不该继续围绕 `Rank 51` 补 intake / admission wording。

### 3) 最近 strategy review
- 最近一条有效 review：`2026-03-18_0720_strategy-review.md`
- 当时判断：`Rank 50` 是下一个 fresh Scout 主资源位。
- 到本轮为止，`Rank 50` 与 `Rank 51` 都已按允许预算完成并 park，因此 `07:20` 的排班已经过期，必须把板子切回 fresh intake。

### 4) 当前 cron 列表（重点）
- `bot3-momentum-auto-opt-13m`：健康，最近已真实执行 `Rank 50 park -> Rank 51 clean replication -> Rank 51 park`。
- `momentum-narrow-paper-lanes-20m`：健康；`manual_narrow_paper_last_run_summary.json @ 2026-03-18T09:16:32Z` 显示 `new_closed_trades_appended=0`，当前没有新的 `P3 status-changing event`。
- `bot7-quant-digest-30m`：本轮前最近一次有用新 source 仍是 `2026-03-18 07:34 UTC` 的 `Rank 51` 对应 digest；本轮没有新的 fresh source 已自动进入 queue。
- `bot6-park-reframe-2h`：健康，但它只是低频派生假设队列，不自动改变当前 desk 排班。
- `bot2-strategy-review-40m`：本 job 当前正在执行；上一些 run 有平台侧 delivery error，但不构成当前 desk judgement 的新证据。

## Desk verdict（本轮必须回答的 5 个问题）

### 1. 谁坐 `Paper Seat`？
- **`EMA baseline family / EMA-PSAR raw alpha`**。
- 当前状态：**`running paper / waiting_not_due`**。
- 最新 due guardrail 直接证据：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A股三条 lane -> 2026-03-19 07:00 UTC`
- 结论：当前 `EMA` 的 blocker 只是 **market clock**，不是漏跑或 admission 退化；因此 bot3 在 `Run 1` 只能做 `due-check only`，不能伪造 paper refresh。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 理由：
  1. 当前没有任何候选完成到足以讨论 `P4 tiny-live review candidate` 的阶段；
  2. `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 都属于 **`P3 narrow paper pilot / continuity 托管位`**，不是当前 live challenger；
  3. `Rank 50 / Rank 51` 都已经被最小 clean replication 压回 `park / evidence pool`；
  4. 不能为了“桌上必须有 live challenger”而把已 bench / 未升格对象重新拔高。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **严格说：当前没有正在存活复刻中的 active Scout 候选。**
- 当前更诚实的读法是：
  - `Rank 50 / chanlun-pro structural reclaim gate` -> 已完成最小 clean replication，**`park / evidence pool`**；
  - `Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate` -> 已完成最小 clean replication，**`park / evidence pool`**；
  - 因此 `Scout Seat` 当前应重置为 **fresh paper / repo based intake queue**，而不是假装还有 active replication 在跑。
- 若 fresh intake 这一轮也拿不到合格 source，当前 derived/fallback 顺序更诚实地应读作：
  - **`Rank 35b > Rank 16b > tiny-live plumbing`**
  - 其中：
    - `Rank 35b` 仍是最像“单轴、窄改写、可 honest 检查”的派生候选；
    - `Rank 16b` 与刚 park 的 `session-range / active-hours` 方向重合较高，因此只能排在 `Rank 35b` 后；
    - `Rank 27b` 已预算用尽；`Rank 32b` 属 `P3 continuity`，不该重新抢回 `Scout Seat`。

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 50 / chanlun-pro structural reclaim gate` -> **`P0`**（`minimal clean replication done -> park / evidence pool`）
- `Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate` -> **`P0`**（`minimal clean replication done -> park / evidence pool`）
- 当前 fresh intake 新 source -> **尚未认领 / 不在分级表内**（下一轮 `Run 2` 先认领 1 条，再决定是否进入 `P1`）
- `Rank 35b` -> **候补派生假设 / fallback only**（尚未正式重新 admit，不应抢在 fresh intake 前）
- `Rank 16b` -> **候补派生假设 / fallback only**（与 `Rank 48` 轴重合较高）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` -> **`P3`**（`narrow paper pilot / continuity only`）
- **当前 `P1` 为空，`P2` 为空，`P4` 为空。**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 — `EMA due-check only`**
   - 只确认是否出现新的 `due-now / overdue` bar；若仍 `waiting_not_due`，立刻切走，不空转。
2. **Run 2 — fresh paper/repo intake**
   - 严格按 `7.10` 先查：`docs/RECENT_PAPER_SEEDS.md` -> `research/quant_digests/INDEX.md` -> `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
   - 只认领 **1 条新的 `5m / 15m crypto` source**，并先做 `source intake + 两条轻量诚实守门`：
     - 能否冻结成 `trade on / trade off`
     - 是否存在明显 `lookahead / repaint / leakage`
3. **Run 3 — 条件式继续，不提前空转到 continuity**
   - 若 `Run 2` 认领到的新 source 已 `guard-passed` 且 `EMA` 仍 `waiting_not_due`，则 **立刻给这条新 source 1 次最小 clean replication**；
   - 若 `Run 2` 这轮仍真实 exhausted，则再比较：**`Rank 35b > Rank 16b > tiny-live plumbing`**；
   - 当前没有理由让 `Rank 2 / 17 / 29 / 32b` 这些 `P3` 托管位重新抢占 `Run 3`。

## active Scout 边际价值比较（本轮必须显式做）

### A. 当前 active fast-lane 候选
- **空集合。**
- 原因：`Rank 50 / 51` 都已经用完允许预算并给出 hard verdict，不能再伪装成 active `P1 / P2`。

### B. 当前 fallback / derived 队列
1. **`Rank 35b` 最高**
   - 单轴足够窄：删掉 `VWAP reclaim`，保留 `higher-tf bias + RSI pullback reclaim`；
   - 比继续磨 `Rank 50 / 51` 的失效 intake wording 更有边际价值；
   - 但依旧只能排在 fresh intake 之后。
2. **`Rank 16b` 次之**
   - 它本质上仍靠 `active-hours / session-range break/retest gate` 这条轴；
   - 与刚 park 的 `Rank 48` 方向相近，边际新增信息较低。
3. **`tiny-live plumbing` 继续最后**
   - 当前 `Live Seat` 仍空席，且没有新的 execution surface / promoted challenger；
   - 除非 fresh intake 与 derived queue 本轮都拿不到合格对象，才轮得到它。

## strongest evidence
- `EMA` 最新 due guardrail 全部显示 **`waiting_not_due`**，说明 `Paper Seat` 只是被 market clock 阻塞，不是漏跑。
- `Rank 51` 已完成最小 clean replication，并在成本后继续深负、`positive_asset_ratio=0/3`，因此没有诚实理由继续留在 queue。
- `manual_narrow_paper_last_run_summary.json @ 09:16 UTC` 显示 `new_closed_trades_appended=0`，说明当前没有新的 `P3 continuity` 事件值得 bot3 抢回去做。

## weakest / should-park lines
- 最不该继续高估的是把 `Rank 50 / 51` 说成“还差一轮就可能升格”的 active Scout；它们都已经给出 hard verdict。
- 同样不该误用的是把 `Rank 2 / 17 / 29 / 32b` 这些 `P3` 托管位误写成新的 seat；当前它们只是低频 continuity，不是 desk 主资源位。

## TODO / web / cron 的最小必要调整
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`**：
  - 在 `Scout Seat` 权威区补了 `09:21` 之后的当前 authoritative 读法：fast-lane 上无 surviving active `P1 / P2`；fallback 顺序改读为 `fresh intake -> Rank 35b > Rank 16b > tiny-live plumbing`。
  - 在 `Next 3 bot3 runs` 区新增 `2026-03-18 09:25 UTC` authoritative 补充：
    - `Run 1 = EMA due-check only`
    - `Run 2 = fresh paper/repo intake`
    - `Run 3 = 若新 source guard-passed 则给 1 次最小 clean replication；否则再比较 Rank 35b > Rank 16b > tiny-live plumbing`
- **cron**：本轮不改。当前不是节奏设计变化，只是 authoritative board 校准。

## reader-facing 同步
- 这轮 verdict / 排兵布阵已有变化，因此已同步到至少一个网页可见落点：
  - `docs/TODO.md` 顶部作战板（并将重建 `reports/site/plans/momentum_todo.html` / `plans/report.html`）

## Commit
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，本轮不安全 mixed commit。
