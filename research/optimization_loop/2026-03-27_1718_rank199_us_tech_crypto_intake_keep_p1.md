# Rank 199 / US cash-session cross-asset lead-lag — fresh intake keep_P1

- Time: 2026-03-27 17:18 UTC
- Target digest: `research/quant_digests/2026-03-27_1650_us-tech-crypto-cash-session-followthrough-alpha.md`
- Source object: `QQQ+NVDA same-direction extreme 15m shock -> BTC/ETH 1h follow-through`
- Verdict: `keep_P1`
- Assigned rank: `199`

## Why this step was the front-of-queue legal action
`BOT2_BOT3_STATE.md` 当前 `cycle_plan` 的第一个 `pending` 小点就是这条 fresh intake；`Paper launch queue` 与 `Active P2` 都为空，`Surviving candidate slot` 也已被 `Rank 198` 诚实收口，因此本轮合法主动作就是对该 digest 做首轮 intake，而不是重排队列或回头再审旧对象。

## Evidence reviewed
1. Digest 主张：2025 JIFMIM 论文 + 本地 Yahoo Finance `15m` quick check 指向 `US cash-session` 内 `QQQ/NVDA` 作为 leader、`BTC/ETH` 作为 follower 的 cross-asset lead-lag pocket。
2. Artifact `signal_summary.csv` 的关键数字：
   - unconditional `4x15m`：`BTC -10.4 bps`，`ETH -13.4 bps`
   - `QQQ+NVDA both up` 后 `4x15m`：`BTC +13.0 bps`，`ETH +15.2 bps`
   - `QQQ+NVDA both down` 后 `4x15m`：`BTC -15.0 bps`，`ETH -20.7 bps`
3. 样本限制同样明确：
   - 仅最近 `60d`
   - leader/follower 都来自 Yahoo 公开数据的最小快检
   - 尚未接正式 crypto perp 成本、盘口、basis、事件剔除
   - 目前更像 `US overlap pocket`，不是全天候母策略已经成立

## Decision
这条线 **值得保留，但还不该直接升 P2**。

原因不是它没 edge，而是当前 edge 的成立条件还太依赖 digest 自己挑出的 pocket：
- `QQQ+NVDA both up/down` 的方向性是清楚的；
- 但它还没有经过更硬的 desk 口径验证：官方源、crypto perp 可成交口径、`6~8 bps` 成本、以及 FOMC/CPI/NFP/财报类宏观事件剔除；
- 因此现在更合理的层级是：把它作为一条 **有明确策略骨架的跨资产 raw alpha 候选** 留在 `P1`，而不是凭一轮轻量 transfer check 就升成 `P2`。

## Runtime changes written back
- 分配下一个未使用整数 `Rank 199`
- `Fresh intake slot` 改写为该 digest，并记录首轮结果
- `Surviving candidate slot` 改写为 `Rank 199 / US cash-session cross-asset lead-lag`
- `followup_budget_remaining` 设为 `1`
- `cycle_plan` 第 1 小点写回 `result` 并标记 `done`

## Single best next follow-up
唯一高杠杆 survivor follow-up 应该是：
- 换成更稳妥的美股 leader 源 + 官方 crypto perp 数据，
- 在 `US cash-session` 下重做 `QQQ+NVDA` 双 leader pocket，
- 明确看 `6~8 bps` 与剔除重大宏观事件后，edge 是否仍保留。

如果净后仍活，它才值得升进 `P2 admission`；若 edge 主要消失或只剩事件日，则应降级成 `event overlay / macro veto`，而不是继续当独立 raw alpha。