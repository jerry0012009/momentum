# 2026-04-21 05:42 UTC · Rank 27 park reframe

## 本轮结论
- 选定条目：`Rank 27 / Mt.Gox neckline confirmation`
- 原 `park` verdict：**保留**
- 本轮 park-reframe 结论：**`keep_park`**
- 额外收紧：`Rank 27` 当前更接近 **hard park with consumed residual**；不再诚实继续保留旧 `Rank 27b` 作为 queue-facing active reframe candidate

## 为什么这轮选 Rank 27
- 本轮按你刚重申的范围，只在 `Rank 1~37` 内选。
- 近 `7` 天已复盘的 `Rank 15 / 3 / 6 / 37 / 33 / 22` 先跳过；`Rank 27` 上一次 park-reframe 在 `2026-04-12 21:15 UTC`，已超出 `7` 天窗口。
- 相比再看已经在 `4/18~4/20` 被连续收紧过的条目，`Rank 27` 更适合做一次低频复核：
  - 原主题是 breakout 后的 neckline / retest 确认；
  - 最近又出现了更强、且更完整的 `retest -> re-break low` short-continuation 新证据；
  - 因而很适合判断：这算不算旧 Rank 27 的可救 residual，还是其实已经是新的 raw-alpha family。

## 原 rank 为什么 park
依据 `2026-03-17_0815_rank27-mtgox-neckline-clean-replication.md`，原 Rank 27 被 park 的原因很清楚：
1. `raw_breakout` 很差：`6bps/side mean_total_return ≈ -13.79%`，`positive_asset_ratio=0/3`；
2. `neckline_confirm` 虽略降假突破率，但收益更差：`≈ -17.42%`；
3. `neckline_confirm_plus_retest_hold` 虽把亏损收窄到 `≈ -3.03%`，但 `false_break_ratio ≈ 68.67%` 仍没有真正改善；
4. 也就是说，**确认层确实在改“形状”，但没有同时做到成本后收益变好、且假突破率更低**。

原始 park 的审计含义不是“颈线 / 回踩主题完全没信息”，而是：
> **把它写成旧 Rank 27 这种 neckline-confirmation filter / gate 形态时，信息密度不够，无法诚实升格。**

## 它更像 hard park 还是 soft park
**本轮更接近 hard park with consumed residual。**

原因：
- 早期它还像 `soft park`，因为存在一条自然残余：把静态 `retest_hold` 收窄成 `ATR-scaled retest zone + bounce reclaim`（即旧 `Rank 27b`）。
- 但截至这轮，新增证据已经把“可救的那点结构信息”进一步上移成**新的、更完整的 raw-alpha 宿主**，而不是旧 Rank 27 的 confirmation 改写。
- 换言之，主题没死，但**可用部分已经不再诚实地属于 old Rank 27 这条线**。

## 有没有“可救信号”？
有主题级信号，但**没有足够诚实地属于 Rank 27 本体的可救信号**。

### 新证据：`2026-04-19_2049_retest-rebreak-short-continuation-alpha.md`
这条新 digest 的核心不是“neckline confirm 更聪明了”，而是：
- 先 downside breakout；
- 再回踩；
- 然后在限定窗口内 **re-break impulse low**；
- 这本身就是一条可独立落地的 short continuation raw alpha。

它和旧 Rank 27 的关系是：
- **相关，但不是同一职责层。**
- 旧 Rank 27 仍在做“pattern-complete breakout 是否该放行”的确认层；
- 新证据则已经把价值重心放到了“回踩失败后再破低”的**完整事件定义 alpha** 上。

所以这轮最重要的判断不是“有没有可救信号”，而是：
> **这些信号救活的是新的 retest→re-break continuation family，不是旧 Rank 27 的 neckline-confirmation residual。**

## 最值得改的唯一一刀是什么
如果硬要改，唯一自然的一刀仍然是旧 `Rank 27b` 那条：
- `replace binary neckline retest_hold with ATR-scaled retest zone + bounce reclaim`

但这轮结论是：**这把刀已经不够用了。**
原因：
- 新证据的主价值不再是“把回踩定义写细一点”；
- 而是把“回踩后再破低”直接升级成独立入场事件；
- 这已经超出 old Rank 27 作为 confirmation/filter 的职责层。

因此本轮不再诚实继续沿 `Rank 27b` 方向保留 queue-facing 激活状态。

## 是否值得形成新的 derived hypothesis？
**不值得。**

不是因为主题没信息，而是因为：
1. 旧 Rank 27 的自然残余已经被长期消费；
2. 新证据的最佳表达方式是新的 raw-alpha family，而不是从 old Rank 27 再派生 `Rank 27c / 27d`；
3. 若此时继续强行派生，只会把“完整事件定义 alpha”错误降格成旧 breakout-confirmation 的附属 filter。

## 本轮回答（按 bot6 固定模板）
1. **原 rank 为什么 park？**
   - 因为 neckline / retest 这层确认并没有同时改善 post-cost return 与 false-break ratio；最好 challenger 也仍是全资产负值。
2. **更像 hard 还是 soft park？**
   - 本轮比 4 月 12 日那轮更接近 `hard park with consumed residual`。
3. **有没有可救信号？**
   - 有主题级新证据，但它救活的是新的 `retest -> re-break low` short-continuation raw-alpha 宿主，不是 old Rank 27 本体。
4. **最值得改的唯一一刀是什么？**
   - 若只看旧线，仍是 `ATR-scaled retest zone + bounce reclaim`；但本轮判断这条刀法已不再足以诚实表达新增价值。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；本轮结论应为 `keep_park`。

## 对 queue 的最小影响
- 本轮只应：
  1. 在 `research/park_reframe/INDEX.md` 追加本轮记录；
  2. 在 `docs/PARK_REFRAME_QUEUE.md` 的 `Recently reviewed` 追加一条 `Rank 27 | keep_park`；
  3. 将旧 `Rank 27b` 从 `Active reframe candidates` 中移除，避免继续误导成仍可随时入板的 active residual。

## 文件与工作区说明
- 当前工作区存在大量与本轮无关的历史脏文件；本轮只做 selective write，不混提，不做 commit。
