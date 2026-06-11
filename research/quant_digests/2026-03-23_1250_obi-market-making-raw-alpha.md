# 别把 OBI 只当 veto：这份高信号新仓库更适合先复现「订单簿失衡驱动的做市 raw alpha」
- 时间：2026-03-23 12:50 UTC
- 类型：GitHub 新仓库教程 + 微观结构论文链路
- 主题类型：raw alpha
- 基础 alpha：Order Book Imbalance（OBI）标准化后对短时价格漂移的预测（用于 fair value 偏移与双边报价）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/order-book-imbalance/market-making/relative-value/execution/cost/latency/1m/3m/5m/15m
- 证据类型：工程证据 + 文献证据

## 1. 这次看了什么
这次主看 **nkaz001/hftbacktest（持续更新，2026 仍活跃）** 里的官方教程 **Market Making with Alpha - Order Book Imbalance**。先回答 base alpha：**不是趋势线/突破确认，而是盘口买卖深度不平衡（OBI）对未来几秒到几十秒价格漂移的预测**，再把这个 alpha 直接塞进做市报价中心（reservation/fair price）。

## 2. 核心结论
- **一句话核心结论：** OBI 在 crypto perp 上可以作为可独立复现的 raw alpha，不必降级成“只做否决层”。
- **一句话证明方式：** 教程给了完整可运行代码（信号→报价→库存约束→费用模型→队列模型）和多时段回测结果，不是口头经验。
- 教程样例（BTCUSDT，2023-05）给出：`SR≈10.83`、`Return≈34.24%`、`MaxDD≈3.72%`、`Return/Trade≈0.0139%`（含 maker rebate 假设）。
- 同参数迁移到更近市场（BTCUSDT，2025-01~02）仍有：`SR≈5.37`、`Return≈45.96%`、`MaxDD≈9.79%`、`Return/Trade≈0.0086%`，显示 edge 在衰减但未消失。
- 2025-05~07 进一步走弱到 `SR≈3.04`、`Return/Trade≈0.0044%`，说明这条 alpha 的生存条件高度依赖**费率+排队成交质量+延迟控制**。
- 最值得复用的不是某个单阈值，而是这条完整骨架：`OBI z-score -> fair_price 偏移 -> 库存 skew -> 双边挂单更新 -> 成本后评估`。

## 3. 为什么和当前项目直接相关
- 直接补充我们现在最缺的池子：**microstructure raw alpha**（区别于最近大量 filter/gate 主题）。
- 能服务 `1m/3m` 快节奏研发（信号在秒级计算），也能反哺 `5m/15m`：作为执行层 alpha（更优入场时点、少吃冲击）。
- 该主题天然包含完整策略要件：entry/exit、仓位上限、库存风控、交易费/返佣、延迟与排队模型。

## 3.5 策略拆解（必填）
- 方向属性：做市型短周期 alpha（可带轻度方向偏置），本质是微观结构相对价值
- 基础 alpha：`alpha_t = zscore(sum_bid_depth - sum_ask_depth)`（或 VAMP/micro-price 变体）
- regime：高流动性、点差稳定、盘口深度连续、延迟可控时更有效
- filter / veto：极端跳价、盘口真空、消息冲击窗口、队列成交率塌陷时停机
- risk / sizing / execution overlay：
  - `reservation_price = fair_price - skew * normalized_position`
  - `max_position_dollar` 硬上限
  - 挂单网格 `grid_num/grid_interval`
  - 成本模型必须显式计入 `maker/taker + 滑点 + 延迟`

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** OBI 标准化信号在 Binance USDT perp 上可提供可交易的秒级 edge，且在成本后仍有正期望。
- **最小定义：**
  1) 数据：Binance perp 公共深度流（top N 档）+ 成交流；采样到 `1s`。
  2) 信号：`obi_raw = sum_bid_qty(0~x%) - sum_ask_qty(0~x%)`，`obi_z = rolling_zscore(30m~60m)`。
  3) 交易：每 `1s` 更新 `fair_price = mid + c1*obi_z`，双边挂单；库存超阈值时只留一侧降仓。
  4) 出场：库存回归、alpha 反转或超时撤单；异常波动触发 kill-switch。
- **样本与周期：**先跑 BTC/ETH 最近 30 天，输出按 `1m/3m` 统计；再汇总到 `5m/15m` 看稳定性。
- **先看 4 个指标：**`post_cost_pnl`、`return_per_trade(bp)`、`fill_ratio`、`inventory_drawdown`。

## 5. 风险与保留意见
- 这条 alpha 对“成交质量”极敏感：排不到队、撤单慢、返佣不足，都会把 edge 吃掉。
- 教程结果包含特定费率假设（含 maker rebate）；实盘需按我们账户等级重算。
- 秒级策略的 infra 要求高，若当前 desk 先跑 `5m/15m`，建议先把它当**执行增强层**并行验证。

## 6. 来源
1. **nkaz001. (ongoing, accessed 2026). _hftbacktest_. GitHub repository.**
   - Repo URL: https://github.com/nkaz001/hftbacktest
   - Readable URL: https://github.com/nkaz001/hftbacktest
2. **hftbacktest Docs. _Market Making with Alpha - Order Book Imbalance_.**
   - Readable URL: https://hftbacktest.readthedocs.io/en/latest/tutorials/Market%20Making%20with%20Alpha%20-%20Order%20Book%20Imbalance.html
3. **Stoikov, S. (2018). _The micro-price: a high-frequency estimator of future prices_. Quantitative Finance.**
   - DOI: `10.1080/14697688.2018.1489139`
   - Readable URL: https://doi.org/10.1080/14697688.2018.1489139
4. **Martin, R., Line Jr., W., & Feng, L. (2023). _Mind the Gaps: Short-Term Crypto Price Prediction_. SSRN.**
   - DOI: `10.2139/ssrn.4351947`
   - Readable URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4351947
