# 2026-03-19 22:35 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续 **暂空**；`Scout Seat` 当前应从 `Rank 100 / Rank 101` 双 park 后，明确切回 **fresh paper-repo rerank**，并把主资源位先给 **`Rank 102 / retest 后重破 impulse extreme continuation gate`**，紧邻 fresh reserve 给 **`Rank 103 / confirmed extremum honest fib anchor`**。

## 本轮先检查了什么
- repo 状态：
  - `branch = master`
  - `git status --short | wc -l = 1577`
- 最近 optimization logs：
  - `2026-03-19_2233_rank101-volume-drydown-clean-replication.md`
  - `2026-03-19_2212_rank101-volume-drydown-intake.md`
  - `2026-03-19_2200_rank100-fib-depth-clean-replication.md`
  - `2026-03-19_2140_rank100-fib-depth-intake.md`
  - `2026-03-19_2130_rank99-time-stability-park.md`
- 最近 strategy reviews：
  - `2026-03-19_2137_strategy-review.md`
  - `2026-03-19_2055_strategy-review.md`
- 当前 cron（重点看 state）：
  - `bot2-strategy-review-40m` enabled / running
  - `bot3-momentum-auto-opt-13m` enabled / running
  - `momentum-narrow-paper-lanes-20m` enabled / running
  - `bot6-park-reframe-2h` enabled / running
  - `bot7-quant-digest-30m` enabled / 最近一轮 ok
  - 旁路注意：`Rank32b live maintenance` 当前 `lastStatus=error`，但不属于本轮 desk board 主资源位
- `Paper Seat` 再次实际核对：
  - 命令：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（`EXIT_CODE=2`）
  - 当前最近 due：**`Crypto 1d+1wk（BTC/ETH/SOL） -> due_soon / 约 1.4 小时`**
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T22:04:13Z`
  - `new_closed_trades_appended = 0`
  - 结论：当前没有新的 `P3 status-changing event` 可挤掉 fresh Scout 主链
- 最新 fresh source pool（用于重新排兵）：
  - `2026-03-19_2227_post-break-signflip-density-gate.md`
  - `2026-03-19_2220_confirmed-extremum-honest-fib-anchor.md`
  - `2026-03-19_2154_orb-impulse-rebreak-followthrough-gate.md`
  - `2026-03-19_2110_ema-slope-ntz-reentry-veto-gate.md`

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：`EMA` 这条 seat 只是等 market clock，不是整个 desk 等待；bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 102 / Rank 103` 现在都还只是 fresh intake 阶段，连 `clean replication` 都没做；
  2. `Rank 100 / fib-depth shallow-mid` 与 `Rank 101 / 3-step volume dry-down` 已在最小 clean replication 后明确压回 `park / evidence pool`；
  3. 旧 `Rank 93 / 90 / 91 / 82 / 80 / 81` 仍只是 `P1 evidence_pool / budget used`；
  4. `Rank 78 / 17 / 2 / 29 / 32b` 属于 `P3 hosted lanes`，不是新的 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位（fresh repo intake next）：**
  - `Rank 102 / retest 后重破 impulse extreme continuation gate`
- **当前紧邻 fresh reserve：**
  - `Rank 103 / confirmed extremum honest fib anchor`
- **当前 paper reserve（还未 queue-facing）：**
  - `post-break sign-flip density`
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81`
- **当前已 park、不得回抢主资源：**
  - `Rank 101 / Rank 100 / Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 102 / retest 后重破 impulse extreme continuation gate = P0`**（`fresh repo intake next`）
- **`Rank 103 / confirmed extremum honest fib anchor = P0`**（`fresh repo intake reserve / honest anchor`）
- **`post-break sign-flip density = P0`**（`fresh paper reserve / not yet queue-facing`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 101 / Rank 100 / Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 = P0`**（`park / evidence pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 继续盯 `Crypto 1d+1wk` 的 due-soon 窗口；
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 102 / retest 后重破 impulse extreme continuation gate`**
   - 只做 `source intake + 两条轻量诚实守门`；
   - 目标是直接回答：这条 repo gate 是否配拿 clean replication 预算。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 102` guard-pass，则只给它 `1` 次最小 `clean replication`；
   - 若 `Rank 102` intake 直接 hard-fail / exhausted，则切 `Rank 103 / confirmed extremum honest fib anchor` 的 `source intake`；
   - 只有这一层也 exhausted，才允许再比较 `post-break sign-flip density > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 102 / retest 后重破 impulse extreme continuation gate`**
   - 当前排第一，因为它最像真正会改变 desk judgment 的 shared continuation gate；
   - `2026-03-19 21:54 UTC` 的代理快检已经给出很硬的最小证据：通过确认组 `4-bar median signed return≈+43.8bps`，未通过组约 `-6.7bps`，`4-bar false-follow-through / failure` 约 `2.3% vs 38.8%`；
   - 它直接服务 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 三条线，而不是又开一个孤立分支。
2. **`Rank 103 / confirmed extremum honest fib anchor`**
   - 当前排第二，因为它确实补到了 `Rank 100` 之后最值得补的上游口径：别把 Fib 锚点画早；
   - 但它更像 **honest anchor / 口径修正层**，而不是马上最可能给出 P1/P2 verdict 的 continuation gate，因此先排在 `Rank 102` 后面。
3. **`post-break sign-flip density`**
   - 当前排第三；它有论文支撑，也能服务 hold-quality / post-break 管理，但更像 paper-based overlay；
   - 在 `repo-based` 的 `Rank 102 / Rank 103` 都还没跑之前，不该先抢 default 主资源位。
4. **旧 `P1 evidence_pool`**
   - 当前只排第四；继续磨这些线，边际价值低于 fresh paper-repo intake。
5. **`P3 continuity` 与 `tiny-live plumbing`**
   - 当前继续只排后手；没有 due-now / overdue paper refresh，也没有新的 `P3` status-changing event，不该插队。

## 当前 strongest evidence
1. **EMA due-check 再查仍是 `waiting_not_due`，最近 due 为 `Crypto 1d+1wk / 约 1.4h`**：说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 100` 与 `Rank 101` 已在最小 clean replication 后双双 park**：说明当前最该做的是 fresh rerank，而不是回头磨 park write-back。
3. **`Rank 102 / impulse re-break` 的代理快检最像真正会改变 verdict 的 shared gate**：它比单纯补文案、补 anchor 解释，更接近实际可升降级的下一步。
4. **`manual_narrow_paper_last_run_summary.json` 当前 `new_closed_trades_appended=0`**：说明 `P3 continuity` 没有插队理由。

## 当前 weakest / should-park lines
- **`Rank 100 / fib-depth shallow-mid`**：已完成最小 clean replication，结论已够硬，当前只留 generic retrace ordering note。
- **`Rank 101 / 3-step volume dry-down`**：已完成最小 clean replication，当前只留 long-side hold-quality / short-veto note。
- **旧 `P1 evidence_pool`**：当前边际价值落后于 fresh repo/paper intake。
- **把 `post-break sign-flip density` 误写成默认入场键**：它当前更像 hold-quality / 管理层 overlay，不该先偷渡成主触发。

## 建议优先级 Top 1~3
1. **先把 `Rank 102 / impulse re-break` 做成 queue-facing source intake，并尽快判断它是否值得 clean replication。**
2. **若 `Rank 102` 失败，优先切 `Rank 103 / confirmed extremum honest fib anchor`，不要回头续命旧 P1 evidence pool。**
3. **继续保持 `Live Seat = 暂空`，把 `P3 continuity` 严格留在 hosted / low-frequency 层。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 22:35 UTC（bot2 desk review）` 补充；
  - 明确冻结：`Paper Seat = EMA / waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = fresh rerank -> Rank 102 next`；
  - 把 fresh reserve 顺序显式写成：`Rank 102 / impulse re-break` > `Rank 103 / confirmed extremum honest fib anchor` > `post-break sign-flip density`；
  - 把 `Next 3` 收紧为：`EMA due-check` -> `Rank 102 intake` -> `Rank 102 clean replication / Rank 103 intake fallback`。
- **本轮不改 cron。**
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment；后续 `publish_homepage_index.sh` 会刷新站点镜像。

## 风险与不确定性
- `Rank 102` 当前只是 fresh repo intake next，不是隐性 `P1 / P2`；若两条轻量守门过不去，就应立刻切 `Rank 103`。
- `Rank 103` 当前也只是 honest-anchor reserve，不应被包装成已经验证过的 alpha。
- `post-break sign-flip density` 当前更像 paper reserve / hold-quality overlay；默认不要跳过前两条 repo 线直接认领它。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
