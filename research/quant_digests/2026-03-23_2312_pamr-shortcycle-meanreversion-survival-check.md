# 别把 PAMR 当可直接上线的 15m 神器：更该先复现的是“one-bar 横截面均值回归 + 低频调仓阈值”生存线
- 时间：2026-03-23 23:12 UTC
- 类型：经典论文 + 近 5 年工程仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：cross-sectional one-bar mean reversion（上一 bar 相对强弱在下一 bar 部分回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前口径下为负样本，需先改造后再进候选池）
- 主题标签：raw-alpha/mean-reversion/cross-sectional/online-portfolio/pamr/rebalance-throttle/turnover/cost/binance/crypto/1m/3m/5m/15m
- 证据类型：论文公式 + 开源实现 + 本地最小快检

## 1) 这次看了什么
先回答 base alpha：**这篇的 base alpha 不是趋势跟随，而是“上一根涨得多的资产下一根更容易回吐、跌得多的更容易反弹”的横截面短期回归**。  
我主看了 PAMR 经典公式（Li et al., 2012）+ 近 5 年可改造工程实现（ryanczm, 2024 里 `rsims.py` 的 trade buffer 思路），并在 Binance 公共 15m 数据上做了最小迁移快检。

## 2) 核心结论
- **一句话核心结论：** PAMR 这条 raw alpha 在我们当前 short-cycle 口径下**可复现但不可直接上线**；真正值得 intake 的是它的“均值回归分配逻辑 + 低频调仓/缓冲带降换手”骨架。  
- **一句话证明方式：** 同样 60 天、15m、8 资产篮子口径下，我跑了 `eps × rebalance cadence` 网格后，PAMR 在 perp 与 spot/BTC 两套宇宙都显著跑输对应等权基准，核心拖累来自换手与成本累积。

3 个关键数据点（本地快检）：
1. **Perp-USDT 宇宙（含 CASH）**：最佳参数也仅 `final=0.402`（`total_return=-59.78%`），而等权基准 `final=0.771`（`-22.86%`）。  
2. **Spot-BTC 宇宙（含 BTCBTC）**：最佳参数 `final=0.919`（`-8.09%`），仍弱于等权基准 `final=0.983`（`-1.74%`）。  
3. 两套宇宙最佳参数的平均换手分别约 **0.206/bar（perp）** 与 **0.398/bar（spot-BTC）**，在 15m 下对净值杀伤明显。

## 3) 为什么和当前 desk 直接相关
这不是 filter/overlay，而是可独立建模的 raw alpha（cross-sectional mean reversion）。它的价值在于：
- 给我们补一条和 breakout/momentum 不同机理的反向 alpha；
- 能完整拆成 entry/exit/sizing/risk/cost；
- 并且很快就能在 `1m/3m/5m/15m` 验证“是否被成本打穿”。

## 3.5) 策略拆解（必填）
- 方向属性：cross-sectional / mean-reversion / long-short（或 long-cash）
- 基础 alpha：横截面上一 bar 价格相对偏离会短时回归
- entry：按 PAMR 更新后目标权重与当前权重偏离触发调仓
- exit：权重回归到阈值内、超时、或 regime veto 触发减仓
- sizing：simplex 约束下按信号强度分配；可加权重上限与现金腿
- risk / veto：交易缓冲带（no-trade buffer）、最大单腿权重、日内回撤阈值
- cost：手续费/滑点显式扣减（本次快检按 5 bps 单边口径）

## 4) 可复刻最小实验（5m/15m 起步）
- 数据源：Binance Futures/Spot Klines（公开 REST）
- 公开性：公开可得，无需私钥
- 更新频率：1m/3m/5m/15m 可直接拉取
- 最小口径：
  - perp：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK + CASH`
  - spot/BTC：`ETHBTC/SOLBTC/BNBBTC/XRPBTC/DOGEBTC/ADABTC/LINKBTC/TRXBTC + BTCBTC`
  - 窗口：近 60 天 15m bars（约 5760 bars）
  - 参数：`eps ∈ {0.3,0.5,0.7,0.9}`，`rebalance_bars ∈ {1,2,4,8}`
- 首看指标：`final/Sharpe/MDD/avg_turnover` 与等权基准对比

## 5) 下一步怎么测（直接可执行）
1. **先做“降换手版 PAMR”**：引入 `trade buffer`（参考 `rsims.py`）+ `min notional band`，看 net 能否从负转平。  
2. **改成 market-neutral 版本再测**：从 simplex long-only 扩展到 dollar-neutral long/short（带杠杆上限），减少 beta 拖累。  
3. **做时段门控**：只在 liquidity 高、spread 低的 UTC 时段启用（先在 15m 测，再下钻 5m/3m）。  
4. **加执行约束敏感性**：maker/taker 混合、滑点分层、资金费（perp）三档压测，先画出生存边界再谈优化。

## 6) 风险与保留意见
- PAMR 原论文是经典在线组合框架，不是专为 crypto 高频微结构设计。  
- 当前最小快检是“工程可迁移性验证”，不是最终生产参数。  
- 在 short-cycle 下，若不先压换手，均值回归信号很容易被成本完全吞噬。

## 7) 来源
1. **Li, B., Zhao, P., Hoi, S. C. H., & Gopalkrishnan, V. (2012). _PAMR: Passive aggressive mean reversion strategy for portfolio selection_. Machine Learning.**  
   - DOI: `10.1007/s10994-012-5281-z`  
   - Readable URL: https://link.springer.com/article/10.1007/s10994-012-5281-z
2. **Chew, R. (2024). _Crypto-Stat-Arb_ (GitHub repository).**  
   - Repo URL: https://github.com/ryanczm/Crypto-Stat-Arb
3. **Binance API Docs (Klines).**  
   - Futures: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data  
   - Spot: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data

## 8) 本地产物
- `reports/artifacts/quant_digests/pamr_shortcycle_probe_20260323/perp_usdt_grid.csv`
- `reports/artifacts/quant_digests/pamr_shortcycle_probe_20260323/spot_btc_grid.csv`
- `reports/artifacts/quant_digests/pamr_shortcycle_probe_20260323/summary.json`
