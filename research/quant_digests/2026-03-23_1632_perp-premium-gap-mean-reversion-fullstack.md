# 别把 perp basis 只当 short veto：这份 2026 新仓库更值钱的是「mark-vs-oracle premium gap」可双向落地的 raw alpha 骨架
- 时间：2026-03-23 16:32 UTC
- 类型：近 5 年新仓库 + 永续文献线索 + 交易所公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：mean reversion（perp `mark - oracle` premium 的极端偏离回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/perpetual/premium/basis/mark-vs-oracle/stat-arb/cost/risk/repo/paper/crypto/1m/3m/5m/15m
- 证据类型：仓库代码规则 + 官方 API 文档 + 本地快检（可复现）

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“极端 premium gap 的均值回归”，不是 filter。**

本轮选题用的是 2026 新仓库 **andreaambrosio/hype-backtesting** 里的 `Basis Dislocation Reversion` 分支（不是继续围绕 breakout/retest 的旁支 gate）。
它直接把策略拆成了完整可执行骨架：
- entry：`abs(premium_bps)` 超阈值 + 超过滚动分位（95%）
- direction：`premium>0` 做空 perp，`premium<0` 做多 perp（双向）
- exit：回归到低阈值 / 超时 / 继续恶化触发 stop
- sizing：按 dislocation 强度缩放仓位（上限封顶）
- cost/risk：显式手续费、滑点、最大回撤 kill-switch

这比“把 basis 写成 no-short gate”更符合当前 desk 的优先级：**可独立复现且可直接落地完整策略的 raw alpha。**

## 2. 核心结论
- **一句话结论：** `mark-vs-oracle premium gap reversion` 可以作为独立 raw alpha intake，但它是明显的“结构化 pocket alpha”，必须靠阈值、持仓时长与成本控制才能活。  
- **一句话证据：** 新仓库给了完整策略实现与回测口径；我再用 Binance 公共 `premiumIndexKlines` 在 5m 做最小代理快检，结论是“全池默认参数不行，但收紧阈值后在局部品种可见正 net pocket”。

最该记住的 3 个数据点：
1. 仓库 README 报告：`Basis Dislocation Reversion` 在其 90 天样本下 **Return +3.88%，Sharpe 4.52，Trades 299**（其口径内）。
2. 我的 Binance 5m 代理快检（4 币等权、默认参数）结果：**ALL_EQ net = -0.3672 bps/bar**（成本后失活）。
3. 同一数据下做小网格后，`SOLUSDT` 出现 pocket：`roll=96, z_in=2.0, z_out=0.25, max_hold=6` 时 **net +0.0428 bps/bar，Sharpe 1.351**。

## 3. 为什么和当前 desk 直接相关
- 它补的是 **raw alpha 素材池**（mean-reversion / basis 家族），不是再给主线加一个解释层。
- 天然兼容 `1m/3m/5m/15m`：
  - 数据本身支持这些周期（HL 文档支持 1m/3m/5m/15m candle snapshot）。
  - 入场与出场是 bar/event 都可实现的规则，不依赖黑箱模型。
- 组件可直接拆到实盘框架：
  - entry：`|premium_z| >= z_in`
  - exit：`|premium_z| <= z_out` 或 `max_hold`
  - sizing：`size ∝ dislocation` + cap
  - risk：继续背离 stop、MDD kill-switch、事件窗口停机
  - cost：双边 fee + slippage + funding 漂移

## 3.5 策略拆解（必填）
- 方向属性：perp 微观结构的均值回归（可双向）
- 基础 alpha：当 `mark` 相对 `oracle` 出现极端偏离时，押注短周期回归
- regime：高波动但流动性尚可、异常偏离可快速回补时更有效
- filter / veto：公告/清算级冲击窗口、盘口深度急降、连续 stop 连发时停机
- risk / sizing / execution overlay：
  - dislocation 越大仓位越大，但有上限
  - 超时强平避免“均值不回”拖死
  - 先 maker 后 taker，控制冲击成本

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A（策略原型）：Hyperliquid `POST /info`
  - `metaAndAssetCtxs`（`markPx/oraclePx/premium/funding/openInterest`）
  - `candleSnapshot`（支持 `1m/3m/5m/15m`）
- 数据源 B（代理快检）：Binance Futures
  - `premiumIndexKlines`（premium 历史）
  - `klines`（价格序列）
- 公开性：均为公开可访问接口（无需私钥）
- 更新频率：可映射到 `1m/3m/5m/15m`（本轮快检用 `5m`）
- 最小可复现实验口径：
  - 标的：`BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT`
  - 长度：最近 1500 根 5m
  - 信号：premium rolling z-score（默认 `roll=96`）
  - 入场：`|z|>=2.0`；出场：`|z|<=0.5` 或 `max_hold=6`
  - 成本：约 `6 bps round-trip`（简化）

### 4.2 快检结果如何解读
**A. 默认参数（全池）**
- `ALL_EQ gross = -0.0967 bps/bar`
- `ALL_EQ net = -0.3672 bps/bar`
- 结论：这条 alpha 不是“默认就能跑”的便宜信号，成本会直接吃掉。

**B. 小网格后（局部 pocket）**
- `SOLUSDT` 在更严格回归阈值下出现正 net：
  - `roll=96,z_in=2.0,z_out=0.25,max_hold=6` → `net +0.0428 bps/bar, Sharpe 1.351`
  - `roll=144,z_in=2.5,z_out=0.25,max_hold=3` → `net +0.0331 bps/bar, Sharpe 1.4714`
- 结论：它更像 **“结构化局部 alpha”**，必须做参数+标的治理，不能全池一把梭。

## 5. 下一步怎么测（直接可执行）
1. **先做跨 venue 复核（必须）**：同口径在 Hyperliquid 原生数据重跑，并与 Binance proxy 对比方向一致性。  
2. **按周期分层**：固定 `z_out=0.25`，分别在 `1m/3m/5m/15m` 扫 `roll,z_in,max_hold`，找“成本后仍为正”的稳定平台，不追单点最优。  
3. **做资金费/拥挤惩罚**：把 `funding` 与 `OI jump` 加入 veto，验证能否减少“极端背离继续扩张”亏损段。  
4. **执行层验证**：增加 maker 占比约束与 participation cap，输出“信号 edge → 可成交 edge”的衰减曲线。  
5. **上 production 前门槛**：要求 OOS `net>0`、`Sharpe>0.8`、且在 `cost+50%` 压力测试仍不翻负。

## 6. 风险与保留意见
- 仓库结果是作者样本与假设下的表现，不能直接外推；本轮用 Binance 做的是代理快检，不是 HL 全量重建。  
- 该策略在“极端行情持续单边扩张”阶段可能连续止损，必须配合超时/停机机制。  
- 当前证据表明它不是 universal alpha，更像可治理的 pocket alpha；若不做标的与参数治理，容易成本后归零。

## 7. 来源
1. **Andrea Ambrosio. (2026). _hype-backtesting_. GitHub repository.**  
   - Repo URL: https://github.com/andreaambrosio/hype-backtesting  
   - Readable URL: https://github.com/andreaambrosio/hype-backtesting
2. **Cao, Yi; Luo, Pengfei; Cheng, Yuhan; Dong, Yizhe. (2026). _Anatomy of Cryptocurrency Perpetual Futures Returns_. SSRN Working Paper.**  
   - DOI: `10.2139/ssrn.6365329`  
   - Readable URL: https://doi.org/10.2139/ssrn.6365329
3. **Zhang, Tianyang. (2026). _Funding Rate Mechanism in Perpetual Futures_. SSRN Working Paper.**  
   - DOI: `10.2139/ssrn.6185958`  
   - Readable URL: https://doi.org/10.2139/ssrn.6185958
4. **Hyperliquid Docs. _Info endpoint_.**  
   - Readable URL: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
5. **Binance Futures API Docs. _Premium Index Kline Data / Kline Data_.**  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Premium-Index-Kline-Data  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 8. 本地复现产物
- `reports/artifacts/quant_digests/premium_gap_reversion_20260323/summary.csv`
- `reports/artifacts/quant_digests/premium_gap_reversion_20260323/grid.csv`
- `reports/artifacts/quant_digests/premium_gap_reversion_20260323/meta.json`
- `reports/artifacts/quant_digests/premium_gap_reversion_20260323/trades.csv`
