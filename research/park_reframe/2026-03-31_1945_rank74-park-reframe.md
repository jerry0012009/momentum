# 2026-03-31 19:45 UTC — Rank 74 park reframe review

## 为什么这轮看 Rank 74
- 按 `bot6` 轮转，本轮继续优先 `50+`，且近期已连续覆盖 `94 / 107 / 99 / 88 / 65` 等更高号段后，回到 `50~79` 里最近 `7` 天未复盘的 parked rank。
- `Rank 74 / ADX+ER price-only trend-readiness gate` 属于典型“方向未必错，但 shared 写法可能过宽”的对象：原 clean replication 里 `breakout_short` 有一点 anti-chop 味道，`Fib retest_long / ER only` 也有局部 pocket，但三线共用主读法并没站住。
- 当前 queue 里还没有 `Rank 74b`；这轮要回答的不是“ADX/ER 有没有一点信息”，而是：**这点残余是否已经足够 distinct，值得再长成一个新的窄 reframe hypothesis。**

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-03-31_1738_rank4-park-reframe.md`
- `research/park_reframe/2026-03-31_1524_rank94-park-reframe.md`
- `research/park_reframe/2026-03-31_1312_rank107-park-reframe.md`
- `research/quant_digests/2026-03-19_0055_adx-er-price-only-trend-readiness-gate.md`
- `research/optimization_loop/2026-03-19_0112_rank74-source-intake.md`
- `research/optimization_loop/2026-03-19_0140_rank74-clean-replication.md`
- `research/park_reframe/2026-03-21_1815_rank18-park-reframe.md`
- `research/park_reframe/2026-03-25_0457_rank101-park-reframe.md`

## 1) 原 Rank 为什么 park？
原 `Rank 74` 想表达的是：
- 用 `ADX14 + ER20 (+ DI alignment)` 做一个 **price-only shared trend-readiness gate**；
- 让它同时服务 `breakout_short / fib_retest_long / ema_psar_long` 三条主线；
- 希望先过滤掉“不是真的在走、只是来回磨”的环境。

原 clean replication 把它压回 `park`，原因很清楚：
1. `breakout_short` 上确实有一点 anti-chop 改善，但主要靠砍样本：
   - `baseline @6bps ≈ -2.58%`
   - `adx_plus_er_plus_di @6bps ≈ -0.48%`
   - 但 `trade_count_retention ≈ 41.22%`
2. `ema_psar_long` 上没有被救活：
   - `baseline @6bps ≈ -5.41%`
   - `adx_plus_er_plus_di @6bps ≈ -5.90%`
   - `trade_count_retention ≈ 32.72%`
3. `fib_retest_long` 的局部 pocket 只在更窄的 `er_only` 臂上好看：
   - `er_only @6bps ≈ +2.16%`
   - `positive_asset_ratio = 100%`
   - 但 `mean_trades ≈ 3.0`
   - `trade_count_retention ≈ 27.27%`
4. shared 主读法 `adx_plus_er_plus_di` 在 Fib 上已经稀到失真边缘：
   - `mean_trades ≈ 0.7`
   - `trade_count_retention ≈ 6.06%`

翻成人话：
**Rank 74 被 park，不是因为 ADX/ER 完全没信息，而是因为“把它写成三条线共用的 shared trend-readiness gate”不够诚实：short 改善主要靠砍单，long 主线没救活，Fib 上真正像样的 pocket 又只剩更窄的 `ER-only` 局部。**

## 2) 它更像 hard park 还是 soft park？
我的判断：**`soft park`，但已经明显朝 hard 那边偏。**

为什么不是 hard park：
- `breakout_short` 的 anti-chop 方向并不荒谬；
- `Fib retest_long / ER only` 也确实留下了一个局部正 pocket；
- 所以“价格路径是否真在推进”这个主题本身没有死。

为什么又说它偏硬：
- shared 主读法已经被 clean replication 否掉；
- 真正好看的残余只存在于**更窄、更稀**的 lane-specific 子臂；
- 而且这些残余的职责边界，已经和队列里既有对象明显重叠：
  - shared `trend-readiness / abstain` 语义，已有 `Rank 18b`；
  - long-side `hold-quality / 少做坏回踩` 语义，已有 `Rank 64b / Rank 101` 一组对象。

所以：
- 对“ADX/ER 主题”本身，仍是 soft park；
- 对原 `Rank 74` 这版 shared queue-facing 命题，已经相当偏 hard。

## 3) 现有证据里有没有“可救信号”？
**有，但不够 distinct。**

### 可救信号 A：`breakout_short` 上有一点 anti-chop 味道
- `adx_plus_er_plus_di` 的确把 `breakout_short` 从 `-2.58%` 拉到 `-0.48%`；
- 说明“先问是不是趋势口袋”并非空想。

但这条线的问题也很明显：
- 改善主要来自 retention 掉到 `≈41.22%`；
- 它更像 shared `abstain / trend-readiness veto` 的已有语义，而不是新的 distinct residual。

### 可救信号 B：`fib_retest_long / ER only` 留下了最自然的残余
- 在所有子臂里，最像“还剩一点东西”的，其实不是 shared `ADX+ER+DI`，而是更窄的 `ER only`；
- 这说明真正值钱的可能不是“趋势强度全套”，而是 **回踩后价格路径是否够顺、不够乱** 这件事。

但它也有两个 blocker：
1. `retention≈27.27%`，仍然偏稀；
2. 这条残余已经非常接近现有 `long-side hold-quality / anti-noise` 语义，和 `Rank 64b / Rank 101` 的边界不够拉开。

## 4) 最值得改的唯一一刀是什么？
如果只保留唯一主修改轴，最值得改的一刀是：

**把 `ADX+ER(+DI)` shared trend-readiness gate，收窄成 `Fib retest_hold long` 专用、以 `ER` 为主的 path-cleanliness / hold-quality veto。**

也就是：
- 不再服务 `breakout_short`；
- 不再要求 `ADX+ER+DI` 三件套一起上；
- 只保留更接近原证据残余的那一部分：
  - `Fib retest_hold long` 已触发后，
  - 再看 `ER` 是否足够高，决定放行 / 否决 / 轻微降仓。

这是一刀明确的收窄，而不是多轴大改。

## 5) 是否值得形成新的 derived hypothesis？
**本轮结论：不值得，维持 `keep_park`。**

原因：
1. 原 `park` 的审计意义仍然很强，不能推翻；
2. shared 主读法已经被 clean replication 否掉；
3. 唯一自然残余虽然存在，但 distinctness 不够：
   - shared 趋势过滤语义已被 `Rank 18b` 覆盖；
   - long-side hold-quality 语义又已被 `Rank 64b / Rank 101` 基本占住；
4. 当前没有新的近 7 天证据把这条 `ER-only Fib residual` 抬成一个足够独立的新 family 或新 front-slot 提案。

换句话说：
- **不是没有残余；**
- 但这条残余更像应被当作既有 `trend-readiness / hold-quality` 家族的补充旁证，
- 而不是再单独长成 `Rank 74b`。

## 6) 如果硬要派生，trade on / trade off 会是什么？
本轮不 draft 新假设，但为审计完整性，记录一下如果硬要往前写，它只可能是什么：
- `trade on`：不改 `Fib retest_hold long` 原始 anchor / retest / entry；只有当 `Fib retest_hold long` 已触发时，额外读取 `ER20`（必要时再比较是否要加 `ADX`），优先先测 `baseline vs ER_veto / ER_halfsize`，不接 breakout_short / EMA。
- `trade off`：放弃原 `Rank 74` 的 shared `ADX+ER+DI` 读法，只保留 long-side 路径干净度这一小块残余；但这样写出来的对象，与现有 `Rank 64b / Rank 101` 的边界已经过近，容易变成重复记账。

所以这轮更诚实的选择仍是：**保留这条 residual 为旁证，不新开 `Rank 74b`。**

## 本轮按模板回答
1. **原 rank 为什么 park？**
   - 因为 shared `ADX+ER(+DI)` 读法没能在三条主线同时给出诚实增量：short 主要靠砍单，EMA long 没救活，Fib 上真正的 pocket 又只剩更窄且偏稀的 `ER only` 子臂。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但对原 shared 写法已明显偏 hard。
3. **有没有“可救信号”？**
   - 有；主要是 `breakout_short` 的 anti-chop 味道与 `Fib retest_long / ER only` 的局部 pocket。
4. **最值得改的唯一一刀是什么？**
   - 把 `ADX+ER(+DI)` shared gate 收窄成 `Fib retest_hold long` 专用、以 `ER` 为主的 path-cleanliness / hold-quality veto。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不写 `Rank 74b`？**
   - 因为唯一自然残余与既有 `Rank 18b / Rank 64b / Rank 101` 的边界过近，当前不够 distinct，容易变成重复记账而不是新的诚实队列项。

## 最终结论
- `Rank 74` 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 74 仍是 soft park，但对原 shared ADX+ER trend-readiness 读法已明显偏 hard；它留下的唯一自然残余更像 `Fib retest_hold long` 的 ER-first 路径干净度提示，但这条线与既有 `Rank 18b / Rank 64b / Rank 101` 的边界过近，当前不诚实再派生 `Rank 74b`。**

## 队列写回
建议在 `docs/PARK_REFRAME_QUEUE.md` / `research/park_reframe/INDEX.md` 中登记为：
- `2026-03-31 19:45 UTC | Rank 74 | verdict=keep_park | original verdict kept=park | note=soft park，但对原 shared ADX+ER trend-readiness 读法已明显偏 hard；原 clean replication 里真正像残余的只剩 Fib retest_long 的 ER-only 局部 pocket，而这条线又与既有 Rank 18b / Rank 64b / Rank 101 的 trend-readiness / hold-quality 语义过近，当前不诚实再派生 Rank 74b`

## Git / 风险备注
- 本轮只做 park-reframe 所需最小文本更新。
- 当前工作区长期存在大量与本轮无关的脏文件；为避免混提，本轮不做 commit。
