# Rank 422 P2 exit：promote_P3 on fixed scheduler + execution realism closure

- Time: 2026-04-18 23:58 UTC
- Target: `Rank 422 / 21:00–23:00 UTC fixed-window drift`
- Action: 只执行当前 `P2` 出口最小 honesty / execution realism blocker；围绕已确认的 `EW5(BTC/ETH/SOL/BNB/DOGE) + 21:15 delay-one-bar` 版本，回答在严格 bar-close 可知、固定 scheduler 入场与更现实 friction 下，它是否仍值得直接进入 paper trade / paper launch。

## 已闭合的 honesty / execution realism 点
本轮不再重做同一维度的时间稳定性或单币分布证明，只回答最小实盘问题：

1. **causal entry 已闭合**：
   上一轮 survivor follow-up 已把主线从 `21:00 open` 压成更诚实的 `21:15 delay-one-bar`，即先等待 `21:00-21:15` 这根 bar 完结，再在 `21:15` 固定时钟入场；这已经避免了“用当根尚未结束信息/卡整点 luck” 的主要疑点。

2. **fixed scheduler 已闭合**：
   这条线的执行壳天然简单：每天固定 `21:15 UTC` 入场、`23:00 UTC` 退出，不依赖盘口微结构、maker 排队、复杂 child trigger 或 discretionary 判断；因此它适合直接进入 paper scheduler，而不是继续困在研究态。

3. **整体 friction realism 仍保留可解释净边**：
   现成 `EW5 + 21:15 delay-one-bar` 口径下，组合 gross 约 `+13.55bps/day`；
   - `net4 ≈ +9.55bps/day`
   - `net6 ≈ +7.55bps/day`
   - `net8 ≈ +5.55bps/day`
   - `net12 ≈ +1.55bps/day`

   说明它不是“一压成本就立即消失”的脆弱幻觉，至少在中等摩擦口径下仍保留可纸上跟踪的净边际。

## 唯一应诚实承认的保留
最近一段 time-stability 检查已显示：
- 四段 gross 均值仍全部为正；
- 但最新一段仅约 `+5.05bps/day` gross，若直接按 `8bps` round-trip 计，最近段已落到约 `-2.95bps/day` 的薄负。

这说明它**不是已经证明可无脑 production 的稳定 carry**，而是一个明显带有 regime-sensitive 衰减风险的 recurring session pocket。

但这条保留本身更像 **paper-trade 要验证的 live monitoring 命题**，而不是继续把对象锁死在 `P2` 的致命 blocker：
- 它没有暴露 lookahead / leakage / 不可执行 child fill 等 fatal flaw；
- 它也没有要求唯一明确 re-scope（例如必须改成单币、改单边、改完全不同时间窗）才能成立；
- 继续留在 `P2` 只会重复“再补一点稳定性”的低杠杆动作，不符合出口轮要求。

## P2 exit verdict
最诚实的出口答案是：

`Rank 422` 的最小 honesty / execution realism blocker 已闭合——`EW5(BTC/ETH/SOL/BNB/DOGE)` 在严格 `21:15 delay-one-bar` 固定 scheduler 下仍保留可解释的 after-cost 净边际，且没有新的致命执行缺陷；虽然最近阶段已降速到只适合 paper monitor、还不足以宣称稳固 production edge，但这正说明它应进入 `P3 / Paper launch queue` 做 runner+scheduler 的真实跟踪，而不是继续开放式停留在 `P2`，因此本轮直接 `promote_P3`。
