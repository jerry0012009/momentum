# Rank 271 / stablecoin discount → peer-parity reversion — survivor follow-up 后转 background/P0

- 时间：2026-03-31 19:02 UTC
- 对应 cycle_plan 小点：`Rank 271 / stablecoin discount → peer-parity reversion`
- 执行动作：执行它作为当前 `Surviving candidate` 的唯一一次 decisive follow-up；只回答在统一 single-anchor / peer-median anchor、统一 fee+spread 成本与统一 depeg veto 下，这条 stablecoin discount / parity MR 是否仍保留可迁移 post-cost edge，以及 direct stablecoin pair 与 same-underlier multi-quote spread 哪条更值得升 `P2`

## 本轮只回答什么
只回答 bot2 指定的 survivor 问题：

> 现有 clean-room replication 证据，是否足以支持 `fiat-backed stablecoin secondary-market discount / peer-parity reversion` 在统一 anchor、统一成本与 depeg veto 下升到 `P2`；若不能，是否应在用尽唯一 follow-up 后直接退出前排。

## 本轮使用的最小证据
本轮没有再去扩写大而全回测，而是用一份最小、统一口径的 Binance 公共数据快检直接做 survivor 决策：

- 产物目录：`reports/artifacts/rank271_survivor_followup_20260331_1902/`
- 抓数口径：
  - direct stablecoin pair：`USDCUSDT / FDUSDUSDT / TUSDUSDT`，最近 `45d`，`5m`
  - same-underlier multi-quote：`BTCUSDT/BTCUSDC/BTCFDUSD` 与 `ETHUSDT/ETHUSDC/ETHFDUSD`，最近 `45d`，`15m`
- 统一设定：
  - `single-anchor`：相对 `USDT = 1.0`
  - `peer-median anchor`：相对 `{USDT=1.0, 其余两条 stablecoin/USDT}` 的中位数
  - `depeg veto`：若任一 stablecoin/USDT 偏离 `1.0` 超过 `50 bps`，则禁止新事件入场
  - `cost`：统一按 `2 bps / fill`
    - direct pair round-trip = `4 bps`
    - same-underlier quote spread 四腿 round-trip = `8 bps`
  - 事件定义：discount 超过 `3 / 5 / 8 bps` 阈值时入场；回收 `60%` 折价或 `3h timeout` 离场

## 决定性结果
### 1) direct stablecoin pair：概念存在，但统一成本后仍不够厚
按 6 条 direct 系列（`3` 个 stablecoin × `single-anchor / peer-median`）汇总：

- `3 bps` 触发：`387` 笔，平均毛收益 `+1.24 bps/trade`，平均净收益 `-2.76 bps/trade`
- `5 bps` 触发：`227` 笔，平均毛收益 `+0.85 bps/trade`，平均净收益 `-3.15 bps/trade`
- `8 bps` 触发：`145` 笔，平均毛收益 `+0.52 bps/trade`，平均净收益 `-3.48 bps/trade`

最接近可做的 pocket 不是 `FDUSD` 或 `TUSD`，而是更稀疏的 `USDC peer-median`：

- `USDC_peer_median @ 8bps`：最近 `45d` 只有 `6` 笔事件
- 平均毛收益 `+3.84 bps/trade`
- 在 direct pair 统一 round-trip `4 bps` 下，平均净收益仍约 `-0.16 bps/trade`

这说明 direct pair 的 discount / parity 回归并不是完全不存在；但在统一 `2bps/fill` 的诚实成本下，最好的 pocket 也只是“接近打平”，还没有厚到能作为可迁移 `P2` admission skeleton。

### 2) same-underlier multi-quote spread：比 direct pair 更弱，离成本线更远
按 4 条 same-underlier 系列（`BTC/ETH × USDC/FDUSD vs USDT`）汇总：

- `3 bps` 触发：`306` 笔，平均毛收益 `+1.72 bps/trade`，平均净收益 `-6.28 bps/trade`
- `5 bps` 触发：`243` 笔，平均毛收益 `+1.86 bps/trade`，平均净收益 `-6.14 bps/trade`
- `8 bps` 触发：`135` 笔，平均毛收益 `+1.64 bps/trade`，平均净收益 `-6.36 bps/trade`

这里的最好单口径是：

- `ETH_FDUSD_vs_USDT @ 5bps`：`132` 笔，平均毛收益 `+2.01 bps/trade`

但它对应的是四腿 round-trip 成本 `8 bps`，离可迁移净边仍差一大截；换句话说，same-underlier multi-quote spread 目前更像“能看见 quote-side 折价影子”，但还远不足以变成统一成本下可执行的 admission path。

### 3) depeg veto 在这个样本里基本未触发，说明问题不是被极端事件污染，而是常态 pocket 本身太薄
这轮 `45d` Binance 样本里，按 `50 bps` depeg veto，direct 与 same-underlier 两条路径的 `vetoed_entries` 都是 `0`。

因此这次 survivor 轮最该收口的话不是“先怪 depeg 扰动”，而是：

> **在没有明显 depeg shock 的常态样本里，discount/parity MR 的可观测回归幅度本身就偏薄；direct pair 最好的 pocket 也只是接近 4bps 成本线，same-underlier 则明显更弱。**

## survivor verdict
`Rank 271`：**用尽唯一 follow-up 后，不升 `P2`，直接转 `background/P0`**。

一句会改变系统认知的话：

> `Rank 271 / stablecoin discount → peer-parity reversion` 的唯一 survivor follow-up 已完成：统一 Binance public-data clean-room probe 显示，direct stablecoin pair 在 `single-anchor / peer-median anchor` 下虽能看到回锚，但最近 `45d` 最强 pocket 也只到 `USDC peer-median @ 8bps` 的 `+3.84 gross bps/trade`、在统一 `2bps/fill` 成本后仍约 `-0.16 net bps/trade`；same-underlier multi-quote spread 更弱，aggregate 仅 `+1.64~1.86 gross bps/trade`，远低于四腿成本线，因此这条 stablecoin discount / parity MR 目前不具备足够厚的可迁移 post-cost edge，本轮用尽唯一 follow-up 后直接回 `background/P0`。

## runtime write-back
- `Surviving candidate slot.current_target` → `none`
- `Surviving candidate slot.followup_budget_remaining` → `0`
- `Surviving candidate slot.latest_result` → 写为 `Rank 271` 已用尽 survivor follow-up，因统一成本下 post-cost edge 不够厚而不升 `P2`
- `Background pool.latest_parked` → 写为 `Rank 271` 回 `background/P0`
- `cycle_plan` 第 1 项：
  - `result` = `Rank 271 / stablecoin discount → peer-parity reversion` 的唯一 survivor follow-up 已完成：统一 Binance public-data clean-room probe 显示，direct stablecoin pair 在 `single-anchor / peer-median anchor` 下虽能看到回锚，但最近 `45d` 最强 pocket 也只到 `USDC peer-median @ 8bps` 的 `+3.84 gross bps/trade`、在统一 `2bps/fill` 成本后仍约 `-0.16 net bps/trade`；same-underlier multi-quote spread 更弱，aggregate 仅 `+1.64~1.86 gross bps/trade`，远低于四腿成本线，因此这条 stablecoin discount / parity MR 目前不具备足够厚的可迁移 post-cost edge，本轮用尽唯一 follow-up 后直接回 `background/P0`。
  - `status` = `done`
