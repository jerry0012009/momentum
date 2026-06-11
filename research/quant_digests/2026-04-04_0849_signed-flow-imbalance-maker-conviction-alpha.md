# 别把这份 OBI repo 只读成“order book 机器学习”：对 short-cycle desk，更该先测的是「1m signed trade imbalance × 5m forward return × maker-only conviction gate」这条 raw alpha——但 15bps 阈值大概率过高

- 时间：2026-04-04 08:49 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/data_integration.py` + `src/feature_engineering.py` + `src/model_training.py` + `src/backtester.py`）+ Binance 公共 aggTrades 最小便携性快检（2024-12-01 ~ 2024-12-03 BTCUSDT）
- 主题类型：raw alpha
- 基础 alpha：**分钟级主动买卖盘失衡（更准确说是 signed trade imbalance，而不是严格 L2 order-book imbalance）会对未来 `5m` 收益产生短周期预测力；只在预测净边际显著大于成本时开仓。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/order-flow/signed-trade-imbalance/aggressor-flow/5m-forward-return/maker-only/conviction-threshold/xgboost/binance-spot/btc/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 源码证据 + 公共数据最小便携性快检

## 1. 这次看了什么

这轮我没有继续补 pairs / carry / breakout，而是刻意补一条 **更底层的 microstructure raw alpha**：

> **分钟级 signed flow / 主动买卖方向失衡，能不能直接变成 `1m -> 5m` 的短周期可交易 alpha？**

主材料是一个 2026 的公开 GitHub repo，但我先说结论：

> **这份仓库值得 intake 的地方，不是 README 里那句“order book imbalance 很强”；而是它把一条可独立复现的 `1m signed-trade-imbalance -> 5m forward return` 策略壳写得很清楚。**

同时，也必须先把一个容易误读的点挑出来：

- README 把它描述成 **Order Book Imbalance (OBI)**；
- 但源码实际抓的是 **Binance public aggTrades**；
- 真正做出来的核心特征，是 **基于 aggressor side 的 signed trade imbalance / buy-sell volume imbalance**；
- 这和严格意义上用 L2 bid/ask 深度算出来的 OBI，不是一回事。

所以这轮最值得写的，不是“OBI 机器学习 repo”，而是：

> **别把 repo 的 headline 当结论；真正可复现的 base alpha，是 `signed trade imbalance`，不是 L2 depth imbalance。**

## 2. 先回答最重要的一句：base alpha 是什么？

一句话版：

> **base alpha 就是：当过去 1 分钟里主动买盘明显压过主动卖盘时，接下来约 5 分钟收益更偏正；反之亦然。**

翻成人话：

- 如果最近这一分钟，成交更像是“追着买”的盘在主导；
- 而不是被动等着成交；
- 那接下来几分钟价格更容易延续同方向；
- 但这个 edge 很薄，必须靠 **阈值、成本过滤和执行方式** 才能活下来。

这也是为什么这轮仍然值得放进研究池：

1. **它是 raw alpha，不是 filter / regime / overlay。**
2. **它和当前 desk 的 `1m / 3m / 5m` 很贴近。**
3. **它补的是目前 digest 池里相对少的“成交流 / microstructure 原始 alpha”方向。**
4. **它天然可以进一步分叉：**
   - 直接当独立 alpha；
   - 或者降级成别的 alpha 的 execution / adverse-selection gate。

## 3. 主 repo 到底是什么

### 3.1 主材料
- **Author / Repo owner**：`tsuithomas`
- **Year**：2026
- **Title / Repo**：*Cryptocurrency Statistical Arbitrage & Microstructure Alpha Research*
- **Venue**：GitHub repository
- **DOI**：无
- **Readable URL**：<https://github.com/tsuithomas/crypto_research_order_book_imbalance>
- **Repo URL**：<https://github.com/tsuithomas/crypto_research_order_book_imbalance>
- **GitHub metadata**：created `2026-03-03`；pushed `2026-03-03`

### 3.2 这次核对的源码
- `README.md`
- `src/data_integration.py`
- `src/feature_engineering.py`
- `src/model_training.py`
- `src/backtester.py`

### 3.3 数据源
repo 用的是：
- **Binance public aggTrades daily archive**
- URL 模式：<https://data.binance.vision/data/spot/daily/aggTrades/BTCUSDT/>
- 公开可得：**是**
- 更新频率：**日归档**；若要 live，可再切 Binance WebSocket aggTrade 流
- 最小可复现实验口径：**BTCUSDT 1 分钟 buy/sell 主动成交量失衡 -> 未来 5 分钟收益**

## 4. repo 真正复现出来的，不是 L2 OBI，而是 signed trade imbalance

### 4.1 数据抓取层已经决定了它不是真 L2 OBI
`src/data_integration.py` 明确抓的是：
- Binance public **aggTrades**
- 字段里有 `price / quantity / timestamp / is_buyer_maker`
- **没有任何 bid/ask depth ladder**

这意味着：
- 它拿不到盘口各档挂单深度；
- 因此不能做严格意义的 book-depth OBI；
- 只能根据 `is_buyer_maker` 去拆主动买 / 主动卖量。

也就是：

> **源码里的核心特征，其实更像 signed trade imbalance / aggressor-flow imbalance，而不是 order-book depth imbalance。**

### 4.2 核心特征怎么构造
`src/feature_engineering.py` 做了 4 件事：

1. 读入每日 aggTrades
2. 聚合到 `1min`
3. 计算：
   - `buy_vol`
   - `sell_vol`
   - `obi = (buy_vol - sell_vol) / volume`
4. 预测目标：
   - `target_fwd_return = log(close[t+5] / close[t])`

也就是非常干净的一条线：

- **信号频率：1 分钟**
- **预测窗口：5 分钟**
- **核心特征：最近 1 分钟 signed flow imbalance**

### 4.3 模型层并不复杂
`src/model_training.py` 用的是：
- `obi`
- `volume`
- `buy_vol`
- `sell_vol`
- `volatility_20`

再喂给一个：
- `XGBRegressor`
- `80/20` 时间顺序切分

这点对我们很重要：

> **repo 的可复现核心，不依赖神秘大模型，也不是几十个外部因子；就是一个非常朴素的 minute microstructure alpha 壳。**

## 5. 为什么这条线对当前 desk 有价值

先回答一句必须回答的话：

> **它为什么比继续补一个 filter 更值得？因为它本身就是可独立复现、可直接落地的 raw alpha。**

而且它补的是当前素材池里相对稀缺的方向：

- 不是又一篇 pairs z-score；
- 不是又一篇 funding / basis；
- 不是又一篇 breakout / EMA shell；
- 而是 **成交流主导的短周期 alpha**。

这条线尤其适合：
- `1m / 3m / 5m` 原生 alpha sleeve；
- `15m` 体系里的 microstructure veto / execution gate；
- 以及未来和 microprice / L2 OBI / queue imbalance 做增量对照。

## 6. repo 给了哪些“完整策略”要素

### 6.1 Entry
`src/backtester.py` 的 admission 很明确：

- 只有当 `predicted_return > +0.0015` 时做多
- 只有当 `predicted_return < -0.0015` 时做空

即：
- **预测未来 5 分钟净收益 > 15bps 才开多**
- **预测未来 5 分钟净收益 < -15bps 才开空**

这说明 repo 不只是说“有一点预测力”；而是明确把它写成：

> **必须过一个成本之后仍然足够厚的 conviction gate，才允许入场。**

### 6.2 Exit
源码里最简单：
- 信号按 `5m` 前瞻收益做
- 收益按下一根开始持有
- 若无强反向信号，允许短暂 `ffill(limit=1)`，减少 whipsaw

翻成人话：
- 这是一条 **超短 holding period** 策略；
- 默认 exit 就是 **预测窗口结束 / 信号衰减**；
- 不是隔夜，不是长持。

### 6.3 Sizing
repo 没有复杂 sizing，但这不妨碍它可落地：
- 第一版完全可以等权 / 定额 notional
- 第二版再改成：
  - `predicted_return / realized_vol` 缩放
  - 或 `minute volume percentile` 限仓

### 6.4 Risk
repo 隐含的几层 risk 很清楚：
- 通过 `15bps` admission 减少噪音交易
- 通过 `1bps maker fee assumption` 保留成本空间
- 通过 `limit=1` 防止 1 分钟级来回反手

但真正风险在于：
1. **信号很薄**
2. **taker 成本一抬，edge 可能直接没了**
3. **maker 能否成交，是实盘生死线**
4. **把 signed trades 误认成 L2 OBI，会高估信息含量**

### 6.5 Cost
repo 在 `backtester.py` 里默认：
- `threshold = 0.0015`（15 bps）
- `fee = 0.0001`（1 bp，maker 假设）

这里最值钱的不是数字，而是 repo 明确承认：

> **这条信号如果要活，必须依赖低成本执行；用 taker 乱打，大概率直接死。**

## 7. repo 自己给出的几个关键数据点

根据 README：

1. **OBI / microstructure 相关特征约占 ~45% feature importance**
2. 在其回测设定里，**maker-only + 15bps threshold** 后，策略净收益约 **+3.21%**
3. 同期 buy-and-hold 市场回报约 **-12.76%**

但这些数字只能算：
- **repo claim / repo-internal result**
- 还不能直接当 desk 结论

原因很简单：
- README 把 signed trade imbalance 叫成了 OBI；
- 没有真正 L2 深度对照；
- 样本、模型、阈值、执行假设都可能让结果很脆弱。

所以这轮我额外做了一个最小便携性 sanity check。

## 8. 最小便携性快检：public BTCUSDT aggTrades 上，这条线到底有多厚？

我额外跑了一个极简复核：

- 数据：**Binance public BTCUSDT spot aggTrades**
- 时间：**2024-12-01 ~ 2024-12-03 UTC**
- 频率：`1m`
- 目标：未来 `5m` log return
- 工件路径：
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/obi_btc_20241201_20241203/summary.json`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/obi_btc_20241201_20241203/rf_summary.json`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/obi_btc_20241201_20241203/rf_backtest_summary.json`

### 8.1 线性 sanity check：单靠这条信号，15bps admission 基本太高
线性模型结果：

- `corr(obi, fwd_5m) = 0.0736`
- `coef_obi = 0.000149`
- 预测收益 `q99 = 1.08 bps`
- 预测收益 `q99.9 = 1.61 bps`
- 按 repo 的 `15bps threshold`：**0 笔交易**

这说明什么？

> **如果只把它当一条“线性的单因子 signed-flow alpha”，repo 里的 15bps conviction gate 大概率过高。**

也就是说：
- 这条线不是完全没信息；
- 但它离“直接稳定吐出 15bps 级别预测”还差得很远。

### 8.2 浅层非线性 sanity check：能做出交易，但稳定性很可疑
我又做了一个浅层 Random Forest 快检，结果是：

- `q99(predicted_return) = 32.24 bps`
- `q99.9(predicted_return) = 36.98 bps`
- 用 repo 的 `15bps threshold`，测试窗里有 **9 笔交易**
- 这 3 天小样本里策略收益约 **+4.05%**，市场约 **+3.13%**

但更关键的是：

- `OOS R² = -0.0468`
- feature importance：
  - `volatility_20 = 54.0%`
  - `buy_vol = 14.7%`
  - `sell_vol = 11.5%`
  - `volume = 11.0%`
  - `obi = 8.7%`

这说明：

> **一旦换成小样本 portability probe，这条策略虽然“能回测出几笔赚钱交易”，但主导特征已经不是 OBI，而是 volatility。**

翻成人话：
- 你可以把它回测得像在赚钱；
- 但别太快得出“OBI 是核心 alpha”的结论；
- 很可能真正起作用的是 **非线性交互 + 波动状态 + maker 执行假设**。

## 9. 这条 alpha 该怎么 desk 化，才不容易被骗

### 9.1 正确读法
正确读法是：

> **它不是“单靠一分钟 signed imbalance 就稳定印钞”；而是“minute flow imbalance + nonlinear interaction + cost-aware admission” 的一条 raw alpha 候选。**

### 9.2 错误读法
不要这样读：
- “README 说 OBI 很强，所以直接上 L2 alpha”
- “15bps 阈值已经被证明有效”
- “只要上 XGBoost 就能自动吐 alpha”

这些都不严谨。

### 9.3 更适合我们 desk 的拆法
对当前 desk，我会把它拆成三层：

1. **raw alpha 主体**：`1m signed trade imbalance -> 5m forward return`
2. **conviction gate**：只有预测净边际大于成本才开仓
3. **execution assumption**：优先 maker / 被动成交，否则 alpha 可能直接消失

## 10. 和 `1m / 3m / 5m / 15m` 的关系

### 10.1 最自然的层级
- **1m**：原生信号频率
- **5m**：原生预测 / 持有窗口

### 10.2 `3m` 的用法
- 可把 `1m` signed flow 做 `3m` 平滑
- 或要求 `1m` 与 `3m` 方向一致才开仓
- 这比直接上 15bps 绝对阈值，可能更稳

### 10.3 `15m` 的用法
这条线到 `15m` 时，不太适合再 pretending 它是同一条逐根 alpha。
更合理的是：

- 把最近 `3 x 5m` 的 signed flow 聚成一个 **microstructure state**；
- 用来做：
  - breakout 的 adverse-selection veto
  - mean reversion 的 entry confirm
  - maker strategy 的 toxicity gate

也就是说：

> **在 `15m` 上，它更像“共享 microstructure gate”，而不是原汁原味的 alpha 本体。**

## 11. 我对这条材料的研究结论

### 11.1 值得 intake 吗？
**值得。**

因为它满足：
- raw alpha
- 可独立复现
- 可直接写成完整策略壳
- 数据公开可得
- 和 `1m/3m/5m` 直接相关

### 11.2 但该放在什么优先级？
我会放在：
- **raw alpha 候选池：中高优先级**
- 但不是“立刻相信 README 结论”的高优先级
- 而是“立刻做严谨分层复核”的高优先级

### 11.3 这轮最重要的 take-away

> **这份 repo 真正可复现的 alpha，不是“神奇 OBI”，而是“signed trade imbalance + nonlinear conviction gate + maker-only economics”。**

如果后续验证失败，最可能死掉的位置不是：
- 信号完全没方向；

而是：
- **阈值设太高，根本没交易；**
- **换成 taker 后，全部被成本吃光；**
- **真正起作用的不是 OBI，而是波动状态。**

## 12. 下一步怎么测

这部分最关键，直接给可开工版本。

### 12.1 实验 A：先把“假 OBI”和“真 OBI”分开
目的：别再让 repo headline 混淆 alpha 本体。

- 数据：Binance / Hyperliquid L2 book + aggTrades
- 同时构造：
  1. signed trade imbalance
  2. L2 depth imbalance
  3. microprice / queue proxy
- 看谁对 `fwd_1m / 3m / 5m` 真有增量预测力

**通过条件：** L2 OBI 至少要相对 signed trades 提供可见增量；否则这条线本质上就该改名成 flow alpha，而不是 book alpha。

### 12.2 实验 B：系统扫 horizon 与 threshold
目的：判断 repo 的 `5m + 15bps` 是不是拍脑袋。

网格：
- horizon：`1m / 3m / 5m / 10m`
- threshold：`2 / 4 / 6 / 8 / 10 / 15 bps`
- cost：
  - maker `1 / 2 bps`
  - taker `4 / 6 / 8 bps`

**通过条件：** 至少找到一块 post-cost 仍为正、而且 trade count 不是接近零的区域。

### 12.3 实验 C：做 walk-forward，不要只看单段 lucky sample
- 训练 / 测试：`30d/7d`、`60d/14d`、`90d/14d`
- 资产：`BTC / ETH / SOL`
- 比较：
  1. 线性模型
  2. 浅树模型
  3. XGBoost

**通过条件：** 如果只有复杂模型赚钱，而线性完全没有信号，要进一步检查是不是过拟合到 volatility regime。

### 12.4 实验 D：若独立 alpha 不够稳，直接降级成 shared gate
如果实验 B/C 结果显示：
- 单独跑不稳；
- 但在高 toxicity / 高 imbalance 时，别的策略明显更容易被反噬；

那就别硬把它当独立 alpha，直接降级成：
- breakout 的 veto
- mean reversion 的 confirm
- maker strategy 的 toxicity gate

这仍然有很高研究价值。

## 13. 参考资料

1. **tsuithomas. (2026). _Cryptocurrency Statistical Arbitrage & Microstructure Alpha Research_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/tsuithomas/crypto_research_order_book_imbalance>  
   - Repo URL: <https://github.com/tsuithomas/crypto_research_order_book_imbalance>

2. **Repo source files used in this digest**  
   - README: <https://raw.githubusercontent.com/tsuithomas/crypto_research_order_book_imbalance/main/README.md>  
   - Data integration: <https://raw.githubusercontent.com/tsuithomas/crypto_research_order_book_imbalance/main/src/data_integration.py>  
   - Feature engineering: <https://raw.githubusercontent.com/tsuithomas/crypto_research_order_book_imbalance/main/src/feature_engineering.py>  
   - Model training: <https://raw.githubusercontent.com/tsuithomas/crypto_research_order_book_imbalance/main/src/model_training.py>  
   - Backtester: <https://raw.githubusercontent.com/tsuithomas/crypto_research_order_book_imbalance/main/src/backtester.py>

3. **Binance Public Data Archive — aggTrades**  
   - Venue: Binance public data  
   - DOI: N/A  
   - Readable URL: <https://data.binance.vision/?prefix=data/spot/daily/aggTrades/>  
   - BTCUSDT path used for portability probe: <https://data.binance.vision/data/spot/daily/aggTrades/BTCUSDT/>
