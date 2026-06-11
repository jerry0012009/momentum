# 别把 Hurst 只当 pairs 的二级过滤：这篇 2024 论文更该先测的是「H<0.5 + spread band」快速均值回归完整骨架
- 时间：2026-03-25 01:58 UTC
- 类型：近 5 年论文（全文 PDF）+ 近 5 年 follow-up 论文 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：跨币种配对 spread 偏离后的快速均值回归；`H<0.5` 用来把更容易“快回归”的那一段切出来
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/hurst/ghe/anti-persistence/spread-band/fast-meanreversion/cost/capacity/binance/crypto/5m/15m/1m/3m/paper
- 证据类型：全文论文证据 + follow-up 论文验证 + 本地公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“配对价差偏离后的均值回归”本体，不是单独一个 filter。**

更准确地说，`H<0.5` 在这里不是凭空产生 alpha，而是把 pairs raw alpha 里**更可能快速回归、因此更可能活过成本**的那一段切出来。对短周期 desk 来说，这很重要：pairs 最大敌人常常不是方向错，而是**回得太慢，被手续费、资金占用和并发仓位拖死**。

本轮主看：
- **Grande, Borondo, Losada & Borondo (2024, Mathematics)**：直接给了 crypto 市场的 `local Hurst + spread band` 入场/出场骨架；
- **Ramos-Requena & Bağcı (2025, Computational Economics)**：作为 follow-up，进一步说明 **GHE-based pair selection** 在 2022–2023 crypto 上相对 Distance / Correlation / Cointegration 仍有竞争力。

## 2. 核心结论
- **一句话核心结论：** 这条线最值得 intake 的，不是“再加一个 Hurst filter”，而是把它当成 **pairs raw alpha 的 fast-reversion admission layer**：当 spread 已偏离、且局部 `H<0.5` 时，回归更快，交易更短，更有希望活过成本。
- 2024 主论文不是只做 backtest 讲故事，而是先做 quasi-natural experiment：
  - Binance 数据；
  - **Top 20 cryptocurrencies**；
  - **2019-01-01 ~ 2024-06-05**；
  - **hourly frequency**；
  - treatment=`H<0.5`，control=`H>=0.5`；
  - 结论是：**对所有 tested window（1/3/5/7/10/14/21/28 天），`H<0.5` 下 spread 回到均值都显著更快（全部 p<0.001）**。
- 论文里一个对 desk 非常关键的数字：当 `TW=5 天` 时，treatment 与 control 的 **median mean-reversion speed 差约 18 小时**，有利于 `H<0.5` 那组。
- 作者后面把它直接落成完整策略：
  - entry：spread 距离均值 `1~2 std`；
  - condition：`H<0.5`；
  - exit：回到均值 / 偏离超过 `2 std` / **72h expiry**。
- 论文回测里，**所有六个版本都赚钱**；其中按 cointegration 选对、再用 `H<0.5` 触发的版本最好，表 A5 给的收益率是：
  - **Cointegration: 61.56%**
  - **MI: 42.57%**
  - **H: 38.67%**
  - **Correlation: 38.63%**
  - **DTW: 23.43%**
- 更值钱的是“交易速度”这层：论文里真正到均值的交易，**使用 `H<0.5` 触发时 median duration 约 13h；不满足 `H<0.5` 时约 22h**。翻成人话：**它先改善的是持仓时长和容量，不是自动保证赚钱。**

## 3. 为什么和当前 desk 直接相关
- 这是标准的 `pairs / relative-value / stat-arb / mean-reversion` raw alpha，不是再给主线塞一个纯解释型 overlay。
- 它直接补 desk 现在最需要的一类素材：**可独立复现、可直接写成完整策略、并且能解释成本为何可能下降**。
- 对 `1m/3m/5m/15m` 的现实映射也顺：
  - **15m**：更适合形成 spread 偏离 + local H 触发；
  - **5m**：更适合做执行切片与更细的出场；
  - **3m/1m**：只建议做执行和 fail-fast，不建议把 H 本体直接压到太细频去承受噪声。
- 这条线还有一个很适合 desk 的“旁支价值”：**它天然服务 cost / capacity 治理**。如果 raw alpha 本来就容易因持仓太久被成本拖死，那么先把“更快回归”的 pocket 切出来，本身就是实战价值。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / pairs mean reversion（market-neutral 倾向）
- 基础 alpha：`spread_t = log(P_A) - β_t log(P_B)` 偏离中枢后回归
- `β_t`：按论文口径可用**滚动波动率比**做 hedge ratio 近似
- trigger / admission：
  - `z_spread` 进入 `1~2 std` 区间
  - 同时要求 local `H<0.5`
- exit：
  - spread 回到 rolling mean
  - 或反向继续恶化超过 `2 std`
  - 或超时（论文是 **72h**）
- pair selection：
  - 论文测试了 Correlation / Cointegration / DTW / MI / Hurst / Random
  - **cointegration 选对 + H trigger** 是他们样本里的最好版本
- risk / sizing / execution overlay：
  - pair 内按 vol-balance 或 equal-risk 配仓
  - 组合层做 gross/net cap 与同时开仓上限
  - 显式纳入手续费、funding、滑点与 borrow / carry 代理成本

## 4. 论文里最值得直接偷的“完整规则”
### 4.1 数据与 spread 定义
- 标的：按 2024-06-06 CoinMarketCap 市值前 20 个 crypto
- 频率：1h
- 样本：2019-01-01 ~ 2024-06-05
- spread：
  - `s_t = log(P_A,t) - β_t log(P_B,t)`
  - `β_t = std(lr_A) / std(lr_B)`
  - 波动率窗口：**过去 30 天（720 个 hourly bar）**

### 4.2 local H 口径
- 论文用的是 **GHE（generalized Hurst exponent）**，`q=1`
- rolling window 试了：**1/3/5/7/10/14/21/28 天**
- 每次计算都只用**当前时点之前**的数据，避免未来函数
- 论文建议的折中区间是 **3~10 天**；正文后半段重点展示 **7 天**，因为它在“更快回归”和“信号数量”之间较平衡

### 4.3 入场与出场
- 入场（sell pair）：`m + 1σ < s < m + 2σ` 且 `H<0.5`
- 入场（buy pair）：`m - 2σ < s < m - 1σ` 且 `H<0.5`
- 出场：
  1. spread 回到均值 `m`
  2. spread 继续偏离、超过 `2σ`
  3. 持仓超过 **72h**

翻成人话：这不是“只要 H<0.5 就开”，而是 **spread 已经偏离**、且 **这段 spread 看起来处在 anti-persistent regime**，才去做那笔回归单。

## 5. 本地最小快检（Binance 公共数据，非论文精确复现）
我补了一个 desk 口径的最小 probe，只看“**快回归特征是否还活着**”，不直接宣称盈利：
- 数据：Binance USDT perp 公共 `15m` K 线
- 标的：`BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK`
- 样本：最近 **60 天**
- pair 数：**28**
- quick-and-dirty 口径：
  - `β` 用 3 天 rolling vol ratio
  - rolling mean / local H window 先取 **5 天**
  - max hold 先按论文思路保留 **72h**

### 5.1 结果
- 在这套 15m 快检里，`H<0.5` 只占全部有效观测的 **5.47%**，说明它天然是个**稀疏 admission layer**。
- 但一旦出现，spread 回归速度明显更快：
  - **`H<0.5`：median 回归时间 13.75h**
  - **`H>=0.5`：median 回归时间 24.0h**
- 如果直接把论文规则生硬压成“所有 pair 都做”的简化策略：
  - `H<0.5` 过滤后共得到 **1,971** 个信号；
  - median 持仓只有 **7.5h**；
  - **没有 expiry exit**；
  - 但粗糙的 spread-unit 正收益占比只有 **35.2%**。
- 对照地，不加 H 过滤时：
  - 信号数暴增到 **47,918**；
  - median 持仓升到 **19.5h**；
  - 出现 **7,398** 次 expiry exit。

### 5.2 这组快检怎么解读
- 好消息：**论文最核心的“速度优势”在当前短周期 perp 上还在。**
- 坏消息：**把它粗暴地当“盈利过滤器”是不诚实的。** 没有 pair selection、成本治理、并发上限和执行约束时，它不保证 PnL 变好。
- 所以 desk 上更合理的定位是：
  - 它首先是 **fast-reversion admission / capacity gate**；
  - 然后才是盈利层面的帮助项；
  - 想把它变成完整正期望，必须配合更好的选对、成本、组合治理。

## 6. 最小可复现实验（面向 5m / 15m）
### 6.1 公开数据源
- Binance USDⓈ-M Futures Klines（公开、无需 key）
- 可直接支持 `1m/3m/5m/15m`
- 如果后续要更贴近论文，可补现货或更大市值池

### 6.2 建议的最小实验口径
- **先做 15m 形成信号，5m 执行**
- 宇宙：8~12 个高流动 perp
- pair selection：
  1. 先用 14d correlation / distance / cointegration 选前 N 对
  2. 再对候选 pair 计算 3d / 5d / 7d local H
- entry：`1<|z_spread|<2` 且 `H<0.5`
- exit：mean / `|z|>2` / timeout（先试 24h / 48h / 72h）
- cost：先显式分层 `8 / 12 / 16 / 20 bps round-trip`
- 核心指标：
  1. `post-cost expectancy per trade`
  2. median hold / expiry ratio
  3. max simultaneous open trades
  4. pair-selection 方法切换前后，速度优势是否仍在

## 7. 下一步怎么测（必须）
1. **先把 H 从“全宇宙过滤器”缩成“候选 pair admission layer”**：只对 top-N correlation / cointegration pairs 用 `H<0.5`，别对所有 pair 乱扫。  
2. **做 `TW grid`**：把 H window 从 `3d / 5d / 7d / 10d` 跑一遍，验证论文说的 sweet spot 是否在短周期 perp 上仍成立。  
3. **做 timeout grid**：`24h / 48h / 72h` 三档，直接看持仓时长、expiry ratio、净收益的交换比。  
4. **补成本生存线**：把 funding、手续费、冲击成本一起算，不要只看 signal-level 胜率。  
5. **做组合容量实验**：记录并发开仓数，看看 `H<0.5` 是否真的像论文说的那样，能在相同风险预算下容纳更大 pair 池。  
6. **若 15m 成立，再下钻 5m 执行**：不要先把 H 本体压到 1m/3m；先让 15m 给方向和 pocket，再在更细频做切片与 fail-fast。

## 8. 风险与保留意见
- 这条线最大的误读风险是：把 `H<0.5` 当成“盈利保证器”。论文和本地快检都不支持这种偷懒读法。  
- 论文的盈利结果建立在**pair 选择 + H trigger + timeout + stop**整套闭环上；拆掉其中任何一块，都可能失真。  
- H 估计本身对窗口长度、采样频率、极端波动都敏感；压得太细，容易把噪声误判成 anti-persistence。  
- 短周期实盘里，pairs 最容易死在执行细节：换手、funding、点差、并发占用，而不是“没找到 fancy 因子”。  
- 所以这条线最诚实的 desk 定位应当是：**raw alpha 骨架 + fast-reversion admission layer**，而不是“万能 filter”。

## 9. 来源
1. **Grande, M., Borondo, F., Losada, J. C., & Borondo, J. (2024). _Anti-Persistent Values of the Hurst Exponent Anticipate Mean Reversion in Pairs Trading: The Cryptocurrencies Market as a Case Study_. Mathematics, 12(18), 2911.**  
   - Venue: Mathematics (MDPI)  
   - DOI: `10.3390/math12182911`  
   - Readable URL: `https://doi.org/10.3390/math12182911`  
   - PDF URL: `https://oa.upm.es/86488/1/10254881.pdf`

2. **Ramos-Requena, J. P., & Bağcı, M. (2025). _Analysis Pairs Trading Strategy Applied to the Cryptocurrency Market_. Computational Economics.**  
   - Venue: Computational Economics  
   - DOI: `10.1007/s10614-025-11149-y`  
   - Readable URL: `https://link.springer.com/article/10.1007/s10614-025-11149-y`  
   - Abstract signal: 文中指出 **GHE strategy 在 2022–2023 crypto 上相对 Distance / Correlation / Cointegration 持续占优，并在 OOS 中保持更优 Sharpe / Sortino / R²**。

3. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 10. 本地复现产物
- `reports/artifacts/quant_digests/hurst_pairs_antipersistence_probe_20260325_0150/metrics.json`
- `reports/artifacts/quant_digests/hurst_pairs_antipersistence_probe_20260325_0150/mr_events.csv`
- `reports/artifacts/quant_digests/hurst_pairs_antipersistence_probe_20260325_0150/strategy_signals.csv`
