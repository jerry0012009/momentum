# 2026-04-21 15:56 UTC — BB+RSI bracket mean reversion fresh intake 收口 background/P0

## 执行对象
- cycle item 2
- target: `research/quant_digests/2026-04-21_1348_bbrsi-bracket-meanreversion-shell.md`
- action: fresh intake first verdict

## 本轮只回答的 decisive blocker
在统一 `8bps` round-trip 成本与 symbol concentration 现实下，这条 `BB20 touch + RSI14 extreme mean reversion × 2%/4% bracket exits` 是否留下了不是 `SOL/DOGE/BTC` 少数 pocket 硬撑的 after-cost MR sleeve。

## 读取到的最小证据
来源：`reports/artifacts/quant_digests/2026-04-21_patrick_meanreversion_probe_summary.csv`

### 15m symbol 摘要（mean_net_bps_8rt）
- `BTC`: `+5.14bps/trade` (`21` trades)
- `ETH`: `-34.32bps/trade`
- `SOL`: `+43.48bps/trade` (`29` trades)
- `XRP`: `-126.63bps/trade`
- `DOGE`: `+51.56bps/trade` (`26` trades)
- `ADA`: `-88.05bps/trade`
- `AVAX`: `-27.02bps/trade`
- `LINK`: `-15.15bps/trade`

### 5m symbol 摘要（mean_net_bps_8rt）
- `BTC`: `+1.26bps/trade` (`25` trades)
- `ETH`: `-33.72bps/trade`
- `SOL`: `-7.54bps/trade`
- `XRP`: `+14.92bps/trade` (`25` trades)
- `DOGE`: `-45.58bps/trade`
- `ADA`: `-91.80bps/trade`
- `AVAX`: `-19.17bps/trade`
- `LINK`: `-35.24bps/trade`

## 结论为什么直接收口
1. **全池并没有保住 after-cost sleeve**：
   - digest 已给出 `15m` 全池约 `-20.22bps/笔`
   - `5m` 全池约 `-26.60bps/笔`
2. **表面正 pocket 明显集中在少数 symbol**：
   - `15m` 基本只剩 `SOL / DOGE / BTC`
   - `5m` 只剩 `BTC / XRP`
   - 这不满足“不是 `SOL/DOGE/BTC` 少数 pocket 硬撑”的 front-slot 要求
3. **兑现质量不理想，说明策略壳更像 baseline 而非可直接前排保留的 raw alpha**：
   - 例如 `5m BTC` 的 `take_profit_rate` 仅 `4%`，`reversal_rate` `56%`
   - 多个 symbol 的 `mean_hold_bars` 在 `100~200` bars 左右，说明收益兑现依赖长持仓与反向信号兜底，而不是清晰、快速、可复制的 short-cycle MR pocket
4. **正 pocket 分布不够广**：
   - 除 `BTC` 外，`15m` 与 `5m` 的正 symbol 并没有形成稳定交集
   - `ETH/ADA/AVAX/LINK` 在两个周期都明显拖累，说明策略并非“多数币可做，只需小修”

## 本轮 verdict
`BB20 touch + RSI14 extreme mean reversion × 2%/4% bracket exits` 的 fresh intake first verdict 已诚实收口：统一 `8bps` 成本下全池 `15m/5m` 都为负，表面正 pocket 主要压在 `15m SOL/DOGE/BTC` 与 `5m BTC/XRP` 这几个少数 symbol，且平均持仓很长、TP 命中并非主要来源，未通过“recent 样本至少两个非 SOL/DOGE/BTC 少数 pocket 且不靠少数好日子硬撑”的 decisive blocker，因此本轮直接收口 `background/P0`。

## runtime 回写
- `cycle_plan` item 2 -> `done`
- `Fresh intake slot.latest_result` 已更新为本轮 verdict
- `Background pool.latest_parked` 已追加本轮收口

## 后续备注
这条线保留为 **selective MR baseline shell** 参考即可；若未来人工 reopen，更合理的方向是把它当作 `symbol router / trend veto / timeout / maker-first execution` 的母壳，而不是当前直接保留为前排对象。
