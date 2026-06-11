# breakout v0 后续验证边界正式写进原型页

## 为什么这次选这个

这轮继续沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线推进，但不做新回测，而是把一个还没完全写死的边界收口掉：**如果这条线继续做 follow-up，到底允许做什么，不允许做什么。**

之所以选这个点：
1. `docs/TODO.md` 里这条任务还没勾掉；
2. 当前 repo 已经有很多在途改动，再开新验证更容易撞到别的脏改动；
3. 这是一个足够小、但能直接提升网页可读性和后续执行纪律的收口动作，符合 13 分钟节奏。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 在 `support_breakout_v0_h24` 页新增一段：`如果继续做 follow-up，允许做什么，不允许做什么？`
   - 明确写死：
     - **允许**：`cost / slippage sensitivity`、`rolling / OOS`、`non-overlap / capital allocation`、以及更窄的环境约束验证（当前优先看 `avoid_fluctuating`）；
     - **也允许**：把 `support_breakout_confirm_1` 作为紧邻确认变体，一起放进同样的 honesty / execution 框架里比较；
     - **不允许**：重新回到 `v3` 式大全参数搜索、泛跨市场大工程、或重新开一轮 breakout 变体排位赛。
2. 重建：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/plans/momentum_todo.html`
3. 更新 `docs/TODO.md`
   - 将 `若继续验证，只允许做更窄的 follow-up...` 这条标记为完成；
   - 并把当前固定口径写成结果说明，避免后面又把 breakout v0 带回发散模式。

## 验证 / 证据

### 1) 网页已出现新的 follow-up 边界段

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现 `如果继续做 follow-up，允许做什么，不允许做什么？`

这说明本轮结果已经真的落到网站，而不是只停留在日志里。

### 2) TODO 与 plans 镜像已同步

验证命中：
- `docs/TODO.md` 中该条任务已改为 `[x]`
- `reports/site/plans/momentum_todo.html` 中对应条目也已同步为完成状态

### 3) 当前项目级口径更收紧了

这轮之后，关于 breakout v0 的后续默认动作更明确：
- 下一步应该优先做更接近策略层的 honesty / execution follow-up；
- 当前最合理的候选问题是 `cost / rolling OOS / non-overlap-capital-allocation / avoid_fluctuating`；
- 不再回到 `v3` 式大全参数扩张，也不再重开 breakout 家族重新排位。

## 风险 / 边界

1. 这轮是 **收口边界 / 执行纪律** 的网页化，不是新回测；
2. 因此没有新增收益、成本或 OOS 数据；
3. 但它确实把 breakout v0 从“知道该继续什么”推进到了“也知道不该再做什么”。

## 下一步建议

下一步最值得接的仍是：
1. `support_breakout_raw @ h24` 的成本 / slippage sensitivity；
2. 或把 `support_breakout_confirm_1` 一起纳入同一套更窄的 honesty / execution 对照。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然很脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 这些路径在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。