# 别把 LiquidityHawk 只读成“情绪看板”：对 short-cycle crypto desk，更该先拆的是「overbought Williams %R × long-crowding liquidation fade」这条 15m raw alpha 候选

- 时间：2026-04-22 13:50 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/data/exchange_tracker.py`）+ Binance USDⓈ-M public-data portability probe（`BTC/ETH/SOL/XRP`，`15m`，近约 `31d`）
- 主题类型：raw alpha
- 基础 alpha：当价格已经处在 **短窗 overbought**（`Williams %R > -20`）且 Binance top-trader **long crowding** 已经明显偏高时，后续更容易出现一段 **long liquidation / squeeze-back-down**；交易表达上就是做一个 `crowded-upmove -> fade back to mid-state` 的短线反转
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/mean-reversion/crowding/long-short-ratio/top-trader-ratio/williams-r/liquidation-fade/short-only/asymmetric/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：repo 规则骨架 + public-data first probe

## 1. 这次看了什么

这轮主来源是一个 2026 新仓：

- **Author / Repo**：Iktiarshovo (2026), `liquidity-hawk`
- **Repo URL**：<https://github.com/Iktiarshovo/liquidity-hawk>
- **Readable URL**：<https://github.com/Iktiarshovo/liquidity-hawk/blob/main/README.md>
- **关键文件**：
  - `README.md`
  - `src/data/exchange_tracker.py`
- **可读结论**：repo 把核心想法写得非常直白：
  - `Williams %R < -80 + Shorts > 60% -> LONG`
  - `Williams %R > -20 + Longs > 60% -> SHORT`
  - 极端 funding 作为 fade 方向的附加确认

但对当前 desk，更值得保留的不是它“对称地做多做空”的表面写法，而是其中更像样的旁支：

> **过热上涨 + 多头拥挤 -> 做 long-liquidation fade。**

也就是：**不是把 long/short crowding 当情绪看板，而是把它和 overbought 价格状态拼起来，做一个可独立回测的 short-cycle crowding reversal raw alpha。**

## 2. base alpha 到底是什么

先按要求只回答一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：是“价格已经涨到短窗极热，同时仓位已经明显挤向多头”时，后面更容易出现一段拥挤多头的反向出清。**

所以它不是纯 filter，也不是纯 overlay。

它的 alpha 本体很明确：
- `Williams %R` 负责描述 **价格位置是否已经挤到局部高位**；
- `top-trader long share` 负责描述 **仓位是否已经明显挤到同一边**；
- 两者共振时，赌的是 **短线回吐 / long liquidation**，不是继续顺势追。

## 3. 为什么这条分支比 repo 原版“对称规则”更值得保留

repo README 给的是对称表述：
- `oversold + short crowding -> long`
- `overbought + long crowding -> short`

但我这轮 public-data probe 的 first verdict 很明确：

- **对称规则整体并不漂亮**；
- 真正有 pocket 的，是**short 这一边**，而且主要集中在 **ETH 15m**；
- 也就是说，这更像一条 **asymmetric crowding-reversal alpha**，不是“任何币、任何方向、60% 一刀切都能用”的通用公式。

这正好符合 desk 当前该做的事：

**不是照抄 repo 的 headline，而是把其中更可移植、更能落成完整策略的旁支拆出来。**

## 4. 最小可复现实验：这轮我是怎么测的

### 4.1 数据源与公开性
- 交易所：Binance USDⓈ-M Futures
- 公开接口：
  - `fapi/v1/klines`
  - `futures/data/topLongShortAccountRatio`
- 公开性：**完全公开可取，无需 API key**
- 频率：`15m`
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT`
- 样本：近约 `2976` 根 `15m` bar（约 `31d`）

### 4.2 指标与规则
- `Williams %R`：`14` 根 lookback
- crowding 指标：Binance `topLongShortAccountRatio` 里的 `longAccount / shortAccount`
- 先测 repo README 的原版口径：
  - long：`Williams %R < -80` 且 `short_share > 60%`
  - short：`Williams %R > -20` 且 `long_share > 60%`
- 入场：信号 bar 后 **下一根 open**
- 出场：
  - long：`Williams %R` 回到 `>-50`
  - short：`Williams %R` 回到 `<-50`
  - 否则 `8` 根 `15m` time stop
- 成本：round-trip `6 bps`

### 4.3 本轮产物
- `reports/artifacts/quant_digests/liquidity_hawk_probe_20260422/summary.csv`
- `reports/artifacts/quant_digests/liquidity_hawk_probe_20260422/threshold_sweep_summary.csv`
- `reports/artifacts/quant_digests/liquidity_hawk_probe_20260422/BTCUSDT_trades.csv`
- `reports/artifacts/quant_digests/liquidity_hawk_probe_20260422/ETHUSDT_trades.csv`
- `reports/artifacts/quant_digests/liquidity_hawk_probe_20260422/SOLUSDT_trades.csv`
- `reports/artifacts/quant_digests/liquidity_hawk_probe_20260422/XRPUSDT_trades.csv`

## 5. first verdict：原版对称规则没过，但 ETH 的 short-only pocket 过了

### 5.1 先看 repo 原版 `60%` 对称口径（含 `6 bps` 成本）

`summary.csv` 的 first probe 结果：

- `BTCUSDT`：`63` 笔，胜率 `58.7%`，平均 **净** `-6.48 bps/笔`
- `ETHUSDT`：`65` 笔，胜率 `61.5%`，平均 **净** `-1.28 bps/笔`
- `SOLUSDT`：`128` 笔，胜率 `64.8%`，平均 **净** `-2.72 bps/笔`
- `XRPUSDT`：`124` 笔，胜率 `62.9%`，平均 **净** `-3.77 bps/笔`

人话：
- 规则有方向感，**median trade** 常常是正的；
- 但按 taker-ish `6 bps` 成本，原版对称规则整体**没真正过线**；
- 所以不能把 repo 原文直接当 production-ready 策略照抄。

### 5.2 但 ETH 的 crowded-long short fade 出现了很清楚的 pocket

我继续在 `threshold_sweep_summary.csv` 里只扫 **crowding 阈值**，发现 **ETH short side** 很明显：

#### ETH，`long_share > 62%`，`Williams %R > -20`，`15m`
- 交易数：`58`
- 胜率：`63.8%`
- 平均净收益：`+5.66 bps/笔`
- 中位数净收益：`+28.60 bps/笔`
- 总净收益：`+328.2 bps`
- 成本口径：round-trip `6 bps`

#### ETH，`long_share > 70%`，`Williams %R > -20`，`15m`
- 交易数：`21`
- 胜率：`71.4%`
- 平均净收益：`+10.52 bps/笔`
- 中位数净收益：`+28.60 bps/笔`
- 总净收益：`+220.9 bps`
- 同样已含 `6 bps` 成本

这组数说明：

> **真正可保留的，不是“任何 60% crowding 都做反转”，而是“ETH 这类高流动 alt，在 15m overbought 且多头拥挤明显超过 62% 时，做 short-side liquidation fade”**。

## 6. 这条 alpha 应该怎么理解

### 6.1 它不是“仓位越偏多越继续涨”
有些 crowding 因子更像 continuation。但这条不是。

这里的结构是：
- 先要求价格已经挤到 `Williams %R > -20` 的局部过热区；
- 再要求 top-trader long share 明显偏高；
- 于是做的不是 trend follow，而是 **挤在一边后的脆弱性回吐**。

### 6.2 它也不是纯 sentiment 因子
单独看 L/S ratio，太容易变成“面板信息”；单独看 Williams %R，也容易变成普通超买超卖指标。

值钱的部分在于两者联动：

- `Williams %R` 给出 **价格 stretch**；
- `top-trader long share` 给出 **仓位拥挤**；
- 合起来，才更像一个可交易的 **liquidation-prone state**。

### 6.3 它更像 15m parent alpha，不像 5m 裸主信号
我额外做了一个很小的 `ETHUSDT 5m` 快检：
- 规则：`long_share > 62%` + `Williams %R > -20`
- exit：回到 `<-50` 或 `12` 根 `5m`
- 成本：`6 bps`
- 结果：`16` 笔，胜率 `43.8%`，平均净收益约 `-14.9 bps/笔`

这说明它更合理的部署方式是：
- **15m**：做 parent signal / admission
- **5m**：做 child execution、分批确认、减少追空时点风险

而不是把 5m 裸信号直接当主策略。

## 7. desk 可直接落地的策略壳

### 7.1 一个当前最像样的壳
以 `ETHUSDT 15m` 为例：

- **Universe**：先只做 `ETHUSDT`
- **Entry**：
  - `Williams %R(14) > -20`
  - `top-trader long share > 62%`
  - 下一根 `15m` open 做空
- **Exit**：
  - `Williams %R < -50` 即平
  - 或 `8` 根 `15m` time stop
- **Sizing**：
  - 固定风险分配起步
  - 之后可叠 `ATR` 或 intraday vol target
- **Risk**：
  - 单笔 hard stop（例如 `1.2~1.5 ATR`）
  - funding 结算前窗口减半仓
  - 避开重大宏观 / ETF / CPI 时间窗
- **Cost**：
  - 如果是 taker-heavy 执行，edge 变薄很快
  - 更适合 `15m signal -> 5m maker-first child execution`

### 7.2 为什么我仍然把“是否可直接落地完整策略”写成“是”
因为这条线已经具备完整壳所需的基本元素：
- 明确 entry
- 明确 exit
- 明确成本口径
- 明确时间止损
- 可补固定 risk / ATR sizing

不是那种只有解释、没有交易壳的主题。

## 8. 风险与保留意见

### 8.1 对称性是错觉
repo 写法看起来对称，但 public-data probe 表明：
- **long side 基本没亮点**；
- 主要 pocket 在 **short side**；
- 而且还集中在 **ETH**，并非所有 major 都同样成立。

### 8.2 这条线对成本很敏感
原版 `60%` 阈值在 `6 bps` 下大多不过线；说明它不是“随便下都赚”的粗边。

### 8.3 crowding 数据本身带交易所口径偏差
这里用的是 Binance `topLongShortAccountRatio`，本质上是交易所给出的 top-trader crowding proxy，不等于全市场持仓真相。跨所迁移要谨慎。

## 9. 下一步怎么测

1. **先做 short-only、asset-specific，而不是继续对称回测。**
   下一轮应直接固定：`ETH 15m short-only`，不再把 long side 混进去稀释。

2. **把 crowding threshold 做 walk-forward。**
   当前 pocket 在 `62%~70%` 之间最像样，但不能静态定死。应该做 rolling re-fit，看阈值是否随市场状态漂移。

3. **叠 funding / OI / taker imbalance 做二层 admission。**
   这条线天然适合叠：
   - positive funding
   - OI 扩张
   - taker buy dominance 放缓 / 反转
   看是否能在不明显减少样本的前提下抬高平均净 bps。

4. **把执行切成 15m signal + 5m child。**
   既然 5m 裸信号不行，下一轮就不要强迫它当主 alpha，而是让它做：
   - 开仓分批
   - 盘口 veto
   - maker-first fill
   - funding 边界前后回避

5. **加入真实止损与事件过滤。**
   当前只做了 `WR mid re-cross + time stop`，还没加：
   - ATR stop
   - breakout continuation veto
   - high-impact event blackout

## 10. 来源

### Repo
- Iktiarshovo. (2026). *liquidity-hawk*. GitHub.
- Repo URL：<https://github.com/Iktiarshovo/liquidity-hawk>
- Readable URL：<https://github.com/Iktiarshovo/liquidity-hawk/blob/main/README.md>
- Raw files：
  - <https://raw.githubusercontent.com/Iktiarshovo/liquidity-hawk/main/README.md>
  - <https://raw.githubusercontent.com/Iktiarshovo/liquidity-hawk/main/src/data/exchange_tracker.py>

### Public data endpoints used in the probe
- Binance USDⓈ-M klines：<https://fapi.binance.com/fapi/v1/klines>
- Binance top trader long/short account ratio：<https://fapi.binance.com/futures/data/topLongShortAccountRatio>

## 11. 一句话收尾

**这份仓真正值得 desk 留下的，不是“L/S ratio 看板”，而是：当 `15m` 价格已经过热、且 top-trader 多头拥挤明显偏高时，去做那段更脆弱的 long-liquidation fade；至少在 ETH 上，这条 short-only 分支已经给出了第一轮可交易口袋。**
