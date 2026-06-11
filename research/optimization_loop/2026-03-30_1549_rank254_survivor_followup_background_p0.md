# Rank 254 / BTC confirmed jump / liquid-alt follower contagion — survivor follow-up exit (`background/P0`)

- Time: 2026-03-30 15:49 UTC
- Target: `Rank 254 / BTC confirmed jump / liquid-alt follower contagion`
- Action type: survivor follow-up (the only allowed follow-up)
- Artifact source: `reports/artifacts/rank254_survivor_followup_20260330/summary_by_variant.csv`, `run_meta.json`, `trade_log.csv`, `reports/site/factors/rank254_jump_follower_survivor_followup/report.html`

## What was executed

按 state 要求，只执行 Rank 254 那唯一一次 survivor follow-up，不改排班，不扩题：

- 事件锚固定为 `BTC 1m return >= 首 30 天样本 99.5% 分位` 且 `BTC volume >= 95% 分位`
- follower universe 固定为 `ETH/LTC/XRP/BCH/ETC`
- 执行口径强制 `next-bar open entry + no-overlap + 8 bps/side`
- 并排比较三条指定诚实版本：
  1. `negative-only`
  2. `13:00–17:00 UTC only`
  3. `beta-hedged follower spread`
- 同时保留 `unconditional_followthrough_baseline` 做对照，防止把泛 BTC beta 延续误读成 jump-specific edge

## What changed system belief

这条线的 frozen replication 已经把最关键的问题回答清楚：**jump 版 follower trade 在诚实成本下没有保住可升级的独立 edge；剩下的大部分表现更像 BTC beta 尾巴，而不是可独立进入前排的 event-pocket alpha。**

最关键的结果来自 `5m` 主持有窗（state 里明确要求给出口型结论）：

- `jump_baseline`: `22` 笔，`mean_net_ret = -13.94 bps/trade`
- `jump_negative_only`: `10` 笔，`mean_net_ret = -22.83 bps/trade`
- `jump_13_17_utc_only`: `7` 笔，`mean_net_ret = -28.88 bps/trade`
- `jump_beta_hedged_spread`: `22` 笔，`mean_net_ret = -7.08 bps/trade`
- `unconditional_followthrough_baseline`: `1839` 笔，`mean_net_ret = -16.43 bps/trade`

这组数说明：

1. **jump 触发并没有把 after-cost edge 稳定抬到无条件基线之上。** `jump_baseline` 虽然略好于无条件基线，但仍然显著为负，远达不到 survivor follow-up 后应给 `promote_P2` 的门槛。
2. **negative-only 没有救活它。** 论文里的负 jump 偏多，并没有转成本地可交易的 short-side 优势，反而更差。
3. **13:00–17:00 UTC gate 也没救活它。** trade count 缩到只剩 `7` 笔，但单笔净收益仍明显为负，说明时间门控没有把它变成高质量 pocket。
4. **beta-hedged 版本仍为负。** 这点最致命：一旦把 follower 对 BTC 的 beta 尾巴显式剥掉，剩余 spread 还是负的，说明这条线并没有保住“leader jump → follower 独立 catch-up alpha”这一核心主张。
5. `3m/15m` 持有窗也都没有出现正的、可升级的诚实版本；不是单一 holding choice 的问题。

## Exit decision

按照 policy，survivor 只有这一次 follow-up 预算；这次已经完成，而且没有得到足够支持 `promote_P2` 的证据，因此本轮必须收口，不再继续开放式补证。

正式结论：

- Verdict: `background/P0`
- Slot effect: 退出 `Surviving candidate slot`
- Why not P2: frozen replication 下所有指定诚实版本在成本后都未呈现可升级 edge，且 `beta-hedged follower spread` 仍为负，说明该对象目前更像 BTC beta 尾巴/事件追涨壳，而不是独立 raw alpha

## One-line result

`Rank 254 / BTC confirmed jump / liquid-alt follower contagion` 的唯一 survivor follow-up 已完成：Binance 1m public-data frozen replication 在 `next-bar + no-overlap + 8 bps/side` 下显示 `jump_baseline / negative-only / 13:00–17:00 UTC only / beta-hedged spread` 各版本的成本后收益均未达到可升级门槛，其中 `5m beta-hedged` 仍为负，说明 edge 主要是 BTC beta 尾巴而非独立 follower alpha；因此本轮用尽唯一 follow-up 后将其收口回 `background/P0`。
