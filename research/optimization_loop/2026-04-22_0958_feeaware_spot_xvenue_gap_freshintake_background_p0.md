# bot3 auto — fee-aware spot cross-venue gap fresh intake first verdict

- 时间：2026-04-22 09:58 UTC
- 执行小点：cycle_plan #1
- 对象：`research/quant_digests/2026-04-22_0458_feeaware-spot-xvenue-gap-shell.md`
- verdict：`background/P0`

## 结论
`fee-aware same-symbol cross-venue spot gap × inventory/maker-first deployment shell` 的 fresh intake first verdict 已诚实收口 `background/P0`：本轮对 `BTC/ETH/SOL` 在 Binance / Coinbase / Kraken / Bitstamp 的公开 top-of-book 做最小 live 复核，表面 cross-venue crossed gap 多数仅约 `1.1–4.4bps`，不足以覆盖普通 taker/taker、稳定币/法币换算、hedge delay、top-of-book size 与 inventory preposition；因此它当前更像 XEMM / inventory-funded maker-first execution infrastructure hint，而不是值得前排保留的独立 after-cost alpha。

## 最小 decisive blocker
本轮只补一个 blocker：**主流同币跨所 spot gap 在统一成本与最小执行现实下是否还有足够厚度**。

### live quote sanity probe
- 采样：6 次，每次间隔约 4 秒。
- 标的：`BTC`, `ETH`, `SOL`。
- venue：Binance Spot / Coinbase Exchange / Kraken / Bitstamp（SOL 无 Bitstamp）。
- 口径：用每次样本中的最高 bid 与最低 ask 估算同币跨 venue 可见 crossed gap；这是乐观口径，尚未扣除：
  - taker fee / maker miss cost；
  - USD/USDT basis；
  - top-of-book size；
  - hedge delay / cancel latency；
  - inventory carry 与 rebalancing friction。

可见区间（bps）：
- `BTC`：约 `1.51–2.85bps`；
- `ETH`：约 `2.93–4.44bps`；
- `SOL`：约 `0.00–2.26bps`。

这说明 digest 里 `BTC` 约 `2–3bps` 的 sanity probe 不是孤例；更宽 venue 池和多标的下仍主要是低个位数 bps 的表面肉。这个厚度可以提示 ultra-low-fee inventory/maker-first XEMM，但不足以成为 bot2/bot3 前排 raw alpha：一旦用常规双边 taker 或任何保守 maker-miss / hedge-delay 折扣，净边际很容易归零或转负。

## 为什么不 keep_P1
`keep_P1` 需要证明至少两个非单一 venue / 时段支撑的新增 after-cost 价值。当前证据只证明：
1. law-of-one-price gap 确实可见；
2. gap 厚度主要落在低个位数 bps；
3. 可交易性高度依赖 fee tier、库存预铺、maker-first fill 与 quote freshness；
4. 本轮没有看到足以覆盖普通 execution realism 的独立 after-cost pocket。

因此本对象保留为 background 里的 execution/deployment hint，不占用 survivor / P2 / P3 槽位。

## runtime 写回
- `Fresh intake slot.latest_result` 更新为本 verdict。
- `cycle_plan #1.result` 写入该结论，`status=done`。
