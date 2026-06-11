# 别把 cross-crypto predictability 继续读成“所有山寨一起跟”：这篇 2024 JEDC 论文更值得先测的是「common-shock lag ranking」raw alpha
- 时间：2026-03-25 19:47 UTC
- 类型：2024 JEDC 论文（ScienceDirect 摘要页 + 导言含主要结果）+ Binance Futures 公共 `15m/5m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：当 `BTC / 全市场` 出现较大短周期 common shock 时，不同 alt 对这类冲击的滞后传导强弱不同；因此更值得做的是 **按预测值做横截面 lag ranking（long 最可能跟随者 / short 最弱或反向者）**，而不是把所有 alt 一把梭同向打包
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/lead-lag/common-shock/lag-ranking/btc-alt/event-pocket/binance/perpetual/5m/15m/paper
- 证据类型：论文证据 + 本地公共数据快检

> 先回答 base alpha：**不是 filter，不是“信息扩散解释层”。base alpha 就是“common shock 之后，谁跟得快、谁跟得慢”的横截面相对值 raw alpha。** 这轮它能进研究池，不是因为我们缺第 N 篇 BTC lead-lag，而是因为它把“BTC 先动 → alt 再动”升级成了 **可排序、可做 long-short、可加成本治理** 的完整骨架。

## 1. 这次看了什么
主来源是：
- **Li Guo, Bo Sang, Jun Tu, Yu Wang (2024), _Cross-cryptocurrency return predictability_, Journal of Economic Dynamics and Control**

这篇论文最值钱的地方，不是“又一次证明 BTC 会带 alt”，而是：

**作者把短周期 alpha 从“单个 leader coin 的直觉”推进成了“跨币 lag network 的可交易预测”。**

论文用 Binance 分钟级数据（top 30 coins，2019-03-25 至 2021-04-30）做的不是纯相关性故事，而是直接落到 **adaptive LASSO / PCA / BTC benchmark** 的 OOS long-short 组合。对当前 desk 来说，它比简单 `BTC shock → 全 alt 篮子` 更值得复现，因为它天然是 **cross-sectional / relative-value** 策略，而不是方向性大盘 beta。

更关键的是，它刚好接上我们最近的学习进展：
- 我们已经有 **BTC shock→alt basket**、**leader-laggard**、**volume-weighted XS momentum** 这些更粗颗粒的 lead-lag intake；
- 这篇东西只有在一个前提下才值得再写一篇：**它给的是“common-shock pocket 里的排序版 raw alpha”，而不是重复讲一遍 leader heuristic。**

## 2. 核心结论
- **一句话核心结论：** 这篇 2024 JEDC 论文最该偷的，不是“lag effect 存在”这句老话，而是：**只有在 common shock 足够大时，cross-crypto lag ranking 才更像可执行的 raw alpha；全天候 always-on 版本太薄。**
- **一句话它怎么证明：** 作者用 Binance 分钟级跨币 return network 做 pooled regression、adaptive LASSO、PCA 和 OOS quintile long-short；我再用 Binance USDⓈ-M Futures 公共 `15m/5m` 数据做最小 proxy，验证“always-on 很薄，但 shock pocket 更厚”。

3 个关键数据点：
1. **论文原始结果**：滞后其他币收益对单币下一分钟收益的 pooled 预测效应大约是 **0.40–4.82 bps / minute（每增加 1 个标准差）**；adaptive LASSO 对每个目标币通常会选出 **至少 6 个** 其他币作为显著 predictor。
2. **论文的交易层结果**：按 OOS 预测值做 quintile long-short，分钟级 spread 大约是 **3.34 bps（LASSO）/ 1.85 bps（PCA）/ 1.54 bps（BTC regression）**；作者还写到 futures 侧在 **4 bps taker cost、10-minute rebalance** 下仍能留下约 **0.34 bps**，`5-minute` 再平衡更强。
3. **本地最小快检（11 个高流动性 alt perp，近 45 天，train/test 一刀切）**：
   - `15m` 上如果全天候做 `BTC-only` lag ranking，平均毛收益只有 **+0.88 bps / rebalance**；`LASSO` 版更薄，只剩 **+0.18 bps**。
   - 但若只保留 **top 30% 的 `|BTC 15m lag return|` common-shock bars**，`BTC-only` lag ranking 会提升到 **+2.17 bps / rebalance**；同口径 `|market lag|` gate 约 **+1.71 bps**。
   - `5m` 上无论 `BTC-only` 还是 `LASSO`，shock gate 后大多仍只在 **~0.7 bps** 附近，说明这条线在当前 perp transfer 上更像 **15m shock-pocket**，还不是 bar-by-bar 的 taker 圣杯。

## 3. 为什么和当前 desk 直接相关
- 这是 **raw alpha**，不是解释层，也不是共享 gate。
- 它补的是我们当前更该继续扩的方向：**cross-sectional / relative-value / stat-arb 式短周期素材池**。
- 它和最近已有的 `BTC shock→alt basket` 最大区别在于：
  - 不是“所有 alt 一起 long/short”；
  - 而是 **按历史传导系数 / 预测值排序**，做 `long strongest lag followers / short weakest or opposite responders`。
- 这让它天然更容易 desk 化成完整策略：
  - `entry`：只在 common shock pocket 开机
  - `ranking`：做横截面预测值排序
  - `exit`：固定 `15m/30m/45m`
  - `sizing`：等权或 inverse-vol
  - `cost/risk`：maker/TWAP、单币上限、sector cap

## 3.5. 策略拆解（必填）
- 方向属性：cross-sectional / relative-value / lead-lag
- 基础 alpha：common shock 之后，不同 alt 的滞后反应强弱可排序
- regime：`|BTC lag return|` 或 `|cross-market lag return|` 处于高分位时才开机
- filter / veto：
  - 只做高流动性、可稳定做空的 perp
  - 跳过极端 funding、异常 OI spikes、刚上新币
  - 可加 `event blackout` 与 `spread/impact veto`
- risk / sizing / execution overlay：
  - 先做等权 long-short，后续加 `inverse-vol`
  - 单币 notional cap、单 sector cap
  - 执行层默认别用 bar-close taker；优先 `5m slice / TWAP / maker-lean`
- entry：
  1. 每根 `15m` bar 计算 `abs(ret_BTC_{t-1})` 或 `cross-market avg abs lag return`
  2. 只有当其落在高分位（如 top 30%）时才生成信号
  3. 用 rolling regression / LASSO / PCA 对每个 alt 预测 `ret_{t}`
  4. `long` 预测值最高的一组，`short` 最低的一组
- exit：首轮先测固定持有 `1 bar / 2 bars / 3 bars`（`15m / 30m / 45m`）

## 4. 可复刻的最小实验
**数据源与公开性**：
- 数据源：Binance USDⓈ-M Futures Klines
- 公开性：公开可得，无需 API key
- 更新频率：`5m / 15m`

**第一版最小回测口径**：
- universe：`ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC/BCH/TRX`
- signal bar：`15m`
- predictor：
  - baseline A：每个 alt 用 `BTC lag return` 做 rolling regression
  - baseline B：用 `other-coins lag returns` 做 rolling LASSO / ridge / PCA proxy
- gate：只保留 `abs(BTC 15m lag return)` 位于过去 `30d` 滚动样本 **top 30%** 的 bars
- portfolio：`long top tercile forecast / short bottom tercile forecast`
- hold：`15m / 30m / 45m`
- 最先看 4 个指标：
  1. `avg gross bps per rebalance`
  2. `break-even round-trip cost`
  3. `hit rate`
  4. `coefficient / rank stability`

## 5. 下一步怎么测
1. **把 train/test 改成 rolling walk-forward**：这轮只是 admission 级一刀切；下一步应做 `30d/45d train + 7d/14d test` 的滚动更新。  
2. **把 hold 从 `15m` 扩到 `30m/45m`**：当前 `+2.17 bps` 的 shock-pocket 毛边还不够 taker；需要确认更长持有是否能把 diffusion 留出来。  
3. **把 shock 分成正/负两侧**：`BTC 大涨后` 与 `BTC 大跌后` 的 alt 传导很可能不对称，别用同一套系数硬混。  
4. **把 gate 从纯价格 shock 升级成“价格 shock × crowding / funding / OI”**：论文里 event/common-shock days 更强，desk 化时应把“只是大波动”与“带 crowding 的大波动”分开。  
5. **做 sector-neutral 与 liquidity-neutral 版本**：防止策略其实只是在吃 meme/高 beta 板块暴露，而不是纯 lag ranking edge。  

## 6. 风险与保留意见
- 论文样本是 **2019–2021 Binance spot 分钟数据**；我这里是 **近期 Binance perp `5m/15m` proxy**，transfer 不一定同号。  
- 论文里强调的是广义 cross-crypto predictability；我当前更认可的 desk 读法是它的 **side branch：common-shock pocket lag ranking**。  
- 本地快检非常诚实地说明：**always-on 版本太薄**，当前只有 shock gate 后才稍微像样。  
- 当前 `+2.17 bps / 15m rebalance` 依然不足以支撑粗糙 taker 执行；如果 `30m/45m` 持有拉不开、或者 maker/TWAP 也吃不下成本，这条线就该降级为 research note，而不是立刻进交易优先级。  
- 这轮 `LASSO` 在近期 perp 样本上反而不如 `BTC-only` baseline，说明别把论文 headline 里的“更复杂模型”自动等同于 desk 最优实现。  

## 7. 来源
1. **Guo, L., Sang, B., Tu, J., & Wang, Y. (2024). _Cross-cryptocurrency return predictability_. Journal of Economic Dynamics and Control, 163, 104863.**  
   - DOI: `10.1016/j.jedc.2024.104863`  
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S0165188924000551`  
   - Metadata URL: `https://api.crossref.org/works/10.1016/j.jedc.2024.104863`  
   - Repo URL: `未见作者官方开源代码`
2. **Binance Developers. USDⓈ-M Futures API – Kline/Candlestick Data.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 8. 本地产物
- `reports/artifacts/quant_digests/cross_crypto_predictability_20260325_1945/summary.csv`
- `reports/artifacts/quant_digests/cross_crypto_predictability_20260325_1945/coefficients.csv`
- `reports/artifacts/quant_digests/cross_crypto_predictability_20260325_1945/portfolio_panel.csv`
- `reports/artifacts/quant_digests/cross_crypto_predictability_20260325_1945/shock_gate_summary.csv`
- `reports/artifacts/quant_digests/cross_crypto_predictability_20260325_1945/meta.json`
