# 2026-03-17 08:15 UTC · Rank 27 Mt.Gox neckline confirmation clean replication

## 为什么这轮选这个
- 先检查了 repo 状态、最近 runs、当前脏文件与 desk 顶板：`Paper Seat / EMA` 仍处于 `waiting_not_due`，当前没有新的 `due-now / overdue` lane；`Rank 26` 已压回 `park / evidence pool`，`Rank 17 / Rank 2` 也没有新的真实 `append/review` need。
- 按顶板当前 authoritative override，这轮不能回去围着旧的 `P3/P2` 线做近义接线；`Rank 27` 已在上一轮被明确收敛为“下一轮唯一允许动作 = 1 个最小 clean replication”。
- 因此本轮主点就是把 `Rank 27` 从 source-intake 推到 first verdict；紧邻子点是把 hard verdict 同步写回 `docs/TODO.md` 与 reader-facing 页面。

## 本轮主点 + 紧邻子点
- 主点：对 `Rank 27 Mt.Gox neckline confirmation / pattern-complete breakout gate` 做 1 个最小 clean replication。
- 紧邻子点：把 verdict 写回 `TRADING DESK BOARD` 与网页可见入口，避免它继续停在“已 intake、未判死活”的中间态。

## 先过两条轻量诚实守门
1. **trade on / trade off 清楚可写**
   - `trade on`：双低点/颈线近似先完成，再比较 `raw_breakout / neckline_confirm / neckline_confirm_plus_retest_hold` 三档确认层；全部按 next-bar open 入场。
   - `trade off`：1 ATR stop、2 ATR target、8 bar time stop；并额外记录 `false_break_ratio` 与 `time_to_failure`。
2. **不偷看未来 / 不 repaint**
   - 形态近似只用 `EMA9(hlc3)` one-sided smoothing + `2-bar confirmed extrema`；
   - `neckline_confirm` 不是“回头看未来 12 根都怎样”，而是**等第二个有效确认 close 真发生后**才触发信号；
   - `retest_hold` 也只在确认后的小窗口内等一次回踩不破再触发，不提前知道结果。

## 做了什么
### 1) 新增 Rank 27 clean replication 脚本
- `scripts/build_mtgox_neckline_clean_replication.py`

固定口径：
- 样本：`BTC / ETH / SOL`，复用现有 `Binance 120d / 15m` cache
- 模式近似：`EMA9(hlc3)` + `2-bar confirmed extrema` + 双低点/颈线近似
- 对照：`raw_breakout` vs `neckline_confirm` vs `neckline_confirm_plus_retest_hold`
- 执行：`next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop`
- 指标：`false_break_ratio / post_cost_return / time_to_failure`
- 边界：只做 long 侧 first verdict；short 侧仍需额外 gate，当前不偷做镜像升格

### 2) 跑出 clean replication artifact + reader-facing report
产物：
- `reports/artifacts/scout_mtgox_neckline_confirmation_15m/overall_summary.csv`
- `reports/artifacts/scout_mtgox_neckline_confirmation_15m/asset_summary.csv`
- `reports/artifacts/scout_mtgox_neckline_confirmation_15m/trades.csv`
- `reports/artifacts/scout_mtgox_neckline_confirmation_15m/clean_replication_meta.csv`
- `reports/site/factors/scout_mtgox_neckline_confirmation_15m/report.html`

### 3) 把 verdict 写回 desk 顶板与 scout 汇总页
已更新：
- `docs/TODO.md`
- `reports/site/reading/trendline_alpha_scout/report.html`

## 关键结果（hard verdict）
**`Rank 27` 当前 hard verdict = `park / evidence pool`。**

原因很直接：
- `raw_breakout`：`6bps/side mean_total_return≈-13.79%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈71.56%`
- `neckline_confirm`：`6bps/side mean_total_return≈-17.42%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈62.50%`
- `neckline_confirm_plus_retest_hold`：`6bps/side mean_total_return≈-3.03%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈68.67%`

更直白地说：
- `neckline_confirm` 的确把假突破率压下去一点，但收益更差；
- `neckline_confirm_plus_retest_hold` 的确把亏损收窄了很多，但假突破率并没有比 raw 更干净；
- 最好的 challenger 也**没有同时做到“成本后收益更好”与“假突破率更低”**。

因此这轮最诚实的 desk call 不是继续把它留在 clean-replication 队列，也不是偷升 `paper candidate`，而是：**直接压回 `park / evidence pool`。**

## 最小验证
已执行并通过：
1. `python3 scripts/build_mtgox_neckline_clean_replication.py`
2. `python3 -m py_compile scripts/build_mtgox_neckline_clean_replication.py`
3. 检查 `reports/artifacts/scout_mtgox_neckline_confirmation_15m/overall_summary.csv`
4. 检查 `reports/artifacts/scout_mtgox_neckline_confirmation_15m/asset_summary.csv`
5. 写回并检查 `docs/TODO.md` 与 `reports/site/reading/trendline_alpha_scout/report.html`

## reader-facing 落点
- `reports/site/factors/scout_mtgox_neckline_confirmation_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

## 风险 / 边界
- 这轮只做了 **最小 clean replication**，没有展开完整 `Light Stability Pack`；
- 样本固定为已有 `120d / 15m` cache，不追新 bar、不做额外下载；
- 形态引擎是可部署近似，不是假装完整复刻论文的全部图形学定义；
- short 侧仍没有被授权一起升格，本轮保持排除。

## 对下一轮的含义
1. `Rank 27` 已完成当前允许预算，默认**不要继续重开近义接线**；
2. `Scout Seat` 下一轮应重新比较 active 候选边际价值；
3. 若 `Rank 5 / Rank 6` 仍因额外数据依赖不够便宜诚实，则优先转去新的 `paper / repo based 5m / 15m crypto` intake，而不是反复打磨已 park 的 `Rank 27`。

## Git
- 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮不做 commit，避免混提。
