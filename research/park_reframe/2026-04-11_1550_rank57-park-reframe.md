# 2026-04-11 15:50 UTC — Rank 57 park reframe

## 本轮选择
- 本轮继续按 queue-facing 低频轮转，只处理 1 条已 `park` rank。
- 虽然 brief 顶部有一处“`Rank 1~37`”的旧范围描述，但当前执行规则、queue 与近期 bot6 轮转都以 `50+` 优先为准；本轮沿用这一审计口径。
- `Rank 57` 上次正式 park-reframe 是 `2026-04-03 06:56 UTC`，已超过 `7` 天；且这 8 天里它的已派生残余 `Rank 57b` 还经历了前推与 fresh-intake first verdict，已经形成足够新的 runtime 证据，适合回头做一次“是否还值得继续派生”的收口复盘。

## 读集
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_1451_rank57-clean-replication-park.md`
- `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
- `research/optimization_loop/2026-04-07_2231_rank57b_compression_admission_forward_to_source_intake.md`
- `research/optimization_loop/2026-04-08_0901_rank57_fresh_intake_first_verdict_background.md`
- `research/quant_digests/2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`

## 原 rank 为什么 park
原 `Rank 57 / TTM squeeze release regime gate` 被 park 的 blocker 没变：
- 它试图把 `TTM squeeze release` 写成横跨 `ema_psar_long / fib_retest_long / breakout_short` 的 shared regime gate；
- 但最小 clean replication 只证明了“个别 setup 大幅砍样本后少亏”，没有证明它能形成跨 setup、跨 lane 的统一 queue-facing 改善。

authoritative 冻结结果（`6bps/side`）仍然很清楚：
- `ema_psar_long`：`base≈-3.68% -> release≈-2.94%`，但 `retention≈13.33%`
- `fib_retest_long`：`base≈+1.17% -> release≈+0.30%`
- `breakout_short`：`base≈-3.55% -> release≈-0.10%`，但 `retention≈25.22%`
- 时间稳定性与 `release 1~4 bars` 参数邻域都没有给出干净、统一、可迁移的 pocket

翻成人话：
**失败对象一直都是“TTM squeeze release 作为跨 setup shared gate”这层职责，而不是 compression→release 主题永远无效。**

## 它更像 hard park 还是 soft park
**结论：仍然是 `soft park`，但现在已经比 4 月 3 日那轮更接近 `hard park`。**

为什么还没彻底变成 hard：
- 原始 clean replication 的 residual 确实主要留在 `breakout_short`；
- 这说明“先压缩、后释放”的 breakout-family 语义不是纯噪声。

为什么又更接近 hard：
- 这条 residual 在 `2026-04-03` 已经被最自然地收窄成 `Rank 57b`；
- 随后的 `2026-04-07` 前推判断，只是确认它**足够具体，可以当 fresh/source-intake 问题去问**；
- 但 `2026-04-08` 的 fresh intake first verdict 又把它直接收口为 `background / P0`：它仍只是 breakout-family-local admission layer，不是独立 queue-facing raw-alpha 主语。

因此现在的状态更像：
**soft residual 已经被诚实消费过一次，并且运行态 first verdict 没把它抬成独立对象。**

## 有没有“可救信号”
**有，但这条可救信号已经被消费完，且不再支持继续派生。**

这条唯一可救信号仍然是：
- `Rank 57` 的 setup asymmetry 很明显；
- 残余主要集中在 `breakout_short`，不在 shared gate；
- 所以最自然的改写只能是把旧 shared squeeze gate 降级成 breakout-family-local pre-break compression admission。

但最新 runtime 证据又把这条残余压得更清楚：
1. `2026-04-08_0901_rank57_fresh_intake_first_verdict_background.md`
   - 已明确写明：这条 residual 仍只是给旧 breakout family 提供 local admission / participation filter；
   - 还没有形成独立、queue-facing、单轴的新 raw alpha intake。
2. `2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`
   - 也继续说明：compression / squeeze release 若还值得追，更像**完整 breakout / continuation raw-alpha 壳**，重点在 quality-weighted admission / sizing / ATR risk shell；
   - 而不是回头再给旧 `Rank 57` 多切一层更薄的 shared-gate 派生。

所以本轮的真实答案是：
**可救信号不是没有，而是已经被 `Rank 57b` 这一刀充分表达；再往下切只会变成重复命名。**

## 最值得改的唯一一刀是什么
如果还要回答“唯一主修改轴”，答案没有变化，仍然只有这一刀：

> **把 symmetric TTM squeeze release shared gate 降级成 breakout-family-local pre-break compression admission。**

但这一刀已经在 `2026-04-03` 被完整 draft 成 `Rank 57b`，随后又在 `2026-04-08` 被 first verdict 收口到 `background / P0`。

因此本轮不再诚实把它继续写成 `Rank 57c`，也不把同一刀换个说法再记一次。

## 是否值得形成新的 derived hypothesis
**不值得。最终结论：`keep_park`。**

### 模板回答
1. **原 rank 为什么 park？**
   - 因为 `TTM squeeze release` 作为跨 `ema_psar_long / fib_retest_long / breakout_short` 的 shared regime gate，没有形成统一增益；改善主要来自单一 setup 上的大幅砍样本少亏。
2. **它更像 hard park 还是 soft park？**
   - 仍是 `soft park`，但比 4 月 3 日那轮更接近 `hard park`。
3. **有没有“可救信号”？**
   - 有；唯一可救信号仍是 breakout-family-local compression admission，但这条残余已经被 `Rank 57b` 诚实消费，并在 fresh intake first verdict 后压回 `background / P0`。
4. **最值得改的唯一一刀是什么？**
   - 把 shared squeeze gate 降级成 breakout-family-local pre-break compression admission。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；这条唯一修改轴已经被 draft 并被运行态消费，当前不诚实再派生 `Rank 57c`。

## 最小审计结论
- 保留原 `park` verdict；
- 本轮状态记为 **`keep_park`**；
- `Rank 57` 的唯一诚实 residual 已被既有 `Rank 57b` 充分表达，并在后续 first verdict 中收口为 `background / P0`；
- 4 月上旬新增的 squeeze/compression 证据继续把主题上移到新的 breakout / continuation raw-alpha 壳，而不是支持从旧 `Rank 57` 再诚实派生新条目。

## Git
- 当前 repo 存在大量无关脏文件与未跟踪文件；本轮只做 park-reframe 最小文本更新。
- 不改 `docs/TODO.md`，也不做混合 commit。
