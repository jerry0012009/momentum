# 2026-03-15 22:26 UTC｜首页守门快照改成动态时钟，避免 EMA 到点后仍显示旧 waiting

## 为什么这次选这个
- 先检查了 `git status --short`、`docs/TODO.md`、`AUTO_OPTIMIZATION_LOOP.md`，以及最近几轮 optimization logs。
- 当前 deployment-first 排序没有变：`EMA = closest to paper`、`breakout = one_more_gate`、`Fibonacci = archive`。
- 这轮最接近 deployment 的未完成主线仍是 `EMA` 的下一轮真实 `market-close refresh / week-1 review`，但现在还没到下一根 completed bar，不能伪造 refresh。
- breakout 旧样本也已进入 `same-sample admission freeze`；继续回切只会重复被禁止的 micro-slicing。
- 所以本轮不再补 EMA 近义 queue / board，也不回切 breakout，而是选一个对网页最终表达和实际执行判断都真的有帮助的小任务：**把首页 `Deployment Watch` 从静态 artifact 文案改成按 `next_expected_close_utc` 动态重算的 honest ops clock。**

## 本轮主点
- 主点：`reports/site/index.html` 的 EMA 守门快照改为动态时钟，不再死读旧的 `relative_due_gap / due_bucket`。
- 紧邻子点：把这条变化回写 `docs/TODO.md` / plans 镜像，避免路线图仍把首页当静态摘要卡。

## 做了什么

### 1) 修改 `scripts/build_site_index.py`
新增了两类轻量 helper：
- `format_due_gap()`：按当前 UTC 时间动态重算距离 `next_expected_close_utc` 的剩余时间 / 超时多久；
- `enrich_due_rows()`：在首页构建阶段直接基于 `next_expected_close_utc` 重算：
  - `dynamic_relative_due_gap`
  - `dynamic_due_bucket`
  - `dynamic_is_due`

这让首页级 `Deployment Watch` 不再盲信 EMA artifact 里上一次 build 时写死的：
- `relative_due_gap`
- `due_bucket`

现在即使 EMA 主报告还没重建，首页也能更诚实地回答：
- 现在是不是已经 `due_now / overdue`
- 最靠前 lane 距离真实 close 还剩多久
- 是否应立刻跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

### 2) 更新首页 `Deployment Watch` 的表述
首页 EMA 那一条现在会显式写成：
- `首页已按 next_expected_close_utc 动态重算时钟`

也就是说，这一块已经从“静态摘要”升级成了**轻量 ops clock**：
- 等待窗口里，剩余时间会随每次 index 发布自动刷新；
- 一旦 close 已过，它不会继续把 lane 假装写成旧的 `due_soon / waiting_not_due`。

### 3) 回写 `docs/TODO.md`
在已完成的首页入口任务下面补了一条新的最新补充（`2026-03-15 22:20 UTC`）：
- 首页 `Deployment Watch` 现在会按 `next_expected_close_utc` 动态重算倒计时与 `due_now / overdue` 状态；
- 它已经不只是读取旧 artifact 文案，而是一个更诚实的首页守门时钟。

## 验证 / 证据
执行：
- `python3 -m py_compile scripts/build_site_index.py`
- `python3 scripts/build_plans_site.py`
- `python3 scripts/build_site_index.py`
- `grep -n "动态重算时钟\|22:20 UTC\|Deployment Watch" reports/site/index.html reports/site/plans/momentum_todo.html`

验证结果：
- `build_site_index.py` 语法检查通过；
- 首页已成功重建；
- `reports/site/index.html` 当前显示：
  - `EMA ledger：首页已按 next_expected_close_utc 动态重算时钟；当前还没有 due_now / overdue lane`；
  - 最靠前 lane 仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`；
  - 距下一次 close 约 `1.6` 小时；
- `reports/site/plans/momentum_todo.html` 已同步出现 `2026-03-15 22:20 UTC` 的新补充。

## 这一步的实际价值
- 这不是新的 EMA forward 结果；
- 也不是 breakout 的新 overturn 证据；
- 但它修掉了一个真实的 deployment-facing 表达风险：**首页原先可能在 close 已过后，仍显示旧的 waiting / due-soon 读法。**

修完后，Jerry 即使只看首页，也更不容易被 stale countdown 误导；等真实 close 到来后，也更容易第一时间判断“现在该跑 guarded refresh 了”。

## 风险 / 边界
- 这一步不会替代 EMA 主报告 rebuild；真正的 `due_now / overdue` artifacts 仍要靠 `build_ema_psar_raw_alpha_report.py` / guarded refresh 正式刷新。
- 它只是把首页入口页改成**更诚实的实时判断层**，避免在 rebuild 之间出现 stale ops wording。
- breakout 线本轮没有新增证据，也没有改写 `one_more_gate / up-flat biased conditional alpha` verdict。

## 执行层 hygiene
- `git status --short` 仍显示大量与本轮无关的历史脏改 / 未跟踪文件；本轮没有混提这些无关内容。
- 本轮直接相关文件只有：
  - `scripts/build_site_index.py`
  - `docs/TODO.md`
  - `reports/site/index.html`
  - `reports/site/plans/momentum_todo.html`
  - `research/optimization_loop/2026-03-15_2226_homepage-dynamic-clock.md`

## Commit hash
- HEAD：`35dd4f9`
- 本轮未提交。

## 未提交原因
- 当前 worktree 里存在大量与本轮无关的既有脏改 / 未跟踪文件；在这种状态下做 selective commit 仍有误混无关文件的风险，因此本轮保持未提交更稳妥。
