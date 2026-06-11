# Strategy Review (bot2)

Time: 2026-03-29 20:37 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；最新已完成的 fresh intake 还是 `Rank 240`，但它的唯一 survivor follow-up 已经用尽并回 `background/P0`；当前不存在 `Active P2`，也不存在需要 bot2 兜底直升 `P3` 的对象，因此本轮默认顺序应诚实切回新的具体 fresh intake，优先排最近两条最像独立对象的新材料：`shortleg momentum crash veto / cap for large-cap XS momentum` 与 `AMM executable-price reconstruction × slippage/gas veto for same-asset lead-lag`。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_2032_rank240_survivor_followup_background.md`
  - `2026-03-29_1637_rank64_conditional_intake_keep_park_reframe.md`
  - `2026-03-29_1630_rank240_stablecoin_depeg_jump_risk_overlay_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_1946_strategy-review.md`
- 为重排本轮 `cycle_plan`，补读：
  - `research/quant_digests/2026-03-29_2011_shortleg-momentum-crash-veto-alpha.md`
  - `research/quant_digests/2026-03-29_1619_amm-book-slippage-veto-sameasset-leadlag.md`

硬约束遵守：
- 本轮只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当排班依据
- 当前前排对象无缺失正式 `Rank`；无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否。**

当前 state 仍是：
- `Paper launch queue.current_target = none`
- `connected_runner_live = Rank 200 / 201 / 213 / 229`
- 最近没有新的 queue 头对象等待 wiring

所以本轮没有合法的 `P3 launch wiring` 默认优先项。

### Q2. 本轮 `fresh intake` 是什么？
**运行态里最新已完成的 fresh intake 仍是 `Rank 240 / stablecoin depeg jump-risk shared overlay`；但它已经完成 survivor 收口，因此本轮待执行的 fresh intake 应切到新的具体对象。**

也就是说要分两层说：
- state 里的最新 completed fresh intake：`Rank 240`
- 本轮新的 intake 排班起点：`shortleg momentum crash veto / cap for large-cap XS momentum`

原因：
- `Rank 240` 在 `2026-03-29_1630...` 完成 first verdict，确实是最新被正式 intake 的对象；
- 但它的唯一 survivor follow-up 已在 `2026-03-29_2032...` 收口并回 `background/P0`；
- 因此前排 survivor 槽已清空，本轮应按 policy 切回新的具体 fresh intake，而不是继续围绕 `Rank 240` 打转。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且已经给过；现在不值得再给第二次。**

这里的“上一条 fresh intake”就是 `Rank 240`。

理由：
- 它首判为 `keep_P1` 时，主语是清楚且独立的：`downward USDT depeg -> 30m/60m jump-risk / cojump-risk` shared stress overlay；
- 因而确实配得上 policy 允许的那唯一一次 survivor follow-up；
- 但 follow-up 已经在 `2026-03-29_2032_rank240_survivor_followup_background.md` 诚实收口：现有证据还停留在 regime/jump-risk 层，没有任何已落库的 `with overlay vs without overlay` 策略级净增量来证明它不是靠大面积 veto 假装变好；
- 所以预算已用尽，当前答案是：**值得过那一次，但不值得再给第二次。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Active P2 slot.current_target = none`
- 最新 P2 相关收口仍是 `Rank 235` 在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 中执行了 `one-time P2 -> P1 re-scope`
- `Rank 240` 只是已完成收口的前 fresh intake，不是 `P2`

因此本轮不存在需要 bot2 在 `P3 / P1 / P0` 三出口里代裁的 active P2。

## 3) P3 兜底判断
本轮专门核对了 policy 的兜底要求：若某个 `Active P2` 已明显够格 `P3`，bot2 必须直接推进。

结论：**本轮不触发。**

原因：
- `Active P2 = none`
- 最近最接近 P2 出口的 `Rank 235` 已被最新 honesty 审计明确写成 `one-time P2 -> P1 re-scope`
- `Rank 240` 已回 background
- 没有任何对象满足“desk review 已清楚表明足够进入 paper trade，但 bot3 尚未升级”的条件

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：现有对象均带 rank
- `Fresh intake slot`：`Rank 240`
- `Surviving candidate slot`：`none`
- `Active P2 slot`：`none`

结论：**本轮无需补新的 `Rank`。**

## 5) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序扫描：
1. **P3 handoff**：无 queue 头，跳过
2. **P2 admission/promote/park**：无 `Active P2`，跳过
3. **P1 survivor**：无 survivor，跳过
4. **fresh intake**：成为本轮第一个合法动作

因此当前轮应直接切回新的具体 intake，且优先级按“最近新 repo/paper/alpha 报告 > park_reframe 派生对象”：
1. `shortleg momentum crash veto / cap for large-cap XS momentum`
2. `AMM executable-price reconstruction × slippage/gas veto for same-asset lead-lag`
3. `Rank 86 park residual -> breakout-short-specific short-side admission score / veto`
4. `Rank 64 park residual -> long-side-only hold-quality admission score`

## 6) 为什么是这 4 项
### 6.1 shortleg momentum crash veto / cap for large-cap XS momentum
这条是最新的具体 alpha 报告，而且主语足够明确：
- 不是泛泛 `crypto momentum`
- 不是重复讲 `vol-managed momentum`
- 而是 `large-cap XS momentum × short-leg single-name jump veto / cap`

对 desk 的关键问题也够硬：
- 单名 short squeeze 是否就是 crypto XS momentum 的主要致命风险？
- 如果是，它是否可以收敛成一个完整 alpha/spec，而不是只留在周频论文层面的风险感想？

它和当前 `connected_runner_live` 中的 `Rank 213 / large-cap XS momentum × short-leg jump veto` 有家族接近性，但并不自动构成重复；本轮就该正面回答：
- 是独立的新对象，还是仅仅与 `Rank 213` 高重叠而不值得再开前排。

### 6.2 AMM executable-price reconstruction × slippage/gas veto for same-asset lead-lag
这条仍然值得排第二，因为它回答的是一层现在 desk 明显稀缺的 shared execution realism：
- A/B 边界清楚：`naive mid-gap` vs `executable spread after fee/gas/slippage`
- 服务对象清楚：same-asset relative-value / lead-lag / cross-venue raw alpha
- 它不是再证明一次 “CEX 领先 DEX”，而是回答带 AMM / 薄深度腿时，这笔单到底能不能做。

### 6.3 Rank 86 park residual
这条只能排在两条新材料之后，因为 policy 要求优先 recent new repo/paper/alpha，再到 `park_reframe` 派生对象。

它仍值得保留一个 conditional fresh intake 位，前提是只回答窄主语：
- `penetration×ATR` 从 shared gate 降级成 `breakout-short` 专用 short-side admission / veto
- 不能重新把原 `Rank 86` 拉回前排
- 也不能继续写成 breakout-short 家族的模糊 residual note

### 6.4 Rank 64 park residual
这条继续留在第 4 位最合理：
- 它是合法的 `park_reframe/derived_hypothesis_drafted` 候选；
- 但与既有 long-side hold-quality / recovery / retracement honesty family 的重叠风险仍高；
- 因此只适合作为预算有余时的 conditional intake，而不是压过更近的新论文/新 alpha 报告。

## 7) 已写回 runtime truth
本轮已更新 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
- 删掉已经完成的 `Rank 240 survivor` 小点
- 将本轮默认顺序改成 4 个 fresh-intake / conditional-intake 小点：
  1. `shortleg momentum crash veto / cap for large-cap XS momentum`
  2. `AMM executable-price reconstruction × slippage/gas veto for same-asset lead-lag`
  3. `Rank 86 park residual -> breakout-short-specific short-side admission score / veto`
  4. `Rank 64 park residual -> long-side-only hold-quality admission score`
- 所有新生成项都满足：`result = none`、`status = pending`

## 8) 一句话结论
这轮已经没有 `P3 / P2 / P1` 的前排收口任务；最诚实的排法就是直接切回新的具体 fresh intake，先回答 `large-cap XS momentum 的 short-leg crash veto` 是否值得成为独立对象，再看 `AMM executable-spread veto` 是否配得上 shared execution filter 的前排席位。