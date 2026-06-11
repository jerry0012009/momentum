# closure board 同步 confirm_1 hourly portfolio path 结果

## 为什么这次选这个

这轮没有再开新验证，而是把刚刚已经落地的 `confirm_1 hourly portfolio path` 真实结果，正式补回 `alpha_closure_board`。

原因很直接：
1. breakout 线最近已经把 `raw` 与 `confirm_1` 都推进到更正式的 `hourly mark-to-market` 统一资金曲线口径；
2. 但总决策页还停留在“下一步再把 confirm_1 放进 hourly path 复核”的旧口径，已经落后于最新结果；
3. 现在最值钱的小步，就是把站点总入口刷新到和最新 breakout 证据一致，让 Jerry 不用自己跨页拼结论。

## 做了什么改动

1. 更新 `scripts/build_alpha_closure_board_report.py`
   - 刷新 breakout 卡的 `当前最强证据`：
     - raw 现在明确写成 `75.03% / 19.40% / 14.04% / 13.83%`
     - `confirm_1` 现在明确写成 `59.38% / 12.04% / 11.54% / 5.06%`
     - 其中第三项就是更正式的 `hourly portfolio path`；
     - 同时补入 `confirm_1` 的 hourly path max drawdown 约 `-13.60%`，略差于 raw 的约 `-12.03%`。
   - 刷新 breakout 卡的 `当前不能过度解读什么`：
     - 不再说“还没把 confirm_1 放进更正式组合路径”，因为这件事已经做完；
     - 改成更真实的缺口：还缺更正式的 sizing policy、rolling OOS honesty，以及把最像样的环境 gate 真正放进统一资金曲线后的复核。
   - 刷新 breakout 卡的 `下一步最值得做什么`：
     - 不再继续纠结 `confirm_1` 会不会抢主线位；
     - 当前更值得做的是继续把 raw 当主原型，并把 `avoid_fluctuating` 放进同一套 `hourly portfolio path / sizing honesty` 里复核。
2. 更新 `docs/TODO.md`
   - 在 `comparison / decision board` 的 latest supplement 链里补上 closure-board 级别的正式读法；
   - 让 `reports/site/plans/momentum_todo.html` 也同步带出这条更新后的总览结论。
3. 重建可见产物
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 核心结果

### 1) closure board 现在明确承认：confirm_1 在更现实口径下也没反超 raw

总决策页当前正式写入：
- raw：
  - `20bps per-asset` 约 `75.03%`
  - `equal-weight concurrent(entry)` 约 `19.40%`
  - `hourly portfolio path` 约 `14.04%`
  - `1-slot global` 约 `13.83%`
- `confirm_1`：
  - `20bps per-asset` 约 `59.38%`
  - `equal-weight concurrent(entry)` 约 `12.04%`
  - `hourly portfolio path` 约 `11.54%`
  - `1-slot global` 约 `5.06%`

而且在更正式的 hourly path 下：
- raw max drawdown 约 `-12.03%`
- `confirm_1` max drawdown 约 `-13.60%`

这说明：随着执行口径越来越诚实，`confirm_1` 也没有出现“越现实越强”的翻盘迹象。

### 2) breakout 线的 next step 因此真正收紧了

这轮之后，closure board 对 breakout 线给出的 next step 已改成：
- 不再继续把资源花在 `confirm_1` 会不会抢主线位上；
- 更值得做的是继续把 raw 当 breakout-short 主原型；
- 若再做一个真实 follow-up，优先把 `avoid_fluctuating` 放进同一套 `hourly portfolio path / sizing honesty`，看它是否比“换成 confirm_1”更能改善执行层结果。

## 验证 / 证据

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 已出现：
  - `confirm_1 对应约 59.38% / 12.04% / 11.54% / 5.06%`
  - `hourly path 的 max drawdown 约 -13.60%`
  - `既然 confirm_1 在更正式 hourly portfolio path 下也没反超 raw`
  - `把 avoid_fluctuating 放进同一套 hourly portfolio path / sizing honesty`
- `docs/TODO.md` 已补入同样口径；
- `reports/site/plans/momentum_todo.html` 也已同步。

## 这轮后的项目级读法

这轮之后，站点总入口与 breakout 子页终于进一步对齐：
- breakout 线仍是 `#2`、值得继续；
- 但继续的对象和顺序现在更清楚：`raw` 继续当主原型，`confirm_1` 不再被当作“也许会在更现实口径下反超”的悬而未决问题；
- 如果要再做一个更接近策略层的小验证，优先应该去检验 `avoid_fluctuating` 在统一资金曲线下到底能不能带来真正改善。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/alpha_closure_board/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
