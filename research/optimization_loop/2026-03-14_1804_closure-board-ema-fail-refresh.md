# closure board 补回 EMA 60m fail / PSAR overlay 失败结果

## 为什么这次选这个

这轮没有再开新验证，而是把刚刚已经落地的两刀 EMA 真实结果，正式补回 `alpha_closure_board`。

原因很直接：
1. `EMA 60m gross vs 20bps rolling slice` 和 `EMA 60m + PSAR exit overlay` 这两刀真实结果已经在 `EMA / PSAR Raw Alpha Focus Report` 落页；
2. 但总决策页 `alpha_closure_board` 还停留在“下一步去做 rolling / overlay”的旧口径，没有同步最新结果；
3. 现在最值钱的小步，就是把总决策页刷新成与最新证据一致，这样 Jerry 不用自己跨页拼结论。

## 做了什么改动

1. 更新 `scripts/build_alpha_closure_board_report.py`
   - 把 `EMA / PSAR` 卡片从旧的“先做 rolling / overlay”改成基于最新真实结果的口径；
   - 新固定读法是：
     - `EMA 60m crypto` 这块最弱口袋已经落入 `fail`；
     - `PSAR exit overlay` 也还没有把它救回来；
     - 因此若还继续这条线，更该问“baseline family 还剩什么”，而不是继续默认 60m 会被修好。
2. 更新 `docs/TODO.md`
   - 在 `comparison / decision board` 的 latest supplement 链里补上这条 closure-board 级别的正式读法；
   - 让 `reports/site/plans/momentum_todo.html` 也同步带出这条总览结论。
3. 重建可见产物
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 关键更新内容

### 1) closure board 现在明确承认：EMA 60m crypto 是失败口袋

总决策页现在正式写入：
- `EMA 60m` 在 `BTC / ETH / SOL` 的 `45d + 15d` rolling slice 中：
  - gross 正窗口仅 `4/30`
  - `20bps` 后仅 `2/30`
  - `0/3` 资产达到“多数窗口 net 为正”

因此它不再被当成支持 baseline 的 hopeful 证据，而是被明确写成 `fail pocket`。

### 2) closure board 也同步承认：PSAR overlay 没救回来

总决策页现在同时写入：
- `PSAR exit overlay` 只在 `4/30` 个窗口里比单跑 `EMA` 更好；
- `EMA` 自己在 `20bps` 下至少还有 `2/30` 个正窗口，但 overlay 后变成 `0/30`；
- 整体 median window net20 delta 约 `-6.26pp`

所以当前项目级读法进一步收紧为：
- `PSAR` 仍可保留为 protective overlay 的研究角色；
- 但至少在最脆的 60m crypto 口袋里，它还没有交出 rescue 证据。

### 3) 总决策页的“下一步”也因此变了

刷新后，`alpha_closure_board` 对 EMA 线给出的 next step 已改成：
- 不再继续包装 `EMA 60m crypto`；
- 若还继续 `EMA / PSAR` 线，更值得补的是：
  1. `日/周频 baseline family 还剩什么`；
  2. `PSAR overlay 为什么显著抬高交易次数却没带来净改善` 的诊断页。

## 验证 / 证据

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 已出现：
  - `继续，但 60m crypto 口袋已落入 fail；若继续应更窄地问 baseline family 还剩什么`
  - `4/30`
  - `2/30`
  - `0/30`
  - `-6.26pp`
- `docs/TODO.md` 已补入同样口径；
- `reports/site/plans/momentum_todo.html` 也已同步。

## 这轮后的项目级读法

这轮之后，站点总入口与子页终于一致：
- breakout 线：仍是最值得继续做结构事件策略 follow-up 的对象；
- Fibonacci：继续归档；
- EMA / PSAR：仍可继续，但不再把 `EMA 60m crypto` 当成支持证据，而是更诚实地问“baseline family 还剩什么、PSAR 为何没救到这块”。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/alpha_closure_board/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
