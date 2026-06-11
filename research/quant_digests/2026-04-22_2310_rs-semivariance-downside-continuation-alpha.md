# 别把 realized semivariance 只读成“风控指标”：对 short-cycle crypto desk，更该先拆的是「downside-dominant 1h path continuation」这条 raw alpha

- 时间：2026-04-22 23:10 UTC
- 类型：论文 abstract/metadata audit + Binance USDⓈ-M public-data portability probe（`BTC/ETH/SOL`，`5m -> 15m`，近约 `120d`）
- 主题类型：raw alpha
- 基础 alpha：**过去 1 小时的路径如果明显是“跌出来的波动”（`RS-` 主导），而最近 15m 也在下行，那么后面 4~8 根 15m 往往还有短线延续；这不是单纯高波动，而是 downside continuation state。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/downside-continuation/realized-semivariance/asymmetry/RSplus-RSminus/short-only/binance-perpetual/5m/15m/paper/public-data/cost/risk
- 证据类型：论文摘要页 + public-data first probe

## 1. 这次看了什么

主来源是这篇近 5 年论文：

- **Liu, Zhenya; Lu, Shanglin; Li, Bo; Wang, Shixuan (2023)**
- **Title**：*Time series momentum and reversal: Intraday information from realized semivariance*
- **Venue**：*Journal of Empirical Finance*, 72, 54–77
- **DOI**：<https://doi.org/10.1016/j.jempfin.2023.03.001>
- **Readable URL**：<https://www.sciencedirect.com/science/article/pii/S0927539823000334>
- **Accepted manuscript mirror**：<https://centaur.reading.ac.uk/111035/>

这篇论文的 headline 很容易被误读成“又一篇风控论文”，但它真正值钱的地方是：

> **把最近收益拆成上行半方差（RS+）和下行半方差（RS-）后，价格路径的方向性不再对称。**

对 short-cycle desk 来说，这个不对称性不只是 veto / filter；它也可以直接变成一条 **downside continuation raw alpha**。

## 2. base alpha 到底是什么

先按要求只回答一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：是“最近 1 小时的波动如果主要是跌出来的、而不是涨出来的，那么接下来短窗继续下行的概率更高”。**

所以它不是纯过滤层。
它的 alpha 本体是：
- `RS-` 主导 = 下跌波动占优；
- 配合最近 15m 仍然走弱；
- 做的是 **short continuation**，不是等比例镜像的 long/short 对称策略。

## 3. 为什么这比继续做“总波动门”更值得

因为总波动只告诉你“吵不吵”，不告诉你“是往上吵还是往下吵”。

而 `RS+ / RS-` 这套拆法会告诉你：
- 价格是被 **上涨冲出来的**，还是被 **下跌砸出来的**；
- 同样是高波动，哪边更像 continuation state，哪边更像 exhaustion / reversal state。

翻成人话：
- **涨出来的波动**，不一定适合继续追空；
- **跌出来的波动**，更像可以继续追空的短线状态。

## 4. 最小可复现实验：这轮我是怎么测的

### 4.1 数据源与公开性
- 交易所：Binance USDⓈ-M Futures
- 接口：`fapi/v1/klines`
- 公开性：完全公开可取，无需 API key
- 周期：`5m` 信号，映射到 `15m` 决策窗
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 样本：近约 `120d`

### 4.2 因子定义
在每个 15m 决策时点：
- 用最近 `12` 根 5m bar（=1h）计算：
  - `RS+ = Σ max(r, 0)^2`
  - `RS- = Σ abs(min(r, 0))^2`
- 非对称分数：
  - `A = (RS+ - RS-) / (RS+ + RS-)`
- 只测 **short-only**：
  - 最近 15m bar 为负；
  - 且 `A` 低于阈值（downside-dominant）
- 出场：分别看 `1 / 2 / 4 / 8` 根 `15m` 持有
- 成本：round-trip `6 bps`

### 4.3 本轮产物
- `reports/artifacts/quant_digests/rs_semivariance_shortprobe_20260422_2310/summary.csv`
- `reports/artifacts/quant_digests/rs_semivariance_shortprobe_20260422_2310/basket_summary.csv`

## 5. first verdict：这条线是 raw alpha，不是空洞的风控备注

### 5.1 资产级 pocket
在 `q=0.95`、`hold=8` 根 `15m` 的最强口径下（已含 `6 bps` 成本）：
- `BTCUSDT`：`+27.82 bps / trade`
- `ETHUSDT`：`+42.36 bps / trade`
- `SOLUSDT`：`+76.75 bps / trade`

这已经不是“稍微好看一点”的过滤器，而是能直接撑起一个短空壳的 raw alpha pocket。

### 5.2 basket 级平均
`q=0.95`：
- `hold=4`：平均 **净** `+21.07 bps / trade`
- `hold=8`：平均 **净** `+48.98 bps / trade`

更直白一点：
- `1~2` 根 `15m` 太短，成本吃得比较凶；
- `4~8` 根 `15m` 才开始像样。

### 5.3 为什么我只把它先写成 short-only
因为这个状态的经济含义本来就不对称：
- `RS-` 主导的 state，天然更像 **downside continuation**；
- long 侧不是不能测，而是当前 first pass 没必要把它硬镜像成“同样强”的对称 alpha。

## 6. 这条 alpha 应该怎么用

### 6.1 最像样的壳
- **Universe**：先只做 `BTC / ETH / SOL`
- **Signal**：`1h RS- dominance` + 最近 `15m` 走弱
- **Direction**：short-only
- **Entry**：下一根 `15m` open
- **Exit**：`4~8` 根 time stop，或叠加动量衰减 exit
- **Risk**：单笔固定风险上限，避免连续追空过度堆仓
- **Cost**：如果执行太偏 taker，edge 会明显缩水；更适合 `15m signal -> 5m child execution`

### 6.2 最小晋级标准
下一轮如果要把它从“好看的 short pocket”升级成更稳的主素材，至少要再过三关：
1. `2026-04-22 之后` 再滚一个更长样本；
2. 加入 `BTC/ETH/SOL` 以外的 mid-cap 检查迁移性；
3. 做一次更真实的 child execution / slippage 敏感性测试。

## 7. 风险与边界
- 论文本身是 **intraday information from realized semivariance**，不是 crypto 专门论文；我们迁移的是 **RS+/RS- 非对称路径逻辑**，不是样本数字。
- 这条线现在更像 **short-only continuation pocket**，不要强行包装成“多空对称主策略”。
- 如果把信号降到 `5m` 裸开仓，成本/噪音会更明显；当前更合理的是 `15m` 作为 parent signal。

## 8. 下一步怎么测

1. **先做 `BTC/ETH/SOL` 的分资产净值曲线，而不是只看 basket 平均。**
2. **把 `q=0.95` 与 `q=0.90` 两档分开，检查是否存在稳定的成本前后拐点。**
3. **加入 maker-first / no-overlap child execution，验证 6 bps 不是把利润夸大了。**
4. **测 long side 但只当对照，不要默认镜像。**

## 9. 来源
1. **Liu, Zhenya; Lu, Shanglin; Li, Bo; Wang, Shixuan (2023)**
   *Time series momentum and reversal: Intraday information from realized semivariance*.
   *Journal of Empirical Finance*, 72, 54–77.
   DOI: <https://doi.org/10.1016/j.jempfin.2023.03.001>
   Readable URL: <https://www.sciencedirect.com/science/article/pii/S0927539823000334>
   Accepted manuscript mirror: <https://centaur.reading.ac.uk/111035/>

2. 本轮 public-data probe artifacts:
   - `reports/artifacts/quant_digests/rs_semivariance_shortprobe_20260422_2310/summary.csv`
   - `reports/artifacts/quant_digests/rs_semivariance_shortprobe_20260422_2310/basket_summary.csv`
