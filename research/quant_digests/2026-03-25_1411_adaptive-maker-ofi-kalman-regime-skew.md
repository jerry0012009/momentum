# 别把 Avellaneda-Stoikov 只当做市教材：这份 2026 新仓库更值得先测的是「Kalman fair value + OFI skew + regime widening」maker raw alpha
- 时间：2026-03-25 14:11 UTC
- 类型：2026 GitHub 新仓库 + 经典 microstructure literature 地基 + repo 自带 benchmark / markout 证据 + 代码级参数审计
- 主题类型：raw alpha
- 基础 alpha：用 `Kalman(mid) + imbalance` 与 `OFI / microprice / vol clustering` 估计未来 `100~500ms` 的短期漂移，把这个 edge 直接映射成 skewed maker quotes；只有当未来漂移能覆盖 adverse selection 与费用时，双边做市才有净边
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/maker/market-making/avellaneda-stoikov/kalman/ofi/microprice/regime/quote-skew/inventory/adverse-selection/binance/spot/1m/3m/repo/paper/execution
- 证据类型：仓库 README/代码证据 + 经典论文地基 + 参数级 desk 审计

> 先回答 base alpha：**不是“挂双边等别人来打”这么空。base alpha 是：短期订单流与盘口结构会让未来几百毫秒的公平价格偏向某一边；如果你能把这个偏向及时体现在 reservation price、spread 宽度和 quote skew 里，maker 也能有 directional raw alpha，而不是纯手续费生意。**

## 1. 这次看了什么
这轮主线不是再写一篇“OBI 很重要”的泛泛笔记，而是直接拆一份很新的完整策略仓库：

- **Aliipou (2026), _mm-live_**, GitHub 新仓库
- 文献地基：
  - **Avellaneda & Stoikov (2008), _High-frequency trading in a limit order book_**, *Quantitative Finance*
  - **Stoikov (2018), _The micro-price: a high-frequency estimator of future prices_**, *Quantitative Finance*

对当前 desk 来说，最值得偷的不是“它会做市”这件事，而是这套**完整 raw alpha 骨架**：
1. 用 `Kalman(mid) + α·imbalance` 做 fair value；
2. 用 `OFI + microprice deviation + vol clustering` 判断 edge 朝哪边偏；
3. 用 `reservation price + adaptive spread + inventory cap + one-sided quoting` 把 edge 落成可执行报价；
4. 再用 **benchmark / markout / drawdown breaker** 验证“吃到的 spread 有没有被 adverse selection 吃回去”。

这和今天已经写过的 **single-asset taker micro alpha** 不一样：
- 那条线是“看见 edge 就直接吃单”；
- 这条线是“**让报价本身朝 edge 倾斜**”，本质上是 maker 版的 microstructure raw alpha。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值得先复现的，不是 textbook A-S 公式本身，而是 **`fair value drift → skewed quotes → markout clean`** 这条完整 maker alpha 闭环。
- **一句话证明方式：** 仓库同时给了信号预测检验、策略基准对比、markout 分析和风险开关，不只是“会挂单”的 execution skeleton。

### 2.1 仓库里最硬的 3 组数字
1. **OFI 的 edge 很短，但不是 0**：
   - `100ms`  horizon：`r = 0.12`，`R² = 0.014`，`t = 3.41`，`p = 0.0007`
   - `500ms` horizon：`r = 0.09`，`R² = 0.008`，`t = 2.61`，`p = 0.0091`
   - `1s` 之后显著性明显衰减；`5s` 基本消失

   翻成人话：**这不是 5m 慢因子，而是几百毫秒到 1 秒内衰减的 micro edge。**

2. **adaptive maker 明显优于固定宽度挂单**：
   - `AdaptiveQuoteEngine`：`142` fills，fill rate `14.2%`，`P&L +0.31`，`Sharpe 1.823`，`MaxDD 0.089`，`WinRate 54.1%`
   - `FixedSpreadMaker(±5)`：`89` fills，`P&L +0.18`，`Sharpe 0.941`
   - `NaiveMaker(±0.5)`：`201` fills，`P&L -0.22`，`Sharpe -0.612`

   这组数最重要的含义不是“做市稳赚”，而是：**同样是 maker，是否把 signal / inventory / regime 写进报价，结果差很多。**

3. **markout 没有被 adverse selection 明显打穿**：
   - `100ms`：平均 markout `+0.0031`
   - `500ms`：平均 markout `+0.0018`
   - `1s`：平均 markout `-0.0002`
   - README 给出的净 edge：**`+0.0479 USD / fill`**

   这点很关键，因为 maker 策略最常见的假繁荣就是“看起来吃到了 spread，实际上 fill 后 mid 马上朝反方向跑”。这个仓库至少把这件事单独拿出来验了。

## 3. 为什么和当前项目直接相关
- 它是 **raw alpha**，不是 filter / overlay 伪装成本体。
- 它补的是我们当前素材池里还不够多的一类：**maker-side microstructure alpha**。
- 它天然对应完整策略，而不是“某个指标很重要”的解释性材料：
  - `entry`：什么时候挂、往哪边 skew、挂多宽
  - `exit`：何时只挂单边、何时触发 TP/库存回补
  - `sizing`：inventory cap / fill qty / gross guard
  - `risk`：drawdown breaker / spread sanity / one-sided quoting
  - `cost`：maker fee + markout + latency / queue 风险
- 对当前 `1m / 3m / 5m / 15m` desk 的价值也很直接：
  - **最适合**：`1m / 3m` 高强度执行型 raw alpha
  - **次适合**：`5m / 15m` 主信号的 execution timing / maker-vs-taker 切换层

## 3.5 策略拆解（必填）
- 方向属性：单资产 / 时间序列 / microstructure / maker raw alpha
- 基础 alpha：未来超短 horizon 公平价格存在可测的方向漂移，maker 应把这个漂移写进 reservation price 与 skewed quotes，而不是围绕当前 mid 机械对称挂单
- 核心信号：
  - `fair_value = Kalman(mid) + α · imbalance`
  - `edge_score = w1·OFI + w2·microprice_dev + w3·vol_urgency`
  - `reservation = fair_value - inventory · γ · σ² · T`
- 报价逻辑：
  - 正常状态：双边挂单
  - `imbalance > 0`：**tighten ask / widen bid**（偏向卖给买方 aggressor）
  - 高波动：spread widen
  - 达库存上限：只挂能减仓的一边
- sizing：
  - 先固定 `fill_qty`
  - 再按 `|edge_score| / σ / spread_state` 做 quote aggressiveness 分层
- risk：
  - `max_inventory_btc`
  - `max_drawdown_usd`
  - `max/min_spread`
  - 盘口漂移太快或 latency 异常时停更/停机
- cost：
  - maker fee / rebate
  - adverse selection（必须看 markout，不可只看 spread capture）
  - queue position / quote-to-fill delay / quote cancel 节流

## 4. 代码级 desk 读法：它默认更像「spread floor + skew + inventory」系统，不完全是 textbook A-S
这份 repo 最有价值的一点，是 README 之外还能做 **代码级 sanity check**。

### 4.1 一个值得先记下的小细节
README 里写的是 textbook A-S 半价差：
`δ = γσ²T/2 + (1/γ) ln(1 + γ/k)`

但仓库 `quoting.py` 实现的是：
`base_delta = γσ²T/2 + (1/k) ln(1 + γ/k)`

这两者不是一回事。
在默认参数 `γ=0.05, k=1.5, T=600` 下：
- textbook 常数项约 **`0.6558`**
- 仓库实现常数项约 **`0.0219`**

同时仓库还设了 `min_half_spread = 0.5 USD`。
我按代码把默认参数扫了一遍，得到一个很关键的 desk 结论：

- 当 `sigma < ~0.1785` 时，**实际 half-spread 基本被 `0.5 USD` 的 floor 钉住**；
- 也就是说在大量正常波动时段，这个系统的实盘行为更像：
  - **固定最小价差**
  - + `imbalance skew`
  - + `inventory pressure`
  - + `high-vol regime widen`

而不是一个由 A-S 理论项完全主导的连续最优 spread 模型。

这反而更符合 desk 现实：**很多时候真正起作用的不是 textbook 闭式解，而是 floor、skew、inventory、throttle 这些“脏工程参数”。**

### 4.2 这意味着什么
- 第一，**repo 很适合做工程型完整策略 intake**，不适合当“原论文一字不差 faithful replication”。
- 第二，若要 live / paper-trade，**先确认 spread 公式到底是故意改写还是实现偏差**；否则参数调优会被错误解释。
- 第三，对 desk 来说，这个 repo 的最佳拆法不是“迷信 A-S”，而是：
  1. 保留 quote floor；
  2. 明确 skew 来自哪些 micro alpha；
  3. 再测 inventory / regime / throttle 是否真的改善 post-cost fill quality。

## 5. 与当前短周期（1m / 3m / 5m / 15m）的关系
### 5.1 最适合的位置
- **`1m / 3m`：** 可直接当独立 maker alpha / execution alpha
- **`5m / 15m`：** 更适合当 execution layer，而不是主 bar-close alpha

原因很简单：仓库给出的 edge 有效窗口主要在 `100ms ~ 500ms`，到 `1s` 以后已经开始衰减。它不是天然 15m 主信号。

### 5.2 对 5m / 15m desk 最实用的读法
如果你已经有一个 `5m` 或 `15m` 主方向信号，这条 maker alpha 最值钱的用法可能是：
1. **决定先 maker 还是直接 taker**；
2. **当 micro edge 与大周期方向相反时，延迟入场 / 降低报价尺寸**；
3. **在 inventory 已偏、spread 已宽、markout 变差时，暂停继续补单。**

也就是：它既可以独立作为快节奏 alpha，也可以作为慢周期 alpha 的 execution veto / timing layer。

## 6. 最小可复现实验（面向 1m / 3m / 5m / 15m）
### 6.1 数据源与公开性
- 数据源：**Binance Spot / Futures 公共 WebSocket** `bookTicker` + `trade` streams
- 公开性：公开可得，无需私钥（只做行情采集时）
- 更新频率：事件驱动，毫秒级
- 最小可复现实验口径：自采 `2~6` 小时即可；先不用私有成交回报，也能先做信号预测与 paper fill 检验

### 6.2 最小实验设计
1. **标的**：先跑 `BTCUSDT / ETHUSDT / SOLUSDT`
2. **采样**：连续采集 `2~6h` 的 `bookTicker + trade`
3. **最小信号**：先只保留 `imbalance / OFI / microprice_dev / relative_spread`
4. **先做 2 类检验**：
   - `OFI -> future mid return` 回归（`100ms / 500ms / 1s`）
   - 自适应 maker vs fixed spread vs naive maker 三路 benchmark
5. **最先看 5 个指标**：
   - `r / t-stat / p-value`（预测性）
   - `P&L / Sharpe / MaxDD`
   - `fill rate`
   - `avg markout`
   - `net edge per fill`

### 6.3 先不要做的事
- 先不要一上来加深度学习
- 先不要跨很多 symbol 扫 universe
- 先不要把秒级 edge 粗暴压成 `15m` 因子再宣称它是 bar alpha

## 7. 下一步怎么测（必须）
1. **先做 paper-fill benchmark，不要直接 live。** 先把 `adaptive vs fixed vs naive` 三组结果在本地自采数据上跑通。  
2. **把 markout 做成 hard gate。** 若 `100ms/500ms` markout 变负，就算 spread capture 看起来漂亮，也先判死。  
3. **专门测“floor 主导还是 A-S 主导”。** 先做 `min_half_spread × gamma × k × sigma regime` 网格，确认策略收益到底来自哪一层。  
4. **把 queue / cancel 节流单独测。** maker 策略最容易纸上繁荣，实盘里却死在 cancel 限速和 queue ranking。  
5. **对 1m/3m 与 5m/15m 分开定位。** 前者看独立 micro alpha；后者看 execution timing / maker-vs-taker 切换，别混成一个指标。  
6. **补一轮资产分层。** BTC/ETH 先看是否 edge 更薄但稳；SOL / midcaps 再看是否 fill 更多但 adverse selection 更重。  
7. **先核对 spread 公式实现。** 如果 `1/k` 不是刻意改写，修正后要重做全套 benchmark，避免对参数含义产生错觉。  

## 8. 风险与保留意见
- 这份 repo 的证据主要来自 README benchmark 与代码结构，不等于严格审稿级 live PnL 证明。  
- maker alpha 的最大敌人通常不是方向预测误差，而是 **queue position / latency / stale quote / cancel throttle**，这些在回测里最容易被低估。  
- 这条 edge 衰减极快；如果基础设施跟不上，alpha 很可能在“知道正确方向”时仍赚不到钱。  
- 若把它硬翻译成 `5m/15m` 主信号，大概率会失真；更诚实的定位是 **micro alpha / execution alpha**。  
- 代码里的 A-S spread 项与 README 公式存在差异，这在 live 前必须先说清楚。  

## 9. 来源
1. **Aliipou. (2026). _mm-live_. GitHub repository.**  
   - Repo URL: `https://github.com/Aliipou/mm-live`  
   - Readable URL: `https://github.com/Aliipou/mm-live`  

2. **Avellaneda, M., & Stoikov, S. (2008). _High-frequency trading in a limit order book_. Quantitative Finance, 8(3), 217–224.**  
   - DOI: `10.1080/14697680701381228`  
   - Readable URL: `https://doi.org/10.1080/14697680701381228`  

3. **Stoikov, S. (2018). _The micro-price: a high-frequency estimator of future prices_. Quantitative Finance, 18(12), 1959–1966.**  
   - DOI: `10.1080/14697688.2018.1489139`  
   - Readable URL: `https://doi.org/10.1080/14697688.2018.1489139`  

4. **Binance Developers. Spot / Futures WebSocket market streams.**  
   - Readable URL: `https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams`  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams`

## 10. 本轮产物
- `reports/artifacts/quant_digests/mm_live_maker_alpha_20260325_1411/source_metrics.json`
- `reports/artifacts/quant_digests/mm_live_maker_alpha_20260325_1411/source_metrics.md`
