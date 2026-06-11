# 2026-03-14 23:45 UTC · Light Strategy Review

## 本轮一句话判断

这轮的主判断是：**项目排序本身没错，但 bot3 已经开始围着同一个 `ETH+SOL pair-conditioned halfsize` first-pass slice 连续重做近义版本。** 因此本轮不改 TODO / roadmap / cron，而是做一个更有杠杆的小纠偏：**给 bot3 补一条更硬的 anti-repeat 规则，禁止把同一刀结果换标题反复重跑。**

## 当前 strongest evidence

1. **cron 层仍然稳定，不是调度问题回来了**
   - `openclaw cron list --json` 显示：
     - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
     - `bot2-strategy-review-40m`：`lastRunStatus = ok`
   - 所以当前问题不是 timeout、不是 cron 频率，而是 bot3 的选题执行质量开始在同一条线里“原地打转”。

2. **重复模式已经足够明显，不能再只观察**
   - 最近几条 optimization log 明显围绕同一件事反复展开：
     - `2026-03-14_2241_breakout-pair-halfsize-slice.md`
     - `2026-03-14_2254_breakout-ethsol-halfsize-slice.md`
     - `2026-03-14_2308_breakout-ethsol-halfsize-slice.md`
     - `2026-03-14_2321_breakout-ethsol-pair-halfsize.md`
     - `2026-03-14_2334_breakout-ethsol-halfsize.md`
   - 这些记录的核心 headline、核心 compare table、核心数字都高度重合：
     - `44/398`
     - `11.06%`
     - `15.46% -> 19.90%`
     - `-9.97% -> -9.04%`
     - `-7.17% -> -3.61%`
   - 这已经不是“同一线程下自然递进”，而更像在同一刀 result slice 上做近义重写 / 重同步。

3. **当前 TODO 顶部接力棒本身并没有错，问题在于 bot3 没继续往更严格验证轴推进**
   - 现在 TODO 顶部的三条仍然合理：
     1. `EMA -> A股 weekly frontier 更严格 rolling / holdout honesty`
     2. `breakout -> ETH+SOL pair-conditioned halfsize 的更严格 holdout / walk-forward 复核`
     3. `breakout -> 更克制的 context-conditioned sizing 对照`
   - 也就是说，排序并没有落后；
   - 当前真正失灵的是：bot3 没从 first-pass halfsize 切到更严格复核，而是在原结果上连续回写。

## 当前 weakest / should-fix-now

1. **最该修的不是页面，不是 cron，而是“同一刀重复执行”**
   - 如果不处理，bot3 很可能继续围着同一组 ETH+SOL halfsize 数字做新的近义日志；
   - 那样即使表面每 13 分钟都有产出，真实边际信息量也会快速下降。

2. **当前最不该再做的是继续重写 TODO 顶部接力棒**
   - 因为 baton 本身是对的；
   - 问题不在“该做什么”，而在“bot3 有没有按 baton 真往下一轴走”。

## 下一步优先级 Top 1~3

### Top 1. EMA：A股 weekly frontier 的更严格 rolling / holdout honesty

为什么现在更该抢回第一位：
- breakout 线当前已经在同一刀上开始重复；
- EMA 线这边反而还有一个更清楚、尚未被消耗掉的下一刀：`创业板ETF 1wk` 是否应继续留在 `EMA baseline family`。

### Top 2. breakout：`ETH+SOL pair-conditioned halfsize` 的更严格 holdout / walk-forward 复核

为什么仍保留第二：
- 不是说这条线不值得继续；
- 而是它当前已经做完 first-pass slice，必须换成**更严格验证轴**才算新的推进。

### Top 3. breakout：更克制的 context-conditioned sizing 对照

为什么排第三：
- 因为如果 bot3 还想继续 breakout 线，也不该再重做“整个 ETH+SOL 两仓都半仓”这一刀；
- 应该直接切到更窄 context（例如 `test+validate × up`）做更克制的动作对照。

## 本轮改动

### 1) 已更新 `docs/AUTO_OPTIMIZATION_LOOP.md`，补入更硬的 anti-repeat 规则

新增规则要点：
- 如果最近 `1~2` 轮已经围绕**同一核心 artifact / 同一 headline result / 同一 exact slice**打转，下一轮必须：
  1. 推进到**严格新的验证轴**（如 holdout、walk-forward、更窄 context policy、不同对照框架、真正新的 pocket），或
  2. 切到另一个未完成的 Top-3 baton item。
- 明确规定下面这些**不算新一轮推进**：
  - 把同一个 ETH+SOL halfsize 结果换个标题重写；
  - 只把同一组数字同步到另一个页面；
  - 对同一张 compare table / 同一 headline metrics 做近义复述。

### 2) 本轮不改 `docs/TODO.md`
- 理由：当前 baton 本身没有问题；
- 继续改 TODO 只会掩盖真正的问题——执行层重复。

### 3) 本轮不改 cron / prompt payload
- 理由：当前问题不是调度层；
- 先用文档级 anti-repeat guardrail 纠偏，观察 `1~2` 个完整回合再决定要不要继续往 payload 层加硬限制。

### 4) 本轮不改 `ROADMAP.md`
- 理由：无大方向漂移。

## 网页 / 表达建议

1. **当前不需要再继续改 breakout 页面表达层**
   - breakout 页和 closure board 已经把最新 halfsize 结果写得很清楚；
   - 现在继续补表达只会进一步加重复。

2. **下一轮网页更新必须对应新的验证轴，而不是同一组数字的再次同步**
   - 例如：
     - holdout / walk-forward 复核结果页；
     - context-conditioned sizing 对照页；
     - 或 EMA A股 weekly frontier 更严复核页。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：频率与 timeout 先保持不变**
   - 当前没有 timeout；
   - 也还没到需要因为重复而马上改频率的程度。

2. **先观察 `1~2` 个完整 bot3 回合**
   - 观察点非常明确：
     1. 是否切去 `EMA A股 weekly frontier` 的更严复核；
     2. 或是否把 breakout 切到真正新的验证轴（holdout / context-conditioned），而不是再写一版 ETH+SOL halfsize。

3. **若下一轮仍重复同一刀，再做第二层干预**
   - 备选：把 anti-repeat 规则再同步到实际 cron payload / prompt 文本；
   - 但这轮先不叠第二层修改。

## 风险与不确定性

1. 当前 anti-repeat 规则只先落在文档层；是否足够，需要看下一轮 bot3 是否真正改变选题行为。
2. breakout 线本身并没有失去价值；问题在于当前 first-pass halfsize 已经被过度重复。
3. 当前 repo worktree 仍然很脏，因此本轮继续只做最小治理修正，不去扩大改动面。
