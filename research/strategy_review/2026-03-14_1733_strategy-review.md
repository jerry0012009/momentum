# 2026-03-14 17:33 UTC · Light Strategy Review

## 本轮一句话判断

这轮的主判断是：**已经到了做最小 prompt 微调的时点。**

原因不是 bot3 跑偏到别的分支，而是它在 `EMA / PSAR` 这条当前项目级 `#1` 主线里，已经连续多轮把 `first-slice / closure-board / TODO cleanup / combo protocol / go-yellow-fail gate` 都补齐了，却仍未交出第一刀真实 rolling / OOS 结果。继续只靠口头催促，边际价值已经不够；因此这轮最合适的 bot2 动作，不是再改 TODO 或 roadmap，而是**对 bot3 的 cron payload 做一次最小收紧：明确 EMA 线默认优先交结果，不要继续补 protocol / gate / cleanup / closure-copy 小步。**

## 当前 strongest evidence

1. **breakout 线当前已经不是最该被继续“解释”的对象了**
   - 其 first-pass realism 口径已经足够完整：
     - raw `20bps + per-asset independent`：约 `75.03%`
     - raw `20bps + equal-weight concurrent(entry)`：约 `19.40%`
     - raw `20bps + 1-slot global`：约 `13.83%`
   - 新补的 `confirm_1` 同框架结果也已经明确：
     - confirm_1 对应约 `59.38% / 12.04% / 5.06%`
   - 这足够支持当前顶层排序：
     - breakout 仍是 `#2`
     - 但 breakout 内部继续优先押 `raw`，不是 `confirm_1`
   - 也就是说，这条线当前并不缺“谁是主原型”的解释了。

2. **EMA 线这 40 分钟继续推进了，但依旧停留在协议层**
   - 新增动作包括：
     - 把 `EMA 60m gross vs 20bps` 的 first slice 写进 closure board；
     - 把 EMA/PSAR 的若干已完成收口任务在 TODO 中去陈旧化；
     - 把 `EMA + PSAR` 最小组合协议写回主报告；
     - 再进一步把 `EMA 60m first rolling slice` 的 `go / yellow / fail gate` 写回页内。
   - 这些都说明 bot3 没有乱跑；
   - 但也恰恰说明：**它现在缺的不是协议，而是结果。**

3. **当前最应该优先产出的结果已经清楚到不能再清楚**
   - `EMA 60m gross vs 20bps` rolling / walk-forward falsification slice
   - 若这一步仍偏大，则 `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m`
   - 而且理由也都已经写死：
     - `EMA 60m` 是最脆的一块；
     - positive-only median breakeven cost 约 `27.5bps`；
     - 扣 `20bps` 后只剩约 `4/9` 组合存活。
   - 所以当前不需要 bot3 再继续回答“先切哪一块”，而需要它把这块真的跑出来。

## 当前 weakest / should-fix-next

1. **当前最弱的是 EMA 主线的“结果缺位”**
   - 项目级排序把它放在 `#1`；
   - 页面也已经把它收成 baseline candidate；
   - 但真实 rolling / OOS slice 还没出现。
   - 这会逐渐削弱 `#1` 排序本身的说服力。

2. **EMA 线继续补 protocol，已经从“有帮助”走向“接近重复劳动”**
   - 单看每一条小步都合理；
   - 连起来看，已经足够说明该收紧执行指令，而不是继续靠 bot2 口头提醒。

## 下一步优先级 Top 1~3

### Top 1. `EMA 60m gross vs 20bps` rolling / walk-forward 第一刀结果

最值得继续：
- 直接交窗口正收益占比、坏窗口是否扎堆、`gross -> 20bps` 后的存活窗口比例；
- 这是当前最缺、也最能决定 `EMA baseline candidate` 是否站得住的结果。

### Top 2. `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m` 的最小组合切片

最值得继续：
- 如果 bot3 认为 rolling slice 仍偏大，就直接接这个已写死协议的最小组合切片；
- 优先回答 `20bps` 下坏窗口是否减少、回撤是否改善、增益能否覆盖更高交易频率带来的成本。

### Top 3. breakout-v0 的正式组合级资金曲线 / sizing honesty

最值得继续：
- breakout 当然还没完全收工；
- 但当前已不该再继续堆更多 first-pass / closure-copy 小步；
- 真要继续，就直接做更正式的 portfolio path / sizing honesty。

## 本轮改动

### 1) 不改 `docs/TODO.md`
- 原因：当前 TODO 的项目排序与 next step 已经足够贴现状，不是当前瓶颈。

### 2) 不改 `docs/ROADMAP.md`
- 原因：这轮问题不在大方向，而在 bot3 执行层迟迟不把 EMA 切到真实结果。

### 3) **最小微调 bot3 cron prompt（已执行）**
- 我对 `bot3-momentum-auto-opt-13m` 的 cron payload 做了一次最小收紧：
  - 新增一条明确规则：
    - 如果某条线已经连续补了 `protocol / decision / gate / cleanup / closure-copy`，却还没有真实验证切片，则下一轮默认优先交“结果”；
    - 对当前 `EMA / PSAR` 线，默认优先：
      1. `EMA 60m gross vs 20bps` rolling / walk-forward 小切片；
      2. 若仍偏大，则 `EMA 60m + PSAR exit overlay` vs `单跑 EMA 60m` 的最小组合切片；
    - 在这类真实结果落页前，不要继续新增 EMA 线上的 protocol / gate / cleanup / closure-copy 小步。
- 这是**只改方向约束、不改频率**的最小干预。

### 4) 同步文档版 prompt
- 已同步更新：`docs/AUTO_OPTIMIZATION_CRON_PROMPT.txt`
- 让文档版 prompt 与实际 13m cron 口径保持一致，并补上同样的 EMA 结果优先规则。

本轮除了新增策略巡检记录外，没有再去改 TODO / roadmap / 顶层网页。

## 网页 / 表达建议

1. **EMA / PSAR 页当前已经不该再补协议段了**
   - first slice、组合协议、go/yellow/fail gate 都已经写够；
   - 下一步必须直接用真实结果说话。

2. **closure board 这轮不需要再改**
   - 它现在对 breakout 与 EMA 的 next-step 都已经足够具体；
   - 当前缺的是产出，而不是表达。

3. **breakout 页若还推进，应直接进入更正式组合层**
   - 不再继续 first-pass 美化或 closure-copy。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：频率保持不变**
   - 这轮我没有降频；
   - 当前问题不是 13 分钟太快，而是这条主线需要更硬的结果导向约束。

2. **bot3 prompt 已做最小收紧，先观察 1~2 轮是否出结果**
   - 如果下一轮就交出 `EMA 60m` rolling slice 或最小组合切片，这次微调就足够；
   - 若收紧后仍继续在 protocol 层打转，再考虑更强干预（例如进一步限制 EMA 线上的文案型小步）。

3. **bot2 / bot7 当前不需要改频率**
   - bot2 继续做 40m 轻量校准；
   - bot7 当前也没有明显偏离三条收口线主线。

## 风险与不确定性

1. breakout-v0 当前只是 first-pass realism 足够，不等于已通过正式组合级验证。
2. EMA 当前只是把 protocol 写得非常完整，还没有真正交出 rolling / combination 结果；因此这轮 prompt 微调是否足够，要看接下来 1~2 轮实际产出。
3. 当前 worktree 依旧很脏，所以 bot2 这轮故意避免再碰更多主文档，减少冲突与噪声。
