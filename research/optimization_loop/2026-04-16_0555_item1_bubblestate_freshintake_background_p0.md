# 2026-04-16 05:55 UTC — item1 `MA(12/48) trend-follow × bubble-state gate` fresh-intake first verdict

## 执行动作
- 对 `research/quant_digests/2026-04-16_0454_bubblestate-ma-cross-trend-alpha.md` 执行 first-verdict。
- 口径：统一 `t+2` 执行延迟 + 单边 `4/6/8 bps` 成本（round-trip `8/12/16 bps`），并拆分 `Asia/EU/US` 分时段。
- honesty/execution realism 最小核对：将信号触发与可成交时点强制对齐为 `t+2 close fill`，检查结论是否保真。

## 证据与产物
- 复算脚本输入：Binance USDⓈ-M `15m` 月包（`2025-01`~`2026-03`），标的 `BTC/ETH/XRP/LTC`。
- 新产物：`reports/artifacts/optimization_loop/2026-04-16_bubblestate_ma_t2_cost468_session_eval.json`

核心结果（等权跨标的 `net_bps/笔`）：
- cost4: `-1.67`
- cost6: `-5.67`
- cost8: `-9.67`

分时段（等权跨标的 `net_bps/笔`）：
- Asia: `-5.59 / -9.59 / -13.59`
- EU: `-5.19 / -9.19 / -13.19`
- US: `+5.76 / +1.76 / -2.24`

分资产摘要：
- `ETH` 在低成本档与部分分时段仍有正值，但到 cost8 已转负（all `-3.06`）。
- `BTC/XRP/LTC` 在 all 口径下三档均为负；仅有局部分时段正 pocket，跨资产不可复制。

honesty/execution realism（可承受单边摩擦上限，`gross/turnover`）：
- BTC `1.93bps`、ETH `6.47bps`、XRP `2.76bps`、LTC `1.51bps`。
- 结论：除 ETH 外其余主分支对摩擦预算过窄，且组合层面在统一 `t+2` 下未保留稳健费后 alpha。

## 本轮结论（first verdict）
`MA(12/48) trend-follow × bubble-state gate` 在统一 `t+2 + 4/6/8bps` 与 Asia/EU/US 口径下未形成跨资产可复制费后 pocket；本轮 fresh intake 直接收口为 `background/P0`（不进入 survivor，不分配 Rank）。
