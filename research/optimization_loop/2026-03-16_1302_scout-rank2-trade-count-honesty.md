# 2026-03-16 13:02 UTC｜Scout Seat：Rank 2 combo_all trade-count honesty / cadence dry-check

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 守门：

- **Run 1 / Paper Seat**：`EMA` 仍是 `running paper / waiting_not_due`，当前没有新的 `due-now / overdue` lane。
- **Run 2 / Scout Seat**：当前默认主点不是追最新 bar，而是沿 `Scout Fast Lane` 继续把候选推进到更诚实的 `轻量稳定性快筛 -> paper candidate / park`。
- 结合 `research/strategy_review/2026-03-16_1250_strategy-review.md`，上一轮已经给 `Rank 2 combo_all` 补了 `shadow-readiness dry-check`；紧邻、且仍属于**纯历史样本**的一刀，就是把它的 `trade-count / cadence` 单独压成一张诚实检查卡，回答它是不是靠过稀疏、过偏科的样本撑出来。

因此本轮只认领 **1 个主点**：为 `Rank 2 combo_all` 补一张 `trade-count honesty / cadence dry-check`；并认领 **1 个紧邻子点**：把这个结论同步到 Rank 2 factor 页与 scout 总览页。

## 开始前检查
### repo / 脏文件
`git status --short` 显示 worktree 中仍有大量与本轮无关的既有脏文件和未跟踪产物（EMA、旧 breakout、站点页、workspace 根目录文件等）。本轮只碰：

- `scripts/build_volume_supportflip_higherlow_first_verdict.py`
- `scripts/build_trendline_alpha_scout_report.py`
- 新生成的 Rank 2 artifact / site 页面
- 本轮 run log

不混碰其他主题，也不做整仓提交。

### 当前席位状态
- `Paper Seat = EMA`：`waiting_not_due`
- `Live Seat`：当前默认空席，不强撑 weak challenger
- `Scout Seat`：继续拿主资源，但本轮动作必须是**历史样本上的轻量稳定性收紧**，不是 continuity / 等新 bar

## 本轮做了什么
### 主点：新增 `combo_all_trade_count_honesty.csv`
更新脚本：`scripts/build_volume_supportflip_higherlow_first_verdict.py`

新增 artifact：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_trade_count_honesty.csv`

新增检查逻辑（全部基于现有 `trades.csv`，不拉新数据）：
1. `min_asset_trade_floor`：每个资产至少有最小交易数；
2. `asset_concentration_watch`：是否被单一资产过度主导；
3. `calendar_breadth_floor`：每个资产至少跨过若干活跃月份；
4. `side_balance_watch`：是否几乎只剩单边交易；
5. `idle_gap_guard`：同一资产的相邻 `combo_all` 交易之间是否出现过长空窗。

### 紧邻子点：把 cadence verdict 外显到网页
同步更新：
- `scripts/build_trendline_alpha_scout_report.py`

重新生成：
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

这样 Jerry 不只在日志/邮件里看到这轮结论，也能在 reader-facing 页面里直接看到 `trade-count honesty / cadence` 的新卡。

## 最小验证
执行：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `grep` 校验网页落点包含 `trade-count honesty / cadence dry-check`

全部通过。

## 关键结果 / hard verdict
`reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_trade_count_honesty.csv` 给出的当前读法：

- `min_asset_trade_floor`：**pass**（最少资产也有 `5` 笔）
- `asset_concentration_watch`：**pass**（最大单资产占比 `40.00%`）
- `calendar_breadth_floor`：**pass**（每个资产至少跨 `3` 个活跃月份）
- `side_balance_watch`：**pass**（最偏的一侧占比 `71.43%`，尚未超过 watch 门槛）
- `idle_gap_guard`：**fail**（最大交易空窗约 `58.6` 天）

一句话 hard verdict：

**`Rank 2 combo_all` 的最小交易数和月度分布足以支撑 `keep-narrower` 读法，但交易节奏仍偏稀疏，存在最长约 `58.6` 天的空窗；因此它还不适合被升格成 `shadow-admission-ready`，更不应被偷写成 tiny-live 候选。**

## 这轮结果对 desk 的含义
- 这张卡没有推翻上一轮的 `shadow-readiness dry-check`，而是把其中“trade-count 过关”进一步拆开成更诚实的 cadence 读法；
- 它支持继续把 `combo_all` 读成 **keep-narrower shadow-candidate / one more light check**；
- 但也明确说明：即便收益、friction、false-break 还不错，只要交易节奏仍这么稀疏，就不能跳步把它写成 `shadow-admission-ready / replace-ready / tiny-live ready`。

## 风险 / 边界
- 这仍然只是 **历史样本上的轻量稳定性检查**，不是 continuity，也不是新的 forward evidence；
- `idle_gap_guard` 的阈值是 desk honesty 用的保守门槛，不是学术上唯一正确门槛；
- 这轮没有新增席位切换：`EMA` 继续 `waiting_not_due`，`Live Seat` 继续空席。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

## Commit hash（基线）
- `b3c2dc4`

## 如果未提交，原因
当前 worktree 里有大量与本轮无关的既有脏文件和未跟踪文件；为避免混提，本轮只做 selective 构建、网页刷新与 run log 记录，不做提交。
