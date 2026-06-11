# 2026-03-14 12:18 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的不是再改研究优先级，而是**把 bot2 / bot3 的职责边界彻底讲清楚并写进文档**：`bot2` 负责思考与维护 `TODO`、校准 cron 与路径；`bot3` 负责从 `TODO` 里认领一个具体项目任务并完成。`TODO.md` 默认应只放项目本身该做的事，不应再让 bot3 把“检查 bot3 有没有运行、维护 bot3 自己”当成高优先级项目任务。

## 当前 strongest evidence

1. **Jerry 的反馈已经明确指出了 bot3 之前的元循环 bug**
   - bot3 会去检查 bot3 自己是否在运行；
   - 然后得出“我确实在运行”；
   - 再给出进一步修改 bot3 提醒词的建议；
   - 这说明之前的职责边界确实不够清晰。

2. **当前主研究优先级本身没有变化**
   - `EMA / PSAR raw alpha focus`
   - `support_breakout_v0 / breakout-short follow-up`
   - `Fibonacci confirmation / retest_hold`
   - 这些仍是 closure-first 的核心线。

3. **真正需要修的是治理分工，不是研究路线**
   - `bot2` 应负责：
     - 维护 TODO 结构
     - 判断优先级
     - 调 cron / prompt / 站点入口
   - `bot3` 应负责：
     - 从 TODO 中认领项目任务
     - 完成一个真实小步
     - 留下产物

## 当前 weakest / should-fix-now

1. **TODO 曾经隐含承接了部分 bot3 自我维护语义**
   - 这会诱导 bot3 把“维护自己”当成项目任务。

2. **bot2 / bot3 职责边界此前没有在文档中写死**
   - 所以即使运行态 prompt 调整了，后续仍可能被旧文档重新污染。

## 建议优先级 Top 1~3

### Top 1. 观察 bot3 在新职责边界下是否开始稳定执行“项目任务”
- 关注它后续是否真从 TODO 中认领：
  - EMA 成本/OOS honesty
  - breakout-v0 × avoid_fluctuating A/B
  - Fibonacci 最终定位页
- 而不是再碰 bot3 自身治理。

### Top 2. EMA baseline 的成本 / OOS honesty
- 这仍是当前最值得继续推进的项目任务。

### Top 3. breakout-v0 × avoid_fluctuating 的最小 A/B
- 这仍是 breakout-short follow-up 最自然的一刀。

## 本轮改动

### 已改

1. **微调 `docs/BOT2_STRATEGY_REVIEW_BRIEF.md`**
   - 明确写入：
     - `bot2` 负责思考 / 维护 / 校准 `TODO`
     - `TODO.md` 默认应只放项目任务
     - `bot3` 负责从 TODO 中认领项目任务并完成
     - 不应把“维护 bot3 自己 / 检查 bot3 是否在运行”当成项目主任务

2. **微调 `docs/TODO.md` 顶部维护规则**
   - 明确写入：
     - `TODO.md` 默认只放项目本身该做的事情
     - bot3 自身运行治理属于 `bot2` / cron 维护职责
     - 除非用户明确要求，否则不应反复占据 bot3 的执行槽位

3. **重建并同步 `plans/` 站点镜像**
   - 避免网页还显示旧口径。

### 本轮未改

- 不改三条收口线的优先级排序
- 不改 bot2 频率
- 不改 bot7 方向

原因：
- 这轮问题已经非常集中，就是职责边界；
- 研究优先级本身并没有被推翻。

## 网页/表达建议

1. `plans/momentum_todo.html` 现在应更适合作为对外统一口径：
   - TODO 是项目任务清单，
   - 不是 bot3 自我维护清单。

2. 后续如果 bot3 仍出现元循环迹象，可以考虑在 closure board 增加一句治理边界提示，但这轮先不加。

## cron / 节奏建议

1. **bot3-auto-opt-20m：保持**
   - 频率已经从 15m 调到 20m；
   - 现在先看新职责边界是否能消除元循环。

2. **bot2-strategy-review-40m：保持**
   - 当前 bot2 的价值正是负责这类 TODO / 治理校准，而不是抢 bot3 的执行工作。

3. **bot7-quant-digest-4h：保持**
   - 这轮不动它。

## 风险与不确定性

1. 即使职责边界已经写清，bot3 仍可能因 worktree 脏、任务粒度不合适而短期内出现 `NO_PROGRESS`；但这和“元循环误领 bot3 自己”已经是两个问题。
2. 真正的验证标准不是文档写得更清楚，而是后续 bot3 是否开始稳定地产出项目任务成果。
3. 当前主研究结论没有变化；本轮修的是治理边界，不是研究结论。
