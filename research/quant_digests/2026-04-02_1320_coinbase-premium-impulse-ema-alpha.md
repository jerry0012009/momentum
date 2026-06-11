# 别把这份 2025 新 repo 只读成 130 维 GA：对 short-cycle desk，更该先测的是「Coinbase premium impulse × EMA trend alignment × 60m hold」这条 BTC directional raw alpha
- 时间：2026-04-02 13:20 UTC
- 主题类型：raw alpha
- 基础 alpha：**Coinbase 相对 Binance 的 premium impulse（`Δpremium` 的 z-score）会先于 BTC 短线方向扩散；顺着 impulse 方向、并只在本地趋势同向时跟随。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**是（可先上最小版 v0）**
- 主题标签：raw-alpha/cross-exchange/price-discovery/coinbase-premium/binance/coinbase/btc/5m/15m/event-driven/cpdiff-zscore/ema-trend/fixed-hold/repo/public-data/cost
- 证据类型：2025 GitHub 仓库 source audit（README + `calculate_premiums.py` + `genome.txt` + `fitness_backtest.py`）+ Coinbase/Binance 公共 `5m` 本地最小快检

## 1) 这次看了什么
这轮不再继续在 generic pairs / funding carry / 纯 orderflow 上内循环，而是补一个 **索引里还没单独展开、且天然可映射到 `1m/5m/15m` 的 raw alpha**：

- **tpmmthomas (2025), `cb-bfx-premium-backtest`**
- repo headline 看上去像“多交易所 premium + funding + EMA + 130 维 GA 优化器”
- 但对我们 desk 真正值得 intake 的，不是整套 GA，而是里面那个更朴素、也更容易短周期复现的旁支：
  - `Coinbase premium`
  - `CPDiff_Zscore`
  - `PriceEMA`

一句话：**不要把它读成 overfit 参数工厂；先把它缩成“Coinbase premium impulse 是否会向 Binance/主盘价格扩散”这条 directional raw alpha。**

## 2) 先回答题眼：base alpha 是什么？
**Base alpha：**
当 Coinbase 相对 Binance 的价格溢价在短时间内突然扩大/收敛（不是静态 premium 水平，而是 `premium` 的变化冲击），BTC 往往会在接下来 `30m~60m` 沿同方向继续扩散；若再加一层本地趋势对齐（只在 `price > EMA` 时接正向 impulse，只在 `price < EMA` 时接负向 impulse），短周期可执行性会明显提升。

所以这不是：
- 纯 cross-exchange spread convergence 套利；也不是
- 低频“Coinbase 长期贵/便宜”解释。

它更像：**一个 5m 级别的 price-discovery / flow-lead directional alpha。**

## 3) 为什么这条线值得进当前素材池
因为它同时满足当前优先级里最重要的几件事：

1. **是 raw alpha，不是纯 gate。**
   - 有明确方向；不是只说“适合过滤别的策略”。
2. **公开可得，复现门槛低。**
   - Coinbase `BTC-USD` candles 公共可抓
   - Binance `BTCUSDT` spot candles 公共可抓
3. **天然贴合 `1m/5m/15m`。**
   - 不需要硬把低频宏观量伪装成逐根主信号。
4. **能直接拆成完整策略骨架。**
   - entry / hold / one-position cap / fee stress 都能马上写出来。
5. **和我们之前做过的“跨所 spread 收敛”不一样。**
   - 那条主线更像 market-neutral stat-arb；
   - 这条更像 **Coinbase 先行 → Binance 跟随** 的 directional price discovery alpha。

## 4) 从 repo 里真正该拿走的是什么
### 4.1 repo 里有用的不是 130 维 GA，而是这几个 primitives
根据 `calculate_premiums.py` 与 `genome.txt`，repo 明确把以下特征做成可优化组件：

- `coinbase_premium = (coinbase_spot - binance_index) / binance_index`
- `CP_Zscore`
- `CPDiff_Zscore`
- `PriceEMA`
- `Funding_Zscore`
- 固定 TP / SL / 多空开关 / AND-OR 逻辑

对 short-cycle desk 最值得先取的是：

> **`CPDiff_Zscore + PriceEMA + 固定时间退出`**

理由很简单：
- `premium level` 往往混进静态结构差、美元/USDT 微偏差、慢变量；
- **`premium change` 才更像“哪边刚刚在主动推价格”**；
- 再用 `PriceEMA` 做一个很廉价的趋势一致性筛选，就能避免把所有 premium 冲击都当成同等可信。

### 4.2 我们 desk 该怎么重构这个 repo
**不要**先复制：
- 130+ 参数
- 多条件组合
- GA 寻优

**先做最小版：**
- 单标的：`BTC`
- 单特征：`CPDiff_Zscore`
- 单过滤：`Price > EMA` / `Price < EMA`
- 单退出：固定 `12 x 5m = 60m`

也就是先回答：
> `Coinbase premium impulse` 本身是不是一个能 survive 的短线 directional alpha？

## 5) 本地最小快检（公开数据，直接映射 5m）
### 5.1 数据口径
我本地用公开 API 做了一个最小 transfer check：

- **Coinbase**：`BTC-USD` `5m` candles
- **Binance Spot**：`BTCUSDT` `5m` klines
- 对齐区间：**2026-03-03 13:20 UTC ~ 2026-04-02 13:15 UTC**
- 对齐后样本：**8640 根 5m bar**（约 30 天）

定义：
- `premium_t = (Coinbase_t - Binance_t) / Binance_t`
- `CPDiff_t = premium_t - premium_{t-1}`
- `CPDiff_Z_t = zscore(CPDiff, rolling_window)`

### 5.2 先看：静态 premium level 不够，impulse 才更像 alpha
我先对比了两类信号：
1. `CP_Zscore`：premium 水平极端
2. `CPDiff_Zscore`：premium 变化冲击极端

结论非常清楚：
- **静态 premium level** 有一点短促 edge，但持续性差，扣成本后很容易死；
- **premium impulse (`CPDiff_Zscore`)** 更像可交易对象，尤其在 `30m~60m` 持有窗更稳。

### 5.3 最小 directional 版本：只做 impulse continuation
#### 版本 A：不加趋势过滤
规则：
- `CPDiff_Z(24) >= 2.0` → 下一根 `5m` 做多 BTC
- `CPDiff_Z(24) <= -2.0` → 下一根 `5m` 做空 BTC
- 持有 `12` 根（60m）
- 非重叠事件，单仓位

结果：
- 交易数：**223**
- 平均单笔毛收益：**+4.76 bps**
- 胜率：**51.6%**
- 按 **2 bps 单边** 成本（约 4 bps round trip）后：**+0.76 bps / trade**
- 对应 30 天累计净收益：**+1.37%**
- 但按 **4 bps 单边** 成本（约 8 bps round trip）后转负

解释：
- 这说明 **impulse 本身是真的有方向信息**；
- 但若 execution 不够好，只靠它裸奔，净 edge 还不够厚。

### 5.4 desk 更该测的版本：impulse × trend alignment
#### 版本 B：加一层 `EMA` 趋势对齐
规则：
- `CPDiff_Z(24) >= 2.5` 且 `Price > EMA(96)` → 下一根做多
- `CPDiff_Z(24) <= -2.5` 且 `Price < EMA(96)` → 下一根做空
- 持有 `12` 根（60m）
- 非重叠事件，单仓位

结果：
- 交易数：**48**
- 平均单笔毛收益：**+20.6 bps**
- 胜率：**62.5%**
- 按 **2 bps 单边** 成本后：**+16.6 bps / trade**，30 天累计净收益 **+8.24%**
- 按 **4 bps 单边** 成本后：**+12.6 bps / trade**，30 天累计净收益 **+6.18%**

这条结果的意义比 headline 更重要：

> **真正值得做的不是“Coinbase premium level”，而是“premium impulse 只在本地趋势同向时做 continuation”。**

### 5.5 一个反证：不是所有 premium 信号都能活
对照组里，若直接用 `CP_Zscore` 做 continuation：
- `CP_Z(24) >= 2.5` / `<= -2.5`
- 持有 `3` 根（15m）
- 虽然毛平均有 **+3.57 bps / trade**，但按 **2 bps 单边** 就接近打平，净后微负

所以别把“Coinbase premium”当成一个笼统单因子；**真正更像 raw alpha 的，是 premium 的冲击项，不是静态项。**

## 6) 最小可落地完整策略（v0）
下面这版已经足够进复现队列：

### 6.1 Entry
执行周期：`5m`（后续可下采样到 `15m`）

- 计算：
  - `premium_t = (Coinbase_t - Binance_t) / Binance_t`
  - `cpdiff_z_24`
  - `ema_96`
- 开多：`cpdiff_z_24 >= 2.5` 且 `binance_close > ema_96`
- 开空：`cpdiff_z_24 <= -2.5` 且 `binance_close < ema_96`
- 执行：**下一根 bar 开盘 / 下一根可成交价**

### 6.2 Exit
最小版先用最朴素的 time stop：
- **固定持有 12 根（60m）**
- 若中途出现反向同级别 impulse，可提前平仓反手（v1 再测）

### 6.3 Sizing
最小版：
- 单标的一次只开 **1 个方向仓位**
- 固定名义仓位即可先跑；
- 若要更稳，改成 `target_vol / realized_vol_96` 的简易 vol-scaling

### 6.4 Risk
最小版先加三条就够：
1. **单仓位上限**：同一时间最多 1 笔
2. **时间止损**：60m 强平，不恋战
3. **日内损失闸门**：若当日累计亏损超过预设阈值（如 3R），当天停手

### 6.5 Cost
至少要同时看两档：
- **2 bps 单边**：较理想的 maker / 优秀 taker 近似
- **4 bps 单边**：更保守的 taker / 含部分滑点近似

当前 30 天快检结论：
- **裸 `CPDiff_Z` continuation**：偏向“低成本才勉强能活”
- **`CPDiff_Z + EMA` 对齐**：在 4 bps 单边压力下仍有存活迹象

## 7) 这条 alpha 和 `15m` 的关系
虽然我这次直接在 `5m` 上做了 transfer check，但它并不只适用于 `5m`：

- `1m/3m`：更适合做 execution / entry refinement
- `5m`：最适合做信号生成本体
- `15m`：更适合做降噪后的 slow execution 版，或者作为 `5m` 信号的聚合确认

对于 desk 的实际落地顺序，我会建议：
1. 先固定 `5m` 做 alpha 真伪判断
2. 再测试 `15m` 版本是否能用更少交易数换更高净 edge
3. 最后才把 `1m/3m` 用来做 execution enhancement

## 8) 下一步怎么测（这篇最重要的部分）
### Step 1：先做 3 维小网格，不碰 GA
只测：
- `z_window ∈ {24, 36, 48}`
- `threshold ∈ {2.0, 2.5, 3.0}`
- `hold ∈ {6, 12, 18}`

目的：确认 edge 是否只出现在单一点，还是有一小块稳定 pocket。

### Step 2：把 `EMA trend alignment` 换成更便宜的 regime 定义
对照：
- `EMA(96)`
- `EMA slope > 0 / < 0`
- `15m close > EMA(32)`（低频一点）

目的：判断我们观察到的净 edge，到底来自“Coinbase premium”，还是其实只是 trend filter 在救命。

### Step 3：把 BTC 扩到 ETH，但先别急着扩山寨
ETH 可以测；
但 SOL/ALT 不要急着照搬，因为：
- Coinbase 在 BTC 的 price discovery 权重更高；
- alt 的跨所 lead-lag 结构未必一样。

### Step 4：补 execution realism
至少补三项：
- next-bar open vs next-bar VWAP
- maker-only queue risk 近似
- 夜间 / 亚洲时段 / 美盘分时表现

### Step 5：测一个更像实盘的 exit
当前 60m 固定时间止盈止损太原始，下一步应比较：
- fixed 60m hold
- opposite impulse exit
- trailing EMA exit
- 0.8~1.2 ATR hard stop + 60m time stop

## 9) 风险与保留意见
1. **当前样本只有最近 30 天。**
   - 这足够做 intake，不足够做上线结论。
2. **Coinbase/Binance 的价格对齐仍有微观噪音。**
   - USD vs USDT、时间戳对齐、接口补洞都可能污染小信号。
3. **repo 本身有明显 overfit 风险。**
   - 130+ 参数 + GA，很容易把 noise 学成 alpha；
   - 所以我们这次故意只拿最小 branch，不采纳整套 optimizer worldview。
4. **BTC 以外可能失效。**
   - 这条线更像 benchmark-level price discovery，不保证能直接平移到 alt。
5. **当前看起来更像 event-driven pocket，不像 always-on continuous edge。**
   - 这不是坏事，反而更符合 short-cycle desk 的现实：
   - pocket 比全天候硬拗更值钱。

## 10) 一句话结论
**这篇东西最值得拿走的，不是“多交易所 premium + 130 维 GA”，而是更窄、更干净的这条 raw alpha：`Coinbase premium impulse × 本地趋势对齐 × 30m~60m continuation`。**

如果只给我一个最小实验优先级，我会先跑：

> `BTC, 5m, CPDiff_Z(24), threshold=2.5, EMA(96) alignment, hold=12 bars, cost=2/4 bps one-way`。

这比继续补一个抽象 filter 更值，因为它已经是 **可执行的 directional alpha 雏形**，而且当前 30 天本地快检里，**只有“impulse + trend alignment”这版表现出了明显的成本存活迹象**。

## 11) 来源
1. **tpmmthomas. (2025). _cb-bfx-premium-backtest_. GitHub Repository.**
   - Authors / Org: tpmmthomas
   - Year: 2025
   - Title: cb-bfx-premium-backtest
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/tpmmthomas/cb-bfx-premium-backtest>
   - Repo URL: <https://github.com/tpmmthomas/cb-bfx-premium-backtest>

2. **tpmmthomas. (2025). _calculate_premiums.py_. GitHub source file.**
   - Authors / Org: tpmmthomas
   - Year: 2025
   - Title: calculate_premiums.py
   - Venue: GitHub source file
   - DOI: N/A
   - Readable URL: <https://github.com/tpmmthomas/cb-bfx-premium-backtest/blob/main/calculate_premiums.py>
   - Repo URL: <https://raw.githubusercontent.com/tpmmthomas/cb-bfx-premium-backtest/main/calculate_premiums.py>

3. **tpmmthomas. (2025). _genome.txt_. GitHub source file.**
   - Authors / Org: tpmmthomas
   - Year: 2025
   - Title: genome.txt
   - Venue: GitHub source file
   - DOI: N/A
   - Readable URL: <https://github.com/tpmmthomas/cb-bfx-premium-backtest/blob/main/genome.txt>
   - Repo URL: <https://raw.githubusercontent.com/tpmmthomas/cb-bfx-premium-backtest/main/genome.txt>

4. **tpmmthomas. (2025). _fitness_backtest.py_. GitHub source file.**
   - Authors / Org: tpmmthomas
   - Year: 2025
   - Title: fitness_backtest.py
   - Venue: GitHub source file
   - DOI: N/A
   - Readable URL: <https://github.com/tpmmthomas/cb-bfx-premium-backtest/blob/main/fitness_backtest.py>
   - Repo URL: <https://raw.githubusercontent.com/tpmmthomas/cb-bfx-premium-backtest/main/fitness_backtest.py>

5. **Coinbase Exchange API Docs. (2026 access). _Get Product Candles_.**
   - Authors / Org: Coinbase
   - Year: 2026 (accessed)
   - Title: Get Product Candles
   - Venue: Official API Docs
   - DOI: N/A
   - Readable URL: <https://docs.cdp.coinbase.com/exchange/reference/exchangerestapi_getproductcandles>
   - Repo URL: N/A

6. **Binance Spot API Docs. (2026 access). _Kline/Candlestick Data_.**
   - Authors / Org: Binance
   - Year: 2026 (accessed)
   - Title: Kline/Candlestick Data
   - Venue: Official API Docs
   - DOI: N/A
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>
   - Repo URL: N/A
