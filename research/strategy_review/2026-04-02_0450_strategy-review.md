# Strategy Review — 2026-04-02 04:50 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并已复核当前 repo/runtime 与最近证据：
- `git status --short`
- `research/optimization_loop/2026-04-02_0426_rank289_volnorm_rocshock_keep_p1.md`
- `research/optimization_loop/2026-04-02_0413_rank288_survivor_followup_background_p0_cleanroom_negative.md`
- `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md`
- `research/strategy_review/2026-04-02_0356_strategy-review.md`
- `research/strategy_review/2026-04-02_0316_strategy-review.md`

## 本轮只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- 否，当前为空。
- `current_target = none`。
- 已完成接线并处于 `connected_runner_live` 的仍是：`Rank 200 / 201 / 213 / 229`。
- 最近证据里没有任何仍停留在 `Active P2` 且已明显达到 `P3 / paper launch` 门槛、但 bot3 尚未升级的对象；因此本轮不存在 bot2 需要兜底直推 `P3` 的情形。

### 2) 本轮 `fresh intake` 是什么？
- 当前 runtime 里的最近 fresh intake 是：
  - `Rank 289 / research/quant_digests/2026-04-02_0344_volnorm-rocshock-ema-volume-alpha.md`
- 它的首判已完成并写回 state：
  - 这不是旧 breakout/TSMOM 换名，而是一条有清晰主语的 `vol-normalized shock continuation` raw alpha skeleton；
  - signal/admission/exit/data-transfer path 已成型；
  - 但当前证据仍停留在 repo/source audit 与偏薄成本壳，尚未完成去优化 clean-room existence、ablation 与厚成本跨资产诚实 admission，因此本轮只记为 `keep_P1`，不直升 `P2`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，而且它现在就是前排第一优先级。
- `Surviving candidate slot` 当前是 `Rank 289`，`followup_budget_remaining = 1`。
- 按 policy，它享有 survivor 锁定权；在这一次诚实收口完成前，不能让别的 `keep_P1` 覆盖它的前排槽位。
- 这唯一一次 follow-up 必须直接回答：
  1. 去优化 `15m` clean-room baseline 下，`shock only / +EMA / +EMA+volume / +EMA+volume+displacement` 的 ablation 是否仍留下真实增量；
  2. `BTC / ETH / SOL` 上是否仍有跨资产可迁移性；
  3. 在 `10 / 20 / 30 bps` 成本梯度下，是否还留有 after-cost pocket。
- 如果这一步过不了，就应直接 `follow-up exhausted -> background/P0`；不能继续把它拖成长尾 `keep_P1`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- `Rank 285` 已在 `2026-04-02 01:59 UTC` 完成 `P2 exit decision`，不再属于 active P2：
  - 结论不是 `P3`，也不是 fatal `P0`；
  - 而是一次性的 `P2 -> P1 re-scope`，收窄为只面向 `mature liquid tail / high-RV` 条件化子桶、并只保留 `1h~4h` 慢节奏持有的窄版 reversal pocket。
- 因此当前没有任何对象处于“离 `P3 / P1 / P0` 出口最近但尚未收口”的 active P2 状态。

## Rank 完整性检查
- `Paper launch queue`: `none`，无 rank 缺口。
- `Surviving candidate slot`: `Rank 289`，已有正式 rank。
- `Active P2 slot`: `none`。
- 当前前排对象不存在“已达 keep_P1 / P2 / P3 但无正式 rank”的问题，因此本轮无需补 rank。

## 本轮排班重写
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 归档`。

当前真实前排链条为：
1. 没有 `P3` queue 头需要接线；
2. 没有 `Active P2`；
3. 有一个必须优先收口的 survivor：`Rank 289`；
4. 因此前排第一项必须是 `Rank 289` 的唯一 follow-up；
5. 只有在它已被诚实排入本轮前部后，才能切回具体 fresh intake。

### 已写回 `BOT2_BOT3_STATE.md` 的新 `cycle_plan`
1. `Rank 289 / vol-normalized ROC shock × EMA displacement × volume confirmation`
   - action: 执行 survivor 的唯一一次 decisive follow-up，直接回答去优化 `15m` clean-room baseline 下 `shock only / +EMA / +EMA+volume / +EMA+volume+displacement` 的 ablation，外加 `BTC/ETH/SOL` 与 `10/20/30 bps` 成本梯度后，是否仍保留可迁移的 after-cost pocket
   - success_criterion: 明确写成 `promote_P2` 或 `follow-up exhausted，退回 background/P0`
   - result: `none`
   - status: `pending`
2. `research/quant_digests/2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`
   - action: 判断 `cross-asset integrated OFI lead/lag` 是否已具备独立可审计的 leader-follower 主语、feature 定义、交易时钟与最小 transfer path
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`
3. `research/quant_digests/2026-04-02_0306_dynamic-coint-percentile-pairs-alpha.md`
   - action: 判断 `dynamic coint percentile pairs` 是否真是 distinct 的 pairs raw alpha，而不是旧 pairs family 改名重回前排
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`
4. `research/quant_digests/2026-04-02_0448_utc-slot-costmap-route-veto-overlay.md`
   - action: 判断 `UTC slot cost map × route veto overlay` 是否足够 distinct 且值得进入前排，而不是把常识性的 time-of-day liquidity 说法包装成新东西
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`

## 结论
- `Paper launch queue`：空
- 本轮 `fresh intake`：`Rank 289`
- 上一条 fresh intake 是否值得唯一 follow-up：值得，而且必须优先收口
- 当前明确 `Active P2`：无
- 因此本轮最诚实的排班是：先收口 `Rank 289`，再继续具体 fresh intake，而不是虚构新的 P2/P3 主线。