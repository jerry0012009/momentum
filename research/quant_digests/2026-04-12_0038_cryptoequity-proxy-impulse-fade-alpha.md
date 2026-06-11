# 别把这份 2026 GitHub crypto-proxy repo 只读成“follow the proxy”：对 short-cycle desk，更该先测的是「US crypto-equity proxy impulse × BTC/ETH 15m fade」这条 raw alpha

- 时间：2026-04-12 00:38 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `strategies/crypto_advanced.py::OnChainProxyStrategy`）+ Yahoo Finance `5m` public chart data + Binance USDⓈ-M `5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**当 `COIN / MARA / RIOT` 这组美股 crypto proxy 在美股常规时段内出现显著正向 `15m` 冲击时，BTC/ETH perp 下一段 `15m` 更像短时反打而不是继续跟；对 desk 更可执行的读法是“proxy impulse exhaustion fade”，不是机械追 proxy。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-asset/lead-lag/mean-reversion/crypto-equity-proxy/coin/mara/riot/btc/eth/us-session/15m/5m/repo/public-data/cost/risk
- 证据类型：repo 源码证据 + 公共数据 portability probe

## 1. 这次看了什么
主材料是一个刚创建的 GitHub 仓库：

- **Repo owner / author handle:** `zwmjj`
- **Year:** 2026
- **Title:** `kuant-strategies`
- **Repo URL:** <https://github.com/zwmjj/kuant-strategies>
- **Readable README:** <https://raw.githubusercontent.com/zwmjj/kuant-strategies/main/README.md>
- **Key source used this round:** <https://raw.githubusercontent.com/zwmjj/kuant-strategies/main/strategies/crypto_advanced.py>
- **GitHub API metadata:** created `2026-04-11T19:54:53Z`, pushed `2026-04-11T20:07:28Z`

README 把它写成一个“大而全”的 quant strategy 仓：momentum、mean reversion、cross-asset、crypto、options、ML 都有。对我们 desk 真正有值钱感的，不是整个框架，而是 `crypto_advanced.py` 里一个很容易被忽略的分支：

> **`OnChainProxyStrategy`：用 `COIN / MARA / RIOT` 这些美股 proxy 去推断 crypto。**

repo 原作者给的默认读法偏“proxy stronger -> BTC stronger”。但源码里其实已经混了两种不同思想：

1. **follow / continuation**：`COIN`、`MARA/RIOT` 相对 BTC 更强时，看多 BTC；
2. **relative-value / mean reversion**：`BTC/COIN` 比率 z-score 偏太多时，反而做回归。

这就给了一个很 desk 化的入口：

> **这些 proxy 不一定是“稳定领先指标”，更可能是“把 crypto risk-on 情绪先在美股里放大、再回吐”的跨资产噪声放大器。**

所以这轮我不照抄 repo 的 20 日 proxy-follow 叙事，而是把它压到 short-cycle 上，先测一个更朴素的版本：

> **如果 `COIN/MARA/RIOT` 在一个 `15m` 里集体猛拉，BTC/ETH perp 在下一段 `15m` 更容易继续跟，还是更容易反打？**

一句话核心结论：

> **对当前 public-data quick probe 来看，更值钱的不是“追 proxy”，而是“fade proxy shock”——尤其是正向 proxy 冲击之后做 BTC/ETH 的下一段 `15m` 反打。**

## 2. 先回答最重要的一句：base alpha 到底是什么
这轮 base alpha 是清楚的：

> **cross-asset proxy impulse exhaustion fade**。

翻成人话：

- 美股里一篮子 crypto proxy（`COIN / MARA / RIOT`）突然在 `15m` 里一起冲很猛；
- 这通常意味着 crypto risk appetite 在美股时段被先放大、先交易、先拥挤；
- 但对 Binance perp 来说，下一段不一定继续顺着走，反而常出现 **短时回吐 / 反打**；
- 因此可以把它写成：
  - **positive proxy shock → short BTC/ETH next 15m**；
  - negative proxy shock 也能测，但当前样本里更弱。

它不是：

- 单纯的宏观 regime 注释；
- 低频 overlay；
- 只有解释、不能下单的情绪故事。

它本身就能形成一条明确的入场-持有-退出规则，所以归类成 **raw alpha** 是成立的。

## 3. repo 里真正值得拿走的，不是“proxy 预测 BTC”，而是“proxy 是噪声放大器”
`OnChainProxyStrategy` 最关键的源码口径大概是三段：

1. **COIN 相对 BTC 更强 -> 看多 BTC**
2. **MARA / RIOT 相对 BTC 更强 -> 看多 BTC**
3. **`BTC/COIN` ratio z-score 极端 -> 做均值回归**

也就是说，这个 repo 自己其实已经承认：

- proxy 与 crypto 之间既有 **trend-follow** 成分，
- 也有 **relative-value reversion** 成分。

对我们 `5m / 15m` desk，后一种读法反而更实用。原因很简单：

- `COIN / MARA / RIOT` 是**美股交易时段**内更新的；
- 它们会把 crypto narrative、风险偏好、ETF 流量想象、矿业 beta、美国盘资金偏好都糅在一起；
- 对 ultra-short crypto perp 而言，这种“先在 proxy 里被放大”的信号，很多时候不适合作为追涨依据，反而更像 **exhaustion / overshoot trigger**。

所以这轮不是把 repo 否掉，而是把它**翻译成更适合我们 desk 的旁支 alpha**：

> **proxy 是 signal source；真正该交易的是 proxy-shock 之后 Binance perp 的短时回吐。**

## 4. 为什么这轮值得做，而不是继续补又一条常规 pairs / XS reversal
因为它补的是当前素材池里相对没那么拥挤的一块：

1. **它是 raw alpha，不是纯 filter。**
2. **它属于 cross-asset / external-data，但更新频率够高。**
   - 不是天频宏观表；
   - 而是可以落到 `5m / 15m` 的可交易 proxy。
3. **它跟当前 short-cycle desk 有直接关系。**
   - 我们已经有很多 venue / OFI / pairs / funding / XS reversal；
   - 但“美股 crypto proxy -> Binance perp”的跨资产短冲击翻译线还没系统收入池子。
4. **它可独立复现。**
   - Yahoo Finance `5m` chart 数据公开可取；
   - Binance USDⓈ-M `5m` klines 公开可取；
   - 不需要专有 feed。

所以这条线不是“为了新而新”，而是确实在现有 pool 里补了一个**不同来源、不同交易时段、不同传导路径**的 raw alpha。

## 5. 本地 portability probe：`COIN/MARA/RIOT` 冲击到底更像 continuation，还是更像 fade？
本地 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/crypto_equity_proxy_lead_probe_summary_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/crypto_equity_proxy_lead_probe_series_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/crypto_equity_proxy_fade_summary_2026-04-12.csv`

### 5.1 数据与口径
- **Proxy leg：** Yahoo Finance `query1.finance.yahoo.com/v8/finance/chart`
  - 标的：`COIN`, `MARA`, `RIOT`
  - 频率：`5m`
  - 区间：近 `60d`
  - 交易时段：Yahoo 常规股票交易时段（工作日、美股常规盘）
- **Crypto leg：** Binance USDⓈ-M Futures `fapi/v1/klines`
  - 标的：`BTCUSDT`, `ETHUSDT`
  - 频率：`5m`
  - 区间：近 `60d`

### 5.2 Signal 构造
先做 proxy 等权篮子：

```text
proxy_ret_5m = mean( ret(COIN), ret(MARA), ret(RIOT) )
proxy_ret_15m = rolling_sum_3bars(proxy_ret_5m)
proxy_z_15m = zscore(proxy_ret_15m, 60 bars)
```

然后看两种读法：

1. **follow-the-proxy**
   - `proxy_z > threshold` 就顺着 proxy 方向去做下一段 crypto；
2. **fade-the-proxy**
   - `proxy_z > threshold` 后，反向做下一段 crypto。

crypto leg 用的是：

- `BTC`、`ETH` 单腿；
- 以及 `BTC/ETH` 等权 basket；
- 持有期优先看 **next `15m`**，再看 **next `5m`**。

### 5.3 结果先说结论
结论非常干脆：

> **当前样本里，“跟 proxy”整体是负的；“fade proxy”在 `15m` 上更像能落地的第一落点。**

也就是说，repo 原始“proxy stronger -> BTC stronger”的方向，压到 short-cycle 后并不自然成立；
对我们 desk，更像该反过来读。

## 6. 这轮最值得记住的 6 个数
### 6.1 `15m` 上，最像 first lane 的是“正向 proxy shock 后做 fade”
对 `BTC/ETH` 等权 basket：

- 当 **`proxy_z_15m > 1.0`** 时，**下一段 `15m` 反向做 BTC/ETH basket**：
  - 约 **`393`** 次事件
  - 平均 **`+3.61 bps / trade`**
  - 胜率约 **`55.2%`**
  - t-stat 约 **`1.63`**

拆到单腿：

- **BTC：** `+3.38 bps / trade`，胜率约 `53.7%`
- **ETH：** `+3.84 bps / trade`，胜率约 `56.5%`

这说明它不是单一币种偶然抽风，更像是 **proxy shock -> major perp short-horizon fade** 的共性现象。

### 6.2 两边都 fade 也行，但正向 shock 更肥
如果做双边版本：

- **`|proxy_z_15m| > 1.0` 时按反向去做**：
  - `BTC/ETH` basket 约 **`778`** 次事件
  - 平均 **`+2.50 bps / trade`**
  - 胜率约 **`55.0%`**

但 asymmetry 很明显：

- **正向 shock fade**：`+3.61 bps / trade`
- **负向 shock fade**：仅约 `+1.36 bps / trade`

所以当前更像：

> **proxy 向上猛拉之后的短时拥挤 / 透支，比 proxy 向下急跌后的 oversold 回补更稳定。**

### 6.3 `5m` 上不是完全没边，但明显更脆
`5m` 也不是完全没反应，但比 `15m` 弱很多：

- `BTC/ETH` basket 在 `5m` 上最稳定的一档，大致只有 **`+0.52 ~ +0.86 bps / trade`**；
- 只有很极端的正向 shock（例如 `z > 2`）时，才会出现约 **`+3.12 bps / trade`** 的单档结果，但事件数只剩 **`86`** 次，稳定性明显差。

翻成人话：

> **它不是最适合抢 `1m/3m` 的 ultra-fast lane，当前更像“美股 proxy 冲击 -> crypto 下一个 15m bar 回吐”的节奏。**

### 6.4 反过来追 proxy，当前样本整体是负的
如果你按 repo 最直觉的方向去追：

- `15m` 的 aligned sign 版本，`BTC/ETH` basket 大约是 **`-0.73 bps / trade`**；
- 阈值筛过之后也大多仍是负的。

这恰恰说明这轮最重要的不是“repo 写了 proxy 看多 BTC”，而是：

> **当同一份材料在 short-cycle 上跑出反向结果时，应该尊重 portability probe，而不是尊重故事。**

## 7. 对当前 desk，最合理的策略化落点是什么
### 7.1 最小可执行版本
先别做太花，最小版就够：

- **交易标的：** `BTCUSDT`, `ETHUSDT`
- **信号频率：** `15m`
- **信号源：** `COIN/MARA/RIOT` 的 `5m` 等权 proxy basket
- **Admission：** 仅在美股常规时段重叠窗口内启用
- **Trigger：** `proxy_z_15m > 1.0`
- **Entry：** 下一根 `15m` 开盘，做空 `BTC/ETH` 等权 basket
- **Exit：** 持有 1 根 `15m` 后平仓
- **Sizing：** BTC/ETH 等权，或按近窗 realized vol 逆波动配权

### 7.2 为什么当前先不建议把负向 shock 对称上满
因为 probe 已经告诉我们：

- negative shock fade 不是完全没边；
- 但肥度和稳定度都明显弱于 positive shock fade。

所以第一版更建议：

> **先把它做成“只做 positive proxy shock fade”的 asymmetric alpha。**

这比一上来硬做对称 long/short 更诚实。

### 7.3 成本怎么想
这条线目前看到的毛边大概在：

- basket `+3.61 bps / trade`
- BTC 单腿 `+3.38 bps / trade`
- ETH 单腿 `+3.84 bps / trade`

所以它很明显是：

- **低成本才能舒服活**；
- `2 bps` 级别 round-trip 还有希望；
- `4 bps` 左右的粗糙全 taker round-trip，边际就会很薄。

正确姿势更像：

- 低费率账户；
- 尽量别在最差流动性点追单；
- 或者把它先当成 **alpha admission / side router**，再嫁接到现有 execution layer。

## 8. 它跟 `1m / 3m / 5m / 15m` 的关系到底怎么理解
这条线并不是那种天然应该先落在 `1m` 的 order-flow 信号。

更合适的理解是：

- **数据更新端** 在美股 `5m`；
- **市场消化端** 在 crypto 更像下一个 `15m`；
- 因此首轮应该把它当 **`15m` cross-asset event alpha**。

如果后面要往更快频率压，建议顺序是：

1. 先检查 `proxy shock` 是否主要集中在**美股开盘后前 60~90 分钟**；
2. 再拆 `open-drive`、`midday`、`close-ramp` 三个 session bucket；
3. 最后才考虑 `3m` 甚至 `1m` 的事件窗。

别一上来就全频率铺开。

## 9. 下一步怎么测
这轮不是“知道个故事”就算完，下一步很明确：

### 9.1 先做 session bucket
把事件分成：

- 美股开盘后 `0~90m`
- 中段
- 临近收盘

看 edge 是不是主要来自开盘拥挤翻译，而不是全天平均现象。

### 9.2 做单腿 vs 双腿 vs BTC-only
当前 `BTC`、`ETH` 都有边，但结构不完全一样：

- BTC 更像更稳一点；
- ETH 毛边略厚。

下一步应直接比较：

- BTC-only
- ETH-only
- BTC/ETH 50-50
- inverse-vol basket

### 9.3 做 threshold / hold 网格
先把这 6 组固定测出来：

- `z > 0.75 / 1.0 / 1.25 / 1.5`
- `hold = 1 / 2 / 3` 个 `15m`

重点看：

- mean bps/trade
- post-cost net bps/trade
- hit rate
- time-to-mean-revert

### 9.4 加入“只做正向 shock”与“news veto”
因为这条线当前主要赚钱的是 **positive proxy shock fade**，所以应额外加两层检查：

1. **只做正向 shock**，别强求对称；
2. **避开 COIN/MARA/RIOT 自身财报 / 个股特异事件**，防止个股新闻污染“crypto proxy”读法。

### 9.5 和现有线做组合关系检查
尤其建议跟这几类现有线做相关性检查：

- BTC/ETH 自身 `lag-1 sign fade`
- funding crowding fade
- spot/futures gap continuation
- OI quadrant router

如果这条 proxy alpha 跟已有线低相关，它就不只是“又一条 15m fade”，而是**真正补了一个新的信号源**。

## 10. 最后一句判断
如果只问一句“这篇东西值不值得进池子”，我的答案是：**值**。

但值钱的点不是 repo 表面写的“proxy 强 -> BTC 强”，而是我们这轮 public-data probe 明确跑出来的另一层意思：

> **对 short-cycle desk，`COIN/MARA/RIOT` 更像是美股时段里的 crypto 情绪放大器；当它们在 `15m` 内一起猛拉时，下一段 `15m` 的 BTC/ETH perp 更值得先测 fade，而不是盲目追随。**

这条线已经满足进 raw alpha 池的最低标准：

- base alpha 清楚；
- 公开数据可拿；
- `15m` 最小实验可直接复现；
- 可写成明确 entry/exit/sizing/risk/cost 骨架；
- 并且和当前 desk 的 pairs / funding / OFI / XS reversal 池子相比，来源维度是新的。

## 参考来源
1. **zwmjj. (2026). _kuant-strategies_. GitHub repository.**
   - Repo URL: <https://github.com/zwmjj/kuant-strategies>
   - README: <https://raw.githubusercontent.com/zwmjj/kuant-strategies/main/README.md>
   - Key source file: <https://raw.githubusercontent.com/zwmjj/kuant-strategies/main/strategies/crypto_advanced.py>
2. **Yahoo Finance Chart API (public endpoint used for probe).**
   - Example: <https://query1.finance.yahoo.com/v8/finance/chart/COIN?range=60d&interval=5m>
   - Example: <https://query1.finance.yahoo.com/v8/finance/chart/MARA?range=60d&interval=5m>
   - Example: <https://query1.finance.yahoo.com/v8/finance/chart/RIOT?range=60d&interval=5m>
3. **Binance USDⓈ-M Futures public klines API.**
   - Docs/API endpoint family used: <https://fapi.binance.com/fapi/v1/klines>
