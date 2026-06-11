# 2026-03-15 23:09 UTC｜首页 Recent Activity 合并重复 NO_PROGRESS

## 为什么这次选这个
- 先检查了 `git status --short`、`docs/TODO.md`、`docs/AUTO_OPTIMIZATION_LOOP.md` 和最近几轮 optimization logs。
- 当前 steering 没变：`EMA baseline family = closest to paper`、`support_breakout_v0 = one_more_gate`、`Fibonacci = archived / optional`。
- `EMA` 当前真正未完成的主线仍是下一轮真实 `market-close refresh / week-1 review`，但现在还没到新的 completed daily bar，继续硬做只会重复 waiting-window 补丁。
- breakout 线也已进入 `same-sample admission freeze`；这时继续回切旧样本，不会新增 overturn scope verdict 的证据。
- 所以这轮选一个更贴近**网页最终表达 / Jerry 判断效率**的小任务：把首页 `Recent Activity` 里的重复 `NO_PROGRESS` 合并显示，减少守门噪音，让真实推进更容易被看见。

## 本轮主点
- 主点：首页 `Recent Activity` 合并显示重复 `NO_PROGRESS`。
- 紧邻子点：把这条变化回写 `docs/TODO.md` / plans 镜像，明确它属于 deployment-facing 首页表达改进，而不是新的 alpha 结论。

## 做了什么改动
### 1) 修改 `scripts/build_site_index.py`
新增两段轻量逻辑：
- `_read_no_progress_reason()`：读取最新 `NO_PROGRESS` 记录第一行原因；
- `_collapse_repeated_no_progress()`：把最近窗口内重复出现的 `bot3 / optimization_loop` 的 `no progress` 记录合并成一条。

当前首页的展示方式改成：
- 若最近窗口里出现多条 `NO_PROGRESS`，不再逐条刷屏；
- 只保留一条合并记录，显示：
  - 合并计数；
  - 最新一条记录路径；
  - 最新原因。

### 2) 更新首页说明文案
`Recent Activity / 最近研究动态` 现在会明确说明：
- 重复出现的 `NO_PROGRESS` 会在首页合并显示；
- 目的是避免 waiting-window 噪音盖过真正的新推进。

### 3) 回写 `docs/TODO.md`
在首页入口那条已完成任务下面补了一条最新说明：
- 首页 `Recent Activity` 现在会自动合并重复 `NO_PROGRESS`；
- Jerry 只看首页，也能更快分清“当前是在诚实等待下一根 completed bar”还是“项目又真的有了新的 deployment-facing 产物”。

## 产出文件
- `scripts/build_site_index.py`
- `docs/TODO.md`
- `reports/site/index.html`
- `reports/site/plans/momentum_todo.html`
- `research/optimization_loop/2026-03-15_2309_homepage-no-progress-merge.md`

## 验证 / 证据
执行：
- `python3 -m py_compile scripts/build_site_index.py`
- `python3 scripts/build_plans_site.py`
- `python3 scripts/build_site_index.py`
- `grep -n "NO_PROGRESS\|已合并\|23:09 UTC\|Recent Activity" reports/site/index.html reports/site/plans/momentum_todo.html`

验证结果：
- `build_site_index.py` 语法检查通过；
- 首页已成功重建；
- 首页 `Recent Activity` 已把最近重复的 `NO_PROGRESS` 合并成一条：`no progress × 5（已合并）`；
- 合并项会显示最新原因：`EMA 仍未到下一根真实 completed daily bar，breakout 旧样本也没有新的翻案入口……`；
- `plans/momentum_todo.html` 已同步出现 `2026-03-15 23:09 UTC` 的最新补充。

## 这一步的实际价值
- 这不是新的 EMA forward 结果；
- 也不是 breakout 的新 overturn 证据；
- 但它确实改善了当前项目最常被看到的入口页表达：
  - Jerry 不会再被一串重复 `NO_PROGRESS` 刷屏；
  - 更容易一眼看到真正有新增产物的回合；
  - 也更容易理解：当前某些轮次停下来，是因为在诚实等真实 completed bar，而不是系统空转。

## 风险 / 边界
- 这一步只改善首页信号密度，不会替代真正的 refresh / forward evidence。
- 若后续 `NO_PROGRESS` 原因发生明显变化，首页仍只展示最新一条原因；细节仍需回看原始日志。
- breakout / Fibonacci 本轮没有新增主结论。

## 执行层 hygiene
- `git status --short` 仍显示大量与本轮无关的既有脏改 / 未跟踪文件；本轮没有把这些无关内容混进记录。
- 本轮只改首页入口表达与对应 TODO 注释，没有回切 EMA waiting-window 补丁，也没有 reopen breakout 冻结样本。

## Commit hash
- HEAD：`f09a838`
- 本轮未提交。

## 未提交原因
- 当前 worktree 很脏，存在大量与本轮无关的既有改动和未跟踪产物；此时做 selective commit 风险仍高。
- 本轮更适合保持为可审计未提交产出 + 站点更新 + 邮件记录。
