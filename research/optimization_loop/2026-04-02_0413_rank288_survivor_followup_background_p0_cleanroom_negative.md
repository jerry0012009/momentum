# bot3 optimization loop — Rank 288 survivor follow-up exhausted → background/P0

- Time: 2026-04-02 04:13 UTC
- Item: `Rank 288 / US crypto ETF midday 30m momentum pocket`
- Outcome: `follow-up exhausted → background/P0`

## What this round executed

按 `cycle_plan`，本轮只执行 `Rank 288` 的唯一一次 survivor follow-up：

1. 用我们自己的 `Yahoo Finance 5m` clean-room 数据，重做 ETF 版本的 `11:00–11:30 ET signal -> 11:30–12:00 ET hold` regular-session midday momentum；
2. 再把 `IBIT+FBTC` vs `ETHA+FETH` 的 signal spread 映射到 `BTCUSDT vs ETHUSDT` 的 dollar-neutral pair，检查 `30/45/60m` hold 与 `0/1/2 bar` delay 下是否还能留下诚实 pocket。

## Clean-room setup

### A. ETF clean-room replication

- 数据源：`query1.finance.yahoo.com` `5m` bars（`includePrePost=false`）
- ETF universe：`IBIT / FBTC / ETHA / FETH`
- 样本：近 `60d` 可得 regular-session `5m` 样本
- 信号窗口：纽约时间 `11:00–11:30`
- 持有窗口：纽约时间 `11:30–12:00`
- 交易定义：按 `11:00–11:30` 收益做横截面排序，`long top 2 / short bottom 2`
- 结果口径：先看毛收益，再看 `10 bps` 与 `14 bps` 的 round-trip 成本壳

### B. BTC-vs-ETH crypto mapping

- signal：`spread_sig = mean(IBIT,FBTC 11:00–11:30 ret) - mean(ETHA,FETH 11:00–11:30 ret)`
- 执行标的：本地 `BTCUSDT_120d_5m.csv` 与 `ETHUSDT_120d_5m.csv`
- sizing：dollar-neutral pair
- direction：`spread_sig > 0 => long BTC / short ETH`；反之反向
- entry delay：`0 / 1 / 2` 根 `5m` bar（即 `11:30 / 11:35 / 11:40 ET`）
- hold：`30 / 45 / 60` 分钟
- 成本口径：先看毛收益，再看 `16 bps` round-trip pair 成本壳（双腿合计）

## Results

### 1) ETF clean-room 并未复现 notebook 所称的 midday momentum

近 `58` 个交易日上，四 ETF 横截面策略结果如下：

- 毛收益：约 `-4.1 bps/day`
- 毛 Sharpe：约 `-2.0`
- 加 `10 bps` round-trip 后：约 `-14.1 bps/day`, `SR -7.0`
- 加 `14 bps` round-trip 后：约 `-18.1 bps/day`, `SR -9.0`

也就是说，哪怕先不谈 crypto 映射，这条 `11:00–11:30 -> 11:30–12:00` 的 ETF 横截面 pocket 在我们自己的 clean-room 里就没有复现出正的 raw alpha。

### 2) 映射到 BTCUSDT vs ETHUSDT 后也没有留下可执行 pocket

`48` 个可对齐交易日上，`30/45/60m` 与 `0/1/2 bar` delay 的 pair 版本全部为负。代表性结果：

- `delay 0, hold 30m`：毛收益约 `-6.4 bps/day`；加 `16 bps` 成本后约 `-22.4 bps/day`
- `delay 0, hold 45m`：毛收益约 `-8.1 bps/day`；加 `16 bps` 成本后约 `-24.1 bps/day`
- `delay 0, hold 60m`：毛收益约 `-7.4 bps/day`；加 `16 bps` 成本后约 `-23.4 bps/day`
- `delay 2, hold 30m`：是最接近零的一档，但毛收益仍约 `-2.4 bps/day`；加成本后约 `-18.4 bps/day`

因此这条线不是“原始 ETF pocket 还行，只是 crypto 成本壳吃掉一部分”；而是 **ETF clean-room 本身就没复现，映射后也没有出现 rescue pocket**。

## Verdict

本轮新的系统认知是：

> `Rank 288 / US crypto ETF midday 30m momentum pocket` 在作者 notebook/source audit 层面看起来像一条独立 regular-session session component，但我们自己的 `Yahoo 5m` clean-room 复现未能重现其 ETF 横截面 raw alpha；进一步映射到 `BTCUSDT vs ETHUSDT` 的 `30/45/60m`、`0/1/2 bar delay` dollar-neutral pair 后也全线为负，因此这条 survivor 已用尽唯一 follow-up 预算，不升 `P2`，直接退回 `background/P0`。

## Runtime action taken

- `Surviving candidate slot`: cleared
- `Background pool`: parked `Rank 288`
- `cycle_plan[1]`: marked `done`

## Notes

这不是在说 notebook 一定错，而是说：

1. 在我们当前使用的公开 `Yahoo 5m` clean-room 路径下，midday pocket **没有以可迁移 raw alpha 的形式复现**；
2. 即使允许它作为 `BTC-vs-ETH` 外部 signal，现实 mapping 也没有留下正向 post-delay / post-cost 结果；
3. 因此这条线当前更诚实的结论不是继续 `keep_P1`，而是 **follow-up exhausted**。
