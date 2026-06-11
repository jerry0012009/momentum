# 别把 `martin-binance` 只读成 martingale 老梗：对 crypto short-cycle desk，更该先测的是「bounded-bounce reverse-grid × ADX/DI trend veto × fee-aware TP」这条完整 raw alpha
- 时间：2026-04-03 21:03 UTC
- 类型：2021-2026 GitHub repo source audit（GitHub API metadata + `README.md` + GitHub Wiki `Trade-idea.md` / `Back-testing-and-parameters-optimization.md` + `martin_binance/params.py` + `martin_binance/templates/cli_0_BTCUSDT.py` + `martin_binance/executor.py` + `CHANGELOG.md`）
- 主题类型：raw alpha
- 基础 alpha：**局部大幅偏离后的“先回一口气”型 bounded mean reversion**；repo 真正值得 desk intake 的，不是“martingale 会不会发财”，而是 `reverse-grid bounce shell + fee-aware take-profit + multi-frame ADX/DI 趋势否决` 这条完整短周期均值回归母板
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / mean-reversion / single-asset / reverse-grid / bounded-bounce / fee-aware-tp / adx-di-veto / bollinger-width / adaptive-grid / maker-first / spot / perp-port / 1m / 3m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：成熟维护中的开源 repo + 可回放 websocket backtest / optuna 优化框架 + 明确参数语义；但**不是**已发表论文实证，结论更接近工程型高信号假设

**先回答 base alpha：这篇东西的 base alpha 很清楚——不是“自动化下单框架”，也不是“参数优化器”，而是一个完整的短周期 raw alpha：当价格短时间内偏离本地平衡区过远时，先赌一段回摆而不是一把梭哈单边延续；只有在趋势没坏到危险区时，才允许开新的回摆循环。**

## 1. 这次看了什么
这次选它，不是因为我们缺“martingale 教程”，而是因为当前 raw alpha 素材池里虽然已经补了不少 pairs / carry / maker / cross-market，但**这种带完整壳的单资产 bounded mean reversion 母板**反而值得再收一条成熟工程实现。

它符合当前 bot7 的优先级：
- **raw alpha 本体清楚**，不是纯 filter / overlay；
- **entry / exit / sizing / risk / cost** 一次写齐；
- 能直接压到 `1m / 3m / 5m / 15m` 做最小实验；
- 和最近 desk 已 intake 的趋势、pairs、carry 线形成互补，而不是继续围着同一种 breakout / retest 内循环。

一句话核心结论：

> 这份 repo 真正值得抄的，不是“加仓网格”本身，而是**用局部带宽决定进场深度、用 fee-aware TP 定义出场、再用多周期 DI/ADX 去否决最危险的逆势抄底**这一整套 short-cycle mean-reversion 框架。

一句话说明它怎么证明：

> 证据主要来自 repo 的**真实工程实现 + websocket 回放回测 + 参数优化框架 + 新近持续维护**，不是学术论文的跨样本显著性结论，所以我们该把它当成**高信号可复现候选**，而不是已验证真理。

## 2. 主来源与最值得看的地方
### 2.1 主来源
1. **Jerry Fedorenko / DogsTailFarmer (2021-2026), _martin-binance_**  
   - Venue：GitHub  
   - DOI：N/A  
   - Readable URL：<https://github.com/DogsTailFarmer/martin-binance>  
   - Repo URL：<https://github.com/DogsTailFarmer/martin-binance>

2. **GitHub Wiki: _Trade idea_**  
   - Readable URL：<https://github.com/DogsTailFarmer/martin-binance/wiki/Trade-idea>

3. **GitHub Wiki: _Back-testing and parameters optimization_**  
   - Readable URL：<https://github.com/DogsTailFarmer/martin-binance/wiki/Back-testing-and-parameters-optimization>

4. **Repo changelog (`3.1.0`, 2026-03-08)**：新增 `Trade Control`，把多时间框架 ADX / DI 趋势否决正式接进策略入口。

### 2.2 这份 repo 为什么算高信号而不是纯 demo
GitHub API metadata 给出的信号不差：
- `224` stars，`56` forks，MIT license；
- 创建于 `2021-12-09`；
- 最近一次 push 是 `2026-04-03`，不是废弃仓库；
- 支持 `Binance / Bitfinex / Huobi / OKX / Bybit` spot；
- 自带 `Trade & Collect / Simulate / Self-Optimization` 三套流程，不只是 README 讲故事。

翻成人话：

> 这不是“发帖吹收益”的一次性脚本，而是一套作者持续维护、能录 websocket、能做回放、能跑 optuna 的交易系统。哪怕最终 alpha 不适合 production，也值得当研究母板拆件。

## 3. repo 里真正可搬走的完整策略骨架
### 3.1 进场：不是无脑抄底，而是“偏离有多大，就布多宽的网格”
`set_trade_conditions()` 的核心逻辑很值得学：
- 用 Bollinger Band 估本地可回摆的价格带宽；
- 对 buy cycle，用 `base_price` 到下轨 `bbb` 的距离决定 `over_price`；对 sell cycle，用上轨 `tbb`；
- `over_price` 再反推 `order_q`（网格层数）和首笔下单量；
- 当 `ADAPTIVE_TRADE_CONDITION=True` 时，`ORDER_Q / OVER_PRICE` 实际上是在控制**网格密度**，而不是写死“跌 x% 就买”。

默认模板参数也很直白：
- `PROFIT = 0.15%`
- `PROFIT_MAX = 0.85%`
- `OVER_PRICE = 0.6%`
- `ORDER_Q = 12`
- `MARTIN = 10%`
- `KBB = 2.0`

这套写法对 desk 有价值的地方在于：

> 它把“做均值回归”从一个单点阈值信号，变成了**一条随局部波动宽度自适应展开的离散库存曲线**。

### 3.2 出场：TP 不是拍脑袋，而是显式补 fee 后再留利润
repo 的 take-profit 逻辑非常 desk-friendly：
- TP 会在每次网格成交后重算；
- 先补 maker / taker fee，再要求一个最小利润；
- 当持仓被更深一层网格摊薄后，TP 价格会自动往均价靠近，意味着只要回摆一小段就能平掉这轮库存。

Wiki 说得很白：**每次 grid fill 后，TP 更接近 grid 均价，因此不需要价格完全回到起点，只要回一口气就能出。**

这正是它的 base alpha：

> 不是赌 V 字完全反转，而是赌“过度偏离之后，哪怕只回一小段，也够把库存卸掉并覆盖成本”。

### 3.3 趋势否决：这份 repo 最值得 desk 单独拆出来的旁支想法
`3.1.0` 新加的 `Trade Control` 很关键，因为它承认了 martingale / reverse-grid 最大的死因：**在单边趋势里逆势接飞刀**。

repo 的处理方式不是简单加一句“别在强趋势里交易”，而是把它写成一个明确可复现的 gate：
- `TC_K = {'1m': 1.0, '15m': 2.0, '1h': 0.5}`：多时间框架 DI 差值加权；
- `TC_ADX_DATA_LIMIT = 60`
- `TC_ADX_PERIOD = 14`
- `TC_DI_DIFF = 5`
- `trade_control()` 会在 `last_diff <= 0` 时阻止新的 buy cycle；
- 当样本足够时，再对 `adx_di_avg_delta` 跑 **Mann-Kendall trend test**；只有趋势改善、且恶化程度不再太深时才放行。

翻成人话：

> 这不是“ADX > 25 就别做”那么粗糙，而是看**1m / 15m / 1h 的方向性合成后，到底还在往更坏的方向滑，还是已经出现拐头修复**。

对我们 desk 来说，这个旁支想法甚至可以脱离 repo 独立复用：
- 给单资产 MR 做 veto；
- 给 pairs / basis 的逆向腿做 admission gate；
- 给 maker inventory skew 做开新库存的阻断器。

### 3.4 参数优化告诉我们：先优化“带宽与利润目标”，不是先迷信 martingale 倍数
Wiki 放了一个 `50` trial optuna 例子，参数重要性排序是：
- `PROFIT_MAX`：`0.3246`
- `KBB`：`0.2650`
- `MARTIN`：`0.1179`
- `LINEAR_GRID_K`：`0.0789`
- `OVER_PRICE`：`0.0780`
- `SHIFT_GRID_DELAY`：`0.0705`

这个排序挺有启发：

> 真正更敏感的，不是“加仓倍率再放大一点”，而是**你给这轮库存多宽的回摆空间、以及你要求多高的利润回吐才肯走**。

这也支持我们做更 desk-friendly 的改写：**可以把原 repo 的激进 martingale 降掉，但保留 adaptive width + fee-aware TP + trend veto 这三件核心资产。**

## 4. 对 crypto short-cycle desk 的正确翻译
### 4.1 这条线的 desk 版命名
如果把它写进当前研究池，我会这样命名：

**`bounded-bounce reverse-grid × ADX/DI trend veto`**

比起笼统写成“martingale grid”，这个名字更准确，因为真正值得复现的是：
1. **bounded bounce**：赌的是短周期先回一口气；
2. **reverse-grid**：用分层限价库存吃回摆，而不是一把 all-in；
3. **trend veto**：明显单边时不许新开逆向库存；
4. **fee-aware TP**：出场定义里直接含成本。

### 4.2 它服务于哪类 raw alpha
这条线显然属于：
- **single-asset mean reversion raw alpha**；
- 也能作为更宽泛的 **inventory-based mean reversion shell**；
- 如果做成多标的轮换，也可扩成 `cross-sectional loser bounce` 的执行壳。

### 4.3 它和我们默认 `1m / 3m / 5m / 15m` 的关系
这份 repo 天然适合压到短周期：
- `1m`：执行层与库存展开；
- `3m / 5m`：主信号层，最适合作为第一轮实验基线；
- `15m`：更稳健的宽带版本，用于看 trade count / cost 后是否仍活。

我不建议一上来就完整照搬 spot-only 原版，而是建议做一个 **perp/spot 通用、但去杠杆化的最小版本**。

## 5. 最小实验怎么做
### 5.1 先做一个“去 martingale 化”的保守版
先别复制原 repo 的完整 reverse cycle，而是做一个更适合 desk 审核的最小版本：

- 标的：`BTC / ETH / SOL`
- 频段：`5m` 主实验，`15m` 稳健对照，`1m` 用于 execution replay
- 信号：
  - 计算 `20 x 60m` 或等价的高层 Bollinger 带宽，得到本地偏离区；
  - 当 `5m` 收盘穿下局部下轨、且 `weighted_DI_diff` 不显著恶化时，允许开 long MR；
  - 当 `5m` 收盘穿上局部上轨、且反向版本的 DI 条件允许时，允许开 short MR。
- 建仓：
  - `3~5` 档限价梯度，不做无限加仓；
  - 每档仓位可用 `1.0 / 1.25 / 1.5 / 1.75 / 2.0` 这种**上限明确**的轻几何，不直接照搬高倍 martingale。
- 出场：
  - TP = `inventory VWAP + fees + 10~20bps`；
  - 或到达中轨 / 半带宽先走；
  - time-stop 设 `30m / 60m / 90m` 三档。
- 风控：
  - hard stop = `1.2~1.5 x max_grid_width`；
  - 若 `ADX` 快速上冲、或 `weighted_DI_diff` 再次恶化，则强制停止开新层。

### 5.2 第一轮最应该看的 4 个指标
1. **TP hit rate**：这条 alpha 的核心不是大赚，而是“小回摆是否经常足够覆盖成本”；
2. **worst ladder depth**：到底经常吃到第几档；
3. **time-to-flat**：库存多久能卸掉；
4. **trend-veto 前后对比**：不开 gate 时是不是死在单边行情里。

### 5.3 friction ladder 要怎么加
这条线对成本特别敏感，所以第一轮就该加：
- maker-only 理想值；
- maker+taker 混合值；
- taker-worst-case；
- 再单独记录 `missed fill` 和 `partial fill`。

如果只有 maker 理想值赚钱，而 taker-worst-case 直接死，这条线就更适合做：
- 低频库存回补；
- maker-first execution shell；
- 或只保留它的 **trend veto / adaptive width** 作为共享组件。

## 6. 我对这条线的判断
### 值得复用 / 学习 / 复现的部分
最值得搬走的是这 3 个部件：
1. **adaptive width**：用局部带宽决定网格展开范围；
2. **fee-aware TP**：把“回一小口也能平”写成明确出场公式；
3. **multi-frame DI veto**：逆向库存只有在方向恶化放缓时才开。

### 不建议原样照搬的部分
- **高倍 martingale 本体**：production 风险太大；
- **spot-only 假设**：需要重写成 perp/spot 都能评估 funding 与库存成本；
- **“最终一定回”叙事**：研究时必须接受有些 regime 根本不回，时间止损与结构止损要前置。

### 当前 verdict
我的判断是：

> 这不是一条可以直接上线的 production alpha，但它绝对是**值得 intake 的 raw alpha 母板**；尤其是 `adaptive width + fee-aware TP + DI/ADX veto` 这三个组件，完全够资格进入当前短周期复现池。

## 7. 下一步怎么测（最重要）
### A. 先做 baseline replication
在 `momentum` 里先落一个 `bounded_bounce_grid` 原型：
- `5m` 信号、`1m` 执行；
- `BTC / ETH / SOL` 三币；
- `3` 档和 `5` 档两组；
- maker / mixed / taker 三档成本。

### B. 明确做三组对照
1. **No gate**：只有带宽进场，不加趋势 veto；
2. **DI veto**：加 repo 的 `weighted_DI_diff` 思路；
3. **DI veto + capped ladder**：再把仓位扩张上限卡死。

如果第二组明显降低深层库存和尾部回撤，而 trade count 没塌，就说明 repo 里最值得抄的并不是 martingale，而是 **trend veto**。

### C. 再决定它最终归宿
根据 first verdict，把它归到三种结果之一：
- **能活**：保留为独立单资产 MR sleeve；
- **alpha 一般但 gate 很强**：抽出 `DI/ADX veto` 变共享过滤器；
- **成本后不活**：只保留 `adaptive TP / inventory logic` 给 maker 或 pairs 库存管理层复用。

## 8. 来源
1. **Fedorenko, Jerry (aka VM) / DogsTailFarmer (2021-2026). _martin-binance_. GitHub repository.**  
   Venue: GitHub  
   DOI: N/A  
   Readable URL: <https://github.com/DogsTailFarmer/martin-binance>  
   Repo URL: <https://github.com/DogsTailFarmer/martin-binance>

2. **Fedorenko, Jerry. _Trade idea_. GitHub Wiki for martin-binance.**  
   Venue: GitHub Wiki  
   DOI: N/A  
   Readable URL: <https://github.com/DogsTailFarmer/martin-binance/wiki/Trade-idea>

3. **Fedorenko, Jerry. _Back-testing and parameters optimization_. GitHub Wiki for martin-binance.**  
   Venue: GitHub Wiki  
   DOI: N/A  
   Readable URL: <https://github.com/DogsTailFarmer/martin-binance/wiki/Back-testing-and-parameters-optimization>

4. **`CHANGELOG.md` (`v3.1.0`, 2026-03-08; `v3.1.3`, 2026-04-03)** for `martin-binance`.  
   Readable URL: <https://github.com/DogsTailFarmer/martin-binance/blob/master/CHANGELOG.md>
