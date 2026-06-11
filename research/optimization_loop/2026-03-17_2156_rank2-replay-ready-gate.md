# 2026-03-17 21:56 UTC · Rank 2 replay ready gate

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / Rank 2 replay ready gate`
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
  - `21:42 UTC`：`Rank 2 execution sync guard`
- 当前 seat 读法：
  - `Paper Seat`：`EMA = waiting_not_due`
  - `Scout Seat`：当前没有新的合格 `paper / repo based 5m / 15m crypto` intake
  - `Run 3`：当前最值钱的一刀不再是继续加 packet / wording，而是回答“Rank 2 现在到底能不能立刻做那 1 次 replay”

## active 路径边际价值比较
### Run 1 / EMA
- 当前 due guardrail 已回到全 desk 无 `due-now / overdue` lane
- 继续认领只会落回 waiting-window 空转

### Run 2 / Scout Seat
- 顶板 authoritative override 已明确：当前本地 `paper / repo based 5m / 15m crypto` fast lane 暂时 exhaustion
- 本轮没有新的合格 source，也没有新的 promoted candidate

### Run 3 / tiny-live plumbing
- 前几轮已经把 `next replay bundle`、`state resync guard`、`execution sync guard` 都做出来了
- 但 operator 仍要自己在三张表之间推断“现在能不能做 replay，还是应先 resync”
- 因此本轮最值钱的是新增一张单行 **ready gate**，把 `queue + bundle + sync guards` 合成一个 authoritative verdict

## 本轮主点 + 紧邻子点
- **主点**：新增 `small_live_rank2_replay_ready_gate_v1.csv`
- **紧邻子点**：把这张 ready gate 挂进 `alpha_closure_board/report.html`

## 本轮做了什么
### 1) 扩展 builder，新增 Rank 2 replay ready gate
修改文件：`scripts/build_alpha_closure_board_report.py`

本轮新增：
- 新 artifact：
  - `reports/artifacts/alpha_closure_board/small_live_rank2_replay_ready_gate_v1.csv`
- 新逻辑：
  - 读取 `small_live_now_action_queue_v1.csv`
  - 读取 `small_live_rank2_next_replay_bundle_v1.csv`
  - 读取 `small_live_rank2_execution_sync_guard_v1.csv`
  - 读取 `small_live_state_resync_guard_v1.csv`
- 单行输出直接写清：
  - `ready_state`
  - `bundle_leg_now`
  - `action_owner_now`
  - `execution_sync_state`
  - `tiny_live_state_sync`
  - `next_allowed_action_now`
  - `still_waiting_for`
  - `hard_stop`
  - `hard_read`

### 2) 把 ready gate 挂成 reader-facing 页面
同一 builder 新增网页卡片：
- `Rank 2 replay ready gate（v1）`

这张卡不再重复 replay bundle 的 symbol / budget 细节，而是直接回答：
- 当前是否真的允许做那 1 次 whitelist-bound `test/no-fill` replay
- 若不允许，先卡在 `execution sync` 还是 `tiny-live state sync`
- 若允许，成功后最多推进到哪一步

### 3) 最小验证 + 发布
执行：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`
- `bash scripts/publish_homepage_index.sh`

结果：
- builder 编译通过
- 新 artifact 已生成：
  - `reports/artifacts/alpha_closure_board/small_live_rank2_replay_ready_gate_v1.csv`
- 页面已重建：
  - `reports/site/factors/alpha_closure_board/report.html`
- 首页已刷新并发布：
  - `https://jp.jerrypsy.top/momentum/`

## 当前 hard verdict
**当前更诚实的 Run 3 读法，不是直接把 Rank 2 当成“ready to replay”，而是先看这张 ready gate。当前结论是 `blocked_resync_tiny_live_state`：`execution sync` 仍是 `synced`，但 `manual_narrow_paper_*` source 已比 closure-layer 稍新，因此此刻默认先做一次 closure-layer resync，比继续沿旧 queue 直接推进 replay 更诚实。**

更直白地说：
- `Rank 2` 仍然只差那一条真实 receipt chain
- 但当前 **不是** “现在立刻照旧 bundle 去 replay”
- 现在更诚实的顺序是：
  1. 先看 ready gate
  2. 若 state sync / execution sync 任一不绿，先 resync
  3. 只有双 sync 都回到 `synced`，才继续读 `SOL` 优先的那 1 次 whitelist-bound `test/no-fill` replay
- 即使将来 replay 通过，也仍只推进到 `eligible_for_shadow_parity_review`，不是 tiny-live 放行

## reader-facing / deployable 落点
- `reports/artifacts/alpha_closure_board/small_live_rank2_replay_ready_gate_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/index.html`
- 对外入口：`https://jp.jerrypsy.top/momentum/`

## 验证 / 证据
已验证：
- 新 CSV 已生成，当前单行读法明确写回：
  - `ready_state=blocked_resync_tiny_live_state`
  - `bundle_leg_now=SOLUSDT`
  - `execution_sync_state=synced`
  - `tiny_live_state_sync=needs_resync`
- 页面检索已确认包含：
  - `Rank 2 replay ready gate（v1）`
  - `small_live_rank2_replay_ready_gate_v1.csv`
- 首页已重新发布

## 风险 / 边界
- 本轮没有触发真实 venue replay
- 本轮没有重开 `Live Seat`
- 本轮没有新增 Scout candidate
- 本轮没有把 `Rank 2` 从 `paper_candidate_only / blocked` 偷渡成 `shadow parity passed`
- 本轮改变的是 **operator 是否“现在就能做 replay” 的显式判定边界**，不是席位本身

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
