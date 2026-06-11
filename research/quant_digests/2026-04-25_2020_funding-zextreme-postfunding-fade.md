# 别把这份 funding repo 只读成“收租/套利外壳”：对 short-cycle crypto desk，更该先拆的是「funding z-score extreme × post-funding fade」这条 raw alpha

- 主题类型：raw alpha
- 基础 alpha：当 perp funding rate 偏到历史尾部，往往意味着仓位一边倒；在短一点的后续窗口里，价格更容易先朝**反方向**回吐，而不是继续单边走。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

**先回答 base alpha 是什么：** 不是“funding carry 收租”，也不是“跨所无风险套利”；这篇更值得 desk 留样的 base alpha，是 **extreme funding 作为拥挤度事件，触发后续 `1h~4h` 的价格反转/fade**。

## 1. 为什么这条线这轮值得写

今天已经连着补了不少 `pairs / xs / carry` 分支；这份 repo `farrellh1/crypto-funding-rate-strategy` 的价值，在于它把 funding 从“低频收租指标”改写成了一个**可交易的短窗事件信号**：

> funding 偏得离谱，说明多空一边倒；一边倒未必马上崩，但至少给了我们一个能在下一小段里测试 reversal / continuation 的公开事件锚点。

翻成人话：
- funding 很正：说明做多拥挤，多头愿意持续付钱；
- funding 很负：说明做空拥挤，空头愿意持续付钱；
- 真正该测的不是“长期 carry 能不能拿”，而是**拥挤刚被打印出来以后，接下来几个小时价格会怎么走**。

**一句话核心结论：** 在我这次 Binance USDⓈ-M 公开数据快检里，`|funding z| >= 1.5` 之后更像是 `1h~4h` 的 **post-funding fade**，不是默认 continuation。  
**一句话证明方式：** 我直接把 funding 事件映射到 Binance perp 公开 `1h` bar，做了 `6` 个 liquid majors、`28d` rolling z-score、`1h/4h/8h` forward return 的 honest pooled event study。

## 2. 我实际看了什么

### Repo
- **Author / Title**: `farrellh1` / *crypto-funding-rate-strategy*
- **类型**: GitHub repository
- **DOI**: N/A
- **Readable URL**: <https://github.com/farrellh1/crypto-funding-rate-strategy>
- **Repo URL**: <https://github.com/farrellh1/crypto-funding-rate-strategy>

### 本轮实际审计文件
- `README.md`
- `signals/zscore.py`
- `signals/filters.py`
- `config.yaml`

### Repo 里最关键的可复用点
1. **alpha 本体写得很清楚**  
   - `z = (current_funding - rolling_mean) / rolling_std`
   - `mean_reversion`: `z >= threshold -> SHORT`, `z <= -threshold -> LONG`
   - `momentum`: 反过来做
2. **完整策略壳是现成的**  
   - lookback、threshold、strategy mode
   - volume / OI filter
   - fixed USD sizing
   - `stop_loss_pct=4%`、`take_profit_pct=2%`
   - maker/taker fee + slippage
3. **repo 默认配置其实已经给了一个 desk 问题**  
   - `lookback_periods: 168`（56 天）
   - `threshold: 2.5`
   - `strategy_mode: momentum`
   - `volume_filter.min_zscore: 0.5`
   - `oi_filter.max_zscore: 2.0`

我对这份 repo 的 desk 化读法是：**先别急着相信它的 momentum 默认值，先做 honest sign test。**

## 3. strategy 拆解（desk 化）

- **方向属性**：单资产、事件驱动、拥挤度触发，可做顺势也可做逆势，但本轮快检更偏 `mean reversion`
- **基础 alpha**：`funding z-score extreme -> post-funding price fade`
- **regime**：资金费率必须进入历史尾部（这本身就是 event regime）
- **filter / veto**：可接 `8h volume z-score`、OI z-score、极端单边趋势 veto
- **risk / sizing / execution overlay**：固定名义仓位或 vol-target；`1h~4h` time stop；再叠加止损/止盈与 maker-vs-taker 成本对照

这里最重要的边界是：
- **funding carry** 是另一条 raw alpha；
- 这篇更值钱的是 **funding extreme 当 crowding shock，看后续价格回吐/延续**；
- 所以别把它硬伪装成“收 funding”的低频中性策略。

## 4. 本地 portability probe（Binance USDⓈ-M public）

### 数据口径
- 资产：`BTC/ETH/SOL/BNB/XRP/DOGE`
- funding：Binance `/fapi/v1/fundingRate`，公开可得，**8h 更新**
- 价格：Binance `/fapi/v1/klines` `1h` bar，公开可得
- 事件定义：`28d` rolling funding z-score，取 `|z| >= 1.5`
- 事件数：pooled 共 **`35`** 个有效事件
- 策略记分：
  - `mean_reversion`：高 funding 做空、低 funding 做多
  - `momentum`：高 funding 做多、低 funding 做空

### pooled 结果
1. **plain mean-reversion，1h 持有**：平均约 **`+22.24 bps/笔`**，胜率约 **`77.4%`**（`35` 笔）
2. **plain mean-reversion，4h 持有**：平均约 **`+14.41 bps/笔`**，胜率约 **`67.4%`**（`35` 笔）
3. **到了 8h，sign 开始翻**：mean-reversion 平均约 **`-10.83 bps/笔`**，而 momentum 约 **`+10.83 bps/笔`**

这组数说明：
- **短一点的后续窗口（1h~4h）更像 fade**；
- **再拖到完整 8h，continuation 反而开始占上风**；
- 所以它更像 `8h parent event -> 1h/15m child execution`，不是“看到 funding 极端就一路拿到下次 funding”。

### 一个额外提醒：volume gate 没有自动加分
repo 很自然地想加 `volume z > 0.5` 过滤；但我这次快检里，留下来的只有 **`7`** 个事件：
- `1h` mean-reversion 反而掉到 **`-15.36 bps/笔`**
- `4h` 也只剩 **`+2.25 bps/笔`**

所以当前至少不能默认把“高量确认”写死成 admission；它更像**待验证 filter**，不是 alpha 本体。

## 5. 为什么和当前 `1m/3m/5m/15m` desk 直接相关

这条线虽然事件源是 `8h` funding，但它很适合被压成短周期实验：

- funding 公布/结算是**公开、稳定、低噪声**的事件锚点；
- 我们不用把它伪装成逐根主信号，而是把它当 **parent regime/event**；
- 真正下手的位置可以放到 `15m` 甚至 `5m`：
  - `high positive funding` 后只找反弹失败做空
  - `deep negative funding` 后只找止跌回收做多
  - 持有 `4/8/16` 根 `15m`，而不是机械拿满 `8h`

也就是说，它最像：
> **公开 crowding 数据驱动的短窗 raw alpha**，而不是一个只能做慢频 overlay 的宏观过滤器。

## 6. 下一步怎么测（最小实验）

### 实验 1：把 `8h event` 压到 `15m child`
- universe：先做 `BTC/ETH/BNB`
- parent：`|funding z| >= {1.5, 2.0}`
- child entry：事件后第 `1~4` 根 `15m`，只在价格朝 crowding 方向再冲一下时反手
- exit：持有 `4/8/16` 根 `15m` 或 hit `1.5*ATR(15m, 20)`
- 先看：**avg net bps / trade、win rate、MAE/MFE**

### 实验 2：别先加 OI，先做最便宜的 veto
- veto A：如果事件后第一根 `15m` 已经直接反向走完 `>0.75 ATR`，不追
- veto B：如果 funding 极端但 basis / perp premium 已经快速回归，不开
- 目标：减少“迟到 fade”

### 实验 3：比较 3 个退出时钟
- `1h fixed hold`
- `4h fixed hold`
- `15m trailing stop + 8h hard time stop`

因为这次快检已经很明确：**edge 更像短 hold，不像长 hold。**

## 7. 风险与保留意见

1. **事件数不多**：当前 pooled 只有 `35` 笔，先当 intake verdict，不当最终定案。  
2. **交易所差异**：repo 原生是 Bybit；我这次 probe 用的是 Binance public data，结论是“可移植线索”，不是逐字复刻。  
3. **8h 数据天然稀疏**：这条线不会变成高频主引擎，更适合作为 `15m/5m` 的 event sleeve。  
4. **volume/OI filter 很容易喧宾夺主**：如果 base alpha 先不稳，继续堆 filter 往往只是在减少样本。  
5. **成本要诚实**：`1h~4h` gross 看起来够厚，但上实盘前必须补 maker/taker、spread、滑点和事件后冲击成本。

## 8. 这轮结论

我会把这条线放进 **raw alpha 素材池**，优先级高于纯 filter / regime 题。原因很简单：
- base alpha 说得清；
- 公开数据能复现；
- repo 自带完整策略壳；
- 快检已经给出一个很实用的 desk 结论：

> **funding extreme 更像短窗拥挤回吐事件，优先测 `1h~4h fade`，不要默认一路拿到下次 funding，更不要默认高量过滤一定更好。**

## 9. 来源

- `farrellh1`. *crypto-funding-rate-strategy*. GitHub repository.  
  Readable URL: <https://github.com/farrellh1/crypto-funding-rate-strategy>
- Binance USDⓈ-M Futures API Docs. Funding Rate History / Klines.  
  Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History>
- 本轮 artifacts：
  - `reports/artifacts/quant_digests/2026-04-25_funding_zextreme_probe.py`
  - `reports/artifacts/quant_digests/2026-04-25_funding_zextreme_probe_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-25_funding_zextreme_probe_detail.csv`
