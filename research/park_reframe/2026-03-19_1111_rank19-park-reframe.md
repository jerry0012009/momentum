# 2026-03-19 11:11 UTC · Rank 19 park reframe review

## Scope
- Source rank: `Rank 19 box consolidation / structure breakout`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 19 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-19_0848_rank6-park-reframe.md`
  - `research/park_reframe/2026-03-19_0644_rank3-park-reframe.md`
  - `research/park_reframe/2026-03-19_0433_rank28-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0320_rank19-box-consolidation-park.md`
  - `research/quant_digests/2026-03-19_1034_stolgo-consolidation-breakout-asymmetry-gate.md`
  - `research/quant_digests/2026-03-19_1059_breakout-reentry-inside-sequence-failure-verdict.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- The original failure was concentrated and interpretable: the standalone box-breakout variants were either **broad and persistently negative** or **narrow but too sparse to admit**.
- A fresh digest now offers a clean role downgrade that fits the original theme without overturning it: **stop asking consolidation breakout to be a standalone entry alpha; test it as a shared `close-range compression` admission layer instead.**

## 1) 原 rank 为什么 park？
Rank 19 被 park，不是因为“价格先压缩再释放”这个主题完全没信息，而是因为它在原最小 clean replication 里，写成了一个 **standalone structure-breakout entry family**，结果不够诚实：

- 主变体 `accumulation_ready @ 6bps/side`
  - `mean_total_return≈-20.13%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈177.3`
- `narrow_accum_ready` 也仍约 `-20.10%`、`0/3`
- 更窄的 `box_breakout_ready`
  - `mean_total_return≈-0.77%`
  - `positive_asset_ratio=1/3`
  - `mean_trades≈9.3`
  - `mean_no_trade_ratio≈99.91%`

Light Stability Pack 也没有给它留下 admission 读法：
- 时间稳定性 `0/3` bucket 为正；
- 参数邻域最不差仍约 `-9.87%`；
- 跨资产 `BTC/ETH/SOL` 三条腿全部为负；
- friction 从 `6 -> 20bps/side` 持续恶化。

翻成人话：
- 它不是“完全无样本”；
- 它是 **宽版本一直亏，窄版本又薄到不够当策略证据**；
- 所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 作为 standalone `box consolidation / structure breakout` 策略，它已经该停；
- 但它失败得并不“彻底抽象无效”，而更像 **信号角色放错层级**：
  - 让压缩/盘整直接负责开仓，太粗；
  - 但让它先回答“现在是不是更像值得放行 long continuation、或至少别去追 short continuation 的压缩释放环境”，仍有一点可救味道。

所以更诚实的读法是：
- 原始 standalone entry 版本 = 已审计消费；
- 但 `compression` 作为 shared admission / veto context，未必已经被同一个 Rank 19 主题本身消费完。

## 3) 有没有“可救信号”？
**有。**

可救信号不在继续调 `box_len / buffer / narrowness`，而在今天新增旁证给出的 **角色降级**：

1. 原 Rank 19 已经证明：
   - `accumulation_ready` 这种宽版结构 breakout，直接拿来当策略会持续亏；
   - `box_breakout_ready` 虽少亏，但交易数过稀，说明它更像“环境筛子”，不像独立 alpha。
2. 2026-03-19 的 `stolgo consolidation asymmetry` digest 给出的快检方向很集中：
   - `close-range compression` 更像 **long-admission**；
   - 对 short 侧则更像 **veto**，而不是对称放大器。
3. 这恰好解释了 Rank 19 原始失败：
   - 问题不一定是“compression 没用”；
   - 更像是“把它写成多空对称、可独立开仓的 breakout family，本身就放大了错位”。

更直白地说：
- Rank 19 留下的最好残余信息，不像“继续做 standalone box breakout”；
- 更像“先压缩、后释放”这件事，可以当作现有三条收口线的 shared allow/deny layer。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀：把 Rank 19 从 standalone `box consolidation breakout` entry，降级成 `close-range compression` shared long-admission + short-veto gate。**

也就是：
- 不再根据 box breakout 本身直接开一笔新交易；
- 只把过去 `N` 根 close 是否处在窄区间，作为现有 `breakout-short / Fib retest_hold / EMA-PSAR` 的 shared gate：
  - long continuation / retest 侧，压缩后释放可放行；
  - short continuation 侧，默认先当 veto / half-size，而不是额外加码。

为什么这算一刀而不是多轴大改：
- 核心主题没变，仍是 `consolidation / compression -> breakout`；
- 数据仍是现有公开 OHLCV；
- 只改了它的 **角色层级**，没有顺手偷换 exit、universe、第二层 regime stack。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 原 `park` 结论完整保留，尤其“standalone structure breakout 不够诚实”这一点不翻案；
- 原 Rank 19 的 blocker 很集中：**宽版持续亏、窄版过稀**；
- 新 digest 提供了一个只改角色、不改主题的窄 reframe：**compression 不再直接开仓，只做 shared admission / veto layer**。

## 6) trade on / trade off 结论
### Proposed derived hypothesis
- `proposed_rank`: `Rank 19b`
- `source_rank`: `Rank 19`
- `single modification axis`: `demote standalone box-consolidation breakout entry into a close-range compression shared long-admission + short-veto gate`
- `trade on`: `不再根据 box breakout 本身直接开仓；而是在固定 lookback（第一轮优先 N=13/21）上计算 close-range compression（例如过去 N 根 close 被压在 max_close*(1-pct) 的窄区间内），再只把它用作 shared allow/deny/sizing gate：compression 成立时优先放行 Fib retest_hold 与 EMA/PSAR long continuation；对 breakout-short 则默认只做 veto / half-size，而不是额外加码。第一轮只测 baseline vs long-admission gate vs short-veto / sizing。`
- `trade off`: `放弃“box consolidation breakout 本身就是可独立交易的结构 alpha”的原 Rank 19 读法，换取更诚实的 compression-release 环境层角色；代价是它不再是独立策略，而且若 compression 阈值过紧，可能只是靠砍单美化结果，因此第一轮必须只测 gate 本身，不偷带新 trigger / exit / second-layer regime。`
- `why now`: `原 Rank 19 clean replication 已很清楚地证明 standalone 宽版结构 breakout 持续为负，而最窄版 box_breakout_ready 又稀到不够 admission；这更像“角色错位”而不是“compression 主题彻底没信息”。2026-03-19 新增的 consolidation asymmetry digest 又正好提供了一个只改角色、不改主题的窄 reframe：close-range compression 更像 shared long-admission + short-veto gate。`
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 19 itself.
It keeps the original `park` intact. The only new move is a narrower role downgrade: **`Rank 19b = stop treating box consolidation as a standalone entry family, and test it only as a close-range compression shared long-admission + short-veto gate for existing lanes.`**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
