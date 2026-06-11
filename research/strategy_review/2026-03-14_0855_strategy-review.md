# 2026-03-14 08:55 UTC · Light Strategy Review

## 本轮一句话判断

这轮继续选择 **不改 TODO / roadmap / cron**。当前方向没有明显跑偏，反而正在把三条收口线补成更像“可决策页面”的状态；在 worktree 已经很脏、且 bot3 仍在活跃推进的情况下，最好的 bot2 动作是**不制造额外编辑冲突**，只给出更窄的下一步排序。

## 证据更新

1. **最近两条 optimization loop 仍在正确服务 closure-first**
   - `2026-03-14_0706_psar-role-framing.md`
     - 把 `PSAR` 正式压成 `fast reaction / loss-protection candidate`；
     - 这说明 `EMA / PSAR` 线正在从“谁看起来更好”进入“谁到底扮演什么角色”的更成熟阶段。
   - `2026-03-14_0626_breakout-v0-path-framing.md`
     - 把 `v3 final verdict -> support_breakout_v0` 的继承路径讲顺；
     - 并且明确 `avoid_fluctuating` 比 `only_downtrend` 更像当前 first-pass gate。

2. **closure 页面入口当前没有明显表达漂移**
   - `alpha_closure_board` 仍在强调：
     - `EMA / PSAR` 与 `breakout-short follow-up` 是当前主资源对象；
     - `Fibonacci` 以收口说明为主；
     - 当前最该补的是成本 / OOS / rolling / 角色判断，而不是继续堆新页面。
   - `support_breakout_v0_h24` 也已经清楚表达：
     - 它是 `v3 final verdict` 的后继原型页；
     - 当前只是策略化原型，不是完整 production 回测。

3. **cron 方向仍一致服务当前主线**
   - `bot3-momentum-auto-opt-15m`：仍然明确只做三条收口线的小步推进；
   - `bot7-quant-digest-4h`：prompt 仍然优先服务三条收口线；
   - `bot4-pytrendline-v3-30m`：仍然 disabled；
   - 因此当前没有看到需要再做 cron 层修正的信号。

## 下一步优先级 Top 1~3

### Top 1. EMA baseline 的成本 / OOS honesty

最值得继续：
- gross / low-cost / high-cost
- rolling / OOS honesty
- 明确 EMA 作为后续结构研究默认 baseline 的地位

为什么仍排第一：
- 现在 `PSAR` 的角色已经讲清了一半；
- 更稀缺的是把 `EMA` 从“目前最像 baseline”推进成“经更完整验证后仍可站住的 baseline candidate”。

### Top 2. breakout-v0 × avoid_fluctuating 的最小 A/B

最值得继续：
- `trade_all` vs `avoid_fluctuating`
- 看 post-cost / sample retention / excess_ret / failure path

为什么排第二：
- 页面表达层已经补好；
- 现在最自然的下一步就是把这个路径判断推进到更像策略层的最小验证，而不是继续写更多解释文案。

### Top 3. Fibonacci 的最终定位页

最值得继续：
- 明确写死它当前支持什么、不支持什么
- 明确不升 `factors/`
- 明确它更像 `optional filter / confirmation reference`

为什么排第三：
- 当前这条线的证据方向已经比较清楚；
- 最缺的是一个不会被误读成“差一点就成主 alpha”的收口页。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
1. 最近两轮自动化与当前 steering 一致；
2. 当前 repo worktree 很脏，存在大量进行中的修改；
3. 这时 bot2 再去改主文档，边际价值低，且更容易和 bot3 的在途改动冲突。

本轮只新增这份轻量巡检记录。

## 网页/表达建议

1. **继续坚持“角色判断 > 新图表”**
   - 当前最值钱的不是再多一张图，而是每条线都更明确地回答：
     - 当前支持什么
     - 当前不支持什么
     - 下一步先补什么

2. **EMA / PSAR 页面下一步要补完整性，不要急着再拆新姐妹页**
   - 成本 / OOS / rolling 比继续拆新专题页更优先。

3. **Fibonacci 页面应该加入更硬的 disclaimer**
   - 类似：`not promoted to factors` / `keep as optional confirmation/filter reference`
   - 避免后续读者再把它误读成 active alpha 线。

## cron / 节奏建议

1. **bot3-auto-opt-15m：继续观察，不改**
   - 虽然频率较高，但最近产出仍属于极小步 closure work；
   - 暂时没有看到它因为频率变高而开始重复劳动或明显跑偏。

2. **bot2-strategy-review-40m：继续保持轻量**
   - 这轮就是一个典型场景：方向正确时，最好的动作是减少干预，而不是每轮都“做点什么”。

3. **bot7-quant-digest-4h：继续观察，不改**
   - 当前更重要的是看它会不会实际产出服务三条收口线的 digest，而不是再次调整文案。

## 风险与不确定性

1. `EMA` 仍是 baseline candidate，不是 production-ready alpha。
2. `support_breakout_v0` 仍是策略化原型，不是完整资金曲线级回测。
3. `Fibonacci` 当前仍主要体现 filter / trade-off 价值，而不是收益翻正。
