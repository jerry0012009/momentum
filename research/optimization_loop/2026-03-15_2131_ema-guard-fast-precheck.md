# 2026-03-15 21:31 UTC｜EMA 守门入口减负：未到点时先 fast-precheck，跳过整份报告重建

## 为什么这次选这个
- 先检查了 `git status --short`、`docs/TODO.md`、`AUTO_OPTIMIZATION_LOOP.md`，以及最近几轮 optimization logs。
- 当前 deployment-first 口径下，真正还没完成、且最接近 `paper trading / 伪实盘` 的主线仍是 EMA 同一张 live ledger 的下一轮真实 `market-close refresh / week-1 review`。
- 但本轮真跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 后，当前最靠前 lane 仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`，距下一次真实 close 还约 `2.5` 小时；也就是说，**现在还不能诚实地产出新的 refresh 结果**。
- 同时我发现一个真实 execution friction：现有守门脚本在 `--require-due` 下，即使所有 lane 都还没到点，也会先重建整份 EMA 主报告与 artifacts。这会在等待窗口里反复做重活，但并不增加任何新的 deployment 证据。
- 所以本轮不再补近义 queue / closure-copy，而是选一个更接近 deployment 执行面的、小而完整的任务：**把 guarded refresh 入口改成先做 fast-precheck；若所有 `next_expected_close_utc` 仍在未来，就直接跳过 full rebuild。**

## 本轮主点
- 主点：`EMA guarded refresh` 在 waiting window 里先 fast-precheck，减少无效 full rebuild。
- 紧邻子点：把这条 execution 改进回写 `docs/TODO.md` / plans 镜像，避免路线图仍把“反复重建”当成正常巡检方式。

## 做了什么改动

### 1) 修改 `scripts/run_ema_paper_trading_guarded_refresh.py`
新增/调整了三部分逻辑：
- 新增 `parse_utc_timestamp()` / `format_due_gap()`，把 `next_expected_close_utc` 变成脚本内可比较的 UTC 时间；
- 新增 `maybe_fast_precheck()`：
  - 只在 `--require-due` 且未显式 `--skip-build` 时启用；
  - 若现有 `ema_paper_trading_due_guardrail_snapshot.csv` 与 `next_close_action_queue.csv` 已存在，且所有 lane 的 `next_expected_close_utc` 都还在未来，则**直接跳过本轮 full rebuild**；
  - 同时仍输出当前最靠前 lane、动态剩余时间、到点动作与阻塞回退提示；
- 只有在以下情况之一出现时，才继续走原来的完整 rebuild 路径：
  - 缺 artifact；
  - 某个 `next_expected_close_utc` 无法解析；
  - 已经到点或超时，需要重新计算 `due-now / overdue`。

这一步的核心价值不是“让脚本更漂亮”，而是把高频等待窗口里的巡检成本压下去：**还没到真实 close 时，默认先做轻量守门，而不是每次都重建整份 EMA 报告。**

### 2) 回写 `docs/TODO.md`
在 EMA 那条尚未完成的主任务下面，补了一条新的 `[x]` 最新补充（`2026-03-15 21:29 UTC`）：
- guarded refresh 现在有 `fast-precheck`；
- 当所有 `next_expected_close_utc` 仍在未来时，会跳过 full rebuild；
- 真正到点后再回到完整 `rebuild + ledger append` 路径。

这让 TODO 的 deployment-facing 口径更准确：当前等待窗口里的合理动作，不是反复重建报告，而是轻量守门并等真实 completed bar。

## 验证 / 证据
执行：
- `python3 -m py_compile scripts/run_ema_paper_trading_guarded_refresh.py`
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due --show-limit 2`

验证结果：
- 语法检查通过；
- 新脚本已直接走 `fast-precheck` 分支，输出：
  - `fast-precheck：所有 lane 的 next_expected_close_utc 仍在未来，跳过本轮 full rebuild`；
  - `ema_paper_trading_refresh_history.csv` 在下一根 completed bar 到来前不会出现新 rows；
  - 当前仍没有 `due-now / overdue` lane；
  - 最靠前 lane 仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `2.5` 小时后到点；
- 并且本轮没有再出现整份 EMA 主报告重建输出，说明 waiting window 的守门入口已经减负成功。

## 风险 / 边界
- 这不是新的 EMA forward 结果，也不是新的 week-1 review；它只是在执行层减少“还没到点就重建整份报告”的无效开销。
- `fast-precheck` 只在“所有 `next_expected_close_utc` 都还在未来”时跳过 full rebuild；一旦到点 / 超时 / artifact 缺失 / 时间解析失败，脚本仍会回到完整 rebuild 路径，不会拿轻量预检冒充真实 refresh。
- breakout 线本轮没有新增证据，也没有改写当前 `one_more_gate / up-flat biased conditional alpha` verdict。

## 下一步建议
1. 在下一次真实 close 到来前，EMA 巡检默认优先跑：
   - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 如果输出仍是 `fast-precheck`，就继续等，不伪造 refresh。
3. 一旦出现 `due-now / overdue`，下一轮再沿同一入口走完整 `rebuild + ledger append + keep/recheck/demote` 路径。

## 执行层 hygiene
- `git status --short` 显示当前 worktree 里仍有大量与本轮无关的既有脏改 / 未跟踪文件；本轮没有把这些无关改动混进来。
- 本轮直接相关文件只有：
  - `scripts/run_ema_paper_trading_guarded_refresh.py`
  - `docs/TODO.md`
  - `research/optimization_loop/2026-03-15_2131_ema-guard-fast-precheck.md`

## Commit hash
- HEAD：`9884685`
- 本轮未提交。

## 未提交原因
- 当前 repo worktree 里存在大量与本轮无关的历史脏改 / 未跟踪文件；在这种状态下做 selective commit 仍有误混无关文件的风险，因此本轮保持未提交更稳妥。
