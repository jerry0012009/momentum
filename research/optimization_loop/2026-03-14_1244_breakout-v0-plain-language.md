# breakout v0 页补齐 plain-language 定位

## 为什么这次选这个

这轮没有继续开新验证，而是沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线，补当前最缺的一块：**把 `support_breakout_raw / confirm_1 @ h24` 到底该读成什么，用 plain-language 讲死**。

原因很直接：
1. `docs/TODO.md` 里这条任务还没勾掉；
2. 当前 `support_breakout_v0_h24` 页虽然已经讲了 raw v0 原型，但还没有把 `raw / confirm_1 / feature-watch` 三者的边界一次讲透；
3. 这是一个很小、但会直接减少误读的 closure 动作，而且能落实到网页可见产物。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 在 `support_breakout_v0_h24` 页新增一整段：`plain-language：raw / confirm_1 / feature-watch 到底怎么区分？`
   - 固定写清三层口径：
     - `support_breakout_raw @ h24` = **可交易原型 / 条件性 alpha**
     - `support_breakout_confirm_1 @ h24` = **co-primary confirmation variant**
     - 真正更像 `feature/watchlist` 的仍是 `support_rebound_confirm_1` 这类对象
   - 同时补一句更可执行的产品判断：如果今天只能保留一个 strategy-facing 原型页，先保留 `raw`；如果要留一个紧邻确认变体做 next-step honesty check，留 `confirm_1`，但不要把它立刻扩成第二条大而全独立策略线。
2. 重建 `reports/site/factors/support_breakout_v0_h24/report.html`
   - 新解释段已经正式进页，可直接在网站上看见。
3. 更新 `docs/TODO.md`
   - 将 `用 plain-language 补清：support_breakout_raw / confirm_1 @ h24 ...` 这条标记为完成；
   - 并把当前固定口径写成结果说明，避免以后又被读回“只是 feature/watch”。

## 验证 / 证据

### 1) 网页已出现新的 plain-language 段

`reports/site/factors/support_breakout_v0_h24/report.html` 现在已正式出现：
- `plain-language：raw / confirm_1 / feature-watch 到底怎么区分？`

这说明本轮结果已经落实到 closure 网页，不只是停留在日志里。

### 2) 当前项目级读法被收得更清楚

这轮之后，关于 breakout-short follow-up 的口径更稳定：
- `raw` 不是“先观察一下”的 feature，而是现在就值得保留的 **v0 原型**；
- `confirm_1` 也不是 watchlist，而是 **co-primary confirmation variant**；
- 真正更像 `feature/watch` 的仍是 `support_rebound_confirm_1` 这种对象。

### 3) 最小技术验证通过

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`

结果：
- 成功重建 `support_breakout_v0_h24/report.html`；
- 本地脚本无报错。

## 风险 / 边界

1. 这轮是 **解释与定位收口**，不是新回测；
2. 因此它没有新增成本/OOS/执行层证据，只是把现有研究结论讲得更不容易误读；
3. `confirm_1` 当前被保留为主候选之一，不代表现在就应该把它扩成第二条完整策略线；当前更合理的顺序仍是：先继续沿 `raw v0` 做成本 / rolling OOS / non-overlap / 环境约束验证。

## 下一步建议

下一步若继续沿 breakout-short 这条线推进，最值得做的是：
1. `support_breakout_raw @ h24` 的成本 / 执行 / rolling OOS honesty；
2. 或最小地把 `confirm_1` 放进同一套 honesty 对照，而不是另起炉灶做大而全第二条策略页。

## Commit

本轮**未提交**。

原因：当前 repo worktree 很脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html` 这些路径本身就在未提交状态；此时做 selective commit 仍不够干净，容易把前序改动一并带上。
