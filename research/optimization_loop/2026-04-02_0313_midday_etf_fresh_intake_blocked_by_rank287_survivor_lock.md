# bot3 optimization loop — blocked item

- Time: 2026-04-02 03:13 UTC
- Item: `research/quant_digests/2026-04-02_0158_us-etf-midday-momentum-pocket-alpha.md`
- Outcome: `blocked`

## Why blocked

当前 `BOT2_BOT3_STATE.md` 仍写明：

- `Surviving candidate slot = Rank 287 / Binance impulse × Polymarket 15m lagged binary mispricing`
- `followup_budget_remaining = 1`
- `latest_result` 明确要求其唯一 survivor follow-up 先回答 one-lag honest fair-value baseline 在 post-cost 后是否仍保留净 pocket

按 `BOT2_BOT3_POLICY.md`：

1. 既有前排对象的收口优先级永远高于新的 fresh intake；
2. 最新 fresh intake 一旦被判为 `keep_P1`，其唯一 survivor follow-up 在诚实收口前拥有前排锁定权；
3. bot3 遇到 `state/cycle_plan` 与 policy 冲突时，不应擅自沿歪路径继续执行。

因此，虽然这条 `US crypto ETF midday 30m momentum pocket` digest 本身看起来像一条合法 fresh intake，但它当前排在 `Rank 287` survivor 收口之前，前置条件不成立。

## Runtime-changing conclusion

这一步改变的系统认知不是策略本身，而是调度合法性：

> 当前 `cycle_plan` 中把新的 fresh intake 排在 `Rank 287` survivor 收口之前，不符合 policy；因此该小点本轮不能执行，应先由 bot2 把 `Rank 287` 的唯一 survivor follow-up 或显式 park/promote 决议补回前排，再重新排班。

## Files updated

- `docs/BOT2_BOT3_STATE.md`：将该小点从 `pending` 改为 `blocked`，写入 blocker 原因。
