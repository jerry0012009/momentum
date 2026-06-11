# 2026-03-14 08:15 UTC · Light Strategy Review

## 本轮一句话判断

这轮不需要再改 TODO 或 cron。最近 1~2 轮自动化已经在正确地给三条收口线补“角色判断 / 路径表达”，方向是对的；当前最该继续的是：**EMA 做成本/OOS honesty，breakout-v0 做 `avoid_fluctuating` A/B，Fibonacci 做最终定位页。**

## 本轮 strongest evidence

1. **EMA / PSAR 线正在往更清楚的角色判断收口**
   - 最新 loop 已把 `PSAR` 明确写成 `fast reaction / loss-protection candidate`，没有把它误升成与 EMA 同级的主 alpha。
   - 这说明这条线的表达方向正在变得更诚实。

2. **breakout-short follow-up 的页面路径已经讲顺**
   - 最新 loop 已经把：
     - `v3 final verdict = 留下了什么`
     - `support_breakout_v0_h24 = 压成最小策略原型后长什么样`
     这层关系讲清楚；
   - 同时也把 `avoid_fluctuating` 明确成当前更可执行的 first-pass 环境约束，而不是 `only_downtrend`。

3. **closure board 入口现在已经足够有方向感**
   - 首页 + `alpha_closure_board` 当前都在服务“先判断下一步该做什么”，而不是继续堆页面。
   - 这对当前阶段是对的。

## 本轮 weakest / should-not-do-now

1. **这轮不要再改 TODO 排序**
   - 近两轮 bot3 已经在按 closure-first 补最该补的表达缺口；
   - 现在再去重排，很容易只是制造噪音。

2. **这轮不要 reopen v3**
   - `v3` 仍应继续当历史证据包；
   - 当前该做的是 breakout-short follow-up，而不是回到 `V3X-*`。

3. **这轮不要让 bot7 回到泛化扩 digest 池**
   - 目前它的 prompt 已经校准到服务三条收口线；
   - 先观察，不要频繁再改。

## 下一步优先级 Top 1~3

### Top 1. EMA baseline 的成本 / OOS honesty

最值得做：
- gross / low-cost / high-cost
- rolling / OOS honesty
- 让 EMA 真正成为后续比较别的结构/过滤层时的默认 baseline

为什么排第一：
- PSAR 的角色已经先讲清了；
- 现在更缺的是把 EMA 从“看起来像 baseline”推进到“经得起更诚实验证的 baseline candidate”。

### Top 2. breakout-v0 把 `avoid_fluctuating` 真带进原型 A/B

最值得做：
- `trade_all` vs `avoid_fluctuating`
- 看 post-cost / sample retention / excess_ret / failure path

为什么排第二：
- 页面表达已经就位；
- 现在该把这个口径真正推进到更接近策略层的一刀验证。

### Top 3. Fibonacci 做最终定位页

最值得做：
- 讲清它当前是 `optional filter / confirmation reference`
- 明确不升 `factors/`
- 明确当前不支持把它当独立 alpha

为什么排第三：
- 这条线的证据已经基本够了；
- 现在最缺的是一个不会被误读的收口表达。

## 本轮改动

- **这轮不改 TODO / roadmap / cron。**
- 原因：最近 40 分钟内自动化产出与当前 steering 一致，没有看到明显跑偏、重复劳动或表达冲突。
- 本轮只新增这份轻量策略巡检记录。

## 网页/表达建议

1. **继续沿“角色判断 > 新图表”这个顺序走**
   - 现在最值钱的不是再加图，而是每条收口线都明确：
     - 当前支持什么
     - 当前不支持什么
     - 下一步该做什么

2. **EMA / PSAR 这条线可以暂时少加新页面，多补同页完整性**
   - 已经有 focus 页；
   - 下一步更该补成本 / OOS，而不是再拆更多姐妹页。

3. **Fibonacci 最需要一个明确的“别过度解读”框**
   - 不然它依然容易被读成“还差一点就成主 alpha”。

## cron / 节奏建议

1. **bot3-auto-opt-15m：先保持**
   - 虽然频率从 40m 提到了 15m，但最近两轮产出仍是极小步、且方向正确；
   - 先观察，不急着再改。

2. **bot2-strategy-review-40m：保持**
   - 轻量校准比重型统揽更适合当前阶段；
   - 这轮就属于“无需再动手，只需确认方向正确”的典型场景。

3. **bot7-quant-digest-4h：继续观察，不再追加 prompt 改动**
   - 最近已经校准过；
   - 下一轮重点是看它会不会真的去服务 closure-first，而不是再改文案。

## 风险与不确定性

1. **EMA 仍只是 baseline candidate，不是 production-ready alpha。**
2. **breakout-v0 目前还是策略化原型，不是完整资金曲线级回测。**
3. **Fibonacci 的帮助更多体现在 filter / trade-off，而不是收益翻正。**
