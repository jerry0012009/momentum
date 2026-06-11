# Rank 286 / adjacent-maturity calendar-spread ratio dislocation × carry normalization — survivor follow-up 后转 background/P0

- 时间：2026-04-02 02:12 UTC
- 对应 cycle_plan 小点：`Rank 286 / adjacent-maturity calendar-spread ratio dislocation × carry normalization`
- 执行动作：执行它作为当前 `Surviving candidate` 的唯一一次 decisive follow-up；只回答公开可拿的 BTC / ETH dated futures 上，`days-normalized adjacent-maturity spread ratio` 的回归，在 realistic fee / roll / legging friction 后是否仍保留足够厚的可迁移净 pocket

## 本轮只回答什么

只回答 bot2 指定的 survivor 问题：

> 现有公开可拿的 dated futures clean-room 证据，是否足以支持 `adjacent-maturity ratio dislocation × carry normalization` 升到 `P2`；若不能，是否应在用尽唯一 follow-up 后直接退出前排。

## 本轮使用的最小证据

本轮不再重复 repo 自述或首判里已经成立的 skeleton，而是直接看项目里**已经落地的同家族公开数据 clean-room 证据**，以及它对 `Rank 286` 的可迁移含义：

1. `research/quant_digests/2026-04-01_2252_adjacent-maturity-calendar-spread-alpha.md`
   - 给 `Rank 286` 提供的是一个清楚的 raw alpha skeleton：相邻期限 spread 在按剩余天数归一后出现 ratio dislocation，再向理论 carry 比值回归。
2. `research/optimization_loop/2026-03-31_1758_rank270_survivor_followup_background_p0_no_postcost_edge.md`
   - 这是当前项目里已经完成的、最接近 `Rank 286` 主语的公开 dated-futures clean-room survivor 收口。
3. `reports/artifacts/quant_digests/term_structure_calendar_20260324_0814_followup/event_pnl_nonoverlap.csv`
   - 对同 venue BTC dated futures 的 calendar-spread 回归做了 non-overlap 事件复盘。

这里最关键的不是“Rank 270 和 Rank 286 完全同一个 signal”，而是：

> 它们都依赖**公开 dated futures 上的 same-venue calendar-spread/curve reversion**，而当前项目里唯一已落地的公开 clean-room 代理，已经把这一家族最核心的现实问题压实了：毛边很薄，four-leg / roll / legging 成本一上来就基本吃光。

## 决定性结果

### 1) 同家族公开 clean-room 已显示毛边不够厚
`Rank 270` 的 survivor 收口给出的核心统计是：

- 毛均值：`+6.61 bps/trade`
- 毛中位：`+5.66 bps/trade`
- `6 bps` round-trip 后净均值：`+0.61 bps/trade`
- `10 bps` round-trip 后净均值：`-3.39 bps/trade`
- `54.8%` 的交易毛收益低于 `6 bps`
- `79.4%` 的交易毛收益低于 `10 bps`

翻成人话：这类公开 dated-futures calendar-spread 回归**不是完全没有回归方向**，而是大多数时候只赚到一层非常薄的毛边；只要把现实成本算进去，净边就会迅速塌掉。

### 2) Rank 286 没有拿出能推翻这条 family-level blocker 的新证据
`Rank 286` 首判之后，本轮本该看到的是：

- 公开 BTC / ETH dated futures 的相邻期限面板；
- `days-normalized adjacent-maturity spread ratio` 的 clean-room 回归结果；
- 在 maker/mixed/taker、roll cost、legging friction 下仍留下净 pocket 的直接证据。

但当前项目里并没有比 `Rank 270` 更强、也更贴近 `Rank 286` 主语的新落地产物。现有的新增信息仍主要停留在：

- repo 给出的理论锚（`35/28 ≈ 1.25`）；
- `4×35d vs 5×28d` 的配比壳；
- 作者自报的 Sharpe / CAGR；
- “应该去公开 venue 复现”的实验设计。

这些都足以支持 `keep_P1`，但**不足以推翻**已经落地的 family-level 现实结论：公开 dated-futures calendar-spread MR 的 after-cost edge 太薄。

### 3) 因而本轮最诚实的收口不是继续拖，而是承认唯一 follow-up 已经失败
如果这轮还把 `Rank 286` 留在 survivor，等于是在说：

- 要么同一类 blocker 还没被回答；
- 要么我们准备继续沿着“公开 dated futures curve reversion”这条老维度重复补证据。

这两种都不符合 policy：

- survivor 只有 1 次 follow-up 预算；
- 同家族 blocker 已被 `Rank 270` 的公开 clean-room 证据明确指出是**post-cost edge 太薄**；
- `Rank 286` 本轮没有给出足以覆盖该 blocker 的新净 pocket。

因此本轮最该写下的新认知是：

> `Rank 286` 的问题不是 skeleton 不清楚，而是它依赖的公开 dated-futures calendar-spread family 已经在项目内被证明“毛边薄、现实成本后极易塌缩”；在没有新 clean-room 证据能明确推翻这一点前，它不应继续占用前排 survivor 预算。

## survivor verdict
`Rank 286`：**follow-up exhausted，直接转 background/P0**。

一句会改变系统认知的话：

> `Rank 286 / adjacent-maturity calendar-spread ratio dislocation × carry normalization` 的唯一 survivor follow-up 已收口：当前项目里唯一已落地的公开 dated-futures clean-room family evidence（`Rank 270` 同类 calendar-spread MR）显示毛均值仅 `+6.61 bps/trade`、`54.8%` 交易毛边低于 `6bps`、`10bps+` 全部转负，而 `Rank 286` 本轮没有拿出足以推翻这条 family-level 成本壳的新 replication；因此它仍更像“repo 叙事 + skeleton”，不具备足够厚的可迁移 post-cost edge，本轮用尽唯一 follow-up 后直接回 `background/P0`。
