# 下跌后买压反转不是 confirmation，而是可独立交易的 raw alpha：pressure-ratio capitulation fade

- 主题类型：raw alpha
- 基础 alpha：`sell-off bar × order-book buy-pressure dominance` 之后的短周期反身性回补 / 均值回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 先回答一句：这篇东西的 base alpha 是什么？
**不是**“盘口失衡可以解释价格”这种机制描述。这里真正值得 intake 的 **base alpha** 是：**当价格刚经历一段向下冲击，但盘口买压已经显著占优时，后面几根 bar 更容易出现反身性回补；反过来，拉升后卖压占优时也更容易出现短周期回落。**

这是一条可以独立成策略的 **microstructure mean reversion / capitulation fade**，不是只给别的主策略做 filter。

---

## 为什么这轮值得写它
最近 digest 池里 continuation、pairs、options、basis 都已经很密；但 **“单资产、可直接落成 1m/3m/5m/15m 的盘口型均值回归”** 反而还不算拥挤。这个题材的价值在于：

1. **raw alpha 清晰**：先有下跌 / 拉升，再看买卖压反转，不需要依附 breakout 主线；
2. **公开数据可拿**：只要有公开 L2 depth / aggTrades / klines，就能先做最小前向实验；
3. **能直接写完整壳子**：entry / exit / timeout / stop / sizing / cost 都能明确；
4. **和最近的 OBI continuation digest 区分明显**：那篇更像“顺着冲击继续追”；这篇更像“冲击尾声出现压力反转就反着做”，属于 **另一条 raw alpha 家族**。

---

## 主要来源

### 1) 直接 repo 来源（主）
- **Owner / Year**: Dave Lam Trader, 2025
- **Title**: `Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy`
- **Type**: GitHub repo
- **Created / Updated**: 2025-08-24 / 2025-08-24
- **Readable URL**: https://github.com/davelamtrader/Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy
- **Repo URL**: https://github.com/davelamtrader/Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy
- **Key files**:
  - `006_Orderbook Imbalance Pattern based Cryptocurrencies Screening Trading Strategy.py`
  - `20170801-天风证券-利用高频数据拓展盘口数据：买卖压力失衡.pdf`

### 2) 机制 / 规则地基（repo 内 PDF）
- **Author / Year**: 吴先兴，2017
- **Title**: 《买卖压力失衡——利用高频数据拓展盘口数据》
- **Venue**: 天风证券金融工程专题报告
- **DOI**: 无
- **Readable URL**: https://github.com/davelamtrader/Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy/raw/main/20170801-%E5%A4%A9%E9%A3%8E%E8%AF%81%E5%88%B8-%E5%88%A9%E7%94%A8%E9%AB%98%E9%A2%91%E6%95%B0%E6%8D%AE%E6%8B%93%E5%B1%95%E7%9B%98%E5%8F%A3%E6%95%B0%E6%8D%AE%EF%BC%9A%E4%B9%B0%E5%8D%96%E5%8E%8B%E5%8A%9B%E5%A4%B1%E8%A1%A1.pdf

### 3) 公开数据接口（最小实验）
- Binance USDⓈ-M Futures public market data
- Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api

> 这轮真正值得拿走的，不是原报告里的 A 股 10 天持有结论本身，而是它那条 **“价格冲击 + 压力失衡”** 的结构，可以很自然压缩到 crypto 的 `1m / 3m / 5m / 15m`。

---

## 原始材料里最值钱的，不是年化数，而是这条结构

### 1) pressure ratio 的定义很直接
原报告先把日内 tick 价格当“探针”，把不同时间点出现过的挂单价格和挂单量汇总成更长的“扩展盘口”。

然后对离当前价格更近的挂单给更高权重：

- `W_i = [Close / (P_i - Close)] / Σ[Close / (P_i - Close)]`
- `P_buy = Σ Vol_i * W_i`（买盘压力）
- `P_sell = Σ Vol_i * W_i`（卖盘压力）
- **压力比**：`P = log(P_buy) - log(P_sell)`

翻成人话：**不是简单比较 bid size 和 ask size，而是比较“离当前成交价更近、对当前价格更有影响的挂单压力”。**

### 2) 原报告的事件逻辑
- 用过去 `20` 个交易日的 `mean ± 1.96 * std` 定义压力失衡边界；
- `P` 向上突破上界 = 买压占优；向下突破下界 = 卖压占优；
- 单看事件，买压占优后短期超额收益为正，卖压占优后短期超额收益为负；
- 但更关键的是：**“当日下跌后出现买压占优”** 这个条件组合最有信息量。

### 3) 最关键的数字
从 PDF 可直接提取出的结果：

1. **买压占优后，后续短期超额收益为正；卖压占优后为负；之后再反向修正。**
2. **“当日下跌后再出现买压占优”** 的组，后面 **6~7 个交易日** 的超额收益最明显。
3. 用这个事件做股票组合，**10 通道** 版本历史上拿到：
   - **年化收益 19.66%**
   - **超额收益 9.56%**
4. 分年表现里，报告特别点名：
   - **2016 年：9.07%**
   - **2017 年（截至 4/28）：6.68%**

这些数字当然不是 crypto 业绩承诺；但它们告诉我们：**“冲击后、压力反向占优”** 确实是一条可成策略的原始 alpha 结构。

---

## desk 化之后，真正该测的不是“10 天持有”，而是 1~8 bar 的 capitulation fade
如果把原报告直接照搬到 crypto，问题很大：
- 原文是 **日频事件评估**；
- 我们现在需要的是 **1m/3m/5m/15m**；
- crypto 盘口撤单、补单、假深度更多，10 天持有根本不是这里的重点。

所以最合理的 desk 化拆法是：

### base alpha 重写
> **先出现一段向下价格冲击，再出现显著买压占优 → 做短周期反弹；**  
> **先出现一段向上价格冲击，再出现显著卖压占优 → 做短周期回落。**

这就是一条完整的 **single-asset microstructure mean reversion**，而且天然适合 `1m / 3m`，其次 `5m / 15m`。

---

## 我建议直接落地成这版完整策略

### 1) 数据口径
- 交易对象：先做 `BTC / ETH / SOL / BNB / DOGE` 永续
- bar：`1m` 为底层；再聚合出 `3m / 5m / 15m`
- 每根 bar close 前，取一次 `top20` depth snapshot
- 同一 bar 内汇总 `aggTrades`

### 2) 压力指标（crypto 版最小可行）
如果做不到“原报告那种扩展盘口轨迹”，最小可行版先直接用 **bar close 的 top-N order book**：

- 以 mid 为锚，按价格距离给权重：
  - `w_bid_i = 1 / max(mid - bid_i, tick)`
  - `w_ask_i = 1 / max(ask_i - mid, tick)`
- `P_buy_t = Σ bid_size_i * w_bid_i`
- `P_sell_t = Σ ask_size_i * w_ask_i`
- `pressure_t = log(P_buy_t) - log(P_sell_t)`
- 再做 rolling z-score：
  - `pressure_z_t = (pressure_t - mean_t) / std_t`

> 如果后面拿到可重建的全轨迹 L2，再升级成“扩展盘口版”；但最小实验没必要等那一步。

### 3) 价格冲击腿
不要只看 pressure。本题的核心是 **shock + pressure reversal**。

定义两条可选冲击腿：
- **短冲击**：`ret_1bar <= -k1 * ATR_bar`（做多）/ `>= +k1 * ATR_bar`（做空）
- **小窗口冲击**：`ret_3bar <= q10`（做多）/ `>= q90`（做空）

我更建议先用第二种，因为它对 1m / 3m 噪音更稳。

### 4) 入场规则
#### Long
同时满足：
1. `pressure_z >= +1.5`
2. `ret_3bar <= rolling_q10` 或 `ret_1bar <= -1.0 * ATR`
3. 当前 bar 结束时，主动卖成交占比不再继续恶化（可用 `trade_delta` 不再创新低做软确认，可选）

#### Short
对称：
1. `pressure_z <= -1.5`
2. `ret_3bar >= rolling_q90` 或 `ret_1bar >= +1.0 * ATR`
3. 主动买成交不再继续扩张（可选）

### 5) 出场规则
这条 alpha 不该恋战，直接做短：
- **主出场**：`pressure_z` 回到 `|z| < 0.5`
- **时间出场**：最多持有 `3 / 5 / 8` bars，做参数扫
- **风控出场**：`1.2 ~ 1.5 * ATR` hard stop
- **反向翻仓**：默认先不要直接 flip，先平仓；避免 turnover 爆炸

### 6) 仓位 / sizing
- 单笔风险预算：`25 ~ 50 bps` of equity
- `position_notional = risk_budget / stop_distance`
- 单币上限：`20%` notional
- 组合层面最多同时开 `2~3` 个仓位，避免同 beta 集中爆仓

### 7) 成本假设
- `1m/3m` 先按 taker round-trip `10 / 15 / 20 bps` 三档压测
- `5m/15m` 额外做 maker-improved 假设，但默认先按 taker 看生存线

这意味着：**它不是“看见压力失衡就无脑抄底”，而是一个有完整 entry / exit / sizing / risk / cost 的可执行骨架。**

---

## 为什么我把它归成 raw alpha，而不是 filter
因为这里的入场条件本身就足够闭环：
- **价格先冲一边**
- **盘口压力却反向占优**
- **于是押注短周期回补**

它不是在替 breakout 决定“能不能追”；它自己就是一条独立下注逻辑。最多后续还能再被别的 overlay 管理，而不是反过来依附别的策略。

---

## 这条 alpha 对 `1m / 3m / 5m / 15m` 的关系

### `1m / 3m`
最自然。因为：
- 冲击和盘口反转之间的时间间隔短；
- 适合抓“砸完一轮、但买盘站出来”的回补；
- 也是最可能有 edge，但最容易被费用吞掉的地方。

### `5m`
我认为是第一优先的 desk transfer 档：
- 比 1m 噪音小；
- 仍然保留足够快的 microstructure 信息；
- 更容易穿过成本门槛。

### `15m`
仍然能做，但更像“冲击后的回补 pocket”，不是全天候 alpha。要特别防止把多个 1m 反转噪音硬聚成一根假信号。

---

## 最小可复现实验

### 数据源
- Binance USDⓈ-M Futures `depth` / `aggTrades` / `klines`

### 公开性
- 全公开，无需付费、无需账号密钥（市场数据）

### 更新频率
- `depth` / `aggTrades`：近实时
- `klines`：`1m` 可直接获取，其他周期可聚合

### 最小实验口径
**不要一上来卷长历史。最快的实验是：**

1. 开一个 recorder，连续录 `7~14` 天：
   - `depth20`
   - `aggTrades`
   - `1m klines`
2. 先做 5 个标的：`BTC / ETH / SOL / BNB / DOGE`
3. 生成每根 `1m` bar 的：
   - `pressure`
   - `pressure_z`
   - `ret_1bar`
   - `ret_3bar`
   - `ATR`
4. 跑四组：
   - `1m` 直接做
   - `3m` 聚合做
   - `5m` 聚合做
   - `1m signal -> 5m hold` 混合版
5. 统一看：
   - `+1 / +3 / +5` bar markout
   - hit rate
   - average adverse excursion
   - turnover
   - 成本后 pnl

---

## 我最建议先测的 4 个假设

### 假设 1：`5m` 可能比 `1m` 更能活
1m 可能信号更漂亮，但 flip 太快，容易被 `10~20 bps` 成本吞光。5m 反而可能是最佳生存点。

### 假设 2：alts 比 BTC 更适合这条 capitulation fade
BTC 常常在高流动状态下“压力看起来很大，但其实只是流动性回补”；高 beta 币更可能出现真正的 overshoot + snapback。

### 假设 3：只做“冲击后反转”，不要做纯 pressure fade
纯 `pressure_z` 容易被 spoofing 污染；加上“前面先有一段冲击”这条腿，能过滤大量无效挂单失衡。

### 假设 4：反向平仓优于直接 flip
因为这条逻辑是 mean reversion，不是 trend-following。直接 flip 很可能只是把一条回补策略错误改成高频双向打脸机。

---

## 风险与失败模式

1. **假深度 / 撤单污染**
   - top20 depth 很容易被 spoofing 干扰；
   - 所以别只看压力，必须保留“先冲击、再反转”的价格腿。

2. **趋势日一直单边**
   - 真单边行情里，早期买压占优可能只是抄底资金接飞刀；
   - 所以 stop 和 timeout 一定要硬。

3. **大币种盘口太厚，edge 被均摊**
   - BTC/ETH 可能更稳定，但也可能更难赚；
   - 需要分币看，不要默认跨币同参。

4. **历史深度回放门槛**
   - 公开 API 适合前向录数；
   - 如果 forward markout 有戏，再考虑补历史档案服务做更长回测。

---

## 一句话结论
这轮最值得 intake 的，不是“订单簿失衡”这四个字，而是这条可以直接 desk 化的 **shock-then-pressure-reversal** 结构：

> **先被砸，再看到买压显著占优，就做短周期回补；先被拉，再看到卖压显著占优，就做短周期回落。**

它是一条**可独立复现、可直接写成完整策略**的 microstructure mean reversion raw alpha，优先级应高于把它降级成 shared filter。

---

## 下一步怎么测（直接执行版）
1. 先录 7~14 天 Binance Futures `depth20 + aggTrades + 1m klines`
2. 先只做 `BTC / ETH / SOL / BNB / DOGE`
3. 跑 `1m / 3m / 5m / 15m` 四档，统一 exits：
   - `pressure_z` 回到 `|z| < 0.5`
   - `3 / 5 / 8` bars timeout
   - `1.2 / 1.5 ATR` hard stop
4. 先做三套成本：`10 / 15 / 20 bps` round-trip
5. 第一轮只回答三个问题：
   - 哪个周期成本后还能活？
   - 哪些币最适合？
   - 纯 pressure vs pressure+shock，哪套更诚实？

---

## 文件信息
- 文件路径：`research/quant_digests/2026-04-02_1007_pressure-ratio-capitulation-fade-alpha.md`
- 站点相对 URL：`/reading/quant_digests/2026-04-02_1007_pressure-ratio-capitulation-fade-alpha.html`
