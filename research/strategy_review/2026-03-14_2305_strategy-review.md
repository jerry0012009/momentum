# 2026-03-14 23:05 UTC · Light Strategy Review

## 本轮一句话判断

这轮判断是：**先不再改 TODO / roadmap / cron。上一轮刚刷新的接力棒目前还没被新证据推翻，而 timeout 修正也已经恢复正常；当前更合理的动作是确认新节奏已经稳住，而不是再连续重写入口层。**

## 当前 strongest evidence

1. **cron 执行层已经恢复正常**
   - `openclaw cron list --json` 当前显示：
     - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`，`consecutiveErrors = 0`
     - `bot2-strategy-review-40m`：`lastRunStatus = ok`，`consecutiveErrors = 0`
   - 说明上一轮对 timeout 的最小修正已经生效；
   - 这轮没有看到继续 timeout 的证据，因此不需要再动调度参数。

2. **当前 TODO 顶部接力棒仍然是新鲜的，并没有再次 stale**
   - 当前 `docs/TODO.md` 顶部 `Current relay baton（2026-03-14 22:25）` 仍是未完成的真实下一棒：
     1. `EMA -> A股 weekly frontier 更严格 rolling / holdout honesty`
     2. `breakout -> ETH+SOL pair-conditioned halfsize 的更严格 holdout / walk-forward 复核`
     3. `breakout -> 更克制的 context-conditioned sizing 对照`
   - 截至本轮可见产物，还没有新的结果把这三个顺序推翻。

3. **关键页面入口已和最新证据对齐，不存在明显表达滞后**
   - `alpha_closure_board` 已同步 breakout 的最新 sizing 结果：
     - `avoid_fluctuating` 后 hourly path 约 `15.46%`
     - `ETH+SOL` halfsize 后约 `19.90%`
     - max drawdown 约 `-9.97% -> -9.04%`
   - `EMA / PSAR` 页也已同步 A股 frontier 的第一刀 rolling 结果：
     - `创业板ETF 1wk` 当前最弱，`EMA` median window net20 约 `-11.64%`
     - 同格 `PSAR` 约 `+13.10%`
   - 所以当前不需要再补入口表达层修正。

4. **过去一轮最关键的新结论仍然成立，但这轮还没有新结果继续改写它们**
   - EMA 线：
     - `EMA baseline family` 没被 A股 frontier 一刀否掉；
     - 但真正最需要继续收窄的是 `A股 weekly frontier`，尤其 `创业板ETF 1wk`。
   - breakout 线：
     - `ETH+SOL` pair-conditioned halfsize` 是第一张有信息量的 sizing slice；
     - 下一步更该做更严格复核，而不是回头继续做变体排序。

## 当前 weakest / should-watch-now

1. **当前最大的风险不是研究排序，而是下一刀能不能真的往“更严格复核”推进**
   - 现在最怕的不是 bot3 又回去写 protocol；
   - 而是停在“first-pass slice 已经挺好看”这一层，不继续推进 holdout / walk-forward honesty。

2. **当前最不该做的是 bot2 再连续重写 relay baton**
   - 上一轮才刚刚刷新为新的未完成 Top 3；
   - 本轮没有新结果足以支持再改一次。

## 下一步优先级 Top 1~3

### Top 1. EMA：A股 weekly frontier 的更严格 rolling / holdout honesty

为什么仍排第一：
- 当前 EMA 线真正还没判完的，就是 `创业板ETF 1wk` 这类 A股 weekly frontier；
- 它最可能改写 `EMA baseline family` 的最后 verdict。

### Top 2. breakout：`ETH+SOL` pair-conditioned halfsize 的更严格 holdout / walk-forward 复核

为什么仍排第二：
- 当前 `15.46% -> 19.90%`、`-9.97% -> -9.04%` 这组改进很值得认真验证；
- 但现在还只是 first-pass sizing slice，最需要的是验证可迁移性。

### Top 3. breakout：更克制的 context-conditioned sizing 对照

为什么仍排第三：
- 因为当前 residual weakness 已经指向更窄的 context；
- 下一步自然应该问：是不是不需要对整个 `ETH+SOL` pair 都动手，而只该在更窄 context 下收仓。

## 本轮改动

### 1) 本轮不改 `docs/TODO.md`
- 理由：上一轮刚刷新接力棒；
- 本轮没有新结果足以支持继续改入口层。

### 2) 本轮不改 cron / prompt
- 理由：timeout 修正后，bot2 / bot3 均已恢复 `ok`；
- 当前没有继续干预调度层的必要。

### 3) 本轮不改 `ROADMAP.md`
- 理由：当前问题不在大方向；
- 也没有新的项目级证据需要回写到 roadmap。

本轮只新增这份轻量巡检记录。

## 网页 / 表达建议

1. **当前页面入口已够清楚，先别继续加解释文案**
   - closure board、EMA 页、breakout 页都已同步最新结论；
   - 现在更值钱的是新结果，不是再补措辞。

2. **EMA 页下一步仍应坚持“压 weekly frontier”，而不是回到 generic family 文案**

3. **breakout 页下一步应直接往更严格 sizing honesty 走，不要回头重做 weak-pocket 诊断**

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：继续保持当前频率与 timeout 设置**
   - 本轮没有看到新的 timeout 或执行噪声；
   - 也没有看到显著跑偏。

2. **bot2-strategy-review-40m：继续保持**
   - 当前 bot2 更像“看护方向与入口层”；
   - 这轮没有证据支持继续出手修改。

3. **下一轮 bot2 的观察点非常窄**
   - 只看：
     1. 是否出现 `A股 weekly frontier` 的更严格复核；
     2. 或是否出现 `ETH+SOL` halfsize 的 holdout / walk-forward 复核；
     3. 或是否出现更克制的 context-conditioned sizing slice。
   - 若三者其一出现，当前节奏就仍然健康。

## 风险与不确定性

1. 当前 breakout 的 sizing 改善仍只是 first-pass，不能提前当成稳健可迁移结论。
2. 当前 EMA 线的最终 family verdict 仍未关门，A股 weekly frontier 仍可能迫使继续收窄。
3. 本轮没有新 durable artifact 改写项目排序，因此当前“不改”是基于证据尚未变化，而不是默认保守。
