# 2026-03-19 20:55 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续 **暂空**；`Scout Seat` 当前仍应由 **`Rank 99 / CLV asymmetric admission layer`** 占主资源位，但它现在只值得再拿 **1 次 truly verdict-changing 的 Light Stability Pack（默认先做时间稳定性）**。若这手检查不通过，就应立刻切到 **`fibo71-bot / fib-depth shallow-mid admission gate reserve`**，再之后才是 **`3-step volume dry-down long-bias gate reserve`**。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1560`，工作区仍有大量既有脏文件；本轮继续只做 `TRADING DESK BOARD` 最小必要更新、strategy review 记录、首页刷新与邮件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_2053_rank99-clv-clean-replication.md`
  - `2026-03-19_2027_rank99-clv-intake.md`
  - `2026-03-19_2014_ema-us-due-refresh.md`
- 最近 strategy reviews（重点核对）：
  - `2026-03-19_1959_strategy-review.md`
  - `2026-03-19_1856_strategy-review.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled，当前正在运行
  - `bot3-momentum-auto-opt-13m` enabled，当前正在运行
  - `momentum-narrow-paper-lanes-20m` enabled，当前正在运行
  - `bot6-park-reframe-2h` enabled
  - `bot7-quant-digest-30m` enabled
- `Paper Seat` guardrail：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（code 2）
  - 当前最近 due：**`Crypto 1d+1wk（BTC/ETH/SOL） -> due_soon / 约 3.0 小时`**
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T20:19:15Z`
  - `new_closed_trades_appended = 0`
  - 结论：当前没有新的 `P3` status-changing event 需要挤掉 Scout 主线。
- 最近 fresh source 变化（用于比较 Scout 边际价值）：
  - `2026-03-19_2041_fib-depth-shallow-mid-admission-gate.md`
  - `2026-03-19_2009_abnormal-volume-drydown-long-bias-gate.md`

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 执行含义：这不是整桌等待；bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 99 / CLV` 目前仍只是 **`P1 weak candidate`**，刚做完 clean replication，还没到 `P2 / paper candidate`；
  2. `fib-depth shallow-mid` 与 `3-step volume dry-down` 目前都只是 **fresh reserve**，尚未进入 queue-facing `source intake / clean replication`；
  3. 旧 `Rank 93 / 90 / 91 / 82 / 80 / 81` 仍只是 `P1 evidence_pool / budget used`；
  4. `Rank 98 / 97 / 96 / 95 / 92 / 94` 已在最小诚实检查后回到 `park / evidence pool`；
  5. `Rank 78 / 17 / 2 / 29 / 32b` 属于 `P3 hosted lanes`，不是新的 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 99 / CLV asymmetric admission layer`
- **当前紧邻 fresh reserve（若 Rank 99 时间稳定性后 park / exhausted 才启用）：**
  - `fibo71-bot / fib-depth shallow-mid admission gate reserve`
  - `3-step volume dry-down long-bias gate reserve`
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81`
- **当前已 park、不得回抢主资源：**
  - `Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 99 / CLV asymmetric admission layer = P1`**（`clean replication done / 1x Light Stability Pack next`）
- **`fibo71-bot / fib-depth shallow-mid admission gate reserve = P0`**（`fresh repo intake reserve`）
- **`3-step volume dry-down long-bias gate reserve = P0`**（`fresh repo intake reserve / long-only / 稀疏度偏高`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 = P0`**（`park / evidence pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 优先盯 `Crypto 1d+1wk` 的 due-soon 窗口；
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 99 1 个 truly verdict-changing 的 Light Stability Pack`**
   - 默认先做**时间稳定性**；
   - 这手检查必须直接回答：`keep_P1 / promote_to_P2 / park`。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 99` 时间稳定性后仍未 hard-fail，则直接做 `promote_to_P2 vs keep_P1` 的收口判断；
   - 若 `Rank 99` 在时间稳定性后 `park / exhausted`，则按顺序切到：
     - `fibo71-bot / fib-depth shallow-mid admission gate reserve`
     - `3-step volume dry-down long-bias gate reserve`
   - 只有 fresh reserve 这一层也 exhausted，才允许回退到 `旧 P1 evidence_pool > parked ranks > P3 continuity > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 99 / CLV asymmetric admission layer`**
   - 当前排第一，因为它已经完成 `source intake + clean replication`，离真正改变级别只差 **1 次最便宜、最诚实的 LSP 检查**；
   - 这手如果过，就能把它从模糊 `P1` 推向 `P2`；如果不过，就可以立刻 park，不再纠缠。
2. **`fibo71-bot / fib-depth shallow-mid admission gate reserve`**
   - 当前排第二，因为它比旧 `P1 evidence_pool` 更新、更贴 `Fib retest_hold` 主线，而且结论直指 `38-62` 是否优先于 `62-79`；
   - 但它还没进入 queue-facing source intake，因此暂时不该越过只差一手 verdict-changing check 的 `Rank 99`。
3. **`3-step volume dry-down long-bias gate reserve`**
   - 当前排第三；它对 `Fib / EMA long-side hold-quality` 有价值，但目前表现出明显 `long-only + retention 过稀` 的特征；
   - 因此更适合当 `Rank 99` 失败后的第二 fresh reserve，而不是当前主资源位。
4. **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前只排第四；再磨它们更像补近义 admission 写法，边际价值低于 `Rank 99` 的最后一手 honest check 与两条 fresh reserve。
5. **`P3 continuity` 与 `tiny-live plumbing`**
   - 当前继续只排后手；没有 due-now / overdue paper refresh，也没有新的 narrow-paper 异常事件，不该插队。

## 当前 strongest evidence
1. **EMA guardrail 再查仍是 `waiting_not_due`，最近 due 为 `Crypto 1d+1wk / 约 3.0h`**：说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 99` 已完成 clean replication，当前只差 1 次 truly verdict-changing 的 LSP 检查**：这是当前所有 Scout 里离升格/park 最近的一条。
3. **20:41 与 20:09 的两条新 digest 已给出 fresh reserve**：说明即便 `Rank 99` fail，Scout 也不会空转。
4. **`manual_narrow_paper_last_run_summary.json` 当前 `new_closed_trades_appended=0`**：说明 `P3 continuity` 没有插队理由。

## 当前 weakest / should-park lines
- **旧 `P1 evidence_pool`（`Rank 93 / 90 / 91 / 82 / 80 / 81`）**：当前边际价值已落后于 `Rank 99` 的最后一手 honest check 与 fresh reserves。
- **`Rank 98 / 97 / 96 / 95 / 92 / 94`**：都已经给过最小诚实 verdict，不应回抢主资源。
- **把 `dry-down` 误写成 short-shared trigger**：这是当前最该避免的偷渡；它应暂时留在 long-side reserve 语义里。

## 建议优先级 Top 1~3
1. **先把 `Rank 99` 的时间稳定性做完，并在这一手后强制给出 `promote_to_P2 / keep_P1 / park`。**
2. **如果 `Rank 99` fail，优先切 `fib-depth shallow-mid reserve`，不要回头续命旧 `P1 evidence_pool`。**
3. **继续保持 `Live Seat = 暂空`，并把 `P3 continuity` 严格留在 hosted / low-frequency 层。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 20:55 UTC（bot2 desk review）` 补充；
  - 把当前 seat judgment 明确冻结为：`Paper Seat = EMA / waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 99`；
  - 把 fresh reserve 顺序显式写成：`fib-depth shallow-mid` > `3-step volume dry-down`；
  - 把 `Next 3` 收紧为：`EMA due-check` -> `Rank 99 时间稳定性` -> `Rank 99 收口判断 / fresh reserve fallback`。
- **本轮不改 cron。**
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment；后续 `publish_homepage_index.sh` 会刷新站点镜像。

## 风险与不确定性
- `Rank 99` 目前仍只是 `P1 weak candidate`，不是隐性 `P2`；若时间稳定性不过关，就应直接 park。
- `fib-depth` 与 `dry-down` 当前都只是 reserve，不应因为刚有新 digest 就偷渡成 active live/scout promotion。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
