# 2026-04-09 02:44 UTC · Rank 71 park reframe review

## Scope
- source rank: `Rank 71 / EMA-VWAP-ATR-volume graded admission score`
- source status kept: `park`
- this round verdict: `soft_reframe_candidate`
- single modification axis considered: `把 graded admission score 从四档等权打分，收窄成 extreme-only 的 high-conviction binary gate / veto`

## Why Rank 71 this round
- 按 `bot6` 轮转，当前仍优先补 `50~79` 号段。
- `docs/PARK_REFRAME_QUEUE.md` 最近 7 天没有复盘过 `Rank 71`。
- `Rank 71` 属于典型“原方向未必全死，但角色/写法可能摆错”的 parked 条目，适合低频检查是否还有新的窄 reframe 空间。

## What the original rank was trying to do
原始假设不是直接发明一个新 entry，而是把 `EMA 结构 + VWAP 相对位置 + ATR/波动位置 + volume` 组合成一个 `0~100` 的 admission score：
- 分数高才放行 `15m continuation / retest_hold` 一类机会；
- 分数低则少做或不做；
- 默认假设是：**这些部件的等权叠加，能比单一 trigger 更诚实地筛掉假突破 / 假续行。**

## Why it was parked
依据原 clean replication（`2026-03-18_2345_rank71-clean-replication-park.md`），它被 park 的核心原因不是“高分完全没改善”，而是：
1. **改善主要是 relative-better，不是 decisive。**
   - baseline 仍明显负。
   - `score>=60` 只是少亏。
   - `score>=75` 在低成本口径下接近打平，但不是稳定、跨成本都站得住的正 edge。
2. **一旦成本更诚实，薄优势就塌。**
   - 原结论明确写到：`score>=75` 在 `6bps` 仅接近打平；到 `10/15/20bps` 又重新转负。
3. **改善很大程度来自 trade retention 下滑。**
   - `score>=60` 与 `score>=75` 都有明显砍样本；后者更稀。
   - 这更像“少做差单”，还不像“留下真正强单”。
4. **组件职责重叠。**
   - `EMA / VWAP / trigger / ATR / volume` 同时都在表达“趋势、位置、确认”，容易变成好看但重复的多项打分。
5. **VWAP anchor 在 crypto 24/7 里先天可疑。**
   - 原 source-intake 自己就把 `session VWAP` 标成潜在弱点；这不是后来才发现的问题。

## Hard or soft park?
我判断它是 **soft park，但已经往 hard park 靠**。

为什么不是 hard park：
- 原 clean replication 至少说明“高分桶比低分桶更像 continuation”，不是全无信息；
- 说明它还有一点 admission 价值残余。

为什么又不该太乐观：
- 这点残余目前仍主要靠砍交易数换来；
- 成本一抬就塌；
- 近期新 digest 也更像把这类信息往完整 trend shell 宿主推，而不是支持继续救原始 `graded score` 结构。

## Is there any salvage signal?
有，但很有限，只够到 `soft_reframe_candidate`：
- 原 replication 里，**真正留下残余信息的不是“四档分数体系”本身，而是极高分那一小撮 trade。**
- 这说明“多组件一起同向共振”可能仍有信息，问题更像：
  - 不该继续保留 mid-score / 渐进式打分；
  - 也不该把它写成一个完整、独立的 graded framework。

同时，近期 `quant_digests` 新证据（如 `HTF EMA gate × 15m RSI pullback continuation`、`VWAP-EMA directional change × asymmetric trend shell`）给出的方向也很一致：
- `EMA/VWAP` 更像完整 trend shell 里的 context / confirmation 组件；
- 不像一个独立可扩展的等权评分门。

这反而压低了继续派生 `Rank 71b` 的确定性。

## The single best cut
如果以后真要再救，最值得改的唯一一刀是：

**把“四档等权 graded admission score”收窄成 extreme-only 的 binary gate / veto，只测试最高共振桶是否值得放行；中段分数一律不再赋予额外语义。**

这刀的含义：
- 不改主题，仍然只看 `EMA/VWAP/ATR/volume` 这一组；
- 但放弃“分数越高越好、60/75 分都可以形成分层框架”的原写法；
- 改成只问一句：**只有极高共振时，是否值得 allow；否则默认不加分。**

## Should this become a new derived hypothesis now?
**不值得现在直接 draft 成新的 derived hypothesis。**

原因：
1. 这条唯一可改轴，目前还缺“为什么 extreme-only 不是继续砍样本美化”的新证据；
2. 近期新 evidence 更支持把 `EMA/VWAP` 吸收到新的 trend-shell 宿主，而不是继续扩写旧 `Rank 71`；
3. 当前若直接写 `Rank 71b`，大概率只是把原来的 mid/high score 思路换个阈值重讲，审计增量不够大。

## This round conclusion
- 原 rank 为什么 park？
  - 因为它只做到 relative-better，没有做到 post-cost decisive；而且高分改善显著依赖 trade retention 下滑与组件重叠。
- 更像 hard 还是 soft park？
  - `soft park`，但已经偏硬。
- 有没有可救信号？
  - 有，主要集中在 extreme high-conviction 桶，而不是整个 graded score 框架。
- 最值得改的唯一一刀是什么？
  - 把 graded score 收窄成 `extreme-only binary gate / veto`，不再保留 mid-score 分层叙事。
- 是否值得形成新的 derived hypothesis？
  - 现在还**不值得**；证据只够保留成 `soft_reframe_candidate`。

## Files checked
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_2326_rank71-source-intake.md`
- `research/optimization_loop/2026-03-18_2345_rank71-clean-replication-park.md`

## Commit status
- 未提交。
- 原因：git 工作区已有无关脏文件；本轮按要求仅做最小必要改动，避免混提。
