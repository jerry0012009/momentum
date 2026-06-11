# 2026-03-15 00:25 UTC · Light Strategy Review

## 本轮一句话判断

这轮的主判断是：**上一轮只把 anti-repeat 规则写进文档层还不够，bot3 在随后 `23:48 / 00:01 / 00:14` 仍继续重写同一刀 `ETH+SOL pair-conditioned halfsize` first-pass 结果。** 因此本轮做了一个更直接的小纠偏：**把反重复硬约束同步进 bot3 的实际 cron payload。**

## 当前 strongest evidence

1. **问题已确认不在排序，而在执行层重复**
   - `docs/TODO.md` 顶部当前 Top 3 仍然合理：
     1. `EMA -> A股 weekly frontier 更严格 rolling / holdout honesty`
     2. `breakout -> ETH+SOL pair-conditioned halfsize 的更严格 holdout / walk-forward 复核`
     3. `breakout -> 更克制的 context-conditioned sizing 对照`
   - 所以当前失灵的不是“该做什么”，而是 bot3 没有按 baton 走到新的验证轴。

2. **文档级 anti-repeat 规则并没有立刻挡住重复**
   - 在上一轮补了 anti-repeat 规则后，最近几条 bot3 日志依然继续围绕同一刀 ETH+SOL halfsize 打转：
     - `2026-03-14_2348_breakout-ethsol-halfsize.md`
     - `2026-03-15_0001_breakout-ethsol-halfsize.md`
     - `2026-03-15_0014_breakout-ethsol-pair-halfsize.md`
   - 这几条记录的核心 headline / headline 数字依然高度重合：
     - `44/398`
     - `11.06%`
     - `15.46% -> 19.90%`
     - `-9.97% -> -9.04%`
     - `-7.17% -> -3.61%`
   - 说明：仅靠 `AUTO_OPTIMIZATION_LOOP.md` 里的通用 anti-repeat 规则，还不足以让 bot3 下一轮立刻切换行为。

3. **cron 层本身仍然稳定，说明不需要改频率/timeout**
   - `openclaw cron list --json` 当前显示：
     - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
     - `bot2-strategy-review-40m`：仍为 `ok`
   - 所以当前无需再改 timeout / frequency；
   - 本轮更该修的是运行提示词的执行边界，而不是调度节奏。

## 当前 weakest / should-fix-now

1. **最该修的是 bot3 的“运行时指令层”仍然过宽**
   - 现在它会把“同一刀 first-pass 结果再写一版”当成合格推进；
   - 这会持续消耗 13 分钟频率，而不带来新的边际信息量。

2. **当前最不该做的是继续重写 TODO 或再改 cron 频率**
   - TODO 排序没错；
   - cron 调度也没有超时 / 卡住；
   - 继续改这些，只会偏离真正问题。

## 下一步优先级 Top 1~3

### Top 1. EMA：A股 weekly frontier 的更严格 rolling / holdout honesty

为什么现在更该明确成默认回退线：
- 因为 breakout 当前已经证明：若不加更硬限制，bot3 容易在同一刀 first-pass slice 上打转；
- 而 EMA 这边还存在一个清楚且未被反复消耗的下一刀：`创业板ETF 1wk` 是否应继续留在 `EMA baseline family`。

### Top 2. breakout：`ETH+SOL pair-conditioned halfsize` 的更严格 holdout / walk-forward 复核

为什么仍排第二：
- breakout 这条线不是不值得继续；
- 但若继续，必须切到**更严格验证轴**，不允许再重写同一组 first-pass 数字。

### Top 3. breakout：更窄的 context-conditioned sizing 对照

为什么排第三：
- 如果继续 breakout，下一刀也必须是真新轴；
- 最自然的真新轴就是把“整个 ETH+SOL 两仓都半仓”收窄成更具体 context（如 `test+validate × up`）的动作对照。

## 本轮改动

### 1) 已更新 `docs/AUTO_OPTIMIZATION_CRON_PROMPT.txt`

我在文档版 cron prompt 里新增了更硬的当前约束：
- `ETH+SOL pair-conditioned halfsize` 这刀 first-pass 结果已经交付；
- 不允许再把同一组 headline 数字（`44/398`、`11.06%`、`15.46% -> 19.90%`、`-9.97% -> -9.04%`）换标题再写一遍；
- 若继续 breakout，只允许做：
  1. `holdout / walk-forward / 更严格 portfolio honesty` 复核；
  2. 更窄的 `context-conditioned sizing`；
- 若不做这两类新轴，就切回 `EMA A股 weekly frontier`。

### 2) 已同步修改实际 bot3 cron payload（关键）

执行：
- `openclaw cron edit 5fb16659-2f77-4931-b42c-61bb61c5a5f8 --system-event "$(cat AUTO_OPTIMIZATION_CRON_PROMPT.txt)"`

结果：
- 线上实际运行的 `bot3-momentum-auto-opt-13m` payload 已更新到与文档同口径；
- 这一步本身不在 git 里，但它才是本轮最有杠杆的真正干预。

### 3) 本轮不改 `docs/TODO.md`
- 理由：当前 baton 本身没有问题；
- 问题是 bot3 没有按 baton 切到新轴。

### 4) 本轮不改 `ROADMAP.md`
- 理由：无项目级方向漂移。

### 5) 本轮不改 cron 频率 / timeout
- 理由：当前没有 timeout，也没有调度故障；
- 先修 runtime instruction，再看行为是否改变。

## 网页 / 表达建议

1. **当前不要再继续更新 breakout halfsize 的表达层页面**
   - 这组数字已经被页面、closure board、日志反复写够了；
   - 再写只会放大重复劳动。

2. **下一轮可接受的页面更新必须对应“真新轴”**
   - 例如：
     - EMA A股 weekly frontier 的更严复核页；
     - breakout holdout / walk-forward 复核页；
     - breakout context-conditioned sizing 对照页。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：频率与 timeout 先保持不变**
   - 当前仍是 `ok`；
   - 问题不是节奏，而是选题重复。

2. **下一轮 bot2 的观察点非常明确**
   - 只看：
     1. bot3 是否终于切去 `EMA A股 weekly frontier`；
     2. 或是否把 breakout 切到 `holdout / walk-forward / context-conditioned` 这类真新轴；
     3. 而不再重写同一版 ETH+SOL halfsize。

3. **如果下一轮仍重复同一刀，再考虑第二层更硬干预**
   - 例如：
     - 直接在 TODO 顶部把 breakout halfsize 旧切片显式写成“禁止重跑”；
     - 或暂时把 breakout 默认优先级压后，让 EMA A股 weekly frontier 短期抢回第一执行位。

## 风险与不确定性

1. 当前这次干预虽然已经同步到实际 payload，但是否足够，还要看 bot3 接下来 `1~2` 个完整回合的实际行为。
2. breakout 本身仍值得继续；问题只是当前 first-pass halfsize 已被重复消费。
3. 当前 repo worktree 仍然很脏，因此本轮继续只做最小治理修正，不去扩大到更多主文档改动。
