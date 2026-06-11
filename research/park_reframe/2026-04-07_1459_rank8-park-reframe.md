# 2026-04-07 14:59 UTC · Rank 8 park reframe review

## Scope
- Source rank: `Rank 8 EMA shielding / threshold + retest_hold`
- Original verdict stays: `park / evidence pool`
- This round only asks: **after the newer trend-shell evidence from early April, should Rank 8 spawn a narrower reframe beyond the already drafted `Rank 8b`?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_2229_ema-shielding-park.md`
  - `research/park_reframe/2026-03-19_0214_rank8-park-reframe.md`
  - `research/park_reframe/2026-03-23_0704_rank8-park-reframe.md`
  - `research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
  - `research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`
  - `research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`

## Why this rank this round
- 本轮按 `Rank 1~37` 的 parked rank 低频复盘来选；`Rank 8` 上次 park-reframe 复盘是 `2026-03-23`，已经超过 7 天。
- 它仍是一个典型的“主题未必死、但原角色写法已被审计得很清楚”的旧 rank。
- 4 月初新增的几篇 digest 都继续围绕趋势壳 / EMA 角色 / 退出骨架展开，正适合回答：这些新证据会不会自然长成 `Rank 8c`，还是只会让我们更确信“到 `8b` 为止就够了”。

## 1) 原 rank 为什么 park？
原 `Rank 8` 被 park，不是因为“EMA 附近别乱做”这个方向完全没信息，而是因为当时落成的 `fixed threshold + retest_hold` 写法没有通过最小诚实门槛：

- `raw_cross @ 6bps ≈ -15.76%`
- `threshold_005 @ 6bps ≈ -15.54%`
- `retest_hold @ 6bps ≈ -6.50%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 54 / asset`
- `Light Stability Pack` 四项全 fail（时间 / 参数 / 跨标的 / 成本）

关键读法一直很集中：
- 固定 `0.5%` threshold 基本和 `raw_cross` 重合，说明这道 fixed band 近乎没起作用；
- `retest_hold` 只是少亏很多，但还没到可诚实重开的程度；
- 所以原 `park` 的审计意义要保留：**原版 EMA shielding 的 blocker 是 fixed-band 写法不成立，而不是 EMA 主题本身就必然为零。**

## 2) 它更像 hard park 还是 soft park？
**仍更像 `soft park`，但对原 Rank 8 本体的读法已经明显偏硬。**

原因：
- `fixed threshold + retest_hold` 这条原始写法已经被审计完成，不值得再回头补文书；
- 但它并不是完全没有 residual clue 的硬死线，因为 `Rank 8b` 已经诚实地保留了一条唯一自然残余：**把 fixed band 改写成 adaptive ATR-scaled no-trade band**；
- 新证据没有推翻这条 residual，反而在把 EMA 主题继续往“角色层 / 壳层 / exit 层”上推。

## 3) 现有证据里是否存在“可救信号”？
**有，但可救信号仍只到既有 `Rank 8b` 为止。**

### 已被消费的可救信号
- `Rank 8` 原 clean replication 已经给出最自然的残余：fixed band 没用，不代表 shielding/no-trade 角色没用。
- 这条 residual 已被 `Rank 8b` 吸收：`fixed threshold -> adaptive ATR-scaled no-trade band`。

### 本轮新证据的真实含义
1. `2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
   - 值钱的地方更像：**完整 trend continuation raw alpha + fast exit shell**；
   - 它说明 EMA 更适合作为 allow / context，而不是单独触发故事。
2. `2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`
   - 值钱的地方更像：**VWAP-EMA directional-change raw alpha + ~1% reversal exit**；
   - 它继续把 EMA 家族往“慢趋势脊柱 / 退出骨架”上推，而不是给 Rank 8 额外开一条 threshold 新轴。
3. `2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`
   - 这条反而提醒：**把 EMA / 趋势确认层写得过于苛刻，很容易退化成不触发的 trend shell**；
   - 它更像 source-audit / firing-density 教训，不是 Rank 8 的新派生入口。

翻成人话：
- 新证据没有告诉我们“再给 Rank 8 加一层新 gate 就能活”；
- 新证据是在继续强调：**EMA 更像 trend shell 的 context / shielding / exit 组件，而不是值得从旧 Rank 8 再派生出 `Rank 8c` 的独立主修改轴。**

## 4) 最值得改的唯一一刀是什么？
**如果今天仍只允许保留一刀，答案还是不变：`fixed threshold -> adaptive ATR-scaled no-trade band`。**

也就是：
- 保留 Rank 8 的 shielding 角色；
- 不再坚持固定百分比 band；
- 第一轮只测 `raw_cross vs fixed_band vs adaptive_band`；
- 不顺手偷带 breakout 主触发、Wilder RSI、VWAP-EMA、SuperTrend、fast-exit 或新的 regime matrix 第二轴。

这也正是为什么本轮不该再 draft `Rank 8c`：
- 因为唯一值得保留的一刀早已明确；
- 现在再继续派生，只会滑向“把 EMA 主题泛化成任何 trend shell 都算 Rank 8 后续”，这不诚实。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. `Rank 8b` 已经消费了最自然、最诚实的窄 reframe；
2. 4 月初的新证据虽然支持 EMA/趋势主题仍有研究价值，但更像新的 raw-alpha family / exit-shell family 宿主，不属于原 Rank 8 可继续诚实派生的同一主轴；
3. 如果此时硬起 `Rank 8c`，大概率会变成多轴漂移：从 `band 写法` 偷换成 `trend shell 重写` 或 `fast exit 重写`，这违反 bot6 每轮只保留 1 条主修改轴的纪律。

## 6) trade on / trade off 如何写？
本轮**不新增** derived hypothesis，因此不新写 `trade on / trade off` 草案。

保留的唯一有效旧草案仍是：
- `Rank 8b`
- `single modification axis = replace fixed EMA shielding threshold with adaptive ATR-scaled no-trade band`

除此之外，本轮没有足够诚实的新单轴值得追加。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park (for the family), but already quite hard for the original Rank 8 implementation`

## Minimal audit note
This round does **not** overturn the original `park`, and it does **not** add `Rank 8c`.
The newer early-April evidence is useful, but mainly as a reminder that EMA-family information now lives more naturally inside **new trend-shell / exit-shell raw-alpha families**, not as another honest extension of old `Rank 8`.

## Git
- 本轮只做最小必要文档更新；未做 commit。
- 原因：工作区存在大量无关未跟踪 / 脏文件，当前不适合安全地 selective commit。
