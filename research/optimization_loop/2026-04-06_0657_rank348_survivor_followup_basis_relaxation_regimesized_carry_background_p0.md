# 2026-04-06 06:57 UTC — Rank 348 survivor follow-up：basis relaxation × regime-sized funding carry 退回 background / P0

## 本轮执行对象
- target: `Rank 348 / basis relaxation × regime-sized funding carry`
- action: 对当前唯一 `Surviving candidate` 执行那唯一一次决定性 follow-up，直接回答它在 `BTC/ETH/SOL × 5m/15m × explicit after-cost` 口径下，是否真保留可迁移增量。

## 结论
**`Rank 348` 的唯一 survivor follow-up 已诚实收口：现有证据只证明它在 `BTC/ETH/SOL` 的 `8h funding-cycle` 账本上，靠 `regime-sized exposure` 改善了原始 carry 的 annualized Sharpe 和尾部路径风险；但它没有把优势压成当前 desk 需要的 `5m/15m` 可迁移 after-cost baseline，因此本轮不升 `P2`，直接退回 `background / P0`。**

## 为什么这轮不给 P2
这轮只补 portability / effectiveness / time / honesty，不再重复“它是不是旧 funding carry 换皮”。结论是：**它有独立主语，但还没有通过 desk transfer。**

### 1) effectiveness：改善真实存在，但主要停留在 8h funding-cycle 壳里
repo README 报告：
- `BTC`: `V2 Physics Sharpe 5.89` vs `Naive 4.73`
- `ETH`: `5.07` vs `4.53`
- `SOL`: `0.73` vs `-0.25`

同时 README 也明确提醒：
- **高 Sharpe 主要来自 `1,095 settlements/year` 的年化放大**；
- **绝对收益只有约 `2%~3% annualized`**。

这说明它的改进更像：
- 在既有 `8h carry + basis MTM` 壳里，靠 regime sizing 压了一部分 drawdown / path risk；
- 而不是已经证明有足够厚的、可直接迁移到 short-cycle desk 的独立 raw edge。

### 2) cross-asset：只覆盖 `BTC/ETH/SOL` 三个大币，且差异本身说明 transfer 依赖资产结构
README 与源码给出的对象只有：
- `BTCUSDT`
- `ETHUSDT`
- `SOLUSDT`

其中最关键的结构差异是：
- `BTC τ_relax ≈ 7.6h`，`ETH ≈ 7.1h`，都接近或低于 `8h funding period`；
- `SOL τ_relax ≈ 12.3h`，明显慢于 `8h funding period`。

所以它的所谓跨资产成功，本质上仍是：
- **大币上 funding/basis 回锚速度刚好匹配 `8h` 结算时钟时，regime sizing 有帮助；**
- **更慢的 alt（像 SOL）则依赖强行降仓才不至于亏损。**

这不足以说明它已经形成更广义、对 desk 有意义的 cross-asset portability；更像是“3 个大币 funding-cycle 壳里的仓位治理经验”。

### 3) time：论文与代码都把 payoff clock 固定在 funding cycle，不是 5m/15m alpha clock
`README` 与 `strategy/backtest_v2.py` 写得很清楚：
- funding 机制按 **8 小时结算**；
- 年化因子直接按 `sqrt(3 * 365)`；
- 回测主循环按 `cycle_index` 推进；
- 每一轮 PnL 都是 `funding_pnl + basis_pnl - fees` 的 **per-cycle** 累加。

这意味着：
- `1m/5m/15m` 在这套材料里更多只是 state refresh / execution shell 的想象空间；
- 真正被验证过的收益时钟仍然是 **next funding cycle**；
- 目前没有直接证据表明，把它切到 `5m/15m` decision clock 后，next-cycle net PnL / drawdown / adverse basis excursion 还能稳定改善。

### 4) honesty：这一点反而是优点，但优点不足以替代 portability
这套材料在 honesty 上是加分项：
- `backtest_v2.py` 显式使用 **signed funding**；
- 显式计入 **basis MTM risk**；
- 费用模型写成 **16 bps round-trip**；
- regime classifier 明确只是 **position sizing**，不是伪装成方向预测 alpha。

但也正因为它写得诚实，结论才更清楚：
- 它证明的是一个 **funding-cycle carry shell 的仓位治理升级**；
- 不是已经证明了一个能在当前 short-cycle desk 里直接晋级 `P2 admission` 的新可迁移基线。

## 本轮 verdict
按 policy，这次唯一 follow-up 用完后必须给终局结论。

本轮终局结论是：
- `Rank 348` **保留了独立主语**，这一点没有被推翻；
- 但它的增量目前仍主要停在 **`8h anchor + regime-sized carry governance`**；
- 还没有把增量压成当前 desk 所需的 **`BTC/ETH/SOL × 5m/15m × explicit after-cost`** 稳定 baseline；
- 因此 **不升 `P2`，直接退回 `background / P0`**。

## 对 runtime 的直接影响
- `Surviving candidate slot` 清空；`followup_budget_remaining` 归零。
- `Background pool.latest_parked` 更新为 `Rank 348` 本轮诚实收口结果。
- `cycle_plan` 第 1 项写成 `done`，其余小点保持不动，等待下一轮继续。

## 本轮改变系统认知的一句话
**`Rank 348` 证明了“basis relaxation × regime-sized governance”可以改善 funding-cycle carry 的路径风险，但这份增量仍锚在 `8h` payoff clock，尚未形成 `5m/15m` short-cycle desk 可迁移 after-cost baseline，因此 survivor follow-up 用尽后应退回 `background / P0`。**
