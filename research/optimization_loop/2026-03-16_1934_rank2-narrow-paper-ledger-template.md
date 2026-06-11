# 2026-03-16 19:34 UTC｜Scout Seat：Rank 2 narrow paper pilot ledger template

## 为什么这轮选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查：

- `Paper Seat / EMA` 当前仍是 `running paper pilot / waiting_not_due`，不应把整轮耗在等待下一根 bar；
- `Live Seat` 仍是暂空，且 board 明确说只有 bot2 点名新 promoted candidate 才重新占位；
- 因此本轮必须落到 `Scout Seat`。

本轮先比较了当前 active Scout 候选的边际价值：

1. `Rank 2 combo_all`
   - 已被 board 提升到 `narrow paper pilot approved`；
   - 但过去多轮主要新增的是 `admission write-back / monitoring / receipt-chain / closeout` 类接线；
   - 若继续认领，唯一还符合 board 的动作应是 **paper ledger / refresh / review 的最小接线**。
2. `Rank 4b crypto stat-arb reframe`
   - `18:53 UTC` 已补完允许的唯一决策刀（time stability）；
   - hard verdict 已明确压回 `park / evidence pool`，本轮继续磨它的边际价值很低。
3. `Rank 5 / Rank 6` 新候补
   - 当前更像 desk hypothesis / source intake；
   - 不如已被提升为 `narrow paper pilot approved` 的 `Rank 2` 更接近当前 desk 主线；
   - 且本轮默认优先服务 **paper / repo based 的 5m / 15m crypto** 主线，不扩新大框架。

因此本轮主点固定为：
- **把 Rank 2 从“只有 monitoring board”继续压成一个真正可复用的 `narrow paper pilot` 最小 ledger template**；
- 紧邻子点：同步 reader-facing 页面，让这次推进不只留在日志/邮件里。

## 开始前检查
- `git status --short`：repo 内外仍有大量与本轮无关的脏文件 / 未跟踪文件，因此本轮不做混提。
- 最近 optimization logs：
  - `2026-03-16_1838_rank4b-clean-replication.md`
  - `2026-03-16_1853_rank4b-time-stability-park.md`
  - 更早 `Rank 2` 连续多轮已完成 `paper candidate admission / monitoring / tiny-live closeout` 类接线。
- 当前席位状态：`Paper=EMA waiting_not_due`，`Live=暂空`，`Scout=默认主资源`。

## 本轮做了什么
1. 修改 `scripts/build_volume_supportflip_higherlow_first_verdict.py`
   - 新增 artifact：
     - `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_ledger_template.csv`
   - 新增函数：
     - `build_narrow_paper_pilot_ledger_template()`
     - `derive_narrow_paper_pilot_ledger_verdict()`
   - 将 verdict 写入 `trial_meta.csv`（字段 `narrow_paper_pilot_ledger_verdict`）
   - 在 Rank 2 factor 页新增 `narrow paper pilot 最小 ledger template` 卡片。

2. 修改 `scripts/build_trendline_alpha_scout_report.py`
   - 在 Rank 2 scout 汇总卡新增：
     - `narrow paper pilot ledger` verdict 行
   - 让 reader-facing 页面直接显示这轮交付的是 **可落账的 paper artifact**，而不是继续打磨 closeout wording。

## 8.1 fallback 记录（本轮执行护栏）
- 在给 `build_volume_supportflip_higherlow_first_verdict.py` 插入新 ledger 模板构建段时，`edit` 首次因 exact text 未命中失败；
- 已立即按要求回退到：`read` 精确定位后再做更稳健改写；
- 没有把整轮直接判成失败。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
5. `grep` 校验网页落点：
   - `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`

## 新产物 / deployable artifact
新增最小接线产物：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_ledger_template.csv`

核心模板字段：
- `candidate_id`
- `scope_tag`
- `asset`
- `signal_ts_utc`
- `breakout_ts_utc`
- `entry_ts_utc`
- `exit_ts_utc`
- `cost_bps_roundtrip`
- `false_break_flag`
- `days_since_last_trade`
- `review_slice`
- `weekly_review_status`
- `promotion_boundary`

当前模板已预置三条 scope seed rows：
- `BTC-USD`
- `ETH-USD`
- `SOL-USD`

## 关键结果 / hard verdict
- 新 verdict：
  - `narrow paper pilot ledger：已把 Rank 2 从‘只有 monitoring board’继续压成可直接复用的 3-asset paper ledger template；后续若继续认领它，默认应沿这张账本做 refresh / review，而不是再补 closeout 近义卡。`
- 这轮**没有**改变 Rank 2 的 alpha / seat verdict：
  - 它仍是 `narrow paper pilot approved / paper only`
  - **没有**被偷升格成 `Live Seat / tiny-live`
- 但本轮把当前 board 真正需要的最小接线补齐了一格：
  - 现在 Rank 2 已不只是“有 monitoring board”，而是已经有 **可落账的 narrow paper pilot ledger template**。

## 对 desk 的意义
- 这轮减少的不是学术不确定性，而是 **执行不确定性**：
  - 后续若继续认领 Rank 2，默认就该沿 ledger 模板去补 `refresh row / weekly review row`；
  - 而不是继续回到 `receipt-chain / closeout docs / operator packet` 这类边际价值更低的近义文档。
- 这更符合当前 desk 口径：
  - `Scout Seat` 的目标不是无限研究，而是把候选更快推进到可部署、可审计、可 paper 的状态。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- 首页索引已刷新：`https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 这轮只补最小 paper ledger template，不新增 forward continuity 证据。
- `Rank 2` 仍需继续保留：
  - `idle_gap`
  - `time-pocket`
  - `BTC weak pocket`
 这些诚实 watch 位；不得因为有了 ledger 模板就误写成 live-ready。

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
