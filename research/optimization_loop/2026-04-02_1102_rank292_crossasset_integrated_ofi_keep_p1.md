# Rank 292 cross-asset integrated OFI fresh intake -> keep_P1

- Time: `2026-04-02 11:02 UTC`
- Target: `research/quant_digests/2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`
- Action: `fresh intake first verdict`
- Verdict: `keep_P1`
- Assigned Rank: `292`

## Why this was the next legal move
- Per current `BOT2_BOT3_STATE.md`, the first pending `cycle_plan` item is this fresh-intake digest.
- There is no active `Paper launch queue` target, no `Active P2`, and the previous survivor (`Rank 291`) has already been honestly closed back to background.
- So the only legal action this round is to give this object a first verdict and, if it survives as `keep_P1` or above, assign a formal rank before ending the turn.

## What changed system cognition
`leader integrated OFI × follower 1m/3m continuation` is distinct enough to survive as a front-slot hypothesis: it names a concrete mother-object — cross-asset order-flow lead-lag, not single-asset OBI, not ordinary pairs mean reversion — and it already specifies a minimally auditable clean-room path with identifiable leader/follower legs, short holding horizons, cost ladder, and best-level vs integrated OFI ablations.

## Why it deserves keep_P1
1. **The alpha mother-object is concrete and distinct.**
   - The digest is not just saying “order book imbalance matters.”
   - It makes a narrower claim: `leader coin lagged integrated OFI` predicts `follower coin next 1m/3m/5m return`.
   - That is a real front-slot hypothesis with explicit leader/follower structure (`BTC -> ETH`, `BTC -> SOL`, `ETH -> SOL`, `ETH -> BNB`).

2. **The feature definition and transfer path are already specific enough to audit.**
   - Feature body is spelled out as `best-level OFI`, `multi-level OFI`, `integrated OFI`, optional `microprice gap`.
   - The intended tests are also concrete: `leader return only` vs `best-level OFI` vs `integrated OFI` vs `integrated OFI + microprice`.
   - Execution horizons are bounded to `1m / 3m / 5m`, which matches the short-decay claim rather than pretending this is a slow 15m edge.

3. **It includes a real clean-room path, not only a concept stack.**
   - The digest names a minimal public-data route (`Binance aggTrades / bookTicker / depth snapshot`, 4-coin universe, simple linear or threshold tests).
   - Entry / exit / risk are crude but explicit enough to support one cheap decisive follow-up.
   - That is enough for `P1` survival.

## Why it does not jump straight to P2
1. **The evidence is still paper-first plus scaffold-first, not existence-check-first.**
   - The core support comes from academic claims and repo code structure.
   - There is not yet a direct desk-local existence check showing this survives even a toy after-cost screen in crypto.

2. **Crypto transfer realism is still assumed, not demonstrated.**
   - The papers are equity / Nasdaq oriented.
   - The digest gives a plausible crypto port, but it has not yet shown whether the lag survives public-data sampling, fee drag, and leader/follower decoupling in the actual crypto universe.

3. **The next question is very clear and cheap.**
   - The unique survivor follow-up should be a narrow existence check: does `leader integrated OFI` beat `leader return only` on a minimal BTC/ETH/SOL/BNB public-data setup after a simple cost ladder?
   - Because there is one obvious decisive follow-up, this belongs in `P1`, not yet `P2`.

## Honest takeaway
This object is more than a generic microstructure story and deserves a durable identity. But the honest posture is still `keep_P1`: the idea is clear, the feature stack is auditable, and the cheapest next blocker is obvious — yet the crypto-specific edge has not been demonstrated enough to occupy `Active P2`.

## Result line for runtime
`Rank 292`：`leader integrated OFI × follower 1m/3m continuation` 已具备可独立审计的 leader/follower 主语、feature 定义、短周期交易时钟与最小 clean-room path，因此 fresh intake 首判为 `keep_P1`，进入 survivor 槽位等待那唯一一次存在性 follow-up。
