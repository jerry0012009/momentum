# 2026-03-25 11:29 UTC — Rank 53 park reframe review

- source rank: `Rank 53`
- original verdict kept: `park`
- this round verdict: `keep_park`
- touched lane: `close-confirmed CHoCH compression gate`

## 为什么这轮选它
- 按 `bot6` 当前轮转规则，继续优先看 `50~79` 号段里已 `park`、且最近 `7` 天未被 `park-reframe` 复盘过的条目。
- `Rank 53` 先前未进入 `park_reframe` 最近复盘名单，且它属于典型“结构确认层是否还有残余信息”的旧 park 条目，适合低频抽查一轮。

## 1. 原 rank 为什么 park？
- 原 clean replication（`2026-03-18_1102_rank53-clean-replication-park.md`）测试的是把 `1h close-confirmed CHoCH / liquidity_sweep_veto` 压到现有 `15m` base setups 上。
- 最能看的主读法 `breakdown_reclaim_short + liquidity_sweep_veto @ 6bps/side` 结果仍然偏负：
  - `mean_total_return ≈ -2.88%`
  - `positive_asset_ratio = 0/3`
  - `mean_trade_count_retention ≈ 39.97%`
- 它不是完全没信息：亏损比 base 略收窄；但改善主要来自显著砍样本，而不是形成能跨资产站住的正 pocket。
- time-pocket 也没有出现“最近一段已转正”的干净信号，因此原结论被压回 `park / evidence pool` 是合理的。

## 2. 它更像 hard park 还是 soft park？
- 结论：**soft park，但偏硬**。
- 原因：
  - 不是纯 hard fail，因为 `wick vs close acceptance` 这层结构语义确实有一点点信息量，至少比“看见 wick 就翻向”更诚实。
  - 但它的残余价值已经很薄：一旦按 desk 口径做成可交易、可计成本、可跨资产的 15m gate，改善幅度不够，且 retention 掉得太快。

## 3. 有没有“可救信号”？
- 有，但很弱，而且更像**旁支残余信息**，不是足够支撑新 rank 的主故事：
  1. `close-confirmed` 确实比 `wick-only` 更少误翻向；
  2. 2026-03-19 的新 digest `breakout-reentry-inside-sequence-failure-verdict` 提醒我们：残余信息更像“先外扩、再收回区间内”的 **failure verdict**，而不是把 CHoCH/compression 本身继续当 shared trend gate。
- 问题在于：这条“失败后回内”的更诚实读法，已经被邻近家族基本吸收：
  - `Rank 31b` 已把 false structural reclaim 改写成 short failure-followthrough；
  - `Rank 33`/相关 failure-verdict digests 也在消费“假破 / 回内 / 失败序列”的同类信息。
- 所以这里的“可救信号”更像是：**原 Rank 53 不是完全胡扯，但它剩下的那点信息已经被更贴题的 failure 家族拿走了。**

## 4. 最值得改的唯一一刀是什么？
- 如果硬要写唯一一刀，最自然的一刀是：
  - **把 `close-confirmed CHoCH compression gate` 从 shared trend-flip gate，降级成 `outside-close -> back-inside-close` 的 post-break failure verdict overlay。**
- 但这刀本轮不建议真的起草为 `Rank 53b`，因为：
  - 它已经不再是原 Rank 53 的自然延长，而是在语义上滑向了更通用的 breakout failure 家族；
  - 这条轴已经被 `Rank 31b` 与近期 failure-verdict digests 先占了位置，再起一个 `Rank 53b` 只会重复讲同一个故事。

## 5. 是否值得形成新的 derived hypothesis？
- **不值得。**
- 本轮最终判断：`keep_park`。
- 原因不是“完全没可救信号”，而是：
  - 可救信号太弱；
  - 且最自然的新写法已被邻近 rank / digest 家族消费；
  - 现在再派生 `Rank 53b`，更像重复包装，而不是新增一个 bot2 值得认真入板判断的窄假设。

## 6. trade on / trade off 怎么看？
- 本轮不形成新的 derived hypothesis，因此不正式起草 `trade on / trade off`。
- 仅保留一句审计备注：若未来有人重新碰这条线，唯一仍值得记住的是——**trade on failure verdict，不 trade on CHoCH gate 本身。** 但在当前队列里，这个残余已经有更好的宿主，不需要 `Rank 53b` 再占一个坑。

## 最终结论
- `Rank 53` 原 `park` verdict 保留。
- 分类：`soft park`，但偏硬。
- 本轮不新增 `derived hypothesis`，不改 `TODO` 顶部排班。

## 文件更新
- 已追加：`research/park_reframe/INDEX.md`
- 已更新：`docs/PARK_REFRAME_QUEUE.md`

## commit
- 未做 git commit。
- 原因：当前工作区存在大量与本轮无关的已修改/未跟踪文件，且 `docs/PARK_REFRAME_QUEUE.md`、`research/park_reframe/INDEX.md` 也已带有其他并发脏改；此时不适合做安全 selective commit。
