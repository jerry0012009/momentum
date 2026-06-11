# 别把这个 long/short ratio collector 只当情绪面板：对 short-cycle desk，更该先测的是「retail-more-short-than-top × SOL 反身性回补」这条 raw alpha
- 时间：2026-04-12 04:40 UTC
- 类型：GitHub / repo source audit
- 主题类型：raw alpha
- 基础 alpha：当 **Binance 全市场账户多空比** 明显比 **top trader 账户多空比** 更悲观时，说明“小账户拥挤做空”没有得到大户账户侧同幅确认；在 `SOLUSDT` 上，这种 **retail-more-short-than-top** 的负向分歧，后续 `15m / 30m / 60m` 更容易出现向上回补。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / mean-reversion / positioning-divergence / retail-vs-top-trader / sol / binance / public-data / 5m
- 证据类型：工程证据（repo source audit）+ Binance 官方 public API live probe

## 1. 这次看了什么
这次看的主材料是 GitHub 新仓库 **Co-Messi / HyperData-Terminal**（创建于 `2026-04-08`，最近更新 `2026-04-10`）。仓库本体是一个 crypto trading terminal，但对 desk 真正有价值的，不是终端 UI，而是它把一批**可免费抓、可高频更新、可直接接成 alpha 输入**的数据源先接好了。

本轮最值得拆出来的，不是 liquidation、whale、funding 那些已经在近期 digest 中被写过很多次的线，而是它的数据层里这条更朴素的 **long/short ratio collector**：

- `globalLongShortAccountRatio`
- `topLongShortAccountRatio`

也就是说，它已经把我们做 **retail-vs-top positioning divergence** 这类信号最关键的两条公开输入接通了。

## 2. 核心结论
- **一句话 base alpha：** 不要把 `global long/short ratio` 当成单纯情绪温度计；更值得测的是 **全市场账户更悲观、但 top trader 账户没那么悲观** 时，`SOLUSDT` 后续 `15m~60m` 的**向上回补**。
- **一句话策略定义：**
  - 记  
    `spread_z = z(log(globalLongShortAccountRatio), 48) - z(log(topLongShortAccountRatio), 48)`
  - 当 `spread_z < -1.5` 时，做多 `SOLUSDT`
  - 基线持有：`3 / 6 / 12` 根 `5m` bar（即 `15m / 30m / 60m`）

这条线是 **raw alpha**，不是 overlay。因为它单独就能回答：
1. 何时进场：`spread_z < -1.5`
2. 做哪边：`long SOL`
3. 持有多久：`15m / 30m / 60m`
4. 风险怎么控：阈值、止损、冷却、成本缓冲都能直接写

## 3. 为什么和当前项目有关
这条线值得进当前素材池，主要因为它补的是一个**不那么重复、但能直接落地**的短周期 mean-reversion alpha：

1. **它不是纯 filter**：可以直接给方向，且入场条件明确；
2. **它用的是完全公开数据**：Binance 公共接口即可，不依赖私有成交、付费数据或链上重 ETL；
3. **它天然适配 `5m / 15m`**：原始数据就是按 `5m` 周期更新，拿来做最小实验非常顺手；
4. **它和已有 BTC crowding 线不完全重复**：
   - 3 月 22 日那篇更像 `overlay`，且核心是 `global-vs-top position gap` 去过滤 breakout；
   - 4 月 6 日那篇更偏 `BTC fuel-cascade`，依赖 crowding + OI + fuel exit 的更复杂壳；
   - 这次更简化，也更像**单因子可落地 alpha**：只抓 **account-ratio divergence**，并优先落在当前 portability 更好的 `SOL long-only` 这条腿上。

## 3.5 策略拆解（必填）
- 方向属性：short-cycle / mean-reversion / positioning-divergence / long-only
- 基础 alpha：`retail-more-short-than-top` 后，`SOLUSDT` 向上回补
- 主题定位：**raw alpha**
- 触发条件：
  - `z_g = z(log(globalLongShortAccountRatio), 48)`
  - `z_t = z(log(topLongShortAccountRatio), 48)`
  - `spread_z = z_g - z_t`
  - 当 `spread_z < -1.5` 时，开 `long SOLUSDT`
- exit：
  - 基线版：固定持有 `6` 或 `12` 根 `5m` bar
  - desk 版：`spread_z` 回到 `>-0.5` 提前止盈；或到达最大持有 `60m` 强平
- sizing：
  - 初版按固定 notional；
  - 更稳的版本按 `|spread_z|` 分层：`1.5~2.0 / 2.0~2.5 / >2.5`
- risk：
  - 只做 `SOL` 这一条更干净的腿，先别一上来做跨资产泛化；
  - 极端波动时加价格止损与信号冷却；
  - 避免重大宏观/交易所事件窗口硬做逆势抄底
- 成本：
  - 先按 round-trip `8 bps` 粗略摩擦估计
  - 如果能吃 maker 或减滑点，真实可交易性会更好

## 4. 代码级最有价值的地方
这份 repo 的价值，不是它已经帮你写好了最终 alpha，而是它把**最有希望做成 alpha 的 positioning 输入**标准化了。

对 desk 有用的点主要是：

### 4.1 它把 `global` 和 `top-trader` 两类账户比率并列抓下来了
这很关键。很多人只看一条 `long/short ratio`，最后只能得到“市场偏多/偏空”的模糊叙事；但真正更像 alpha 的，往往不是 level，而是：

> **小账户拥挤方向，和更强账户群体方向，是否开始分叉？**

这正是 `globalLongShortAccountRatio` 与 `topLongShortAccountRatio` 组合起来的意义。

### 4.2 它提醒我们：positioning 因子真正值得测的是“谁在拥挤”，不是“市场现在看起来偏多还是偏空”
如果只盯 `global LSR`，很容易写回情绪周报；
如果改成 `global - top` 的分歧，才更像 desk 能下手的信号壳。

## 5. Binance public live probe：这条线现在有没有 alpha 壳？
我用 Binance 公共接口做了一个 **20 天、`5m` 频率、public-only** 的最小 portability probe，标的先看：
- `BTCUSDT`
- `ETHUSDT`
- `SOLUSDT`

实验口径：
- 数据：
  - `globalLongShortAccountRatio`
  - `topLongShortAccountRatio`
  - `fapi/v1/klines`
- 规则：
  - `spread_z = z(log(global),48) - z(log(top),48)`
  - `spread_z > 1.5`：代表 retail 比 top 更偏多
  - `spread_z < -1.5`：代表 retail 比 top 更偏空
- 持有窗口：`3 / 6 / 12` 根 `5m` bar

### 5.1 结果先说结论
- **BTC**：这条因子其实两边都能做，`30m / 60m` pooled gross 分别约 **`+8.65 bps / +13.55 bps`**；
- **ETH**：不干净，long side 明显拖后腿，不适合作为当前主 intake；
- **SOL**：最值得单独拎出来的是 **`spread_z < -1.5` 的 long-only 回补壳**。

### 5.2 SOL 这一腿的关键数字
当 `spread_z < -1.5`（也就是 **全市场账户显著比 top trader 更偏空**）时：

- 持有 `15m`：`n=197`，mean **`+11.04 bps`**，win rate **`61.4%`**
- 持有 `30m`：`n=197`，mean **`+13.45 bps`**，win rate **`64.0%`**
- 持有 `60m`：`n=197`，mean **`+16.29 bps`**，win rate **`54.3%`**

若先按 `8 bps` round-trip 粗略扣摩擦，仍分别约为：
- `15m`: **`+3.04 bps`**
- `30m`: **`+5.45 bps`**
- `60m`: **`+8.29 bps`**

### 5.3 阈值分层后，更像 desk 可以直接试的版本
只看 `SOLUSDT long-only` 且提高信号阈值：

- `spread_z < -2.0`
  - `30m`: `n=106`，mean **`+14.88 bps`**，win rate **`68.9%`**
  - `60m`: `n=106`，mean **`+31.01 bps`**，win rate **`64.2%`**
- `spread_z < -2.5`
  - `30m`: `n=64`，mean **`+16.14 bps`**
  - `60m`: `n=64`，mean **`+48.88 bps`**，win rate **`70.3%`**

这说明它不是“阈值越松越稳”的宽温度计，反而更像**极端负向 crowding 下的反身性回补**：信号越极端，后续 bounce 反而越像可交易事件。

### 5.4 为什么我最后锁定 SOL，而不是 BTC
BTC 这条线其实也有东西，但与本月已经积累过的 crowding / fuel-cascade / smart-money 题材更近；
`SOL long-only` 这条腿反而更像本轮新的、低重复的 intake：
- base alpha 清楚
- 规则短
- portability probe 正向
- 数据公开
- 更适合先做最小实验

## 6. 对 short-cycle desk 的正确落地方式
别把它理解成“仓位面情绪指标”。更合理的姿势是：

- **信号时钟**：每 `5m` 更新一次 spread
- **进场时钟**：信号触发当根收盘进，或下一根开盘进
- **持有时钟**：先测 `30m / 60m`
- **策略本体**：mean-reversion raw alpha
- **1m/3m 的职责**：不是重新定义因子，而是做更细的 execution / split-entry / micro-stop

## 7. 最小可复现实验（下一步怎么测）
### 7.1 先做最小策略壳
1. 每 `5m` 拉：
   - `globalLongShortAccountRatio`
   - `topLongShortAccountRatio`
   - `SOLUSDT` `5m` kline 或 bookTicker
2. 滚动算：
   - `z_g = z(log(global),48)`
   - `z_t = z(log(top),48)`
   - `spread_z = z_g - z_t`
3. 入场条件先试三档：
   - `spread_z < -1.5`
   - `spread_z < -2.0`
   - `spread_z < -2.5`
4. exit 先并行测两套：
   - **fixed-hold**：持有 `6` / `12` 根 `5m`
   - **reversion exit**：若 `spread_z > -0.5` 则提前平仓

### 7.2 第一个版本必须看的 6 个指标
- `signals / week`
- `gross mean bps`
- `net after fee/slippage`
- `win rate`
- `max adverse excursion`
- `time-to-mean-reversion`

### 7.3 第二轮必须加的现实过滤器
- `price trend veto`：若当根已是超大阴线，先分层看是否该等待一根确认
- `funding / event veto`：大事件前后单独分层
- `cooldown`：连续信号避免层层补仓变成硬接 falling knife
- `volatility bucket`：高波动 / 低波动分桶，检查 edge 是否集中在某一类 regime

### 7.4 我建议的最先落地版本
最先别做太花，直接从这版开始：
- 标的：`SOLUSDT`
- bar：`5m`
- entry：`spread_z < -2.0`
- exit：`30m` 与 `60m` 两版并行
- 成本：`8 bps` round-trip
- 风控：单笔固定风险 + `90m` 冷却

## 8. 风险与保留意见
- 这条边际当前是 **20 天 portability probe**，不是多年完整样本；要防短样本过拟合。
- `top trader` 与 `global` 都是 Binance 自己定义的账户分组，字段含义相对稳定，但仍要防接口口径变动。
- `SOL` 的 edge 目前更像 **long-only crowd-short unwind**，不代表 short side 同样成立。
- 极端趋势日里，这种逆 crowding 的均值回归壳可能会先吃较大浮亏，不能只看终值均值。
- 如果实盘只能吃 taker 且滑点偏大，阈值必须更严；`-2.0 / -2.5` 很可能比 `-1.5` 更接近可交易版本。

## 9. 一句话结论
> 这份新 repo 最值得 desk intake 的，不是 long/short ratio 看板，而是它提示了一条更可交易的 **positioning-divergence raw alpha**：当 **retail 账户比 top trader 账户更极端地偏空** 时，`SOLUSDT` 在接下来 `15m~60m` 更容易出现向上回补；先从 `spread_z < -2.0` 的 `30m / 60m` long-only 壳开始测，最合适。

## 10. 本轮产出物与路径
- 研究笔记：`research/quant_digests/2026-04-12_0440_sol-retailtop-account-divergence-alpha.md`
- live probe artifact：`reports/artifacts/literature/lsr_account_divergence_probe_2026-04-12/`
  - `summary.csv`
  - `detail.csv`
  - `metadata.json`

## 11. 来源
1. **Co-Messi** (2026). *HyperData-Terminal*. GitHub Repo.  
   - Repo URL: `https://github.com/Co-Messi/HyperData-Terminal`
   - Readable URL: `https://github.com/Co-Messi/HyperData-Terminal`
   - 关键文件：`src/data_layer/long_short_ratio.py`
   - 备注：仓库创建于 `2026-04-08`，更新于 `2026-04-10`

2. **Binance USDⓈ-M Futures Public API**（本轮 live probe 实际使用）  
   - Global Long/Short Account Ratio: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Long-Short-Ratio`
   - Top Trader Long/Short Account Ratio: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Top-Trader-Long-Short-Account-Ratio`
   - Kline / Candlestick Data: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

3. **本轮 public-only portability probe**（2026-04-12 04:30 UTC 生成）  
   - 口径：`20d × 5m × BTC/ETH/SOL`
   - 主规则：`spread_z = z(log(global),48) - z(log(top),48)`
   - 重点结论：`SOLUSDT` 的 `spread_z < -1.5 / -2.0 / -2.5` long-only 回补壳最值得继续复现
