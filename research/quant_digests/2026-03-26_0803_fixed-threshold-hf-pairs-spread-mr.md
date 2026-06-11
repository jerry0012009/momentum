# 别把高频 pairs 又写成“必须动态阈值”：这篇 2025 论文更该先测的是「fixed-threshold 的 15m/5m spread MR」
- 时间：2026-03-26 08:03 UTC
- 类型：2025 China Finance Review International 论文（摘要级证据）+ Binance Futures 公共 `15m/5m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：高相关 coin pair 的 spread / relative-value 均值回归；先选 pair，再用固定 entry band 触发、均值回归或 timeout 出场
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/high-frequency/fixed-threshold/distance-method/cointegration/hybrid/binance/perpetual/15m/5m/paper
- 证据类型：论文摘要证据 + Binance Futures 公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 很清楚，就是 high-frequency crypto pairs 的 spread mean reversion。**

这轮值得 intake 的，不是“pairs 也能赚钱”这种老结论，而是论文给了一个对 short-cycle desk 很实用的判断：**在 `15m/5m` 这种高频层，先别默认 dynamic threshold 一定更高级；fixed threshold 反而可能更能活。**

这和我们当前素材池直接相关，因为 desk 现在已经积累了不少 `cointegration / Hurst / OBI veto / basket construction`，但**“固定阈值 vs 动态阈值”在高频 pairs 上到底谁更诚实**，反而还没单独冻结成一篇可复现实验卡。

## 2. 论文核心结论
- **一句话核心结论：** 这篇 2025 论文最值得 desk 先偷的，不是又加一个 pair-selection 指标，而是——**在 crypto 高频 pairs 里，fixed threshold 不是土办法，反而可能比 dynamic threshold 更赚钱。**
- 摘要里最硬的几条信息：
  - 样本来自 **Binance top 50 cryptocurrencies**；
  - 同时覆盖 **daily / 4h / 1h / 15m / 5m**；
  - 方法不是单一套路，而是同时比较 **distance / cointegration / hybrid** 三类 pairs 方法；
  - 还显式扫了 **fixed vs dynamic threshold**、`1.44 / 1.65 / 2σ` entry band、不同 exit threshold、不同 pair 数量；
  - 摘要明确说：**高频时间框架（尤其 `15m / 5m`）可盈利，且 fixed threshold 在收益和 Sharpe 上显著优于 dynamic threshold。**

翻成人话：**pairs 在短周期不一定输在“没动态化”，很多时候反而是把阈值搞得太会飘，结果把本来能吃到的回归段自己过滤掉了。**

## 3. 为什么和当前项目直接相关
- 这是标准 **raw alpha**，不是把 filter / overlay 假装成 alpha 本体。
- 它和当前 desk 最匹配的地方在于：
  - 交易对象是 **market-neutral relative value**，天然适合补 raw alpha 池；
  - 可直接落到 `entry / exit / timeout / pair count / cost`；
  - 频率正好卡在我们最关心的 `15m / 5m`；
  - 它不是又去卷某个特定形态，而是给 pairs/stat-arb 线补一块 **真正会改 verdict 的 execution design**。
- 相比继续在 pairs 上只加 `更复杂 selection` 或 `更多 regime gate`，这篇更值得先测，因为它先碰的是**策略骨架本体**：
  - 何时进？
  - 用固定还是动态阈值？
  - 进多少对？
  - 什么宽度才扛得住成本？

## 3.5 策略拆解（必填）
- 方向属性：pairs / relative-value / market-neutral mean reversion
- 基础 alpha：`spread_t = f(P_A, P_B)` 偏离均值后回归；最小可读法可用 distance-normalized spread 或 cointegration residual
- regime：只在高相关、关系未明显断裂的 pair 上开仓；高频下优先 separate `15m` 与 `5m` 阈值面，不默认共用一个 entry band
- filter / veto：rolling corr 崩塌、spread 波动异常膨胀、funding/fee 过高、timeout 过长仍未回归时拒绝或强平
- risk / sizing / execution overlay：pair 内等权或 beta-neutral；组合层限制同时开仓对数与共因子暴露；显式计入 4-leg 成本、滑点、funding；必须带 timeout 与 hard stop

## 4. 本地最小快检（Binance Futures 公共数据，轻量 proxy，不是论文精确复现）
我补了一个最小 desk 版本，只问一句：**fixed-threshold 的高频 spread MR，在 `15m` 和 `5m` 上到底有没有可活的 pocket？**

### 4.1 `15m` proxy
- 数据：Binance USDⓈ-M Futures 公共 `15m` K 线
- 宇宙：`BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK/LTC/BCH/AVAX/DOT/TRX/APT`
- formation：最近 **30 天**
- trade window：最近 **14 天**
- pair selection：distance method + `corr > 0.75`，贪心挑 **4 对不重叠 pair**
- 选出的 pair：
  - `BTCUSDT-BNBUSDT`
  - `LINKUSDT-LTCUSDT`
  - `ETHUSDT-SOLUSDT`
  - `ADAUSDT-DOGEUSDT`
- 交易规则：
  - 用 formation spread 的均值/标准差定固定 band；
  - entry 扫 `1.44 / 1.65 / 2.0σ`；
  - exit：`|z| <= 0.25` 或 timeout；
  - 成本代理：**12 bps pair round-trip**。

#### `15m` 结果
- `1.44σ`：**15 笔**，`net_total_bps ≈ +207.4`，`mean_pair_avg_pnl ≈ +29.0 bps`
- `1.65σ`：**12 笔**，`net_total_bps ≈ +17.1`，`mean_pair_avg_pnl ≈ +8.3 bps`
- `2.0σ`：**9 笔**，`net_total_bps ≈ -1.3`，接近被成本吃平

这组结果很直白：**在 `15m` 上，band 太宽反而不一定更好；更窄一点的 fixed threshold 才有足够的 trade density 去覆盖成本。**

### 4.2 `5m` proxy
- 数据：Binance USDⓈ-M Futures 公共 `5m` K 线
- 同一主流 perp basket
- formation：最近 **20 天**
- trade window：最近 **7 天**
- pair selection：distance method + `corr > 0.75`，挑 **4 对不重叠 pair**
- 选出的 pair：
  - `XRPUSDT-LINKUSDT`
  - `BTCUSDT-BNBUSDT`
  - `SOLUSDT-AVAXUSDT`
  - `DOGEUSDT-BCHUSDT`
- 其余口径同上，成本仍用 **12 bps pair RT**。

#### `5m` 结果
- `1.44σ`：**18 笔**，`net_total_bps ≈ +31.5`，`mean_pair_avg_pnl ≈ -0.25 bps`，几乎只是勉强活着
- `1.65σ`：**15 笔**，`net_total_bps ≈ +262.9`，`mean_pair_avg_pnl ≈ +13.7 bps`
- `2.0σ`：**13 笔**，`net_total_bps ≈ +318.6`，`mean_pair_avg_pnl ≈ +22.0 bps`，`mean_pair_win_rate ≈ 83.8%`

翻成人话：**`5m` 和 `15m` 的最优 band 方向不一样。**
- `15m` 更像要保 trade density，`1.44σ` 反而最好；
- `5m` 更像要先过滤噪音，`1.65~2.0σ` 才开始真正过成本。

### 4.3 当前 desk 可直接拿走的结论
1. **fixed threshold 确实值得先做，不需要先预设 dynamic 才高级。**  
2. **不能拿一个通用 σ 同时服务 `15m` 和 `5m`。**  
3. **高频 pair MR 的 alpha 不是“越快越窄越好”**：在 `5m` 反而更需要宽 band 才能躲掉噪音。  
4. 两个窗口的 **median hold 都贴近 24h timeout**，说明它是“`5m/15m` 触发 + 更长时间收敛”的策略，不是那种几根 bar 内就清掉的超短平仓模型。

## 5. 最小可复现实验（面向 `1m / 3m / 5m / 15m`）
如果下一轮正式推进，这条线建议这样冻结：

- **selection 频率**：先用 `1h` 或 `15m` formation 定 pair universe，不建议每根 `5m` 重选 pair
- **trade frequency**：
  - `15m` 版：固定 threshold 优先扫 `1.25 ~ 1.75σ`
  - `5m` 版：固定 threshold 优先扫 `1.65 ~ 2.25σ`
- **pair construction baseline**：
  1. distance
  2. cointegration residual
  3. hybrid（论文主线之一）
- **exit**：
  - mean reversion (`|z| < exit_band`)
  - timeout（`12h / 24h / 36h`）
  - spread break / rolling corr break
- **cost**：先跑 `8 / 12 / 16 / 20 bps pair RT` 四档
- **必须记录**：post-cost expectancy、median hold、timeout 占比、pair overlap、funding drag、不同市场状态下的 survival

## 6. 下一步怎么测（必须）
1. **先把 fixed vs dynamic 做成同口径对照实验**：这篇论文最值钱的点就在这里，不能只复现 fixed 不对照 dynamic。  
2. **分开为 `15m` 和 `5m` 建各自阈值面**：不要再默认一个 `1.5σ` 就够全 desk。  
3. **补 pair-count sweep**：论文摘要明确说 pair 数量会影响盈利；下一轮至少跑 `4 / 6 / 8` 对。  
4. **补 distance vs cointegration vs hybrid**：当前本地只做了 distance proxy，下一步必须把另两条主线补上。  
5. **把 timeout 当一级参数，不要当附属条款**：这轮本地快检里持有时长贴近上限，说明 timeout 不是小细节，而是 PnL 主变量。  
6. **加 funding 与 leg-level fee/slippage**：如果 `5m` 也要持有到十几小时甚至一天，funding 和夜间流动性不能继续省略。  
7. **最后再谈 shared gate**：这条线当前最有价值的身份仍是完整 raw alpha，不是先把它拆成 overlay。

## 7. 风险与保留意见
- 当前主论文我直接拿到的是 **摘要级证据**，不是全文细节；因此“fixed 显著优于 dynamic”这句目前以摘要为准，本地尚未做完全同构复现。  
- 本地快检只用了 **distance method proxy**，还没把 cointegration / hybrid 补齐。  
- 这轮用的是 Binance perp 主流币 basket，不是论文里的 `top 50 × bull/stable/bear` 全样本，不能把数值直接当论文 replication。  
- `median hold ≈ 24h timeout` 说明这类高频 pair 信号不一定真是“超短”，如果 desk 只想做极快回转，需要额外压缩持仓寿命。  
- 如果后续 dynamic threshold 加进来后反而更稳，那这篇 digest 的价值也还在：它至少先告诉我们**fixed 不该被默认淘汰**。

## 8. 来源
1. **Aghamohammadi, A., & Dastkhan, H. (2025). _Pair trading with high-frequency data in the cryptocurrency market_. China Finance Review International.**  
   - Venue: *China Finance Review International*  
   - DOI: `10.1108/CFRI-11-2024-0727`  
   - Readable URL: `https://doi.org/10.1108/CFRI-11-2024-0727`  
   - Repo URL: **未见 paper-specific public repo**  
   - Evidence note: 当前可直接拿到的是 Crossref/OpenAlex 摘要字段，摘要已明确写出 `distance / cointegration / hybrid`、`daily/4h/1h/15m/5m`、`fixed vs dynamic threshold`、`1.44/1.65/2σ` 与 `15m/5m` 盈利结论。

2. **Binance Developers. USDⓈ-M Futures API – Kline/Candlestick Data.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

3. **Binance Developers. USDⓈ-M Futures API – 24hr Ticker Price Change Statistics / Exchange Info.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/24hr-Ticker-Price-Change-Statistics`  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information`

## 9. 本地复现产物
- `reports/artifacts/quant_digests/hf_pairs_fixed_threshold_probe_20260326_0803/summary.json`
- `reports/artifacts/quant_digests/hf_pairs_fixed_threshold_probe_20260326_0803/summary.csv`
- `reports/artifacts/quant_digests/hf_pairs_fixed_threshold_probe_20260326_0803/pair_metrics.csv`
- `reports/artifacts/quant_digests/hf_pairs_fixed_threshold_probe_20260326_0803/trade_log.csv`
- `reports/artifacts/quant_digests/hf_pairs_fixed_threshold_probe_20260326_0803_5m/summary.json`
- `reports/artifacts/quant_digests/hf_pairs_fixed_threshold_probe_20260326_0803_5m/summary.csv`
- `reports/artifacts/quant_digests/hf_pairs_fixed_threshold_probe_20260326_0803_5m/pair_metrics.csv`
- `reports/artifacts/quant_digests/hf_pairs_fixed_threshold_probe_20260326_0803_5m/trade_log.csv`
