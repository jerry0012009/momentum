# Rank 327 — survivor follow-up：threshold honesty × cost survival 收口到 background/P0

- 时间：2026-04-04 11:34 UTC
- 对象：`Rank 327 / Frost Asian-session MA deviation fade × ATR/trend veto × mean-target exit`
- 层级动作：`P1 survivor -> background/P0`
- 结论一句话：`Rank 327` 的唯一 survivor follow-up 已诚实收口：把阈值按注释意图放大后，这条 `15m` 亚洲时段单币均值回复壳并没有留下能在更诚实成本下清楚存活的 desk pocket；repo 当前紧阈值版本下 `BTC/ETH` 连 `4bps` round-trip 都扛不住，而注释意图版里 `ETH` 直接转负、`BTC` 也仍不足以过成本，因此本轮不升 `P2`，转入 `background/P0`。

## 本轮执行的唯一合法问题
state 已把这次 survivor 的唯一 follow-up 收敛成一句话：

> 修正“注释阈值 vs 实际代码阈值”后，这个 `15m` 单币亚洲时段均值回复壳是否还能在不依赖过低成本的前提下保留清楚、可迁移的 post-cost pocket？

这轮不再补第二个 survivor 检查，也不再横向扩写 fresh intake；只回答这个出口问题。

## 本轮最小诚实快检
我用 Kraken 公共 `15m` OHLC 对 `XBTUSD / ETHUSD` 做了一次最小 replay，对照两套阈值：

1. **repo 当前真实代码口径**
   - BTC：`min/max deviation = $5 / $100`，`max ATR = $60`
   - ETH：`min/max deviation = $0.5 / $10`，`max ATR = $6`
2. **按注释意图放大 10 倍的口径**
   - BTC：`min/max deviation = $50 / $1000`，`max ATR = $600`
   - ETH：`min/max deviation = $5 / $100`，`max ATR = $60`

统一口径：
- 只在 `00:00–05:30 UTC` 开新仓
- `20 x 15m` MA 偏离触发，`14-bar ATR` + `10-bar slope` 做 veto
- 下一根开盘入场
- `80%` mean-target exit + buffer stop + 最长 `16` 根持有
- 成本检查重点看 round-trip `4 / 8bps`

## 结果

### A) repo 当前紧阈值版本：仍没有离开超低成本就能站住的 pocket
- **XBTUSD**：`8` 笔，gross `+0.61bps`，`4bps` 后转负，`8bps` 更差
- **ETHUSD**：`14` 笔，gross `+29.90bps`，但 `4bps` 后同样转负，`8bps` 更差

翻成人话：

> repo 当前真实阈值下，它更像一条被过紧偏离阈值挤出来的超薄 demo，不是能在最小 desk 成本下独立站住的 `15m` 单币 sleeve。

### B) 按注释意图放大 10 倍后：honesty 没有把它救活，反而把 ETH pocket 直接打掉
- **XBTUSD**：`3` 笔，gross `+0.88bps`，仍无法覆盖 `4bps` 成本
- **ETHUSD**：`24` 笔，gross `-297.24bps`，不用算成本也已经显著为负

翻成人话：

> 一旦把阈值修回更接近 README / 注释暗示的大偏离口径，这条壳并没有出现“更少但更厚”的 post-cost pocket；相反，ETH lane 直接塌掉，BTC 也仍然太薄。

## 为什么这次不能升 P2
P2 admission 的默认门槛不是“看起来有点像 alpha”，而是至少要留下值得继续 admission 的最小 desk shell。

但 `Rank 327` 这次 follow-up 的结论更接近：

1. **threshold honesty 是真 blocker**：repo 注释与代码口径不一致，必须先纠偏；
2. **纠偏后没有出现更清楚、更厚的 lane**：尤其 ETH 直接转成明显负收益；
3. **repo 当前版本也不够厚**：`BTC/ETH` 在本轮最小 replay 里连 `4bps` round-trip 都扛不住；
4. **因此不存在“至少一块清楚可迁移的 post-cost pocket”**，不满足 survivor 升 `P2` 的 success criterion。

所以这一步不能写成 `keep_P1` 更不能勉强写成 `promote_P2`；唯一诚实动作就是用尽 survivor 预算，把它收口回 `background/P0`。

## Runtime impact
- `Surviving candidate slot` 释放，`Rank 327` 不再占据前排 survivor 锁定权
- `Background pool` 增加最新 parked 对象：`Rank 327 / Frost Asian-session MA deviation fade`
- 当前系统认知更新为：**这条材料更适合作为“单币均值回复 demo / context shell 备查证据”，而不是继续向 admission 推进的 front-slot raw alpha**

## Artifact summary
```json
{
  "repo_like_tight": {
    "XBTUSD": {"signals": 8, "gross_bps": 0.6074, "net_4bps": -0.003139, "net_8bps": -0.006339},
    "ETHUSD": {"signals": 14, "gross_bps": 29.9035, "net_4bps": -0.002610, "net_8bps": -0.008210}
  },
  "comment_intent_10x": {
    "XBTUSD": {"signals": 3, "gross_bps": 0.8761, "net_4bps": -0.001112, "net_8bps": -0.002312},
    "ETHUSD": {"signals": 24, "gross_bps": -297.2416, "net_4bps": -0.039324, "net_8bps": -0.048924}
  }
}
```
