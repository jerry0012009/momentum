# 2026-03-19 13:34 UTC · Rank 5 park reframe review

## Scope
- Source rank: `Rank 5 session-aware intraday TSMOM`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 5 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-19_1111_rank19-park-reframe.md`
  - `research/park_reframe/2026-03-19_0848_rank6-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_2149_intraday-tsmom-session-park.md`
  - `research/quant_digests/2026-03-19_0426_bitcoin-first-30m-impulse-quality-gate.md`
  - `research/optimization_loop/2026-03-19_0547_rank80-clean-replication-keep-p1.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- The original failure was clear but also concentrated: the direct `session front -> session tail` lag-trade framing was broadly negative, yet the newer adjacent evidence suggests the open-session impulse may still contain **context information**, just not enough to stand alone as a session-end trade.
- A fresh nearby line (`Rank 80`) now offers a clean, single-axis role downgrade that keeps the session-aware momentum theme but removes the overclaim: **stop trading session tail directly; test open-session impulse only as a shared continuation gate / sizing hint.**

## 1) 原 rank 为什么 park？
Rank 5 被 park，核心不是“session-aware intraday momentum 这个主题彻底没信息”，而是它在原 clean replication 里被写成了一个 **standalone session-tail trade**，证据不够诚实：

- 主读法 `funding_8h_q60 @ 6bps/side`
  - `mean_total_return≈-22.74%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈145`
  - `mean_direction_hit_rate≈42.53%`
- 分资产也没有留下 pocket：
  - `BTC≈-20.65%`
  - `ETH≈-23.93%`
  - `SOL≈-23.64%`
- 全部 6bps 变体里最不差的 `utc_day_q70` 也仍约 `-6.35%`
- `Light Stability Pack` 四项一起 fail：
  - 时间稳定性 `0/3 positive buckets`
  - 参数邻域 `0/3 positive neighbors`
  - 跨资产 `0/3 positive assets`
  - 成本生存 `0/4 cost levels positive`

翻成人话：
- 这不是样本太稀导致的“没法下判断”；
- 是 **把 session 前段走势硬写成“尾段直接跟单”的交易形状后，跨资产、跨参数、跨成本都不成立**；
- 所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 作为 standalone `session-aware intraday TSMOM` 尾段交易，这条线已经被审计消费；
- 但它的问题更像是 **角色放错层级、交易形状太直给**，而不是“开段冲击质量 / session-aware continuation 信息完全为零”。
- 也就是说：
  - 原 Rank 5 版本该停；
  - 但 `session open impulse` 作为 shared gate / sizing hint，仍可能留有窄重开空间。

## 3) 有没有“可救信号”？
**有。**

可救信号不是原 Rank 5 本身留下了好 pocket，而是它的近邻旁证把“session-aware momentum”重新解释成了更诚实的角色：

1. 原 Rank 5 已经证明：
   - `前 2 根 15m -> session 最后 2 根 15m` 这种 direct tail-trade 写法太粗；
   - 问题主要在于把 session-aware 信息硬当成可独立吃成本的主 alpha。
2. 2026-03-19 的 `first-30m impulse quality` digest 给出的旁支很集中：
   - 不是所有 continuation 都该放行；
   - 当开段同时具备方向、量能、波动三者共识时，后续 continuation 更值得放行。
3. 更关键的是，邻近的 `Rank 80` 最小 clean replication 已经给出一个很有用的边界：
   - `impulse_veto` 太狠，`trade_count_retention≈14.01%`，不能当通用 desk gate；
   - 但 `impulse_halfsize` 相比 baseline，确实把 desk 级亏损从约 `-2.00%` 收窄到约 `-1.09%`，expectancy 也从约 `-0.065%` 改善到约 `-0.039%`；
   - 这说明开段冲击质量**不像独立 alpha，但像 shared sizing / admission hint**。

更直白地说：
- Rank 5 最值得留下的，不是“session tail 直接跟单”；
- 而是“先看开段冲击质量，再决定 continuation setup 出手强度”。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀：把 Rank 5 从 direct `session-tail intraday TSMOM` entry，降级成 `first-30m impulse quality` shared continuation gate / sizing layer。**

也就是：
- 不再根据 session 前段方向，直接去做 session 尾段那一笔；
- 只把 session 开段 `方向 + 成交量 + 波动` 质量，当作现有 `breakout-short / EMA-PSAR continuation / Fib retest_hold` 的 shared allow/half-size/veto 层；
- 第一轮优先测 `half-size`，而不是 strict veto，因为相邻证据已经显示 strict veto 太容易靠砍单美化。

为什么这算一刀而不是多轴大改：
- 核心主题没变，仍是 `session-aware intraday momentum`；
- 数据仍是已有 5m/15m OHLCV；
- 只改了它的 **角色层级**，没有顺手换 exit、换 universe、换多层 regime stack。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 原 `park` 结论完整保留，尤其“direct session-tail trade 不成立”这一点不翻案；
- 原 Rank 5 的失败集中在交易形状太粗、直接 alpha 过度主张；
- 新旁证提供了一个只改角色、不改主题的窄 reframe：**open-session impulse 不再单独开仓，只做 continuation gate / sizing hint。**

## 6) trade on / trade off 结论
### Proposed derived hypothesis
- `proposed_rank`: `Rank 5b`
- `source_rank`: `Rank 5`
- `single modification axis`: `demote direct session-tail intraday TSMOM entry into a first-30m impulse-quality shared continuation gate / sizing layer`
- `trade on`: `不再根据 session 前段收益方向直接去做尾段跟随；而是在固定 funding-style session（第一轮优先 00/08/16 UTC）上，只用开段前 30 分钟的 impulse quality（方向 + volume z-score + realized-vol percentile）来决定现有 continuation setups 的 allow / half-size / veto：当 open30 与 setup 同向且量波共振时，优先放行或加权 breakout-short 与 EMA/PSAR continuation；当 impulse 质量弱时，优先 half-size；对 Fib retest_hold 只先测 sizing，不偷带新的 trigger。第一轮只测 baseline vs half-size gate vs strict veto。`
- `trade off`: `放弃“session-aware intraday TSMOM 本身就是可独立交易的尾段 alpha”的原 Rank 5 读法，换取更诚实的开段冲击质量 gate / sizing 角色；代价是它不再是 standalone 策略，而且若直接用 strict veto，可能只是靠大幅砍单美化结果，因此第一轮必须先把 half-size 作为主臂，不偷带新 exit / second-layer regime / event stack。`
- `why now`: `原 Rank 5 clean replication 已很清楚地证明 direct session-tail intraday TSMOM 在 BTC/ETH/SOL 15m 上跨资产、跨参数、跨成本一起转负；但 2026-03-19 新增的 first-30m impulse-quality digest 与邻近 Rank 80 clean replication 又共同说明：session-aware opening impulse 仍可能作为 shared continuation sizing hint 留下一点信息，只是不该再被写成独立 tail trade。`
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 5 itself.
It keeps the original `park` intact. The only new move is a narrower role downgrade: **`Rank 5b = stop trading session-tail intraday TSMOM directly, and test session open impulse quality only as a shared continuation gate / sizing layer for existing lanes.`**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
