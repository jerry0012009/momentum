# 2026-03-31 15:24 UTC — Rank 94 park reframe review

## 为什么这轮看 Rank 94
- 遵循 `bot6` 轮转：本轮继续优先 `80~110` 号段，且最近 `7` 天内未见 `Rank 94` 的 `park_reframe` 复盘记录。
- `Rank 94 / two-bar outside-range follow-through gate` 属于典型“方向并不荒谬，但很容易因为极端砍样本而看起来变好”的 continuation / persistence 命题，适合做一次低频复盘。
- 最近还有一条关键新证据：`2026-03-30_0529_rank1_outside_persistence_intake_blocked_absorbed_by_rank94.md` 已明确说明，`Rank 1` 的 `two-stage outside-persistence` residual 与 `Rank 94` 是同题同边界，而 `Rank 94` 自己已经做过 clean replication 并回到 `park / evidence_pool`。这让本轮能更诚实地判断：该主题是否还值得再单独派生。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/quant_digests/2026-03-19_1448_two-bar-outside-range-followthrough-gate.md`
- `research/optimization_loop/2026-03-19_1512_rank94-two-bar-outside-range-intake.md`
- `research/optimization_loop/2026-03-19_1535_rank94-clean-replication-park.md`
- `research/optimization_loop/2026-03-30_0529_rank1_outside_persistence_intake_blocked_absorbed_by_rank94.md`

## 1) 原 Rank 为什么 park？
原 `Rank 94` 想表达的是：
- 第一根 break 不算数；
- 只有当后续连续两根收盘仍站在父区间外，才把这次 move 当作更诚实的 continuation / path-persistence；
- 作为 `breakout_short / Fib retest_hold / EMA-PSAR` 三条线可共用的 shared persistence gate。

原始 clean replication 给出的 hard verdict 很干净：
1. **`ft_gate` 没有改善，反而更差。**
   - `baseline @6bps ≈ -13.00%`
   - `ft_gate @6bps ≈ -14.03%`
   - `trade_count_retention ≈ 69.65%`
   - 说明“等两根都站在区间外”这件事，并没有把 shared continuation 读法变诚实。
2. **唯一转正的是极窄的 `sft_lite_gate` 小样本 pocket。**
   - `sft_lite_gate @6bps ≈ +3.40%`
   - 但 `trade_count_retention` 只剩 `≈11.87%`
   - 这更像极端砍样本后的局部 pocket，不像 desk 可继续占位的 shared gate。
3. **`baseline_half_ft_full` 也没把事情救回来。**
   - 它只是把平均仓位压到 `≈82.82%`
   - `mean_total_return ≈ -13.55%`
   - 跨资产仍只有 `1/3` 为正
4. **最近的新运行态证据又补了一刀。**
   - `2026-03-30_0529_rank1_outside_persistence_intake_blocked_absorbed_by_rank94.md` 明确记账：
   - `Rank 1b / two-stage outside-persistence continuation gate` 与 `Rank 94` 在对象层面已经重合；
   - 而 `Rank 94` 本身已完成 clean replication 并回 `park / evidence_pool`。

翻成人话：
**Rank 94 被 park，不是因为“outside persistence” 这个主题毫无信息，而是因为把它写成三线共用的 shared continuation gate 后，真正站得住的只剩一个极窄小样本 pocket；更宽、更诚实的 shared 写法已经被 clean replication 否掉。**

## 2) 它更像 hard park 还是 soft park？
我的判断：**`soft park`，但现在已经很偏 hard。**

为什么不是纯 hard park：
- “第一根 break 不够，要看后续 path persistence” 这个方向本身并不荒谬；
- `sft_lite` 至少证明，极少数连续推进很干净的 break 之后，确实可能有 continuation pocket。

为什么又说“很偏 hard”：
- 这个 pocket 的成立高度依赖极端 retention；
- `ft_gate` 与 `baseline_half_ft_full` 都没把 shared 读法救活；
- 更关键的是，最近 `Rank 1` 的同主题 residual 已经被正式认定为 **被 Rank 94 吸收**，而不是值得再独立前排 intake；
- 也就是说，这条血缘里最自然的窄救法，已经被 `Rank 94` 自己消费并失败过了。

所以主题不算完全死透，但对 **Rank 94 这版 queue-facing shared persistence gate** 来说，已经接近 hard enough。

## 3) 现有证据里有没有“可救信号”？
**有，但只剩一个很薄的 continuation pocket，而且不足以再诚实派生。**

### 可救信号
1. **`sft_lite` 小样本正 pocket 说明“连续两根真正推进”并非纯噪声。**
   - 不是所有 persistence 读法都错；
   - 真正更干净的推进形状，确实比单根 break 更有信息量。
2. **outside-persistence 主题后来还被 `Rank 1b` 重新提炼过。**
   - 这说明 desk 也承认：原始 breakout 主题的残余价值，最自然就是收敛到 `two-stage outside-persistence` 这一刀。

### 但为什么它不够救回 Rank 94
- 这条 pocket 已经被 `Rank 94` 自己做过最小 clean replication；
- 并且 `Rank 1 residual` 再次想进入 front-slot 时，也被明确拦下，理由正是：**它和 Rank 94 同题同边界，而 Rank 94 已经 park**；
- 换句话说：
  - 不是没有 residual；
  - 而是这条 residual 已经被“最诚实的近邻对象”消耗过，当前没有新证据把它重新抬出 `park`。

## 4) 最值得改的唯一一刀是什么？
如果硬要保留唯一主修改轴，最自然的一刀仍然只有：

**把“第一根 break”改成“只有后续两根仍站在父区间外才承认 continuation”。**

也就是 `two-stage outside-persistence / two-bar outside-range follow-through` 这条轴。

但问题在于：
- 这已经不是“本轮新发现”；
- 它就是 `Rank 94` 自己的主轴，也是 `Rank 1b` 后来试图复用的主轴；
- 而且这条主轴已经做过 clean replication，并被运行态记账为“已吸收且已失败”。

所以：
- **它仍然是最值得改的唯一一刀；**
- **但它不是今天值得新 draft 的一刀。**

## 5) 是否值得形成新的 derived hypothesis？
**本轮结论：不值得，维持 `keep_park`。**

原因有四个：
1. 原 `park` 的审计意义很强，不能推翻：
   - shared `FT` 读法已被 clean replication 清楚否掉；
2. 唯一可救信号只剩 `sft_lite` 极窄 pocket，太依赖缩样本；
3. 最近新证据不是给出新的 distinct axis，而是在说明：
   - `Rank 1b` 的同主题 residual 已被 `Rank 94` 吸收；
4. 如果现在硬写 `Rank 94b`，大概率只是在重复表述：
   - “outside persistence 是 continuation 的更诚实 gate”，
   - 但这正是 `Rank 94` 已经测过、且不够 queue-facing 的对象。

换句话说：
- **不是完全没有可救语义；**
- 但这条语义已经被现有血缘对象消费过，当前没有新的 distinctness 支撑再诚实派生 `Rank 94b`。

## 6) 如果硬要派生，trade on / trade off 会是什么？
本轮不 draft 新假设，但为审计完整性，记录一下如果硬要派生，它只可能是什么：
- **trade on**：只在原 breakout / continuation 事件已触发后，额外读取 two-stage outside persistence（后续两根仍站在父区间外）作为 continuation allow / size-up；默认不改原 trigger / exit。
- **trade off**：彻底放弃“第一根 break 已足够说明 continuation”的读法；但这条线已与 `Rank 94` 本体、以及被拦下的 `Rank 1b` 完全重叠，再独立起新 rank 只会重复记账。

因此本轮选择：**保留这条 residual 作为已知经验，但不新开 `Rank 94b`。**

## 本轮按模板回答
1. **原 rank 为什么 park？**
   - 因为 shared `two-bar outside-range follow-through` 在最小 clean replication 下没有诚实改善；`ft_gate` 反而更差，`sft_lite` 只剩 `≈11.87%` retention 的极窄 pocket。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但已很偏 hard。
3. **有没有“可救信号”？**
   - 有；但只剩极窄的 `sft_lite` continuation pocket，而且该主题残余已被 `Rank 94` / `Rank 1b` 这组对象消费过。
4. **最值得改的唯一一刀是什么？**
   - `first break -> two-stage outside-persistence continuation gate`。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不写 `Rank 94b`？**
   - 因为唯一主修改轴已经被 `Rank 94` 本体和后续 `Rank 1b` 残余完整消费；最近新证据是在确认“它已被吸收且已失败”，不是在提供新的 distinct residual。

## 最终结论
- `Rank 94` 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 94 更像 soft park，但已经很偏 hard；它唯一留下的 residual 仍是 two-stage outside-persistence 这条 continuation 语义，而这条语义已被 Rank 94 本体和后续 Rank 1b 尝试完整消费并记账为已吸收，当前不诚实再派生 Rank 94b。**

## 队列写回
建议在 `docs/PARK_REFRAME_QUEUE.md` / `research/park_reframe/INDEX.md` 中登记为：
- `2026-03-31 15:24 UTC | Rank 94 | verdict=keep_park | original verdict kept=park | note=soft park，但已很偏 hard；原 Rank 94 的 two-bar outside-range follow-through shared persistence gate 已被 clean replication 审清：ft_gate 反而更差，唯一正 pocket 只剩 retention≈11.87% 的 sft_lite；而 2026-03-30 的运行态又明确记账 Rank 1 的同主题 residual 已被 Rank 94 吸收且 Rank 94 本身已 park，因此当前不诚实再派生 Rank 94b`

## Git / 风险备注
- 本轮只做最小必要文件改动。
- 当前工作区长期存在大量与本轮无关的脏文件；为避免混提，本轮不做 commit。
