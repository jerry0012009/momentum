# 2026-03-17 20:46 UTC · Rank 2 receipt audit rounding sync

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / Rank 2 receipt audit sync`
- 触发原因：
  - 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Paper Seat / EMA` 当前仍是 `running paper / waiting_not_due`
  - `Scout Seat` 顶板仍是 `暂无线格新 intake / exhaustion state`
  - `Rank 2 / Rank 17 / Rank 29` 的 `P3 continuity` 日预算已不适合再做近义接线
  - 因此本轮诚实落到 `Run 3`；但当前最值钱的 tiny-live 主点，不是继续补同义 packet，而是把 **`Rank 2 receipt-chain audit` 与已写出的 `rounding-budget ladder` 真正接上**，避免 operator 继续把三条 replay 腿误读成同级

## 开始前检查
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 最近 runs：
  - `19:37 UTC`：`scout fast-lane exhaustion state`
  - `19:53 UTC`：`tiny-live state resync`
  - `20:17 UTC`：`EMA due window resync`
  - `20:36 UTC`：`Rank 2 replay order honesty sync`
- 当前 seat 读法：
  - `Paper Seat`：`EMA = waiting_not_due`
  - `Live Seat`：默认空席
  - `Scout Seat`：当前暂无新的合格 `paper / repo based 5m / 15m crypto` intake
  - 因此本轮主资源继续落在 `Run 3 / tiny-live plumbing`

## active 路径边际价值比较
### Run 1 / EMA
- 当前没有新的 `due-now / overdue` continuation；继续认领只会落回 waiting-window 空转

### Run 2 / Scout Seat
- 顶板仍是 `暂无合格新 intake`
- 这轮没有 bot2 点名新的 promoted candidate，也没有新的 fast-lane source 进入 clean replication

### Run 3 / tiny-live plumbing
- 当前最真实的 operator blocker 仍在 `Rank 2`
- `20:36 UTC` 已把 `replay runsheet / now-action queue` 的顺序改成 `SOL -> ETH -> BTC`
- 但 `small_live_rank2_receipt_chain_audit_v1.csv` 仍只会告诉人：三条腿都 `0/3 refs`，**不会**同时告诉人：
  - 谁应该先做
  - 若坚持 `<=25bps` rounding 预算，各腿最小样例金额该是多少
  - `50U` 在各腿上到底是 `pass_25bps / pass_50bps_only / fails_even_50bps_guard`
- 这会让 `receipt-chain audit` 继续把三条腿误表述成“都只是缺 refs”，而不是“缺 refs + replay honesty 级别并不一样”
- 因此本轮主点应是：**把 `Rank 2 receipt-chain audit` 升级成真正可执行的 replay audit**

## 本轮主点 + 紧邻子点
- **主点**：更新 `scripts/build_alpha_closure_board_report.py`，让 `small_live_rank2_receipt_chain_audit_v1.csv` 自动读取 `small_live_rank2_replay_rounding_budget_ladder_v1.csv`
- **紧邻子点**：重建 `alpha_closure_board`，把新的 receipt audit 同步到 reader-facing 页面与 deployable artifact

## 本轮做了什么
### 1) 扩充 replay context
文件：`scripts/build_alpha_closure_board_report.py`

本轮没有新开框架，只补最小必要字段：
- 让 `get_rank2_replay_priority_context()` 除了已有的 `priority / order_text / policy_blurb` 之外，再输出：
  - `suggested_notional_by_symbol`
  - `budget_read_by_symbol`
  - `ladder_row_by_symbol`
- 这些字段直接来自现有 `small_live_rank2_replay_rounding_budget_ladder_v1.csv`，不是重新发明新规则

### 2) 升级 `Rank 2 receipt-chain audit`
文件：`scripts/build_alpha_closure_board_report.py`

本轮把 `get_rank2_receipt_audit_rows()` 从“按 log template 默认顺序枚举”改成“按 rounding 预算真实优先级输出”：
- `audit_order` 现在直接读取 `P1 / P2 / P3`
- 新增三列：
  - `suggested_notional_for_25bps_usdt`
  - `sample_50u_budget_read`
  - `operator_action_read`
- `generated_at_utc` 默认优先使用 rounding ladder 的 `observed_at_utc`
- 输出顺序改成按 replay 优先级排序，而不是模板原始顺序

因此新的 `receipt-chain audit` 不再只是说“三条腿都还没拿到真实 refs”，而是会同时告诉 operator：
- **先做 `SOL` 更诚实**
- `ETH` 若坚持首腿，样例更适合先抬到 `>=100U`
- `BTC` 当前仍只适合作为最后备选，约 `300U` 才接近 `<=25bps` 口径

### 3) 重建 closure board
执行：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`

刷新后关键产物：
- `reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_audit_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

## 当前 hard verdict
**这轮最值得补的不是再写一张 `Rank 2` 同义 packet，而是让 receipt audit 本身变得“可执行”。当前最诚实的 `Rank 2` 读法不该只是“三条 whitelist 腿都缺 `intent/ack/cancel(close)` refs”，而应是：三条腿虽然都还缺 refs，但 replay 诚实度并不相同——若坚持 `50U` 且把 rounding 损耗预算压到 `<=25bps`，当前应先做 `SOL`；`ETH` 更适合先抬到 `>=100U`；`BTC` 继续只保留最后备选。**

更直白地说：
- 现在真正会改状态的动作仍然只有 `1 次 whitelist-bound test/no-fill replay`
- 但这次 replay 也不该再被表述成“随便先做哪条腿都一样”
- 本轮把这个差异压进了 authoritative audit artifact

## reader-facing / deployable 落点
- 网页：`reports/site/factors/alpha_closure_board/report.html`
- artifact：`reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_audit_v1.csv`

新的 audit 关键行现在读成：
- `P1 = SOL-USD / suggested_notional_for_25bps_usdt=40 / sample_50u_budget_read=pass_25bps`
- `P2 = ETH-USD / suggested_notional_for_25bps_usdt=100 / sample_50u_budget_read=pass_50bps_only`
- `P3 = BTC-USD / suggested_notional_for_25bps_usdt=300 / sample_50u_budget_read=fails_even_50bps_guard`

## 验证 / 证据
已验证：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py` 成功
- builder 成功退出并重建 `alpha_closure_board/report.html`
- `small_live_rank2_receipt_chain_audit_v1.csv` 当前确实已按 `P1 / P2 / P3` 排序
- 新 audit 已包含 `suggested_notional_for_25bps_usdt / sample_50u_budget_read / operator_action_read`
- 当前 `P1` 已明确写回 `SOL-USD`

## 风险 / 边界
- 本轮没有触发真实 venue replay
- 本轮没有补新的 Scout candidate，也没有重开 Live Seat
- 本轮没有把 `Rank 2` 从 `paper_candidate_only / blocked` 偷渡成 `shadow_parity passed`
- 本轮只是把**下次唯一允许动作**写得更诚实、更不容易误操作

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
