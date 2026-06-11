# 2026-03-23 07:04 UTC · Rank 8 park reframe review

## Scope
- Source rank: `Rank 8 EMA shielding / threshold + retest_hold`
- Original verdict stays: `park / evidence pool`
- This round only asks: **after the newer EMA role-split evidence, should Rank 8 spawn a narrower reframe beyond the already drafted `Rank 8b`?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_2229_ema_shielding_park.md`
  - `research/park_reframe/2026-03-19_0214_rank8-park-reframe.md`
  - `research/quant_digests/2026-03-19_0210_adjustable-band-ema-cost-survival.md`
  - `research/quant_digests/2026-03-23_0234_apextrend-ema-role-split-breakout-primary.md`

## Why this rank this round
- `Rank 1~37` 里的 parked ranks 近 7 天几乎都被 `bot6` 复盘过；这轮若要重复碰旧 rank，必须有新证据。
- `Rank 8` 在 2026-03-19 已经形成过 `Rank 8b`，但 2026-03-23 新增的 ApexTrend digest 又给出一句更硬的旁证：**EMA 更像 context / confirm / exit 的角色层，不像应该自己负责按扳机的主 alpha。**
- 这轮要判断的，不是推翻原 `park`，而是：这条新旁证会不会自然长成 `Rank 8c`，还是只会让我们更确信“到 `8b` 为止就够了”。

## 1) 原 rank 为什么 park？
原 `Rank 8` 被 park，不是因为“EMA 附近别乱做”这个总方向完全没信息，而是因为当时落成的 `fixed threshold + retest_hold` 写法没有通过最小诚实门槛：

- `raw_cross @ 6bps ≈ -15.76%`
- `threshold_005 @ 6bps ≈ -15.54%`
- `retest_hold @ 6bps ≈ -6.50%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 54 / asset`
- `Light Stability Pack` 四项全 fail（时间 / 参数 / 跨标的 / 成本）

最关键的读法其实很集中：
- `fixed 0.5% threshold` 几乎和 `raw_cross` 重合，说明这道固定 band 基本没起作用；
- `retest_hold` 只做到“少亏很多”，但仍没翻正；
- 所以原 `park` 的审计意义应保留：**原版 EMA shielding 不是没故事，而是 fixed-band 这套实现不够诚实。**

## 2) 它更像 hard park 还是 soft park？
**仍更像 `soft park`。**

原因：
- 原 `fixed threshold + retest_hold` 本体已经该停；
- 但它留下了清楚的“角色没写好”痕迹，而不是完全无 pocket 的硬死线；
- 这也是为什么上轮已经诚实起草出 `Rank 8b`：把固定阈值改成 `adaptive ATR-scaled no-trade band`。

## 3) 有没有“可救信号”？
**有，但新证据只是在收紧既有 `Rank 8b` 的角色边界，不足以再开一条新主轴。**

### 已有可救信号
- `2026-03-19_0210_adjustable-band-ema-cost-survival.md` 已经说明：对 crypto 均线规则，真正有信息的可能不是“有没有 band”，而是 `band` 是否随波动自适应。
- 这条证据正对原 blocker，因此上轮形成 `Rank 8b` 是合理的。

### 本轮新增可救信号
- `2026-03-23_0234_apextrend-ema-role-split-breakout-primary.md` 新增的旁证更进一步说明：
  - EMA 更像 `macro gate + momentum confirm + fast exit`；
  - 真正按扳机的通常还是 breakout；
  - PSAR 甚至不一定需要出场。

这条新证据值钱的地方，不是“再给 Rank 8 造一个新 EMA 玩法”，而是提醒我们：
**即便保留 `8b`，也应该把它理解成 shielding / no-trade layer，而不是让 EMA 再次偷偷升格成独立主触发。**

## 4) 最值得改的唯一一刀是什么？
**如果今天仍只允许保留一刀，答案不变：`fixed threshold -> adaptive ATR-scaled no-trade band`。**

也就是：
- 保留 Rank 8 的 shielding 角色；
- 不再坚持固定百分比 band；
- 只测 `raw_cross vs fixed_band vs adaptive_band`；
- 不顺手改成“breakout 触发 + EMA context gate”那种第二条故事线。

换句话说：
- `2026-03-23` 的 ApexTrend 新证据，说明 EMA 更该待在角色层；
- 但对 `Rank 8` 来说，这不构成新的独立主修改轴；
- 它只是让 `Rank 8b` 的定位更稳：**band 是 admission/shielding，不是让 EMA 重新自己开火。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. `Rank 8b` 已经消费了最自然、最诚实的单轴改写：`fixed band -> adaptive band`。
2. 2026-03-23 的 ApexTrend 新证据，没有再提供一条新的单轴；它只是强化“EMA 应待在角色层”的解释框架。
3. 如果这轮硬起 `Rank 8c`，大概率会滑向第二轴漂移：把原本讨论 `band 写法` 的问题，偷换成 `trigger role rewrite`，这不符合 bot6 每轮只保留 1 条唯一主修改轴的纪律。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** overturn the original `park`, and it does **not** add `Rank 8c`.
The newer ApexTrend evidence is useful, but only as a role-clarification note for the already drafted `Rank 8b`: EMA should stay a shielding / context layer, not quietly become a standalone trigger again.

## Git
- 本轮只做最小必要文档更新；未做 commit。
- 原因：工作区存在无关脏文件，当前不适合安全地 selective commit。
