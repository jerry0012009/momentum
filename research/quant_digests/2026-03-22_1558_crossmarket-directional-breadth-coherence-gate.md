# 别把 cross-market gate 继续写成“单币先动”：`directional breadth coherence` 更像 15m 的 asymmetric continuation veto
- 时间：2026-03-22 15:58 UTC
- 类型：论文 + Binance 公共数据最小快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/cross-market/intraday/directional-breadth/coherence/continuation/failure/filter/paper/crypto/5m/15m
- 证据类型：论文证据 + 工程快检

## 1. 这次看了什么
这次不再重复“BTC 先动”单 leader 口径，而是沿着 **Xu et al. (2024) Cross-Market Intraday TSMOM** 的思路，抽一个更适合 desk 的旁支变量：

**信号前 1 小时，主流币 5m 收益对“当前方向”的一致性（directional breadth coherence）**。

直觉上，它更像我们三条收口线都能复用的 `avoid-chop / continuation-confirmation` 层：
- 一致性很差，说明市场在打架；
- 一致性高，说明“至少方向语义一致”，再谈 follow-up 才更诚实。

## 2. 核心结论
- **一句话核心结论：** 在 15m breakout proxy 上，`directional breadth` 越差，成本后表现越差；它更像一个可共享的 continuation 质量过滤层，而不是方向预测器。
- **一句话它怎么证明：** 用论文给的 cross-market intraday 框架做最小本地快检（BTC/ETH/SOL，15m breakout proxy，前 1h 的 5m directional breadth），分桶后看到显著梯度：低一致性桶最差，高一致性桶相对最好。
- 本轮快检（近 150d，`N=3772`，`20-bar breakout`，`hold=4 bars`，`12bps round-trip`）结果：
  - `high breadth > 0.60`：`N=2375`，`mean net = -6.98 bps`
  - `mid (0.45,0.60]`：`N=1265`，`mean net = -12.68 bps`
  - `low <= 0.45`：`N=132`，`mean net = -25.26 bps`
- 也就是说，虽然 proxy 本身仍偏弱（总体仍负），但 **低一致性桶明显更差**，是非常便宜的 veto 候选。
- 方向上有明显不对称：`low breadth` 下 long 侧最差（`-41.16 bps`），short 侧仅 `-6.19 bps`；这提示它更适合先用于 **Fib/EMA 长侧收口的硬 veto**，对 breakout-short 更像轻量过滤而非强 veto。

## 3. 为什么和当前项目有关
- **`V3 final-verdict / breakout-short follow-up`**：可把它作为 `post-break continuation` 的便宜质量分层。当前证据看 short 侧改善有限，所以先做“极低一致性降权/半仓”，别直接 hard deny。
- **`Fibonacci confirmation / retest_hold`**：最直接受益点。若信号前 1h `directional breadth <= 0.45`，long retest_hold 很可能只是噪音回弹，优先 veto。
- **`EMA / PSAR raw alpha focus`**：可作为 shared context gate（特别是 long lane），先挡掉市场分歧过大的口袋，再让 EMA/PSAR 负责触发。
- 如果问“这轮为什么值得做”：它正好补了我们在 `单 leader` 与 `流数据 overlay` 之间的空档——**只用公开行情、低实现成本、可快速接入三条收口线**。

## 4. 可复刻的最小实验
- **研究假设：** 对 15m 三条收口线，信号前 1h 的跨资产 directional breadth 越低，后续 continuation 质量越差；把它做成 gate 可改善成本后质量。
- **可计算定义（事件时刻 t，方向 d∈{+1,-1}）：**
  1. 取 `BTC/ETH/SOL` 在 `(t-60m, t]` 内 5m returns；
  2. `aligned = 1(sign(ret)==d)`；
  3. `dir_breadth_1h = mean(aligned)`（对时间×资产双维平均）。
- **最小回测切口：**
  - 标的：BTC/ETH/SOL perp
  - 周期：15m
  - 先接现有三条线，不改 entry/exit，只加 gate：
    - `baseline`
    - `soft gate`: `dir_breadth_1h <= 0.45` 时 half-size
    - `hard gate`: `dir_breadth_1h <= 0.45` 直接 veto
  - 成本：`6/10/15 bps per side` 三档
- **先看 3 个指标：**
  1. `post_cost_expectancy`
  2. `false_follow_ratio`（入场后 2~4 bar 快速反向）
  3. `trade_retention`
- **下一步怎么测（本轮建议直接执行）：**
  1) 先在 `Fib retest_hold long` 与 `EMA/PSAR long` 上跑 `low-breadth veto`；
  2) breakout-short 只先试 `low-breadth half-size`，不急着 hard veto；
  3) 若 OOS 下 `trade_retention` 仍 >70% 且净值改善，再升级为 shared gate。

## 5. 风险与保留意见
- 这轮是 `breakout proxy` 快检，不是三条正式策略的 clean replication；结论只能说明“变量有信息”，不能直接当 production 阈值。
- `low breadth` 样本占比仅约 `3.5%`，有稀疏风险；先做 veto/降仓比直接做连续打分更稳妥。
- 该变量天然会随市场结构漂移（牛熊切换、波动状态变化），需要 rolling 监控分布。
- 当前结果显示它对 long 侧更强、short 侧更弱，**不应多空镜像套同一阈值**。

## 6. 来源
1) Xu, D., Li, B., Singh, T., & Li, J. (2024). *Cross-Market Intraday Time-Series Momentum*. SSRN Working Paper.
- Venue: SSRN
- DOI: `https://doi.org/10.2139/ssrn.4765613`（早期版本：`10.2139/ssrn.4651331`）
- Readable URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4765613`
- Repo URL: N/A

2) Li, Z., Sakkas, A., & Urquhart, A. (2022). *Intraday time series momentum: Global evidence and links to market characteristics*. Journal of Financial Markets, 57, 100619.
- Venue: Journal of Financial Markets
- DOI: `https://doi.org/10.1016/j.finmar.2021.100619`
- Readable URL: `https://www.sciencedirect.com/science/article/pii/S1386418121000064`
- Repo URL: N/A

3) Binance USDⓈ-M Futures API（公开行情）
- Data source: `https://fapi.binance.com/fapi/v1/klines`
- Public availability: 公开 REST，无需私钥
- Update frequency: 5m / 15m Kline 实时滚动更新
- 本轮最小复核产物：
  - `reports/artifacts/quant_digests/crossmarket_directional_breadth_proxy_20260322/summary.csv`
  - `reports/artifacts/quant_digests/crossmarket_directional_breadth_proxy_20260322/side_split.csv`
  - `reports/artifacts/quant_digests/crossmarket_directional_breadth_proxy_20260322/event_log.csv`
  - `reports/artifacts/quant_digests/crossmarket_directional_breadth_proxy_20260322/metadata.json`
