# 别把 OBI 直接当 15m 逐根信号：更像该先测的是 crash-risk nowcast 做三条线的仓位闸门
- 时间：2026-03-18 11:25 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/order-imbalance/regime/risk-overlay/position-sizing/crypto/15m
- 证据类型：论文证据（主）+ 可公开复现实验口径（辅）

## 1. 这次看了什么
这次看的是 Koutmos & Wei（2023）在 *Review of Quantitative Finance and Accounting* 的论文 **Nowcasting bitcoin’s crash risk with order imbalance**。它主线不是“做 15m 入场信号”，而是用 `order flow imbalance + 区块链/网络价值控制变量` 去做 **比特币崩跌风险的提前预警**。对我们 desk 更有价值的旁支读法是：把它降级成 `regime gate / 仓位 overlay`，服务当前三条收口线，而不是硬改成逐根 15m 主 alpha。

## 2. 核心结论
- **一句话核心结论**：这篇论文最值得借的不是“猜下一根涨跌”，而是“先估计当前是不是 crash-prone 状态，再决定是否放行信号和给多大仓位”。
- **一句话证明方式**：作者用两类模型（`GEV` 与 `logistic`）对 crash risk 做 nowcast，并把 order imbalance 放进解释变量；结果显示两种模型在准确度上可比，但 `type I / type II error` 会随概率阈值显著迁移，说明“阈值治理”本身就是策略设计的一部分。
- 论文样本覆盖了 **COVID-19** 时段与 **FTX 崩盘** 时段，说明它研究的是“极端风险阶段”的可预警性，而不是平静期里的小波动择时。
- 对我们三条线的直接启发：`breakout-short follow-up` 可以把高 crash-risk 视为顺风环境；`Fib retest_hold` 与 `EMA/PSAR continuation` 的 long 侧则应在高 crash-risk 状态下降仓或加 veto，而不是继续等权开火。

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：这篇论文给的是“是否处在下行脆弱期”的先验，不是 entry；它更像 continuation 的环境门。
- 对 `Fibonacci confirmation / retest_hold`：很多“回踩守住”在系统性下行冲击里会被二次击穿；先做 crash-risk gate 能减少把结构确认误读成低风险环境。
- 对 `EMA / PSAR raw alpha focus`：EMA/PSAR 继续管方向，crash-risk 负责“该不该降杠杆/减仓/禁多”。这比继续堆同类价格过滤器更像独立增量。
- 若问“为什么它比继续收口三条线更值得”：答案是它不是新分支，而是能被三条线共用的风险层，且能快速做最小实验。

## 4. 可复刻的最小实验
- **研究假设**：在 `BTC/ETH/SOL` perpetual 的 `15m` 上，为现有三条 setup 增加 `crash-risk probability` overlay，可在成本后降低回撤与假 hold 损失。
- **公开数据源（可快速拿）**：
  1. Binance `aggTrades`（公开 REST）：1m 主动买卖量代理，用于 imbalance；
  2. Binance mark/index klines（公开 REST）：构造波动与回撤标签；
  3. （可选）公开 funding / OI（若接入快则加，不快先不加）。
- **最小定义**：
  1. `flow_imb_1m = (buy_vol - sell_vol)/(buy_vol + sell_vol + 1e-8)`；
  2. 聚合到 15m 得 `imb_level` 与 `imb_shock`（近 3~6 根变化）；
  3. 定义 crash 标签：未来 `8` 根内最大不利收益 <= `-1.2*ATR(14)`（可做 `-1.0/-1.5 ATR` 灵敏度）；
  4. 用 rolling logistic 估 `p_crash_t`（日更或每 4h 更新均可）；
  5. 应用于三条线：
     - breakout-short：`p_crash_t` 高于阈值时允许正常或略增仓；
     - Fib/EMA long：`p_crash_t` 高于阈值时减仓（如 50%）或直接 veto。
- **最小回测切口**：近 `180~365` 天，15m，next-bar open，no-overlap；成本先看 `6/10/15 bps per side`。
- **先看 4 个指标**：`post-cost return`、`max drawdown`、`false-hold rate`（入场后4根内反向穿透阈值）、`trade_count retention`。
- **下一步怎么测**：先做最小 ablation：`base` vs `base+binary gate` vs `base+position sizing`。如果只有强阈值禁入有效、而连续仓位缩放无效，就优先保留简单 gate，别把 overlay 复杂化。

## 5. 风险与保留意见
- 论文主问题是 crash nowcast，不是 5m/15m 高频入场；直接平移成逐根交易信号会失真。
- 文中模型阈值会显著改变 I/II 错误结构，实盘侧必须先定义“宁可错过还是宁可误杀”的风险偏好。
- 论文资产核心是 BTC；迁移到 ETH/SOL 需要独立校准，不能默认参数共享。
- 该论文未提供官方公开代码仓库，复现要自行实现特征工程与滚动训练管线。

## 6. 来源
- Koutmos, D., & Wei, W. C. (2023). *Nowcasting bitcoin’s crash risk with order imbalance*. **Review of Quantitative Finance and Accounting**, 61, 125–154.
- DOI: `10.1007/s11156-023-01148-1`
- Readable URL: <https://link.springer.com/article/10.1007/s11156-023-01148-1>
- DOI URL: <https://doi.org/10.1007/s11156-023-01148-1>
- Repo URL: `N/A（论文未给官方代码仓库）`
- 论文注释中可见数据入口示例：
  - Bitstamp order book API: <https://www.bitstamp.net/api/#order-book>
  - Blockchain charts: <https://www.blockchain.com/charts>
