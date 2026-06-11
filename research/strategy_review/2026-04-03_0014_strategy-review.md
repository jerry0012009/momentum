# Strategy Review — 2026-04-03 00:14 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_0003_rank299_survivor_exit_background.md`
  - `research/optimization_loop/2026-04-02_2329_rank299_ema_rsi_regime_keep_p1.md`
  - `research/optimization_loop/2026-04-02_2258_rank298_survivor_exit_background.md`
  - `research/optimization_loop/2026-04-02_2221_rank298_dynamic_factor_multipair_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-02_2334_strategy-review.md`
- 当前最相关新 intake 候选：
  - `research/quant_digests/2026-04-02_2319_liquidity-split-lagged-return-alpha.md`
  - `research/quant_digests/2026-04-02_2356_bb-zscore-rsi-trendveto-meanreversion-alpha.md`
  - `research/quant_digests/2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`
  - `research/quant_digests/2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有等待 bot2 兜底推进的 `P3 / Paper launch queue` 新对象。

2) 本轮 `fresh intake` 是什么？
- 本轮 fresh intake 头已切到 `research/quant_digests/2026-04-02_2319_liquidity-split-lagged-return-alpha.md`。
- 它的核心问题不是“再看一遍 crypto loser-bounce”，而是判断 `24h lagged-return × liquidity-split sign flip` 是否已形成对当前 liquid perp desk 更贴近 `winner-follow` 的独立 raw alpha 主语。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，但现在已经收口完毕。
- 上一条 fresh intake 是 `Rank 299 / EMA(RSI) regime hierarchy trend alpha`；它当时具备独立主语与 clean-room 路径，因此值得获得唯一一次 survivor follow-up。
- 但最新 evidence 已明确：BTC perp `15m/5m` clean-room 下，`EMA(RSI)>60` uptrend gate（含 `PSAR` 保护）虽然减少交易，但没有把裸 `EMA9/20` 趋势壳提升成成本后可存活的 short-cycle sleeve；最好 pocket 也只是 gross 微正、net 明显为负。
- 因此这一次 follow-up 已被诚实用完，结论是 `survivor budget exhausted -> background/P0`，不再保留前排锁。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`；此后没有新的对象进入 `Active P2`。
- 因而当前不存在需要 bot2 兜底裁成 `P3 / P1 / P0` 的在役 P2 对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot = none`
- `Active P2 slot = none`
- 当前前排没有无 rank 对象；本轮无需补发新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 最近 desk review / optimization 证据里，也没有出现“对象已足够进入 paper trade，但 bot3 尚未升级”的漏升案例。
- 因此本轮不触发 bot2 直接改写到 `P3 / Paper launch queue` 或 handoff 路径。

## 本轮排班结论
继续严格按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 归档`

但当前运行态为：
- `P3` 无待接线对象；
- `Active P2 = none`；
- `Surviving candidate = none`；
- `Rank 299` 已于最新 optimization 证据中完成 survivor 收口并回到 `background/P0`。

所以本轮 `cycle_plan` 应当回到 fresh intake，并按“最近新 repo / paper / alpha 报告”优先级，填入具体对象而不是泛模板：
1. `2026-04-02_2319_liquidity-split-lagged-return-alpha.md`
2. `2026-04-02_2356_bb-zscore-rsi-trendveto-meanreversion-alpha.md`
3. `2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`
4. `2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`

其中：
- `2319` 仍是最该先做的 fresh intake 头；
- `2356` 比 `2257/2043` 更新，也确实提供了与当前 pairs/carry 家族不同的单币 mean-reversion raw alpha 主体，因此应插入第二位；
- `2257` 与 `2043` 继续作为随后两条具体 intake。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排

## 本轮改变系统认知的一句话
`Rank 299` 的唯一 survivor follow-up 已经诚实收口并回到 `background/P0`，所以当前轮不该继续假装前排还有未结事项；运行态应正式切回新的 fresh intake，且由 `liquidity-split lagged-return` 领衔，其后依次是 `BB/z-score overshoot`、`RF threshold pairs`、`best-venue funding z-score carry`。