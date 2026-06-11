# 2026-03-17 07:46 UTC · Rank 2 weekly review writeback seed

## 为什么这轮选这个
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - `Paper Seat / EMA` 在 `07:04 UTC` 的 due-follow-up 已如实消化，当前全 desk 没有新的 `due-now / overdue` lane，因此这轮不能继续停在 `Run 1`。
  - `Rank 26` 的 genuinely verdict-changing 最小检查已在上一轮做完，并压回 `park / evidence pool`。
  - `Rank 17` 的 `weekly review` 也已在上一轮压成 `narrow_paper_pilot_ethsol_weekly_review_writeback_seed.csv`。
- 然后比较 active Scout 候选的当前边际价值：
  1. `Rank 17` 当前最小 `append/review` need 已消化；
  2. `Rank 26` 已完成那唯一值得做的最小诚实检查；
  3. `Rank 2` 的 `combo_all_narrow_paper_pilot_continuity_snapshot.csv` 仍明确显示：`ETH/SOL = append_ready_green`，`BTC = blocked_by_red_watch`；也就是说，这条 `P3 narrow paper pilot` 还存在一个真实、具体、不会改变规则边界的最小 `weekly review writeback` need。
- 因此本轮最诚实的主点不是继续磨 `Rank 17/26`，也不是硬开第二条 fresh intake，而是先把 `Rank 2` 当前真实存在的 `weekly review` 续写需求压成真正可 append 的 writeback rows。

## 本轮主点 + 紧邻子点
- 主点：把 `Rank 2` 当前真实存在的 `weekly review need` 压成 `weekly review writeback seed`。
- 紧邻子点：把新 artifact 同步挂到 factor 页与 reader-facing 总览页，并把 `docs/TODO.md` 顶部 override 更新成“`Rank 2` 当前这一步也已消化，下轮默认切 fresh intake”。

## 先过诚实边界
1. **trade on / trade off 不变**
   - 仍保持已冻结的 `combo_all` 规则，不改策略、不改参数、不改 scope。
2. **不引入 lookahead / repaint / leakage**
   - 只复用已有历史样本与现成 artifact：
     - `combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv`
     - `combo_all_narrow_paper_pilot_continuity_snapshot.csv`
   - 不追新 bar，不重跑重型回测。
3. **seat verdict 不变**
   - `Rank 2` 仍然只是 `narrow paper pilot approved / paper_only_until_new_evidence`；
   - `BTC` 继续保留 `red-watch blocked`，不能借由 writeback 种子被洗成绿腿。

## 做了什么
### 1) 新增脚本
- `scripts/build_rank2_weekly_review_writeback_seed.py`

输入：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv`
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_continuity_snapshot.csv`

输出：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_weekly_review_writeback_seed.csv`
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/weekly_review_writeback_seed.html`

### 2) 产出 append-ready weekly review rows
共 3 行：
- `ETH-USD` → `routine_weekly_review / green`
- `SOL-USD` → `routine_weekly_review / green`
- `BTC-USD` → `red_watch_hold / red`

统一保持：
- `operator_action = append_weekly_review_writeback_seed`
- `writeback_target = combo_all_narrow_paper_pilot_refresh_history.csv`
- `promotion_boundary = paper_only_until_new_evidence`

### 3) 同步 reader-facing 页面
- 更新 `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
  - 新增 `weekly_review_writeback_seed.html` 入口。
- 更新 `reports/site/reading/trendline_alpha_scout/report.html`
  - 在 Rank 2 条目里新增本轮 writeback artifact 的 reader-facing 摘要。

### 4) 写回 desk 顶部板子
- 更新 `docs/TODO.md`：
  - 把顶部 authoritative override 改为：`Rank 2` 当前真实存在的 `weekly review need` 也已被消化；
  - 因此后续默认应切到新的 `paper / repo based 5m / 15m crypto` fresh intake，而不是继续围着 `Rank 2 / Rank 17 / Rank 26` 打磨近义接线。
- 同时在 `Rank 2` 条目下追加 `2026-03-17 07:41 UTC` 最新补充，记录这次 `weekly review writeback seed` 已就位。

## 关键结果（hard verdict）
### 这轮没有改变 Rank 2 的席位判断
- `Rank 2` 仍然只是：**`narrow paper pilot approved`**
- `BTC` 仍然是：**`blocked_by_red_watch / false_break_watch`**
- 没有偷升 `tiny-live`，也没有用 writeback artifact 包装成更高等级。

### 这轮真正补齐的，是当前真实存在的 P3 weekly-review append artifact
- `combo_all_narrow_paper_pilot_weekly_review_writeback_seed.csv` 让 `Rank 2` 的当前 `append_ready_green / blocked_by_red_watch` 不再只停在 weekly seed 或 continuity snapshot。
- 它把当前最诚实的写回口径压成：
  - `ETH/SOL` 可以继续沿 `green weekly review` 追加；
  - `BTC` 继续以 `red_watch_hold` 保持 blocked。

## 一句话结论
**这轮不是继续磨 Rank 2 的 admission / closeout 近义说明，而是把它当前真实存在的 weekly review need 真正压成可 append 的 writeback rows；因此这条 P3 当前可见的最小 `append/review` need 已被进一步消化，下一轮默认应切 fresh intake。**

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_rank2_weekly_review_writeback_seed.py`
2. `python3 scripts/build_rank2_weekly_review_writeback_seed.py`
3. `sed -n '1,12p' reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_weekly_review_writeback_seed.csv`
4. `sed -n '1,80p' reports/site/factors/scout_volume_supportflip_higherlow_15m/weekly_review_writeback_seed.html`
5. `grep -n 'weekly review writeback' reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html reports/site/reading/trendline_alpha_scout/report.html`

## reader-facing 落点
- 页面：`reports/site/factors/scout_volume_supportflip_higherlow_15m/weekly_review_writeback_seed.html`
- 因子主页入口：`reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- 总览页入口：`reports/site/reading/trendline_alpha_scout/report.html`
- Desk 指挥板：`docs/TODO.md` 顶部 `TRADING DESK BOARD`

## 风险 / 边界
- 没有追新 bar
- 没有改策略规则 / 参数 / scope
- 没有同时打开新的 fresh candidate
- 这轮只消化了 `Rank 2` 当前真实存在的 `weekly review` 续写需求，不代表它更接近 `tiny-live`

## Git
- 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮不做 commit，避免混提。
