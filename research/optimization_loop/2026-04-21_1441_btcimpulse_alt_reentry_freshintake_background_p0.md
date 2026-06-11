# bot3 optimization loop — 2026-04-21 14:41 UTC

## 执行对象
- cycle item 2
- target: `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
- action: fresh intake first verdict

## 本轮最小 decisive blocker
检验 `BTC impulse × alt own-move confirmation / reentry × BTC-fail exits` 在 `15m`、统一成本与 symbol router 现实下，是否至少保留 **两个 liquid alts 的同向 after-cost continuation pocket**，且不是靠少数 lucky trades / 长时间拖仓撑住。

## 使用证据
- digest: `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
- artifact summary: `reports/artifacts/quant_digests/btc_led_alt_reentry_probe_summary_2026-04-21.json`
- artifact combo: `reports/artifacts/quant_digests/btc_led_alt_reentry_probe_combo_2026-04-21.json`

## 关键读数
### 组合层
- `15m ALL`: `669` trades, `avg_gross_bps=+1.36`, `avg_net_proxy_bps=-18.64`, `median_net_proxy_bps=-43.48`
- `5m ALL`: `455` trades, `avg_gross_bps=-12.78`, `avg_net_proxy_bps=-32.78`

### 15m 分币
- `AVAX`: `89` trades, `avg_gross_bps=+17.36`, `avg_net_proxy_bps=-2.64`, `median_net_proxy_bps=-48.35`
- `ETH`: `80` trades, `avg_gross_bps=+9.59`, `avg_net_proxy_bps=-10.41`, `median_net_proxy_bps=-32.07`
- `XRP`: `83` trades, `avg_gross_bps=+2.96`, `avg_net_proxy_bps=-17.04`
- `DOGE`: `85` trades, `avg_gross_bps=+1.00`, `avg_net_proxy_bps=-19.00`
- `SOL/BNB/LINK/ADA` 15m gross 本身已转负

### 出场结构
- `15m ALL` exits: `time_cap=344`, `take_profit=163`, `btc_exit=103`, `btc_panic=28`, `btc_exit_long=31`
- `time_cap` 占比约 `51.4%`，说明大量仓位不是靠事件 payoff 或 BTC-fail 快速兑现，而是被 8h timeout 被动清掉。

## 结论
`BTC impulse × alt own-move confirmation / reentry × BTC-fail exits` 的 fresh intake first verdict 已诚实收口：recent `15m` probe 虽显示 `AVAX/ETH` 保留一定 gross continuation 结构，但在统一 repo-style roundtrip `20bps` 成本下 `8` 个 liquid alts 没有留下至少两个同向为正的 after-cost pocket（最强 `AVAX` 仍约 `-2.64bps/trade`，`ETH` 约 `-10.41bps/trade`），且 `time_cap` 占比过半，说明收益兑现仍严重依赖长时间拖仓而不是可复制的短周期 payoff，因此本轮直接收口 `background/P0`，不进入 survivor。

## 对 runtime 的影响
- Fresh intake slot 更新为该对象已完成 first verdict 并转入 `background/P0`
- cycle_plan item 2 标记为 `done`
- Background pool 追加本次 parked 结论
