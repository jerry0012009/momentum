# 2026-03-19 21:37 UTC bot2 strategy review

## 本轮一句话判断
本轮 **desk verdict 不变**：`Paper Seat = EMA / running paper / waiting_not_due`，`Live Seat = 暂空`，`Scout Seat = fib-depth shallow-mid admission gate reserve（进入 queue-facing 时先拿 Rank 100）`。`Rank 99 / CLV` 已在 `21:30 UTC` 的时间稳定性检查后正式压回 `park / evidence pool`，因此当前 bot3 默认不该再围着 CLV 收口，而应直接切到 **`Rank 100 / fib-depth shallow-mid` source intake**；紧邻后备才是 **`Rank 101 / 3-step volume dry-down long-bias gate`**。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1565`，工作区仍有大量既有脏文件；本轮不做无关混改。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_2130_rank99-time-stability-park.md`
  - `2026-03-19_2053_rank99-clv-clean-replication.md`
  - `2026-03-19_2027_rank99-clv-intake.md`
  - `2026-03-19_2014_ema-us-due-refresh.md`
- 最近 strategy reviews（重点核对）：
  - `2026-03-19_2055_strategy-review.md`
  - `2026-03-19_1959_strategy-review.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled，当前正在运行
  - `bot3-momentum-auto-opt-13m` enabled，但上一轮 `lastRunStatus=error`，报错原因为 **`rg: command not found`**
  - `momentum-narrow-paper-lanes-20m` enabled，最近一次运行正常
  - `bot6-park-reframe-2h` enabled
  - `bot7-quant-digest-30m` enabled，但上一轮也因 `rg` 缺失报错
- `Paper Seat` guardrail：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（exit code `2`）
  - 当前最近 due：**`Crypto 1d+1wk（BTC/ETH/SOL） -> due_soon / 约 2.4 小时`**
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T21:33:47Z`
  - `new_closed_trades_appended = 0`
  - 结论：当前没有新的 `P3 status-changing event` 需要挤掉 Scout 主线。
- 最近 fresh source / reserve（用于比较 Scout 边际价值）：
  - `2026-03-19_2041_fib-depth-shallow-mid-admission-gate.md`
  - `2026-03-19_2009_abnormal-volume-drydown-long-bias-gate.md`

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 执行含义：这不是整桌等待；当 `EMA` 仍是 `waiting_not_due` 时，bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 100 / fib-depth shallow-mid` 目前还只是 **fresh repo reserve / source intake next**，尚未进入 `clean replication`；
  2. `Rank 101 / 3-step volume dry-down` 也只是 **fresh reserve**，且当前更像 long-side hold-quality gate，不是可直接升格的 shared live challenger；
  3. `Rank 99 / CLV` 已在时间稳定性后压回 **`park / evidence pool`**；
  4. 旧 `Rank 93 / 90 / 91 / 82 / 80 / 81` 仍只是 **`P1 evidence_pool / budget used`**；
  5. `Rank 78 / 17 / 2 / 29 / 32b` 仍属于 **`P3 hosted lanes`**，不是新的 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `fibo71-bot / fib-depth shallow-mid admission gate reserve`（进入 queue-facing 时先拿 `Rank 100`）
- **当前紧邻后备：**
  - `3-step volume dry-down long-bias gate reserve`（进入 queue-facing 时拿 `Rank 101`）
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81`
- **当前已 park、不得回抢主资源：**
  - `Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 100 / fib-depth shallow-mid admission gate reserve = P0`**（`fresh repo intake next`）
- **`Rank 101 / 3-step volume dry-down long-bias gate reserve = P0`**（`fresh repo intake reserve / long-side hold-quality gate`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 = P0`**（`park / evidence pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 优先盯 `Crypto 1d+1wk` 的 due-soon 窗口；
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 100 / fib-depth shallow-mid admission gate reserve 的 source intake`**
   - 只做 `1 个主点 + 1 个紧邻子点`；
   - 先冻结 `trade on / trade off` 与 `no lookahead / no leakage` 两条轻量诚实守门。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 100` guard-pass，则只给 **1 次最小 clean replication**；
   - 若 `Rank 100` 在 intake 直接 hard-fail / exhausted，则切 **`Rank 101 / 3-step volume dry-down long-bias gate reserve`** 的 source intake；
   - 只有 fresh reserve 这一层也 exhausted，才允许回退到 `旧 P1 evidence_pool > parked ranks > P3 continuity > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 100 / fib-depth shallow-mid admission gate reserve`**
   - 当前排第一，因为 `Rank 99` 已在 truly verdict-changing 的时间稳定性里给出 `park`，这条 fresh repo reserve 变成当前最接近减少真实 gate 的新主点；
   - 它直接回答当前 `Fib retest_hold` 主线最实际的问题：15m 回踩默认应优先 `38-62` 还是更深的 `62-79 / 71-79`。
2. **`Rank 101 / 3-step volume dry-down long-bias gate reserve`**
   - 当前排第二，因为它对 `Fib / EMA long-side hold-quality` 仍有价值；
   - 但目前明显更偏 long-side、且保留率偏稀，边际价值低于更能直接改变 `Fib admission ordering` 的 `Rank 100`。
3. **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前只排第三；继续磨它们更像补近义 admission 写法，边际价值低于两条 fresh reserve。
4. **`Rank 99 / 98 / 97 / 96 / 95 / 92 / 94 park / evidence pool`**
   - 当前只排第四；这些线都已经给过足够诚实的最小 verdict，不应重新回抢主资源。
5. **`P3 continuity` 与 `tiny-live plumbing`**
   - 当前继续只排后手；既没有 `due-now / overdue` paper refresh，也没有新的 `P3 status-changing event`，不该插队。

## 当前 strongest evidence
1. **EMA guardrail 再查仍是 `waiting_not_due`，最近 due 为 `Crypto 1d+1wk / 约 2.4h`**：说明 `Paper Seat` 继续诚实 keep。
2. **`Rank 99` 已在 `21:30 UTC` 的时间稳定性检查后正式 `park`**：当前 Scout 主线必须切走，不能再假装它还在 active queue 里。
3. **`fib-depth` 与 `dry-down` 两条 fresh reserve 已就位**：说明即便 `Rank 99` fail，Scout 也没有 exhausted，更不该回头续命旧 `P1 evidence_pool`。
4. **`manual_narrow_paper_last_run_summary.json @ 21:33:47Z = new_closed_trades_appended=0`**：说明 `P3 continuity` 仍无插队理由。

## 当前 weakest / should-park lines
- **`Rank 99 / CLV`**：时间稳定性已经把这条线的 active Scout 身份判掉；后续只保留 short-biased bar-quality 线索，不再占主资源。
- **旧 `P1 evidence_pool`（`Rank 93 / 90 / 91 / 82 / 80 / 81`）**：当前边际价值落后于两条 fresh reserve。
- **把 `dry-down` 误写成 short-shared trigger**：这仍是当前最该避免的偷渡；它更适合 long-side hold-quality / short-veto 语义。

## 建议优先级 Top 1~3
1. **下一轮 bot3 直接切 `Rank 100 / fib-depth shallow-mid` source intake，不再围绕 `Rank 99` 收口。**
2. **若 `Rank 100` intake 通过，就立刻给它 1 次最小 clean replication；若不过，就切 `Rank 101`，不要回头续命旧 `P1 evidence_pool`。**
3. **继续保持 `Live Seat = 暂空`，并把 `P3 continuity` 严格留在 hosted / low-frequency 层。**

## TODO / roadmap / web / cron 的改动或建议
- **本轮不改 `docs/TODO.md`。**
  - 原因：顶板在 `21:30 UTC` 已由最新 bot3 结果同步到位，当前席位判断、Scout 分级与 `Next 3` 顺序都仍然准确；本轮属于**无 seat verdict 变化的巡检确认**。
- **本轮不改 cron。**
  - 但应记录一个运行风险：`bot3-momentum-auto-opt-13m` 与 `bot7-quant-digest-30m` 最近都出现了 `rg: command not found`。这还**没有**改变 desk 排班，但若下一轮继续复现，应优先把 shell 搜索口径收敛到系统现有的 `grep/find`，避免无意义的执行性报错继续吞轮次。
- **reader-facing 落点本轮不新增。**
  - 原因：当前 reader-facing 判断已在 `docs/TODO.md` 顶板与 `Rank 99 time-stability` 页面里可见，本轮只是确认不翻盘。

## 风险与不确定性
- `Rank 100 / fib-depth shallow-mid` 目前仍只是 reserve，不是隐性 `P1 / P2`；若 source intake 的两条轻量诚实守门不过，应直接切 `Rank 101`。
- `Rank 101 / dry-down` 当前仍带有明显 long-side 与稀疏度特征，不应被误包装成多空对称 shared gate。
- bot3 / bot7 最近的 `rg` 缺失报错还没演变成桌面判断变化，但它确实可能影响执行节拍；若重复出现，后续需要最小修正执行习惯或 prompt。
- repo 工作区继续很脏；本轮仍避免混改，只做 review 记录、首页刷新与邮件这条最小链路。
