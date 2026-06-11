# 2026-03-17 20:36 UTC · Rank 2 replay order honesty sync

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / Rank 2 replay order sync`
- 触发原因：
  - 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Paper Seat / EMA` 当前已回到 `running paper / waiting_not_due`
  - `Scout Seat` 顶板仍是本地 fast-lane `exhaustion state`
  - 因此本轮继续诚实落到 `Run 3`
  - 但当前 `Run 3` 不该继续重复写 tiny-live 近义说明；更值得修的是 **alpha_closure_board 内部对 Rank 2 replay 顺序的口径仍停留在 `ETH -> SOL -> BTC`，与 19:24 UTC 已写出的 rounding-budget ladder 硬结论不一致**

## 开始前检查
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮只做 selective 写入，不混提
- 最近 runs：
  - `19:16 UTC`：`rank2 replay preflight snapshot`
  - `19:24 UTC`：`rank2 replay rounding budget ladder`
  - `19:53 UTC`：`tiny-live state resync`
  - `20:17 UTC`：`EMA due window resync`
- 当前 seat 读法：
  - `Paper Seat`：`EMA = waiting_not_due`
  - `Live Seat`：默认空席
  - `Scout Seat`：当前暂无新的合格 `paper / repo based 5m / 15m crypto` intake
  - 因此这轮主资源应继续落在 `Run 3 / tiny-live plumbing`

## active 路径边际价值比较
### Run 1 / EMA
- 当前没有新的 `due-now / overdue` continuation；继续认领会落回 waiting-window 空转

### Run 2 / Scout Seat
- 顶板已明确写回 `exhaustion state`
- 这一轮没有 bot2 点名 promoted candidate，也没有新的合格 source intake

### Run 3 / tiny-live plumbing
- 这里仍有一个真实会减少误读的 blocker：
  - `small_live_rank2_replay_rounding_budget_ladder_v1.csv` 已在 19:24 UTC 写出：**若坚持 `50U` test/no-fill 且把 rounding 损耗预算压到 `<=25bps`，更诚实的 replay 顺序应读成 `SOL -> ETH -> BTC`**
  - 但 `alpha_closure_board` 的 `runsheet / now-action queue / launch packet summary` 仍沿用旧的 `ETH -> SOL -> BTC`
- 这不是文案小问题，而是 operator-facing 读板会因此把“能下单”误读成“样例也够干净”
- 因此本轮主点应是：**把 Rank 2 replay 顺序与最新 rounding-budget hard verdict 对齐**

## 本轮主点 + 紧邻子点
- **主点**：更新 `scripts/build_alpha_closure_board_report.py`，让 Rank 2 replay / launch / queue 口径自动读取 `small_live_rank2_replay_rounding_budget_ladder_v1.csv`
- **紧邻子点**：重建 `alpha_closure_board`，把 reader-facing 页面与 CSV 一并刷新到同一口径

## 本轮做了什么
### 1) 修复 builder 的 authoritative priority 来源
文件：`scripts/build_alpha_closure_board_report.py`

本轮新增/调整：
- 新增 `get_rank2_replay_priority_context()`
  - 从 `small_live_rank2_replay_rounding_budget_ladder_v1.csv` 读取当前更诚实的 replay 排序、operator action、政策摘要
  - 默认 fallback 仍保留静态白名单顺序，避免 artifact 缺失时整页失效
- 把以下生成逻辑从静态 `ETH/SOL/BTC` 改成动态读取 rounding-budget ladder：
  - `small_live_now_action_queue_v1.csv`
  - `small_live_rank2_replay_runsheet_v1.csv`
  - `small_live_rank2_replay_closeout_matrix_v1.csv`
  - `small_live_rank2_shadow_parity_launch_packet_v1.csv`
- 同步把网页里原先硬编码的 `ETH -> SOL -> BTC` 摘要文字，改成复用同一组动态 context

### 2) 重建 closure board
执行：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`

重建后已对齐的关键产物：
- `reports/artifacts/alpha_closure_board/small_live_now_action_queue_v1.csv`
- `reports/artifacts/alpha_closure_board/small_live_rank2_replay_runsheet_v1.csv`
- `reports/artifacts/alpha_closure_board/small_live_rank2_replay_closeout_matrix_v1.csv`
- `reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_launch_packet_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

## 当前 hard verdict
**当前更诚实的 Rank 2 replay 读法，不是继续笼统地说 `ETH -> SOL -> BTC`，而是要分两层：**
1. **若只看 venue pass/fail**：三条 whitelist leg 都还可以做 `test/no-fill`
2. **若坚持 `50U` 样例，且把 rounding 损耗预算压到 `<=25bps`**：当前应读成 **`SOL -> ETH -> BTC`**
   - `SOL`：当前 50U 已过 `<=25bps`
   - `ETH`：若坚持 ETH 首腿，更诚实做法是先把样例提高到 `>=100U`
   - `BTC`：继续只保留最后备选，约 `>=300U` 才接近同档口径

更直白地说：
- 这轮不是新开 tiny-live，也不是做真实 replay
- 这轮修的是 **operator-facing 的当前顺序口径**
- 修完之后，Run 3 的默认动作终于不再同时说两套互相打架的话

## reader-facing 落点
- `reports/site/factors/alpha_closure_board/report.html`
  - `Rank 2 single-replay runsheet（v1）`
  - `Rank 2 shadow-parity launch packet（v1）`
  - `Rank 2 shadow-parity starter rows（v1）`
- 同步 artifact：
  - `reports/artifacts/alpha_closure_board/small_live_now_action_queue_v1.csv`
  - `reports/artifacts/alpha_closure_board/small_live_rank2_replay_runsheet_v1.csv`

## 验证 / 证据
已验证：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py` 成功
- builder 成功退出并重建 `alpha_closure_board/report.html`
- `small_live_now_action_queue_v1.csv` 已明确写回：
  - `若坚持 50U 且要把 rounding 损耗预算压到 <=25bps，当前先做 SOL 更诚实`
- `small_live_rank2_replay_runsheet_v1.csv` 当前优先级已改成：
  - `P1 = SOL`
  - `P2 = ETH`
  - `P3 = BTC`
- 网页已出现 `SOL → ETH → BTC` 的同步摘要

## 风险 / 边界
- 本轮没有触发真实 venue replay
- 本轮没有把 `Rank 2` 升格成 `shadow_parity passed` 或 `tiny-live ready`
- 本轮也没有继续扩新的 tiny-live 近义文档，而是只修正了一个确实会影响 operator 行动顺序的 authoritative sync 问题

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
