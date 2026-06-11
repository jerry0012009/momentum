# Fibonacci 收口标签正式写死

## 为什么这次选这个

这轮没有再开新验证，而是沿 `Fibonacci confirmation / retest_hold` 这条收口线，把最后一个仍未完全写死的小问题补完：**它在当前项目里到底算什么**。

原因很简单：
1. `docs/TODO.md` 里 Fibonacci 仍有两条收口任务没勾掉；
2. `support_breakout_v0_fib_ab` 页虽然已经有 A/B 结论，但还缺一个更明确的角色归类段，容易让人误读成“只是暂时不强、以后也许还能当主 alpha”；
3. 这是一个足够小、但能真正把这条线从“半收口”推进到“正式归档”的动作。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 在 `support_breakout_v0_fib_ab` 页的 `Fibonacci 这条线的最终结论` 段里，补齐了四件事：
     - 它原本想解决什么；
     - 它确实改善了什么；
     - 它没改善什么；
     - 为什么当前不再把它当主 alpha。
   - 另新增一段：`它在当前项目里到底算什么？`
     - 明确写死当前正式标签是 `optional filter candidate with archived status`；
     - 同时解释为什么它不是主 alpha、也不只是纯 teaching example。
2. 重建 `reports/site/factors/support_breakout_v0_fib_ab/report.html`
   - 新角色段与更完整的最终结论都已经正式进页。
3. 更新 `docs/TODO.md`
   - 将 `把 Fibonacci 线正式收成一页“结论页 / archived idea page”` 标记为完成；
   - 将 `明确它在当前项目里到底是 optional filter / teaching example / future revisit candidate` 标记为完成；
   - 并把当前固定口径直接写成结果说明。

## 验证 / 证据

### 1) 网页已出现新的角色归类段

验证命中：
- `reports/site/factors/support_breakout_v0_fib_ab/report.html` 已出现 `它在当前项目里到底算什么？`
- 页内已明确出现一句：`optional filter candidate with archived status`

这说明本轮结果已经真正落到网站可见产物，而不是只留在日志里。

### 2) 当前 Fibonacci 的项目级口径已经被写死

这轮之后，关于这条线最诚实的结论是：
- 它想解决的是“breakout 后等反抽确认再做空”的过滤问题；
- 它确实改善了过滤层的机制表达，但没有改善主线收益结果；
- 在当前 A/B 中，v0 breakout 平均单笔约 `1.44%`、累计约 `92.45%`，fib 版只有约 `0.71%`、累计约 `20.00%`，且平均入场延迟约 `12.5` 根 bar；
- 因此它当前应正式归类为：**optional filter candidate with archived status**。

### 3) 最小技术验证通过

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`

结果：
- 脚本成功执行；
- `support_breakout_v0_fib_ab/report.html` 已更新；
- 本轮无阻塞性报错。

## 风险 / 边界

1. 这轮是 **收口表达 / 角色归类**，不是新回测；
2. 因此没有新增样本、成本、OOS 或执行层证据；
3. 但它确实把 Fibonacci 这条线从“结论大致清楚”推进到了“角色标签也清楚、TODO 也正式勾掉”的状态。

## 下一步建议

Fibonacci 这条线现在可以基本退出主研发轮次。下一步更值得继续的是：
1. `EMA` 的 rolling / OOS honesty；
2. 或 `support_breakout_raw @ h24` 的成本 / 执行 / non-overlap / 环境约束验证。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然很脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_fib_ab/report.html` 这些路径本身就在未提交状态；此时做 selective commit 仍无法保证只打包本轮改动。\n