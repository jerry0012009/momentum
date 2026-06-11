# 2026-04-23 00:49 UTC — Rank 57 park reframe

## 本轮选择
- `Rank 57`
- 选择原因：继续按 `50+` 优先的低频轮转处理 1 条 parked rank；`Rank 57` 距上次正式 park-reframe（`2026-04-11 15:50 UTC`）已超过 `7` 天，且 4 月 19~22 新增了与 compression / squeeze breakout 直接相关的新 digest，足够支持一次“是否还值得继续派生”的复核。

## 读集
必读：
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`

补充：
- `research/optimization_loop/2026-03-18_1451_rank57-clean-replication-park.md`
- `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
- `research/park_reframe/2026-04-11_1550_rank57-park-reframe.md`
- `research/optimization_loop/2026-04-07_2231_rank57b_compression_admission_forward_to_source_intake.md`
- `research/optimization_loop/2026-04-08_0901_rank57_fresh_intake_first_verdict_background.md`
- `research/optimization_loop/2026-04-17_2159_rank57_freshintake_background_p0_compression_residual_replay_closed.md`
- `research/quant_digests/2026-04-19_1746_bbsqueeze-release-shortbasket-alpha.md`
- `research/quant_digests/2026-04-22_0515_bbcompress-consensus-breakout-shell.md`

## 原 rank 为什么 park
原 `Rank 57 / TTM squeeze release regime gate` 被 park 的原因没有变化：
- 它想把 `TTM squeeze release` 写成横跨 `ema_psar_long / fib_retest_long / breakout_short` 的 shared regime gate；
- 但 `2026-03-18` 的最小 clean replication 只证明了“个别 setup 在大幅砍样本后少亏”，没有证明它能形成跨 setup、跨 lane 的统一增益。

authoritative 冻结结果仍然足够清楚（`6bps/side`）：
- `ema_psar_long`：`base≈-3.68% -> release≈-2.94%`，但 `retention≈13.33%`
- `fib_retest_long`：`base≈+1.17% -> release≈+0.30%`
- `breakout_short`：`base≈-3.55% -> release≈-0.10%`，但 `retention≈25.22%`
- 时间稳定性与 `release 1~4 bars` 参数邻域都没有给出干净、跨 setup 统一的 pocket。

翻成人话：失败对象始终是 **“TTM squeeze release 作为跨 setup shared gate”** 这层职责，而不是 compression / release 主题本身永远无效。

## 它更像 hard park 还是 soft park
**本轮判断：仍是 `soft park`，但已经非常接近 `hard park with consumed residual`。**

为什么还保留 `soft`：
- 原 clean replication 的残余确实主要留在 `breakout_short`；
- 说明“压缩后释放”在 breakout family 里并非纯噪声。

为什么又更接近 `hard`：
- 这条唯一自然残余，已经在 `2026-04-03` 被收窄成 `Rank 57b / breakout-family-local pre-break compression admission`；
- `2026-04-08` fresh-intake first verdict 已把它收口为 `background / P0`；
- `2026-04-17` 又进一步确认：继续 replay 的对象仍只是 breakout-family-local admission layer，不构成新的独立 queue-facing 主语。

所以当前状态不是“还有很多没试过”，而是：**唯一诚实 residual 已被表达、前推、首判并关单。**

## 有没有“可救信号”
**有，但已被消费，不再支持继续派生。**

唯一可救信号一直是：
- `Rank 57` 的 setup asymmetry 明显；
- 残余主要集中在 `breakout_short`，不在 shared gate；
- 所以最自然的改写只能是把旧 shared squeeze gate 降级成 breakout-family-local pre-break compression admission。

但 4 月 19~22 的新证据没有把旧对象救回，反而继续把主题往**新的完整 raw-alpha 宿主**上推：
1. `2026-04-19_1746_bbsqueeze-release-shortbasket-alpha.md`
   - 新证据支持的是 `15m downside squeeze release short basket` 这种完整 raw-alpha 壳；
   - 它说明 compression/squeeze 主题仍有信息，但更像独立 short-basket breakout 宿主，而不是旧 `Rank 57` 的 shared/local gate 再切一刀。
2. `2026-04-22_0515_bbcompress-consensus-breakout-shell.md`
   - 新证据支持的是 `low-vol BB squeeze breakout × EMA/MACD confirmation` 这种完整 breakout shell；
   - 它进一步说明值得追的是新的 volatility-breakout continuation body，而不是回头给 old `Rank 57` 再命名一个 `57c`。

因此本轮的真实判断是：
- compression 主题仍活着；
- 但它活在新的 breakout shell / short-basket 宿主里；
- **不活在 old `Rank 57` 再继续局部派生。**

## 最值得改的唯一一刀是什么
如果还要回答“唯一主修改轴”，答案仍然只有这一刀：

> **把 symmetric TTM squeeze release shared gate 降级成 breakout-family-local pre-break compression admission。**

但这一刀已经被 `Rank 57b` 完整表达，并已在 runtime 中被 first-verdict 收口为 `background / P0`。本轮不再诚实把同一刀换个词重复写成 `Rank 57c`。

## 是否值得形成新的 derived hypothesis
**不值得。最终结论：`keep_park`。**

### 固定回答
1. **原 rank 为什么 park？**
   - 因为 `TTM squeeze release` 作为跨 `ema_psar_long / fib_retest_long / breakout_short` 的 shared regime gate，没有形成统一增益；改善主要来自单一 setup 上的大幅砍样本少亏。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但现在已非常接近 `hard park with consumed residual`。
3. **有没有“可救信号”？**
   - 有；唯一可救信号仍是 breakout-family-local compression admission，但这条残余已经被 `Rank 57b` 诚实消费，并在 fresh-intake/runtime 中正式收口。
4. **最值得改的唯一一刀是什么？**
   - 把 shared squeeze gate 降级成 breakout-family-local pre-break compression admission。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；同一修改轴已经被 draft、前推并收口，近期新证据又把主题推向新的完整 breakout shell / short-basket raw-alpha 宿主，而不是支持 old `Rank 57` 再派生新条目。

## 最小审计结论
- 保留原 `park` verdict；
- 本轮状态：**`keep_park`**；
- `Rank 57` 的唯一诚实 residual 已被 `Rank 57b` 充分表达并被 runtime 消费；
- 4 月 19~22 的新证据没有把 old `Rank 57` 拉回 queue-facing，而是继续说明 compression / squeeze 主题若还有价值，更像新的完整 breakout / short-basket raw-alpha 宿主。

## Git / commit
- `git status --short` 显示工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件；
- 为避免混提，本轮只做最小必要文档更新；
- **不做 commit。**
