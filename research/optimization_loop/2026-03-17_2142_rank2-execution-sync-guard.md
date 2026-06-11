# 2026-03-17 21:42 UTC · Rank 2 execution sync guard

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / Rank 2 execution sync guard`
- 触发原因：
  - 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Paper Seat / EMA` 当前仍是 `running paper / waiting_not_due`
  - `Scout Seat` 顶板 authoritative 读法仍是本地 fast-lane `exhaustion state`
  - `Live Seat` 默认空席；本轮没有 bot2 新的 promoted candidate
  - 因此本轮继续诚实落到 `Run 3 / tiny-live plumbing fallback`

## 开始前检查
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 最近 runs：
  - `21:09 UTC`：`Rank 2 reader-facing replay bundle`
  - `21:29 UTC`：`tiny-live state resync guard`
- 当前 seat 读法：
  - `Paper Seat`：`EMA = waiting_not_due`
  - `Scout Seat`：当前没有新的合格 `paper / repo based 5m / 15m crypto` intake
  - `Run 3`：当前最值钱的一刀不是再补一张 Rank 2 近义文档，而是回答“现有 replay bundle 还能不能继续被当 authoritative 执行包”

## active 路径边际价值比较
### Run 1 / EMA
- 当前 due guardrail 已回到全 desk 无 `due-now / overdue` lane
- 继续认领只会落回 waiting-window 空转

### Run 2 / Scout Seat
- 顶板 authoritative override 已明确：当前本地 `paper / repo based 5m / 15m crypto` fast lane 暂时 exhaustion
- 本轮没有新的合格 source，也没有新的 promoted candidate

### Run 3 / tiny-live plumbing
- `Rank 2 next replay bundle` 已经 reader-facing，但仍缺一层更诚实的 guard：
  - 上游 `preflight / rounding / receipt audit / runsheet` 若比 bundle 更新，operator 不该继续照旧 bundle 执行
  - 上一轮已经补了 manual-runner -> closure-layer 的 `state resync guard`
  - 这轮更值钱的是补 `Rank 2 replay evidence -> replay bundle` 的同步 guard，而不是继续扩 packet / wording

## 本轮主点 + 紧邻子点
- **主点**：新增 `small_live_rank2_execution_sync_guard_v1.csv`，把 `Rank 2 replay bundle` 与其上游 evidence 的同步条件写成显式 guard
- **紧邻子点**：把这张 guard 挂进 `alpha_closure_board/report.html`，并让 `small_live_now_action_queue_v1.csv` 在 guard 不同步时默认先要求 resync

## 本轮做了什么
### 1) 扩展 builder，新增 Rank 2 execution sync guard
修改文件：`scripts/build_alpha_closure_board_report.py`

本轮新增：
- 新 artifact：
  - `reports/artifacts/alpha_closure_board/small_live_rank2_execution_sync_guard_v1.csv`
- 新 helper：
  - `format_sync_guard(...)`
- 新 guard 生成逻辑：
  - `small_live_rank2_replay_preflight_snapshot_v1.csv -> small_live_rank2_next_replay_bundle_v1.csv`
  - `small_live_rank2_replay_rounding_budget_ladder_v1.csv -> small_live_rank2_next_replay_bundle_v1.csv`
  - `small_live_rank2_receipt_chain_audit_v1.csv -> small_live_rank2_next_replay_bundle_v1.csv`
  - `small_live_rank2_replay_runsheet_v1.csv -> small_live_rank2_next_replay_bundle_v1.csv`

每行直接写清：
- `source_file / source_role`
- `dependent_artifact / dependent_role`
- `source/dependent mtime`
- `lag_read`
- `guard_state`
- `hard_read`
- `required_action`

### 2) 把 guard 挂成 reader-facing 页面
同一 builder 新增网页卡片：
- `Rank 2 replay execution sync guard（v1）`

这张卡不是重复解释 replay 顺序，而是直接回答：
- 当前公开页面里的 `next replay bundle` 还是否跟得上它依赖的上游 evidence
- 若不同步，是否必须先重建 `alpha_closure_board`
- 只有 guard 全部回到 `synced` 时，才继续把 bundle 当 authoritative 执行包

### 3) 让 now-action queue 在 future stale 场景下自动更诚实
- 调整 `small_live_now_action_queue_v1.csv` 的 `Rank 2 / combo_all` 逻辑：
  - 若 execution-sync guard 全部 `synced`：继续维持当前读法 —— 下一步仍是 `1` 次 whitelist-bound `test/no-fill` replay
  - 若未来出现上游 evidence 比 bundle 更新：默认先把 `action_owner_now` 切到 `run3 closure sync`，要求先重建 replay bundle，而不是继续照旧 bundle 推 operator 步骤

## 最小验证 + 发布
执行：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`
- `bash scripts/publish_homepage_index.sh`

结果：
- builder 编译通过
- 新 artifact 已生成：
  - `reports/artifacts/alpha_closure_board/small_live_rank2_execution_sync_guard_v1.csv`
- 页面已重建：
  - `reports/site/factors/alpha_closure_board/report.html`
- 首页已刷新并发布：
  - `https://jp.jerrypsy.top/momentum/`

## 当前 hard verdict
**当前更诚实的 Run 3 读法不是继续猜 `next replay bundle` 会不会旧，而是先看 execution-sync guard。当前 4 条上游依赖全部是 `synced`，所以 `Rank 2` 的当前允许动作仍然没有变化：先做 `1` 次 whitelist-bound `test/no-fill` replay，优先 `SOL`；但如果后续上游 evidence 比 bundle 更新，则默认动作必须先切回 resync，而不是拿旧 bundle 继续推进。**

更直白地说：
- `Live Seat` 继续默认空席
- `Rank 17 / Rank 29` 继续只是 `P3 continuity`
- `Rank 2` 继续只差那一条真实 receipt chain
- 但现在多了一层显式 guard：以后先看 `execution sync`，再信任 replay bundle

## reader-facing / deployable 落点
- `reports/artifacts/alpha_closure_board/small_live_rank2_execution_sync_guard_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/index.html`
- 对外入口：`https://jp.jerrypsy.top/momentum/`

## 验证 / 证据
已验证：
- `small_live_rank2_execution_sync_guard_v1.csv` 已生成
- 当前 4 行 guard 全部显示 `synced`
- 页面检索已确认包含 `Rank 2 replay execution sync guard（v1）`
- `small_live_now_action_queue_v1.csv` 中 `Rank 2` 当前仍维持 `operator / run3 closeout` 读法，没有误切到 stale-resync 分支

## 风险 / 边界
- 本轮没有触发真实 venue replay
- 本轮没有重开 `Live Seat`
- 本轮没有新增 Scout candidate
- 本轮没有把 `Rank 2` 从 `paper_candidate_only / blocked` 偷渡成 `shadow parity passed`
- 本轮改变的是 **Rank 2 replay bundle 的可审计同步边界**，不是策略席位本身

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
