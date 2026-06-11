# 别把 MACD 背离交叉当“低位抄底神器”：对 short-cycle crypto desk，更该先拆的是「零轴下 MACD bullish cross / histogram divergence bounce」这条 raw alpha 壳是不是手续费陷阱

- 主题类型：`raw alpha`（带 histogram-strength sizing / exit 组件）
- 基础 alpha：`MACD 零轴下 bullish crossover 或价格新低但 histogram 抬高的 divergence bounce`，做多后用 bearish crossover / histogram fade / hard time-stop 出场
- 是否可独立复现：`是`
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：`是`

## 0) 先说结论（给 desk 的一句话）
**这条线目前不该直接进入实盘候选。** `keitaj/hyperliquid-bot` 的 MACD 模块给了一个结构很完整、可快速复现的短周期 raw alpha 壳，但迁到 Binance USDⓈ-M `5m/15m` 后，简单 long-only bounce 版本在 6 个高流动性币上全为成本后负收益；它更适合作为“反弹入场组件 / 趋势策略减仓确认”，而不是独立主 alpha。

## 1) 这次为什么值得写（且不重复）
近期池子里已经覆盖了很多 `breakout`、`cross-sectional loser→winner fade`、`pairs / basis / funding`，但**“单标的动量指标的低位反弹壳：MACD cross + divergence + 动态 sizing”**还没有被单独拆过。这个 2026 高活跃 Hyperliquid 仓库的价值在于：

- raw alpha 清楚：`MACD bullish cross below zero` 或 `bullish divergence`；
- entry / exit 清楚：post-only buy，bearish crossover 或 histogram 衰退卖出；
- sizing 清楚：按 histogram strength 放大 / 缩小；
- 风控壳完整：仓位上限、risk guardrails、per-trade stop、daily loss limit 等在 repo 层有参数入口。

换句话说，这不是“泛指标介绍”，而是一个可以马上跑 `first verdict` 的完整策略骨架。

## 2) 来源与策略拆解（repo source audit）
本轮主来源：
- 仓库：`keitaj/hyperliquid-bot`（GitHub，2026 仍活跃）
- README：声明支持 Hyperliquid / HIP-3，多策略包括 `simple_ma / rsi / bollinger_bands / macd / grid_trading / breakout / market_making`
- 源码：`strategies/macd_strategy.py`

源码里的 MACD 规则可还原为：
1. 计算 `EMA(12) - EMA(26)` 得到 `macd_line`，再用 `EMA(9)` 得到 `signal_line`；
2. 买入条件 A：上一根 `macd <= signal`，当前 `macd > signal`，且 `macd < 0`；
3. 买入条件 B：最近窗口里价格创新低，但 `macd_histogram` 没有同步创新低，且 histogram 正在抬升；
4. 卖出条件：持多时出现 bearish crossover，或 histogram 转负且继续下降；
5. 仓位调节：`histogram_strength` 高则放大，低则缩小。

> 一句话核心结论：**MACD cross/divergence 是 raw alpha 本体；histogram strength 是 sizing，bearish cross/hist fade 是 exit，不应把整件事误读成单纯 filter。**

> 一句话“它怎么证明”：**我们把源码的核心 trade-on/trade-off 规则迁到 Binance 公共短周期 K 线，直接测 `5m/15m` long-only 成本后表现。**

## 3) 最小可复现实验（5m/15m portability probe）
### 3.1 数据与口径
- 数据源：Binance USDⓈ-M Futures 公共 klines（公开可得）
- 周期：`15m` 近 `75d`；`5m` 近 `21d`
- 标的：`BTC/ETH/SOL/BNB/XRP/DOGE` 共 6 个高流动性合约
- 信号：`t` 生成，`t+1 open` 入场 / 出场
- 成本：单边 `4 bps fee + 2 bps slip`，往返约 `12 bps`
- 持仓限制：`15m` 最多 `16 bars`；`5m` 最多 `24 bars`
- 版本说明：这是 first verdict，不是参数优化；保留 repo 的核心思想，但用最小可复现口径替代真实 Hyperliquid 下单细节。

### 3.2 核心结果
`15m`：
- 6 个币合计 `1420` 笔，单币中位 `231` 笔；
- 平均每笔净收益 `-11.14 bps`；
- 中位净收益 `-26.73%`，正收益币种 `0/6`；
- 中位胜率约 `30.27%`，中位 MDD `-28.06%`；
- 入场中约 `60.2%` 来自 bullish cross，其余来自 divergence。

`5m`：
- 6 个币合计 `1250` 笔，单币中位 `205.5` 笔；
- 平均每笔净收益 `-10.05 bps`；
- 中位净收益 `-18.85%`，正收益币种 `0/6`；
- 中位胜率约 `24.87%`，中位 MDD `-20.01%`。

### 3.3 人话解释
这组结果很像典型“看图很舒服、扣成本很难活”的反弹策略：

- `MACD 零轴下金叉`确实能频繁抓到底部尝试，但**反弹幅度不稳定，很多交易刚够覆盖方向噪音，覆盖不了手续费 + 滑点**；
- `histogram divergence` 作为早期反弹信号太敏感，容易在下跌趋势中连续接刀；
- 如果不加趋势 / regime / 流动性 gate，单独 long-only 做 `5m/15m` 反弹，结果更像“手续费转移器”。

## 4) 对当前素材池的意义（取舍）
保留，但要降级定位：

- 不把 `MACD cross/divergence bounce` 当独立主 alpha 直接推进；
- 可以把它放进两个更有价值的位置：
  1. **trend-pullback 的再入场确认**：只在上级趋势向上、回调末端出现 bullish cross/divergence 时入场；
  2. **mean-reversion 策略的 exit / size-down 信号**：histogram 继续恶化时减少接刀仓位。
- 若后续要继续测，必须先加 `BTC regime + volatility gate + spread/liquidity gate`，否则大概率继续被成本吃掉。

## 5) 下一步怎么测（直接可执行）
1. **加上级趋势过滤**：只允许 `15m/1h EMA fast > slow` 且 BTC 不在下跌 regime 时，触发 `5m MACD bullish cross below zero`。
2. **拆 cross 与 divergence**：分别测 `bullish cross only`、`divergence only`、`cross+divergence 同时满足`，别把两个噪音水平不同的信号混在一起。
3. **改成 router 而非单币连续交易**：每根只选 histogram reversal 最强、且 spread/volume 过线的 top1/top2 币，降低无效交易数。
4. **做成本阶梯**：`2/4/6/8/12 bps round-trip`，确认它是“彻底没 edge”还是“只适合 maker-first / Hyperliquid 低费率环境”。
5. **加 time-stop / ATR-stop A/B**：当前 hard time-stop 只是兜底；需要对比 `1.5~2.0 ATR stop` 与 `opposite MACD cross exit` 的收益分布。

## 6) 关键来源（含 DOI / URL）
1. **keitaj (2026)**. *hyperliquid-bot*. GitHub Repository.  
   - Authors: `keitaj`  
   - Year: `2026`（仓库活跃更新）  
   - Title: `Hyperliquid Trading Bot`  
   - Venue: `GitHub`  
   - DOI: `N/A`  
   - Readable URL: `https://github.com/keitaj/hyperliquid-bot`  
   - Repo URL: `https://github.com/keitaj/hyperliquid-bot`  
   - Source file: `strategies/macd_strategy.py`

2. **Lo, A. W., Mamaysky, H., & Wang, J. (2000)**. *Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation*. NBER Working Paper / Journal of Finance version.  
   - DOI: `10.3386/w7613`  
   - Readable URL: `https://www.nber.org/papers/w7613`

3. **Svogun, D., & Bazán-Palomino, W. (2022)**. *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?* *Journal of International Financial Markets, Institutions and Money*.  
   - DOI: `10.1016/j.intfin.2022.101601`  
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1042443122000130`

---

## 附：本轮实验文件
- `reports/artifacts/quant_digests/macd_divergence_probe_20260422/summary.txt`
