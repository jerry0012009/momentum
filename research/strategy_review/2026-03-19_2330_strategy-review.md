# 2026-03-19 23:30 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due（Crypto 1d+1wk 已进入 due_soon，约 28 分钟后到点）** 占位；`Live Seat` 继续 **暂空**；`Scout Seat` 当前仍应优先给 **`Rank 102 / retest 后重破 impulse extreme continuation gate`** 那 1 次真正会改变 verdict 的便宜诚实检查，`Rank 103 / confirmed extremum honest fib anchor` 保持紧邻 reserve。`Rank 17` 虽出现 `2` 笔 closed-trade append，但当前仍只算 **P3 hosted sidecar**，不抢默认主资源位。

## 本轮先检查了什么
- repo 状态：
  - `branch = master`
  - `git status --short | wc -l = 1592`
- 最近 optimization logs：
  - `2026-03-19_2315_rank102-clean-replication.md`
  - `2026-03-19_2258_rank102-impulse-rebreak-intake.md`
  - `2026-03-19_2233_rank101-volume-drydown-clean-replication.md`
  - `2026-03-19_2212_rank101-volume-drydown-intake.md`
  - `2026-03-19_2200_rank100-fib-depth-clean-replication.md`
- 最近 strategy reviews：
  - `2026-03-19_2235_strategy-review.md`
  - `2026-03-19_2137_strategy-review.md`
  - `2026-03-19_2055_strategy-review.md`
- 当前 cron（只记与 desk 相关的 state）：
  - `bot2-strategy-review-40m` enabled / running
  - `bot3-momentum-auto-opt-13m` enabled / ok
  - `momentum-narrow-paper-lanes-20m` enabled / 最近一轮 ok
  - `bot7-quant-digest-30m` enabled / running
  - `bot6-park-reframe-2h` enabled / ok
  - 旁路注意：`Rank32b live maintenance` 仍 `lastStatus=error`（`rg: command not found`），但这不是当前 desk 主资源位判断
- `Paper Seat` 再次实际核对：
  - 命令：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（`EXIT_CODE=2`）
  - 当前最近 due：**`Crypto 1d+1wk（BTC/ETH/SOL） -> due_soon / 约 28 分钟后到点`**
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T23:03:00Z`
  - `new_closed_trades_appended = 2`
  - `manual_narrow_paper_status.csv` 显示：两笔 append 都落在 **`Rank 17 / pullback recovery confirmation`**，并在 `22:45 UTC` 同步出现新的 open short
  - 结论：这是**真实 status-changing event**，但当前 ledger / status 已由专属 narrow-paper cron 接住，暂时只配当 **low-frequency sidecar / brief summary**，不自动挤掉 `Rank 102` 或即将到点的 `EMA`
- 最新 fresh source / backlog（用于本轮重排）：
  - `2026-03-19_2329_prebreak-higherlow-pressure-ladder-context-gate.md`
  - `2026-03-19_2227_post-break-signflip-density-gate.md`
  - `2026-03-19_2220_confirmed-extremum-honest-fib-anchor.md`
  - `2026-03-19_2154_orb-impulse-rebreak-followthrough-gate.md`

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due（due_soon）`**。
- 更直白地说：当前不是整桌等待，而只是 `EMA` 还在等下一根 completed bar；在到点前，bot3 不能空转。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 102` 目前只到 **`P1 / one cheap honesty check left`**，还没过 `Light Stability Pack`；
  2. `Rank 103` 仍只是 **`P0 / fresh repo reserve`**；
  3. `Rank 100 / 101` 已在最小 clean replication 后压回 **`park / evidence pool`**；
  4. `Rank 17 / 2 / 29 / 32b` 虽然仍在跑 hosted lanes，且 `Rank 17` 刚有 `2` 笔 closed-trade append，但它们都还是 **`P3 continuity`**，不是新的 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 102 / retest 后重破 impulse extreme continuation gate`
- **当前紧邻 reserve：**
  - `Rank 103 / confirmed extremum honest fib anchor`
- **当前 paper reserve：**
  - `post-break sign-flip density`
- **当前 fresh backlog（不 queue-facing）：**
  - `prebreak higher-low pressure ladder context gate`
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81`
- **当前 hosted / sidecar only：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 102 = P1`**（`clean replication 已完成 / one cheap time-stability check left`）
- **`Rank 103 = P0`**（`fresh repo reserve / source intake next if Rank 102 parks`）
- **`post-break sign-flip density = P0`**（`fresh paper reserve`）
- **`prebreak higher-low pressure ladder context gate = P0`**（`fresh repo backlog / context-only for now`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 101 / Rank 100 / Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 = P0`**（`park / evidence pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 继续盯 `Crypto 1d+1wk` 的 due-soon 窗口；
   - 若脚本仍返回 `waiting_not_due`，必须立刻切 Run 2，不得空转。
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 102 1 次 truly verdict-changing 的便宜诚实检查`**
   - 默认优先：**时间稳定性**（最近 / 较早两半窗拆分）
   - 目标：直接回答这条线是更像 `promote_to_P2` 还是 `park`
3. **`Run 3 = 优先级分支`**
   - **第一优先：**若 `Crypto` lane 已转为 `due-now / overdue`，先执行 **EMA guarded refresh**；
   - **否则：**不再继续给 `Rank 102` 第三轮近义检查，而是按 Run 2 结果直接收口：
     - 若 Run 2 已把 `Rank 102` 压回 `park`，则切 **`Rank 103 / confirmed extremum honest fib anchor`** 的 source intake；
     - 若 Run 2 没 park 且还没到 due-now，则直接做 `Rank 102` 的 **`promote_to_P2 / park`** 二选一收口；
   - 只有这一层也 exhausted，才允许回退到 `post-break sign-flip density > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 102 / impulse re-break`**
   - 当前排第一，因为它已经做完 clean replication，只剩那 **1 次真正会改变 verdict 的 cheap check**；
   - 继续磨旧 write-up 没价值，但直接回答 `P2 / park` 还有边际价值。
2. **`Rank 103 / confirmed extremum honest fib anchor`**
   - 当前排第二；它解决的是 `Fib` 锚点“别画早”的 honest-anchor 问题，价值真实，但仍低于先把 `Rank 102` 收口。
3. **`post-break sign-flip density`**
   - 当前排第三；它更像 hold-quality / post-break 管理层 overlay，不该先于两条 repo 线抢主资源。
4. **`prebreak higher-low pressure ladder context gate`**
   - 当前排第四；`23:29 UTC` 的 digest 已明确它更像 **retest context feature**，不是独立入场硬门，因此先留 backlog，不 queue-facing。
5. **`P3 continuity sidecar`**
   - 尽管 `Rank 17` 刚有 `2` 笔 closed-trade append，但当前 ledger/status 已由专属 cron 接住，且没有异常写回需求；
   - 在 `Rank 102` 仍未收口、且 `EMA` close 只剩约半小时的窗口里，它应继续排在 sidecar，而不是新主资源位。

## 当前 strongest evidence
1. **EMA due-check 再查仍是 `waiting_not_due`，但 Crypto close 只剩约 28 分钟**：说明 `Paper Seat` 还没到点，但下一个 close 已经逼近，`Next 3` 不能再假装离 due 很远。
2. **`Rank 102` 已完成 clean replication，且规则上仍剩 1 次合法 cheap check**：按 desk 纪律，这一轮最值钱的 Scout 动作就是把它做成 `P2 / park` 的分水岭。
3. **`manual_narrow_paper_last_run_summary.json` 已出现 `new_closed_trades_appended=2`**：这证明 hosted P3 lane 不是死寂，但当前它更像 status sidecar，不足以盖过 `Rank 102 + 临近 EMA close`。
4. **`23:29 UTC` 新 digest 已把 higher-low ladder 明确压成 context feature**：因此当前不该被它带偏去新开一条 queue-facing 主线。

## 当前 weakest / should-stay-park lines
- **`Rank 100 / fib-depth shallow-mid`**：已 park，只留 honesty / ordering note。
- **`Rank 101 / 3-step volume dry-down`**：已 park，只留 long-side hold-quality / short-veto note。
- **旧 `P1 evidence_pool`（`Rank 93 / 90 / 91 / 82 / 80 / 81`）**：当前边际价值低于 `Rank 102 收口` 与 `Rank 103 reserve`。
- **把 `Rank 17` append 误写成新 seat**：这是当前最该避免的误读；它只是 hosted P3 continuity 的 status event。

## TODO / roadmap / web / cron 的改动或建议
- **已对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小必要更新**：
  - 新增 `2026-03-19 23:30 UTC（bot2 desk review）` 补充；
  - 明确写死：`Paper Seat = EMA / waiting_not_due（due_soon）`、`Live Seat = 暂空`、`Scout Seat = Rank 102`；
  - 把 `Rank 17` 的 `2` 笔 append 明确归类为 `P3 continuity sidecar`，不误写成新 seat；
  - 把 `Next 3` 更新成：`EMA due-check` -> `Rank 102 cheap check` -> `EMA due-now refresh / Rank102收口 / Rank103 intake` 的动态优先级。
- **本轮不改 cron。**
- **reader-facing 落点已满足**：`TODO` 顶板已同步最新 judgment；后续刷新首页镜像即可。

## 风险与不确定性
- `Rank 102` 当前仍可能在时间稳定性后被直接压回 `park`；不要预设它会自然升到 `P2`。
- `Rank 103` 当前还是 reserve；只有在 `Rank 102` park 或 due 窗口未到时，才轮到它。
- `Rank 17` 的 `2` 笔 append 当前看起来只是正常 hosted continuity；若下一轮出现 ledger/page 异常，再考虑 low-frequency health-check，不要提前把它升级成主资源。
- `Rank32b live maintenance` 的 `rg` 缺失错误仍在，但它属于旁路维护问题，不应污染当前 bot2 desk 排兵布阵。
