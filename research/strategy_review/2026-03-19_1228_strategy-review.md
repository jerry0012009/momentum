# 2026-03-19 12:28 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 当前明确由 **`Rank 89 / outside-close -> back-inside-close failure verdict`** 占位，下一手应直接做 **minimal clean replication**，而不是把“已完成 intake”误写成一个独立 run。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1408`，工作区仍有大量既有脏文件；本轮只做顶板最小必要写回、strategy review 记录、首页刷新与邮件，不混改无关文件。
- 最近 optimization logs（本轮重点核对）：
  - `2026-03-19_1219_rank89-outside-inside-intake.md`
  - `2026-03-19_1201_rank88-clean-replication-park.md`
  - `2026-03-19_1149_rank88_macro_event_overlay_intake.md`
  - `2026-03-19_1126_rank87-clean-replication-park.md`
- 最近 strategy review：
  - `2026-03-19_1150_strategy-review.md`
  - `2026-03-19_1107_strategy-review.md`
  - `2026-03-19_1012_strategy-review.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled 且本轮正在运行；
  - `bot3-momentum-auto-opt-13m` enabled，最近一轮仍是 `12:19 UTC / Rank 89 intake`；
  - `momentum-narrow-paper-lanes-20m` enabled，最近 summary `2026-03-19T12:23:11Z`，`new_closed_trades_appended=0`；
  - `bot7-quant-digest-30m` enabled；
  - `bot6-park-reframe-2h` enabled，但最近一轮报错仍是 `rg: command not found`，不改变本轮席位判断。
- `Paper Seat` guardrail：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**
  - 当前全 desk 仍无 `due-now / overdue` lane
  - 最近 due 点约为：
    - `美股 1d+1wk -> 约 7.5h`
    - `Crypto 1d+1wk -> 约 11.5h`
    - `创业板ETF 1d -> 约 18.5h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是 guardrail 明确给出的真 waiting，不是整桌等待；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 89` 当前只到 **`P1 / guard-passed / minimal clean replication next`**；
  2. `Rank 88 / 87 / 86 / 85 / 84 / 83` 已明确回到 **`P0 park / evidence_pool`**；
  3. `Rank 82 / 80 / 81` 继续只是 **`P1 evidence_pool`**，不值得重新吃主资源；
  4. `Rank 78 / 17 / 2 / 29 / 32b` 是 `P3 narrow paper continuity` 托管位，不应误写成 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 active 主资源位：**
  - `Rank 89 / outside-close -> back-inside-close failure verdict`
- **当前紧邻后备：**
  - `close-range compression asymmetry`
- **当前只留证据池、不再默认续命：**
  - `Rank 82 / ETF lead regime gate`
  - `Rank 80 / first-30m impulse quality gate`
  - `Rank 81 / RS semivariance asymmetry gate`
  - `Rank 88 / macro-event blackout + size-down risk overlay`
  - `Rank 87 / volume-clock + CS spread interaction gate`
  - `Rank 86 / SignalPro penetration×ATR admission`
  - `Rank 85 / fresh pullback -> reclaim re-arm gate`
  - `Rank 84 / volume-price interaction admission layer`
  - `Rank 83 / Fib trend-strength admission layer`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / 17 / 2 / 29 / 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 89 / outside-close -> back-inside-close failure verdict = P1`**（`source intake / 两条轻量诚实守门已过；minimal clean replication next`）
- **`close-range compression asymmetry = P0`**（`fresh digest backlog / source intake pending`）
- **`Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / 不再默认续命`）
- **`Rank 88 / 87 / 86 / 85 / 84 / 83 = P0`**（`park / evidence_pool`）
- **`Rank 78 / 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / low-frequency hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得伪造 refresh，也不得空转。
2. **`Run 2 = Rank 89 / outside-close -> back-inside-close failure verdict minimal clean replication`**
   - 统一保持 `signal 当根及之前数据 + next-bar open + no-overlap`；做完直接回答 **`promote_to_P2 / park`**。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 89` clean replication **没有被判死刑**，则只给它 **1 个 truly verdict-changing 的 Light Stability Pack**（默认时间稳定性），直接回答 **`keep_P2 / promote_to_P3 / park`**；
   - 若 `Rank 89` clean replication **直接 hard-fail / park**，则切到 **`close-range compression asymmetry source intake + 两条轻量诚实守门`**；
   - 只有这一层也 exhausted，才允许回退到 `Rank 82 / 80 / 81 evidence_pool > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 89 / outside-close -> back-inside-close failure verdict`**
   - 当前排第一，因为它已经完成 `source intake + honesty gate`，离改变层级判断最近；而且它更像 `post-break failure verdict / re-entry veto`，不是重新放大 breakout 追涨叙事。
2. **`close-range compression asymmetry`**
   - 当前排第二，作为紧邻 fresh backlog 保留；但在 `Rank 89` 还没跑完那唯一一手 minimal clean replication 之前，不应并开抢跑。
3. **`Rank 82 / 80 / 81`**
   - 继续只留 `P1 evidence_pool`；它们都已经用掉最小诚实预算，再磨更像补文案，不像减少真实 gate。
4. **`Rank 78 / 17 / 2 / 29 / 32b`**
   - 继续只算 `P3` 托管位；本轮没有新的 status-changing event，不该插队。
5. **`tiny-live plumbing`**
   - 当前继续只作更后层 fallback，不该在 fresh Scout 仍有明确动作时抢前排。

## 当前 strongest evidence
1. **EMA guardrail 再次实查仍是 `waiting_not_due`**：当前没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 89` 已完成 source intake + 两条轻量诚实守门**：当前已从 fresh backlog 升到 **`P1 / minimal clean replication next`**，是唯一值得拿下一手主资源的 active Scout 候选。
3. **`Rank 88` 已在 clean replication 后如实 park**：避免了继续把宏观 overlay 误写成 active Scout 主线。
4. **`P3` 托管层当前无新异常**：`manual_narrow_paper_last_run_summary.json @ 12:23 UTC` 仍是 `new_closed_trades_appended=0`，没有理由让 `Rank 78 / 17 / 2 / 29 / 32b` 抢回主资源。

## 当前 weakest / should-park lines
- **`Rank 88 / macro-event blackout + size-down risk overlay`**：最小 clean replication 已证明事件窗覆盖过少，不足以支撑 shared overlay admission，应继续视为 **park**。
- **`Rank 87 / volume-clock + CS spread interaction gate`**：clean replication 的改善主要来自 retention 断崖式下降，应继续视为 **park**。
- **`Rank 86 / SignalPro penetration×ATR admission`**：时间稳定性检查后已明确 **park**。
- **`Rank 85 / fresh pullback -> reclaim re-arm gate`**：最小 clean replication 已给完，继续应视为 **park**。

## TODO / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 12:28 UTC（bot2 desk review）` 补充；
  - 明确当前 `Paper Seat / Live Seat / Scout Seat` 维持 `EMA / 暂空 / Rank 89`；
  - 把 `Next 3` 从“`Run 2 = 已完成 intake`”修正为真正可执行的：`Run 2 = Rank 89 minimal clean replication`、`Run 3 = Rank 89 stability or close-range backlog`。
- **本轮不改 cron。**
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮排兵布阵变更；配合本轮 strategy review 与既有 `Rank 89` intake 页面，足够对外可见。

## 风险与不确定性
- `Rank 89` 当前仍只到 `P1`，不是升格结论；下一手必须是 **1 次最小 clean replication**，而不是继续补 intake wording。
- 若 `Rank 89` 的改善主要来自极端缩样本，而不是更诚实地识别坏 break，它也应快速压回 `park`，不要因为“failure verdict”叙事好听而续命。
- 当前 repo 工作区依旧很脏；本轮继续避免混改，只做顶板、review、首页与邮件这条最小链路。
