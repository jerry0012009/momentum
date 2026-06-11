# 别把这篇 2024 IREF 论文只读成“crypto 也有日内周期”：对 short-cycle desk，更该先测的是「NYSE open 正向 market pulse × beta-spread continuation」这条 raw alpha
- 时间：2026-04-12 09:24 UTC
- 类型：2024 论文摘要/元数据 + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**当 NYSE 开盘后第一个 `15m` 市场脉冲足够强时，高 beta token 往往会在接下来 `90~120m` 继续跑赢低 beta major；更像可交易的不是单腿追涨，而是做 `high-beta long / low-beta short` 的相对价值 spread。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-sectional / relative-value / beta-spread / session-pocket / NYSE-open / intraday-periodicity / BTC / BNB / LINK / DOGE / SOL / Binance-perpetual / 15m / 90m / 120m
- 证据类型：论文摘要/元数据 + Binance USDⓈ-M public-data probe

## 1. 这次看了什么
这次看的是 **Joann Jasiak, Cheng Zhong (2024), _Intraday and daily dynamics of cryptocurrency_, International Review of Economics & Finance, DOI `10.1016/j.iref.2024.103658`**。

这篇 paper 表面上更像“crypto 日内周期 / functional CAPM”的市场结构文，不像现成策略论文；但它有一句对 desk 很有用的话：
> **native cryptocurrencies 与 tokens 的 intraday 周期，很大程度受 `NYSE / LSE / Hang Seng` 这些股票市场交易时段驱动，而且 BTC / ETH / LINK 对市场组合的 beta 本身也带有日内周期。**

把它翻成人话，就是：
- 某些固定外部时钟，不只是“活跃一点”；
- 它们还会改变 **哪类币更像高 beta 风险承载器**；
- 所以真正值得先测的，不只是“session 有 seasonality”，而是 **session open 的第一脚市场冲击，会不会把 high-beta token / low-beta major 的 spread 一起拉开。**

## 2. 核心结论
- **一句话核心结论：** 这篇 paper 最适合当前 desk intake 的，不是泛泛的“crypto 也有日内周期”，而是更具体的 **`NYSE open first-15m positive pulse -> next 2h beta-spread continuation`**。
- **一句话证明方式：** 先用 paper abstract 里的“equity-market hours 驱动 intraday periodicity + periodic beta”做机制地基，再用 Binance USDⓈ-M `15m` 公共数据对 `BTC/ETH/BNB/XRP/DOGE/LINK/SOL` 做最小 public-only probe。
- 我先把 paper 里的直觉压成一个更 desk 化的规则：
  1. 在 `NYSE open`（美东 `09:30`）对应的第一根 `15m` bar 上，计算 7 币等权市场组合回报；
  2. 用过去约 `20` 天 `15m` 数据估 rolling beta，找出当下 **最高 beta** 与 **最低 beta** 的两端；
  3. 若第一根 open-bar 的 market pulse 为正且足够大，就做 **long top-beta / short low-beta**；
  4. 持有 `60m / 90m / 120m` 对比。
- 本轮先做 session 对照后发现：
  - `Hang Seng open` 这条线整体偏负；
  - `LSE open` 有一点 edge，但强度不够稳；
  - **真正过成本线的是 `NYSE open` 的正向大脉冲。**
- 具体到 `NYSE open` 的正向 pulse：
  - 若 open 后首根 `15m` 市场等权回报 **≥ `+50 bps`**，则未来
    - `60m`：`28` 次事件，约 **`+25.48 bps/次`** gross，胜率 **`60.7%`**；
    - `90m`：`28` 次事件，约 **`+27.54 bps/次`** gross，胜率 **`60.7%`**；
    - `120m`：`28` 次事件，约 **`+31.34 bps/次`** gross，胜率 **`60.7%`**。
- 若把两腿 round-trip 总成本粗扣为 `8 / 12 / 16 / 20 / 24 bps`，`120m` 这版仍约为：
  - **`+23.34 / +19.34 / +15.34 / +11.34 / +7.34 bps/次`**；
  - 说明它至少在 **中等强度 taker 成本** 下，已经有 first-verdict 级别的可交易雏形。
- 这条线不是“所有 beta-spread 都行”。`NYSE open` 的 **负向 pulse** 在同口径下明显弱很多；当前更像一条 **risk-on upward impulse** 下的正向 spread continuation，而不是完全对称的双边书。

## 3. 为什么和当前项目有关
这条线值得进池，主要因为它补的是 **当前素材池里较少的“session-clock × factor-spread” raw alpha**：
1. **它不是 filter。** 方向、进场、持有窗、成本都能单独定义；
2. **它直接映射到 `15m -> 90m/120m`。** 不需要慢频外部数据硬装成逐根 alpha；
3. **它把论文里的“periodic beta”翻成可下单的 spread book。** 不是再重复 funding / liquidation / generic breakout；
4. **它天然是 relative-value / market-neutral-ish 壳。** 对当前 desk 来说，比单腿追高更容易压掉部分大盘噪音。

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / relative-value / beta-spread / session-pocket continuation
- 基础 alpha：`NYSE open` 后若 market pulse 足够强，高 beta token 对低 beta major 的 spread 往往继续扩张 `90~120m`
- regime：美股现金开盘对应的 risk-on 脉冲；当前以 **正向大脉冲** 最像有效 pocket
- filter / veto：仅做 `NYSE open`；仅做首根 `15m` market pulse `>= +50 bps`；先不做负向 pulse
- risk / sizing / execution overlay：双腿等 notional；`60/90/120m` 时间退出；总成本先按 `8~24 bps` 梯度；若 open 后第二根 bar 直接反向吞没第一根，可加入早停

## 4. 可复刻的最小实验
### 研究假设
美股现金开盘会把 crypto 的 risk-taking 偏好短时抬高；当首根 `15m` 市场组合已经明显走强时，**高 beta token** 会在接下来 `1.5~2h` 继续相对跑赢 **低 beta major**。

### 一个可计算定义
1. 资产池：`BTCUSDT / ETHUSDT / BNBUSDT / XRPUSDT / DOGEUSDT / LINKUSDT / SOLUSDT`
2. 周期：`15m`
3. 在每个 `NYSE open` bar（美东 `09:30`）上，计算 7 币等权 `market_pulse`
4. 用前 `20` 天 `15m` 收益对等权 market 做 rolling beta
5. 若 `market_pulse >= +50 bps`：
   - `long = 当下最高 beta 资产`
   - `short = 当下最低 beta 资产`
6. 持有 `120m` 后平仓；成本先测总 round-trip `8 / 12 / 16 / 20 / 24 bps`

### 本轮建议先测哪版
先测最简单也最像当前 evidence 的版本：
- `session`: `NYSE open`
- `signal`: first `15m` equal-weight market pulse `>= +50 bps`
- `book`: long top-beta / short low-beta
- `exit`: `120m`
- `sizing`: 双腿等 notional，单日最多一笔

## 5. 风险与保留意见
- 这篇 paper 本轮只拿到了 **OpenAlex abstract + Crossref metadata**，没成功拿到全文页面；所以学术证据这边要按 **abstract-grounded** 而不是 full-text confirmed 来看。
- 当前样本仅约 `2025-10-01 ~ 2026-04-12`，事件数不算大；`>= +50 bps` 的 `NYSE open` 正向脉冲只有 `28` 次。
- 这条线明显依赖 **threshold**；不设阈值时，`NYSE open` 的平均 beta-spread 并不漂亮。
- 当前 top-beta / low-beta 在样本里常落到 `DOGE / LINK / SOL` 对 `BTC / BNB`，说明它有一定资产集中度；后续要防止 edge 其实只来自少数几组组合。
- 这是两腿策略，总成本不应偷算成单腿；如果要上更激进频率，必须把挂单成交率与滑点单独拆出来。

## 6. 最值得复用的点
最值得复用的不是 paper 的 functional CAPM 形式本身，而是它提示了一个很好用的研究模板：
**外部交易时钟 → market pulse → factor spread 响应。**
这套模板后面不只可以测 beta，也能拿去测：
- size / liquidity spread
- alt / major spread
- funding-sensitive sleeve / non-funding-sensitive sleeve

## 7. 一句话结论
> 这篇 2024 IREF 论文真正适合当前 short-cycle desk 先 intake 的，不是“crypto 也有日内周期”这句大话，而是里面更可交易的旁支：**NYSE 开盘第一脚若把市场组合直接拉到 `+50 bps` 以上，高 beta token 对低 beta major 的 spread 往往还会继续走 `1.5~2h`。** 本轮 public probe 下，`120m` 版本约 `28` 次、`+31.34 bps/次` gross，按双腿总 round-trip `16 bps` 粗扣后仍约 `+15.34 bps/次`。

## 8. 本轮产物
- 研究笔记：`research/quant_digests/2026-04-12_0924_nyse-open-betaspread-continuation-alpha.md`
- Session summary：`reports/artifacts/literature/nyse_open_beta_spread_probe_2026-04-12_session_summary.csv`
- Event detail：`reports/artifacts/literature/nyse_open_beta_spread_probe_2026-04-12_detail.csv`
- Threshold sweep：`reports/artifacts/literature/nyse_open_beta_spread_probe_2026-04-12_threshold_summary.csv`
- Pair breakdown：`reports/artifacts/literature/nyse_open_beta_spread_probe_2026-04-12_pair_breakdown.csv`
- Cost ladder：`reports/artifacts/literature/nyse_open_beta_spread_probe_2026-04-12_costladder.csv`

## 9. 来源
1. **Jasiak, J., & Zhong, C. (2024). _Intraday and daily dynamics of cryptocurrency_. International Review of Economics & Finance, 96, 103658.**
   - DOI: `https://doi.org/10.1016/j.iref.2024.103658`
   - Readable URL: `https://doi.org/10.1016/j.iref.2024.103658`
   - OpenAlex work: `https://openalex.org/W4402908168`
   - Note: 本轮主要使用 OpenAlex abstract / metadata 与 Crossref metadata，未拿到稳定全文页
2. **Binance USDⓈ-M Futures Public API**（本轮 portability probe 实际使用）
   - Kline / Candlestick Data: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
3. **本地 public probe artifacts**
   - `reports/artifacts/literature/nyse_open_beta_spread_probe_2026-04-12_session_summary.csv`
   - `reports/artifacts/literature/nyse_open_beta_spread_probe_2026-04-12_threshold_summary.csv`
   - `reports/artifacts/literature/nyse_open_beta_spread_probe_2026-04-12_costladder.csv`
