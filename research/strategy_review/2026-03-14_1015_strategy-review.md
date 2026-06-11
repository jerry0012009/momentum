# 2026-03-14 10:15 UTC · Light Strategy Review

## 本轮一句话判断

这轮继续不改 `TODO / roadmap / cron`。当前 closure-first 的三条收口线仍然没有出现新的方向漂移：`EMA / PSAR` 线继续稳定在 baseline/role-audit 口径，`breakout-short follow-up` 仍以 `avoid_fluctuating` 为更可执行的 first-pass gate，`Fibonacci` 仍应继续当收口说明对象；因此当前最值得继续的 3 件事不变：**EMA 成本/OOS honesty、breakout-v0 × avoid_fluctuating A/B、Fibonacci 最终定位页**。

## 当前 strongest evidence

1. **EMA / PSAR 线的排序与角色仍稳定**
   - 当前页面与最近 loop 仍支持：
     - `EMA = raw alpha baseline candidate`
     - `PSAR = fast reaction / loss-protection candidate`
   - 暂未看到需要改写这条结论的新证据。

2. **breakout-short follow-up 的执行口径仍稳定**
   - `support_breakout_v0_h24` 仍是 v3 留下的最小策略原型页；
   - 当前最可执行的环境约束仍是 `avoid_fluctuating`，不是 `only_downtrend`。

3. **closure board 总览页仍在正确服务“先收口再扩张”**
   - 它仍然把：
     - `EMA / PSAR`
     - `breakout-short follow-up`
     - `Fibonacci 收口说明`
     排成当前最该继续关注的三条线；
   - 没有再次把重心拉回泛化扩题或 reopen v3。

## 当前 weakest / should-not-do-now

1. **这轮不要继续动主文档**
   - 当前 worktree 仍然很脏，说明有在途修改；
   - 这时 bot2 的职责是减少编辑冲突，而不是再做一次“形式上的微调”。

2. **不要重新打开 v3 本体**
   - 当前仍应只引用 final verdict；
   - follow-up 的对象是 breakout-short 原型，不是整条 `V3X-*`。

3. **不要现在就把更多资源拨回外部 alpha scouting**
   - 当前三条收口线还没完成一轮更完整的成本 / OOS / 角色判断；
   - 现在就回拨，容易重新分散注意力。

## 建议优先级 Top 1~3

### Top 1. EMA baseline 的成本 / OOS honesty
- gross / low-cost / high-cost
- rolling / OOS honesty
- 明确 EMA 作为默认 baseline 的地位

### Top 2. breakout-v0 × avoid_fluctuating 的最小 A/B
- `trade_all` vs `avoid_fluctuating`
- 看 post-cost / sample retention / excess_ret / failure path

### Top 3. Fibonacci 的最终定位页
- 明确支持什么 / 不支持什么
- 明确不升 `factors/`
- 明确它只是 `optional filter / confirmation reference`

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
- 最近几轮方向判断完全一致；
- 当前更需要执行 closure work，而不是继续改规划文件。

本轮只新增这份轻量策略巡检记录，并发送简短邮件摘要。

## 网页/表达建议

1. **继续坚持“角色判断 > 新图表”**
2. **EMA / PSAR 线先补完整性，不急着再拆新页面**
3. **Fibonacci 继续补硬一点的 disclaimer**

## cron / 节奏建议

1. **bot3-auto-opt-15m：继续观察，不改**
2. **bot2-strategy-review-40m：继续保持轻量**
3. **bot7-quant-digest-4h：继续观察，不改**

## 风险与不确定性

1. `EMA` 仍只是 baseline candidate，不是 production-ready alpha。
2. `support_breakout_v0` 仍是策略化原型，不是完整资金曲线级回测。
3. `Fibonacci` 当前仍主要体现 filter / trade-off 价值，而不是收益翻正。
