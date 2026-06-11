# 2026-03-18 17:25 UTC · Rank 25 park reframe review

## Scope
- Source rank: `Rank 25 EMA + Donchian breakout confirmation`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 25 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_1513_rank30-park-reframe.md`
  - `research/park_reframe/2026-03-18_1314_rank26-park-reframe.md`
  - `research/park_reframe/2026-03-18_1036_rank18-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0610_rank25-ema-donchian-p2.md`
  - `research/optimization_loop/2026-03-17_0623_rank25-time-redwatch-park.md`
  - `reports/site/factors/scout_ema_donchian_breakout_15m/report.html`
  - `research/quant_digests/2026-03-18_1707_regime-matrix-shared-state-gate.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- It is one of the clearest `park-but-not-hopeless` ranks: the original line once got as far as temporary `P2`, then got honestly cut back only because **time stability kept repeating `bucket_1负 / bucket_2正 / bucket_3负`**.
- That makes it a good fit for `bot6`: keep the original park intact, and ask whether there is **one narrow axis** that specifically targets the regime/time-pocket blocker, instead of pretending the whole story was wrong.

## 1) 原 rank 为什么 park？
Rank 25 被 park，不是因为 `EMA + Donchian breakout` 完全没 edge，而是因为它在最关键的诚实检查上，**没能证明这条 edge 不是只活在中段时间 pocket 里**。

原始 `P2` 证据其实很强：
- `ema_donchian_l30_c3 @ 6bps/side`：`mean_total_return≈+16.83%`
- `positive_asset_ratio=3/3`
- `mean_trades≈33.67`
- 成本梯度下仍保留正 pocket：`10/15/20bps ≈ +13.74% / +10.00% / +6.37%`
- 参数邻域里 `l30_c3 / l40_c3` 都是正 pocket

但真正把它压回 `park` 的那次最小诚实检查也很直接：
- 主变体 `l30_c3` 出现 `bucket_1负 / bucket_2正 / bucket_3负`
- 邻近正 pocket `l40_c3` 也重复同样结构
- 就算诚实缩到 `ETH+SOL-only`，时间三桶仍然只有中段为正

更直白地说：
- 问题不是 `Donchian breakout` 没选到参数；
- 也不是跨资产 / 成本一碰就碎；
- 问题是 **它更像在吃某种阶段性环境，而不是一条足够平稳的 continuation 语法**。

所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 它不是全线硬 fail，反而是曾经最接近升格的 parked rank 之一；
- 原始 clean replication 与成本/参数/跨资产读法都不差；
- 真正的 blocker 很集中：**time/regime instability**，而不是“这个方向天生不行”。

但它也还不能直接重开原 rank，因为：
- 那次 honest recheck 已经说明时间问题不是单点热像素；
- 继续沿原写法硬推，等于无视已经做过的审计结论。

所以更诚实的读法不是“把 park 推翻”，而是：
- 原 Rank 25 仍该保留为 `park / evidence pool`；
- 但它留下了一条很明确的可重写方向。

## 3) 有没有“可救信号”？
**有，而且信号相当清楚。**

当前可救信号主要有四点：
1. 原始主变体不是少亏，而是 **跨资产、成本、邻域都曾经给出真 pocket**；
2. 被压回 park 的核心原因很集中，不是多项硬 fail 同时爆炸；
3. 时间结构呈现很明确的 `负 / 正 / 负` 三段式，像环境不对，而不像信号骨架彻底坏掉；
4. 最新 quant digest 已经提供一条与这个 blocker 高度同构、且足够窄的救法：**4-state regime matrix shared allow/deny gate**。

翻成人话：
- Rank 25 更像“entry 有东西，但不该在所有 15m 环境里一视同仁地开火”；
- 如果要救，它最自然的一刀不是继续磨 Donchian 参数，而是补一层 **什么时候允许这类 breakout continuation 出手** 的上层状态门。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀：保留原 `EMA bias + Donchian breakout confirmation` entry，不改 entry 结构，只增加一个上层 `4-state regime matrix allow/deny gate`。**

也就是：
- 保留原来的方向与 breakout 确认骨架；
- 不再默认所有 bar 都允许 `l30_c3 / l40_c3` 这类 Donchian continuation 出手；
- 只在上层 `30m` regime 属于 `Trend / Expansion`，或至少不是 `Mean Reversion` 时，才放行；
- 第一轮先做最窄表达：`no-MR gate` 或 `trend-expansion only`，不要同时偷渡 adaptive EMA / ATR 宽度 / 新 exit。

为什么这是一刀而不是多轴：
- timeframe 不改；
- universe 不改；
- entry trigger 不改；
- hold / execution 不改；
- 只改一件事：**原 Rank 25 什么时候被允许出手。**

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 原 `park` 保留完整审计意义；
- 原 rank 的失败非常集中，确实像“缺 regime allowance”，而不是“entry 故事全错”；
- 最新 digest 正好给出一条与该 blocker 高度对位、且可用公开 OHLCV 快速复刻的 shared state gate；
- 这不是无边界重写，而是非常窄的“给原 entry 补一层 allow/deny 环境门”。

## 6) trade on / trade off 结论
### Proposed derived hypothesis
- `proposed_rank`: `Rank 25b`
- `source_rank`: `Rank 25`
- `single modification axis`: `add a 30m 4-state regime matrix allow/deny gate on top of the original EMA+Donchian breakout confirmation`
- `trade on`: `保留原 Rank 25 的 1h EMA bias + Donchian breakout confirmed-close entry；只在上层 30m regime 属于 Trend / Expansion（或最小版先只排除 Mean Reversion）时，才允许按 next-bar open 入场`
- `trade off`: `放弃“所有 15m 环境都平权允许 breakout continuation 出手”的原口径，换取更贴合 time-redwatch blocker 的环境许可层；代价是 trade count 可能下降，而且若 regime classifier 太噪，会退化成切样本美化，因此第一轮必须只测 gate 本身，不偷带 adaptive EMA / stop / exit`
- `why now`: `原 Rank 25 的 clean replication 曾显示跨资产/成本/参数邻域都留有真 pocket，而最终 park 的主因非常集中——时间三桶反复出现 bucket_1负 / bucket_2正 / bucket_3负；最新 regime-matrix digest 又恰好提供了一个针对“环境许可”而非“entry 再改写”的单轴窄救法`
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 25 itself.
It keeps the original `park` intact, while drafting only one narrow follow-up idea: **`Rank 25b = keep EMA+Donchian breakout confirmation, but only allow it to fire when a simple 30m regime matrix says the environment is continuation-friendly.`**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
