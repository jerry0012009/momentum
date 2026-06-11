# EMA / PSAR 收口 TODO 去陈旧化

## 为什么这次选这个

这轮没有再开新验证，而是优先处理一个已经开始影响判断顺序的小问题：`docs/TODO.md` 里有几条 **其实已经被网页与总览页写死、但状态仍停留在未完成** 的 EMA / PSAR 收口任务。

之所以选这个点：
1. 当前自动循环已经连续把 `EMA / PSAR` 这条线推进到“策略决策页 + closure board + first falsification slice”阶段；
2. 但 TODO 里还残留若干旧的 `[ ]`，会让人误以为这些基础口径还没收口；
3. 这是一个很小、但对后续排优先级很有帮助的收口动作，而且能直接落到网站可见的 `plans/momentum_todo.html`。

## 做了什么改动

1. 更新 `docs/TODO.md`
   - 将以下 4 条已实质完成的 EMA / PSAR 收口任务改为 `[x]`：
     - `把 EMA 正式作为当前项目的 raw alpha baseline 候选挂入主线比较口径`
     - `把 PSAR 正式作为第二原始 alpha 候选挂入研究队列`
     - `对 PSAR 做角色审计`
     - `为 V3 / Fibonacci / EMA-PSAR 各自补一版 closure-style report framing`
   - 同时为每条补上结果说明，明确对应证据已经落在哪些网页：
     - `EMA / PSAR Raw Alpha Focus Report`
     - `alpha_closure_board`
     - `support_breakout_v0_h24`
     - `support_breakout_v0_fib_ab`
2. 重建可见产物
   - 执行 `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`
   - 让 `reports/site/plans/momentum_todo.html` 与最新 TODO 状态同步

## 验证 / 证据

### 1) 这 4 条旧任务现在已被诚实勾掉

验证后，`docs/TODO.md` 中已明确出现：
- `[x] 把 EMA 正式作为当前项目的 raw alpha baseline 候选挂入主线比较口径`
- `[x] 把 PSAR 正式作为第二原始 alpha 候选挂入研究队列`
- `[x] 对 PSAR 做角色审计`
- `[x] 为 V3 / Fibonacci / EMA-PSAR 各自补一版 closure-style report framing`

### 2) 这些勾掉不是“空打勾”，都有现成网页证据

当前网页侧已经明确支持这些结论：
- `EMA / PSAR Raw Alpha Focus Report` 已写死：`EMA = raw alpha baseline candidate`，`PSAR = fast reaction / loss-protection candidate`
- `support_breakout_v0_fib_ab` 已写死：`optional filter candidate with archived status`
- `support_breakout_v0_h24` 已把 breakout v0 收成 `conditional alpha / strategy-facing prototype`

也就是说，这轮做的是 **把已完成的网页收口结果，回填到 TODO 状态层**，避免排期板继续滞后于实际结论。

### 3) 网站可见产物已同步

验证命中：
- `reports/site/plans/momentum_todo.html` 已同步出现上述 `[x]` 状态与结果说明

这说明本轮不是只改本地 TODO，而是确实把结果推到了站点可见的 plans 页面。

## 风险 / 边界

1. 这轮是 **TODO / plans 状态收口**，不是新回测；
2. 没有新增收益、成本或 OOS 数据；
3. 但它减少了一个很实际的误导：后续再看 TODO 时，不会再把已经完成的基础定位当成未完成工作。

## 下一步建议

下一步最值得继续的仍然是实质验证，而不是继续修文案：
1. `EMA 60m gross vs 20bps` 的 rolling / walk-forward falsification slice；
2. 或 `EMA + PSAR` 最小组合研究。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
