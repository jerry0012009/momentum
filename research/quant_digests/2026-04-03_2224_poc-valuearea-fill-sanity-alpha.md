# Rolling POC / Value-Area Displacement：先别把 volume-profile 反转脚本直接当成可交易 alpha

- 时间：2026-04-03 22:24 UTC
- 类型：repo / source audit + local reproducibility check
- 主题标签：raw-alpha/mean-reversion/single-asset/volume-profile/poc/value-area/liquidity-zone/orderbook-proxy/ema200/next-open-fill/15m/5m/3m/1m/repo/public-data/cost/risk
- 证据类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `backtest_poc.py` + `bot.py`）+ repo 附带 `BTCUSDT_15m_real.csv` 本地复核

- 主题类型：raw alpha
- 基础 alpha：价格偏离最近 50 根 bar 构造的 rolling volume-profile POC（成交量重心）后，向 POC / value area 回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但当前 repo 版本不宜直接上线

## 1. 这次看了什么
这次看的是一个 2026-03-22 新 GitHub repo：`berkant1863-netizen/automated-trading-system`。它表面上像“Volume Profile + Point of Control 自动交易 bot”，但对我们 desk 真正有价值的不是“会不会画 POC”，而是这条 base alpha 能不能在 `15m` 上被干净拆成：**rolling POC 锚点 + 偏离入场 + ATR 风控 + 成本生存线**。

一句话先下结论：**base alpha 很清楚，确实是 raw alpha；但 repo 当前版本的优势几乎全部来自过于乐观的成交假设。把 fill model 改 honest 以后，策略会从“看起来像大坑/神迹”同时塌回“接近零边、极易被手续费吃掉”。**

## 2. 为什么这轮值得看它
当前研究池里，pairs / funding / cross-market 已经很密；但 **volume-profile / value-area anchor** 还比较少见。它的好处是：

- 是完整单资产 raw alpha，不只是 filter；
- 直接映射到 `15m`，也能往 `5m / 3m` 压；
- 如果 standalone 不够强，也能退化成 shared feature：`distance_to_POC`、`POC_drift`、`value-area excursion`。

所以这类题值得补进素材池，但前提是先把 **alpha 本体** 和 **执行幻觉** 分开。

## 3. 来源与材料
### 3.1 仓库信息
- Author / Repo：`berkant1863-netizen/automated-trading-system`
- Year：2026
- Repo title：`automated-trading-system`
- GitHub URL：<https://github.com/berkant1863-netizen/automated-trading-system>
- Created at：2026-03-22 21:24:57 UTC
- Repo description：`TC/USDT automated trading bot using Volume Profile and Point of Control strategy with backtesting`

### 3.2 这份 repo 里最关键的文件
- `bot.py`
- `backtest_poc.py`
- `BTCUSDT_15m_real.csv`

### 3.3 数据公开性
- repo 自带公开 CSV：`BTCUSDT_15m_real.csv`
- 样本区间：`2024-06-01 00:00:00` → `2025-07-09 17:30:00`
- bar 数：`38,759` 根 `15m` BTCUSDT bar
- 可复现性：高；即便不信 repo 数据，也能很快换成 Binance public `15m/5m/3m` kline 重跑

## 4. 这条 base alpha 到底是什么
### 4.1 策略骨架
repo 的逻辑很直接：

1. 用最近 `50` 根 bar 的 `high-low` 区间，把每根 bar 的 volume 均匀撒到价格桶里；
2. 找出 volume 最大的价格桶，作为 rolling `POC`；
3. 当当前价格低于 `POC - offset` 时，做多，赌价格回到 POC；
4. 当当前价格高于 `POC + offset` 时，做空，赌价格回到 POC；
5. 风控用 `ATR(21)`：
   - `SL = 1.5 x ATR`
   - `TP = 3.0 x ATR`
6. 仓位：`max($50, capital x 0.5%)`

### 4.2 用 desk 语言翻成人话
这不是 breakout，也不是 order-book imbalance continuation。

它本质上是：

- **一个“成交量重心锚点”均值回归策略**；
- 假设最近一段时间真正有成交密度的“公允区”在 POC 附近；
- 价格一旦离这个公允区太远，就会回摆。

所以它的 base alpha 很清楚：

> **rolling POC displacement fade**

也就是：

> **对“偏离近期成交量重心”的价格做 fade。**

这条线本身就是 raw alpha，不需要借别的 headline 才成立。

## 5. 我做的最小复核
### 5.1 先复现 repo 自己的回测口径
我先按 `backtest_poc.py` 的原始逻辑复现了一遍。关键点是：

- 信号在当前 bar 产生；
- 但成交价直接按 `POC ± offset` 记；
- 不要求下一根 bar 真触到这个价格，也不要求盘口里真的成交；
- 这等于默认你总能在“比当前 mid 更好”的旧价位拿到单。

复现结果：

- 总交易数：`17,796`
- 胜率：`2.83%`
- 总 PnL：`-4,437.13 USD`（初始资金 `10,000 USD`）
- Profit Factor：`0.057`

这和 repo 注释里写的“`Win rate 2-4%`、`SL 96-97%`”基本一致。

### 5.2 一个很关键的诊断：fill model 比 signal 本身还重要
我做了一个故意的 stress test：

- 保持同样的 stale-fill 假设；
- 只是把信号方向反过来（不再 fade，而是 follow）。

结果会直接从“血崩”变成“看起来像神迹”：

- `follow_no_gate`：
  - 交易数：`8,186`
  - 胜率：`88.32%`
  - 总 PnL：`+4,572.94 USD`
  - Profit Factor：`15.87`

这不是在说“POC breakout continuation 真有这么强”，而是在说：

> **同一份数据，只要你允许自己在过期的理想价成交，连信号方向都能被 fill 假设盖过去。**

也就是说，这份 repo 当前最先需要验证的不是“信号精不精”，而是“成交是不是假的”。

### 5.3 换成更 honest 的入场：信号 bar 结束后，下一根 open 入场
我把入场改成更保守、更适合 desk 最小实验的规则：

- 当前 bar 只负责出信号；
- 真正成交发生在**下一根 open**；
- 仍保留 ATR 止损止盈；
- 先不加手续费，只看 gross。

#### A. 仍然做 POC fade，并加最简单 EMA200 同向 gate
- 交易数：`1,481`
- 胜率：`35.92%`
- 总 PnL：`+11.33 USD`
- Profit Factor：`1.045`
- 单笔平均毛利：`0.00765 USD`
- 对应可承受 round-trip 成本阈值：约 `1.53 bps`

#### B. 改成 POC displacement follow，并加 EMA200 gate
- 交易数：`2,472`
- 胜率：`35.40%`
- 总 PnL：`+27.70 USD`
- Profit Factor：`1.067`
- 单笔平均毛利：`0.0112 USD`
- 对应可承受 round-trip 成本阈值：约 `2.24 bps`

### 5.4 这些数字怎么读
关键不是“哪一边略微正”，而是：

- 一旦把 fill model 改 honest，**fade 和 follow 都只剩很薄的 gross edge**；
- 这层毛边大致只够承受 `1.5 ~ 2.2 bps` 的 round-trip 成本；
- 对 crypto perp/spot 的真实 taker 成本来说，基本一加就死；
- 即便 maker-first，也远没到可以放心上线的厚度。

举例：

- `fade + EMA200 + next-open` 在 `2 bps` round-trip 下就会转负；
- `follow + EMA200 + next-open` 大约到 `3 bps` round-trip 也会转负。

所以更准确的判断是：

> **POC displacement 不是完全没信息，但 repo 当前版本的“可交易性”远弱于它展示出来的样子。**

## 6. 对 desk 的真正价值
### 6.1 这条 alpha 还能不能留在池子里
可以留，但**不能以“现成完整策略”心态直接抄**。

更合适的定位是：

- 一级：`raw alpha 候选（待严格执行复核）`
- 二级：`shared feature / shared gate`

### 6.2 更值得保留的不是整套脚本，而是 3 个可复用组件
1. **distance_to_POC**
   - 当前价格离 rolling POC 有多远；
   - 可做 mean reversion 入场强度，也可做 breakout stretch 指标。

2. **POC_drift**
   - 最近若 POC 自己也在快速漂移，说明“公允区”在移动；
   - 这时硬做 fade，往往是在逆着新价值迁移开仓。

3. **value-area excursion state**
   - 价格是刚离开 value area，还是已经离开很久；
   - 可给 breakout、trend、MR 三类壳共用。

### 6.3 我对这份材料的 desk 级判断
如果一定要给一句短判断：

> **这不是“马上上线的 standalone raw alpha”，但它很适合被拆成一个 under-covered 的价量锚点特征族。**

比起继续把它写成“POC 反转 bot”，更值得做的是：

- 用它服务 `mean reversion` 的 admission；
- 用它服务 `breakout/trend` 的 stretch / exhaustion 判别；
- 用真实执行假设先把幻觉挤掉。

## 7. 下一步怎么测
### 7.1 最小实验 1：先把 fill model 做对
同一条信号，至少并排测 4 种成交口径：

1. `signal close -> next bar open`
2. `touch-confirmed limit`
3. `maker-if-touched else skip`
4. `stale POC fill`（只保留作对照，不作 production 结论）

如果 alpha 只在第 4 种活着，那就不是 alpha，是回测假设。

### 7.2 最小实验 2：从 `15m` 压到 `5m / 3m`
建议先测：

- 标的：`BTCUSDT`, `ETHUSDT`
- 周期：`15m`, `5m`, `3m`
- 变体：
  - fade
  - follow
  - fade + EMA200 gate
  - follow + EMA200 gate
  - fade/follow + `POC_drift` veto
- 成本：`0 / 2 / 3 / 5 bps` round-trip

判定标准很简单：

- 若成本阈值始终 `< 3 bps`，降级成 feature，不当 standalone 策略；
- 只有在 `5m/15m` 至少一个桶里能稳定扛住 `>= 5 bps`，才值得继续做 execution 细化。

### 7.3 最小实验 3：把“假的 order-book POC”换成“真的微观结构 POC”
repo 现在的 POC 其实不是 order book 算出来的，而是：

- 把 kline 的 `high-low` 区间按 volume 均匀分桶；
- 这是一个很粗的 **成交量分布 proxy**。

下一步应该拆开测：

- `kline-derived rolling volume profile`
- `1m 聚合成交量 profile`
- `真实 depth snapshot / book ticker` 构造的 book POC

如果只有 proxy POC 有效、真 POC 没效，那就说明它更像 price-path artifact，而不是稳定微观结构信号。

## 8. 这篇东西最后怎么归档
### 8.1 主题归类
- 主题类型：`raw alpha`
- 更细归类：`single-asset mean reversion / value-anchor displacement`

### 8.2 是否进入当前优先复现队列
我的建议：

- **不进 standalone 高优先实盘复现队列**；
- **进 feature / state-variable 候选池**；
- 如果后续做 `5m/3m` breakout 或 short-horizon MR，可以把它当共享输入层复用。

## 9. 来源链接
- Repo：<https://github.com/berkant1863-netizen/automated-trading-system>
- README：<https://raw.githubusercontent.com/berkant1863-netizen/automated-trading-system/main/README.md>
- Backtest script：<https://raw.githubusercontent.com/berkant1863-netizen/automated-trading-system/main/backtest_poc.py>
- Bot source：<https://raw.githubusercontent.com/berkant1863-netizen/automated-trading-system/main/bot.py>
- Public dataset file：<https://raw.githubusercontent.com/berkant1863-netizen/automated-trading-system/main/BTCUSDT_15m_real.csv>

## 10. 最短版结论
这份 2026 volume-profile repo 的 **base alpha 很清楚**：就是 `rolling POC displacement fade`。但最小复核表明，当前脚本的表现高度依赖乐观 fill；把入场改成 next-open 后，fade/follow 都只剩 `1.5~2.2 bps` 量级的毛边，远没到可直接上线的厚度。

所以这轮最值得保留的，不是整份 bot，而是：

- `distance_to_POC`
- `POC_drift`
- `value-area excursion`

把它们当成后续 `mean reversion / breakout / trend` 共用特征，会比继续把这份 repo 当成独立 alpha 更划算。