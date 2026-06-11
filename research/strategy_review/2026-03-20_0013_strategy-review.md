# 2026-03-20 00:13 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 仍由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续 **暂空**；`Scout Seat` 当前应切到 **`Rank 103 / confirmed extremum honest fib anchor`**，`post-break sign-flip density` 做紧邻 reserve，`prebreak higher-low pressure ladder context gate` 留在 context-only backlog。`Rank 102` 已在 `23:38 UTC` 的时间稳定性检查后如实压回 `park / evidence pool`，因此不应再把主资源回退到它或更老的 `Rank 100 / Rank 101` 顺序。

## 本轮先检查了什么
- repo 状态：
  - `branch = master`
  - `git status --short | wc -l = 1598`
- 最近 optimization logs：
  - `2026-03-20_0009_ema-crypto-due-refresh.md`
  - `2026-03-19_2338_rank102-time-stability-park.md`
  - `2026-03-19_2315_rank102-clean-replication.md`
  - `2026-03-19_2258_rank102-impulse-rebreak-intake.md`
  - `2026-03-19_2233_rank101-volume-drydown-clean-replication.md`
- 最近 strategy reviews：
  - `2026-03-19_2330_strategy-review.md`
  - `2026-03-19_2235_strategy-review.md`
  - `2026-03-19_2137_strategy-review.md`
- 当前 cron（只记与 desk 相关的 state）：
  - `bot2-strategy-review-40m` enabled / running
  - `bot3-momentum-auto-opt-13m` enabled / ok
  - `momentum-narrow-paper-lanes-20m` enabled / ok
  - `bot7-quant-digest-30m` enabled / lastStatus=error（timeout）
  - `bot6-park-reframe-2h` enabled / ok
  - 旁路注意：`Rank32b live maintenance` 仍 `lastStatus=error`（`rg: command not found`），但这不是当前 desk 主资源位判断
- `Paper Seat` 当前实况：
  - `2026-03-20 00:09 UTC` 已真实执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - `Crypto 1d+1wk` due window 已被消化，`ema_paper_trading_refresh_history.csv` 累计到 `21` 条 completed-bar rows
  - 最新 `ema_paper_trading_due_guardrail_snapshot.csv`：全 desk 无 `due-now / overdue` lane；最近 due = `A股三条 lane -> 2026-03-20 07:00 UTC`
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T00:13:10Z`
  - `new_closed_trades_appended = 0`
  - 结论：当前没有新的 `P3 status-changing event` 可以插队

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 更直白地说：`Crypto` 的 due window 刚在 `00:09 UTC` 被诚实消化，接下来最近 due 是 `A股 07:00 UTC`；因此 `EMA` 现在是“真等时钟”，不是“假装有事可做”。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 103` 还只在 **`P0 / source intake next`**，尚未过 `clean replication`；
  2. `post-break sign-flip density` 仍只是 **`P0 / fresh paper reserve`**；
  3. `Rank 102` 已在 `23:38 UTC` 时间稳定性后如实压回 **`P0 / park`**；
  4. `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b` 虽属 hosted lanes，但仍只是 **`P3 continuity / sidecar`**，不是新的 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 103 / confirmed extremum honest fib anchor`
- **当前紧邻 reserve：**
  - `post-break sign-flip density`
- **当前 fresh backlog（context-only）：**
  - `prebreak higher-low pressure ladder context gate`
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81`
- **当前 hosted / sidecar only：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 103 = P0`**（`fresh repo reserve / source intake next`）
- **`post-break sign-flip density = P0`**（`fresh paper reserve`）
- **`prebreak higher-low pressure ladder context gate = P0`**（`fresh repo backlog / context-only for now`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 102 / Rank 101 / Rank 100 / Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 = P0`**（`park / evidence pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 重点盯 `A股三条 lane -> 2026-03-20 07:00 UTC`；
   - 若仍 `waiting_not_due`，不得空转。
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 103 / confirmed extremum honest fib anchor 的 source intake + 两条轻量诚实守门`**
   - 目标：明确 `trade on / trade off` 与 `no lookahead / no repaint / no leakage` 是否站得住。
3. **`Run 3 = 优先级分支`**
   - **第一优先：**若 `A股` lane 已转为 `due-now / overdue`，先执行 **EMA guarded refresh**；
   - **否则：**若 `Rank 103` guard-pass，则只给它 **1 次最小 clean replication**；
   - **若 `Rank 103` 在 intake 直接 hard-fail / exhausted**，则切 **`post-break sign-flip density`**；再之后才轮到 `prebreak higher-low pressure ladder context gate > 旧 P1 evidence_pool > P3 continuity > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 103 / confirmed extremum honest fib anchor`**
   - 当前排第一，因为 `Rank 102` 已 park 后，`Rank 103` 是最接近 queue-facing 的 fresh repo 候选；
   - 它解决的是 Fib 系列里最核心的诚实问题：锚点到底何时才算“确认过”，避免把尚未确认的 swing 事后画成完美回撤。
2. **`post-break sign-flip density`**
   - 当前排第二；它更像 post-break hold-quality / confirmation overlay，价值真实，但仍低于先把 `Rank 103` 从 intake 推到可复制阶段。
3. **`prebreak higher-low pressure ladder context gate`**
   - 当前排第三；最近 digest 已把它压成 context feature，不宜在这一拍先于 `Rank 103` 抢主资源。
4. **旧 `P1 evidence_pool`（`Rank 93 / 90 / 91 / 82 / 80 / 81`）**
   - 当前排第四；这些线都已 budget used，不应再默认续命。
5. **`P3 continuity sidecar`**
   - 当前 `new_closed_trades_appended=0`，没有新的 status-changing event，因此继续排在 sidecar，而不是主资源位。

## 当前 strongest evidence
1. **`00:09 UTC` 的 EMA refresh 真实消化了 crypto due window**：说明 `Paper Seat` 当前的确已回到 `waiting_not_due`，不是伪等待。
2. **`23:38 UTC / Rank 102` 已在时间稳定性检查后 park**：说明当前默认 Scout 主资源必须切换，不能再沿旧 `Rank 102 -> Rank 100` 惯性排班。
3. **`00:13 UTC` 的 narrow-paper 托管状态 `new_closed_trades_appended=0`**：说明当前没有新的 `P3` 事件足以插队。

## 当前 weakest / should-stay-park lines
- **`Rank 102 / impulse re-break`**：已 park，不再占主资源。
- **`Rank 100 / fib-depth shallow-mid` 与 `Rank 101 / volume dry-down`**：当前应视作旧 board 惯性残留，不应压过更新后的 `Rank 103`。
- **旧 `P1 evidence_pool`（`Rank 93 / 90 / 91 / 82 / 80 / 81`）**：当前边际价值低于 fresh intake。
- **把 `P3 continuity` 误写成新 seat**：此刻最该避免的误读。

## 建议优先级 Top 1~3
1. **先把 `TRADING DESK BOARD` 顶部顺序校正为 `EMA waiting_not_due -> Rank 103 intake`**。
2. **若下一拍 `EMA` 仍 waiting_not_due，bot3 只认领 `Rank 103` 这 1 条主点，不并开第二条 fresh candidate。**
3. **若 `Rank 103` 直接 hard-fail，再切 `post-break sign-flip density`，而不是回头续磨旧 `P1` 或 `P3 continuity`。**

## TODO / roadmap / web / cron 的改动或建议
- **已对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小必要更新**：
  - 新增 `2026-03-20 00:13 UTC（bot2 desk review）` 补充；
  - 把 `Scout Seat` 明确写回 **`Rank 103 / confirmed extremum honest fib anchor`**；
  - 把 `Rank 102` 正式归回 `P0 park / evidence pool`；
  - 把 `Next 3` 校正为：`EMA due-check` -> `Rank 103 intake` -> `EMA due-now refresh / Rank 103 clean replication / post-break sign-flip density reserve`。
- **本轮不改 cron。**
- **reader-facing 落点已满足**：`TODO` 顶板已同步最新 judgment；后续刷新首页镜像即可。

## 风险与不确定性
- `Rank 103` 目前还只是 intake next，不要预设它一定会比 `Rank 102` 更强。
- `post-break sign-flip density` 仍只是 reserve；只有 `Rank 103` 直接 hard-fail / exhausted，才应上位。
- `A股 07:00 UTC` 是下一个真实 due window；若 bot3 节拍正好压到 due-now，应先诚实消化 `Paper Seat`，再释放后续 Scout 动作。
- `bot7-quant-digest-30m` 当前一次 timeout，但这不应污染本轮 desk seat 判断。
