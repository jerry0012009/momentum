# 别把 2022 crypto trading network 论文只读成复杂网络图：对 desk 更该先测的是「leader-basket → selected-follower spread catch-up」raw alpha
- 时间：2026-03-30 08:08 UTC
- 类型：2022 *Scientific Reports* 开放获取全文 HTML + Binance Spot 公共 `15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**由 `BTC/ETH/LTC` 这类高影响 leader basket 先动、而 selected follower 当根明显落后时，下一根更值得做的是「long follower / short leader basket」的相对回补，不是无差别追整个 alt basket**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-crypto/lead-lag/network/granger-causality/relative-value/spread-convergence/leader-basket/follower-routing/stablecoin-synergy-gate/15m/5m/paper/public-data/cost
- 证据类型：论文全文证据 + 本地公共数据快检

> 先回答 base alpha：**这次不是单纯讲 network / regime。真正可交易的 base alpha 是 cross-crypto relative-value：leader 先动、follower 滞后，下一根做 spread catch-up。** 论文里的高阶依赖和 stablecoin synergy，更像是这条 raw alpha 的配套 gate，不是 alpha 本体。

## 1. 这次看了什么
主看 **Scagliarini, Pappalardo, Biondo, Pluchino, Rapisarda, Stramaglia (2022), _Pairwise and high-order dependencies in the cryptocurrency trading network_, Scientific Reports**。

这篇 paper 表面是在做复杂网络和高阶信息流，但对当前 desk 更值钱的读法，不是再写一篇“市场很复杂”的综述，而是直接拆成两层：

1. **pairwise Granger network = leader/follower 选边器**；
2. **high-order stablecoin synergy = 只在需要时才上的 regime/gate**。

翻成人话：先别把全市场 alt basket 一把抓。更诚实的做法，是先用论文告诉我们的 **influencer → follower routing** 去挑对象，再决定哪几个 spread 值得做 catch-up。

## 2. 核心结论
- **论文给了一个很清楚的 network 地基。** 作者用 Kraken 数据，把成交逐笔数据聚合到 **分钟级**，看 **2020-01 ~ 2021-12 共 104 个周窗口**、**99 条加密货币收益序列** 的信息流；pairwise Granger 链接用 **1% 显著性阈值** 保留。文中点名的 top influencers 主要是 **Bitcoin / Ethereum / Litecoin**，而更受影响的一侧偏向较年轻、较小的币。
- **这个网络不是天天重做、天天换边。** 论文写得很直白：相邻周的 pairwise network 相似度通常 **高于 0.9**；也就是说，leader/follower 结构在平稳阶段并不乱飘，这很适合 desk 先把它当作一个“慢更新的选边器”，而不是每根 bar 重新选宇宙。
- **高阶部分告诉我们：别把 stablecoin 只看成边缘资产。** 在 pairwise 里 stablecoin 角色不强，但在 synergy multiplets 里反而更常出现。作者还把样本分成三段：**2020 年高冗余/低协同，2021 上半年冗余下行而协同上升，2021 下半年进入较高但更稳定的平台。** 这更像一个 regime 提示：当 stablecoin / 高阶联动开始抬头时，pairwise routing 可能还在，但 basket 化做法未必还适合无脑放大。

### 3 个最有用的数据点
1. **论文样本口径：** `99` 条收益序列、`104` 个周窗口、分钟聚合后的收益序列。  
2. **论文结构结论：** pairwise network 的相邻窗口相关性经常 **> 0.9**，说明 leader/follower 关系有稳定性。  
3. **本地 `15m` 快检：** 用 `BTC/ETH/LTC` 做 leader basket，在 Binance Spot 最近 `999` 根 `15m` bar（`2026-03-19 22:30 UTC ~ 2026-03-30 08:00 UTC`）上测试：
   - **equal-weight follower basket 整体几乎没边：`-0.04 bps/trade`，`n=200`**
   - 但 **pair-specific pocket** 明显存在：
     - `LINKUSDT`：**`+7.92 bps/trade`，hit `74.5%`，t≈`7.45`**
     - `ADAUSDT`：**`+3.00 bps/trade`，hit `58.5%`，t≈`2.14`**
     - `XRPUSDT`：**`+1.73 bps/trade`，hit `54.5%`**

## 3. 为什么和当前项目有关
这条线值钱，不是因为我们又多看了一篇 lead-lag 论文，而是因为它**修正了一个很常见的坏习惯**：

> 看到大币先动，就顺手追一个“alt basket catch-up”。

论文 + 本地快检一起给出的更诚实版本是：

- **别做“全篮子会跟”的想象；**
- 先承认 **leader/follower 是网络路由问题，不是 universe 平权问题**；
- 然后把 raw alpha 写成：**只做那几个被选出来的 follower spread。**

这直接补的是 desk 的 **cross-crypto relative-value / lead-lag raw alpha 素材池**，而且还顺手给了一个以后能扩展到 `5m / 3m / 1m` 的 pair-selection primitive。

## 3.5 策略拆解（必填）
- 方向属性：**相对价值 / lead-lag / spread convergence**
- 基础 alpha：**leader basket 当根先动、selected follower 明显掉队时，下一根做 follower 对 leader 的回补**
- regime：**优先在 pairwise network 较稳定、stablecoin-stress 不极端的时段启用；stablecoin synergy 抬升时，更适合降杠杆或减小 basket 化暴露**
- filter / veto：
  - 只保留最近 rolling edge 仍为正的 follower（例如当前快检中的 `LINK / ADA / XRP`）
  - 仅在 `|leader_ret - follower_ret|` 进入本币 `q80+` 时触发
  - 避开宏观事件条、stablecoin depeg、极端 funding/OI 冲击条
- risk / sizing / execution overlay：
  - 做 **beta / dollar-neutral** 的 `long follower / short leader basket`
  - 先从 `15m` 再平衡开始，不要一上来卷 `1m` 高频
  - 真实落地应先测 perp 版，并扣掉 taker/slippage/funding

## 4. 可复刻的最小实验
### 最小定义
- `leader_t = mean(ret_t(BTC), ret_t(ETH), ret_t(LTC))`
- 对每个 follower `j`：`spread_{j,t} = leader_t - ret_{j,t}`
- 当 `|spread_{j,t}|` 进入过去样本的 **top 20%**：
  - 若 `spread > 0`：`long follower_j / short leader basket`
  - 若 `spread < 0`：`short follower_j / long leader basket`
- 持有 **下一根 `15m`**，按 follower 逐个评估，不做无脑 basket 汇总

### 本轮已做的最小快检
- 数据源：**Binance Spot 公共 `15m` klines**
- leaders：`BTCUSDT / ETHUSDT / LTCUSDT`
- followers：`TRXUSDT / XRPUSDT / ETCUSDT / ADAUSDT / DOGEUSDT / LINKUSDT`
- honest 结论：
  - **basket 不行，不要硬上**
  - **routing map 有 pocket**，当前最像样的是 `LINK / ADA / XRP`

## 5. 风险与保留意见
- 论文本身不是交易回测论文，而是 **network / information-flow 描述论文**；我们这里拿走的是其中最适合 desk 的那条 raw-alpha 分支。  
- 本地快检样本只有最近 `999` 根 `15m` bar，属于**很轻的 pocket scan**，不是正式 walk-forward。  
- 目前结果还是 **gross spread**，没扣交易费、滑点、资金费。  
- follower routing 很可能会漂移，不能把 `LINK/ADA/XRP` 当永久真理；它更像一个 **rolling routing map**。  

## 6. 下一步怎么测
1. **把 follower routing 改成 rolling walk-forward。** 每 `7/14/30` 天重估一次 `leader → follower` pocket，避免把旧网络关系硬搬到新市场。  
2. **从 Spot 快检迁到 Perp 可执行口径。** 直接在 Binance USDⓈ-M 上做 `15m` 和 `5m`，并扣 `fee + slippage + funding`。  
3. **单独给 stablecoin-stress 做 veto。** 当 `USDT/USDC` 偏离、funding dispersion、OI shock 同时抬升时，比较开/不开这个 gate 的差异。  
4. **只保留“pair-specific 正 pocket”，不要再回退到 equal-weight alt basket。** 这是这篇 paper 对 desk 最有价值的一点。  

## 7. 来源
1. **Scagliarini, T., Pappalardo, G., Biondo, A. E., Pluchino, A., Rapisarda, A., & Stramaglia, S. (2022). _Pairwise and high-order dependencies in the cryptocurrency trading network_. Scientific Reports.**  
   - DOI: `10.1038/s41598-022-21192-6`  
   - Readable URL: <https://www.nature.com/articles/s41598-022-21192-6>  
   - DOI URL: <https://doi.org/10.1038/s41598-022-21192-6>  
   - Repo URL: `N/A`
2. **Crossref metadata for the same paper**  
   - Readable URL: <https://api.crossref.org/works/10.1038/s41598-022-21192-6>
3. **Binance Spot API docs – Kline/Candlestick Data**  
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>
4. **Kraken historical trade data**（论文数据来源说明）  
   - Readable URL: <https://support.kraken.com/articles/360047124832-downloadable-historical-ohlcvt-open-high-low-close-volume-trades-data>

## 8. 本地产物
- `reports/artifacts/quant_digests/network_leader_follower_spread_20260330_0808/summary.json`
- `reports/artifacts/quant_digests/network_leader_follower_spread_20260330_0808/linkusdt_events.csv`
- `reports/artifacts/quant_digests/network_leader_follower_spread_20260330_0808/adausdt_events.csv`
- `reports/artifacts/quant_digests/network_leader_follower_spread_20260330_0808/xrpusdt_events.csv`
