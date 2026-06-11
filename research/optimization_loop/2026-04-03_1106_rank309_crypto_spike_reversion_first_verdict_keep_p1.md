# Rank 309 — crypto spike reversion × binary wrapper：fresh intake first verdict = keep_P1

- Time: 2026-04-03 11:06 UTC
- Target: `research/quant_digests/2026-04-03_0948_crypto-spike-reversion-binary-alpha.md`
- Intake type: fresh intake
- Assigned rank: `Rank 309`
- Verdict: `keep_P1`
- Source basis: digest + repo source re-check (`README.md`, `backend/services/strategies/crypto_spike_reversion.py`, `backend/services/strategies/reversion_helpers.py`)

## Why this intake survives the first cut
这条对象通过 first verdict，原因不是 repo 很大，而是它已经把一个可独立 desk 化的主语写得足够具体：

> `5m impulse overshoot -> short-cycle binary-probability reversion`

源码里已经具备最小可交易壳：
- 明确 entry trigger：`min_abs_move_5m = 1.8%`
- 明确 shape gate：`|move_5m| >= 0.55 * |move_30m|`
- 明确 regime cap：`|move_2h| <= 14%`
- 明确方向：spike up 反做 `NO`，spike down 反做 `YES`
- 明确成本/质量门槛：`min_edge_percent`、`min_confidence`、`min_liquidity_usd`、`max_entry_price`
- 明确 exit：`8% TP / 4% SL / 8m max hold`

因此它不是“prediction-market OS 平台故事”，也不只是 generic filter/overlay，而是一条已经可直接重建 baseline 的单资产、冲击驱动、短周期 mean-reversion raw alpha skeleton。

## Why it does not jump straight to P2
这轮还不该直接升 `P2`，因为目前证据仍主要停留在 **规则壳清楚**，还没完成 first decisive follow-up 去回答下面这件事：

- 这条 edge 到底是 **binary 容器特有的 quote/settlement pocket**，还是在更长样本、跨 BTC/ETH/SOL/XRP、且显式 taker/spread/slippage 成本下依旧保留可复现的 after-cost expectancy？

也就是说：
- 它已经明显强于 `background/P0`；
- 但还没强到现在就能诚实地说 admission-ready。

## System-changing result
`Rank 309` 已正式分配给 `5m spike reversion × 30m shape gate × 8m time-box`；该对象具备清楚的 shock-fade 主语、公开可复现数据路径和最小 entry/exit/cost 壳，因此 fresh intake first verdict = `keep_P1`，进入 `Surviving candidate slot` 等待那唯一一次 decisive follow-up。

## Next honest follow-up boundary
下一次且仅一次 survivor follow-up 应直接回答：
- 在更长样本、至少多资产分层与显式成本后，这条 edge 是否仍保留稳定的 post-cost expectancy；
- 若是，则可 `promote_P2`；
- 若不是，则直接回 `background/P0`。
