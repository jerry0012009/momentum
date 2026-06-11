# 别把 ETF price discovery 只当机制文献：这篇 2025 论文更该先测的是「IBIT/FBTC/GBTC 5m lead → BTC follow-through」raw alpha，但 Binance perp 映射几乎不剩边
- 时间：2026-03-25 02:41 UTC
- 类型：近 5 年论文（全文本地）+ 公共 ETF/BTC 行情最小快检
- 主题类型：raw alpha
- 基础 alpha：cross-asset / cross-venue lead-lag——US 上市 BTC ETF 篮子在 5m 上先动，随后 BTC 现货/期货在下一个 `5m~15m` 窗口同向跟随
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-asset/lead-lag/price-discovery/etf/btc/spot/perpetual/us-session/intraday/5m/15m/cost/paper/external-data
- 证据类型：论文证据 + 公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这不是 ETF filter，本体就是“ETF tape 先动，BTC 后跟”的跨市场 lead-lag raw alpha。**

主材料是 **Azhar Mohamad (2025), _Do Bitcoin ETFs Lead Price Discovery Following their Introduction in the Bitcoin Market?_**。论文 headline 是“price discovery 在哪边”，但对我们 desk 更值钱的旁支读法不是继续把它当机制论文，而是直接问：

> **如果 `IBIT / FBTC / GBTC` 这类最活跃 ETF 的 5m return 先动，能不能在下一个 `5m / 15m` 窗口里交易 BTC？**

这就把论文从“解释谁先反应”翻成了一个可执行的短周期 raw alpha 候选。

## 2. 核心结论
- **一句话结论：** 这条线在“ETF → BTC spot”上还看得到可测毛边，但一映射到 `Binance BTCUSDT perp`，边几乎被吃光；所以它更像**受 venue 约束的 cross-market raw alpha**，不是可以直接搬进我们 crypto perp desk 的通用主策略。
- 论文用 `2024-01-11 ~ 2024-10-11` 的 **5m** 数据（bitcoin spot + 9 只 ETF）做 `IS / CS / ILS`，结论是：**IBIT / GBTC / FBTC 的 MA20 ILS 在约 85% 的时间里高于 0.5**，说明最活跃 ETF 多数时候比 bitcoin spot 更快反映信息。
- 我用公共可得的 `Yahoo Finance 5m` 数据，对 `IBIT / FBTC / GBTC` 做了一个美元成交额近似加权 basket，再看它对 `BTC-USD` 下一个窗口的带动：
  - 在 `2026-01-26 ~ 2026-03-24` 的重叠样本里，**ETF basket 5m return 与 BTC-USD 下一根 5m return 的相关约 `0.119`**；
  - 当 ETF basket 出现 **`+1σ` 正冲击** 时，BTC-USD 下一根 **平均约 `+15.8 bps`**，**同向率约 `65.7%`**；
  - 当 ETF basket 出现 **`-1σ` 负冲击** 时，BTC-USD 下一根 **平均约 `-13.1 bps`**，**同向率约 `62.1%`**；
  - 放到下一段 `15m`（3 bars）后，边已经开始衰减到 **约 `+9.9 / -8.2 bps`**。
- 但把同一信号直接映射到 **Binance Futures `BTCUSDT perp`** 时，结论明显变差：
  - 同期 ETF basket 对 **perp 下一根 5m** 的相关只剩 **约 `0.012`**；
  - `+1σ` 正冲击后，perp 下一根平均只剩 **约 `+0.7 bps`**；
  - `-1σ` 负冲击后，perp 下一根平均约 **`-3.5 bps`**，且同向率都不到 50%。
- 翻成人话：**这条 alpha 更像“ETF cash-session 先反应、部分 spot 跟上”的跨 venue pocket，而不是“ETF 一动，Binance perp 就会乖乖跟”的通用 desk alpha。**

## 3. 为什么和当前项目有关
- 它补的是我们当前明确要持续扩充的 **raw alpha 素材池**，而且是和近期 `pairs / basis / cross-sectional / mean reversion` 不同的一类：**regulated-market → crypto venue 的跨市场 lead-lag**。
- 它也给了一个很重要的 desk 边界判断：
  - **raw alpha 本体**：ETF 先动，BTC 后跟；
  - **不是** shared gate，也不是“ETF close 附近加一个确认就算完”；
  - **真正关键的问题**不是有没有相关性，而是：`它到底落在哪个 venue / 哪个可交易腿上`。
- 这比继续泛化写“ETF 有信息”更有用，因为它直接回答：
  1. 这是不是独立 raw alpha？**是。**
  2. 能不能快速做最小实验？**能。**
  3. 能不能直接迁移到我们最关心的 `1m/3m/5m/15m` crypto perp？**目前看很难。**

## 3.5 策略拆解（必填）
- 方向属性：跨资产 / 跨 venue / 单标的 BTC lead-lag，可做多空双向
- 基础 alpha：
  - `basket_ret_5m = Σ(w_i * ret_i)`，其中 `i ∈ {IBIT, FBTC, GBTC}`
  - `w_i` 第一轮可先用等权，或用 `close * volume` 做美元成交额近似权重
  - `signal_z = zscore(basket_ret_5m, rolling_window)`
- entry：
  - 若 `signal_z >= z_enter`，则下一根 BTC bar 同向做多
  - 若 `signal_z <= -z_enter`，则下一根 BTC bar 同向做空
  - 第一轮优先测 `z_enter ∈ {1.0, 1.5}`
- exit：
  - 固定持有 `1 bar (5m)` 或 `3 bars (15m)`
  - 或加 `opposite ETF shock` 提前出场作为对照臂
- sizing：
  - 先做 fixed-notional；第二轮再做 `size ∝ min(|signal_z|, z_cap)`
- risk：
  - 只在 ETF 正常交易窗口内交易
  - 事件冲击过大时（如单根 ETF basket > `2.5σ`）单独分 bucket，避免把 jump pocket 和常规 bar 混在一起
- cost：
  - spot 代理第一轮先看低成本假设；
  - perp 迁移必须单独看 `4 / 8 / 12 bps` round-trip，而不能拿 spot 结果替代。

## 4. 可复刻的最小实验
### 研究假设
如果 ETF 真在 price discovery 上领先，那么最小可交易读法就不是“谁更快”这句机制话，而是：

- **H1：** 最活跃 BTC ETF basket 的 5m return，对 BTC 现货下一根 `5m` return 有同向预测力；
- **H2：** 这种预测力在 `15m` 会衰减；
- **H3：** 把它直接搬到 `Binance BTCUSDT perp` 后，alpha 大概率明显变弱，说明 edge 更像 venue-specific。

### 数据源、公开性、更新频率、最小可复现实验口径
- ETF 数据：`Yahoo Finance Chart API`（公开可得，但有抓取频率限制）
  - 标的：`IBIT / FBTC / GBTC`
  - 更新频率：分钟级，最小实验可用 `5m`
- BTC 现货代理：`Yahoo Finance BTC-USD 5m`
  - 公开可得，适合先验证“ETF → BTC spot”这条 paper-side lead-lag
- BTC perp 迁移：`Binance USDⓈ-M Futures Kline API`
  - 公开可得，分钟级实时
  - 用于回答 desk 最关心的“能不能直接迁到 perp”

### 这次本地最小快检结果
- ETF basket → `BTC-USD spot`：
  - next `5m` corr ≈ **`0.119`**
  - `+1σ` shock 后 next `5m` ≈ **`+15.8 bps`**
  - `-1σ` shock 后 next `5m` ≈ **`-13.1 bps`**
- ETF basket → `BTCUSDT perp`：
  - next `5m` corr ≈ **`0.012`**
  - `+1σ` shock 后 next `5m` ≈ **`+0.7 bps`**
  - `-1σ` shock 后 next `5m` ≈ **`-3.5 bps`**

### 下一步怎么测
1. **先做 venue A/B，不要一上来就只看 perp。**
   - `BTC-USD spot` vs `Coinbase BTC spot` vs `Binance BTC perp` 三腿并排，直接回答 edge 到底死在哪一层。
2. **把 ETF basket 从单根 return，改成“冲击质量分层”。**
   - 分成 `0.5~1σ / 1~1.5σ / >1.5σ`，看是不是只有中高冲击才有可交易边。
3. **做 clock-aware 版本，而不是全天混算。**
   - 把 `open first hour / mid-session / close last hour` 分开，检验 edge 是否只在特定 cash-session pocket 成立。
4. **若仍想服务 desk，就优先测“跟 BTC 现货，不跟 perp”的代理腿。**
   - 例如 Coinbase/Bitstamp/BTC spot proxy，再决定是否值得做更复杂的 cross-venue routing；
   - 如果 perp 端继续几乎没边，就应把它降级成“研究边界已确认”，而不是继续硬磨成主策略。

## 5. 风险与保留意见
- 论文里的 ETF 数据来自 **Refinitiv**，而我的最小实验用的是 **Yahoo Finance 公共 5m bars**；方向上能做 first-pass 验证，但不是论文原始数据的逐点复刻。
- 论文本身是 **price discovery / VECM** 研究，不是交易回测论文；这里是按用户允许的“把更适合 desk 的旁支想法单独拎出来”来做 raw alpha 读法。
- 目前最关键的 honesty point 已经很清楚：**spot 侧还能看到一点 lead-lag，perp 侧几乎没有。**
- 所以这条线暂时不该被包装成“可直接上 Binance perp 的高优先级主 alpha”；更诚实的定位是：
  - `cross-market raw alpha candidate`
  - `venue-specific pocket`
  - `值得做一次 venue boundary decisive test`，但不是默认继续重投入的 front-row 题。

## 6. 来源
1. **Mohamad, A. (2025). _Do Bitcoin ETFs Lead Price Discovery Following their Introduction in the Bitcoin Market?_ Computational Economics.**
   - Authors: Azhar Mohamad
   - Year: 2025
   - Venue: `Computational Economics`
   - DOI: `10.1007/s10614-025-10998-x`
   - Readable URL: `https://doi.org/10.1007/s10614-025-10998-x`
   - Repo URL: `N/A（未见官方复现仓库）`

2. **Yahoo Finance Chart API（公开可得 ETF / BTC 分钟行情）**
   - Data source: Yahoo Finance
   - Publicness: 公开可得（有频率限制）
   - Update frequency: 分钟级
   - Readable URL: `https://finance.yahoo.com/`

3. **Binance USDⓈ-M Futures Kline API（desk 迁移实验）**
   - Data source: Binance Developers
   - Publicness: 公开可得
   - Update frequency: 分钟级
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

4. **本地最小快检 artifact（2026-03-25）**
   - `reports/artifacts/quant_digests/etf_btc_price_discovery_probe_20260325/summary.csv`
   - `reports/artifacts/quant_digests/etf_btc_price_discovery_probe_20260325/spot_events_absz15.csv`
   - `reports/artifacts/quant_digests/etf_btc_price_discovery_probe_20260325/perp_events_absz15.csv`
