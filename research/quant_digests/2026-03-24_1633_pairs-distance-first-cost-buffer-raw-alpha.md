# 别把 pairs 默认从 cointegration 开始：这篇近 5 年论文更该先测的是「Distance-first 选对 + trade-buffer/cost 治理」完整 raw alpha 骨架
- 时间：2026-03-24 16:33 UTC
- 类型：近 5 年论文 + stat-arb 开源仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：跨币种配对价差的短周期均值回归（relative-value / stat-arb）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/distance-method/correlation/cointegration/trade-buffer/commission/cost/binance/1m/3m/5m/15m/paper/repo
- 证据类型：论文证据 + 工程仓库 + 本地公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“配对价差偏离后回归均值”**，不是单纯 filter。主论文是 Ko 等（2023 online / 2024 print）对 crypto pairs 六种选对方法的对比；工程侧补了 `ryanczm/Crypto-Stat-Arb` 里可直接借用的 `trade_buffer + commission + funding` 回测骨架。

## 2. 核心结论
- 论文给的最重要信息不是“pairs 能不能做”，而是：**在他们样本里，Distance 选对法在 1m/5m/60m 都是稳健前排**。文中给出的 Distance 总收益分别是 **208.12%（1m）/236.31%（5m）/210.36%（60m）**（Binance、30 币、2022-01-01~2022-03-31）。
- 同一论文还给出一个对 desk 很实用的旁支：在 `1m/5m` 上 Cointegration 与 Hurst 表现“接近 Distance”，但在 `60m` 上 Distance 在风控与成功率维度更稳，说明**先用 Distance 做候选池，再让更重方法做二次筛选**是更实操的路线。
- 本地最小快检（Binance USDT perp 5m，8 个主流币，2025-12-01~2026-03-24，3d lookback、日频换对、entry z=2、pair round-trip 成本=20bps）里，绝对收益仍为负，但 **Distance 依然优于相关系数选对**：
  - Distance：`avg -180.16 bps/对-日`，win-rate `24.24%`，110 天累计 `-594.54%`
  - Correlation：`avg -197.38 bps/对-日`，win-rate `14.24%`，110 天累计 `-651.36%`
- 翻成人话：**方法排序优势存在，但“没过成本线”就不是可交易 alpha**。先解决执行与换手，再谈更复杂模型。

## 3. 为什么和当前项目有关
- 这条线直接补的是 desk 当前最该补的 `pairs / relative-value / stat-arb` raw alpha 素材池，不是再做一层泛 filter。
- 对 `1m/3m/5m/15m` 的现实价值：可以先从 `5m/15m` 建立可执行骨架，再下钻 `3m/1m`；流程上与现有 first-verdict → clean replication 完全兼容。
- `Crypto-Stat-Arb` 仓库里已有可借鉴的交易摩擦治理：`commission_pct=0.0015` 与 `trade_buffer=0.05` 的回测接口，适合直接嫁接到 pairs 框架，避免“理论有 edge，实盘被换手吃光”。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 配对均值回归（market-neutral 倾向）
- 基础 alpha：配对 spread 的偏离回归（z-score reversion）
- regime：波动分层（高波动降权或停做）、交易时段分桶（亚洲/欧盘/美盘）
- filter / veto：
  - 一级：Distance 选前 N 对
  - 二级：Cointegration/Hurst/半衰期阈值（二选一即可）
  - 三级：流动性与点差门槛（不达标 veto）
- risk / sizing / execution overlay：
  - sizing：对内 equal-risk，组合层做 gross/net cap
  - execution：next-bar + no-trade buffer，减少微小再平衡
  - cost：显式手续费+滑点+冲击阶梯；先过 cost cliff 再扩交易数

## 4. 可复刻的最小实验
- 研究假设：在短周期 pairs 里，**Distance-first 选对**可作为更快、更稳的候选池入口；alpha 是否存活取决于成本与换手治理。
- 最小可复现实验口径：
  - 数据源：Binance Futures `fapi/v1/klines`（公开、5m 可持续更新）
  - 标的：先 8~12 个高流动 perp（BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK…）
  - 周期：5m 执行，15m 做 regime gating；再下钻 3m
- 先看 3 个指标：
  1) 成本后 `avg net bps/trade`；
  2) `trade_count` 与 `win_rate` 的交换比；
  3) veto 前后 turnover 与净收益变化。
- **下一步怎么测**：
  1) 补齐 Cointegration/Hurst 分支（当前环境缺 `statsmodels`，先装依赖后与 Distance 同口径对照）；
  2) 做 `cost ladder`（8/12/16/20 bps）+ `trade_buffer`（0/2%/5%/8%）二维网格；
  3) 把“选对频率”从日频改为 12h/6h，检验 turnover-信号衰减最优点；
  4) 仅保留“流动性×点差”达标 pair，观察是否从负毛利回到可生存 pocket。

## 5. 风险与保留意见
- 本地快检只是 first verdict，不是论文精确复现；当前结果仍未过成本线。
- 论文样本期较短（3 个月）且市场状态特定，迁移到当前市场需做分段稳健性。
- 如果只看“方法排名”不看执行约束，会高估真实可交易性。

## 6. 来源
1) Ko, P.-C., Lin, P.-C., Do, H.-T., Kuo, Y.-H., Mai, L. M., & Huang, Y.-F. (2024). *Pairs trading in cryptocurrency markets: A comparative study of statistical methods*. Investment Analysts Journal, 53(2), 102–119.  
   - DOI: `10.1080/10293523.2023.2268386`  
   - Readable URL: `https://doi.org/10.1080/10293523.2023.2268386`  
   - Venue URL: `https://www.tandfonline.com/doi/full/10.1080/10293523.2023.2268386`

2) ryanczm. (2024). *Crypto-Stat-Arb* (GitHub repository).  
   - Repo URL: `https://github.com/ryanczm/Crypto-Stat-Arb`  
   - README URL: `https://raw.githubusercontent.com/ryanczm/Crypto-Stat-Arb/master/readme.md`  
   - Backtest notebook URL: `https://github.com/ryanczm/Crypto-Stat-Arb/blob/master/stat-arb-backtest.ipynb`

3) Binance Developers. *USDⓈ-M Futures API – Kline/Candlestick Data*.  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

4) 本地最小快检 artifact（2026-03-24）  
   - `reports/artifacts/quant_digests/pairs_distance_vs_corr_probe_20260324/summary.json`  
   - `reports/artifacts/quant_digests/pairs_distance_vs_corr_probe_20260324/distance_pairday_stats.csv`  
   - `reports/artifacts/quant_digests/pairs_distance_vs_corr_probe_20260324/correlation_pairday_stats.csv`
