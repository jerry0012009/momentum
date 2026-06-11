# 2026-04-10 06:11 UTC · Rank 89 park reframe review

## Scope
- source rank: `Rank 89 / outside-close -> back-inside-close failure verdict`
- original status kept: `park`
- this round verdict: `soft_reframe_candidate`
- review reason: 位于 `80~110` 轮转带内，且最近 `7` 天未见同 rank 的 bot6 复盘记录；本轮只处理这一条，不改 `TODO` 顶部排班。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-10_0030_rank68-park-reframe.md`
- `research/park_reframe/2026-04-09_0244_rank71-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-19_1219_rank89-outside-inside-intake.md`
- `research/optimization_loop/2026-03-19_1252_rank89-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-03-19_1059_breakout-reentry-inside-sequence-failure-verdict.md`
- `research/quant_digests/2026-03-22_2028_dc-first-hit-followup-verdict-gate.md`
- `research/quant_digests/2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md`（via index summary）
- `research/quant_digests/2026-04-10_0047_intraday-momentum-reversal-crypto-router.md`（via index summary）

## What Rank 89 originally tried to do
原始 Rank 89 想把 `outside close -> back inside close` 写成一个 **shared failure verdict allow-gate**：
- 先看价格是否收到前 `16` 根 `15m` 区间外；
- 再看未来 `1~4` 根内是否收回区间内；
- 若最近发生了与当前 setup 同方向的这种 failure verdict，才放行 `breakout_short / fib_retest_long / ema_psar_long`。

直白说：它赌的是“先假突破、再缩回去”能告诉你这笔 setup 更值得做。

## Why it was parked
原 clean replication 的核心结论很明确：
- `6bps/side` 下，`outside_inside_binary` 的总体收益确实从 baseline 的约 `-28.85%` 改善到约 `+2.34%`；
- 但代价是 `trade_count_retention` 只剩约 `4.45%`；
- `breakout_short` 的确从约 `-15.99%` 改到约 `+1.71%`，`fib_retest_long` 也从约 `-7.60%` 改到约 `+0.99%`；
- 可这些改善几乎全靠把样本砍到极薄；
- `seqext_size` 这层 overshoot 深度分档没有再提供诚实增量，反而略弱于纯 binary verdict。

所以它被 park，不是因为“failure verdict 完全没信息”，而是因为当时写成 **shared allow-gate** 时，信息量太稀、太靠切样本，撑不起 queue-facing 的可交易厚度。

## Hard park or soft park?
**更像 `soft park`，但已经在向 hard park 靠。**

原因：
- soft 的部分在于，failure 形状本身不是全死，至少在 `breakout_short / fib_retest_long` 上留下了方向性残余；
- hard 的部分在于，这个残余离“可直接重开一条 lane”还很远，而且原写法的 shared-gate 角色已经基本被证伪。

## Is there a rescue signal?
**有，但很窄。**

我认为唯一还能算“可救信号”的不是原来的 shared allow-gate，而是：
- `back-inside close` 这根 bar 本身，可能更像一个 **event-driven failure-followthrough verdict anchor**；
- 也就是：不是拿它去给所有 setup 放行，而是把它当成“外扩失败、重新缩回”的事件点，再看其后很短 horizon 的 follow-through / fade。

这和近几轮 digest 的方向是对齐的：
- `2026-03-19 breakout-reentry-inside-sequence-failure-verdict` 已经把主题收缩到“failure verdict”，而不是 generic gate；
- `2026-03-22 directional-change first-hit follow-up verdict` 进一步说明，真正有信息的往往是 **event-first-hit 之后的短窗 follow-up**，不是把 verdict 拉平做 shared overlay；
- `2026-04-08 dynamic turning-point trend leg` 与 `2026-04-10 horizon router` 也都在把信息往 **更短、更事件化、更 horizon-aware** 的 raw-alpha 宿主推进。

## The single best modification axis
**唯一值得改的一刀：把 `outside-close -> back-inside-close` 从 shared same-direction allow-gate，改写成 `back-inside bar anchored failure-followthrough setup`。**

只改这一刀，不偷带第二轴：
- 不改 universe；
- 不叠新的 regime/filter；
- 不顺手换 exit；
- 不把它重新包装成 multi-setup shared overlay。

直白说：如果以后要救，就别再问“它能不能帮所有 setup 做 shared allow？”
而要问：“`back-inside` 这一下，能不能单独当作一个 failure-followthrough 事件来做？”

## Should this become a derived hypothesis now?
**暂时不值得。结论：`soft_reframe_candidate`，但不升级为 `derived_hypothesis_drafted`。**

原因有三条：
1. **厚度还是太差**
   - 原最优臂 retention 约 `4.45%`，这不是“略稀”，而是已经接近只剩零散 pocket。
2. **distinctness 还不够**
   - 如果把它改写成 failure-followthrough event setup，它会明显靠近既有 `Rank 31b` / `Rank 104` 那条 failure-verdict family；
   - 当前还没有足够新的外部证据，能证明 `Rank 89b` 会是一个与那条 family 足够不同、值得单列的 proposal。
3. **新证据在推主题外流，不是在救原 rank 壳**
   - 最近证据更支持“事件锚 + 短窗 follow-up / fade”这种新宿主；
   - 不支持把 `Rank 89` 原先那种 shared same-direction allow-gate 重新写回 queue。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录未来若要救时的唯一诚实方向。

- trade on:
  - 保留 `outside -> back-inside` 这一下作为失败事件锚；
  - 更贴近“假突破后回到区间内”的短窗 follow-through / fade 语义；
  - 有机会避免原 shared gate 把信息摊薄。
- trade off:
  - 会失去“共享给多个 setup”的通用外观；
  - 很可能交易更稀；
  - 还可能与既有 failure family 高度重叠，最后证明不值得单列。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为收益改善主要靠极端砍样本，shared allow-gate 角色站不住。
2. **更像 hard 还是 soft park？**
   - `soft park`，但已明显向 hard 靠。
3. **有没有可救信号？**
   - 有，且只剩 `back-inside` failure verdict 这一条很窄的事件残余。
4. **最值得改的唯一一刀是什么？**
   - 从 shared allow-gate 改成 `back-inside bar anchored failure-followthrough setup`。
5. **是否值得形成新的 derived hypothesis？**
   - 现在还不值得；保留为 `soft_reframe_candidate` 即可。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未尝试 git commit：共享工作区长期存在大量与本轮无关的脏文件，当前不适合安全 selective commit。
