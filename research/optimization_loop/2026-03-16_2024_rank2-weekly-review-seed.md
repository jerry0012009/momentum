# 2026-03-16 20:24 UTC｜Scout Seat：Rank 2 narrow paper weekly review seed rows

## 为什么这轮选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 走：

- `Paper Seat / EMA` 当前仍是 `running paper pilot / waiting_not_due`，本轮没有新的 `due-now / overdue` refresh；
- `Live Seat` 继续允许暂空；
- 因此默认主资源必须落到 `Run 2 / Scout Seat`。

本轮先比较 active Scout 候选的边际价值：

1. `Rank 2 combo_all`
   - 当前是唯一仍保留前推资格的 Scout 候选，且已经被 desk 收紧为 **`narrow paper pilot approved`**；
   - 前两轮刚补完 `ledger template` 与 `refresh seed rows`；
   - 按 board 7.6，继续认领它时只允许补 `paper ledger / monitoring / refresh / review` 的最小接线，或一刀真正改变 paper verdict 的检查。
2. `Rank 4b stat-arb`
   - 已在 `18:53 UTC` 明确压回 `park / evidence pool`；没有新数据源/新 universe/新 spec，不应再占本轮主资源。
3. 其他候选（Rank 1 / 3 / 原 Rank 4 / 新 intake）
   - 当前都没有比 Rank 2 更接近 desk 主线的可落地动作。

因此本轮主点固定为：
- **把 Rank 2 从 `refresh seed rows` 再推进一格到 `weekly review seed rows`，让它能直接承接 red/yellow/green 巡检，而不是继续停在抽象 monitoring 说明。**

紧邻子点：
- 同步 factor 页与 scout 汇总页，避免结果只停在日志/邮件里。

## 开始前检查
- `git status --short`：工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，本轮不做混提。
- 最近 runs：
  - `2026-03-16_1942_rank2-refresh-seed-rows.md`
  - `2026-03-16_1934_rank2-narrow-paper-ledger-template.md`
  - `2026-03-16_1853_rank4b-time-stability-park.md`
- 轮前 Rank 2 状态：
  - 已有 `paper_candidate_admission_verdict`
  - 已有 `paper_candidate_monitoring_verdict`
  - 已有 `narrow_paper_pilot_ledger_verdict`
  - 已有 `narrow_paper_pilot_refresh_seed_verdict`
  - **尚无** `narrow_paper_pilot_weekly_review_seed_verdict`

## 本轮改动
### 1) `scripts/build_volume_supportflip_higherlow_first_verdict.py`
把脚本里原本已写出的 weekly review seed 骨架真正接入到可交付链路：

- 新增 / 接通 artifact：
  - `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv`
- 把现有函数真正接入主流程：
  - `build_narrow_paper_pilot_weekly_review_seed_rows(...)`
  - `derive_narrow_paper_pilot_weekly_review_seed_verdict(...)`
- 新增 `trial_meta.csv` 字段：
  - `narrow_paper_pilot_weekly_review_seed_verdict`
- 在 Rank 2 factor 页新增 reader-facing 卡片：
  - `narrow paper pilot weekly review seed rows`

这一步的实际逻辑：
- 复用已有 `refresh seed rows`；
- 结合 `asset_summary.csv` 与 `cache_meta.csv`；
- 为 BTC / ETH / SOL 各生成一条 weekly review row，写出：
  - `sample_end_utc`
  - `days_since_last_trade`
  - `lifetime_total_return`
  - `lifetime_false_break_ratio`
  - `weekly_review_status`
  - `primary_watch`
  - `operator_action`
  - `promotion_boundary`

### 2) `scripts/build_trendline_alpha_scout_report.py`
- 在 Rank 2 scout 汇总卡新增：
  - `narrow paper weekly review seed` verdict 行
- 把说明文改成更诚实的当前口径：
  - 这张卡现在承接的不只是 first verdict / paper candidate admission，
  - 还承接 `narrow paper wiring`（`ledger / refresh / weekly review` 的最小接线）。

## 8.1 fallback 记录
- 这轮第一次尝试对 `build_volume_supportflip_higherlow_first_verdict.py` 做精确大块替换时，出现了 `exact text` 未命中的情况；
- 已按要求立刻 fallback 到：先重新读取、再按更稳健的局部定位方式改写；
- 最终没有把整轮直接判失败。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `grep -n "weekly review seed" reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html reports/site/reading/trendline_alpha_scout/report.html`

## 新产物 / deployable artifact
新增：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv`

当前 weekly review rows（基于现有历史样本，不引入新 bar）：
- `BTC-USD`
  - `days_since_last_trade = 34.1`
  - `lifetime_total_return ≈ -1.15%`
  - `lifetime_false_break_ratio = 20%`
  - `weekly_review_status = red`
  - `primary_watch = false_break_watch`
- `ETH-USD`
  - `days_since_last_trade = 0.0`
  - `lifetime_total_return ≈ +3.90%`
  - `lifetime_false_break_ratio = 0%`
  - `weekly_review_status = green`
- `SOL-USD`
  - `days_since_last_trade = 3.3`
  - `lifetime_total_return ≈ +4.22%`
  - `lifetime_false_break_ratio = 0%`
  - `weekly_review_status = green`

## 硬结论（hard verdict）
- 本轮新增结论：
  - **`narrow paper weekly review seed` 已就位。** Rank 2 现在不只是“有 ledger template + refresh seed”，而是已经可以沿同一张审计链直接做 red / yellow / green 周度巡检。
- 更具体地说：
  - **BTC 这条腿必须如实保留 red watch**，因为当前历史样本下仍是负收益且 `false_break_ratio=20%`；
  - ETH / SOL 当前可记为 green；
  - 因此这轮没有把 Rank 2 偷升格成 live-ready，反而把它的 paper review 边界写得更诚实。

## 对 desk 主线的意义
- 这轮符合 board 7.6：
  - 已进入 `narrow paper pilot` 的候选，后续只做最小 `paper ledger / monitoring / refresh / review` 接线；
  - 不再继续打磨 admission / receipt / closeout 近义文档。
- 相比继续补抽象说明，本轮真正减少的是执行 gate：
  - 现在后续可以直接沿 weekly review rows 去补 `refresh writeback / review continuity`；
  - 而不是继续停留在“怎么 review”的文字层。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

## 本轮是否改 `TODO`
- **不改 `docs/TODO.md`。**
- 原因：当前顶板已经能诚实表达 Rank 2 的 seat 角色与后续约束；这轮新增的是更具体的 paper wiring artifact，不涉及新的 desk-level verdict 变化。

## 风险 / 边界
- 这不是新的 alpha 证据，也不是新的 forward continuity；
- 它只是在现有历史样本上，把 Rank 2 的 `weekly review` 接线从抽象说明压成可复用 seed rows；
- `BTC weak pocket / false_break_watch / idle-gap / time-pocket` 仍必须继续如实保留，不得把这次接线误写成 live admission。

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
