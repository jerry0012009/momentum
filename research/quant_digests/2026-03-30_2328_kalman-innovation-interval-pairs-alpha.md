# 别把 Kalman pairs 继续写成 `dynamic beta + rolling z-score`：这篇 2024 COMPSAC 更该先测的是「innovation-vol interval trigger × pair mean reversion」完整 raw alpha
- 时间：2026-03-30 23:28 UTC
- 类型：2024 IEEE COMPSAC 摘要元数据（OpenAlex/Crossref/DOI） + Binance USDⓈ-M Perpetual 公共 `15m` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：**co-integrated / co-moving pair 的相对价格错位回摆**——不是赌单边方向，而是用 Kalman 动态 beta 定义 fair spread；当当前 innovation 偏离超过预测的 innovation-vol 区间时，做 long-short spread，吃的是相对价格向动态均衡回归的 alpha。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/kalman-filter/dynamic-beta/innovation-volatility/interval-forecast/hourly/15m/5m/1m/3m/paper/abstract-only/binance/perpetual/cost
- 证据类型：**摘要级论文证据 + 本地公共数据 transfer check**（注意：原文全文未开放拿到，这次 intake 只写能从摘要清楚推断、且已被本地快检验证过方向的部分）

> 先把 **base alpha** 说清楚：
>
> **这不是“Kalman 只是更平滑的 filter”。真正的 alpha 本体，是 pair spread 的均值回归；innovation-vol interval 只是把 entry 从“看到偏离就上”升级成“只在偏离已经越过预测区间时才上”。**

## 1. 这次看了什么
这次主看 **You Liang, Aerambamoorthy Thavaneswaran, Juan Liyau, Areebah Muhammad, Thimani Ranathungage, Ruppa Thulasiram (2024)** 的会议论文：

> **_A Cryptocurrency Multiple Trading Strategy with Kalman Filter Innovation Volatility Interval Forecasts_**  
> *2024 IEEE 48th Annual Computers, Software, and Applications Conference (COMPSAC)*  
> DOI: `10.1109/COMPSAC61105.2024.00037`

先说结论：

> **对我们 desk 来说，这篇东西最值钱的不是“Kalman + neural network”这几个词，而是它明确把 pairs raw alpha 的入场层改写成了：`dynamic beta fair spread` → `innovation volatility interval` → `only breach then trade`。**

这和当前项目直接相关，因为我们库里 pairs / stat-arb 已经有：
- 静态或 rolling z-score 的 spread MR；
- threshold map / correlation-aware threshold；
- multi-pair / market-factor neutralized pair book；
- OBI / cost / matching / concentration 这类 overlay。

**相对还缺的，是一个更像 timing layer 的东西：不是只看 spread 已经偏多远，而是看它是否已经越过“本该容忍的 innovation 区间”。**

## 2. 论文摘要里真正能确认的东西
由于本次拿到的是 **摘要级证据**，所以只写摘要里明确说到的内容，不乱补：

1. 论文研究的是 **market-neutral pairs / multiple trading**，核心是利用 **nonstationary but co-integrated asset prices 的 mean reversion**。
2. 作者不是只做普通 Kalman fair value，而是把 **KF algorithm** 和 **KF innovation volatility interval forecasts** 结合起来。
3. 样本资产是 **Bitcoin / Ethereum / Bitcoin Cash 的小时价格**，样本场景明确写的是 **bear market**。
4. 摘要直接给出的主结论是：
   - **upper / lower trading intervals using KF innovation volatility interval forecasts**
   - **优于**
   - **upper / lower trading bands using KF innovation volatility point forecasts**。
5. 摘要还明确说：在 **考虑 transaction costs** 的情况下，interval-forecast 策略相较 point-forecast 策略依然表现出：
   - **更高 profits**
   - **更稳健的交易笔数**。

这已经足够支持一个很清晰的 desk 化读法：

> **pair raw alpha 还是 spread MR，但触发器别继续死写 rolling z-score；更值得先测的是“当前 mispricing 是否越过预测 innovation-vol 区间”。**

## 3. 这篇东西为什么值得进当前素材池
先回答一句：

> **它为什么比再补一篇 generic trend / breakout 更值得？**

因为当前 desk 的 raw alpha 池虽然已经开始补 pairs / stat-arb，但很多还停在：
- `spread > threshold` 就上；
- `z-score > ±k` 就上；
- `threshold map` 调的是边界大小，而不是边界来源。

这篇 paper 提供的是另一种更像“结构升级”的读法：

### 3.1 alpha 本体没变，但 timing layer 变了
- **alpha 本体**：spread mean reversion
- **不是 alpha 本体的层**：innovation-vol interval
- **它的角色**：决定这次偏离是否已经大到值得做

换成人话：

> **不是所有正 residual 都值得做空 spread，也不是所有负 residual 都值得做多 spread。更该做的，是等 residual 连“预测出来的容忍区间”都已经越过去。**

### 3.2 它服务的是完整策略，而不是纯 filter
这不是那种“只能当 overlay 的小零件”，因为它可以独立定义：
- `pair selection`：高共动 / 协整或近协整的 pair
- `entry`：innovation interval breach
- `exit`：回到中性带 / max hold / 反向 breach
- `sizing`：按 interval 宽度、forecast confidence、pair liquidity 缩放
- `risk`：beta jump / spread persistence / cost veto
- `cost`：双腿 round-trip + funding

所以它虽然是 pairs 里的 timing 改造，但本质上仍是 **可单独落地的 raw alpha skeleton**。

## 4. 最值得 desk 直接偷走的策略骨架
我会把这篇东西直接翻成下面这条策略：

### 4.1 Universe
先只做流动性足够、关系稳定的 majors pair：
- `BTC-ETH`
- `ETH-BCH`
- `BTC-BCH`
- desk 实盘化时再换成更当代的 `ETH-BNB / ETH-SOL / BTC-ETH`

### 4.2 Fair spread
用 **Kalman 动态回归** 持续更新：
- `y_t = alpha_t + beta_t * x_t + innovation_t`
- `innovation_t` = 当前 pair mispricing

### 4.3 Entry
不是 `|zscore| > k`，而是：
- 预测/估计当前 innovation 的可容忍波动区间；
- 当 `innovation` **越过 upper/lower interval** 才开仓；
- `innovation > upper`：做空 spread；
- `innovation < lower`：做多 spread。

### 4.4 Exit
- innovation 回到中性带；
- 或穿回 `|z| < 0.25`；
- 或 `max hold = 4~8 bars`；
- 或 beta / spread 结构突变时强平。

### 4.5 Sizing / veto
- interval 越宽：越像结构不稳，应该减仓；
- liquidity / funding / legs borrow / taker spread 越差：越该 veto；
- `1m/3m` 更适合拿来做 execution veto，不要直接当主 alpha 时钟。

## 5. 本地最小 transfer check：Binance perpetual `15m`
为了避免只在摘要上空转，这次我直接做了一个 **paper → desk proxy**：

### 5.1 代理实验怎么做
- 数据：Binance USDⓈ-M Perpetual 公共 `15m` K 线
- 资产：`BTCUSDT / ETHUSDT / BCHUSDT`
- 样本：最近约 **120 天**（本地抓取共约 **11,472 bars / pair**）
- pair：
  - `ETHUSDT-BTCUSDT`
  - `BCHUSDT-BTCUSDT`
  - `BCHUSDT-ETHUSDT`
- fair spread：Kalman 动态 beta
- 对比 3 个版本：
  1. **point_forecast**：看到 residual 偏离就每 bar 反着做一把
  2. **rolling_band**：传统 rolling residual std 阈值
  3. **innovation_interval**：用 innovation volatility proxy（EWMA interval）定义 entry threshold

注意：
- 这不是论文原始完整复刻；
- 它是一个非常明确的 **transfer proxy**，只回答一句：
  - **把 entry 从 point / rolling band 改成 innovation interval，能不能在 15m 上先看到更像样的 gross edge？**

### 5.2 总体结果：gross 上，interval 确实比 point / rolling band 更像样
本地汇总结果（3 个 pair 合并）：

- **innovation_interval**
  - 交易数：`2,840`
  - 胜率：`52.82%`
  - 平均净值（未扣成本）：**`+0.56 bps/trade`**
  - 平均持有：`1.68 bars`
- **rolling_band**
  - 交易数：`2,646`
  - 胜率：`52.77%`
  - 平均净值（未扣成本）：**`+0.25 bps/trade`**
  - 平均持有：`1.70 bars`
- **point_forecast**
  - 交易数：`17,205`
  - 胜率：`50.36%`
  - 平均净值（未扣成本）：**`-0.02 bps/trade`**
  - 平均持有：`1.00 bar`

这组数的意义非常直接：

> **paper 里“interval 优于 point forecast”的方向，在我们 15m proxy 里是能看到 transfer 痕迹的。**

而且不只是“比 point 好一点”，而是：
- **point** 基本是高换手、低质量；
- **rolling band** 有一点 gross edge；
- **innovation interval** 在 gross 上又更进一步。

### 5.3 最好的 pair 是 `BCH-ETH`
在这组旧 paper trio 里，最强的是 `BCHUSDT-ETHUSDT`：

- **innovation_interval**：
  - 交易数：`951`
  - 胜率：`53.52%`
  - 平均 gross：**`+2.09 bps/trade`**
  - 持有：`1.77 bars`
- **rolling_band**：
  - 交易数：`877`
  - 胜率：`53.25%`
  - 平均 gross：**`+1.44 bps/trade`**
- **point_forecast**：
  - 交易数：`5,735`
  - 胜率：`50.34%`
  - 平均 gross：**`+0.22 bps/trade`**

这说明：

> **在适配的 pair 上，innovation interval 不只是“过滤掉一部分噪声交易”，而是真的把单笔 spread 回摆质量抬上去了。**

### 5.4 但别高兴太早：taker 成本仍然会把它杀死
按本地 proxy 的 `8 bps round-trip` 成本去看：
- **innovation_interval**：平均 **`-7.44 bps/trade`**
- **rolling_band**：平均 **`-7.75 bps/trade`**
- **point_forecast**：平均 **`-8.02 bps/trade`**

也就是说：

> **目前这条 transfer 更像“raw alpha 候选已出现，但还没过 execution / cost 生存线”。**

它不是现在就能全天候 taker 硬跑的策略，至少还需要：
- 更稀疏的 entry；
- 更强的 pair pre-selection；
- maker / rebate / queue quality 假设；
- 或者只在更宽 mispricing 事件里做。

## 6. 这次该怎么定位：raw alpha，不是纯 overlay
这里要避免一个误读：

> **innovation interval 不是单独的 filter 主题，它服务的是 spread mean reversion 这个 raw alpha。**

如果只把它当 filter，会低估它的价值。更准确的说法是：
- **raw alpha**：pair spread MR
- **这篇 paper 的新增贡献**：entry timing layer 的升级
- **不是主角的东西**：神经网络名字本身

所以这轮 digest 的正确归类还是：**raw alpha**。

## 7. 为什么和当前学习进展直接相关
结合当前项目进度，这篇最合适的切入点不是“再做一篇 Kalman 论文综述”，而是：

1. **pairs 池已经有不少 spread/z-score 体裁**，但“threshold 从哪来”还没挖够；
2. **desk 现在优先补 raw alpha**，这篇仍然是 raw alpha，不是纯 gate；
3. **它补的是 entry 机制，而不是再换一个同质化 pair selector**；
4. **它天然适合 `15m 主时钟 + 5m execution` 的两层实现**。

用一句更短的话说：

> **这篇 paper 的价值，不在于证明 Kalman 很厉害，而在于提醒我们：pairs 的触发边界完全可以来源于 innovation interval，而不是只来源于 rolling std。**

## 8. 下一步怎么测（必做）
### 8.1 先做 15m 正式 baseline，不急着压到 1m
下一步最小正式实验建议：

**Universe**
- 先换到更当代、更可交易的 majors：
  - `ETH-BNB`
  - `ETH-SOL`
  - `BTC-ETH`
  - `BTC-BNB`
- 保留 `BCH-ETH` 只作为 paper-era reference，不把它当主实盘对象。

**Signal**
- `Kalman fair spread`
- `innovation volatility interval`
- 对比：
  - `rolling z-score`
  - `innovation interval`
  - `innovation interval + wider threshold only`

**Entry**
- 只做最极端 `10% / 5%` breach，别每次轻微越界都做；
- 增加 `cooldown`，防止同一段 spread 抖动里反复来回打。

**Exit**
- `z -> 0` / 中性带回归；
- `max hold = 4 / 8 / 12 bars` 参数扫一遍；
- 同时比较 `time stop` 和 `mid-band stop`。

**Cost**
- 明确区分：
  - taker-taker
  - maker-taker
  - maker-maker（仅理论上界）
- funding 必须单列，不要吞进 return。

### 8.2 5m / 3m / 1m 应该怎么接
我的建议不是把这条线直接缩到 `1m` 开主策略，而是：

- **15m**：负责 alpha clock（pair 是否已经足够偏离）
- **5m**：负责切片、排队、微结构 veto
- **3m / 1m**：负责 execution timing，不负责重新定义 base alpha

原因很简单：
- 当前 15m gross edge 本来就不厚；
- 盲目压到 1m/3m，大概率先被成本和来回抖动吃死；
- 正确路线是：**先把 15m 的 interval-trigger 做厚，再把 5m/1m 用来减少成交损耗。**

### 8.3 最应该优先回答的 4 个问题
1. **interval threshold 是否稳定优于 rolling z-score？**
2. **这种优势只出现在旧 trio（BTC/ETH/BCH），还是对当前 majors 也成立？**
3. **必须要“预测区间”吗，还是简单 EWMA/GARCH innovation vol 就已经够用？**
4. **在哪个成本结构下它开始可活：maker-taker 还是必须 rebate 才行？**

## 9. 当前结论（一句话版）
> **这篇 2024 COMPSAC 对我们最有价值的，不是“Kalman + NN”本身，而是把 pairs raw alpha 的入场层从 `rolling z-score` 改写成 `innovation-vol interval breach`；在本地 Binance `15m` proxy 上，这个改写确实比 point / rolling band 更像样，但目前还没过 taker 成本线。**

## 10. 文件与产物
- 研究笔记：`research/quant_digests/2026-03-30_2328_kalman-innovation-interval-pairs-alpha.md`
- 本地实验目录：`reports/artifacts/quant_digests/kalman_innovation_interval_pairs_20260330/`
- 关键产物：
  - `summary.csv`
  - `overall_summary.csv`
  - `trade_log.csv`
  - `pair_diagnostics.csv`
  - `*_pair_frame.csv`
  - `kalman_innovation_interval_pairs_20260330_run_probe.py`

## 11. 来源
1. **Liang, Y., Thavaneswaran, A., Liyau, J., Muhammad, A., Ranathungage, T., & Thulasiram, R. (2024). _A Cryptocurrency Multiple Trading Strategy with Kalman Filter Innovation Volatility Interval Forecasts_. 2024 IEEE 48th Annual Computers, Software, and Applications Conference (COMPSAC).**
   - DOI: `10.1109/COMPSAC61105.2024.00037`
   - DOI URL: `https://doi.org/10.1109/COMPSAC61105.2024.00037`
   - OpenAlex metadata URL: `https://api.openalex.org/works/https://doi.org/10.1109/COMPSAC61105.2024.00037`
   - Crossref metadata URL: `https://api.crossref.org/works/10.1109/COMPSAC61105.2024.00037`
   - 说明：本次 intake 主要依赖摘要元数据与本地 transfer proxy，未拿到可直接通读的开放全文。
2. **Binance USDⓈ-M Futures API**（本地 `15m` transfer check 数据源）
   - Klines endpoint: `https://fapi.binance.com/fapi/v1/klines`
   - 公开性：公开 API，无需私钥即可抓取历史 K 线
   - 更新频率：按交易所 bar 频率更新
   - 最小可复现实验口径：`BTCUSDT / ETHUSDT / BCHUSDT`，`15m`，约 120 天，Kalman 动态 beta + innovation interval proxy vs rolling band / point forecast
