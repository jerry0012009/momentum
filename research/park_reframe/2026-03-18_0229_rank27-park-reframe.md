# 2026-03-18 02:29 UTC · Rank 27 park reframe review

## Scope
- Source rank: `Rank 27 Mt.Gox neckline confirmation / pattern-complete breakout gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 27 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_0022_rank34-park-reframe.md`
  - `research/park_reframe/2026-03-17_2222_rank35-park-reframe.md`
  - `research/park_reframe/2026-03-17_2022_rank32-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0815_rank27-mtgox-neckline-clean-replication.md`
  - `research/quant_digests/2026-03-18_0226_breakout-retest-atr-bounce-gate.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- Its original evidence does not read like a total idea collapse. More precisely: adding confirmation clearly changed the shape of the result, but the current confirmation style still was not honest enough.
- That makes it a better reframe candidate than ranks whose core signal stayed uniformly bad under every nearby framing.

## 1) 原 rank 为什么 park？
Rank 27 被 park，不是因为“结构 breakout 完全没戏”，而是因为当前冻结的 `neckline confirm / retest_hold` 版本**没有同时做到收益改善与假突破显著下降**。

原 clean replication 关键证据：
- `raw_breakout @ 6bps/side`：`mean_total_return≈-13.79%`、`positive_asset_ratio=0/3`、`mean_false_break_ratio≈71.56%`
- `neckline_confirm @ 6bps/side`：`mean_total_return≈-17.42%`、`positive_asset_ratio=0/3`、`mean_false_break_ratio≈62.50%`
- `neckline_confirm_plus_retest_hold @ 6bps/side`：`mean_total_return≈-3.03%`、`positive_asset_ratio=0/3`、`mean_false_break_ratio≈68.67%`

更直白地说：
- `neckline_confirm` 的确把假突破率压低了一些，但收益更差；
- `retest_hold` 版本又把亏损显著收窄了，但并没有把假突破率一起拉到足够干净；
- 所以原 rank 当前最诚实的读法仍然是：**确认层方向可能有价值，但这版确认写法还不够好，不能据此撤销 `park`。**

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 从 `raw_breakout -> neckline_confirm_plus_retest_hold`，亏损从约 `-13.79%` 收窄到约 `-3.03%`，说明这条线不是“加确认也没差”；
- 真正的问题更像是：当前 `retest_hold` 仍然写得太硬、太二元，导致它没有把 continuation 和 failed breakout 更诚实地分开；
- 也就是说，blocker 更像“确认层定义还不够像真实执行语义”，而不是“pattern-complete breakout 方向已经被彻底判死”。

所以这条线更接近 **保留原 park 的 soft park**，而不是 hard park。

## 3) 有没有“可救信号”？
**有。**

最值得保留的可救信号有两个：
1. 原 clean replication 已经证明：比起 `raw_breakout`，加入 `retest_hold` 后，损失明显收窄；
2. 刚加入的外部旁支证据 `2026-03-18_0226_breakout-retest-atr-bounce-gate.md` 给了一个更贴近执行面的解释：
   - retest 不该被写成“碰回那根线就算”；
   - 更像应该写成 **`ATR 弹性回踩区 + bounce reclaim`**；
   - 也就是允许价格在突破位附近有一个可容忍的波动带，再看是否重新站回 / 压回方向侧。

这两个信号连起来，说明：
- `Rank 27` 的问题未必在“neckline breakout 不行”；
- 更可能在于**当前 retest 定义过于僵硬，没把真正的 continuation bounce 与普通回落分开。**

## 4) 最值得改的唯一一刀是什么？
**唯一主修改轴：把当前二元 `retest_hold`，改写成 `ATR-scaled retest zone + bounce reclaim`。**

保持不变的部分：
- 仍保留 `pattern-complete + neckline breakout` 的前置语义；
- 仍保留 `next-bar open` 的执行口径；
- 仍保留当前最小 clean-room 的 stop / target / time-stop 框架；
- 不换 universe，不换 exit，不扩成多过滤器大礼包。

唯一改变的是确认层定义：
- 旧：回踩后“留在 neckline 外”就算 hold；
- 新：回踩必须发生在 neckline 附近的 `ATR` 容忍区内，随后要出现一次方向一致的 `bounce reclaim` 才触发。

## 5) 是否值得形成新的 derived hypothesis？
**值得，结论：`derived_hypothesis_drafted`。**

理由不是原 rank 已翻案，而是：
- 当前 evidence 已显示确认层方向确实影响结果；
- 新旁支证据又给出了一个足够窄、足够可执行、且更贴近 15m 实盘语义的单轴改写；
- 这条改写可以写成 `bot2` 后续是否入板都能直接判断的短提案，而不需要现在就动 `TODO` 顶部排班。

## 6) Drafted derived hypothesis
- `proposed_rank`: `Rank 27b / Rank 27 ATR retest bounce reclaim`
- `source_rank`: `Rank 27`
- `status`: `derived_hypothesis_drafted`
- `single modification axis`: `replace binary neckline retest_hold with ATR-scaled retest zone + bounce reclaim`
- `trade on`: `先保留双低点/颈线完成 + neckline breakout；随后只在价格于 1~8 根 15m bar 内回到 neckline 附近（例如 <=0.5 ATR）的弹性回踩区，并出现一次方向一致的 bounce reclaim 后，按 next-bar open 入场`
- `trade off`: `若回踩过深（例如 close 反向穿越 neckline 超过 1 ATR）、或超时仍未完成 retest、或没有 bounce reclaim，则 setup 直接取消；不再把“只是留在 neckline 外”视为足够确认`
- `trade on / trade off summary`: `保留 pattern-complete breakout 的主故事，但把确认层从“静态 retest_hold”改成“波动率缩放的回踩区 + 二次站回”`
- `trade on`: 更有机会把普通 noise retest 与真正 continuation bounce 分开
- `trade off`: 交易数大概率继续下降，且若 ATR 区间设得不诚实，也可能只是把样本再压薄
- `why now`: 原 rank 已显示 `retest_hold` 至少把亏损明显收窄；新 digest 又直接指出 15m retest 更像 `ATR elastic zone + reclaim` 而不是固定线位触碰，因此现在有了一个足够窄、且与原 blocker 正对的唯一改刀
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 27 itself.
It only records that if the desk later wants one narrow salvage attempt from the parked pool, the most honest single-axis derivative is:
**`Rank 27b = keep neckline completion, but replace static retest_hold with ATR-scaled retest zone + bounce reclaim`.**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区仍有无关脏文件，当前不适合安全地 selective commit。
