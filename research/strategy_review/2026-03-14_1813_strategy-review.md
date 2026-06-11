# 2026-03-14 18:13 UTC · Light Strategy Review

## 本轮一句话判断

这轮的核心判断是：**上一轮做的最小 prompt 收紧是合理的，而且这轮先保持，不再追加第二次干预。**

原因不是问题已经解决，而是当前最合理的策略顺序是：
1. 先承认 `EMA / PSAR` 线此前确实连续多轮停留在 protocol / closure / gate 层；
2. 因此上一轮对 bot3 做“EMA 先交结果、别再补 protocol”的最小收紧是必要的；
3. 但在还没给这个新约束 1~2 个完整回合反应时间前，不应该立刻继续叠第二层干预。

所以这轮 bot2 的最优动作不是再改 TODO 或再改 prompt，而是：**明确进入“观察 prompt 收紧是否生效”的窗口，同时保持项目级优先级不变。**

## 当前 strongest evidence

1. **breakout 线的资源排序现在已经非常清楚，不是当前主要问题来源**
   - 当前顶层与子页都已经能一致回答：
     - raw `20bps + per-asset independent / equal-weight / 1-slot` 约 `75.03% / 19.40% / 13.83%`
     - confirm_1 同框架约 `59.38% / 12.04% / 5.06%`
   - 因而 breakout 内部排序已经稳定：
     - `raw` 继续作为主原型
     - `confirm_1` 只作为紧邻确认变体
   - 这条线还没收工，但当前不缺“该往哪边继续”的判断。

2. **EMA 线在干预前，确实已经出现明显的“协议层连做多轮”现象**
   - 最近连续推进的都是：
     - first falsification slice 定义
     - closure board next-step 回挂
     - TODO 去陈旧化
     - 最小组合协议
     - go / yellow / fail gate
   - 这些动作单条都合理，但合起来已经足够说明：
     - 当前瓶颈不在“还没定义好怎么验”
     - 而在“还没把第一刀真实切片跑出来”

3. **因此，上轮 prompt 收紧是对症的最小修正**
   - 我已经对 bot3 的 cron payload 增加了一条很克制的硬约束：
     - 若某条线连续补了 `protocol / decision / gate / cleanup / closure-copy` 却没有真实验证切片，则默认优先交结果；
     - 对当前 `EMA / PSAR` 线，默认优先：
       1. `EMA 60m gross vs 20bps` rolling / walk-forward 小切片；
       2. 若仍偏大，则 `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m`
   - 这属于“只改执行约束，不改节奏/频率”的最小干预，方向上是对的。

4. **这轮还看不到足够的新结果来判断收紧是否已经生效**
   - 当前观察窗口还太短；
   - 因此这轮最稳妥的 bot2 行为，不是继续加码干预，而是先保持，让 bot3 按新约束跑 1~2 轮，再看它是否真正交出 EMA 结果页。

## 当前 weakest / should-fix-next

1. **当前最弱点依旧是 EMA 主线的“结果缺位”**
   - 这点没有变；
   - 区别只在于：现在已经从“口头提醒阶段”进入“已做最小 prompt 干预、等待执行验证阶段”。

2. **当前不该做的是过度连环干预**
   - 若刚收紧一次 prompt，就马上再继续叠限制，容易把 bot2 从路径校准器变成 bot3 的 micromanager；
   - 这不符合 brief 里“最小必要调整”的要求。

## 下一步优先级 Top 1~3

### Top 1. 观察 bot3 是否按新约束交出 `EMA 60m gross vs 20bps` rolling / walk-forward 第一刀结果

最值得继续：
- 不是再写更多协议；
- 而是看下一轮是否真的出现：
  - 窗口正收益占比
  - 坏窗口是否扎堆
  - `gross -> 20bps` 后存活窗口比例

为什么排第一：
- 因为这将直接验证上轮 prompt 收紧是否有效。

### Top 2. 若 rolling slice 仍偏大，则交 `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m` 的最小组合切片

最值得继续：
- 这是当前已经写死、且最自然的备选结果路径；
- 可直接回答 PSAR 的保护层价值是否足以覆盖成本。

为什么排第二：
- 因为它同样能让 `EMA / PSAR` 主线从协议层进入结果层。

### Top 3. breakout-v0 的正式组合级资金曲线 / sizing honesty

最值得继续：
- breakout 若继续推进，应直接进入更正式组合层；
- 但其项目级边际价值，目前仍低于把 EMA 主线拉进真实结果层。

## 本轮改动

### 1) 本轮不改 `docs/TODO.md`
- 理由：当前 TODO 的项目排序和 next step 已经足够贴近现状，当前瓶颈不在板子本身。

### 2) 本轮不改 `docs/ROADMAP.md`
- 理由：这轮问题仍是执行落地，不是大方向漂移。

### 3) 本轮不再追加第二次 prompt 干预
- 理由：上一轮刚完成最小收紧；
- 这轮更合理的是给它一个完整观察窗口，而不是连续叠加约束。

### 4) 延续上一轮已做改动（本轮确认继续有效）
- bot3 cron payload 已收紧为：
  - EMA 线默认优先交真实结果，不继续补 protocol / gate / cleanup / closure-copy；
- 文档版 `docs/AUTO_OPTIMIZATION_CRON_PROMPT.txt` 已同步到 13m 口径，并带同样约束。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **EMA / PSAR 页本轮不要再补任何“怎么验”段落**
   - 当前真的已经写够了；
   - 没有新结果前，再加只会重复。

2. **closure board 本轮不动是对的**
   - 顶层排序与 next-step 已够清晰；
   - 现在要看的不是表达是否更漂亮，而是 bot3 是否按新约束交付结果。

3. **breakout 页若还推进，应直接做更正式组合层，而不是继续 closure-copy**
   - 当前它的 first-pass realism 已经足够服务项目判断。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：本轮继续保持频率不变**
   - 上一轮已经做了最小 prompt 收紧；
   - 现在先不要在一个观察窗口里同时改 prompt 又改频率。

2. **bot2 下一轮的核心观察问题已经非常明确**
   - 只问一件事：
     - bot3 是否按新约束交出了 `EMA 60m` rolling slice 或最小组合切片？
   - 若有，则当前干预已足够；
   - 若仍无，则下一轮才考虑进一步加强约束。

3. **bot7 当前不用改**
   - 没看到它偏离当前三条收口线主线。

## 风险与不确定性

1. breakout-v0 仍只是 first-pass realism 足够，不等于已通过正式组合级验证。
2. EMA 主线当前仍未交出 rolling / combination 真实结果，因此上一轮 prompt 收紧是否足够，还需要接下来 1~2 轮观察。
3. 当前 worktree 依旧很脏，所以 bot2 这轮继续避免触碰更多主文档，以减少冲突与噪声。
