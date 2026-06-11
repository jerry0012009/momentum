# 2026-03-16 06:42 UTC｜Live Seat 一次性 hard verdict sync（breakout）

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：当前窗口要求 close 前先给 `support_breakout_v0` 打一枪（Run 1），并避免无限重跑。
- `EMA` 线在本轮时点仍是 close 前 waiting-window，不适合伪造 paper refresh，因此本轮优先落 Live Seat。

## 本轮认领
- 主点：`support_breakout_v0` 的一次性 `honest rerun / hard verdict sync`。
- 紧邻子点：把 hard verdict 明确写入可审计 artifact + `TODO` 顶部指挥板镜像，避免下一轮再做同类无边界 rerun。

## 做了什么
1. 先触发一次 Live Seat 重跑尝试（按 board 的“一次性一枪”执行）：
   - `.venv/bin/python scripts/build_pytrendline_event_validation_v3_report.py --refresh-data`
   - `.venv/bin/python scripts/build_support_breakout_v0_reports.py`
2. 由于该路径进入长下载且超时风险明显，本轮不继续硬耗，按 loop 要求切回“复用缓存、避免无必要重型下载”。
3. 基于现有最新可用证据，落地 hard verdict artifact：
   - `reports/artifacts/support_breakout_v0_h24/breakout_live_seat_hard_verdict_20260316_0624.csv`
4. 同步更新 `docs/TODO.md` 顶部 `Live Seat verdict` 最新补充（06:24 UTC），并重建 plans 页：
   - `reports/site/plans/momentum_todo.html`

## 关键证据（本轮 hard verdict）
- `pure_down_coverage = 0/100`
- `predown_bridge_12h = 0/11`
- `downrisk_48h = 0/109`
- `future_pure_down_48h = 0/44`
- 因此当前结论保持：`keep but narrower-scope`，但若下一轮仍无 blocker reduction，默认优先 `bench review`，不再继续同类 rerun。

## 最小验证
- `python3 scripts/build_plans_site.py`（通过，plans 镜像已更新）
- 核对 artifact：
  - `reports/artifacts/support_breakout_v0_h24/breakout_live_seat_hard_verdict_20260316_0624.csv`
- 核对 reader-facing 落点：
  - `docs/TODO.md`
  - `reports/site/plans/momentum_todo.html`

## 风险 / 边界
- 本轮没有新增“blocker 降低”的新数据证据；价值在于把 Live Seat 当前边界压成可审计 hard verdict，防止无限重跑。
- 若后续要继续给 breakout 机会，应优先要求 genuinely new blocker reduction；否则按 board 进入 `bench review` 更诚实。

## 提交状态
- HEAD：`1f84291`
- 本轮未提交（worktree 仍有大量无关脏文件，避免混提）。
