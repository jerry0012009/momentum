# 2026-03-15 19:59 UTC｜EMA 守门刷新入口：把下一次真实 close 的执行动作压成单命令入口

## 为什么这次选这个
- 先检查了 `git status --short`、`docs/TODO.md`、最近几轮 optimization logs。
- 当前 deployment-facing 主线里：
  - `breakout` 当前样本已经 freeze，继续切旧样本只会重复 `one_more_gate / up-flat biased conditional alpha`；
  - `EMA` 真正未完成的主线仍是 **沿同一张 live ledger 落下一轮真实 `market-close refresh / week-1 review`**，但现在还没到下一根 completed daily bar。
- 最近 3 轮已经连续诚实写成 `NO_PROGRESS`；这轮如果再补 queue/source/closure-copy，就会继续踩 steering 明令禁止的近义页。
- 因此本轮选一个更 deployment-facing、但不伪造 forward 的小切口：**把下一次真实 close 的执行守门压成一个单命令入口**，减少到点时还要手动翻 `report / queue / due guardrail` 的执行漂移。

## 做了什么改动
### 1) 新增守门执行脚本
新增：`scripts/run_ema_paper_trading_guarded_refresh.py`

它做的事很克制：
- 默认先重跑 `scripts/build_ema_psar_raw_alpha_report.py`；
- 然后只读取：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_next_close_action_queue.csv`
- 最后只输出三类与执行直接相关的 lane：
  - `due_now_refresh_window`
  - `overdue_refresh_check`
  - `due_soon`

支持的最关键守门参数：
- `--require-due`：如果当前还没有 `due_now / overdue` lane，就直接以退出码 `2` 拒绝继续，把“还没到 close”跟“真的该刷了”硬分开；
- `--skip-build`：复用现有 artifacts，方便本轮只做轻量验证，不再重刷整份 EMA 报告。

### 2) 回写 TODO（但不假装完成主任务）
更新 `docs/TODO.md`，在 EMA 那条仍未完成的主任务下补一条最新说明：
- 现在已经有 `scripts/run_ema_paper_trading_guarded_refresh.py` 这个守门入口；
- 下一次真实 close 到来时，默认先跑这个入口，而不是继续手动翻 queue / report，或再新增近义页面；
- 但这 **不等于** line-299 已完成，因为新的 completed bar 还没到。

### 3) 轻量更新网页可见面
- 只重建了 `plans` 镜像：`python3 scripts/build_plans_site.py`
- 让站点上的 `momentum_todo.html` 也能看到这条新的执行入口说明。
- 本轮**没有**重跑 EMA 主报告生成，避免在没有新 completed bar 的情况下再制造一轮近义 refresh 痕迹。

## 验证 / 证据
执行：
- `python3 -m py_compile scripts/run_ema_paper_trading_guarded_refresh.py scripts/build_plans_site.py`
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --skip-build --show-limit 2`
- `python3 scripts/build_plans_site.py`

验证结果：
- 语法检查通过；
- 守门脚本当前输出为：**没有 `due_now / overdue` lane**，最靠前的是 `Crypto 1d+1wk（BTC/ETH/SOL）`，状态 `due_soon`，距下一次 close 约 `4.4` 小时；
- 说明脚本没有伪造 refresh，而是正确复用了现有 guardrail / queue 产物，把当前状态压成单命令可读输出；
- `plans` 镜像已成功重建，`reports/site/plans/momentum_todo.html` 已包含这条新说明。

## 风险 / 边界
- 这不是新的 EMA alpha 证据，也不是新的 paper review；它只是在**执行层**把“到点再跑”和“还没到点别伪跑”写得更硬。
- 本轮没有改写 `breakout` verdict，也没有解除 `EMA` 的等待事实：当前仍应等下一根真实 completed daily bar。
- 脚本默认会重跑 `build_ema_psar_raw_alpha_report.py`；本轮验证时用了 `--skip-build`，就是为了避免在 close 前再生成一轮近义 refresh 输出。

## 下一步建议
1. 到了下一次真实 close（尤其 `Crypto 1d` 的 `2026-03-16 00:00 UTC`）后，默认先跑：
   - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 若脚本仍返回“没有 due-now / overdue lane”，就继续等，不伪造 refresh；
3. 若进入 `due_now / overdue`，再沿同一张 live ledger 真落下一轮 refresh / review，而不是再补新的 queue/closure-copy 页面。

## 执行层 hygiene
- `git status --short` 显示工作区仍有大量与本轮无关的既有脏改 / 未跟踪文件；本轮没有把这些无关变动混进来。
- 本轮直接相关的文件只有：
  - `scripts/run_ema_paper_trading_guarded_refresh.py`
  - `docs/TODO.md`
  - `reports/site/plans/momentum_todo.html`

## Commit hash
- HEAD：`48edfb3`
- 本轮未提交。
- 原因：当前 worktree 噪音很大，且存在大量与本轮无关的历史脏改 / 未跟踪产物；为避免误把无关文件混入，本轮保持未提交更安全。
