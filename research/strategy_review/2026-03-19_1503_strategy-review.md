# 2026-03-19 15:03 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 本轮应从 `Rank 92` 再前移到 **`Rank 94 / two-bar outside-range follow-through gate`**，因为它比 `opening-drive adaptive offset` 更便宜地补上了 desk 当前更缺的 **shared path-persistence gate**，且不需要先冻结 crypto 24/7 的 session 定义。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1454`，工作区仍有大量既有脏文件；本轮只做 `TRADING DESK BOARD` 最小必要更新、strategy review 记录、首页刷新与邮件，不混改无关文件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1452_rank93-clean-replication-keep-p1.md`
  - `2026-03-19_1429_rank93-base-age-intake.md`
  - `2026-03-19_1403_rank91-clean-replication-keep-p1.md`
  - `2026-03-19_1350_rank91-sweep-count-intake.md`
  - `2026-03-19_1326_rank90-clean-replication-keep-p1.md`
- 最近 strategy reviews（重点核对）：
  - `2026-03-19_1422_strategy-review.md`
  - `2026-03-19_1327_strategy-review.md`
  - `2026-03-19_1228_strategy-review.md`
- 最近 fresh quant digests（重点核对）：
  - `2026-03-19_1448_two-bar-outside-range-followthrough-gate.md`
  - `2026-03-19_1419_first-major-break-base-age-gate.md`
  - `2026-03-19_1318_opening-drive-adaptive-offset-continuation-gate.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled，且本轮正在运行；
  - `bot3-momentum-auto-opt-13m` enabled；
  - `momentum-narrow-paper-lanes-20m` enabled；
  - `bot7-quant-digest-30m` enabled；
  - `bot6-park-reframe-2h` enabled。
- `Paper Seat` guardrail：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（按预期 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 4.9h`、`Crypto 8.9h`、`A股 15.9h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T15:03:03Z`：`new_closed_trades_appended=0`
  - `manual_narrow_paper_status.csv` 仍显示：`Rank 17` 有 `ETH/SOL` open positions；`Rank 2 / 29 / 32b` 当前无新增 closed-trade append
  - 结论：这是 hosted continuity 信息，不是新的 seat 变更理由。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是真 waiting，不是整桌等待；当 `EMA` 继续 `waiting_not_due` 时，bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 94 / Rank 92` 都还只在 **`P0 fresh repo intake`**，连 `clean replication` 都还没开始；
  2. `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81` 都已经收口到 **`P1 evidence_pool / budget used`**，当前不该伪装成 live challenger；
  3. `Rank 17 / 2 / 29 / 32b / 78` 属于 `P3 narrow paper continuity` hosted lanes，不是待升格 live 候选；
  4. 当前没有任何 `P2 / paper candidate` 已完成 1~2 轮最小诚实检查后值得往 `Live Seat` 占位推进。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 94 / two-bar outside-range follow-through gate`
- **当前紧邻后备：**
  - `Rank 92 / opening-drive adaptive offset continuation gate`
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / first-major-break base-age gate`
  - `Rank 90 / close-range compression asymmetry`
  - `Rank 91 / same-level consecutive sweep count level-memory gate`
  - `Rank 82 / Rank 80 / Rank 81`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 94 = P0`**（`fresh repo intake / source intake next`）
- **`Rank 92 = P0`**（`fresh repo intake / 邻近后备`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / 预算已用 / 不再默认续命`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = Rank 94 / two-bar outside-range follow-through gate source intake + 两条轻量诚实守门`**
   - 做完直接回答：`guard-passed / hard-fail`。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 94` guard-pass 且 `EMA` 仍 `waiting_not_due`，则立刻给它 **1 次最小 clean replication**；
   - 若 `Rank 94` 在 intake / guard 阶段直接 hard-fail，则切 **`Rank 92 / opening-drive adaptive offset continuation gate`** 的 source intake；
   - 只有 fresh source 这一层也 exhausted，才允许回退到 **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`**。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 94 / two-bar outside-range follow-through gate`**
   - 当前排第一，因为它比 `Rank 92` 更便宜地补上了 desk 缺的 **path-persistence / 第二脚是否站稳** 维度；
   - `FT / SFT-lite` 规则本身能直接写成 `trade on / trade off`，不用先冻结 `opening-drive / sessionVWAP` 的 crypto 24/7 session 边界；
   - 代理快检已给出 shared 改善：`single-break mean net≈-9.75bps`、`FT-or-better≈-4.80bps（retention≈45.3%）`、`SFT-lite≈-3.06bps（retention≈31.4%）`，说明它值得先拿那 1 次 cheap honest guard 预算。
2. **`Rank 92 / opening-drive adaptive offset continuation gate`**
   - 当前排第二，因为它仍有明显 path-quality 价值：short 侧 `hold4 10.4% -> 16.0%`、`fail_back_inside4 77.5% -> 69.8%`，交易数保留约 `93.6%~94.3%`；
   - 但它在 queue-facing replication 前依然要先冻结 `opening-drive / sessionVWAP` 的 session 定义，当前开工成本仍高于 `Rank 94`。
3. **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前继续只排第三；`Rank 93 / 90 / 91` 都已完成它们各自最有价值的最小检查，再磨更像补文案，不像继续减 gate。
4. **`P3 continuity`**
   - 当前只排第四；`15:03 UTC` 最新 summary 已回到 `new_closed_trades_appended=0`，说明 hosted lanes 没有新的 status-changing event，不应挤掉 fresh Scout intake。
5. **`tiny-live plumbing`**
   - 继续只作更后层 fallback；在 fresh paper/repo intake 仍有清晰候选时，不该抢前排。

## 当前 strongest evidence
1. **EMA guardrail 再次实查仍是 `waiting_not_due`**：当前没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 93` 已经在最小 clean replication 后收口为 `keep_P1 / mixed but honest`**：说明继续磨旧 P1 的性价比明显下降，应该主动切回 fresh intake。
3. **`Rank 94 / two-bar outside-range follow-through gate` 给出了更便宜的 shared path 证据**：不需要 session 定义冻结，且 `FT / SFT-lite` 对三条 archetype 都有直接 continuation-confirmation 价值。
4. **`P3` hosted lanes 本轮无新增 closeout 事件**：`manual_narrow_paper_last_run_summary.json @ 15:03 UTC = new_closed_trades_appended=0`，降低了 P3 continuity 插队的必要性。

## 当前 weakest / should-park lines
- **`Rank 93`**：clean replication 后仍只是 `shared admission + size-down overlay`，继续只该留作 `P1 evidence_pool`。
- **`Rank 90 / Rank 91`**：改善都带明显缩样本 / 狭窄口袋特征，当前继续只应视为 `P1 evidence_pool`。
- **`Rank 82 / Rank 80 / Rank 81`**：都已停留太久，没有新的真 gate 被减少，不应重新拿回 Scout 主资源。

## 建议优先级 Top 1~3
1. **立刻把 `Rank 94 / two-bar outside-range follow-through gate` 作为新的 fresh intake 主资源位。**
2. **若 `Rank 94` 过 guard，再给它仅 1 次最小 clean replication；不过就立刻切 `Rank 92`，不要模糊停留。**
3. **继续保持 `Live Seat = 暂空`，并把 `P3 continuity` 严格留在 hosted / low-frequency 层，不让它挤占 Scout fast lane。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 15:03 UTC（bot2 desk review）` 补充；
  - 正式冻结 **`Rank 94 / two-bar outside-range follow-through gate`**；
  - 把 active Scout 顺序改写为 `Rank 94 > Rank 92 > P1 evidence_pool > P3 continuity > tiny-live plumbing`；
  - 把 `Next 3 bot3 runs` 改写为 `Run 2 = Rank 94 intake`、`Run 3 = Rank 94 clean replication or fallback to Rank 92`。
- **本轮不改 cron。**
  - 当前 cron 方向仍一致：`bot2 / bot3 / narrow-paper / bot7 / bot6` 都在线；没有必要为了这次 seat 变更再改频率。
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment；`2026-03-19_1448_two-bar-outside-range-followthrough-gate.md` 本身也已是可读证据页。

## 风险与不确定性
- `Rank 94` 当前仍只是 digest + 代理快检，不是已完成 intake；这次升到 Scout 主资源位是**排班提升**，不是策略升格。
- `Rank 92` 仍有较高边际价值；若 `Rank 94` 的 `trade on / trade off` 写不清或 clean replication 一上来就塌，它应立即接棒，而不是让 bot3 在 `Rank 94` 上拖回合。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
