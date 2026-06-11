# 2026-03-16 18:20 UTC — Rank 2 replay closeout matrix

## 本轮先看 desk board / seat 状态
- 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- `Paper Seat = EMA` 当前仍属于真实 `waiting_not_due`，本轮不应在 EMA refresh 上空转。
- `Run 2` 当前对 `Rank 2 combo_all` 的 scout 研究已经足够收敛：它仍是窄范围 `paper candidate`，但下一步不该再扩研究，而是继续把 **tiny-live plumbing / 单次 replay closeout** 压实。
- 因此本轮继续按 `Run 3 — tiny-live plumbing` 认领 1 个主点：把上一轮的 `single-replay runsheet` 再往前推成 **closeout / writeback matrix**。

## 启动时 repo / 脏文件检查
- `git status --short` 显示工作区仍有大量与本轮无关的历史脏文件与未跟踪文件。
- 本轮只改：
  - `scripts/build_alpha_closure_board_report.py`
  - `docs/TODO.md`
  - 新生成 `reports/artifacts/alpha_closure_board/small_live_rank2_replay_closeout_matrix_v1.csv`
  - 重建后的 `reports/site/factors/alpha_closure_board/report.html`
- 未做 commit，避免把无关脏文件混提。

## 本轮主点
### 主点：把 Rank 2 的“真实 replay 之后怎么关单”压成 closeout matrix
上一轮已经有：
- `small_live_rank2_replay_runsheet_v1.csv`

但 runsheet 只回答：
- 先跑哪条 whitelist leg；
- 要抓哪三段 refs；
- 首腿成功后最多只允许进到哪个 gate。

它还没有把另一个紧邻执行问题写死：
- **真实 replay 一旦发生，operator 应该开什么 review ticket？**
- **成功时怎么写回 closeout / next queue？**
- **失败时怎么关回 blocked，而不是口头说“之后再补”？**

因此本轮新增：
- `reports/artifacts/alpha_closure_board/small_live_rank2_replay_closeout_matrix_v1.csv`

当前 matrix 把 `ETH -> SOL -> BTC` 三条 whitelist leg 统一压成：
- 建议 review ticket：
  - `SL-DRYRUN-RANK2-ETHUSDT-TEST-RECEIPT-001`
  - `SL-DRYRUN-RANK2-SOLUSDT-TEST-RECEIPT-001`
  - `SL-DRYRUN-RANK2-BTCUSDT-TEST-RECEIPT-001`
- 若 replay 成功：
  - 只能关成 `dry_run_pass -> eligible_for_shadow_parity_review only`
  - 默认 `next_queue_if_pass = shadow_parity`
- 若 replay 失败：
  - 必须继续 `keep dry_run_only / blocked`
  - 默认 `next_queue_if_fail = routing_dry_run_replay`
- 三条腿统一仍要求：
  - `intent_ref + ack_ref + cancel_or_close_ref`
  - 任一缺失 / `scope drift` / `capital > 0` / 缺 `cancel-close` 都继续 blocked。

### 紧邻子点：同步 reader-facing / operator-facing 页面与指挥板
- `alpha_closure_board` 新增 `Rank 2 replay closeout matrix（v1）` 卡片。
- `docs/TODO.md` 的 `Rank 2` 条目新增 `2026-03-16 18:20 UTC` 补充：把“真实 replay 后该如何关单 / 写回 / 进下一队列”钉成 authoritative desk 读法。

## 实现细节
- 修改 `scripts/build_alpha_closure_board_report.py`：
  - 新增 `SMALL_LIVE_RANK2_REPLAY_CLOSEOUT_MATRIX_PATH`
  - 新增 `get_rank2_replay_closeout_matrix_rows()`
  - 新增 `write_rank2_replay_closeout_matrix_csv()`
  - 在 HTML render 中新增 `Rank 2 replay closeout matrix（v1）` 卡片
  - 在 `main()` 中把新 artifact 纳入生成与打印清单
- 本轮中途第一次脚本替换没命中目标片段；已按 loop 护栏执行 fallback：先重读目标片段，再做更稳健的脚本替换，避免把可恢复编辑错误升级成整轮失败。

## 最小验证
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py` ✅
- `python3 scripts/build_alpha_closure_board_report.py` ✅
- 新 artifact 核对：
  - `ETH -> SOL -> BTC` 顺序已保留；
  - 每条腿都已有可直接打开的 review ticket stub；
  - 成功 closeout 统一只到 `eligible_for_shadow_parity_review`；
  - 失败 closeout 统一回到 `dry_run_only / blocked -> routing_dry_run_replay`。
- 页面核对：
  - `reports/site/factors/alpha_closure_board/report.html` 已出现 `Rank 2 replay closeout matrix（v1）` 卡片。

## 本轮硬结论
- `EMA` 当前仍应诚实视为 `waiting_not_due`，本轮不该在 Paper Seat 近义空转。
- `Rank 2` 当前也不该再扩 scout 研究；更接近主线的一步，是把 **真实 replay 后的 closeout / writeback / next queue** 也压成 operator 可直接照抄的 artifact。
- 新硬结论仍然没有变成“更接近 tiny-live 了”；它只是把边界写得更硬：
  - **任一 replay 成功，最多只到 `eligible_for_shadow_parity_review`；**
  - **任一 replay 失败，必须回 `dry_run_only / blocked`；**
  - **在真实三段 refs 同链落地前，`Rank 2` 仍不是 `tiny-live ready`。**

## reader-facing 落点
- 网页：`reports/site/factors/alpha_closure_board/report.html`
- 指挥板：`docs/TODO.md`
- 新 artifact：`reports/artifacts/alpha_closure_board/small_live_rank2_replay_closeout_matrix_v1.csv`

## 后续最小下一步
- 不是继续补近义说明页；而是未来若 operator 真做一次 whitelist-bound `test/no-fill replay`，应直接沿这张 matrix 开 ticket、关 closeout、写 next queue。
- 在真实 `intent_ref + ack_ref + cancel_or_close_ref` 同链落地前，`Rank 2` 继续保持 `paper_candidate_only / blocked`。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，本轮不适合安全 selective commit。
