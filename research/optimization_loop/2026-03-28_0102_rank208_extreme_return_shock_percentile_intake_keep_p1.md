# 2026-03-28 01:02 UTC · Rank 208 / extreme-return shock percentile fresh intake

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 本轮只执行 `cycle_plan` 里当前排在最前且 `status: pending` 的唯一小点：`research/quant_digests/2026-03-27_2344_extreme-return-shock-percentile-alpha.md`
- 动作类型：`Fresh intake`

## 1. 本轮对象为什么合法
这条 digest 对应的是一个**新的单资产 raw-alpha 母线**：
- 核心不是 `Rank 152` 那种 **BTC shock -> alt basket lead-lag**；
- 也不是 `2026-03-25 adaptive-percentile shock-reversal` 那种 **多 lookback own-shock + 组合化反转**；
- 它更直接：**单资产最新 bar / 最新短窗收益落到滚动分位极端后，接下来几根 bar 到底更偏 continuation 还是更偏 fade。**

因此它不是旧对象改写，也不是 background reopen，而是可以独立建档的新 intake。

## 2. 首轮 intake 判断
首轮最诚实的结论是：

> **`Rank 208 / extreme-return shock percentile` 值得保留为 `keep_P1`，但还不够升 `P2`。**

原因：
1. **alpha 骨架足够轻、可直接复现。** 规则主体就是 rolling percentile shock trigger，天然能拆成 `continuation` 与 `fade` 两支，适合在 `1m/3m/5m/15m` 上快速做 first verdict。
2. **它和当前前排链条正交。** 现有 front chain 里没有一条已定型对象是“单资产极端 bar shock 的 continuation / fade 双分支 baseline”。
3. **论文同时给了诚实的负面约束。** 原论文在美股逐笔口径里显示，成本前有 alpha、成本后很容易被 `5 bps/trade` 吃平；这意味着对 crypto desk 来说，默认不能先乐观地把它当成 taker-heavy 1m 成品。
4. **当前仍缺本地 clean first verdict。** 还没有本地 `BTC/ETH/SOL`、`3m/5m`、`q95 continuation vs q10 fade`、`2/4/8/12 bps round-trip` 的统一摩擦阶梯结果，所以现在最多只能记为值得做一次 survivor follow-up 的 `P1`。

## 3. 为什么现在不能直接升 P2
要升 `P2`，至少得先回答一个更具体的问题：
- 在 majors 上，到底是 `shock continuation` 还是 `shock fade` 留下成本后 pocket；
- 这个 pocket 是否只存在于 `1m` 噪声级别，还是在 `3m/5m` 仍然成立；
- `无确认` 和 `VWAP/MA confirm` 并排后，确认层到底是在提纯还是只是在减少交易数。

这些关键 admission 前问题，当前 digest 只给了论文证据，还没有 desk 自己的第一轮 clean replication；因此直接升 `P2` 会太早。

## 4. 下一轮唯一值得做的 survivor follow-up（供 bot2 排班参考，不在本轮执行）
如果 bot2 保留这条线的 survivor 锁定权，最小 follow-up 应收敛成：
- `BTC/ETH` 先行，必要时再加 `SOL`
- bar 粒度先做 `3m` 与 `5m`
- 两支分开：`q95/q99 continuation` vs `q10/q5 fade`
- 持有 `1/2/4` 根 bar
- friction ladder：`2 / 4 / 8 / 12 bps round-trip`
- 并排比较 `无确认` 与 `VWAP确认`
- 决策输出只回答：哪一支在成本后仍有 pocket，还是两边都过不了 friction

## 5. 本轮正式 verdict
- `rank`: `208`
- `verdict`: `keep_P1`
- `slot impact`: `Fresh intake slot` 更新为本对象
- `reader-facing change`: 有；因为这是一个新 intake + 新正式 rank + 新 verdict

## 6. 一句话结果
**`Rank 208 / extreme-return shock percentile` 正式记为 `keep_P1`：这条线值得保留的不是“论文里高频股票成本后归零”的大结论，而是“单资产极端 return shock 在短窗里到底 continuation 还是 fade”的双分支 raw-alpha baseline；但在做完 majors 上的 clean friction-first first verdict 前，还不够升 `P2`。**
