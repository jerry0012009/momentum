# 2026-03-19 02:14 UTC · Rank 8 park reframe review

## Scope
- Source rank: `Rank 8 EMA shielding / threshold + retest_hold`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 8 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_2357_rank7-park-reframe.md`
  - `research/park_reframe/2026-03-18_2145_rank4-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_2229_ema-shielding-park.md`
  - `reports/site/factors/scout_ema_shielding_15m/report.html`
  - `research/quant_digests/2026-03-19_0210_adjustable-band-ema-cost-survival.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- It has one clear salvage clue: the original `retest_hold` arm did improve a lot versus `raw_cross / threshold_005` (`-6.50%` vs about `-15.5%` at `6bps/side`), but the original fixed threshold design looked basically inert.
- A fresh paper digest now points at a tighter rewrite: **stop asking fixed `%` shielding to work like a universal filter; test an adaptive ATR-scaled no-trade band instead.**

## 1) 原 rank 为什么 park？
Rank 8 被 park，不是因为“EMA 附近别乱追”这个方向完全没价值，而是因为当时落成的 **fixed threshold + retest_hold** 版本并没有形成能穿过最小诚实门槛的可执行候选。

原 clean replication 的关键证据：
- `raw_cross @ 6bps ≈ -15.76%`，`positive_asset_ratio=0/3`
- `threshold_005 @ 6bps ≈ -15.54%`，几乎和 raw 一样，说明固定阈值基本没起作用
- `retest_hold @ 6bps ≈ -6.50%`，虽然明显少亏，但仍是 `0/3` 资产为正
- `mean_trades≈54 / asset`、`mean_no_trade_ratio≈5.38%`，说明它不是靠极端稀疏交易才“看起来不那么差”
- `Light Stability Pack` 四项全 fail：时间、参数、跨标的、成本

更直白地说：
- 原 Rank 8 的主题没死；
- 但“固定 0.5% 阈值 + 二元 retest_hold”这套写法不够诚实地活下来；
- 继续沿原 fixed-band 近邻微调，边际价值已经很低。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 作为当前已经审计过的 `fixed threshold + retest_hold` 方案，它该继续 `park`；
- 但它不是那种“完全没 pocket”的硬死线，因为 `retest_hold` 至少把亏损显著收窄，而且新的论文 digest 又直接指出：对 crypto 均线规则来说，关键可能不是“有没有 threshold”，而是 **threshold 是不是要随波动自适应**。

所以更诚实的读法是：
- 原 Rank 8 保持 `park`；
- 但它留下了一个窄而明确的可救信号：**fixed band 可能错在 band 写法太死，不是 shielding/no-trade 角色本身一定错。**

## 3) 有没有“可救信号”？
**有。**

可救信号主要有三点：
1. `retest_hold` 相比 `raw_cross / threshold_005` 的改善是真实存在的，说明“别在 EMA 边上零阈值乱触发”这个总方向并非纯噪音；
2. `threshold_005` 几乎和 `raw_cross` 重合，说明 blocker 更像 **阈值设计无效**，而不是 shielding 这个角色天然无用；
3. 最新 `adaptive no-trade band` digest 给出了一条非常窄、而且正对原 blocker 的单轴改写：把固定 `%` 阈值改成 **ATR / price 驱动的动态 band**。

翻成人话：
- 原 Rank 8 不是证明“band 没用”；
- 它更像只证明了“**这版 fixed band 几乎等于没 band**”。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀：把 Rank 8 的固定 shielding threshold 改成 `adaptive ATR-scaled no-trade band`。**

也就是：
- 保留 Rank 8 的核心角色：它仍是 EMA-family 的 shielding / admission layer；
- 但不再把门槛写死成 `0.5%` 这种固定带；
- 改成例如 `band_t = max(base_floor, q * ATR14 / close)` 的动态 no-trade 带，先回答“离均线太近的噪声触发，要不要按当下波动大小决定先别做”。

第一轮必须保持窄：
- 只比较 `raw_cross vs fixed_band vs adaptive_band`；
- 不顺手偷带新 regime、VWAP、volume、更换 exit；
- `retest_hold` 若保留，也只能当对照，不应再把“换 threshold + 换 retest 语义”混成多轴大改。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 原 `park` 结论完整保留，尤其“fixed threshold + retest_hold 版本不够诚实”这点不推翻；
- 原证据里最值得保留的不是具体 `0.5%` 参数，而是“零阈值触发太容易被成本磨损”的问题意识；
- 最新 digest 提供了一个足够窄、且与原 Rank 8 高度同主题的单轴改写：**把 fixed band 改成 adaptive band**。

## 6) trade on / trade off 结论
### Proposed derived hypothesis
- `proposed_rank`: `Rank 8b`
- `source_rank`: `Rank 8`
- `single modification axis`: `replace fixed EMA shielding threshold with adaptive ATR-scaled no-trade band`
- `trade on`: `保留 Rank 8 的 EMA family shielding 角色，不再用固定 0.5% band；改成只有当 close 脱离 EMA trigger 达到动态 band（如 max(0.10%, q * ATR14/close)）后，才允许按 next-bar open 触发；short 镜像。第一轮只测 raw_cross vs fixed_band vs adaptive_band。`
- `trade off`: `放弃“固定百分比阈值到处通用”的原 Rank 8 写法，换取更贴近 crypto 波动状态的 no-trade 带；代价是它不再是简单静态规则，而且若 q / base_floor 选得太宽，可能只是靠砍单美化结果，因此第一轮必须只测 band 本身，不偷带新 retest / regime / exit。`
- `why now`: `原 Rank 8 里真正明显失效的是 fixed threshold 近乎不工作，而 retest_hold 至少证明 shielding 方向并非完全无效；最新 adaptive-band digest 又正好提供了一个只改阈值写法、不改 Rank 8 主题的窄重开路径。`
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 8 itself.
It keeps the original `park` intact. The only new move is a narrower threshold rewrite: **`Rank 8b = keep the shielding/no-trade role, but replace the inert fixed percentage threshold with an adaptive ATR-scaled band.`**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
