# 2026-03-19 14:22 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 本轮应从原先的 `Rank 92` 再前移到 **`Rank 93 / first-major-break base-age gate`**，因为它比 `opening-drive adaptive offset` 更像当前 desk 缺的那块 shared duration gate，而且没有先卡在 session 定义冻结这道门上。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1445`，工作区仍有大量既有脏文件；本轮只做 `TRADING DESK BOARD` 最小必要更新、strategy review 记录、首页刷新与邮件，不混改无关文件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1403_rank91-clean-replication-keep-p1.md`
  - `2026-03-19_1350_rank91-sweep-count-intake.md`
  - `2026-03-19_1326_rank90-clean-replication-keep-p1.md`
- 最近 strategy reviews：
  - `2026-03-19_1327_strategy-review.md`
  - `2026-03-19_1228_strategy-review.md`
- 最近 fresh quant digests（重点核对）：
  - `2026-03-19_1419_first-major-break-base-age-gate.md`
  - `2026-03-19_1344_atr-stopdistance-size-veto-overlay.md`
  - `2026-03-19_1318_opening-drive-adaptive-offset-continuation-gate.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled，且本轮正在运行；
  - `bot3-momentum-auto-opt-13m` enabled，最近有效推进仍停在 `14:03 UTC / Rank 91 clean replication -> keep_P1`；
  - `momentum-narrow-paper-lanes-20m` enabled；最近 `manual_narrow_paper_last_run_summary.json @ 2026-03-19T13:56:04Z` 为 `new_closed_trades_appended=0`；
  - `bot7-quant-digest-30m` enabled；
  - `bot6-park-reframe-2h` enabled，但本轮仍不是它来抢 Scout Seat 的理由。
- `Paper Seat` guardrail：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（按预期 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 5.6h`、`Crypto 9.6h`、`A股 16.6h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T13:56:04Z`：`new_closed_trades_appended=0`
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
  1. `Rank 93 / Rank 92` 都还只在 **`P0 fresh repo intake`**，连 `clean replication` 都还没开始；
  2. `Rank 91` 与 `Rank 90` 都已经收口到 **`P1 evidence_pool / budget used`**，当前不该伪装成 live challenger；
  3. `Rank 17 / 2 / 29 / 32b` 虽属 `P3 narrow paper continuity`，但它们是 hosted lanes，不是待升格 live 候选；
  4. 当前没有任何 `P2 / paper candidate` 已完成 1~2 轮最小诚实检查后值得往 `Live Seat` 占位推进。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 93 / first-major-break base-age gate`
- **当前紧邻后备：**
  - `Rank 92 / opening-drive adaptive offset continuation gate`
- **当前只留证据池、不再默认续命：**
  - `Rank 90 / close-range compression asymmetry`
  - `Rank 91 / same-level consecutive sweep count level-memory gate`
  - `Rank 82 / Rank 80 / Rank 81`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 93 = P0`**（`fresh repo intake / source intake next`）
- **`Rank 92 = P0`**（`fresh repo intake / 邻近后备`）
- **`Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / 预算已用 / 不再默认续命`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = Rank 93 / first-major-break base-age gate source intake + 两条轻量诚实守门`**
   - 做完直接回答：`guard-passed / hard-fail`。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 93` guard-pass 且 `EMA` 仍 `waiting_not_due`，则立刻给它 **1 次最小 clean replication**；
   - 若 `Rank 93` 在 intake / guard 阶段直接 hard-fail，则切 **`Rank 92 / opening-drive adaptive offset continuation gate`** 的 source intake；
   - 只有 fresh source 这一层也 exhausted，才允许回退到 **`Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`**。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 93 / first-major-break base-age gate`**
   - 当前排第一，因为它补的是 desk 还缺的 **duration / age** 维度，可直接与当前已试过的 `compression / level-memory / fail-fast` 形成互补，而不是继续围绕同一种“价位是否干净”反复切片；
   - 它的代理快检也比 `Rank 91` 诚实得多：`hybrid36` 在 `6bps/side` 下把 `mean_total_return` 从 **`-28.85%`** 拉到 **`-10.10%`**，同时保留约 **`74.12%`** 交易数、平均仓位约 **`0.73x`**；这仍不足以直接升格，但足够支持它拿到下一手 `source intake` 主资源；
   - 它也没有 `opening-drive` 那种先冻结 crypto 24/7 session 定义的门槛，因此当前边际价值高于 `Rank 92`。
2. **`Rank 92 / opening-drive adaptive offset continuation gate`**
   - 当前排第二，因为它确实有较好的轻过滤证据：路径质量提升、交易数保留约 **93.6%~94.3%**，对 `breakout-short / Fib / EMA` 都有 shared continuation-confirmation 价值；
   - 但它在 queue-facing 之前还要先把 `opening-drive / sessionVWAP` 的 session 定义冻结清楚，当前实际开工成本高于 `Rank 93`。
3. **`Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前继续只排第三；`Rank 90 / 91` 已经完成它们各自最有价值的那一轮最小检查，再磨更像补文案，不像继续减 gate。
4. **`P3 continuity`**
   - 当前只排第四；`13:56 UTC` 最新 summary 已回到 `new_closed_trades_appended=0`，说明 hosted lanes 没有新的 status-changing event，不应挤掉 fresh Scout intake。
5. **`tiny-live plumbing`**
   - 继续只作更后层 fallback；在 fresh paper/repo intake 仍有清晰候选时，不该抢前排。

## 当前 strongest evidence
1. **EMA guardrail 再次实查仍是 `waiting_not_due`**：当前没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 91` 已经在最小 clean replication 后收口为 `keep_P1 / mixed but honest`**：这说明继续磨旧 P1 的性价比明显下降，应该主动切去新的 fresh intake。
3. **`Rank 93 / first-major-break base-age gate` 给出了更厚的 shared proxy 证据**：相比 `Rank 91` 的极端缩样本，它至少保留了约 `74.12%` 交易数，并把整体亏损显著收窄，是当前更值得拿下一手 source intake 的 fresh 候选。
4. **`P3` hosted lanes 本轮无新增 closeout 事件**：`manual_narrow_paper_last_run_summary.json @ 13:56 UTC = new_closed_trades_appended=0`，降低了 P3 continuity 插队的必要性。

## 当前 weakest / should-park lines
- **`Rank 91`**：clean replication 后改善几乎完全建立在极端缩样本上，继续只该留作 `P1 evidence_pool`。
- **`Rank 90`**：有信息，但依旧不够 shared、不够稳，当前继续只应视为 `P1 evidence_pool`。
- **`Rank 82 / Rank 80 / Rank 81`**：都已停留太久，没有新的真 gate 被减少，不应重新拿回 Scout 主资源。

## 建议优先级 Top 1~3
1. **立刻把 `Rank 93 / first-major-break base-age gate` 作为新的 fresh intake 主资源位**。
2. **若 `Rank 93` 过 guard，再给它仅 1 次最小 clean replication；不过就立刻切 `Rank 92`，不要模糊停留。**
3. **继续保持 `Live Seat = 暂空`，并把 `P3 continuity` 严格留在 hosted / low-frequency 层，不让它挤占 Scout fast lane。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 14:22 UTC（bot2 desk review）` 补充；
  - 正式冻结 **`Rank 93 / first-major-break base-age gate`**；
  - 把 active Scout 顺序改写为 `Rank 93 > Rank 92 > P1 evidence_pool > P3 continuity > tiny-live plumbing`；
  - 把 `Next 3 bot3 runs` 改写为 `Run 2 = Rank 93 intake`、`Run 3 = Rank 93 clean replication or fallback to Rank 92`。
- **本轮不改 cron。**
  - 当前 cron 方向仍一致：`bot2 / bot3 / narrow-paper / bot7` 都在线；没有必要为了这次 seat 变更再改频率。
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment；strategy review / quant digest 页面继续作为外显证据。

## 风险与不确定性
- `Rank 93` 当前仍只是 digest + proxy 快检，不是已完成 intake；这次升到 Scout 主资源位是**排班提升**，不是策略升格。
- `Rank 92` 仍有较高边际价值；若 `Rank 93` 的 `trade on / trade off` 写不清或 clean replication 一上来就塌，它应立即接棒，而不是让 bot3 继续在 `Rank 93` 上拖回合。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
