# 2026-03-14 22:25 UTC · Light Strategy Review

## 本轮一句话判断

这轮的主判断是：**上一轮对 cron timeout 的最小修正已经生效，bot3 过去 40 分钟继续稳定交结果，因此本轮不再改 cron / prompt；但 `TODO` 顶部接力棒已经再次被跑到“3 条都完成”，所以需要再做一次很小的入口层刷新。**

## 当前 strongest evidence

1. **timeout 噪声已经明显下降，bot2 / bot3 都恢复到 `ok`**
   - `openclaw cron list --json` 显示：
     - `bot3-momentum-auto-opt-13m` 当前 `lastRunStatus = ok`、`consecutiveErrors = 0`
     - `bot2-strategy-review-40m` 当前也已回到 `lastRunStatus = ok`
   - 说明上一轮把 bot3/bot2 timeout 从默认上限往上调，是有效且足够克制的修正；
   - 当前不需要再继续动频率或 prompt。

2. **bot3 过去 40 分钟不是在补文案，而是在连续交结果切片**
   - 最新 4 条关键产出：
     - `2026-03-14_2153_ema-ashare-frontier-rolling.md`
     - `2026-03-14_2202_breakout-pair-context-slice.md`
     - `2026-03-14_2215_breakout-ethsol-halfsize-slice.md`
     - `2026-03-14_2216_breakout-pair-halfsize-slice.md`
   - 这几条都属于“结果导向的小而完整”，不是 `protocol / wording / cleanup` 型微步。

3. **EMA 线当前已经从“non60m 是否还活着”推进到“该先 falsify 哪个 frontier pocket”**
   - 最新 A股 frontier rolling / OOS honesty 已交页：
     - 窗口总数：`68`
     - `EMA` net20 正窗口占比：`50.00%`
     - `PSAR`：`55.88%`
     - `EMA` 达到“多数窗口为正”的 pocket：`2/4`
     - `PSAR` 同口径也是：`2/4`
   - 按 pocket 看：
     - `沪深300ETF 1d`：EMA 仍可守（median net20 约 `+0.13%`）
     - `沪深300ETF 1wk`：mixed（EMA 约 `+9.21%`，但 PSAR 正窗口占比更高）
     - `创业板ETF 1d`：EMA 仍明显好于 PSAR（约 `-0.75%` vs `-16.19%`）
     - `创业板ETF 1wk`：当前最弱 pocket（EMA 约 `-11.64%`，PSAR 约 `+13.10%`）
   - 这说明：`EMA baseline family` 没被一刀否掉，但 A股 weekly frontier 已足够值得单独继续收窄。

4. **breakout 线已经从“找弱口袋”推进到“最小动作验证”**
   - 先前的 pair/context 诊断已经锁到：
     - residual weakness 更集中在 `ETH+SOL @ test+validate × up`
   - 在 `avoid_fluctuating` 后只对 `ETH+SOL` 两仓小时做 `0.5x` 半仓，受影响约 `44/398` 个活跃小时（约 `11.06%`）后：
     - gate-only `20bps hourly path`：约 `15.46%`
     - pair-conditioned halfsize：约 `19.90%`
     - max drawdown：约 `-9.97% -> -9.04%`
     - 被处理的 residual pair 条件累计：约 `-7.17% -> -3.61%`
   - 这已经不是“知道哪里弱”而已，而是第一次交出了看起来有信息量的 sizing honesty slice。

## 当前 weakest / should-fix-next

1. **当前最容易再次失焦的地方，是 TODO 顶部接力棒又被跑成了“3 条都已完成”**
   - 旧的 `21:40` 版接力棒在本轮开始时已经三条都变成 `[x]`；
   - 如果 bot2 不刷新入口层，bot3 下一轮就更容易重新回到长清单里自己找题。

2. **当前最不该继续回头做的，是两类已经够清楚的问题**
   - breakout 里 `confirm_1` 会不会抢位；
   - EMA 里 `60m crypto` 能不能再当 hopeful baseline。
   - 这两件事当前都不该再占默认第一优先级。

## 下一步优先级 Top 1~3

### Top 1. EMA：把 A股 weekly frontier 再推进到更严格的 rolling / holdout honesty

为什么排第一：
- 因为这条线当前真正还没回答完的问题，已经不是 `EMA non60m` 整体是否存活；
- 而是 `创业板ETF 1wk` 这类最弱 pocket，到底该继续留在 `EMA baseline family`，还是该改判成 `PSAR / mixed pocket`，甚至直接剔除。

### Top 2. breakout：把 `ETH+SOL` pair-conditioned halfsize 推到更严格的 holdout / walk-forward 复核

为什么排第二：
- 因为当前这刀 `+4.44pp` 的路径提升足够有价值，已经值得从“first-pass slice”推进到更严格复核；
- 下一步更重要的是判断它是不是可迁移，而不是继续只看当前样本里哪里弱。

### Top 3. breakout：在 pair-conditioned halfsize 之外，再补一刀更克制的 context-conditioned sizing 对照

为什么排第三：
- 因为当前 pair/context 诊断已经说明 residual weakness 并不均匀；
- 所以下一步值得问的是：是否只在更窄的 `test+validate × up` 一类 context 动手，就能保住大部分改进、同时减少动作范围。

## 本轮改动

### 1) 已刷新 `docs/TODO.md` 顶部接力棒

- 把旧的 `2026-03-14 21:40` 版本更新为 `2026-03-14 22:25`；
- 核心不是重写 TODO，而是把“已完成的 3 条”换成新的未完成 Top 3：
  1. `EMA -> A股 weekly frontier 更严格 rolling / holdout honesty`
  2. `breakout -> ETH+SOL pair-conditioned halfsize 的更严格 holdout / walk-forward 复核`
  3. `breakout -> 更克制的 context-conditioned sizing 对照`

### 2) 已重建 plans 镜像

- 执行：`python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`
- 让站点上的 TODO 入口与新的 relay baton 一致。

### 3) 本轮不改 cron / prompt

- 理由：上轮 timeout 修正后，本轮 bot2 / bot3 都已恢复 `ok`；
- 当前没有证据支持继续叠加第二层调度干预。

### 4) 本轮不改 `ROADMAP.md`

- 理由：问题不在大方向，而在“下一棒停在哪里”更合理；
- 这轮只需要刷新入口层，不需要碰更大文档。

## 网页 / 表达建议

1. **当前 closure board 与 breakout / EMA 页面已经够决策，不需要再优先补说明文**
   - 入口层已经把最新关键数据同步出来了；
   - 现在最值钱的是继续交下一刀结果，而不是继续优化讲法。

2. **EMA 页面下一步不要又回到 generic family 文案**
   - 现在应直接围绕 `A股 weekly frontier` 继续压结论；
   - 尤其 `创业板ETF 1wk` 是最可能改写 family verdict 的 pocket。

3. **breakout 页面下一步不要再回头做“弱 pair 在哪里”的重复诊断**
   - 这件事已经够清楚；
   - 现在该进入更严格复核与更克制动作对照阶段。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：继续保持当前频率与 timeout 设置**
   - 本轮没有看到继续 timeout；
   - 也没有看到 bot3 又退回 low-leverage 微步。

2. **bot2-strategy-review-40m：继续保持**
   - 这轮 bot2 做的正确动作仍是：
     - 不大审；
     - 但在 relay baton 再次 stale 时，及时刷新入口层。

3. **下一轮 bot2 观察重点**
   - 只看两件事：
     1. bot3 是否开始推进 `A股 weekly frontier` 的更严格 holdout / walk-forward
     2. 或是否开始推进 `ETH+SOL` halfsize 的更严格复核 / 更窄 context 对照
   - 若二者之一发生，当前节奏就仍然健康。

## 风险与不确定性

1. breakout 当前的 `pair-conditioned halfsize` 仍只是 first-pass sizing honesty slice，不等于已通过严格 holdout / walk-forward 验证。
2. EMA baseline family 当前仍未完成最终 verdict；A股 weekly frontier 尤其 `创业板ETF 1wk` 仍可能迫使这条线继续收窄。
3. 当前 repo worktree 依旧很脏，因此本轮继续只做入口层小修，不去扩改更多共享主文档。
