# closure board 补齐资源顺序与 fallback 决策

## 为什么这次选这个

这轮没有再去开新验证，而是把 `docs/TODO.md` 里还没彻底收口的一项补完：**给三条收口线的 comparison / decision board 补上真正可执行的资源顺序与 fallback 路径。**

原因是：
1. `alpha_closure_board` 虽然已经能并排讲三条线，但之前还差最后一层“如果今天只能继续投 1~2 个资源位，该怎么排；如果三条线都不够强，又该回到哪类新 alpha 搜索”；
2. 这正好对应 TODO 里那条还没勾掉的 `comparison / decision board`；
3. 在 13 分钟节奏下，这是一个很小、但很像最终决策页的收口动作，而且能直接落到网页可见产物。

## 做了什么改动

1. 更新 `scripts/build_alpha_closure_board_report.py`
   - 给三条线都补上了明确的 `资源顺序` 标签：
     - `EMA / PSAR = #1`
     - `breakout-short follow-up = #2`
     - `Fibonacci = archive`
   - 在并排卡片和总表中都把资源顺序显式写出来，不再只靠读者自己从文字里猜；
   - 新增一张 fallback 卡片：`如果这三条线都没过 gate，下一轮该回到哪里找新 alpha？`
     - 明确写死：若三条线在 rolling / OOS / cost 后都明显转弱，下一轮应优先回到 `structure-event confirmation / retest / filter / raw baseline` 相关的 E-track，而不是泛泛扩候选池。
2. 更新 `docs/TODO.md`
   - 将 `为这 3 条线补一个更上位的 comparison / decision board` 正式标记为完成；
   - 并把当前固定口径补成结果说明，避免后续又回到“有 board 但还没真正回答 fallback”的半完成状态。
3. 重建可见产物：
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) 网页现在明确给出资源顺序

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 已出现：
  - `资源顺序：#1 · EMA = 主 raw alpha baseline 候选...`
  - `资源顺序：#2 · 当前最值得继续往结构事件策略层推进的候选`
  - `资源顺序：archive · 当前不再当主 alpha 推进...`

这说明 comparison board 已从“并排说明页”升级成了真正的决策顺序页。

### 2) fallback 路径也已经正式写回网页

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 已出现：
  - `如果这三条线都没过 gate，下一轮该回到哪里找新 alpha？`

当前固定口径是：
- 若三条线在 `rolling / OOS / cost` 后都明显转弱；
- 下一轮应优先回到 `structure-event confirmation / retest / filter / raw baseline` 相关的 E-track；
- 不应退回到泛泛 digest 式扩候选池。

### 3) TODO 与 plans 镜像已同步

验证命中：
- `docs/TODO.md` 中该条已改为 `[x]`
- `reports/site/plans/momentum_todo.html` 中对应条目也已同步为完成状态

这意味着 closure board 相关主入口 / 决策层任务现在可以诚实视为收口完成。

## 风险 / 边界

1. 这轮是 **决策层网页收口**，不是新回测；
2. 没有新增收益、成本或 OOS 数字；
3. 但它确实把“谁先做、谁归档、如果都不行回哪里继续找 alpha”这三件事写成了网站可见的明确结论。

## 下一步建议

下一步最值得接的还是两件更实质的验证：
1. `EMA` 的真正 rolling / OOS 页；
2. `support_breakout_raw @ h24` 的成本 / non-overlap / 执行层 honesty。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/alpha_closure_board/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
