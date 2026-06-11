# 2026-03-16 20:38 UTC｜Scout Seat：Rank 2 narrow paper continuity snapshot

## 为什么这轮选这个
先按 `TRADING DESK BOARD` 判断：

- `Run 1 / Paper Seat`：`EMA` 已是明确 `waiting_not_due`，本轮不能在 paper refresh 窗口里空转；
- `Run 2 / Scout Seat`：默认主资源位；
- `Live Seat`：仍暂空，没有 bot2 新 promoted candidate。

本轮先比较 active Scout 候选的当前边际价值：

1. `Rank 1 τ-band`
   - 已有 hard verdict：相对 raw 更不差，但绝对 post-cost 仍负；
   - 当前已在 `park / execution guard evidence`，这轮没有新 gate 可降。
2. `Rank 3 third-touch + EMA/MACD`
   - 已补齐最小 `Light Stability Pack`，当前 verdict 已是 `park`；
   - 继续认领只会重复低边际价值 closeout。
3. `Rank 4 / Rank 4b stat-arb`
   - `Rank 4b` 已补完唯一允许的一刀时间稳定性，并明确压回 `park / evidence pool`；
   - 没有新 pair universe / 新数据源 / 新 spec，不适合继续占默认主资源。
4. `Rank 2 combo_all`
   - 当前是唯一仍处于 **`narrow paper pilot approved`** 链路上的候选；
   - 但按 board 7.6 / 7.7，继续认领它时不能再补近义 receipt / closeout / wording；
   - 若继续做，必须是一个真实减少 gate 的最小 `paper ledger / monitoring / refresh / review` artifact。

因此本轮主点固定为：
- **把 Rank 2 现有的 ledger template + refresh seed + weekly review seed + writeback seed 真正并成一份可 append 的 continuity snapshot。**

紧邻子点：
- 把这份 continuity snapshot 挂到 Rank 2 factor 页和 scout 汇总页，避免结果只停在 artifact / 日志层。

## 开始前检查
- `git status --short`：工作区有大量与本轮无关的脏文件 / 未跟踪文件；本轮不做混提。
- 最近 runs：
  - `2026-03-16_2028_rank2-refresh-writeback-seed.md`
  - `2026-03-16_2024_rank2-weekly-review-seed.md`
  - `2026-03-16_1942_rank2-refresh-seed-rows.md`
  - `2026-03-16_1934_rank2-narrow-paper-ledger-template.md`
- 读法：最近 Rank 2 已连续几轮在补 paper wiring；这轮若还继续做它，必须从“说明能接线”推进到“真的有一份可落账快照”。

## 本轮改动
### 1) 新增脚本
- `scripts/build_rank2_narrow_paper_continuity_snapshot.py`

输入：
- `combo_all_narrow_paper_pilot_ledger_template.csv`
- `combo_all_narrow_paper_pilot_refresh_seed_rows.csv`
- `combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv`
- `combo_all_narrow_paper_pilot_refresh_writeback_seed_rows.csv`

输出：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_continuity_snapshot.csv`
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/continuity_snapshot_report.html`

核心作用：
- 不再只是说“可以 writeback / 可以 review”；
- 而是把每条资产腿现在到底处于：
  - `append_ready_green`
  - `append_ready_with_followup`
  - `blocked_by_red_watch`
  真正压成一份可 append 的 narrow-paper continuity snapshot。

### 2) reader-facing 页面同步
最小局部修改：
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
  - 新增 `narrow paper continuity snapshot` 卡片；
  - 链接到 `continuity_snapshot_report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
  - 在 Rank 2 卡片下新增一条 `narrow paper continuity snapshot` reader-facing 行

## 8.1 / fallback 与修正记录
这轮没有遇到 `edit exact text` 型失败，但有一个脚本级可恢复问题：

- 第一次生成 continuity snapshot 时，`ledger template` 中的占位 `weekly_review_status` 字段覆盖了真实 `weekly review seed` 值，导致输出把真实 `red/green` 误写成占位逻辑；
- 发现后立即回退修正脚本：
  - 对 weekly seed 字段显式重命名后再 merge；
  - 增加 `_first_present(...)` 以避免 `0.0` 这类合法值被 Python `or` 吃掉；
- 随后重新运行脚本，最终产出的 continuity snapshot 已恢复为真实状态。

这属于本轮内部修正完成，不构成整轮失败。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_rank2_narrow_paper_continuity_snapshot.py`
2. `python3 scripts/build_rank2_narrow_paper_continuity_snapshot.py`
3. `sed -n '1,8p' reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_continuity_snapshot.csv`
4. `grep -n "continuity snapshot" reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html reports/site/reading/trendline_alpha_scout/report.html`

## 新产物 / deployable artifact
新增：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_continuity_snapshot.csv`
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/continuity_snapshot_report.html`

当前 continuity snapshot 的真实读法：
- `BTC-USD`
  - `weekly_review_status = red`
  - `writeback_status = red_watch_hold`
  - `continuity_status = blocked_by_red_watch`
  - `gate_action = hold_narrow_paper_and_escalate_weekly_ticket`
- `ETH-USD`
  - `weekly_review_status = green`
  - `writeback_status = green_watch_continue`
  - `continuity_status = append_ready_green`
- `SOL-USD`
  - `weekly_review_status = green`
  - `writeback_status = green_watch_continue`
  - `continuity_status = append_ready_green`

## 硬结论（hard verdict）
- 本轮把 Rank 2 从“已有多张 wiring seed 卡”继续推进到：
  - **有一份可直接 append 的 narrow-paper continuity snapshot**。
- 它没有改变 desk verdict：
  - Rank 2 仍然是 `narrow paper pilot approved / paper-only`；
  - 仍然不能越级写成 live-ready。
- 但它确实减少了一个真实 gate：
  - 现在不再只是“知道该怎么写回”；
  - 而是已经能在同一张快照里看清：哪条腿可继续 append，哪条腿必须因 red watch 暂停。

## 对 desk 主线的意义
- 这轮符合当前 `EMA waiting_not_due -> Scout Seat` 的主回退；
- 也符合 board 7.6：
  - 对已进入 `narrow paper pilot` 的候选，只补最小 `ledger / monitoring / refresh / review` 接线；
  - 不再继续补近义 receipt-chain / closeout / admission wording。
- 与最近几轮相比，这轮新增的是**真正可执行的 continuity artifact**，而不是再多一张说明卡。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/continuity_snapshot_report.html`
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

## 是否改 `TODO`
- **不改 `docs/TODO.md`。**
- 原因：本轮没有改变 desk-level seat verdict，也没有改变 `Next 3 bot3 runs`；新增的是 Rank 2 在既有 `narrow paper pilot approved` 范围内的一步最小 continuity artifact。

## 风险 / 边界
- 这不是新的 alpha 证据，不是新的 forward 数据，也不是 live admission；
- 它只是把现有历史样本下的 Rank 2 narrow-paper 链路，压成一份可继续 append / review 的 continuity 快照；
- BTC 这条腿仍必须如实保留 red watch，不能被 ETH / SOL 的 green append-ready 掩盖。

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
