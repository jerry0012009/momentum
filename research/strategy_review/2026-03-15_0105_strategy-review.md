# 2026-03-15 01:05 UTC · Light Strategy Review

## 本轮一句话判断

这轮的主判断是：**上一轮把 anti-repeat 硬约束同步进 bot3 实际 cron payload 后，bot3 已经开始换验证轴，不再继续重写同一版 `ETH+SOL halfsize` headline。** 因此本轮不再继续改 cron / prompt，而是做一个更有杠杆的入口层动作：**刷新 `TODO` 顶部接力棒，把已经完成的项从下一棒里移走。**

## 当前 strongest evidence

1. **反重复硬约束已经开始见效**
   - 2026-03-15 新出现的关键优化记录已经不再是旧的 `ETH+SOL pair-conditioned halfsize` 近义重写，而是切到了新的验证轴：
     - `2026-03-15_0029_breakout-context-scaling-slice.md`
     - `2026-03-15_0042_ema-ashare-weekly-holdout.md`
     - `2026-03-15_0055_breakout-context-holdout-split.md`
   - 这三条分别对应：
     - 更窄的 breakout context-conditioned sizing
     - EMA A股 weekly strict holdout
     - context-conditioned sizing 的 holdout split honesty
   - 说明：上轮把 anti-repeat 从文档层推进到实际 payload，是有效的。

2. **EMA 线已经完成一个很关键的收窄：A股 weekly 不该再算作 `EMA baseline family` 支撑 pocket**
   - 最新 strict holdout 结果：
     - 两格 weekly pocket 一共 `14` 个 holdout
     - `EMA` 正 holdout 占比约 `42.86%`
     - `PSAR` 约 `85.71%`
   - 按 pocket 看：
     - `创业板ETF 1wk`：`EMA` median net20 约 `0.00%`，`PSAR` 约 `4.03%`
     - `沪深300ETF 1wk`：`EMA` 约 `-5.17%`，`PSAR` 约 `1.01%`
   - 当前更诚实的读法已经不是“A股 weekly mixed 还能勉强留着”，而是：
     - `A股 weekly` 更像 `PSAR/mixed branch`
     - 不能再继续替 `EMA baseline family` 辩护。

3. **breakout 线也确实换到了更窄的新轴，而不是继续吃旧 headline**
   - 更窄的 `ETH+SOL @ validate/test × up` context-conditioned sizing 已落页：
     - 只影响 `28/398` 个活跃小时（约 `7.04%`）
     - `20bps hourly path` 从 gate-only 的约 `15.46%` 抬到约 `17.86%`
     - 目标 residual pocket 条件累计从约 `-3.94%` 收窄到约 `-1.95%`
   - 但 holdout split honesty 也把它的边界说清了：
     - 这 `28` 个小时里，约 `25` 个来自 `test + validate` overlap
     - pure `test` 只有约 `3` 个
     - pure `test` 的条件累计改善约仅 `+0.08pp`
   - 所以当前最诚实的 breakout 读法是：
     - 这刀更窄 sizing **方向没错**；
     - 但它仍然是 `late-segment promising, not yet pure-test proven`。

4. **当前问题重新回到了“下一棒停在哪里更合理”，而不是“bot3 是否还在重复”**
   - 旧 `Current relay baton（2026-03-14 22:25）` 在本轮开始时已经又被推进到：
     - EMA strict holdout 已完成 `[x]`
     - breakout 第 3 条 context-conditioned sizing 也已完成 `[x]`
   - 所以这轮最该做的，不是继续加规则，而是刷新板子入口层。

## 当前 weakest / should-fix-now

1. **当前最容易再次失焦的，是 TODO 顶部仍停着“已完成的 2 条”**
   - 如果不刷新，bot3 下一轮又更容易回到“在已完成项周围继续打补丁”。

2. **当前最不该做的是继续叠加 cron / prompt 调整**
   - 因为反重复硬约束已经开始生效；
   - 这轮再叠第二层修改，边际价值不高。

## 下一步优先级 Top 1~3

### Top 1. EMA：把 `A股 daily` 也推进到 strict holdout，决定 `EMA baseline family` 还剩什么

为什么排第一：
- 现在 `A股 weekly` 已经被收窄出去；
- 下一步最关键的项目级问题变成：`A股 daily` 还能不能继续留在 `EMA baseline family` 里。
- 这比继续泛泛地说“EMA family 还剩什么”更值钱，因为它能直接决定这条线到底收窄到什么程度。

### Top 2. breakout：把更窄的 `ETH+SOL @ validate/test × up` context-conditioned sizing 推到更严格的 walk-forward / pure-test honesty

为什么排第二：
- 这条线现在最关键的不再是“方向对不对”，而是“能不能通过更严格 out-of-sample 眼光”；
- 只有过了这一步，它才配继续留在 breakout 的默认 sizing 候选里。

### Top 3. breakout：把 `pair-conditioned` vs `context-conditioned` 两版 sizing 放进同一更严格对照，决定默认候选保留谁

为什么排第三：
- 现在 breakout 线已经有两版 first-pass 动作：
  - `pair-conditioned`：更强，但更宽
  - `context-conditioned`：更窄，但证据更薄
- 若不把它们放进同一更严格框架，后面就会长期悬着两个候选同时占资源。

## 本轮改动

### 1) 已刷新 `docs/TODO.md` 顶部接力棒

把旧的 `2026-03-14 22:25` 版本更新为 `2026-03-15 01:05`，并把已完成的两条从“下一棒”位置移开。

新的未完成 Top 3 现在变成：
1. `EMA -> A股 daily strict holdout`
2. `breakout -> 更窄 context-conditioned sizing 的 walk-forward / pure-test honesty`
3. `breakout -> pair-conditioned vs context-conditioned 的更严格同框对照`

### 2) 已重建 plans 镜像

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

### 3) 本轮不改 cron / prompt

理由：
- 上轮同步到实际 payload 的 anti-repeat 硬约束已经开始见效；
- 当前没有证据支持继续叠加运行时限制。

### 4) 本轮不改 `ROADMAP.md`

理由：
- 当前问题不在项目大方向；
- 更像是入口层需要跟上最新结果节奏。

## 网页 / 表达建议

1. **当前 closure board / EMA / breakout 页面已经足够支撑决策，不需要再优先补解释文案**
   - 现在更值钱的是继续把“strict holdout / walk-forward honesty”往前推。

2. **EMA 页下一步应从 `A股 weekly` 转到 `A股 daily`，不要继续停在 weekly verdict 附近盘旋**

3. **breakout 页下一步不要再写新的 first-pass sizing 说明文**
   - 现在该做的是更严格复核与同框对照。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：保持当前频率与当前 payload**
   - 因为反重复约束已经开始起作用；
   - 本轮不需要继续动调度层。

2. **bot2-strategy-review-40m：继续保持**
   - 这轮 bot2 做的正确动作是：
     - 不再继续加规则；
     - 而是刷新入口层，让下一棒重新变清楚。

3. **下一轮 bot2 的观察点**
   - 只看：
     1. bot3 是否开始推进 `A股 daily strict holdout`；
     2. 或是否把 breakout context-conditioned sizing 推到 walk-forward / pure-test honesty；
     3. 或是否开始做 pair-vs-context 的更严格同框对照。

## 风险与不确定性

1. breakout 的更窄 context-conditioned sizing 当前仍只是 `late-segment promising`，不能提前当成已通过 pure-test 验证。
2. `EMA baseline family` 当前已被收窄，但尚未完成最终 closure；`A股 daily` 仍可能继续改写边界。
3. 当前 repo worktree 仍然很脏，因此本轮继续只做入口层小修与记录，不扩大改动面。
