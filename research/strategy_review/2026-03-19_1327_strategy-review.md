# 2026-03-19 13:27 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 当前应继续明确给 **`Rank 91 / same-level consecutive sweep count level-memory gate`**，紧邻后备是 **`Rank 92 / opening-drive adaptive offset continuation gate`**。`P3` 虽在 `12:56 UTC` 出现了真实 closed-trade append，但该状态变化已被专属 narrow-paper cron 正常吸收，**不足以挤掉 fresh Scout intake**。

## 本轮先检查了什么
- repo 状态：`git status --short --branch` 仍显示大量既有脏文件；本轮只做 `TRADING DESK BOARD` 最小必要更新、strategy review 记录、首页刷新与邮件，不混改无关文件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1300_rank90-close-range-compression-intake.md`
  - `2026-03-19_1326_rank90-clean-replication-keep-p1.md`
  - 向前复核：`2026-03-19_1252_rank89-clean-replication-park.md`
- 最近 strategy review：
  - `2026-03-19_1228_strategy-review.md`
  - `2026-03-19_1150_strategy-review.md`
  - `2026-03-19_1107_strategy-review.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled，且本轮正在运行；
  - `bot3-momentum-auto-opt-13m` enabled，最近一轮已推进到 `13:26 UTC / Rank 90 clean replication -> keep_P1`；
  - `momentum-narrow-paper-lanes-20m` enabled；最新 `manual_narrow_paper_last_run_summary.json @ 2026-03-19T12:56:06Z` 为 `new_closed_trades_appended=1`；
  - `bot7-quant-digest-30m` enabled；
  - `bot6-park-reframe-2h` enabled，但最近报错仍是 `rg: command not found`，本轮只记账，不改席位判断。
- `Paper Seat` guardrail：本轮继续以 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 为准
  - 当前全 desk 仍无 `due-now / overdue` lane；
  - 最近 due 约为：`美股 12.9h`、`Crypto 16.9h`、`A股 23.9h`；
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`。
- `P3 narrow paper` 托管状态（本轮新增关键信号）：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T12:56:06Z`：`new_closed_trades_appended=1`
  - `manual_narrow_paper_status.csv` 显示主要变化落在 **`Rank 17`**：
    - `ETH-USD` 在 `2026-03-19T03:30:00Z` 有已追加 closed trade；
    - `SOL-USD` 在 `2026-03-19T12:15:00Z` 出现新的 open position；
  - 结论：这是 **真实 `P3 status-changing event`**，但当前已被 narrow-paper 专属 cron 正常吸收，还不足以改变主 seat 排兵。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是真 waiting，不是全 desk 等待；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 91 / Rank 92` 还都停在 **`P0 fresh intake`**，尚未经过 `clean replication`；
  2. `Rank 90` 虽在 `13:26 UTC` 给出 **`keep_P1 / mixed but honest`**，但离 `P2 / paper candidate` 仍差一截；
  3. `Rank 82 / 80 / 81` 继续只是 **`P1 evidence_pool`**；
  4. `Rank 17 / 2 / 29 / 32b / 78` 属于 `P3 narrow paper continuity` 托管位，不该被误写成 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 91 / same-level consecutive sweep count level-memory gate`
- **当前紧邻后备：**
  - `Rank 92 / opening-drive adaptive offset continuation gate`
- **当前 fresh backlog（不抢主资源）：**
  - `12:41 impulse-volume anchor + small-body retest-hold gate`
  - `12:13 same-parent SL cooldown execution veto`
- **当前只留在证据池、不再默认续命：**
  - `Rank 90 / close-range compression asymmetry`
  - `Rank 82 / ETF lead regime gate`
  - `Rank 80 / first-30m impulse quality gate`
  - `Rank 81 / RS semivariance asymmetry gate`
  - `Rank 89 / 88 / 87 / 86 / 85 / 84 / 83`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / 17 / 2 / 29 / 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 91 = P0`**（`fresh repo intake / source intake next`）
- **`Rank 92 = P0`**（`fresh repo intake / 邻近后备`）
- **`12:41 impulse-volume anchor + small-body retest-hold gate = P0`**（`fresh digest backlog / 未排进主资源位`）
- **`12:13 same-parent SL cooldown execution veto = P0`**（`fresh digest backlog / execution-veto 倾向更强`）
- **`Rank 90 = P1`**（`cheap honest check 已用 / keep_P1 / evidence_pool`）
- **`Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / 不再默认续命`）
- **`Rank 89 / Rank 88 / Rank 87 / Rank 86 / Rank 85 / Rank 84 / Rank 83 = P0`**（`park / evidence_pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得伪造 refresh，也不得空转。
2. **`Run 2 = Rank 91 / same-level consecutive sweep count level-memory gate source intake + 两条轻量诚实守门`**
   - 做完直接回答：`guard-passed / hard-fail`。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 91` guard-pass 且 `EMA` 仍 `waiting_not_due`，则立刻给它 **1 次最小 clean replication**；
   - 若 `Rank 91` 在 intake / guard 阶段直接 hard-fail，则切 **`Rank 92 / opening-drive adaptive offset continuation gate`** 的 source intake；
   - 只有 fresh source 这一层也 exhausted，才允许回退到 **`Rank 90 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`**。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 91 / same-level consecutive sweep count level-memory gate`**
   - 当前排第一，因为它仍是 paper / repo based 的 `5m/15m crypto` fresh intake；规则更像 shared level-memory gate，不需要先冻结 opening-drive session 边界，进入 `trade on / trade off` 的成本最低。
2. **`Rank 92 / opening-drive adaptive offset continuation gate`**
   - 当前排第二，因为它也有近邻 repo 价值，但在 queue-facing replication 前还要先把 opening-drive 定义冻结清楚，当前边际价值略低于 `Rank 91`。
3. **`12:41 impulse-volume anchor + small-body retest-hold gate`**
   - 当前排第三；它更偏 retest 子线，而不是三条主线都能共享的第一优先 shared gate。
4. **`12:13 same-parent SL cooldown execution veto`**
   - 当前排第四；它更像 execution veto / tiny-live plumbing 邻近层，不该先抢掉 fresh Scout 主资源位。
5. **`Rank 90 / 82 / 80 / 81 evidence_pool`**
   - 继续只留证据池；它们都已经用掉了 cheap check 或 minimal clean replication 预算，再磨更像补说明，不像继续减 gate。
6. **`P3 continuity`**
   - 本轮虽因 `Rank 17` closed-trade append 获得了**真实状态变化**，但这更像 narrow-paper 托管层的 sidecar 事件，而不是新的 Scout Seat 抢位理由；因此只保留在 `fresh source` 之后、`tiny-live plumbing` 之前。

## 当前 strongest evidence
1. **EMA guardrail 仍明确显示 `waiting_not_due`**：这轮没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 90` 已在最小 clean replication 后给出 `keep_P1 / mixed but honest`**：说明它有信息，但还不够硬，不应继续占主资源位。
3. **两条最新 fresh repo digests（13:11 / 13:18）已经给出更便宜的新 shared gate 候选**：这让 `Scout Seat` 有明确新入口，不需要回头再磨旧 P1。
4. **`P3` 当前确有 status-changing event，但已经被专属 cron 正常吸收**：这降低了“必须立即抢回 bot3 主资源”的必要性。

## 当前 weakest / should-park lines
- **`Rank 89`**：clean replication 后靠极端缩样本改善，已应继续视为 **park**。
- **`Rank 88 / 87 / 86 / 85 / 84 / 83`**：都已预算用尽并给出 `park / evidence_pool`，不应回头续命。
- **`Rank 90`**：虽未判死，但当前更像 **P1 evidence_pool**，不是继续霸占 Scout Seat 的理由。

## TODO / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 13:27 UTC（bot2 desk review）` 补充；
  - 明确 `P3` 本轮有真实 closed-trade append，但仍不挤掉 `Rank 91 -> Rank 92` 这条 fresh Scout 顺序；
  - 明确 `Next 3` 继续沿用 `13:24 UTC` 版本，不额外翻盘。
- **本轮不改 cron。**
  - 仅记录：`bot6-park-reframe-2h` 仍因 `rg` 缺失报错，后续应单独修，但不影响本轮排兵布阵。
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment；strategy review / 既有 factor 页面继续作为外显证据。

## 风险与不确定性
- `Rank 91 / Rank 92` 目前还都只停在 `P0 fresh intake`，任何 live / paper 升格都还太早。
- `Rank 17` 的 narrow-paper 状态变化虽然真实，但若后续 open-position / closeout 连续异常，下一轮就可能值得提高 `P3 continuity` 的边际权重。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
