# bot3 optimization loop — BTC-beta-neutral residual loser-bounce basket first verdict

- Time: 2026-04-18 01:58 UTC
- Target: `research/quant_digests/2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `background/P0`

## What was checked
按 `cycle_plan` 只做这一个最小 honesty / execution-realism 收口：检查该 repo 的 `BTC-beta-neutral residual loser-bounce basket` 在已给出的 `5m/15m` portability probe 下，是否仍能摆脱“仅在 ~2.4–2.9bps 超低 round-trip 摩擦下才成立”的薄成本幻想。

读取并采用现成 artifact：
- `jerry/momentum/reports/artifacts/quant_digests/2026-04-17_betaneutral_residual_reversal_probe_summary.json`
- `jerry/momentum/reports/artifacts/quant_digests/2026-04-17_betaneutral_residual_reversal_probe_summary.csv`

## Key evidence
### 15m best-net
- `beta_window=48`, `threshold_quantile=0.95`, `ema=24`
- `mean_gross_bps = +0.1321`
- `avg_turnover = 0.04583`
- 对应每 bar 成本拖累约 `8bps * 0.04583 = 0.3666bps`
- `mean_net_bps = -0.2345`
- implied break-even round-trip cost 约 `0.1321 / 0.04583 = 2.88bps`

### 5m best-net
- `beta_window=96`, `threshold_quantile=0.98`, `ema=36`
- `mean_gross_bps = +0.0348`
- `avg_turnover = 0.01448`
- 对应每 bar 成本拖累约 `8bps * 0.01448 = 0.1158bps`
- `mean_net_bps = -0.0810`
- implied break-even round-trip cost 约 `0.0348 / 0.01448 = 2.41bps`

## Why this changes the system view
这条线在短周期 transfer 后并非完全无信息，但当前可见 alpha 只够覆盖大约 `2.4–2.9bps` round-trip 成本；一旦放进统一 `8bps` 成本口径立即持续转负，而且当前 digest 没有给出更强的 execution shell（maker share、分腿同步、queue priority、滑点控制）来证明 desk 现实里能稳定压到这个阈值以下。

因此，本轮最小 honesty 检查已经足够回答前排问题：

> `BTC-beta-neutral residual loser-bounce basket` 仍只是“极薄摩擦口袋 + 更优执行想象”，不足以诚实支撑新的 fresh-intake front slot，直接收口 `background/P0`。

## Runtime impact
- 当前 fresh intake 对象完成 first verdict：`background/P0`
- 不分配新 `Rank`（因为未达到 `keep_P1`）
- fresh intake front slot 顺延到下一条具体对象：`research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`

## Reader-facing one-line result
`BTC-beta-neutral residual loser-bounce basket` 的 5m/15m portability probe 只留下 `~2.41–2.88bps` 的 break-even cost 薄阈值、且缺少能把真实 round-trip 稳定压到该门槛下的 execution 壳，因此本轮 fresh intake first verdict 直接收口 `background/P0`。
