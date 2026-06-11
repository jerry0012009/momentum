# 2026-03-14 09:35 UTC · Light Strategy Review

## 本轮一句话判断

这轮仍然不需要改 `TODO / roadmap / cron`。当前三条收口线的方向继续一致：`EMA / PSAR` 线正在补角色与完整性、`breakout-short follow-up` 线正在把路径与 first-pass gate 讲顺、`Fibonacci` 仍应继续按收口说明处理；现在最该继续的还是 **EMA 成本/OOS honesty、breakout-v0 × avoid_fluctuating A/B、Fibonacci 最终定位页**。

## 当前 strongest evidence

1. **EMA / PSAR raw alpha focus**
   - `EMA / PSAR Raw Alpha Focus Report` 当前口径仍然稳定：
     - `EMA = raw alpha baseline candidate`
     - `PSAR = fast reaction / loss-protection candidate`
   - 当前没有出现新证据推翻这个排序。

2. **breakout-short follow-up**
   - 最近两轮 closure work 已把：
     - `v3 final verdict = 留下了什么`
     - `support_breakout_v0_h24 = 最小策略原型长什么样`
     这条路径讲顺；
   - 当前更可执行的 first-pass gate 仍是 `avoid_fluctuating`，不是 `only_downtrend`。

3. **closure board 入口仍然一致服务当前主线**
   - `alpha_closure_board` 仍在强调：
     - `EMA / PSAR` 与 `breakout-short follow-up` 是当前主资源对象；
     - `Fibonacci` 主要以收口说明为主；
     - 先补成本 / OOS / rolling / 角色判断，再决定是否回拨资源给外部 alpha scouting。

## 当前 weakest / should-not-do-now

1. **这轮不要再改主文档**
   - 当前 repo worktree 仍然很脏，存在大量进行中的修改；
   - 这时 bot2 再去动 `TODO` / 页面主文案，容易和 bot3 的在途改动冲突。

2. **不要 reopen `v3` 本体**
   - `v3` 仍应只作为历史证据包与 final verdict；
   - 当前该做的是 breakout-short follow-up，不是回到 `V3X-*`。

3. **不要让 bot7 重新泛化扩题**
   - 当前 prompt 仍已对齐 closure-first；
   - 现在更重要的是看它后续实际产出是否继续服务三条收口线。

## 建议优先级 Top 1~3

### Top 1. EMA baseline 的成本 / OOS honesty

最值得继续：
- gross / low-cost / high-cost
- rolling / OOS honesty
- 让 EMA 真正成为后续结构/过滤层比较时的默认 baseline

### Top 2. breakout-v0 × avoid_fluctuating 的最小 A/B

最值得继续：
- `trade_all` vs `avoid_fluctuating`
- 看 post-cost / sample retention / excess_ret / failure path

### Top 3. Fibonacci 的最终定位页

最值得继续：
- 明确它当前支持什么、不支持什么
- 明确不升 `factors/`
- 明确它更像 `optional filter / confirmation reference`

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
- 最近自动化方向仍正确；
- 当前更需要的是继续执行 closure work，而不是频繁重排。

本轮只新增这份轻量策略巡检记录。

## 网页/表达建议

1. **继续坚持“角色判断 > 新图表”**
   - 现在最值钱的不是继续堆图，而是让每条收口线更明确回答：
     - 当前支持什么
     - 当前不支持什么
     - 下一步先做什么

2. **EMA / PSAR 线先补完整性，不急着再拆新姐妹页**
   - 成本 / OOS / rolling 比继续拆新专题页更优先。

3. **Fibonacci 需要更硬的 disclaimer**
   - 建议继续补一句类似：`not promoted to factors; keep as optional confirmation/filter reference`。

## cron / 节奏建议

1. **bot3-auto-opt-15m：继续观察，不改**
   - 虽然频率高，但最近产出仍是极小步 closure work；
   - 暂时没有看到明显重复劳动或方向漂移。

2. **bot2-strategy-review-40m：继续保持轻量**
   - 当前阶段 bot2 最好的动作往往是“少干预、把下一步讲清楚”。

3. **bot7-quant-digest-4h：继续观察，不改**
   - 当前更重要的是看实际产出，而不是继续改 prompt 文案。

## 风险与不确定性

1. `EMA` 仍只是 baseline candidate，不是 production-ready alpha。
2. `support_breakout_v0` 仍是策略化原型，不是完整资金曲线级回测。
3. `Fibonacci` 当前仍主要体现 filter / trade-off 价值，而不是收益翻正。
