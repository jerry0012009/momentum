# 2026-03-16 21:07 UTC｜Scout Seat：Rank 2 narrow paper refresh history seed

## 为什么这轮选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 判断：

- `Run 1 / Paper Seat`：`EMA` 已在上一轮完成 due follow-up，当前回到 `waiting_not_due / due_soon`，这轮不能继续在 paper refresh 窗口里空转；
- `Run 2 / Scout Seat`：按当前 authoritative override，是这轮默认主资源位；
- `Live Seat`：仍暂空，没有 bot2 新 promoted candidate。

本轮先比较 active Scout 候选的当前边际价值：

1. `Rank 1 τ-band`
   - 已有 hard verdict：绝对 post-cost return 仍负；
   - 当前停在 `park / execution guard evidence`，没有新 gate 可降。
2. `Rank 3 third-touch + EMA/MACD`
   - 已补完最小 `Light Stability Pack`，当前 verdict 也是 `park`；
   - 继续认领只会重复低边际价值 closeout。
3. `Rank 4 / Rank 4b stat-arb`
   - 原版与窄重开都已压回 `park / evidence pool`；
   - 当前没有新的 pair universe / 新数据源 / 新 spec，不适合继续占主资源。
4. `Rank 2 combo_all`
   - 当前仍是唯一处于 **`narrow paper pilot approved`** 链路上的候选；
   - 但最近几轮已经连续补了 `ledger template / refresh seed / weekly review seed / writeback seed / continuity snapshot`；
   - 如果继续认领，必须做一个真正减少 gate 的最小 `paper ledger / monitoring / refresh / review` artifact，而不是再写近义说明卡。

因此本轮主点固定为：
- **把 Rank 2 从 continuity snapshot 再推进半步，落成一份真正可 append 的 `refresh history` 种子链。**

紧邻子点：
- 把这份 `refresh history` 同步挂到 Rank 2 factor 页与 `Trendline Alpha Scout` 汇总页，避免结果只停在 artifact / 日志层。

## 开始前检查
- `git status --short`：工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮不做混提。
- 最近 runs：
  - `2026-03-16_2052_ema-due-followup-reset-to-scout.md`
  - `2026-03-16_2038_rank2-continuity-snapshot.md`
  - `2026-03-16_2028_rank2-refresh-writeback-seed.md`
- 读法：上一轮已经把 Rank 2 压成 continuity snapshot；这轮若继续做 Rank 2，就必须把它从“静态快照”推进到“可续写历史链”。

## 本轮做了什么
### 1) 新增脚本
- `scripts/build_rank2_narrow_paper_refresh_history.py`

输入：
- `combo_all_narrow_paper_pilot_continuity_snapshot.csv`
- `combo_all_narrow_paper_pilot_refresh_writeback_seed_rows.csv`

输出：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_history.csv`
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/refresh_history_report.html`

核心作用：
- 不再只是描述“当前三条腿分别是什么状态”；
- 而是把 `ETH/SOL` 的 green append-ready 与 `BTC` 的 red-watch blocked，压成 **第一版可 append 的 history rows**；
- 这样 Rank 2 现在不只是“有模板 / 有 snapshot”，而是已经有一张可继续续写的 `paper-only refresh history`。

### 2) reader-facing 页面同步
最小局部同步：
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
  - 新增 `narrow paper refresh history（本轮新增）` 卡片；
  - 链接到 `refresh_history_report.html`。
- `reports/site/reading/trendline_alpha_scout/report.html`
  - 在 Rank 2 卡片下新增一条 `narrow paper refresh history` reader-facing 行。

### 3) 网站落点
- 执行：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
- 首页索引已刷新，`https://jp.jerrypsy.top/momentum/` 可看到最新 note / report 时间戳。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_rank2_narrow_paper_refresh_history.py`
2. `python3 scripts/build_rank2_narrow_paper_refresh_history.py`
3. `grep -n "refresh history" reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html reports/site/reading/trendline_alpha_scout/report.html`
4. `sed -n '1,8p' reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_history.csv`
5. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

## 新产物 / deployable artifact
新增：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_history.csv`
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/refresh_history_report.html`

当前 refresh history 的诚实读法：
- `ETH-USD`
  - `append_status = seed_append_ready_green`
  - `weekly_review_status = green`
  - `gate_action = continue_paper_and_log_review`
- `SOL-USD`
  - `append_status = seed_append_ready_green`
  - `weekly_review_status = green`
  - `gate_action = continue_paper_and_log_review`
- `BTC-USD`
  - `append_status = seed_blocked_red_watch`
  - `weekly_review_status = red`
  - `gate_action = hold_narrow_paper_and_escalate_weekly_ticket`

## 硬结论（hard verdict）
- 本轮把 Rank 2 从“已有 continuity snapshot”继续推进到：
  - **有一份可继续 append 的 narrow-paper refresh history 种子链。**
- 它没有改变 desk-level seat verdict：
  - Rank 2 仍是 `narrow paper pilot approved / paper-only`；
  - 仍然不能越级写成 live-ready。
- 但它确实减少了一个真实 gate：
  - 现在不再只是“知道当前状态”；
  - 而是已经有一张可延续的 history row，可以承接后续 refresh / review 续写，而不是继续停在模板与快照层。

## 对 desk 主线的意义
- 这轮符合当前 `EMA waiting_not_due -> Scout Seat` 的默认回退；
- 也符合 board 7.6：
  - 对已进入 `narrow paper pilot` 的候选，只补最小 `paper ledger / monitoring / refresh / review` 接线；
  - 不再继续补 receipt-chain / closeout / admission 近义卡。
- 与最近几轮相比，这轮新增的是**可 append 的 history artifact**，而不是再多一张静态说明页。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/refresh_history_report.html`
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `https://jp.jerrypsy.top/momentum/`

## 是否改 `TODO`
- **不改 `docs/TODO.md`。**
- 原因：本轮没有改变 desk-level seat verdict，也没有改变 `Next 3 bot3 runs`；新增的是 Rank 2 在既有 `narrow paper pilot approved` 范围内的一步最小 refresh-history 接线。

## 风险 / 边界
- 这不是新的 alpha 证据，不是新的 forward 数据，也不是 live admission；
- 它只是把现有历史样本下的 Rank 2 narrow-paper 链路，从 snapshot 推进到第一版 history；
- `BTC` 这条腿仍必须保留 red watch，不能被 `ETH/SOL` 的 green append-ready 掩盖。

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
