# 把 v3 final verdict → breakout v0 的路径讲顺：默认 follow-up 先试 avoid_fluctuating，不是 only_downtrend

## 为什么这次选这个

这轮我没有继续做新的回测切片，也没有回到外部文献池。

原因是当前提醒已经把短期主任务收紧成三条收口线，而 `pytrendline_event_validation_v3` 也明确要求“只作为历史证据包引用，不再继续延伸”。在这种前提下，最值钱的一小步不再是加一层新分析，而是把**已经得到的结论真正落到网页入口和策略原型页**，让后续阅读顺序和研发动作更清楚。

这轮最值得复用/借鉴的点是：**如果一个研究线已经收工，下一步最重要的不是再补一个新 slice，而是把“研究结论 → 候选策略原型”的继承关系讲顺，并把真正可执行的 follow-up 口径写到人会先看到的页面上。**

## 核心结论（中文摘要）

核心结论：**当前 `support_breakout_v0` 这条 breakout-short follow-up 线，默认最值得继续验证的环境约束应写成 `avoid_fluctuating`，而不是 `only_downtrend`；并且这个结论应该直接体现在 `support_breakout_v0_h24` 页与 `alpha_closure_board` 上，而不只躺在研究日志里。**

证据如何支持这个结论：**上一轮已经完成了最小 policy 对照：在 OOS 段，`trade_all` 的 `avg_excess_ret_h24` 约 `-1.55%`，`avoid_fluctuating` 提升到约 `-1.88%` 且仍保留约 `84%` 样本，而 `only_downtrend` 虽也为负（约 `-1.73%`）但只剩约 `37%` 样本，性价比明显不如 `avoid_fluctuating`。因此网页上继续写“更适合 down / flat”已经不够，应该明确升级成“若要加 first-pass gate，优先试 `avoid_fluctuating`”。**

## 本轮做了什么改动

本轮只做一个主点：**把 v3 收工结论与 breakout v0 follow-up 的页面路径讲顺，并把 `avoid_fluctuating` 明确写成当前更可执行的 first-pass 口径。**

具体动作：

1. 更新 `docs/TODO.md`
   - 把 `C0-C1` 下的这一条勾掉：
     - `把 v3 final verdict 与 support_breakout_v0_h24 串成更清楚的“研究结论 -> 候选策略原型”路径`
   - 并补一句说明：
     - `v3 final verdict` 负责回答“留下了什么”；
     - `support_breakout_v0_h24` 负责回答“把留下来的 breakout-short 候选压成最小策略原型后长什么样”；
     - 当前更可执行的 follow-up 口径是 `avoid_fluctuating`，不是 `only_downtrend`。

2. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 在 v0 页 hero note 里直接补上：
     - 这是 `v3 final verdict` 的后继原型页；
     - 前者回答“留下了什么”，后者回答“压成策略原型后长什么样”。
   - 在“收口定位”区补入：
     - 若要加 first-pass 环境约束，当前更像样的是 `avoid_fluctuating`；
     - 不应机械地默认 `only_downtrend`。
   - 同时把这条线的产品定位收紧为：
     - `条件性 alpha / strategy-facing breakout-short 原型`
   - 并把下一步动作写得更像实现层：
     - 成本、rolling OOS、non-overlap / capital allocation、环境约束验证。

3. 更新 `scripts/build_alpha_closure_board_report.py`
   - 在 breakout-short follow-up 那张卡的“当前最强证据”里补入：
     - `avoid_fluctuating` 比 `only_downtrend` 更像样。
   - 在“下一步最值得做什么”里也明确写死：
     - 环境约束的 first-pass 默认口径优先试 `avoid_fluctuating`，不是 `only_downtrend`。

4. 重建并发布页面
   - 重新生成：
     - `reports/site/factors/support_breakout_v0_h24/report.html`
     - `reports/site/factors/support_breakout_v0_fib_ab/report.html`
     - `reports/site/factors/alpha_closure_board/report.html`
     - `reports/site/plans/momentum_todo.html`
   - 同步到站点镜像。

## 验证 / 证据

### 1) 页面落地验证
重建后页面中已能直接检索到：
- `support_breakout_v0_h24/report.html`
  - `这页是 v3 final verdict 的后继原型页`
  - `avoid_fluctuating`
  - `only_downtrend`
- `alpha_closure_board/report.html`
  - `avoid_fluctuating`
  - `only_downtrend`
- `plans/momentum_todo.html`
  - 已写入对应 TODO 勾选与补充说明

### 2) 为什么这步现在比继续补新 slice 更值钱

因为当前短期目标已经切成三条收口线，而且系统明确要求：
- `v3` 已正式收工；
- 后续只把它当历史证据包引用；
- 当前更重要的是帮助 Jerry 判断：
  - 这条线到底该不该继续往策略/实盘推进；
  - 如果继续，下一步先补什么。

在这种阶段，**把正确的 next-step 口径写到默认入口页上**，比再多跑一刀小样本更直接有用。

## 风险 / 边界

- 这轮没有新增策略证据，也没有新增回测结果；
- 它完成的是“表达与路径收口”，不是“数值层新增发现”；
- 但这一步对后续决策很重要：避免继续沿着 `only_downtrend` 这种已经被 first-pass 否掉的直觉写页面和排任务。

## 下一步建议

如果下一轮继续沿三条收口线推进，更合理的候选是：

1. `support_breakout_v0 / breakout-short follow-up`
   - 补最小成本 / non-overlap / capital allocation honesty
   - 或把 `avoid_fluctuating` 真正带入 v0 原型回测做一刀 A/B

2. `EMA / PSAR raw alpha focus`
   - 补 `PSAR` 的角色判断
   - 或做 `EMA + PSAR` 最小组合页

3. `Fibonacci confirmation / retest_hold`
   - 只做 archived/filter 结论页表达补强，不再回到主 alpha 推进

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成页面口径、TODO、日志与邮件同步，不做提交。