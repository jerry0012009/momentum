# 2026-03-17 05:59 UTC · Rank 17 narrow paper continuity snapshot

## 为什么这轮选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 读当前席位：
- `Paper Seat / EMA`：crypto due-now 窗口已在 `00:20 UTC` 实际消化，当前仍是 `waiting_not_due`
- `Live Seat`：仍空，且没有 bot2 新 promoted candidate
- 因此本轮默认应落到 `Run 2 / Scout Seat`

再比较所有 active Scout 候选当前边际价值：
1. `Rank 17 pullback recovery confirmation`
   - 已是 `narrow paper pilot approved（ETH+SOL only）`
   - 已有 `refresh_history / monitoring_board / weekly_review_queue`
   - 但还缺一张把这些 P3 接线真正并成“可直接续写、能一眼看清 ETH/SOL append-ready 与 BTC excluded red-watch 边界”的 continuity snapshot
2. `Rank 2 combo_all`
   - 同样是 `P3 narrow paper pilot approved`
   - 但最近已连续补完 `continuity snapshot -> refresh history`，当前未见新的真实 append/review 缺口
3. fresh intake
   - 只有在 `P3 / P2 / P1` 都没有真实允许动作时才该拿默认主资源
   - 这轮 `Rank 17` 仍有一个合法且最小的 `P3` 接线缺口，因此不应跳去新 intake

因此本轮主点固定为：**给 `Rank 17` 补 1 张真正可部署的 `P3 continuity snapshot`**。

## 本轮主点 + 紧邻子点
- 主点：新增 `Rank 17` 的 `narrow paper continuity snapshot` artifact
- 紧邻子点：把该 artifact 同步挂到 `Rank 17` factor 页，形成 reader-facing 网页落点

## 做了什么
### 1) 新增脚本
- `scripts/build_pullback_recovery_narrow_pilot_continuity_snapshot.py`

输入：
- `narrow_paper_pilot_ethsol_refresh_history.csv`
- `narrow_paper_pilot_ethsol_weekly_review_queue.csv`
- `narrow_paper_pilot_ethsol_monitoring_board.csv`

输出：
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_continuity_snapshot.csv`
- `reports/site/factors/scout_pullback_recovery_confirmation_15m/continuity_snapshot_report.html`

逻辑：
- 不追新 bar、不改信号规则、不下载数据
- 只把现有 `refresh_history + review queue + monitoring watch` 合并成一张 `P3 continuity snapshot`
- 结果直接区分：
  - `ETH / SOL = append_ready_green`
  - `BTC = excluded_red_watch`
- 同时把 `next_review_due_utc` 固定为当前 `sample_end + 7d`

### 2) reader-facing 页面同步
更新：
- `reports/site/factors/scout_pullback_recovery_confirmation_15m/report.html`

新增卡片：
- `ETH+SOL narrow paper continuity snapshot（本轮新增）`
- 直接把 ETH / SOL / BTC 三条腿的 `scope_tag / continuity_status / review bucket / gate_action` 摆出来
- 并链接到新页面 `continuity_snapshot_report.html`

## 本轮新增 artifact / 网页落点
新增：
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_continuity_snapshot.csv`
- `reports/site/factors/scout_pullback_recovery_confirmation_15m/continuity_snapshot_report.html`

同步更新：
- `reports/site/factors/scout_pullback_recovery_confirmation_15m/report.html`

## 核心结果
### ETH / SOL
- `continuity_status = append_ready_green`
- `weekly_review_status = green_keep_narrow_pilot`
- `review_bucket_queue = bucket_1`（ETH） / `bucket_1, bucket_2`（SOL）
- `gate_action = continue_paper_and_append_refresh_review`

### BTC
- `scope_tag = park_btc_excluded_leg`
- `continuity_status = excluded_red_watch`
- `weekly_review_status = red_keep_parked`
- `gate_action = keep_btc_excluded_and_require_new_honest_evidence`

### Reader-facing 边界
- 这轮不是升格，也不是新 alpha 证据
- 只是把 `Rank 17` 的 `P3 narrow paper pilot` 再推进半步，变成一张更可执行的 continuity artifact
- `promotion_boundary` 仍保持：
  - `ETH/SOL = paper_only_narrow_pilot_until_new_live_clearance`
  - `BTC = park_until_new_honest_evidence`

## hard verdict
- `Rank 17` 仍维持：**`narrow paper pilot approved（ETH+SOL only）`**
- `BTC` 仍维持：**`park / excluded red-watch leg`**
- 本轮价值是：**补齐一张真正能承接后续 refresh / review append 的 `P3 continuity snapshot`**，而不是继续磨 wording / admission 近义卡

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_pullback_recovery_narrow_pilot_continuity_snapshot.py`
2. `python3 scripts/build_pullback_recovery_narrow_pilot_continuity_snapshot.py`
3. `sed -n '1,8p' reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_continuity_snapshot.csv`
4. `grep -n "Rank17 narrow paper continuity snapshot\|narrow_paper_pilot_ethsol_continuity_snapshot.csv" reports/site/factors/scout_pullback_recovery_confirmation_15m/continuity_snapshot_report.html`

## TODO / board 是否改动
- **未改 `docs/TODO.md`**
- 原因：本轮没有改变 desk-level seat verdict，也没有改变 `Next 3 bot3 runs`；新增的是 `Rank 17` 在既有 `P3 narrow paper pilot` 边界内的一张 continuity artifact

## 风险 / 边界
- 本轮没有追最新 bar
- 没有重跑重型下载
- 没有改 `Live Seat`、没有触碰 tiny-live
- 没有把 `BTC` 弱腿洗白成 pilot green row

## Git / 提交
- 本轮未提交
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit
