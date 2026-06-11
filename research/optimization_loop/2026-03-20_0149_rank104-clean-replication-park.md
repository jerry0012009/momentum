# 2026-03-20 01:49 UTC — Rank 104 post-break sign-flip density clean replication → park

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `5.2h`）
  - 脚本如实返回 `require-due` guard，不做伪 refresh
- 因此按当前 `TRADING DESK BOARD` 的 authoritative `Next 3`，本轮必须落在 `Scout Seat`，不能空转。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1623`
- 最近 optimization logs：
  - `2026-03-20_0115_rank104-post-break-signflip-intake.md`
  - `2026-03-20_0054_rank103-clean-replication-park.md`
  - `2026-03-20_0034_rank103-confirmed-extremum-intake.md`
  - `2026-03-20_0009_ema-crypto-due-refresh.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前的 `Scout Seat` 候选顺序为：`Rank 104 / post-break sign-flip density > body-defined zone re-entry honest failure verdict > MTF CHOP charged-up count > prebreak higher-low pressure ladder context gate`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T01:22:46Z` 仍是 `new_closed_trades_appended=0`，不构成 `P3 continuity` 插队理由。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 104 / post-break sign-flip density`**
   - 上轮已完成 intake 且过了两条轻量诚实守门；当前是唯一合法的 queue-facing 下一手。
   - 直接回答 breakout 后“走得很顺”到底应不应该被奖励，最贴当前 desk 的管理层主线。
2. **`body-defined zone re-entry honest failure verdict`**
   - 是当前最邻近的 fresh repo reserve，但在 `Rank 104` 尚未拿到 clean replication verdict 前，不该提前抢占本轮主资源位。
3. **`MTF CHOP charged-up count` / `prebreak higher-low pressure ladder context gate`**
   - 仍是后置 reserve；当前边际价值低于 `Rank 104` 的 verdict 收口。
4. **旧 `P1 evidence_pool` / `P3 continuity` / `tiny-live plumbing`**
   - 当前都不该抢主资源位。

结论：本轮只认领 `Rank 104` 的唯一那手 clean replication，不并开第二条候选。

## 本轮认领
- 主点：`Rank 104 / post-break sign-flip density`
- 紧邻子点：把 clean replication artifact、reader-facing 页面、`TODO` 顶板与下一轮顺序一次写齐

## Clean replication 口径（strict non-leaky early-window）
- 固定样本：`BTC/ETH/SOL 120d 15m` 本地 cache
- breakout 事件定义沿用 digest：
  - `close` 突破 `prev_high_20 / prev_low_20`
  - `body_ratio >= 0.4`
  - `extension >= 0.2 ATR`
- 关键诚实约束：
  - 决策只允许使用 breakout 后**前 3 根已完成 bars** 的 sign-flip count
  - 之后只评估后续 `5` 根的 residual 管理价值
  - 不允许把完整 `6` 根 path 倒灌回 breakout 当下
- 管理政策对比：
  - `baseline_hold8`
  - `overlay_exit_low_after_3bars`（若 early-window 为 `low_flip_0`，则在第 `4` 根 open 提前退出；其余继续持有到 `8` bars）
- 统一执行：`signal 当根及之前数据 + next-bar open + no-overlap` 的 clean-room 读法

## 结果摘要
### 事件分桶
- 样本总数：`N=2108`
- `low_flip_0`：`446`（`21.16%`）
  - `mean_gross_ret_hold8 ≈ +1.89bps`
  - `mean_gross_ret_residual_5bars ≈ -0.84bps`
  - `cont_hit_rate_after_decision ≈ 73.54%`
  - `fail_back_inside_rate_after_decision ≈ 65.02%`
  - `tail_loss_p05_after_decision ≈ -202.29bps`
- `mid_flip_1`：`1050`（`49.81%`）
  - `mean_gross_ret_hold8 ≈ +5.60bps`
  - `mean_gross_ret_residual_5bars ≈ -1.19bps`
  - `fail_back_inside_rate_after_decision ≈ 58.38%`
- `high_flip_2`：`612`（`29.03%`）
  - `mean_gross_ret_hold8 ≈ +2.99bps`
  - `mean_gross_ret_residual_5bars ≈ +3.96bps`
  - `fail_back_inside_rate_after_decision ≈ 65.03%`

### 6 bps/side 管理政策对比
- `baseline_hold8`
  - `mean_net_ret ≈ -7.94bps`
  - `tail_loss_p05 ≈ -179.13bps`
  - `positive_rate ≈ 38.71%`
- `overlay_exit_low_after_3bars`
  - `mean_net_ret ≈ -7.79bps`
  - `tail_loss_p05 ≈ -167.15bps`
  - `positive_rate ≈ 38.76%`
- 差值：
  - `overlay - baseline mean_net_ret ≈ +0.16bps`
  - `overlay - baseline tail_loss_p05 ≈ +11.99bps`（轻微削尾）

### side 读法
- `long`：low-flip 提前退出反而略差，`mean_net_ret` 从约 `-12.79bps` 变成 `-13.08bps`
- `short`：确有一点改善，`mean_net_ret` 从约 `-3.55bps` 到 `-2.99bps`，但仍远不够支撑升格

## 当前硬结论
**`Rank 104 = park / evidence pool`**。

翻成人话：把完整 6 根 path 改成诚实的 early-window 之后，这条线仍只留下一个很弱的风险管理影子——它更多是在帮你稍微少挨一点尾部回撤，而不是把 shared gate 的 expectancy 真正推过门槛。这个量级不足以继续占默认 Scout 主资源位。

## 本轮交付（deployable artifact）
- artifact：
  - `reports/artifacts/scout_rank104_post_break_signflip_density_15m/event_log.csv`
  - `reports/artifacts/scout_rank104_post_break_signflip_density_15m/bucket_summary.csv`
  - `reports/artifacts/scout_rank104_post_break_signflip_density_15m/side_summary.csv`
  - `reports/artifacts/scout_rank104_post_break_signflip_density_15m/policy_compare.csv`
  - `reports/artifacts/scout_rank104_post_break_signflip_density_15m/verdict_summary.csv`
  - `reports/artifacts/scout_rank104_post_break_signflip_density_15m/summary_snapshot.json`
- reader-facing 页面：
  - `reports/site/factors/scout_rank104_post_break_signflip_density_15m/report.html`
  - `reports/site/reading/repo_scout/rank104_post_break_signflip_density_clean_replication.html`
- 可复现脚本：
  - `scripts/build_rank104_post_break_signflip_clean_replication.py`

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 默认从 `Rank 104` 切到 **`body-defined zone re-entry honest failure verdict`**
- 当前 active Scout 顺序应改写为：
  1. `body-defined zone re-entry honest failure verdict`
  2. `MTF CHOP charged-up count`
  3. `prebreak higher-low pressure ladder context gate`
  4. `Rank 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`（`P0 park / evidence pool`）
  5. `Rank 93 / 90 / 91 / 82 / 80 / 81`（`P1 evidence_pool / budget used`）
  6. `P3 continuity sidecar`
  7. `tiny-live plumbing`
- 当前最新 `Next 3`：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 body-defined zone re-entry honest failure verdict 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 body-defined zone re-entry honest failure verdict guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则切 MTF CHOP charged-up count；只有 fresh source 也 exhausted，才允许继续回退到 prebreak ladder > 旧 evidence_pool > P3 continuity > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前仍是 `waiting_not_due`
- `python3 scripts/build_rank104_post_break_signflip_clean_replication.py`
  - 成功生成 rank104 clean replication artifact 与 reader-facing 页面
- 回读以下文件，确认已写入成功：
  - `reports/artifacts/scout_rank104_post_break_signflip_density_15m/verdict_summary.csv`
  - `reports/site/factors/scout_rank104_post_break_signflip_density_15m/report.html`
  - `docs/TODO.md`

## 备注
- 本轮没有并开 `body-defined zone re-entry`、`MTF CHOP` 或 `P3 continuity`
- 本轮没有触发 `edit exact text 不匹配` fallback（直接使用 `write + 脚本稳健改写`）
- 工作区仍有大量历史脏文件；本轮未尝试整理、提交或覆盖这些无关改动
