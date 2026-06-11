# 别把这份 2026 跨预测市场 repo 只读成 dashboard：对 short-cycle desk，更该先测的是「same-hour strike mismatch × binary lock-in arb」

- 时间：2026-04-08 03:22 UTC
- 类型：GitHub 新 repo + 内置 thesis + backend source audit
- 主题类型：raw alpha
- 基础 alpha：同一小时到期的 BTC 二元事件，在 Polymarket 与 Kalshi 上会因**strike 设定与合约表达不同**出现可锁定的组合错价；当 `Poly leg + Kalshi leg + fee_buffer < 1` 时，可做跨 venue binary arb。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（更适合先做 `1m / 3m` 事件驱动版）
- 主题标签：raw-alpha / relative-value / stat-arb / prediction-market / polymarket / kalshi / binary / same-expiry / strike-mismatch / 1m / 3m / 5m / repo / public-data / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
这次主看 `CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot`，重点不是它的可视化，而是 repo 自带的 `thesis.md` 和 `backend/arbitrage_bot.py` 把一个可独立复现的 raw alpha 讲得很清楚：**同一小时到期的 BTC 价格事件，如果 Polymarket 的 strike 和 Kalshi 的 strike 没完全对齐，就能用跨市场双腿把终局 payout 锁成至少 1 美元，但买入成本有时低于 1 美元。**

## 2. 核心结论
- 这条 edge 的 base alpha 很直接：不是情绪、不是预测，而是**same-expiry binary contract mispricing**。repo 明写两种组合：当 `Poly Strike > Kalshi Strike` 时检查 `Poly Down + Kalshi Yes`；反过来则检查 `Poly Up + Kalshi No`。
- README 写得很明确：系统**每秒抓一次**两边实时价格，并把“`Total Cost < $1.00`”当成 arbitrage 判定门槛。翻成人话：这不是长篇理论，而是已经落成了实时扫描器。
- `thesis.md` 给出的 payout 逻辑也够硬：由于两边 strike 不同，最终价格只要落在“低于低 strike / 位于两 strike 之间 / 高于高 strike”这三种状态之一，组合里至少有一条腿会兑付 `$1`；如果建仓成本低于 `$1`，理论上就锁进了毛利。
- `arbitrage_bot.py` 进一步把它写成可执行逻辑：按 strike 关系选方向、读取双方 best price、计算 `total_cost` 与 `profit = 1 - total_cost`，再输出最佳机会。也就是说，这不是“研究灵感”，而是已经接近完整策略壳。

## 3. 为什么和当前项目有关
这条线和当前 desk 的关系，在于它补的是**极短持有、明确定价上限、公开数据可拿**的 relative-value raw alpha：
- 数据公开：Polymarket CLOB + Kalshi API；
- 逻辑简单：不是预测 BTC 涨跌，而是找两个 venue 对**同一到期事件**的错误拼接；
- 适合短周期：天然更像 `1m / 3m` 事件流策略，`5m` 还能做机会聚合，`15m` 更适合拿来做监控/容量统计而不是主信号。

如果我们想持续扩充“可直接落地、不是只靠回归系数讲故事”的 raw alpha 素材池，这类**硬到期、硬 payout、硬价差**的题材是值得保留的。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb
- 基础 alpha：same-expiry BTC binary markets 的 strike mismatch 造成组合成本低于最小到期兑付
- regime：接近整点到期、两边同时活跃、order book 尚可成交的窗口
- filter / veto：只保留相同 expiry、相同底层定义、strike 可清楚映射的市场；若任一边深度太薄、暂停交易、报价陈旧、或 fee 后边际不足，则 veto
- risk / sizing / execution overlay：仓位按双腿最小可成交深度定；优先只做 `expected_locked_edge > fees + slippage + cancel risk` 的组合；若两腿未能同步成交、或 expiry mapping 不一致，立即降仓/撤单

## 4. 可复刻的最小实验
- **研究假设**：在 Polymarket 与 Kalshi 的 BTC 1-hour markets 上，same-expiry strike mismatch 会持续产生 `combo_cost < 1` 的短时窗口，且在扣掉两边费用后仍保留正的锁定收益。
- **可计算定义**：
  - 对每个相同 expiry 的市场对，抓 `poly_up / poly_down / kalshi_yes / kalshi_no`
  - 若 `poly_strike > kalshi_strike`，算 `combo_cost = poly_down_ask + kalshi_yes_ask + fee_buffer`
  - 若 `poly_strike < kalshi_strike`，算 `combo_cost = poly_up_ask + kalshi_no_ask + fee_buffer`
  - 入场：`combo_cost < 1 - edge_min`
  - 出场：持有到 expiry，或在二级市场提前收敛时平掉
- **最小回测切口**：先做最近 `30~60` 天的 BTC hourly markets，按秒级/事件级快照回放，再聚合成 `1m / 3m / 5m` 机会统计；`15m` 只看容量与机会密度。
- **最该先看 2 个指标**：`post-fee locked edge per trade`、`orphan-leg ratio`。前者决定值不值得做，后者决定这是不是“纸上无风险”。

## 5. 风险与保留意见
- repo 把它写成“risk-free”，但实盘里最真实的风险是**双腿不同步成交**、queue 被抢、撤单失败、或其中一边临近结算时流动性突然消失。
- Kalshi/Polymarket 的规则文本、到期时间、strike 表述要严格对齐；只要 mapping 有一个细节搞错，就不是套利而是裸方向。
- 这条线天然偏事件化，不是全天连续流策略；更适合做素材池里的**高确定性小容量 sleeve**。
- 真正上线前，必须补 fee schedule、资金占用、API 限速、最小下单单位与 market halt 风险，不然 `$1 - total_cost` 很容易只是毛边际。

## 6. 来源
1. CarlosIbCu. (2026). **Polymarket-Kalshi BTC Arbitrage Bot**.
   - Repo URL: `https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot`
2. CarlosIbCu. (2026). **The Arbitrage Thesis**.
   - Readable URL: `https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot/blob/main/thesis.md`
3. 关键源码：
   - `backend/arbitrage_bot.py`
   - `backend/fetch_current_polymarket.py`
   - `backend/fetch_current_kalshi.py`
