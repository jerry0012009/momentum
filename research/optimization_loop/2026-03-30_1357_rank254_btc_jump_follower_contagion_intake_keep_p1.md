# Rank 254 / BTC confirmed jump / liquid-alt follower contagion — fresh intake first verdict (`keep_P1`)

- Time: 2026-03-30 13:57 UTC
- Target: `research/quant_digests/2026-03-30_1311_btc-jump-follower-contagion-alpha.md`
- Action type: fresh intake first verdict

## What was checked

只做这条 intake 的最小首判，不扩写新排班：复核 digest 里已经明确写出的 event anchor、follower universe、holding windows、成本骨架与相对当前池子的对象边界，回答它是否已经足够作为独立前排对象保留，还是只是已有 `BTC shock -> alt follow-through` 家族的换壳版本。

本轮直接依赖的已落地证据：

- 事件锚：`BTC confirmed jump`
- follower universe：`ETH / LTC / XRP / BCH / ETC`
- horizon：`1m / 3m / 5m / 15m` 同日内持有，不做隔夜 drift 读法
- time gate：优先 `13:00–17:00 UTC`，回避 `01:00–06:00 UTC`
- 成本口径：事件期 round-trip 先按 `12~20 bps` 压测
- 论文级结构证据：tick-by-tick jump contamination / co-jump / same-day effect / negative-jump asymmetry

## What changes system belief

这条线已经足够说明：**不是所有 BTC→alt 跟随都该并入常开 lead-lag 家族；`confirmed jump` 本身可以当成一个更稀疏、更事件化的 anchor，而 liquid majors 的 same-sign delayed catch-up 是可单独审理的 pocket。**

当前最关键的可保留信息：

1. **对象边界是清楚的。** 这里不是泛 volatility burst，也不是 generic market beta 延续，而是 `BTC confirmed jump -> ETH/LTC/XRP/BCH/ETC same-sign delayed follow-through`。
2. **与已有池子的差异是清楚的。**
   - 它不是 `BTC 5m shock -> alt basket delayed follow-through` 那种常开型 shock 阈值家族；
   - 也不是 `liquidity-ranked laggards` 那种靠低 trade-count 慢反应吃边的小币 pocket；
   - 更不是 `leader basket -> selected follower spread` 的相对价值对冲结构。
   它补的是 **稀疏 confirmed-jump 事件 -> liquid major followers 同向 catch-up** 这一条更窄但更干净的事件型 raw alpha 支线。
3. **执行骨架已经够完整，足以保留。** digest 已经把 event anchor、basket、next-bar/短窗执行、negative-side 优先、time-of-day gate 与保守事件滑点框架写清楚，不再只是 jump 风险统计解读。

## Why it does NOT go straight to P2

当前证据还不够诚实地直接升 `P2`，blocker 也很明确：

1. **还没有本地 frozen replication。** 目前主证据仍来自论文结构与转译，不是我们自己的 public-data costed event study。
2. **jump 定义尚未冻结。** digest 虽给了两个最小代理版（`1m return + volume` 与 `3m signed move / realized vol`），但还没验证不同 jump proxy 下结论是否稳。
3. **after-cost 还没在本地样本上回答。** 虽然成本框架已经给到 `12~20 bps`，但还没有同口径事件研究证明在这个 friction 下净后仍有边。
4. **当前还没回答“追的是 follower alpha 还是 BTC beta 尾巴”。** 下一轮需要明确比较 follower-only、beta-hedged、negative-only/time-gated 版本，防止把市场大冲击误读成独立 alpha。

因此，**它值得作为独立 raw alpha 候选保留，但当前最诚实的 first verdict 只能是 `keep_P1`，不能直接 `promote_P2`。**

## Formal verdict

- Assigned rank: `Rank 254`
- Verdict: `keep_P1`
- Slot effect: 进入 `Surviving candidate slot`
- Required next decisive follow-up: 做一次 public-data frozen replication，强制 `next-bar execution + no-overlap + 6~10 bps/side friction`，并把 `negative-only`、`13:00–17:00 UTC only` 与 `beta-hedged follower spread` 三个版本并排比较；若成本后仍优于无条件 follow-through 基线，则可升 `P2`，否则收口回 background。

## One-line result

`Rank 254 / BTC confirmed jump / liquid-alt follower contagion` 的 fresh intake 首判已完成：当前公开论文证据已经把 confirmed-jump 事件锚、`ETH/LTC/XRP/BCH/ETC` follower basket、`1m/3m/5m/15m` 持有窗与 `12~20 bps` 事件成本压测骨架讲清，这条线补的是“稀疏 BTC jump -> liquid majors 同向 catch-up”的事件 pocket，而不是泛化的 BTC→alt 常开 follow-through；但因仍缺 public-data 下的 frozen、costed replication，本轮按 `keep_P1` 收口并进入 survivor，不直接升 `P2`.
