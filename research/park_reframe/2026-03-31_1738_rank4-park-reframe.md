# 2026-03-31 17:38 UTC — Rank 4 park reframe review

## 为什么这轮看 Rank 4
- 遵循 `bot6` 轮转：`50+` 与 `80~110` 号段这两天已连续覆盖，本轮回到 `1~24`。
- `Rank 4` 上一次正式 `park_reframe` 是 `2026-03-24 14:30 UTC`，已超过最近 `7` 天回避窗口。
- 它也很适合做一次低频复盘：原命题是典型的 `pairs direct-entry` 失败案例，但最近 3/30~3/31 又连续出现多条 pairs / stat-arb 新证据，正好回答一个问题——这些新证据到底是在“救 Rank 4”，还是只是在继续把 pairs 主题上移成新的 full-stack raw-alpha family。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`
- `research/optimization_loop/2026-03-16_1508_rank4-pairs-clean-replication-park.md`
- `research/optimization_loop/2026-03-30_0143_rank4_threshold_governed_pairs_residual_stays_park_reframe.md`
- `research/quant_digests/2026-03-30_0633_dynamic-coint-forecast-threshold-pairs-alpha.md`
- `research/quant_digests/2026-03-30_1858_percentile-entry-cointegration-pairs-alpha.md`
- `research/quant_digests/2026-03-31_1234_moving-band-basket-statarb-alpha.md`

## 1) 原 Rank 为什么 park？
原 `Rank 4` 被 park 的原因一直很清楚：
- 它原本想表达的是 **少数 crypto pairs 的 direct spread-entry / stat-arb alpha**；
- 但最小 clean replication 完成后，三组主 pair 一起为负：
  - `BTC/ETH`：`cumulative_net_return ≈ -12.42%`
  - `BTC/SOL`：`≈ -22.91%`
  - `ETH/SOL`：`≈ -27.77%`
- 后续 `Rank 4b` 虽把部分 pair 拉回轻微正 pocket，但时间稳定性一补，最近 tercile / 最新月份又重新转负；
- 因此审计结论早就不是“再多磨一点参数也许能活”，而是：
  - **把 spread 偏离本身当 standalone pairs alpha，这条路应继续 park。**

翻成人话：
`pairs / spread` 这个大主题没有死，但 **原 Rank 4 那种 fixed-pair / fixed-threshold / direct-entry 读法已经被审计掉了**。

## 2) 它更像 hard park 还是 soft park？
我的判断仍然是：**`soft park`，但对 Rank 4 这版旧命题来说已经相当偏 hard。**

为什么不是纯 hard park：
- 最近的新证据没有说 pairs / stat-arb 完全没边；
- 相反，3/30~3/31 的 digest 一直在说明这条主题还活着：
  - `dynamic-coint spread forecast × percentile trigger × PIW gate`
  - `percentile-entry × cointegration spread MR`
  - `moving-band basket stat-arb × 线性 inventory shell`
- 也就是说，**主题还活**。

为什么又说“对 Rank 4 已经相当偏 hard”：
- 活下来的内容越来越不像“原 Rank 4 的一刀小修”；
- 它们共同指向的是新的、完整的 raw-alpha family：
  - 动态协整
  - 分位阈值治理
  - basket governance
  - uncertainty / inventory shell
- 这些都超出了原 Rank 4 那种 direct-entry pairs spread 的残余边界。

所以：
- 对 pairs 主题：不是 hard park；
- 对原 `Rank 4` 这版 queue-facing 对象：已经很接近“soft 但 hard enough”。

## 3) 现有证据里有没有“可救信号”？
**有，但它们更像“pairs 主题可救”，不像“Rank 4 本体可救”。**

### 可救信号 A：threshold governance 还活
`2026-03-30_1858_percentile-entry-cointegration-pairs-alpha.md` 与 `2026-03-30_0633_dynamic-coint-forecast-threshold-pairs-alpha.md` 共同说明：
- spread 主题的问题，不是“再也没有回归”；
- 而是 **固定 `±2σ` / static z-score` 这套写法过粗**；
- 更自然的读法是：
  - `cointegration / dynamic-coint pair selection`
  - `percentile trigger`
  - `forecast-score timing`
  - `PIW / uncertainty gate`

### 可救信号 B：对象正在从 pair 升到 basket
`2026-03-31_1234_moving-band-basket-statarb-alpha.md` 更进一步说明：
- 真正值得 desk 先测的，不一定是“两条线的 spread”；
- 而可能是 **moving-band basket mean reversion + inventory shell**。

### 但为什么这些仍然不够救 Rank 4
因为这些可救信号共同指向的是：
- 不是“原 Rank 4 只差一个更聪明的阈值”；
- 而是“如果 pairs / stat-arb 要活，重写的是整条策略骨架”。

换句话说：
- **可救的是 family，不是 Rank 4 本体。**

## 4) 最值得改的唯一一刀是什么？
如果只保留“对原 Rank 4 最自然、且唯一还能成立的一刀”，答案仍然不是新东西，而是既有的：

**把 `BTC-ETH spread z-score` 从 direct pairs-trade entry，降级成 shared risk overlay / position-sizing gate。**

也就是既有 `Rank 4c` 的那一刀。

为什么这仍然是唯一主修改轴：
- 它没有推翻原 `park`；
- 只改角色，不改核心变量；
- 也是目前唯一还能说得上“属于 Rank 4 血缘内部残余”的改写。

为什么本轮不再往前多写一刀：
- 再往前的东西就会变成：
  - percentile 阈值治理
  - dynamic-coint forecast timing
  - moving-band basket shell
- 这些都已经不是 `Rank 4c` 之后的“第二条窄 residual”，而是**另一条 full-stack family intake**。

## 5) 是否值得形成新的 derived hypothesis？
**本轮结论：不值得，维持 `keep_park`。**

原因：
1. 原 `park` 的审计意义仍然有效，不能推翻；
2. 最近新证据虽然更强，但强在新的 pairs raw-alpha family，而不是原 Rank 4 本体；
3. 对 Rank 4 自己来说，唯一诚实的一刀仍只是既有 `Rank 4c`；
4. 如果现在硬写 `Rank 4d`，大概率只是把“dynamic-coint / percentile / basket governance”伪装成原 Rank 4 的小修补件，边界会很不诚实。

所以这轮最诚实的动作不是新增派生，而是明确记账：
- **Rank 4 的 residual 仍停在 Rank 4c；**
- **更宽的新证据应被视作 pairs / stat-arb 新 family 的上位入口，不应继续挂在 Rank 4 名下。**

## 6) 如果硬要派生，trade on / trade off 会是什么？
本轮不 draft 新假设，但为审计完整性，记录一下如果硬要往前写，它只可能是什么：
- `trade on`：保留 pairs / relative-value 主题，但把对象改写成 dynamic-coint pair selection + percentile trigger + uncertainty-width / inventory shell 的完整 raw-alpha family；
- `trade off`：这会完全放弃原 Rank 4 的 direct-entry residual 语义，也会与既有 `Rank 4c` 的 overlay 残余分家。

这已经明显不是“从 Rank 4 再切一刀”，而是**另开 fresh intake**。

## 本轮按模板回答
1. **原 rank 为什么 park？**
   - 因为原 `fixed pairs + direct spread entry` clean replication 后三组主 pair 一起为负，后续 time-stability 也没把它救回 candidate。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但对原 Rank 4 本体已很偏 hard。
3. **有没有“可救信号”？**
   - 有；但可救的是 pairs / stat-arb 新 family（dynamic-coint / percentile / basket），不是原 Rank 4 本体。
4. **最值得改的唯一一刀是什么？**
   - 仍然只是既有 `Rank 4c`：把 spread z-score 从 direct entry 降级成 shared risk overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不写 `Rank 4d`？**
   - 因为新增 evidence 抬升的是另一条 full-stack raw-alpha family，而不是原 Rank 4 的第二条窄 residual。

## 最终结论
- `Rank 4` 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 4 仍是 soft park，但对其原始 direct-entry 读法已相当偏 hard；最近 pairs 新证据持续说明主题活在 dynamic-coint / percentile / basket 的 full-stack raw-alpha family，而不是原 Rank 4 值得再诚实派生出 `Rank 4d`。**

## 队列写回
建议在 `docs/PARK_REFRAME_QUEUE.md` / `research/park_reframe/INDEX.md` 中登记为：
- `2026-03-31 17:38 UTC | Rank 4 | verdict=keep_park | original verdict kept=park | note=soft park，但对原 direct-entry pairs 读法已很偏 hard；3/30~3/31 的 dynamic-coint / percentile / moving-band basket 新证据继续证明，活下来的其实是更上位的 pairs/stat-arb full-stack raw-alpha family，而不是原 Rank 4 可再诚实切出的 Rank 4d；当前唯一自然残余仍只是既有 Rank 4c。`

## Git / 风险备注
- 本轮只做最小必要文件改动。
- 当前工作区长期存在大量与本轮无关的脏文件；为避免混提，本轮不做 commit。
