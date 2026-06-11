# 2026-03-16 18:07 UTC — Rank 2 replay runsheet

## 本轮先看 desk board / seat 状态
- 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- `Paper Seat = EMA` 当前仍属于真实 `waiting_not_due`：本轮不应伪造 refresh，也不应继续把时间花在 EMA 近义说明页上。
- 按 board 固定顺序，本轮从 `Run 1` 自动回退到 `Run 3`：当前 `Rank 2 combo_all` 的 scout 研究结论已经够诚实，剩下更接近执行的一步是继续压实 **tiny-live plumbing / receipt replay 开工包**。

## 启动时 repo / 脏文件检查
- `git status --short` 显示工作区仍有大量与本轮无关的历史脏文件与未跟踪文件。
- 本轮只改：
  - `scripts/build_alpha_closure_board_report.py`
  - `docs/TODO.md`
  - 新增 `reports/artifacts/alpha_closure_board/small_live_rank2_replay_runsheet_v1.csv`
  - 重建后的 `reports/site/factors/alpha_closure_board/report.html`
- 未做 commit，避免把无关脏文件混提。

## 本轮主点
### 主点：把 Rank 2 的“唯一允许动作”压成单次 replay runsheet
在已有：
- `small_live_rank2_routing_dry_run_replay_ticket_v1.csv`
- `small_live_rank2_receipt_chain_operator_packet_v1.csv`
- `small_live_rank2_receipt_chain_log_template_v1.csv`
- `small_live_rank2_receipt_chain_completion_gate_v1.csv`
- `small_live_rank2_receipt_chain_audit_v1.csv`

基础上，再压出一张更接近 operator 开工包的 artifact：
- `reports/artifacts/alpha_closure_board/small_live_rank2_replay_runsheet_v1.csv`

这张 runsheet 直接把：
- replay 优先顺序
- 每个 whitelist leg 的当前 log stub
- 必须抓到的三段 refs
- 成功 / 失败 writeback
- 通过后才允许进入的 gate
- 硬阻断条件

放进同一张表，减少 future run 再临时拼 ticket / packet / gate 的摩擦。

### 紧邻子点：同步 reader-facing / operator-facing 页面与指挥板
- `alpha_closure_board` 新增 `Rank 2 single-replay runsheet（v1）` 卡片。
- `docs/TODO.md` 的 `Rank 2` 条目新增 `2026-03-16 18:07 UTC` 补充，明确当前默认顺序固定为 **`ETH -> SOL -> BTC`**，并再次钉死：首腿 replay 即便成功，也只允许进入 `eligible_for_shadow_parity_review`，仍不得误写成 `tiny-live ready`。

## 代码 / 构建改动
- 改 `scripts/build_alpha_closure_board_report.py`：
  1. 新增 `SMALL_LIVE_RANK2_REPLAY_RUNSHEET_PATH`
  2. 新增 `get_rank2_replay_runsheet_rows()`
  3. 新增 `write_rank2_replay_runsheet_csv()`
  4. 在 HTML render 中新增 `Rank 2 single-replay runsheet（v1）` 卡片
  5. 在 `main()` 中把新 artifact 纳入构建与打印清单
- 生成的 runsheet 当前把优先级压成：
  - `P1 = ETH-USD / ETHUSDT`
  - `P2 = SOL-USD / SOLUSDT`
  - `P3 = BTC-USD / BTCUSDT`

## 最小验证
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py` ✅
- `python3 scripts/build_alpha_closure_board_report.py` ✅
- 新 artifact 内容核对：
  - `ETH -> SOL -> BTC` 顺序已固定；
  - 三条腿都仍要求同一套 `intent -> ack -> cancel/close` receipt chain；
  - `final_gate` 统一仍是 `eligible_for_shadow_parity_review only; still not tiny-live`；
  - `hard_stop` 统一仍是 `scope drift / capital > 0 / missing ack or cancel / new symbol routing => keep blocked`。
- 页面核对：`reports/site/factors/alpha_closure_board/report.html` 已出现 `Rank 2 single-replay runsheet（v1）` 与 `ETH → SOL → BTC` 提示。

## 本轮硬结论
- `EMA` 当前仍应诚实视为 `waiting_not_due`，本轮不该在 Paper Seat 空转。
- `Rank 2` 当前也不需要再扩 scout 研究；更接近 desk 主线的一步，是把唯一允许动作继续压成 operator 真能照着开的单次 replay runsheet。
- 新硬结论不是“更接近 tiny-live 了”，而是：**当前默认开工顺序固定为 `ETH -> SOL -> BTC`；即使首腿 replay 成功，也只是第一次拿到 `eligible_for_shadow_parity_review`，仍不是 `tiny-live ready`。**

## reader-facing 落点
- 网页：`reports/site/factors/alpha_closure_board/report.html`
- 指挥板：`docs/TODO.md`
- artifact：`reports/artifacts/alpha_closure_board/small_live_rank2_replay_runsheet_v1.csv`

## 后续最小下一步
- 不是继续补近义说明页；而是等未来真实 operator replay 时，优先按 `ETH -> SOL -> BTC` 的 whitelist 顺序回填同一条 `intent_ref + ack_ref + cancel_or_close_ref`。
- 在真实三段 refs 同链落地前，`Rank 2` 继续保持 `paper_candidate_only / blocked`。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，本轮不适合安全 selective commit。
