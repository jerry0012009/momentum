# 别把这份 2026 risk-monitor repo 只读成“做市运维面板”：对 short-cycle desk，更该先接的是「OFI × liquidation-cost veto」这层 shared maker overlay，但默认黑天鹅阈值需要重标定
- 时间：2026-04-12 20:28 UTC
- 类型：GitHub repo + live public-data quick check
- 主题类型：overlay
- 基础 alpha：`不是独立方向 alpha；它服务于现有 maker raw alpha（reference-price anchored spread capture / OFI×fair-value skew / OBI quote-skew）的 execution veto 与 inventory-risk overlay`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：overlay / maker / market-making / OFI / liquidation-cost / L-VaR / inventory-risk / indifference-price / execution-veto / binance / btcusdt / 1s / 1m / 3m / 5m / repo / live-public-data
- 证据类型：repo source audit + live public-data quick check

## 1. 这次看了什么
这次主源不是再补一条新 raw alpha，而是补一层**可直接挂到现有 maker alpha 上的共享 veto**：

1. **jianingwang124 (2026), _Real-time Market Making Risk Monitor_**，GitHub repo。它把做市风险拆成 4 个很实用的实时量：`OFI(top10)`、`inventory delta`、`Avellaneda-Stoikov indifference price`、`1-minute liquidation cost`，再往上叠 `L-VaR` 与 `black swan scenario`，最后把 breach 映射成 `throttle / reduce inventory / kill-switch`。
2. 我额外用 **Binance USDⓈ-M BTCUSDT public depth(50)** 做了一个 **180 秒、1Hz** 的 live quick check，目的不是证明它“已经能上生产”，而是先回答：**这层 veto 对我们当前 `1s/1m/3m/5m` maker 线到底有没有 desk 价值，默认阈值是不是像样。**

一句话核心结论：**这份 repo 最该被 intake 的不是 dashboard，而是“把 OFI + 清仓成本 + inventory reservation drift 变成 quote-on / quote-off 开关”的那层 maker overlay；但它给的默认 tail-risk 标尺对 BTCUSDT 深盘口明显过松，黑天鹅成本函数还需要重写。**

它怎么证明这件事：**repo 里已经把指标、阈值与风险动作写成完整工程骨架；我再用 Binance live depth 做最小快检，验证这些阈值在真实盘口下是否会真正触发。**

## 2. 核心结论
- 这篇东西的 **base alpha 不是方向信号**，而是服务于现有 maker raw alpha 的**执行否决层**：当 order-flow、库存与流动性同时恶化时，先减 quote、再缩 inventory，而不是继续把 alpha 本体硬顶上去。
- 对当前 desk，最值得抄的不是整套 Streamlit/UI，而是 repo 已经明写出来的这条控制链：`OFI / indifference price / liquidation cost -> risk flags -> throttle / kill-switch`。
- 这层 overlay 直接服务至少 2 条当前主线：
  - `2026-04-12_1830_refprice-anchored-maker-shell.md`
  - `2026-04-12_1352_mm-live-ofi-fairvalue-maker-alpha.md`
  - 也能顺手接到更早的 `2026-04-11_0945_binance-obi-quote-skew-maker-shell.md`
- live quick check 显示：**思路对，默认阈值不对。** BTCUSDT 深盘口下，repo 默认 `max_liquidation_cost_usdt = 75000` 基本不可能触发；如果直接照抄，等于“写了风控，但平时根本不工作”。
- black-swan stress 的现写法也不够像真正 tail loss：它把 book 与 mark 一起 gap down，导致小仓位时 `stress_liquidation_cost` 甚至可能比 base cost 还低；这更像“深度萎缩实验”，不像完整的尾部清仓损失模型。

## 3. 关键数据点（这轮最值得记住的 4 个数）
1. **180 个快照 / 179 个 OFI transition**：Binance USDⓈ-M `BTCUSDT`，`depth=50`，1Hz，持续 180 秒。  
2. **盘口极深、spread 极窄**：样本期 median spread 只有 **0.0141 bps**。  
3. **1 分钟清仓成本（按 repo 的 top-book depth 模型）很小**：median `liq_cost` 对 **0.25 / 0.5 / 1.5 BTC** 分别约 **8.88 / 17.77 / 53.30 USDT**。这和 repo 默认上限 **75,000 USDT** 相差太远。  
4. **repo 默认 `max_abs_ofi = 50` 并非永不触发，但也很少触发**：本轮只在 **2 / 179** 次 transition 上越线；说明 OFI 阈值还算像“红灯”，但 liquidation-cost 阈值明显不像。  

补一条更关键的实现审计结论：按 repo 当前 `black_swan_scenario()` 写法，本轮 **0.25 BTC** 的 stressed liquidation cost 中位数约 **8.17 USDT**，反而**低于** base cost **8.88 USDT**。这不是市场在帮你省钱，而是 stress 函数把 mark 和执行价格一起下移，吃掉了本该体现的尾部损失。

## 4. 为什么这轮值得做它，而不是再补一条 raw alpha
先诚实回答那句内部问题：**它为什么比继续补 raw alpha 更值得？**

因为今天 raw alpha 池已经连续补了 pairs / carry / maker / relative-value 多条新线，当前更缺的不是“再来一个信号故事”，而是**把现有 maker 原型接上一层统一的 quote veto / inventory throttle**。如果没有这一层：
- `reference-price` maker shell 会在流动性抽走时继续机械挂单；
- `OFI × fair-value` maker alpha 会把强流偏与库存风险混在一起；
- 研发上会一直讨论“alpha 对不对”，但缺少一个统一回答“什么时候根本不该继续报单”的组件。

所以它虽然不是 raw alpha，但它不是泛风险闲聊，而是**直接服务当前 raw alpha 素材池里最活跃的 maker 分支**。

## 4.5 策略拆解（必填）
- 方向属性：不是方向 alpha；属于 maker execution veto / inventory-risk overlay
- 基础 alpha：`reference-price anchored spread capture`、`OFI × fair-value shift maker skew`、`OBI quote-skew`
- regime：高流动 / 低流动；order-flow 平稳 / 冲击；库存中性 / 库存偏斜
- filter / veto：`abs(OFI)` 过阈、`liq_cost(position)` 过阈、`|indifference_price - mid|` 过阈时，降档或停 quote
- risk / sizing / execution overlay：quote width 放宽、size cut、inventory unwind、kill-switch

## 5. 可复刻的最小实验
### 研究假设
对任何一个 `1s/5s/1m` maker alpha，**当 `abs(OFI)`、`liquidation_cost(position)`、`reservation drift` 同时变坏时，继续维持原 quoting aggressiveness 会显著放大 adverse selection；加 veto 后，净 markout / inventory drift 会改善，哪怕 quote-on ratio 略降。**

### 最小实验口径
直接拿现有两条 maker 原型做 replay：
1. `refprice-anchored-maker-shell`
2. `mm-live-ofi-fairvalue-maker-alpha`

对每条策略，在同一份 `depth/trade` 回放里比较两版：
- **baseline**：只按 alpha 报单
- **overlay 版**：额外加三道门
  - `abs(OFI_top10) > q90`
  - `liq_cost(position) > q90(position_bucket)`
  - `|indifference_price - mid| > k * spread`

观察 4 组指标：
- 未来 `5s / 30s / 60s` adverse markout
- inventory drift / forced unwind 次数
- quote-on ratio
- fill-adjusted pnl after fees

### 阈值怎么定
第一版**不要**照抄 repo 默认 hard limits，而是用本品种经验分位数：
- OFI：rolling `q90 / q95`
- 清仓成本：按 inventory bucket（如 `0.1 / 0.25 / 0.5 / 1.0 BTC`）分别定 `q90`
- reservation drift：按 `spread` 或 `ATR(1m)` 标准化后再设阈值

## 6. 这份 repo 最值得复用的 3 个模块
### A. `metrics.py`
最值钱的是它把 **OFI / inventory delta / indifference price / liquidation cost** 全部压成了可实时算的函数，而不是抽象风控口号。

### B. `engine.py`
它已经把 `metric -> risk_flags -> action semantics` 这条链子写出来了。对我们 desk，这比 UI 更值钱，因为它能直接接策略网关。

### C. `stress_test.py`
思路值得保留：`L-VaR + liquidity shock` 应该成为 maker 风控层的一部分；但当前实现必须重标定，不能直接当生产真值。

## 7. 风险与保留意见
- 这不是独立 raw alpha，不能把它伪装成“又发现了一条做市 edge”。它只回答**什么时候不该继续挂原来的单**。
- 我这轮 live probe 只做了 **BTCUSDT / 180 秒 / public depth**，证据强度属于 **快检**，不是完整回测。
- repo 的 `liquidation_cost_1m` 只看当前 order book 深度，不含真实 queue position、partial fill path、latency、self-impact、撤单失败；它更像实时风控 proxy，不是真实成交成本全息模型。
- 当前 `black_swan_scenario()` 对小仓位会低估尾部损失，第一版接生产前必须改。

## 8. 下一步怎么测
1. 先把这层 overlay 接到两条现有 maker alpha 的 replay，不要再单独空谈风控。  
2. 把 repo 默认 hard limits 全部改成 **symbol-specific percentile limits**。  
3. 重写 black-swan stress：不要让 mark 与执行 book 同比例平移后互相抵消，应单独保留 inventory mark-to-market 损失，再叠加流动性塌陷成本。  
4. 若 overlay 版能明显降低 adverse selection、inventory drift 和 forced unwind，再决定是否进 live shadow。  

## 9. 数据源与最小可复现实验口径
- **Repo source**：GitHub 公开仓库，源码可读，可直接复用函数定义与风险链条。
- **市场数据**：Binance public `fapi/v1/depth?symbol=BTCUSDT&limit=50`
- **公开性**：公开，无需私钥
- **更新频率**：本轮 quick check 以 **1Hz REST polling** 采样；正式最小复现建议切到 WebSocket `depth@100ms + aggTrade`
- **本轮实验文件**：
  - `/root/clawd/jerry/momentum/tmp/live_mm_risk_probe_20260412_2018.json`
  - `/root/clawd/jerry/momentum/tmp/live_mm_risk_probe_20260412_2018_summary.json`

## 10. 来源
- Jianing Wang. (2026). *Real-time Market Making Risk Monitor*. GitHub repository.  
  - Venue: GitHub  
  - DOI: N/A  
  - Readable URL: `https://github.com/jianingwang124/Real-time-Market-Making-Risk-Monitor`  
  - Repo URL: `https://github.com/jianingwang124/Real-time-Market-Making-Risk-Monitor`  
  - 关键文件：`README.md`、`src/risk_monitor/metrics.py`、`src/risk_monitor/stress_test.py`、`src/risk_monitor/config.py`、`src/risk_monitor/engine.py`
- Binance USDⓈ-M Futures public depth API.  
  - Endpoint: `https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=50`
