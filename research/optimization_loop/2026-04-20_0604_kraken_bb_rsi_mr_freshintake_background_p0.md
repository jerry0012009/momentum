# bot3 optimization loop log — 2026-04-20 06:04 UTC

## 执行小点
- target: `research/quant_digests/2026-04-19_2156_kraken-bb-rsi-montecarlo-mr-shell.md`
- action: fresh intake：对 `BB 下轨偏离 × RSI/vol/Monte Carlo confidence long MR shell` 做 first verdict，只补 1 条最小 blocker——README-heavy 证据压到可复算 `5m/15m` Binance/Kraken proxy 后，long-only mean reversion 是否能覆盖成本与 trend-day 接飞刀风险。

## 使用证据
- digest：`research/quant_digests/2026-04-19_2156_kraken-bb-rsi-montecarlo-mr-shell.md`
- probe summary：`reports/artifacts/quant_digests/2026-04-19_bb-rsi-meanreversion_probe_summary.json`
- supporting summaries：
  - `reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_15m_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_5m_summary.csv`

## 最小诚实检查
直接采用同日已落库的最小 portability / cost probe：
- `5m`：`trade_count=135`，`avg_gross_bps≈-0.56`，统一 `8bps` 后 `avg_net_bps≈-8.56`，`win_rate_net≈45.2%`
- `15m`：`trade_count=124`，`avg_gross_bps≈+1.21`，统一 `8bps` 后 `avg_net_bps≈-6.79`，`win_rate_net≈46.0%`

supporting summary 也显示，这条 BB-family MR 在更宽松的 all-signals 统计下虽然可在更长持有窗看到正 gross，但 TIME exit 仍占主导：
- `15m` hold `4/8/12` bars 的 `time_stop_rate≈88.7%/75.9%/63.4%`
- `5m` hold `6/12` bars 的 `time_stop_rate≈87.1%/72.1%`

这说明公开 shell 的表面边际主要依赖更长等待与未显式建模的更低摩擦，而不是一个已经被当前 desk 口径验证过的短周期、费后仍存活的独立 pocket。README 中强调的 `RSI / volatility / Monte Carlo confidence` 更像 admission / sizing 包装；在最小可复算 proxy 下，并没有把 long-only mean reversion 拉到可保留的 after-cost 水平。

## 结论
`BB 下轨偏离 × RSI/vol/Monte Carlo confidence long MR shell` 在 README-heavy 证据压到最小 `5m/15m` 可复算 proxy 后，没有保住可独立承接的 after-cost pocket：统一 `8bps` 下 `5m/15m` 平均单笔净收益约为 `-8.56bps / -6.79bps`，且 TIME exit 仍占主导，因此本轮 fresh intake 直接收口 `background/P0`。

## runtime writeback
- cycle_plan item 4 -> `done`
- verdict: `background/P0`
- no rank assigned（未达到 `keep_P1`）
