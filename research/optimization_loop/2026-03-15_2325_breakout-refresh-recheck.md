# 2026-03-15 23:25 UTC｜breakout fresh-refresh recheck：确认仍无 overturn evidence

## 为什么这次选这个
- 先检查了 `git status --short`、`docs/TODO.md`、`docs/AUTO_OPTIMIZATION_LOOP.md`，以及最近几轮 optimization logs。
- 当前 steering 仍是：优先做**更接近 paper / admission** 的事；`EMA` 是 closest to paper，但 line-305 仍要等下一根真实 completed bar，当前 `--require-due` fast-precheck 继续显示还没到点。
- breakout 线则被明确要求：如果还继续做，就只该找**真正可能 overturn scope verdict** 的证据，而不是继续切旧样本 micro-slices。
- 因此本轮选择一个更硬、更短、也更贴近 admission honesty 的动作：对 breakout 做一轮 **fresh-refresh recheck**，看看在真重跑当前 data loader 后，是否终于出现新的 post-tail event / pure-down / pre-down bridge 证据；如果没有，就把“这轮不该再做同类 rerun”的边界写死。

## 本轮主点
- 主点：`support_breakout_v0 / breakout-short follow-up`
- 紧邻子点：把 fresh rerun 的结论压成可复核 artifact，并回写 `docs/TODO.md` / plans 镜像，避免下一轮再把同类 refresh 当成默认高价值动作。

## 做了什么

### 1) 真跑一轮 fresh refresh
执行：
- `.venv/bin/python scripts/build_pytrendline_event_validation_v3_report.py --refresh-data`
- `.venv/bin/python scripts/build_support_breakout_v0_reports.py`

这次不是只读旧 artifact，而是沿当前 loader 真重跑一遍 breakout 的上游样本与下游报告。

### 2) 把关键 admission blocker 压成一张 refresh-recheck artifact
新增：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_refresh_recheck_20260315_20bps.csv`

这张表把本轮最关键的几项 recheck 直接写死：
- `v3_cache_latest_bar_utc`
- `breakout_event_latest_confirm_utc`
- `breakout_event_latest_action_utc`
- `pair_halfsize_pure_down_coverage`
- `pair_halfsize_predown_bridge_12h`
- `pair_halfsize_downrisk_48h`
- `pair_halfsize_future_pure_down_48h`
- `pair_halfsize_pure_test_6h_active_positive_blocks`
- `refresh_recheck_verdict`

### 3) 回写 `docs/TODO.md`
在 breakout freeze 那条已完成项下补了一条最新说明：
- 这轮已经真跑 fresh rerun；
- 但 `event_sample_purged.csv` 的最新 `action_timestamp` 仍停在 `2026-03-10 11:00 UTC`；
- default pair 的硬 blocker 仍完全没动：
  - `pure down = 0/100`
  - `12h pre-down bridge = 0/11`
  - `48h down-risk zone = 0/109`
  - `future pure-down 48h = 0/44`
  - strict pure-test `6h` active-positive blocks 仍只 `1/5`
- 因此 breakout 线继续维持 `same-sample admission freeze / one_more_gate`，下一轮不该再做同类 rerun，除非底层数据窗口或 post-tail 事件真的往后走。

## 产出文件
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_refresh_recheck_20260315_20bps.csv`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- `research/optimization_loop/2026-03-15_2325_breakout-refresh-recheck.md`

## 验证 / 证据
执行：
- `.venv/bin/python scripts/build_pytrendline_event_validation_v3_report.py --refresh-data`
- `.venv/bin/python scripts/build_support_breakout_v0_reports.py`
- `.venv/bin/python scripts/build_plans_site.py`
- `grep -n "2026-03-15 23:25 UTC\|avoid_fluctuating_refresh_recheck_20260315_20bps" docs/TODO.md reports/site/plans/momentum_todo.html`
- `python3` 读取新 artifact / 相关 CSV，确认关键 blocker 仍为 `0/100`、`0/11`、`0/109`、`0/44`、`1/5`

验证结果：
- refresh rerun 成功执行，`pytrendline_event_validation_v3` 与 `support_breakout_v0` 报告已重建；
- 但 breakout 主样本尾部仍未向后推进，最新 `action_timestamp` 还是 `2026-03-10 11:00 UTC`；
- 新 artifact 已落地，并把当前最关键 blocker 全部压成单表；
- `docs/TODO.md` 与 `plans/momentum_todo.html` 已同步写明：当前不存在 fresh overturn evidence，breakout 继续停在 `same-sample admission freeze / one_more_gate`。

## 这一步的实际价值
- 它没有继续在旧样本上做新的 micro-slice；
- 也没有假装 breakout 因为“又刷新了一次”就更接近 admission；
- 它做的是更诚实的一刀：
  - 真跑 fresh rerun；
  - 然后确认**当前 loader 路径下，样本尾部和 blocker 都没变**；
  - 把这件事正式写成 artifact + TODO 边界。

对 Jerry 的实际帮助是：
- breakout 这条线现在不再只是“口头上说别再切旧样本”；
- 而是有一轮 fresh rerun 作为证据，证明当前真的还没有值得 overturn 的新 admission 证据；
- 因此短期资源更该回到 EMA 的下一次真实 close refresh，而不是继续把 breakout rerun 当默认动作。

## 风险 / 边界
- 这轮 recheck 依赖当前 loader 能拿到的最新 bars；它不能证明“未来几天一定不会出现新 breakout event”，只能证明**在这次 fresh rerun 时点，样本尾部与 blocker 还没动**。
- `pytrendline_event_validation_v3` 本身没有被 reopen 成新主线；这里只是把它当 breakout follow-up 的上游样本生成器再跑一遍。
- breakout / Fibonacci 本轮都没有新增更乐观 verdict；新增的是“当前不该再对 breakout 做同类 rerun”的更硬边界。

## 执行层 hygiene
- `git status --short` 显示 worktree 里仍有大量与本轮无关的既有脏改 / 未跟踪文件；本轮没有把这些无关内容混进记录。
- 本轮只选择性补了 breakout recheck artifact、TODO 更新和站点镜像，没有去碰 EMA waiting-window 垫片，也没有 reopen `pytrendline_event_validation_v3` 的延伸任务。

## Commit hash
- HEAD：`f09a838`
- 本轮未提交。

## 未提交原因
- 当前工作区过脏，存在大量与本轮无关的既有修改与未跟踪产物；在这种状态下做 selective commit 风险高。
- 本轮更适合保持为：可审计 artifact + TODO/site 更新 + optimization log。