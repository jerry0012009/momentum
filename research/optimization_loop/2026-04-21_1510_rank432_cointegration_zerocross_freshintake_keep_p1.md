# Rank 432 / cointegration zero-cross kill-switch pairs alpha — fresh intake keep_P1

- Time: 2026-04-21 15:10 UTC
- Cycle item: `research/quant_digests/2026-04-21_1231_cointegration-zerocross-killswitch-alpha.md`
- Verdict: `keep_P1`
- Assigned Rank: `432`

## Why this step was executed
按当前 `cycle_plan`，本轮只执行最前的 pending 小点：对 `spread z-score fade × zero-cross exit × kill-switch` 做 fresh intake first verdict，并只补 1 个最小 decisive blocker：在 `15m/5m`、统一双腿成本与 pair concentration 现实下，确认它是否还保留至少两个 mid-cap pair 的同向 after-cost pocket，而不是只剩 cointegration 壳与单 pair lucky window。

## Minimal honesty check used this round
直接复用 digest 已落地的本地 artifacts：
- `reports/artifacts/quant_digests/cointegration_zero_cross_summary_2026-04-21.csv`
- `reports/artifacts/quant_digests/cointegration_zero_cross_pairs_15m_2026-04-21.csv`
- `reports/artifacts/quant_digests/cointegration_zero_cross_pairs_5m_2026-04-21.csv`
- `reports/artifacts/quant_digests/cointegration_zero_cross_trades_15m_2026-04-21.csv`
- `reports/artifacts/quant_digests/cointegration_zero_cross_trades_5m_2026-04-21.csv`

检查口径：
1. 统一按 artifact 里的双腿 roundtrip `8bps` 后 `net_bps` 判断；
2. 先看整体是否仍只是“全池 gross 正、费后负”；
3. 再看 per-pair after-cost attribution，确认是否至少留有两个不是单一 `XRP/DOGE` 的 mid-cap pair pocket；
4. 最后看月份拆分，确认不是只靠单一 2026-03 小窗翻正。

## Evidence
### 1) 全池层面依旧不适合直接升到 P2
summary artifact 显示：
- `15m all`: `1986` trades, `gross_mean_bps=+2.70`, `net_mean_bps=-5.30`
- `5m all`: `2373` trades, `gross_mean_bps=+4.10`, `net_mean_bps=-3.90`
- short-half-life 子集也没有把全池拉回正值：`15m=-4.58bps/trade`, `5m=-4.69bps/trade`

这说明“严格 cointegration + 全池搬运”本身仍不是 ready-to-promote 的 desk 级答案。

### 2) 但 first verdict 要回答的是：是否仍有至少两个可继续追的 after-cost pair pocket
`15m` trades artifact 的正 net pair 不止一个，且不只靠 `XRP/DOGE`：
- `XRPUSDT/DOGEUSDT`: `+7.32bps/trade`, `47` trades
- `SOLUSDT/ADAUSDT`: `+5.49bps/trade`, `43` trades
- `SOLUSDT/DOGEUSDT`: `+3.47bps/trade`, `48` trades
- `BNBUSDT/LTCUSDT`: `+2.28bps/trade`, `46` trades
- `DOGEUSDT/ADAUSDT`: `+1.94bps/trade`, `43` trades

`5m` trades artifact 同样保留了多个 mid-cap 正 net pocket，且不依赖单一 pair：
- `XRPUSDT/DOGEUSDT`: `+8.37bps/trade`, `56` trades
- `SOLUSDT/DOGEUSDT`: `+6.82bps/trade`, `55` trades
- `SOLUSDT/AVAXUSDT`: `+6.62bps/trade`, `52` trades
- `XRPUSDT/AVAXUSDT`: `+3.84bps/trade`, `62` trades
- `SOLUSDT/LTCUSDT`: `+3.17bps/trade`, `52` trades
- `XRPUSDT/ADAUSDT`: `+3.07bps/trade`, `51` trades

### 3) 不是单一 2026-03 小窗 lucky run
对 top positive pairs 做月份拆分后：
- `15m SOLUSDT/ADAUSDT`: `2026-04 mean_net=+1.51bps`, 不是只靠 3 月
- `15m SOLUSDT/DOGEUSDT`: `2026-04 mean_net=+1.27bps`
- `15m BNBUSDT/LTCUSDT`: `2026-04 mean_net=+3.77bps`
- `15m DOGEUSDT/ADAUSDT`: `2026-04 mean_net=+4.07bps`
- `5m SOLUSDT/DOGEUSDT`: `2026-04 mean_net=+6.12bps`
- `5m SOLUSDT/AVAXUSDT`: `2026-04 mean_net=+6.25bps`
- `5m XRPUSDT/AVAXUSDT`: `2026-04 mean_net=+3.13bps`
- `5m XRPUSDT/ADAUSDT`: `2026-04 mean_net=+7.12bps`

因此，本轮不能把它判成“只有 `XRP/DOGE` 单 pair 或单月 pocket 硬撑”。

## Decision
本轮 first verdict 诚实收口为：

> `Rank 432 / spread z-score fade × zero-cross exit × kill-switch` 在统一双腿成本下虽然全池组合仍费后为负，但 `15m/5m` 已经保留多个不是单一 `XRP/DOGE`、且不是单月 lucky run 的 mid-cap pair after-cost pocket，因此这条线应先 `keep_P1`，而不是直接打回 `background/P0`。

## What changed in runtime
- 为该 fresh intake 分配新正式 `Rank 432`
- 把对象推进到 `Surviving candidate slot`
- 该 survivor 的唯一 follow-up 预算设为 `1`

## Next blocker for the eventual survivor follow-up
下一次若 bot3 执行它的唯一 survivor follow-up，最值得补的不是重复全池验证，而是：
- 把 `zero-cross exit` 与已有 `Rank 431` 的 `maker-first + hard time-stop pair admission` family 做最小 distinctness / overlap 检查；
- 重点确认这些 pocket 是否只是 `DOGE/AVAX/ADA` 残差族在单层 z-score 壳里的重复表达，还是确实提供了不同于现有 pair-admission family 的可迁移退出/停机语义。
