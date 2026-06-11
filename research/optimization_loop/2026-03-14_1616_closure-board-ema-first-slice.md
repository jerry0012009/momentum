# closure board 把 EMA 的 first falsification slice 写死

## 为什么这次选这个

这轮不再开新验证，而是把最近刚补进 `EMA / PSAR Raw Alpha Focus Report` 的一个关键信号，正式回挂到最上层的 `alpha_closure_board`：**如果下一步只先做一个最小 rolling / OOS 切片，默认先做哪一块。**

之所以选这个点：
1. `alpha_closure_board` 是现在 Jerry 最容易先看的总入口；
2. EMA 页里虽然已经写清“先做 `EMA 60m gross vs 20bps` falsification slice”，但顶层决策页还没同步这个更具体的 next-step；
3. 这是一个很小、但能直接提升后续执行清晰度的网页收口动作，符合 13 分钟节奏。

## 做了什么改动

1. 更新 `scripts/build_alpha_closure_board_report.py`
   - 把 `EMA / PSAR raw alpha focus` 卡片里的“下一步最值得做什么”改成更具体版本；
   - 不再只写泛泛的 `rolling / OOS honesty`，而是明确写死：
     - 第一刀默认先做 `EMA 60m gross vs 20bps` 的 `rolling / walk-forward falsification slice`；
     - 原因是这块最脆，最适合先检验 baseline 幻觉会不会塌。
2. 重建可见产物：
   - `reports/site/factors/alpha_closure_board/report.html`

## 验证 / 证据

### 1) closure board 已出现更具体的 EMA 下一步

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 已出现：
  - `EMA 60m gross vs 20bps`
  - `rolling / walk-forward falsification slice`

这说明顶层决策页现在不只是在说“继续验证”，而是在说“先从哪一刀开始验证”。

### 2) 当前顶层读法更可执行了

这轮之后，关于 EMA 线的总览口径更明确：
- `EMA / PSAR` 仍是当前 `#1` 资源位；
- 但下一步不是泛泛地“补 rolling / OOS”；
- 而是优先拿最脆的 `EMA 60m` 做 `gross vs 20bps` 的最小 falsification slice，先看 baseline 幻觉会不会被打掉。

这比只说“以后记得补 OOS”更像真正可执行的任务分解。

## 风险 / 边界

1. 这轮是 **顶层决策页刷新**，不是新 rolling 回测；
2. 没有新增窗口统计或净值曲线；
3. 但它确实把 EMA 线下一步该从哪里先下刀，写成了网站可见的明确结论。

## 下一步建议

下一步最值得接的就是：
1. 真做一版 `EMA 60m gross vs 20bps` 的 rolling / walk-forward 小切片；
2. 优先报告窗口正收益占比、坏窗口是否扎堆、以及 `gross -> 20bps` 后的窗口存活比例。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `scripts/build_alpha_closure_board_report.py` 与 `reports/site/factors/alpha_closure_board/report.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
