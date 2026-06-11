# Rankless / EMA20 pullback × swing-break continuation fresh intake -> background/P0

- Time: 2026-04-24 02:41 UTC
- Target: `research/quant_digests/2026-04-23_2036_ema20-pullback-swingbreak-continuation-alpha.md`
- Action: fresh intake first verdict
- Policy basis: only补 1 个最小 decisive blocker，判断它是否留下可独立排队的 after-cost continuation pocket，而不是只剩 trend-context / pullback gating 提示。

## What I checked
只读取该 digest 对应的本地 portability artifact：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/smart_money_bot_continuation_probe_2026-04-23.json`

## Key evidence
### 15m basket
- Aggregate: `n=578`, `gross_avg=+0.56bps/trade`, `net_avg=-7.44bps/trade`
- 8 个 liquid majors 中，只有 `SOLUSDT` 费后略正：`n=78`, `net_avg=+0.23bps/trade`, `cum_net=+17.84bps`
- 其余 `BTC/ETH/BNB/XRP/DOGE/ADA/LINK` 全部费后为负，范围约 `-4.52bps` 到 `-16.05bps/trade`

### 5m portability stress
- Aggregate: `n=573`, `net_avg=-7.95bps/trade`
- `SOLUSDT` 在 5m 也转负：`n=72`, `net_avg=-2.49bps/trade`
- 没有出现第二个 symbol 或第二个 timeframe 的稳健费后正 pocket

## Verdict
`EMA20 pullback × swing-break continuation` 的 fresh intake first verdict 诚实收口 `background/P0`：当前证据只剩 `SOL 15m` 单币、单切口、接近噪音级别的微弱 pocket，未形成“非单月份、非单 symbol lucky-run 之外仍成立”的 after-cost continuation alpha，因此不能进入 `keep_P1`；它更适合作为 trend-context / pullback gating 提示，不能作为独立 front-slot 候选继续排队。

## Runtime impact
- No rank assigned.
- No slot promotion.
- `cycle_plan` item 2 should be marked `done` with `background/P0` result.
