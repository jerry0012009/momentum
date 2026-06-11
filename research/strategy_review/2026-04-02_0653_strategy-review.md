# Strategy Review — 2026-04-02 06:53 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并已复核当前 repo/runtime 与最近证据：
- `git status --short`
- `research/optimization_loop/2026-04-02_0614_rank290_l2_delta_vote_keep_p1.md`
- `research/optimization_loop/2026-04-02_0627_kvsi_intake_blocked_by_rank290_survivor_lock.md`
- `research/optimization_loop/2026-04-02_0641_rank290_survivor_lock_blocks_rank_dynamic_coint_intake.md`
- `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md`
- `research/strategy_review/2026-04-02_0604_strategy-review.md`

## 本轮只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- 否，当前为空。
- `current_target = none`。
- 已处于 `connected_runner_live` 的仍是：`Rank 200 / 201 / 213 / 229`。
- 最近证据里没有新的 `Active P2` 已经明显达到 `P3 / paper launch` 门槛却尚未升级；因此本轮不存在 bot2 需要兜底直推 `P3` 的对象。

### 2) 本轮 `fresh intake` 是什么？
- 严格说，**当前前排最先要执行的不是新的 fresh intake，而是 survivor 收口**。
- 当前 runtime 中唯一合法的前排 pending 动作是：
  - `Rank 290 / L2 imbalance × aggressive trade delta × EMA vote` 的唯一一次 survivor follow-up。
- 因此新的 fresh intake 只能排在它后面；按本轮重排后的顺序，survivor 收口之后的第一条 fresh intake 才是：
  - `research/quant_digests/2026-04-02_0522_kvsi-korean-venue-share-regime-gate.md`

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，而且现在就该执行。
- 上一条 fresh intake 是：
  - `Rank 290 / L2 imbalance × aggressive trade delta × EMA vote`
- 它已在 `2026-04-02 06:14 UTC` 得到 `keep_P1`：
  - 不是旧 OBI 家族简单换壳；
  - 有明确 `OBI + aggressor delta + EMA` 三腿共振主语；
  - 有最小前向录数与可执行 skeleton；
  - 但 still 缺最关键的 after-cost markout。
- 所以它正好符合 policy 所说的“只配 1 次最小 decisive follow-up”的 survivor：
  - 若 after-cost pocket 不存在，则应立即回 `background/P0`；
  - 若至少留下清晰 pocket，则应直接升 `P2`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 最近一个 active P2 是 `Rank 285`，但它已在 `2026-04-02 01:59 UTC` 完成出口决策，不再属于 active P2：
  - broad `24h losers-vs-winners XS reversal` 不足以诚实升 `P3`；
  - 但也不是 fatal `P0`；
  - 已执行一次性的 `P2 -> P1 re-scope`，收窄到 `mature liquid tail / high-RV` 且 `1h~4h` 慢节奏持有的窄版 pocket。
- 因此当前不存在“仍在 active P2 且离 `P3 / P1 / P0` 哪个出口最近”的对象。

## Rank 完整性检查
- `Paper launch queue`: `none`，无 rank 缺口。
- `Surviving candidate slot`: `Rank 290`，已有正式 rank。
- `Active P2 slot`: `none`。
- 当前前排对象不存在“达到 keep_P1 / P2 / P3 但无 rank”的情况，因此本轮无需补 rank。

## 本轮排班修正
上一版 runtime 把新的 fresh intake 放在 survivor 前面，且第 2/3 项已经被 guard 标成 `blocked`；这说明排班顺序不符合 policy 的 authoritative priority ladder。

按 policy，本轮合法顺序应为：
1. `Rank 290` survivor 唯一 follow-up
2. `KVSI` fresh intake
3. `dynamic coint percentile pairs` fresh intake
4. `cross-asset integrated OFI lead/lag` fresh intake

### 已写回 `BOT2_BOT3_STATE.md` 的新 `cycle_plan`
1. `Rank 290 / L2 imbalance × aggressive trade delta × EMA vote`
   - action: 执行 survivor 唯一一次诚实 follow-up，直接回答它在 `BTC/ETH/SOL/BNB/DOGE` 上按最小前向 / bar-close markout 口径是否至少留下一块成本后仍存活的 `1m/3m` pocket，并顺手区分 `volume bonus` 是 alpha 本体还是噪音装饰
   - success_criterion: 必须给出明确 survivor verdict：`promote_P2` 或 `回 background/P0`
   - result: `none`
   - status: `pending`
2. `research/quant_digests/2026-04-02_0522_kvsi-korean-venue-share-regime-gate.md`
   - action: 作为 survivor 收口后的第一条 fresh intake 做 first verdict
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`
3. `research/quant_digests/2026-04-02_0306_dynamic-coint-percentile-pairs-alpha.md`
   - action: 作为下一条 fresh intake 做 first verdict
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`
4. `research/quant_digests/2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`
   - action: 作为再下一条 fresh intake 做 first verdict
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`

## 结论
- `Paper launch queue`：空
- 当前真正需要优先执行的前排动作：`Rank 290` 的 survivor follow-up
- survivor 收口后的第一条 fresh intake：`KVSI`
- 上一条 fresh intake 是否值得唯一一次 follow-up：值得，而且现在就该做
- 当前明确 `Active P2`：无
- 本轮 bot2 已把 runtime 重排回合法顺序，避免新的 intake 越过 survivor 锁。