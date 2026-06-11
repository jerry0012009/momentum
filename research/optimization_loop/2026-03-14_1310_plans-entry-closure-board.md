# 把三条收口线正式挂进 Plans 入口页

## 为什么这次选这个

这轮没有继续开新验证，而是补当前 closure-first 流程里一个还没完全收口的小缺口：**让 `plans/index.html` 也把三条收口线作为固定入口挂出来，而且把 `Current Alpha Closure Board` 放到最前面。**

原因很直接：
1. `docs/TODO.md` 里“在网页主入口或主线页中把这 3 条线挂成当前收口中的候选”这条还没勾掉；
2. 站点首页虽然已经强调 closure-first，但 `Plans / Roadmaps` 页还是更像规划目录，缺一个真正的“先看总入口、再分流三条线”的清晰入口；
3. 这是一刀很小、但对 Jerry 实际看站点路径非常有帮助的网页入口收口动作。

## 做了什么改动

1. 更新 `scripts/build_plans_site.py`
   - 在 `current alpha entry board` 里新增：`Current Alpha Closure Board`；
   - 并把它放到所有入口的第一位，标签固定为 `当前收口总入口`；
   - 当前入口顺序变成：
     1. `Current Alpha Closure Board`
     2. `Mainline`
     3. `PyTrendline v3 Final Verdict`
     4. `support_breakout v0`
     5. `Fib A/B honesty`
     6. `EMA / PSAR Raw Alpha`
2. 重建：
   - `reports/site/plans/index.html`
   - `reports/site/plans/report.html`
3. 更新 `docs/TODO.md`
   - 将 `在网页主入口或主线页中把这 3 条线挂成“当前收口中的候选”` 这条标记为完成；
   - 并把当前固定读法写成结果说明：站点首页与 plans 页都已按 `closure-first` 挂出固定入口，不再需要 Jerry 自己在一堆中间页里找主结论。

## 验证 / 证据

### 1) Plans 入口页已出现新的总入口卡片

验证命中：
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

两页现在都已出现：
- `Current Alpha Closure Board`
- 标签：`当前收口总入口`

### 2) TODO 这条入口任务已能诚实勾掉

当前项目的入口组织已经形成闭环：
- `reports/site/index.html`：首页先按 closure-first 展示推荐入口；
- `reports/site/plans/index.html`：plans 入口页也先给 closure board，再分流到 breakout / fib / EMA-PSAR；
- `reports/site/factors/alpha_closure_board/report.html`：负责并排讲三条收口线。

因此这条任务现在可以诚实视为完成，而不是“首页提过一次但 plans 入口仍然不顺”。

### 3) 最小技术验证通过

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

结果：
- 成功重建 `reports/site/plans/`；
- 本轮无阻塞性报错。

## 风险 / 边界

1. 这轮是 **网页主入口收口**，不是新研究验证；
2. 它不会改变 breakout / fib / EMA-PSAR 的实证结论，只是让当前主结论更容易被看见；
3. 这也意味着下一轮仍应回到更实质的 follow-up（例如 EMA rolling/OOS，或 breakout v0 的成本/执行层验证）。

## 下一步建议

现在入口层已经够顺了，下一步更值得补的是：
1. `EMA` 的 rolling / OOS honesty；
2. 或 `support_breakout_raw @ h24` 的成本 / non-overlap / 执行层 honesty。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然很脏，而且 `docs/TODO.md`、`reports/site/plans/index.html`、`reports/site/plans/report.html` 本身就在未提交状态；此时做 selective commit 无法保证只打包本轮改动。