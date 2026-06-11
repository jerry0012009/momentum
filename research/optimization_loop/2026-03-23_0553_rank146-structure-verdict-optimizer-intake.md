# 2026-03-23 05:53 UTC · Rank 146 / structure verdict optimizer source intake

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / fresh intake reserve`
- 范围控制：只推进 **1 个主点**（fresh intake reserve）+ **1 个紧邻子点**（与当前 active compare 的边际价值比较）。

## 0. 先判 interrupt
- `Paper / 正在自动运行` 顶板未写入新的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`。
- `tiny-live / live-shadow plumbing` 也未见新的 blocking anomaly。
- 因此本轮不抢 interrupt，继续按 `Next 3 bot3 runs`：`Paper launch queue` 为空时，先执行 fresh intake reserve。

## 1. 为什么这轮切 fresh intake，而不是继续磨旧 P1
当前顶板 authoritative 口径已经把：
- `Rank 145 / 14b / 140 / 125 / 112 / 111` 都收进了 `keep_P1 / budget used` 或 `active compare anchor / not default primary`；
- `Rank 144 / 143 / 142 / 141` 也都已退回 `park` 或 evidence-only。

所以这轮最值得认领的，不是再给 exhausted P1 做近义切片，而是给 **能直接帮助三条收口线避免“参数错杀”** 的新 reserve 一个最低成本 intake。

## 2. 本轮认领
### 主点
- **`Rank 146 / structure verdict optimizer`**

### 紧邻子点
- 只做 1 个边际价值比较：它和 `Rank 140 / Rank 111` 这类 compare anchor 相比，是否值得占新的 Scout 主资源位？

结论：**值得进入 active Scout，但暂只到 `keep_P1`。**
原因不是它已经证明某条 alpha 有边，而是它能更快回答 desk 当前最关键的问题：
> `EMA / PSAR raw alpha`、`breakout-short follow-up`、`Fib retest_hold` 现在的坏分数，到底是结构本身不行，还是连续参数手工猜错了。

## 3. 来源与 reader-facing 定义
来源基底：
- `research/quant_digests/2026-03-23_0550_split-brain-optimizer-structure-verdict.md`
- repo：`dietmarwo/autoresearch-trading`

reader-facing 定义：
> 不再把 `EMA / PSAR / breakout / retest` 的失败一股脑判成“没边”，而是先固定结构，再用自动优化去搜连续参数，并用严格 rolling walk-forward 判断：到底是 `structure dead`，还是只是 `parameter guessed wrong`。

## 4. 为什么它现在的边际价值高
1. **直接服务 desk 三条收口线**
   - `EMA / PSAR raw alpha focus` 最容易被手工阈值错杀；
   - `breakout-short follow-up` 常被 timeout / penetration / wait-bars 搅乱；
   - `Fib retest_hold` 也常被 zone 宽度 / reclaim 容差假噪声掩盖。

2. **它是方法层增益，不要求先证明一个新 alpha**
   - 这轮不需要再 intake 一个形态；
   - 只需要把“结构 verdict”和“连续参数搜索”拆开，就能让现有 desk 的失败读法更诚实。

3. **它更像 routing 改写器，而不是装饰性证据**
   - 如果本地 frozen-skeleton walk-forward 显示某条结构在自动调参后仍死，那就应更快 park；
   - 如果有一条结构在 rolling OOS 下重新活过来，它就值得从 `keep_P1` 推到 `P2`。

## 5. 本轮最小 intake verdict
### desk-level 读法
- **`Rank 146 = P1 / keep_P1 / fresh intake admitted / method-layer reserve`**
- 它不是 alpha、本身也不是 deployable gate；
- 它更像 desk 的 **structure-vs-parameter honesty accelerator**。

### 当前最小 evidence（仅 intake，不做本地 replication）
从 digest 可直接提炼的 reader-facing 锚点：
- repo 已覆盖 `EMA / ADX / PSAR / Supertrend / Donchian / ATR / VWAP` 等组件；
- 方法上明确把 **离散结构** 与 **连续参数** 分离；
- 强调 `rolling walk-forward`，适合做 first verdict，而不是只看 in-sample best run。

这些证据足以把它从“泛泛优化器”压成一个 desk 可用的 reserve。

## 6. 轻量 scorecard
artifact：
- `reports/artifacts/scout_rank146_structure_verdict_optimizer_15m/source_intake_card.csv`
- `reports/artifacts/scout_rank146_structure_verdict_optimizer_15m/promotion_scorecard.csv`
- `reports/artifacts/scout_rank146_structure_verdict_optimizer_15m/promotion_scorecard.json`

- `usefulness = 3/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 2/3`
- `deployability = 2/3`
- `hard-fail flags = not_alpha_itself; optimization_overfit_risk; local_replication_not_run; parameter_stability_unproven`
- `recommended_action = keep_P1`
- `why_now = 它直接回答当前 desk 最现实的问题：坏分数是结构死，还是参数错；这比继续磨 exhausted P1 更可能改变后续 routing。`
- `main_weakness = 目前只有 repo/readme 工程证据，没有 desk 本地 fixed-skeleton + rolling walk-forward replication。`

## 7. 对后续 run 的最小授权边界
如果后续继续给 `Rank 146` 默认预算，只允许做 **1 次真正会改变 verdict 的最小 frozen-skeleton 检查**：

### 允许的唯一下一刀
固定 4 个 skeleton，只让优化器搜连续参数：
1. `EMA stack`
2. `EMA + ADX gate`
3. `EMA + PSAR fail-safe`
4. `Donchian breakout + EMA context`

统一口径：
- 资产：`BTC / ETH / SOL`
- 周期：`15m`
- 样本：`180d`
- 评估：`rolling walk-forward`
- 对照：`人工默认参数` vs `自动优化连续参数`

### 只看 4 个指标
1. `OOS post-cost expectancy`
2. `positive-fold ratio`
3. `parameter stability`
4. `structure rank stability`

### 过门槛才可升层
- 若至少有 1 个固定 skeleton 在 `BTC/ETH/SOL` 的 rolling OOS 中出现 **更高 positive-fold ratio 且参数不乱跳**，才允许从 `keep_P1` 讨论到 `promote_P2`；
- 否则直接把它留在 `method evidence pool`，不再烧默认轮次。

## 8. 本轮结论
- 这轮最诚实的选择，是把 `Rank 146` 作为新的 fresh intake reserve 写入顶板，而不是继续回头磨 exhausted P1。
- 它当前最像的是 **方法层 honesty accelerator**，不是新 alpha。
- 但正因为它能避免“参数错杀”，它的边际价值高于继续给 `Rank 140 / 111` 做更多近义 compare。
