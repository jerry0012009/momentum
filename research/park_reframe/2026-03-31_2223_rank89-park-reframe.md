# 2026-03-31 22:23 UTC — Rank 89 park reframe review

## 为什么这轮看 Rank 89
- 按 `bot6` 当前轮转，这轮优先继续覆盖 `80~110` 号段里最近 `7` 天未被复盘的 parked rank。
- `Rank 89 / outside-close -> back-inside-close failure verdict` 上一次是 optimization loop 里的 intake + clean replication + park（`2026-03-19`），但还没有进入 `bot6` 的低频 park-reframe 审查。
- 它很适合做一次“值不值得再长出窄 reframe”的判断：原 clean replication 已明确显示这条线有一点 post-break failure verdict 残余，但 retention 只剩 `≈4.45%`；最近的新旁证（尤其 `DC first-hit` 与 `FT/NFT`）又都在强调 **更上位的 event-driven final-verdict / post-break router family**。本轮要回答的是：**这些新证据是在救 Rank 89 本体，还是只是在把主题继续上移。**

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-03-31_1945_rank74-park-reframe.md`
- `research/park_reframe/2026-03-31_1738_rank4-park-reframe.md`
- `research/park_reframe/2026-03-26_0016_rank105-park-reframe.md`
- `research/optimization_loop/2026-03-19_1219_rank89-outside-inside-intake.md`
- `research/optimization_loop/2026-03-19_1252_rank89-clean-replication-park.md`
- `research/quant_digests/2026-03-22_2028_dc-first-hit-followup-verdict-gate.md`
- `research/quant_digests/2026-03-23_0312_ft-nft-killzone-postbreak-router.md`

## 1) 原 Rank 为什么 park？
原 `Rank 89` 想表达的是：
- 先定义一个 rolling 区间（前 `16` 根 `15m` 高低区间）；
- 若价格先 `outside close`，再在接下来 `1~4` 根内 `back-inside close`，就把这次 break 记成 failure event；
- 再把它当成 `breakout_short / fib_retest_long / ema_psar_long` 可共用的 post-break failure verdict / overlay。

原 clean replication 把它压回 `park`，原因非常集中：
1. `outside_inside_binary` 的确把 overall 从 `≈-28.85%` 拉到 `≈+2.34%`；
2. 但改善几乎完全来自 **极端缩样本**：
   - `mean_trades ≈ 292.3 -> 14.3`
   - `trade_count_retention ≈ 4.45%`
3. setup 级看也一样：
   - `breakout_short @6bps ≈ -15.99% -> +1.71%`，但 retention 仅 `≈3.47%`
   - `fib_retest_long @6bps ≈ -7.60% -> +0.99%`，但 retention 仅 `≈5.52%`
   - `ema_psar_long @6bps ≈ -5.26% -> -0.03%`，并未真正转正
4. `sequence-extreme size` 这条更花的分档没有新增诚实增益，反而略弱于纯 `binary`。

翻成人话：
**Rank 89 被 park，不是因为“outside->back-inside”完全没信息，而是因为把它写成 queue-facing shared verdict 时，改善主要靠把交易砍到只剩极少数样本；这更像局部 clue，不像值得继续占默认资源位的独立命题。**

## 2) 它更像 hard park 还是 soft park？
我的判断：**`soft park`，但已经明显朝 hard park 那边偏。**

为什么不是 hard park：
- clean replication 里，`breakout_short` 与 `fib_retest_long` 都确实留下了一点 failure-verdict 残余；
- 主题层面上，post-break path / failure routing 也没有死，最近两条 digest 还在继续给这类语言加旁证。

为什么又说它偏硬：
- 这点残余必须靠 `≈4.45%` 的 retention 才显形；
- shared overlay / shared verdict 的原写法已被 clean replication 否掉；
- 最近新证据支持的不是“Rank 89 再窄修一下”，而是 **更上位的 event-driven first-hit / FT-NFT router family**。

所以：
- 对“post-break failure verdict”主题本身，仍是 soft park；
- 对原 `Rank 89` 这版 queue-facing shared 命题，已经很偏 hard。

## 3) 现有证据里有没有“可救信号”？
**有，但可救的是主题，不是 Rank 89 本体。**

### 可救信号 A：failure verdict 主题确实有信息
原 clean replication 已经给出第一层证据：
- `outside_close -> back_inside_close` 的确比“只看固定持有后盈亏”更贴近真假 break 的路径语义；
- 尤其在 `breakout_short` 上，说明“先假跌破、再回区间”这类 failure 形状并非空想。

### 可救信号 B：最近新证据把这条残余上移成更诚实的 event-driven verdict family
- `2026-03-22 DC first-hit` 旁证说明：**比固定 N 根 bar 更值钱的，是“先 hit continuation 还是先 hit failure”的 first-hit 判决**；
- `2026-03-23 FT/NFT router` 又说明：**post-break path 应先分路由，再谈 follow-up verdict**，而不是继续用单一路径 + 固定观察窗去写。

这两条新证据共同说明：
- 真正活下来的，不是 Rank 89 这种 `rolling range outside->back-inside` 的具体写法；
- 而是更上位的 **event-driven final-verdict / post-break router** 语言。

## 4) 最值得改的唯一一刀是什么？
如果只保留唯一主修改轴，最值得改的一刀会是：

**把 Rank 89 从“固定 rolling 区间 outside-close -> back-inside-close 的 shared verdict”收窄成“event-driven first-hit / FT-NFT router 下的一种 failure-routing clue”，不再让它自己直接担任 queue-facing gate。**

也就是：
- 不再把 `outside->back-inside` 当最终成品；
- 只把它当更大一层 `post-break path classification` 里的一个子信号；
- 优先服务 `breakout_short final-verdict`，而不是继续同时挂在 `Fib / EMA` 上。

但这也是本轮不 draft 的关键：
- 这条“一刀”已经明显不是在修 Rank 89 本体；
- 它实际上是在承认 Rank 89 的残余应该并入更上位 family。

## 5) 是否值得形成新的 derived hypothesis？
**本轮结论：不值得，维持 `keep_park`。**

原因：
1. 原 `park` 的审计意义仍然很强，不能推翻；
2. 原 clean replication 里的改善主要靠 `≈4.45%` retention，太薄；
3. 唯一自然残余已经从 “Rank 89 本体” 上移成了更上位的 `event-driven final-verdict / FT-NFT router` family；
4. 如果现在硬写 `Rank 89b`，大概率只是把 `DC first-hit / FT-NFT` 家族换壳挂回 Rank 89，边界会很不诚实；
5. failure-verdict 残余在队列里也已有近邻：`Rank 31b`、`Rank 105`、`Rank 33` 这些对象已经把“假突破 / false reclaim / body verdict / failure-routing”这条语义带往更通用的 family 方向。

所以这轮最诚实的动作不是 draft 新假设，而是明确记账：
- **Rank 89 原 `park` 保留；**
- **其残余价值已更像上位的 post-break verdict family 旁证，不应再单独长成 `Rank 89b`。**

## 6) 如果硬要派生，trade on / trade off 会是什么？
本轮不 draft，但为审计完整性，记录一下如果硬要往前写，它只可能是什么：
- `trade on`：不再用固定 `N` 根 15m rolling 区间直接做最终 verdict；保留 `outside->back-inside` 只作为 `event-driven first-hit / FT-NFT router` 下的 failure clue，优先先测 breakout-short final-verdict 的 A/B；
- `trade off`：放弃原 Rank 89 作为 shared post-break gate 的读法，承认它只是更大一层 event-driven router 里的局部特征；但这样一来，它与 `DC first-hit / FT-NFT / false reclaim` 近邻 family 的边界会高度重叠，已不再像一个独立 queue-facing rank。

## 本轮按模板回答
1. **原 rank 为什么 park？**
   - 因为 `outside-close -> back-inside-close` 的改善主要靠把样本砍到 `≈4.45%` retention；shared verdict 写法不够厚，也没有把 `ema_psar_long` 真正救活。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但对原 Rank 89 写法已明显偏 hard。
3. **有没有“可救信号”？**
   - 有；主要是 post-break failure verdict 主题本身仍有信息，且被 `DC first-hit` 与 `FT/NFT router` 新证据继续支持。
4. **最值得改的唯一一刀是什么？**
   - 把 Rank 89 从固定 rolling-range shared verdict，收窄成 event-driven final-verdict / router family 里的一个 failure clue。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不写 `Rank 89b`？**
   - 因为唯一自然残余已经明显上移成更上位的 event-driven post-break verdict family；若硬写 `Rank 89b`，只是把 `DC first-hit / FT-NFT` 换壳挂回原 rank，不够 distinct，也不够诚实。

## 最终结论
- `Rank 89` 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 89 仍是 soft park，但对原 `outside-close -> back-inside-close` shared verdict 读法已明显偏 hard；它留下的唯一自然残余更像应上移到 `event-driven final-verdict / FT-NFT router` family，而不是再诚实派生出 `Rank 89b`。**

## 队列写回
建议在 `docs/PARK_REFRAME_QUEUE.md` / `research/park_reframe/INDEX.md` 中登记为：
- `2026-03-31 22:23 UTC | Rank 89 | verdict=keep_park | original verdict kept=park | note=soft park，但对原 outside-close -> back-inside-close shared verdict 读法已明显偏 hard；clean replication 的改善主要靠 retention≈4.45% 的极端缩样本，而 3/22~3/23 的新旁证又把残余价值上移到更上位的 event-driven final-verdict / FT-NFT router family，当前不诚实再派生 Rank 89b`

## Git / 风险备注
- 本轮只做 park-reframe 所需最小文本更新。
- 当前工作区存在大量与本轮无关的脏文件；为避免混提，本轮不做 commit。
