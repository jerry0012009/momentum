# Strategy Review — 2026-04-02 03:16 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并已复核最近运行证据：
- `research/optimization_loop/2026-04-02_0240_rank287_binance_polymarket_lagged_binary_keep_p1.md`
- `research/optimization_loop/2026-04-02_0212_rank286_survivor_followup_background_p0_thin_postcost_edge.md`
- `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md`
- `research/optimization_loop/2026-04-02_0313_midday_etf_fresh_intake_blocked_by_rank287_survivor_lock.md`
- `research/strategy_review/2026-04-02_0203_strategy-review.md`

## 本轮只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- 否，当前仍为空。
- `current_target = none`。
- 已完成接线并处于 `connected_runner_live` 的仍是：`Rank 200 / 201 / 213 / 229`。
- 最近证据里没有新的 `Active P2` 已经明显达到 `P3 / paper launch` 但尚未被升级的对象，因此本轮不存在 bot2 需要兜底直推 `P3` 的情形。

### 2) 本轮 `fresh intake` 是什么？
- 当前 runtime 里最近一条已经完成首判的 fresh intake 是：
  - `research/quant_digests/2026-04-02_0117_binance-polymarket-lagged-binary-mispricing-alpha.md`
  - 即 `Rank 287 / Binance impulse × Polymarket 15m lagged binary mispricing`
- 它的首判已经落库：对象已形成可独立审计的 cross-market raw alpha skeleton，因此记为 `keep_P1`；但当前证据仍主要停留在 repo/source audit 与 live endpoint snapshot，尚未完成 clean-room lagged post-cost baseline，所以不直升 `P2`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，而且它现在就是前排第一优先级。
- `Rank 287` 已占据 `Surviving candidate slot`，`followup_budget_remaining = 1`。
- 这唯一一次 follow-up 必须直接回答：
  - 在公开可拿的 `Polymarket 15m crypto binary × Binance futures` 数据上，做 one-lag honest fair-value baseline 后，`p_fair_up - p_mid_up` 在 `spread / fee / near-expiry veto / quote staleness` 之后是否仍留下可执行净 pocket。
- 这一步做完后若仍不能升 `P2`，按 policy 就应视为 survivor 预算耗尽并退出前排；因此不能再让新的 `keep_P1` 覆盖它的 survivor 槽位。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- `Rank 285` 已在 `2026-04-02 01:59 UTC` 完成 P2 出口决策，不再属于 active P2：
  - 结论不是 `P3`，也不是 fatal `P0`；
  - 而是一次性的 `P2 -> P1 re-scope`，收窄为仅面向 `mature liquid tail / high-RV` 条件化子桶、且只保留 `1h~4h` 慢节奏持有的窄版 reversal pocket。
- 因此本轮没有任何对象处于“离 `P3 / P1 / P0` 出口最近且仍未收口”的 active P2 状态。

## Rank 完整性检查
- `Paper launch queue`: 当前 target 为 `none`，不存在缺 rank。
- `Surviving candidate slot`: `Rank 287`，已有正式 rank。
- `Active P2 slot`: `none`。
- 当前前排对象不存在“已达 keep_P1/P2/P3 但无正式 rank”的问题，因此本轮无需补 rank。

## 本轮排班重写
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前真实前排链条为：
1. 没有 `P3` queue 头需要接线；
2. 没有 `Active P2`；
3. 有一个必须优先收口的 survivor：`Rank 287`；
4. 因此前排第一项必须是 `Rank 287` 的唯一 follow-up；
5. 只有在它已被诚实排入本轮前部后，才能切回新的 `fresh intake`。

### 已写回 `BOT2_BOT3_STATE.md` 的新 `cycle_plan`
1. `Rank 287 / Binance impulse × Polymarket 15m lagged binary mispricing`
   - action: 做 one-lag honest fair-value baseline，直接回答 post-cost 后是否仍有可执行净 pocket
   - success_criterion: 明确写成 `promote_P2` 或 `follow-up exhausted，退回 background/P0`
   - result: `none`
   - status: `pending`
2. `research/quant_digests/2026-04-02_0158_us-etf-midday-momentum-pocket-alpha.md`
   - action: 判断 `US crypto ETF midday 30m momentum pocket` 是否具备清晰可审计的 intraday raw alpha skeleton
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`
3. `research/quant_digests/2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`
   - action: 判断 `cross-asset integrated OFI lead/lag` 是否具备独立可复核的 feature、传导主语、交易时钟与执行边界
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`
4. `research/quant_digests/2026-04-02_0306_dynamic-coint-percentile-pairs-alpha.md`
   - action: 判断这条 `dynamic coint percentile pairs` 是否真是 distinct 的新主语，而不是旧 pairs family 改名后重复回前排
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`

## 结论
- `Paper launch queue`：空
- 本轮 fresh intake：`Rank 287`
- 上一条 fresh intake 是否值得唯一 follow-up：值得，而且必须排在第一位
- 当前明确 `Active P2`：无
- 因此本轮最诚实的排班不是继续围绕旧 `P2` 开放式延长，也不是跳过 survivor 直接追新，而是先收口 `Rank 287`，再补具体 fresh intake。
