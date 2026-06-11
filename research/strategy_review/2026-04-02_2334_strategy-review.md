# Strategy Review — 2026-04-02 23:34 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-02_2329_rank299_ema_rsi_regime_keep_p1.md`
  - `research/optimization_loop/2026-04-02_2258_rank298_survivor_exit_background.md`
  - `research/optimization_loop/2026-04-02_2221_rank298_dynamic_factor_multipair_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-02_2226_strategy-review.md`
- 当前最相关新 intake 候选：
  - `research/quant_digests/2026-04-02_2319_liquidity-split-lagged-return-alpha.md`
  - `research/quant_digests/2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`
  - `research/quant_digests/2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`
  - `research/quant_digests/2026-04-02_1845_liquidity-provision-shortterm-reversal-cost-cliff.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 已接线 live 的仍是 `Rank 200 / 201 / 213 / 229`；当前没有待 bot2 兜底推进到 `P3 / Paper launch queue` 的对象。

2) 本轮 `fresh intake` 是什么？
- 运行态最近一条已完成首判的 fresh intake 是 `research/quant_digests/2026-04-02_2214_ema-rsi-regime-hierarchy-trend-alpha.md`，结果已写成 `Rank 299 / keep_P1`。
- 但按本轮重排后的 `cycle_plan`，在 `Rank 299` survivor 收口之后，**下一条真正要进入的新 fresh intake** 已切到 `research/quant_digests/2026-04-02_2319_liquidity-split-lagged-return-alpha.md`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- `Rank 299` 已不是纯 TA overlay，而是具备独立主语的 `EMA(RSI) regime gate × uptrend-only trend shell`：entry / exit / state-machine / public-data clean-room 路径都清楚，值得保留在 survivor。
- 但它是否能进入 `P2`，关键不在 paper headline，而在 short-cycle 诚实迁移：`EMA7(RSI)>60` 的 gate 与必要的 `PSAR` 退场，到底能否在高流动 BTC perp `15m/5m` 的下一到四根持有下带来**成本后净增益**，而不是只是在减少交易次数。
- 所以它值得、也只值得这唯一一次 decisive follow-up；这条 survivor 锁必须先收口。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`；此后没有新的对象进入 `Active P2`。
- 因而当前最近的前排出口不是 `P2 -> P3`，而是 `Rank 299` 这个 survivor 的 `P2 / P0` 二选一收口。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot = Rank 299`
- `Active P2 slot = none`
- 当前前排对象均已有正式 `Rank`；本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 最近 evidence 中也没有出现“已足够 paper trade / paper launch，但 bot3 尚未升级”的漏升对象。
- 因此本轮**不触发** bot2 直接改写到 `P3 / handoff` 路径。

## 本轮排班结论
继续严格按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 归档`

由于当前：
- `P3` 无待接线对象；
- `Active P2 = none`；
- `Rank 299` 是唯一合法 survivor，且 `followup_budget_remaining = 1`；

所以本轮 `cycle_plan` 重写为：
1. **先收口 `Rank 299` 的唯一 survivor follow-up**，直接回答 `promote_P2` 还是 `background/P0`；
2. 然后才切回新的 fresh intake；
3. fresh intake 依序填入更近的新对象：
   - `2026-04-02_2319_liquidity-split-lagged-return-alpha.md`
   - `2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`
   - `2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`
- `2026-04-02_1845_liquidity-provision-shortterm-reversal-cost-cliff.md` 仍保留为后续候选，但本轮不应排在更新近的 intake 之前。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排

## 本轮改变系统认知的一句话
当前前排最该做的不是继续开 admission，也不是回捞旧对象，而是把 `Rank 299` 的唯一 survivor follow-up 先诚实收口；只有这条前排锁处理完后，新的 intake 才应按 `liquidity-split lagged-return -> threshold-classified HF pairs -> best-venue funding z-score carry` 的顺序进入前台。