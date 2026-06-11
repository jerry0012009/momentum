# 别把这份 2026 新研究库只读成 walk-forward infra：对 short-cycle desk，更该先测的是「EMA 趋势壳 × OBV caution veto × ATR trailing stop」这条完整单资产 raw alpha
- 时间：2026-04-03 04:45 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + repo 目录结构 + `topics/momentum/strategies/wf_testing/momentumBTC_wf.ipynb` raw notebook 输出）
- 主题类型：raw alpha
- 基础 alpha：单资产趋势跟随；`Close > EMA` 的趋势壳为本体，再用 `OBV divergence + swing/ATR caution + ADX override + ATR sizing/stop` 决定何时放行、何时缩手、何时退出
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但 repo 里 sizing 参数存在明显口径疑点，必须重做成本与参数卫生检查）
- 主题标签：raw-alpha/trend/momentum/single-asset/ema/obv/adx/atr/trailing-stop/caution-veto/volume-confirmation/walk-forward/optuna/binance/btc/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：公开 GitHub repo + 原始 notebook 代码 + notebook 已保存回测输出 + 明确参数空间 + 明确成本压力测试

## 1. 这次看了什么
这次补的不是又一个 pairs / carry / ETF 分支，而是一条**可以独立成完整策略、而且非常适合快速下沉到 `15m / 5m` 的单资产趋势 raw alpha 壳**。

主材料来自一个很新的公开仓库：
- **Author / Org**：`Epsilon-Fund`
- **Year**：2026（repo created at `2026-02-18`, updated at `2026-04-02`）
- **Title / Repo**：*Epsilon-Quant-Research*
- **Venue**：GitHub repository / research notebook
- **DOI**：N/A
- **Readable URL**：https://github.com/Epsilon-Fund/Epsilon-Quant-Research
- **Repo URL**：https://github.com/Epsilon-Fund/Epsilon-Quant-Research
- **Notebook URL**：https://github.com/Epsilon-Fund/Epsilon-Quant-Research/blob/main/topics/momentum/strategies/wf_testing/momentumBTC_wf.ipynb
- **Raw notebook URL**：https://raw.githubusercontent.com/Epsilon-Fund/Epsilon-Quant-Research/main/topics/momentum/strategies/wf_testing/momentumBTC_wf.ipynb

这个 repo 首页写得很泛：`Systematic crypto trading research | Momentum, stat-arb & algorithmic strategies`。但真正值得 desk intake 的，不是它“有很多 topic”，而是 notebook 里已经给出了一条**规则清楚、可 walk-forward、带 sizing/stop/cost stress 的完整趋势骨架**。

我这轮把它定成主 digest，是因为它先能清楚回答一句话：

> **base alpha 是什么？**
>
> **就是单资产趋势延续；EMA 趋势方向是 alpha 本体，OBV divergence / ATR caution / ADX override 这些不是 alpha 本体，而是让趋势单在不该追的时候少追、在该收手的时候更快收手。**

这点很重要：它不是“一个模糊的过滤器专题”，而是**有 entry / exit / sizing / risk / cost 全链路的 raw alpha 候选**。

## 2. 这条东西的 base alpha 到底是什么
先把结构讲成人话。

repo 里这条 momentum notebook 做的不是复杂预测，而是一个很典型、但被认真包装成 production shell 的逻辑：

1. **方向本体**：价格站在 EMA 之上时，默认认为趋势向上；
2. **放行条件**：只有当量能没塌、趋势强度够，且没有出现明显的“价格继续涨但 OBV 没跟”的背离时，才允许入场；
3. **风险约束**：即便入场，也不是 fixed size，而是按 ATR 动态估仓；
4. **退出机制**：不是等均线死叉，而是用更快的 swing/ATR trailing stop 把趋势利润锁住。

所以如果要一句话概括：

> **base alpha = 趋势延续；repo 真正提供的新信息，是如何把“追趋势”包进一个相对完整的 caution-veto + dynamic stop 壳里。**

这正适合当前 desk，因为最近素材池里：
- pairs / stat-arb 很多；
- carry / basis 也在累；
- microstructure raw alpha 也不少；

但一个**极轻量、只依赖 OHLCV、可以几小时内跑完最小实验的单资产 trend shell**，反而仍然值得多补几个高质量版本做对照。

## 3. repo 到底给了哪些可复现规则
### 3.1 数据与框架能力
notebook 明确写了：
- **Pairs**：支持 Binance 交易对，如 `BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- **Intervals**：支持 `'1m' '5m' '15m' '1h' '4h' '1d' '1w'`
- **Walk-forward**：使用 rolling train/test folds + Optuna 优化 + OOS 检验
- **成本参数**：notebook 有显式 `COST = 0.001`，并附 transaction cost stress test

虽然示例 notebook 实际拉的是：
- `SYMBOL = 'BTCUSDT'`
- `INTERVAL = '1d'`
- `LOOKBACK = 2150`

但关键在于：**这套策略只用 OHLCV 派生指标**，所以迁移到 `15m / 5m` 并不需要新的低频外部数据。

### 3.2 入场本体：EMA 趋势 + 成交量确认
核心代码可以概括成：
- `EMA = Close.ewm(span=ema_span)`
- `Vol_MA = Volume.rolling(vol_ma_period).mean()`
- `Entry_Long = (Close > EMA) & (~Caution_Long | ADX_14 > adx_override) & (Volume > Vol_MA)`

翻译一下：
- **Close > EMA**：方向本体，趋势壳；
- **Volume > Vol_MA**：不是没量也硬追；
- **~Caution_Long | ADX override**：如果出现 caution，原则上先别追；除非 ADX 很强，说明趋势确实够硬，可以 override 掉警报。

这点非常 desk-friendly，因为它不是那种“再加十个指标拼投票”的杂糅逻辑，而是很清楚地把结构分成：
- alpha 本体：趋势
- 入场否决：caution
- 强趋势豁免：ADX override

### 3.3 caution 机制：不是另一个 alpha，而是追涨否决层
repo 里最有意思的部分是 `Caution_Long`：

1. **Swing/ATR caution**
   - `((Swing_Hi_Cau - Low) > caution_threshold * ATR_Cau)`
   - 本质上在问：最近价格相对局部 swing 区间是不是已经被拉得太开 / 太危险？

2. **OBV caution**
   - `(Close > Close.shift(obv_lookback)) & (OBV < OBV_MA)`
   - 即：价格比若干 bar 前更高，但 OBV 没同步走强，出现 price-up / flow-weak 的背离。

所以这条策略最值得 intake 的一句，不是“EMA 有用”，而是：

> **追趋势时，最该先补的不是再找一个 entry trigger，而是做一个专门拦截“拉高末端追单”的 caution veto。**

这比很多“均线 + RSI + MACD 一起买”的东西更像 production 逻辑。

### 3.4 sizing 与退出：ATR 做统一风险坐标
repo 里把 `ATR` 同时用于三件事：

1. **caution 尺度统一**：局部 swing 拉伸是否过度，用 ATR 归一；
2. **position sizing**：
   - `position_size_raw = risk_per_trade / (ATR_Sz / Close)`
   - 再 clip 到 `max_leverage`
3. **trailing stop**：
   - 用 `Swing_Hi_Stp - ATR_Stp * stop_multiple * stop_atr_scale`
   - 持仓后只会上调 stop，不会下调

这意味着它不是“仅有入场，没有风险管理”的半成品，而是个完整壳。

## 4. notebook 里最有信息量的数字
### 4.1 四个 walk-forward OOS fold：前三个能活，最后一个明显翻车
notebook 保存的 OOS fold 结果是：
- **Fold 1 OOS Sharpe：`1.44`，test return `0.80`，test DD `-0.31`，`12` 笔交易**
- **Fold 2 OOS Sharpe：`2.09`，test return `0.93`，test DD `-0.14`，`16` 笔**
- **Fold 3 OOS Sharpe：`1.56`，test return `0.99`，test DD `-0.31`，`11` 笔**
- **Fold 4 OOS Sharpe：`-2.22`，test return `-0.60`，test DD `-0.60`，`9` 笔**

这组数的正确信息量不是“平均下来还不错”，而是：

> **这条壳不是纯过拟合垃圾，因为前三个 OOS fold 能活；但它也绝不是稳定 production alpha，因为最近一个 OOS fold 明显失效。**

这恰好符合我们 intake 的标准：**值得进素材池，但必须快速复现、快速证伪。**

### 4.2 成本压力测试：成本加倍后没立刻死，但 drawdown 很丑
notebook 的 transaction cost stress test：
- **Cost = `0.0010`**：Sharpe `0.84`，Return `173.19%`，MaxDD `-72.42%`
- **Cost = `0.0015`**：Sharpe `0.81`，Return `160.50%`
- **Cost = `0.0020`**：Sharpe `0.78`，Return `148.39%`
- **Cost = `0.0030`**：Sharpe `0.73`，Return `125.81%`，MaxDD `-73.57%`

这说明两件事：
1. **它对成本不是一碰就碎**，说明趋势壳至少不是靠极高换手硬堆出来；
2. **但 drawdown 巨大**，所以不能把它当成“稳健 alpha”，更像一条需要再加 regime / cost veto / session filter 的母策略。

### 4.3 参数稳定性里，有值得抄的，也有必须怀疑的
notebook 给出稳定后固定的参数包括：
- `ema_span = 21`
- `adx_override = 63`
- `max_leverage = 3`
- `stop_mult_ent_normal = 1`
- `stop_mult_pos_normal = 1`
- `atr_size = 13`

这些是相对像样的“骨架参数”。

但同时它还打印出：
- `risk_per_trade = 0.46`

而前面 notebook 声明的搜索空间却是：
- `risk_per_trade: 0.005 ~ 0.05`

这意味着 repo 至少存在一个**参数口径 / 展示卫生问题**。所以正确读法不是盲信 tuned number，而是：

> **抄结构，不抄参数。尤其 sizing 参数，必须自己重做。**

## 5. 这条东西为什么值得进当前 short-cycle 研究池
### 5.1 因为它是“完整策略壳”，不是只会讲故事
当前很多新材料的问题是：
- 要么只有 signal，没有 risk；
- 要么只有 filter，没有 alpha 本体；
- 要么是低频宏观 / funding 结构，只能做 gate。

而这条 repo 提供的是：
- **entry**：`Close > EMA` + volume confirm
- **veto**：OBV divergence / swing-ATR caution
- **override**：ADX 很强时允许穿透 caution
- **sizing**：ATR-based
- **exit**：swing/ATR trailing stop
- **cost**：至少做了显式 stress test

这完全符合“可直接落地完整策略”的优先级。

### 5.2 因为它可以服务 `15m / 5m / 3m / 1m` 的最小实验
虽然 notebook 示例是 `1d`，但这套规则只依赖：
- close
- high / low
- volume
- ATR
- OBV
- ADX

所以它对 desk 最大的价值不是 daily 表现，而是：

> **可以直接压缩到短周期，并快速回答：在 crypto perp 的高噪声环境里，OBV caution veto 到底能不能显著改善趋势策略的“追顶死法”？**

这是一个很适合当前阶段的问题，因为它既服务单资产趋势，也可能反向服务：
- breakout 策略的追单否决层
- momentum sleeve 的 size attenuation
- raw trend alpha 的 shared execution veto

## 6. 我对这份 repo 的判断：值得 intake，但不要把它当现成 production
### 值得 intake 的地方
1. **base alpha 清楚**：趋势延续，而不是模糊 filter
2. **结构完整**：entry / veto / override / sizing / stop 都有
3. **代码可读**：几十行策略函数就能复现，不是黑箱
4. **支持 walk-forward**：至少知道作者在做 OOS 验证，而不是只放一张 equity curve

### 必须警惕的地方
1. **示例仍是日频 BTC**，不是原生短周期 production 结果
2. **第四个 OOS fold 失效严重**，稳定性并不干净
3. **drawdown 很大**，绝不算温和
4. **`risk_per_trade` 参数口径异常**，说明 repo 有实现 / 展示卫生风险
5. **long-only 壳偏重**，对 short-cycle desk 还缺 short-side / flat-regime 处理

所以这轮最合理的定位是：

> **把它当“单资产趋势壳候选 + caution veto 组件库”，而不是把 notebook 输出当成可直接信任的收益证明。**

## 7. 对我们 desk，最值得先测的不是 headline，而是哪三个部件
如果只能摘 3 个最值得复现的模块，我会选：

1. **EMA 趋势壳**
   - 最轻量、最容易做 baseline
2. **OBV divergence caution veto**
   - 这是 repo 里最像“production 拦截器”的组件
3. **ATR trailing stop**
   - 能直接回答：短周期里不用死等均线死叉，是否更能锁住 trend legs

反而我不会先抄：
- 它的具体 Optuna 最优参数
- notebook 里的 sizing 数值
- daily 结果对应的任何 headline return

## 8. 下一步怎么测
### 实验 A：15m BTCUSDT perp 最小复现
**目标**：先验证这条壳能不能在短周期 survive `fee + funding + slippage`。

- **标的**：Binance / Bybit / OKX `BTCUSDT perp`
- **bar**：`15m`
- **entry baseline**：`Close > EMA(21)` 且 `Volume > Vol_MA(12~24)`
- **caution veto**：
  - `price-up / OBV-weak` 背离
  - `(recent swing extension) / ATR > threshold`
- **override**：`ADX(14) > 55~65`
- **exit**：`swing high/low + ATR trailing stop`
- **cost**：双边 taker fee + conservative slippage + funding
- **看什么**：
  1. 加入 caution 后，trade count 是否明显下降；
  2. caution 是否主要改善尾部亏损，而不是只减少收益；
  3. trailing stop 是否比 `EMA cross down` 更能保留 trend leg。

### 实验 B：5m 版本，专门测“追顶否决”是否成立
**目标**：验证 repo 最有意思的旁支——OBV caution veto——在快周期是否真的有增益。

- 只做两套对照：
  - **baseline**：EMA 趋势壳
  - **variant**：EMA 趋势壳 + OBV caution veto
- 不先调太多参数，避免多重试错
- 输出只看：
  - net Sharpe
  - max DD
  - worst decile trade loss
  - avg adverse excursion

如果 `variant` 只是让 trade 少了，但尾部没改善，那这个 caution 组件就不值得扩散到更多策略里。

### 实验 C：跨资产 transfer，但只在 A/B 成立后做
**标的**：`ETH / SOL / BNB`

目的不是立刻做多币组合，而是回答：

> **这条壳是 BTC 专属，还是主流大币 trend shell？**

若 BTC 有效、ETH/SOL 同向，则可把它升级成：
- 单币 trend sleeve
- 或 multi-asset trend allocator 的基础模块

## 9. 一句话结论
这份 2026 新 repo 真正值得 desk intake 的，不是 notebook 上那串回测数字，而是它把一个**简单趋势 alpha**包装成了一个**有 veto、有 override、有 sizing、有 trailing stop 的完整策略壳**。

对我们来说，最该先复现的问题不是“它 daily 有没有赚很多”，而是：

> **把 `OBV caution veto` 和 `ATR trailing stop` 塞进 `15m / 5m` 的 EMA 趋势壳后，能不能明显减少 short-cycle 里最伤的那类追顶回撤。**

## 10. 参考资料
1. **Epsilon-Fund. (2026). _Epsilon-Quant-Research_. GitHub repository.**  
   - Venue: GitHub repository  
   - DOI: N/A  
   - Repo URL: https://github.com/Epsilon-Fund/Epsilon-Quant-Research  
   - Readable URL: https://github.com/Epsilon-Fund/Epsilon-Quant-Research

2. **Epsilon-Fund. (2026). _momentumBTC_wf.ipynb_.**  
   - Notebook URL: https://github.com/Epsilon-Fund/Epsilon-Quant-Research/blob/main/topics/momentum/strategies/wf_testing/momentumBTC_wf.ipynb  
   - Raw notebook URL: https://raw.githubusercontent.com/Epsilon-Fund/Epsilon-Quant-Research/main/topics/momentum/strategies/wf_testing/momentumBTC_wf.ipynb

3. **GitHub API metadata — Epsilon-Fund / Epsilon-Quant-Research.**  
   - Repo created: `2026-02-18T13:17:24Z`  
   - Repo updated: `2026-04-02T16:09:50Z`  
   - Description: `Systematic crypto trading research | Momentum, stat-arb & algorithmic strategies`
