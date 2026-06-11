# bot3 auto optimization log — 2026-03-22 23:16 UTC

## 本轮入口
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- 严格按 `Next 3 bot3 runs` 执行，且本轮只保留 **1 个主点 + 1 个紧邻子点**。

## Run 1 / EMA due-check first
- 执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：当前 **没有 `due-now / overdue` lane**。
- 最靠前 lane：`Crypto 1d+1wk（BTC/ETH/SOL）`，状态 `due_soon`，约 **43 分钟后**到点。
- 结论：`Paper Seat / EMA` 仍是 **真实 `waiting_not_due`**，本轮不得伪造 refresh，必须立刻切到下一个允许动作。

## Run 2 / Hosted P3 continuity（事件驱动）
- 本轮未看到新的 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 证据。
- 结论：**跳过 Run 2**，不做近义健康检查重复劳动。

## Run 3 / Scout Seat（只选 1 个主点）
### 主点：切到 `fresh intake reserve = Rank 14b / directional-breadth-coherence long-side continuation veto`

选择原因：
1. 顶板已明确：若当前 `P1` 候选连续 2 轮没有层级变化、且没有新增 decisive evidence，**不得继续占用 Scout 主资源位**。
2. `Rank 140` 在最近两轮 family-board 最小定锚后，结论仍是 `guard_failed / keep_P1 / budget used`，本轮不能继续把它当默认主点。
3. 当前 active Scout 里的 `Rank 125 / 112 / 111` 也都已更接近 `keep_P1 / evidence_pool / budget used`，继续回头磨边际价值低。
4. `docs/PARK_REFRAME_QUEUE.md` 已有较新的 `derived_hypothesis_drafted`：
   - `Rank 14b`
   - 单一修改轴清楚：把原 `peer-basket same-direction confirmation` 改写为 **directional-breadth-coherence 的 long-side veto-only gate**；
   - 口径足够窄，符合当前 desk 对 fresh reserve 的要求。

### 紧邻子点：冻结这轮的最小执行口径
若下一轮 `EMA` 仍非 due-now，则优先只给 `Rank 14b` **1 次 source-intake / 最小 clean-replication 设计确认**，严格保持：
- 只测 `baseline vs veto-only`；
- 只做 `long-side`；
- 不顺手扩成 short / half-size / 多层 regime stack；
- 不与其他 Scout 候选并行打开。

## 本轮产出
- 新日志：`research/optimization_loop/2026-03-22_2316_rank14b-breadth-veto-reserve.md`
- 这轮没有重跑 paper refresh，也没有重开 hosted continuity；真实推进是把 Scout 主资源从已消费的 `P1` 候选切回一个更诚实的 fresh intake reserve，并把下一刀收窄到单轴 `Rank 14b`。

## 当前最诚实的 desk 读法
- `Paper Seat`：`EMA / running paper / waiting_not_due`（下一真实 close 前继续等待）
- `Live Seat`：暂空
- `Scout Seat`：本轮切换到 **`Rank 14b / directional-breadth-coherence long-side continuation veto`** 作为 fresh reserve 主点

## 给下一轮的最短提醒
- 若 `Crypto 1d+1wk` 到点并进入 `due-now / overdue`：先回 `Run 1` 做 EMA 真实 refresh。
- 若仍 `waiting_not_due`：不要回头继续磨 `Rank 140 / 125 / 112 / 111`，先按 `Rank 14b` 的单轴最小 intake/replication 继续。 
