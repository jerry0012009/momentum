# Rank 350 — BTC lead × low-liquidity alt lag first verdict: keep_P1

- Time: 2026-04-06 08:26 UTC
- Source target: `research/quant_digests/2026-04-06_0558_btc-lead-liquidity-lag-alt-alpha.md`
- Verdict: `keep_P1`
- Assigned Rank: `350`
- New level: `Surviving candidate slot`

## Why this changes runtime truth

`BTC leader -> low-liquidity alt delayed catch-up` is a distinct cross-market raw alpha shell with a clear short half-life boundary (`1m` primary, `3m` only as child aggregation) and an honest minimum executable skeleton (`BTC impulse gate + lagging alt bucket + fixed 1-bar/2-3 bar hold + explicit after-cost audit`), so it is not just a low-leverage restatement of generic `BTC move -> alt follows` market beta.

## Minimal decisive read

1. **Independent subject is clear**
   - The core subject is not “BTC matters.”
   - It is specifically: `BTC price discovery happens first`, while `low-trade-count alts absorb that information with delay`.
   - That makes this a leader-laggard / relative-value raw alpha family, not a regime filter.

2. **Half-life boundary is explicit enough for first verdict**
   - The digest’s portability probe already compresses the critical boundary:
     - `1m`: visible lag remains;
     - `3m`: mostly degraded into contemporaneous catch-up;
     - `5m/15m`: no longer honest as the native signal frequency.
   - That is enough to reject the vague “multi-horizon BTC spillover” reading and keep only the short-cycle shell.

3. **Execution shell is concrete, not just narrative**
   - Leader: `BTCUSDT`
   - Lagger universe: low-trade-count but still tradable alt bucket
   - Trigger: `BTC(t-1)` impulse plus `ALT` underreaction / low-trade-count confirmation
   - Exit: fixed short hold first, then only minimal extension
   - Cost framing: explicit after-cost accounting is already central, not an afterthought

4. **Why it is not yet P2**
   - The current evidence is still mostly paper + tiny portability probe.
   - It has not yet demonstrated transportable net edge under a current tradable bucket with explicit fill/cost realism.
   - So the honest first verdict is `keep_P1`, not direct `promote_P2`.

## Result sentence for runtime

`Rank 350`：`BTC lead × low-liquidity alt lag` 已压清为独立的 cross-market raw alpha——主语是 `BTC 先发现 + 低成交 alt 慢半拍补价`，且物理半衰期边界明确落在 `1m 主信号 / 3m 仅可做 child aggregation`，因此本轮 first verdict 给出 `keep_P1` 并进入唯一 survivor follow-up。
