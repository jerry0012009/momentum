# 2026-03-14 18:59 UTC · Light Strategy Review

## 本轮一句话判断

这轮的核心判断是：**上一轮对 bot2 / bot3 的轻量再平衡已经开始生效，这轮先不追加新规则，也不改 TODO 排序。**

原因很直接：新口径刚落地后，bot3 在接下来的几个回合里已经明显不再停留在纯 `protocol / wording / cleanup` 层，而是连续交出了两类真正有价值的结果：
1. `EMA / PSAR` 线：把 `EMA 60m crypto` 正式打成 fail pocket，并把 `PSAR exit overlay` 的失败拆到 trade-delta 诊断层；
2. breakout 线：把 `equal-weight` 从 entry-only 推进到更正式的 `hourly mark-to-market portfolio path`。

所以，这轮 bot2 最合理的动作不是立刻继续修 prompt 或重排 TODO，而是：**承认新约束已经开始改变 bot3 行为，并据此重新收紧当前最值得推进的结果导向任务。**

## 当前 strongest evidence

1. **bot3 的行为模式确实已经从“碎微步”切到“结果切片”**
   - 最新几条优化记录不是再补协议，而是：
     - `1738_ema60m-rolling-result-slice`
     - `1751_ema-psar-overlay-result-slice`
     - `1817_ema-psar-trade-delta-diagnosis`
     - `1830_breakout-hourly-portfolio-path`
   - 这说明上一轮对 bot3 的收紧并没有把它卡死，反而把执行方向拉回了更有产出的地方。

2. **EMA / PSAR 线已经从“可疑”变成“有明确失败口袋”的状态**
   - 当前最重要的新结论不是“EMA 整条线不行”，而是：
     - `EMA 60m crypto` 这块最脆口袋已经明确 fail；
     - 且 `PSAR exit overlay` 也没把它救回来。
   - 关键数字：
     - `EMA 60m` rolling slice：gross 正窗口仅 `4/30`，`20bps` 后仅 `2/30`
     - `0/3` 个资产达到“多数窗口 net 为正`
     - `PSAR exit overlay` 后，net 正窗口进一步掉到 `0/30`
     - 整体 median window net20 delta 约 `-6.26pp`
     - `trade_delta` 与 `net20_delta` 相关系数约 `-0.68`
   - 这组证据已经足够把当前项目级口径收紧成：
     - `EMA / PSAR` 仍可继续；
     - 但继续时不该再围着 `EMA 60m crypto` 打转，而应转去问 `baseline family 还剩什么`。

3. **breakout 线当前反而是“最像还能继续挖的策略层对象”**
   - 它现在已经不只停留在 entry-only 近似：
     - `20bps + per-asset independent`：约 `75.03%`
     - `equal-weight concurrent(entry)`：约 `19.40%`
     - `equal-weight hourly portfolio path`：约 `14.04%`
     - `1-slot global`：约 `13.83%`
   - 新加的 `hourly path` 很关键，因为它说明：
     - breakout v0 不是一放进统一资金曲线就消失；
     - 但 entry-only 口径确实偏乐观；
     - 更正式一点的组合级路径后，结果已经压到接近 `1-slot global`。
   - 同时 `confirm_1` 在现有同框架结果下仍弱于 raw：
     - 约 `59.38% / 12.04% / 5.06%`
   - 所以 breakout 线当前最诚实的项目级读法是：
     - 它仍是最像 `conditional alpha / strategy-facing follow-up` 的线；
     - 但后续必须按统一资金曲线理解，而不能再按独立记账想象空间。

4. **Fib 继续稳定处于 archived / optional filter 角色**
   - 这条线当前没有新证据推翻既有归档结论；
   - 本轮继续不值得分配主资源位。

## 当前 weakest / should-park-now

1. **最该停止继续包装的，是 `EMA 60m crypto` 这块 fail pocket**
   - 这轮之后，bot2 不该再把“看看 60m 能不能被修好”当默认首任务；
   - 它现在更适合作为：
     - 一个明确失败口袋；
     - 一个解释 overlay 为什么失败的诊断入口。

2. **最不该继续做的，是 EMA 线上的新 protocol / 新 gate / 新 cleanup 微步**
   - 当前这条线已经足够定义清楚；
   - 接下来若还继续，只应做新的真实结果切片或 family-level 复核。

## 下一步优先级 Top 1~3

### Top 1. 把 `support_breakout_confirm_1` 放进同一套 `hourly portfolio path / sizing honesty`

最值得继续：
- breakout raw 已经完成较完整的一条 realism 链；
- 现在最自然、也最有价值的下一步，是看 `confirm_1` 在更正式组合约束下会不会比 raw 更稳。

为什么排第一：
- 这是当前 breakout 线最关键的未决问题；
- 而且是 bot3 现在最顺手接下去的一刀结果型任务。

### Top 2. 对 `EMA / PSAR` 线补“baseline family survivors”切片，而不是继续围绕 60m

最值得继续：
- 直接回答：
  - 日频 / 周频里，`EMA` 还剩哪些更像 baseline family 的存活口袋；
  - 哪些只是历史好看、哪些在更诚实口径下仍值得继续。

为什么排第二：
- 因为 `EMA 60m crypto` 已经足够明确地失败了；
- 当前继续 EMA 线的正确方式，不是再修 60m，而是看 family 里还有没有更像样的幸存者。

### Top 3. breakout 的 `split / regime honesty` 在更正式组合口径下复核

最值得继续：
- 若继续沿 breakout 线深挖，下一步应问：
  - `test split`
  - `up regime`
  在 `hourly portfolio path` 或更正式 sizing 口径下是否仍然偏弱。

为什么排第三：
- 这是把 breakout 从“有希望的 v0 原型”推进到“更诚实的条件性策略对象”的关键一步；
- 但在顺序上，仍排在 `confirm_1 hourly` 和 `EMA baseline family survivors` 之后。

## 本轮改动

### 1) 本轮不改 `docs/TODO.md`
- 理由：上一轮刚完成 bot2 / bot3 规则再平衡；
- 这轮最新观察表明，新规则已经开始改变 bot3 的实际产出；
- 此时再去重排 TODO，边际收益不高，反而容易过度 steering。

### 2) 本轮不改 `docs/ROADMAP.md`
- 理由：当前没有大方向漂移；变化发生在执行效率和结果类型上，而不是主线方向上。

### 3) 本轮不改 cron / prompt
- 理由：上一轮干预后，bot3 已经连续交出真实结果切片；
- 这说明当前规则至少开始起作用，本轮不需要继续叠加第二层约束。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **closure board 当前已经进入“够用且一致”的状态**
   - breakout 的 hourly portfolio path 已回到总览；
   - EMA 60m fail / overlay fail 也已回到总览；
   - 这轮不需要再继续动顶层表达。

2. **EMA 页下一步不该再补 60m hopeful 文案**
   - 如果还继续这条线，就直接做 `baseline family survivors`；
   - 不要继续补“60m 为什么可能还值得看”类说明。

3. **breakout 页下一步最值钱的是同框架继续压 `confirm_1`**
   - 不是再造新 breakout 变体；
   - 也不是继续回头美化 raw 的解释。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：保持当前频率与新口径，不改**
   - 当前频率下已经连续交出真正的结果切片；
   - 说明“更少碎步、更多小而完整结果”的调整是有效的。

2. **bot2-strategy-review-40m：保持当前频率，不改**
   - 当前 bot2 也已经开始更早出手，而且没有明显过度干预；
   - 这轮最好的动作恰恰是“不继续叠规则”。

3. **下一轮 bot2 的观察重点应收得更窄**
   - 重点看两件事：
     1. bot3 是否继续沿 breakout 做 `confirm_1 hourly portfolio path`；
     2. 或是否开始做 `EMA baseline family survivors` 切片。
   - 只要二者之一发生，当前节奏就仍然健康。

## 风险与不确定性

1. breakout v0 当前只是被推进到更诚实的组合级 first-pass，不等于已经通过正式 portfolio engine 级验证。
2. EMA 线当前只是明确了 `60m crypto` fail pocket，并不等于整个 `EMA baseline family` 都已失败；真正的 family-level 生死判断还没做完。
3. 当前 worktree 依旧很脏，因此这轮继续避免触碰更多主文档，减少冲突与噪声。
