# Basis dislocation percentile as a breakout-short disable filter

- **Date:** 2026-03-20 05:11 UTC
- **Mainline:** V3 final-verdict / breakout-short follow-up
- **Role:** regime gate / veto（不是逐根 15m 主信号）

## Why this topic, why now

这轮继续服务 V3 收口：我们已经测过 `funding`、`OI`、`compression`、`break severity`，但还缺一块常见且公开可得的衍生品上下文——**perp basis（mark-index 偏离）**。

这比再做一篇泛化 S/R 更值得：它直接回答 V3 的关键问题——哪些下破不该追空。尤其在已经“贴地”负基差的阶段，继续追空常见的是拥挤与回补风险，而不是干净延续。

## Source summary

### Paper（机制锚点）

- **Authors:** Kachnowski
- **Year:** 2022
- **Title:** *Futures As Prelude: Bitcoin Price Forecasting From Perpetual Futures Data*
- **Venue:** SSRN Electronic Journal
- **DOI:** `10.2139/ssrn.4097789`
- **Readable URL:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4097789
- **DOI URL:** https://doi.org/10.2139/ssrn.4097789
- **Repo URL:** N/A（论文）

**对我们有用的旁支结论（非 headline 抄写）**
- perp futures 侧变量对后续现货/价格路径有前瞻信息；
- desk 可落地的读法不是“用 basis 直接做入场信号”，而是：把它作为 **breakout-short 的拥挤/透支过滤层**。

### Repo + public data plumbing（快速复现锚点）

1. **binance/binance-connector-python**（官方 Python 连接器）  
   - URL: https://github.com/binance/binance-connector-python  
   - 用途：快速拉取衍生品公开接口，减少自写签名/重试/限速样板。

2. **Binance USDⓈ-M Futures public endpoints**（公开、可直接拉）
   - Mark Price: `GET /fapi/v1/premiumIndex`  
     文档: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price
   - Open Interest: `GET /fapi/v1/openInterest`  
     文档: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest
   - Funding Rate History: `GET /fapi/v1/fundingRate`  
     文档: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History
   - Premium Index Kline: premium 指数 K 线（可对齐 5m/15m）  
     文档: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Premium-Index-Kline-Data

## Desk interpretation

这不是“新 alpha 主引擎”，而是 V3 的 **no-short gate**：

- `basis_t = (markPrice - indexPrice) / indexPrice`
- 重点不是 basis 的绝对值，而是其**滚动分位/极端程度**。

直觉：
- 当下破发生在 `basis` 已处于极端负分位（例如过去 30 天 P10 以下）时，继续追空更容易遇到透支 + 反抽；
- 当 `basis` 仍中性、且 OI/波动结构支持时，下破延续概率更高。

## Minimal test design (15m-first)

### Hypothesis

在 15m BTC/ETH/SOL 的 breakout-short 事件中：

- **极端负基差**（`basis_pct_30d <= 10%`）且
- **OI 未扩张或转负**（`oi_delta_1h <= 0`）

对应的后续 4/8/12 bar 延续率显著更差；将其设为 veto 可降低 false-break short。

### Data source / openness / update frequency

- **数据源：** Binance Futures 公开 REST（无需私钥即可读取市场数据）。
- **公开性：** 公网可访问；接口文档公开。
- **更新频率（实务口径）：**
  - `premiumIndex`/`openInterest`：近实时快照（返回 `time` 时间戳）；
  - `fundingRate`：按资金费率结算节奏更新（通常 8h 档位）；
  - `premium index kline`：可直接取 5m/15m K 线粒度对齐实验。

### Minimal reproducible experiment（最小复现实验口径）

1. 复用当前 V3 breakout-short 触发事件集（不改入场定义）。
2. 对每个事件，取触发前最近可得：
   - `basis_pct_30d`（滚动 30d 分位）
   - `basis_z_7d`
   - `oi_delta_1h`, `oi_delta_4h`
   - `funding_sign_persist`（过去 N 次 funding 同号持续）
3. 仅加一条 veto 规则首测：
   - `if basis_pct_30d <= 10% and oi_delta_1h <= 0: skip short`
4. 评估：
   - continuation@4/8/12 bars
   - false-break ratio
   - MAE/MFE
   - 交易频率保留率（避免“过滤太猛”）

## Risks / failure modes

- 极端负基差在某些崩跌段可能反而是“趋势确认”而非透支；需做 regime 分层。
- funding 低频，不能伪装成逐根 15m 主信号；只应做 gate/overlay。
- 不同币种基差分布不同，分位阈值要按 symbol 标准化。

## Next action

先做 **1 日可交付** 的 event-study：

- 固定现有 V3 触发；
- 增加 `basis_pct_30d + oi_delta_1h` 二维分桶；
- 先在 BTC/ETH/SOL 15m 跑 90~180 天滚动窗口；
- 若 `false-break` 降幅明显且频率留存 > 60%，再考虑纳入正式 `no-short` gate。