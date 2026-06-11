# 别把 ETHBTC 论文只读成 ETH：对 short-cycle desk，更该先测的是「ALTBTC 挂牌价 vs 合成价」parity mean reversion
- 时间：2026-03-25 13:50 UTC
- 类型：2022 arXiv 论文（全文本地抽取）+ Binance Spot 公共 `5m/15m` K 线 desk 化分叉快检 + 三角套利工程 repo
- 主题类型：raw alpha
- 基础 alpha：同交易所挂牌 `ALTBTC` 与合成 `ALTUSDT / BTCUSDT` 的 log parity spread 偏离后回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/triangular-parity/altbtc/synthetic-cross/mean-reversion/binance/spot/5m/15m/1m/3m/paper/repo/execution/cost
- 证据类型：论文全文证据 + 工程 repo 参考 + 本地公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 很清楚，就是“挂牌交叉汇率 vs 合成汇率”的相对价值均值回归。**

Mallik 这篇 paper 原文研究的是：
`s_t = ln(ETHBTC_t) - ln(ETHUSDT_t / BTCUSDT_t)`。
如果市场完全无摩擦、价格完全同步，这个值理论上应接近 `0`；只要它偏离，再回去，就是可交易的 raw alpha。

对我们 desk 更值钱的读法不是继续盯着 `ETHBTC` 本身，而是把这套定义扩成**一整条 ALTBTC universe 的 synthetic-cross parity mean reversion**。这比继续围着 breakout / retest 内循环更符合当前任务：它本身就是一条可独立复现、可直接落地的 relative-value / stat-arb 原始 alpha 线。

## 2. 核心结论
- **一句话核心结论：** 这篇 paper 真正值得偷的不是 “ETHBTC 是 OU” 这句学术表述，而是 **“同交易所交叉报价相对合成报价会反复失衡，而且会很快回归”** 这条 raw alpha 骨架。
- **一句话证明方式：** 作者用 **2017-09-01 到 2021-08-31 的 Binance `1m` 数据（样本超 200 万）**，先做分布与 Dickey-Fuller 检验，再用 **Ornstein-Uhlenbeck + MLE** 去拟合这个 spread。
- 原文三个最硬的数据点：
  - 全样本 percentiles 显示该 spread 并不恒为 0，整体 **IQR ≈ 3.16 bps**；
  - 年度 IQR 从 **Year1 ≈ 14.83 bps** 下降到 **Year4 ≈ 1.47 bps**，说明大币主对随时间被套利压薄；
  - OU 参数估计为 **`α≈0.8457`、`μ≈-2.424e-05`、`σ≈0.001703`**，其中长期均值 `μ` 为负且与 0 在 `1e-05` 精度上可区分。
- 这也给了 desk 一个很直接的分叉判断：**ETHBTC 这种最成熟主对，edge 可能还在，但已经薄到很容易被费率和滑点吃掉；更值得扫的是“同一逻辑下、但偏离更厚的 ALTBTC 交叉”。**

## 3. 为什么和当前项目直接相关
- 这是标准 **raw alpha**，不是 filter / overlay 伪装成本体。
- 它直接补的是我们当前更缺的 **relative-value / stat-arb / pairs** 素材，而不是继续堆 trend/breakout confirmation。
- 这条线天然适配短周期：
  - `1m/3m`：监控偏离、做 maker-first 执行；
  - `5m/15m`：做 z-score admission、timeout、成本分层；
  - `1h`：只负责更新 symbol 白名单与容量预算。
- 更关键的是，它本身就包含完整策略组件：**entry、exit、sizing、risk、cost** 都能明确写出来，不需要先借别的 alpha 本体。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / stat-arb / market-neutral mean reversion
- 基础 alpha：`s_t = ln(ALTBTC_t) - ln(ALTUSDT_t / BTCUSDT_t)` 偏离后回归
- regime：只做仍存在稳定偏离、且回归半衰期短于 holding budget 的 `ALTBTC` 交叉
- filter / veto：symbol 预选（IQR / 极值幅度 / z>2 事件频率 / bid-ask / 深度 / fee tier）；避开异常公告、极端缺深度、零费活动切换窗口
- risk / sizing / execution overlay：三腿按 BTC notional 中性配平；优先 maker / post-only；限制单 symbol gross、单时刻并发腿数、以及净 BTC 暴露残差

## 4. 本地最小快检（Binance Spot 公共数据，desk 化分叉，不是论文精确复现）
我按 paper 的定义，把 `ETHBTC` 扩成 `ETH/SOL/XRP/DOGE/BNB/ADA/LTC` 这组 `ALTBTC` 挂牌交叉，对照其 `ALTUSDT/BTCUSDT` 合成价，做了最近 `1200` 根 `5m/15m` bar 的轻量快检。

### 4.1 ETHBTC：原论文主角，今天依然会回，但已经很薄
- `ETHBTC 5m`：spread **IQR ≈ 3.21 bps**，`|z|>=2` 事件的平均入场偏离 **≈ 4.67 bps**，后续 `1 bar` 平均回归 **≈ 4.25 bps**，胜率 **96%**。
- `ETHBTC 15m`：spread **IQR ≈ 3.14 bps**，`|z|>=2` 事件平均入场偏离 **≈ 4.71 bps**，后续 `1 bar` 平均回归 **≈ 4.64 bps**，胜率 **100%**。

翻成人话：**major cross 的价差确实会回，但厚度大概就是几 bps，天然要先过成本生死线。**

### 4.2 更值得 desk 继续追的是“同逻辑下的厚尾交叉”
- `DOGEBTC 5m`：IQR **≈ 55.6 bps**；`|z|>=2` 事件平均偏离 **≈ 73.2 bps**；后续 `3 bar` 平均回归 **≈ 56.6 bps**。
- `ADABTC 5m`：IQR **≈ 19.1 bps**；平均偏离 **≈ 28.9 bps**；后续 `3 bar` 平均回归 **≈ 29.6 bps**。
- `LTCBTC 5m`：IQR **≈ 9.5 bps**；平均偏离 **≈ 16.8 bps**；后续 `3 bar` 平均回归 **≈ 18.0 bps**。
- `DOGEBTC 15m` 仍然很厚：平均偏离 **≈ 70.4 bps**，后续 `1 bar` 平均回归 **≈ 57.4 bps**。

这组结果对当前 desk 最有价值的一句其实是：**paper 的 base alpha 是对的，但最值得测的未必是 paper headline 里的 ETHBTC，而是更厚、更慢、更容易留下净边的 ALTBTC 交叉。**

## 5. 最小可复现实验（面向 1m / 3m / 5m / 15m）
- **研究假设**：Binance spot 中部分 `ALTBTC` 挂牌交叉，会相对合成 `ALTUSDT/BTCUSDT` 出现可重复的短期偏离，并在 `1~3` 根 bar 内回归。
- **信号定义**：
  - `s_t = ln(ALTBTC_t) - ln(ALTUSDT_t / BTCUSDT_t)`
  - 在 `5m` 用 rolling `288` bars、在 `15m` 用 rolling `96` bars 计算 `z-score`
- **最小策略骨架**：
  - `z > 2`：做空 spread（short `ALTBTC`，long synthetic）
  - `z < -2`：做多 spread（long `ALTBTC`，short synthetic）
  - exit：`z` 回到 `0` 附近 / `max_hold = 1~3 bars` / `spread` 继续恶化到 `entry + 0.5σ`
- **样本切口**：先跑 `ETH/SOL/XRP/DOGE/ADA/LTC/BNB` 七个 spot 交叉，窗口 `60~90d`，主频先看 `5m/15m`，再下钻 `1m/3m`
- **先看 2 个指标**：
  1. `post-cost expectancy`（按 3-leg round-trip `6/12/20/40 bps` 四档）
  2. `timeout 前回归占比`（是否真的是快回归，而不是慢飘）

## 6. 下一步怎么测（必须）
1. **先做 symbol selection，不要一上来全市场扫。** 先按 `entry_abs_bps / post-cost survival / half-life` 给 `ALTBTC` universe 排序。  
2. **把 bar close proxy 升级成 quote / book 口径。** 下一轮至少用 best bid/ask 中间价，避免把“收盘同步误差”误当真钱。  
3. **成本必须按三腿真实计。** 这条线最容易自欺的地方，就是只看 spread 回归、不看 6 次成交与残余 BTC 暴露。  
4. **对 major 和 tail 分开测。** `ETHBTC/SOLBTC` 更像低幅高频；`DOGEBTC/ADABTC/LTCBTC` 更像高幅低频，两个 bucket 不要混在一起调同一组参数。  
5. **补执行 veto。** 若合成腿某一腿深度不足、盘口跨档过大、或预计净 edge 小于成本 `1.5x`，直接不做。  
6. **若 spot 三腿成本仍太高，再测试“signal-only proxy trade”。** 例如用 parity spread 只驱动 `ALTBTC` 单腿或 `ALTBTC vs BTC beta-hedge`，看能否保留方向性回归而减少交易腿数。

## 7. 风险与保留意见
- 原论文是 **close-based statistical fit**，不是可直接成交的 execution paper；它证明了偏离与回归存在，不等于证明了净收益自动存在。  
- `ETHBTC` 这类成熟主对已经被压得很薄，**普通 taker 费率下大概率不值得碰**。  
- `DOGEBTC/ADABTC` 这类厚尾交叉，可能部分来自 **tick size / depth 缺口 / 盘口不连续**，下一轮必须用 order-book 口径核实。  
- 这条 alpha 强依赖交易所微观结构和费率制度；若零费活动、撮合规则、maker rebate 发生变化，历史结果很容易塌。  
- 跨腿异步成交会留下净 BTC 或净 ALT 残差，实盘上它不是“纯数学 spread”，而是一个带执行失败风险的组合单。

## 8. 来源
1. **Mallik, S. (2022). _Pricing cryptocurrencies: Modelling the ETHBTC spot-quotient variation as a diffusion process_. arXiv / q-fin.PR.**  
   - DOI: `10.48550/arXiv.2111.11609`  
   - Readable URL: `https://arxiv.org/abs/2111.11609`  
   - Repo URL: **未见 paper-specific public repo**

2. **Binance Developers. _Spot API Docs – Market Data Endpoints / Kline Candlestick Data_.**  
   - Readable URL: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints`

3. **Drakkar-Software. _Triangular-Arbitrage_.**  
   - Repo URL: `https://github.com/Drakkar-Software/Triangular-Arbitrage`  
   - 作用：不是 paper 官方代码，但可作为后续 real-time cycle detection / execution orchestration 的工程参考。

## 9. 本地复现产物
- `reports/artifacts/quant_digests/synthetic_cross_parity_altbtc_20260325_1350/summary.json`
- `reports/artifacts/quant_digests/synthetic_cross_parity_altbtc_20260325_1350/summary.csv`
- `reports/artifacts/quant_digests/synthetic_cross_parity_altbtc_20260325_1350/altbtc_cross_parity_5m_detail.csv`
- `reports/artifacts/quant_digests/synthetic_cross_parity_altbtc_20260325_1350/altbtc_cross_parity_15m_detail.csv`
