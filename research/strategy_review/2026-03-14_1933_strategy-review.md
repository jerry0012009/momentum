# 2026-03-14 19:33 UTC · Light Strategy Review

## 本轮一句话判断

这轮的主判断是：**可以开始把新节奏正式写回 TODO 入口层了。**

上一轮我选择“不再加规则，只观察新规则是否生效”；而这轮观察结果已经足够明确：bot3 不仅没有继续回到碎微步，反而连续交出了 `EMA 60m fail slice / PSAR overlay fail diagnosis / breakout hourly portfolio path` 这类结果型切片。既然行为模式已经被拉正，这轮最有杠杆的 bot2 动作，就不再是继续改 prompt，而是把当前最值得认领的 1~3 个结果导向任务正式写进 `TODO.md` 前部，避免 bot3 又在长清单里自己捡低杠杆边角料。

## 当前 strongest evidence

1. **新的 bot2 / bot3 口径已经开始改变实际产出，不再只是纸面修词**
   - 最近 bot3 连续产出的关键记录是：
     - `1738_ema60m-rolling-result-slice`
     - `1751_ema-psar-overlay-result-slice`
     - `1817_ema-psar-trade-delta-diagnosis`
     - `1830_breakout-hourly-portfolio-path`
     - 以及两条 closure-board refresh
   - 这说明此前“bot3 过分强调最小任务、拆得太碎”的问题，至少已经开始被矫正。

2. **EMA / PSAR 线现在已经完成一轮诚实收缩**
   - 当前关键结论不再是“EMA 很可能是 baseline”，而是更窄：
     - `EMA 60m crypto` 是明确 `fail pocket`
     - `PSAR exit overlay` 也没把它救回来
   - 关键数字：
     - `EMA 60m` rolling slice：gross 正窗口仅 `4/30`，`20bps` 后仅 `2/30`
     - `0/3` 资产达到“多数窗口 net 为正”
     - overlay 后正窗口变成 `0/30`
     - median window net20 delta 约 `-6.26pp`
     - `trade_delta` 与 `net20_delta` 相关系数约 `-0.68`
   - 因而当前更合理的继续方式，不是再围着 60m hopeful 文案打转，而是转去问：`baseline family 还剩什么`。

3. **breakout 线现在是最像“继续往策略层推进但要更诚实”的对象**
   - raw 在 `20bps` 下的几档口径现在已经很清楚：
     - per-asset independent：约 `75.03%`
     - equal-weight concurrent(entry)：约 `19.40%`
     - equal-weight hourly portfolio path：约 `14.04%`
     - 1-slot global：约 `13.83%`
   - 这说明它不是一进统一资金曲线就归零；
   - 但也说明过去更乐观的独立记账 / entry-only 读法必须让位于更正式组合口径。
   - 同时 `confirm_1` 在现有同框架结果下仍弱于 raw：
     - 约 `59.38% / 12.04% / 5.06%`
   - 所以 breakout 当前最值钱的未决问题，就变成：**`confirm_1` 放进同一套 hourly portfolio path 后，会不会比 raw 更稳？**

4. **当前 TODO 虽然并不失真，但还缺一个“结果导向接力棒”入口层**
   - 细节条目很多、证据链也都在；
   - 但对 bot3 来说，仍然容易出现：
     - 看到长清单后去挑最碎、最轻、最安全的小边角；
     - 而不是直接认领当前最值得做的结果切片。
   - 因此，这轮最值得做的就是补一小段“当前接力棒”。

## 当前 weakest / should-fix-next

1. **最该停止继续浪费回合的，是“EMA 线继续补 protocol / gate / cleanup / closure-copy”**
   - 当前这条线缺的已经不是定义；
   - 再继续写定义，边际价值会很低。

2. **最该避免的，是 breakout 线重新扩成新变体竞赛**
   - 当前更值钱的是把 `raw vs confirm_1` 在更正式组合约束下看清；
   - 而不是再开新的 breakout 衍生分支。

## 下一步优先级 Top 1~3

### Top 1. `support_breakout_confirm_1` 放进同一套 `hourly portfolio path / sizing honesty`

最值得继续：
- 直接回答 `confirm_1` 在更正式组合约束下会不会比 raw 更稳；
- 这也是当前 breakout 线最自然、最有结果感的一刀。

### Top 2. `EMA baseline family survivors` 切片

最值得继续：
- 直接去看日频 / 周频里，哪些口袋还像 `baseline family` 的幸存者；
- 不再默认围着 `EMA 60m crypto` 打转。

### Top 3. breakout 的 `split / regime honesty` 在更正式组合口径下复核

最值得继续：
- 进一步回答：
  - `test split`
  - `up regime`
  在 `hourly portfolio path / sizing` 口径下是不是仍然偏弱。

## 本轮改动

### 1) 微调 `docs/TODO.md`（已执行）
我没有重写 TODO，而是只在前部新增了一个很小的：
- **`当前接力棒（2026-03-14 19:33）`**

里面正式写入了 3 个当前最值得认领的结果导向任务：
1. `confirm_1 hourly portfolio path / sizing honesty`
2. `EMA baseline family survivors`
3. `breakout split / regime honesty` in formal portfolio context

同时也明确写入两条“当前不优先”：
- 不再优先新增 `EMA` 线上的 `protocol / gate / cleanup / closure-copy`
- 不再优先扩新的 breakout 变体

### 2) 重建 plans 镜像（已执行）
- 执行：`python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`
- 让站点上的 `momentum_todo` 镜像也同步带上这段结果导向接力棒。

### 3) 本轮不改 cron / prompt
- 理由：上一轮改的规则已经开始起作用；
- 这轮更有价值的是把当前接力棒写回板子，而不是继续叠规则。

### 4) 本轮不改 `ROADMAP.md`
- 理由：当前不是大方向问题，而是执行入口层如何更直接服务下一回合认领。

## 网页 / 表达建议

1. **当前最值得改的表达层不是 closure board，而是 TODO 入口层**
   - closure board 现在已经够清楚；
   - 但 bot3 真正每天在用的是 TODO。

2. **EMA 页接下来不要再补 60m hopeful 文案**
   - 若继续，就直接补 `baseline family survivors`。

3. **breakout 页接下来最值钱的是 `confirm_1 hourly path`**
   - 而不是再补 raw 的解释，或重新扩 breakout 家族。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：保持当前频率与新口径**
   - 现在看，新的“小而完整 / 结果优先”口径已经开始带来真实结果；
   - 当前不需要再继续改频率或叠规则。

2. **bot2-strategy-review-40m：继续保持**
   - 这轮 bot2 做的，就是 brief 里最该做的一类事：
     - 不过度大审；
     - 但在证据足够时，直接改板子入口层。

3. **下一轮 bot2 的观察重点**
   - 只问：
     1. bot3 是否接上 `confirm_1 hourly path`；
     2. 或是否开始做 `EMA baseline family survivors`。
   - 只要二者之一发生，当前调整就仍然健康。

## 风险与不确定性

1. breakout v0 当前仍只是更诚实的组合级 first-pass，不是正式 portfolio engine 结论。
2. EMA 线当前只是明确了 `60m crypto` fail pocket；family-level 生死判断仍未完成。
3. 当前 worktree 依旧很脏，所以本轮刻意只做 TODO 入口层微调，而不去碰更多大文档或大范围页面结构。
