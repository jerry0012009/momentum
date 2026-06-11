# 别把这篇 2024 IJFS 论文只读成“ETH 法币 quote 特例”：对 short-cycle desk，更该先测的是「same-underlier multispread mean reversion × optimizer sizing」完整 raw alpha

- 时间：2026-04-03 03:55 UTC
- 类型：2024 IJFS 开放获取论文全文 + arXiv 预印本全文 + Kraken 公共历史数据口径
- 主题标签：raw-alpha/relative-value/stat-arb/same-underlier/multispread/mean-reversion/optimizer-sizing/market-neutral/kraken/eth-fiat/public-data/cost/1m/3m/5m/15m/paper
- 证据类型：paper-based（期刊全文为主，arXiv 预印本与数据源说明为辅）

- 主题类型：raw alpha
- 基础 alpha：**same-underlier multispread mean reversion**；同一标的（论文里是 ETH）在不同 quote bucket 里的相对错价会短暂拉开，再通过 `long cheap leg / short rich leg` 回归，且多条 spread 可同时触发，用一个 optimizer 统一分配仓位。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
### 一句话核心结论
**这篇论文真正值得 desk intake 的，不是“ETH 对不同法币也能做配对”这个表面结论，而是它给出了一条更适合我们迁移到 crypto short-cycle 的完整 skeleton：`同一底层资产的多条相对价差做均值回归，信号层看 spread 偏离，组合层用 optimizer 把重叠腿净额化并做 market-neutral sizing`。**

### 为什么这轮比继续补一个泛 filter 更值得
因为它补的是一条当前素材池里还不算拥挤的 **same-underlier / same-asset relative-value raw alpha**：
- 不是 generic regime gate；
- 不是再来一篇“不同币 cointegration pairs”；
- 而是**同一资产的多腿错价回归**，天然更接近我们后面会做的：
  - `spot vs perp`
  - `perp vs perp cross-venue`
  - `front vs back`
  - `同标的不同 quote / 不同 venue / 不同合成路径`
- 更重要的是，论文不只给 entry/exit，还把 **capital allocation / overlapping spread netting / risk-aversion λ** 一起写了出来，像一条可以直接拆零件复刻的完整策略卡。

### 最关键的硬数据
先记住这几组最有用的数字：
- 交易对象是 **Kraken 上 ETH 对 `USD / CAD / GBP / EUR` 的 spot quote bucket**，从中形成 **`6` 条 spread**；
- formation/screening 期是 **`2018-01-01 ~ 2020-01-01`**，主要测试期包括：
  - bull：`2021-01-01 ~ 2022-01-01`
  - bear：`2022-01-01 ~ 2023-01-01`
  - full-cycle：`2021-01-15 ~ 2022-10-01`
- 论文比较了 `1m / 5m / 60m`；
- 在 **full-cycle + 0.1% fee + λ=1** 下，年化收益约：
  - `1m: 14.87%`
  - `5m: 15.49%`
  - `60m: 5.00%`
- 同样 full-cycle 下，baseline Distance Method 只有：
  - `1m: 5.33%`
  - `5m: 0.60%`
  - `60m: 3.93%`
- full-cycle 的 Sharpe：
  - `OTT λ=1: 0.68`
  - `OTT λ=0.5: 1.11`
  - `DM: -0.41`
- full-cycle `5m` 交易指标：
  - 交易次数 **`12,166`**
  - 胜率 **`54.4%`**
  - win/loss ratio **`1.19`**
  - 平均持仓 **`5.09 小时`**
- 交易成本影响极大：`5m, λ=1` 的 full-cycle 年化收益，**从 `44.98%`（0 fee）掉到 `15.49%`（0.1% fee）**。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这轮 **base alpha 很清楚**：

> **同一底层资产在多条 quote/venue/synthetic 路径上的相对定价不会永远一致；当其中一条腿短时偏贵、另一条腿偏便宜时，做多便宜腿、做空昂贵腿，赌偏离回归。**

论文的写法是 ETH 对多个法币 quote；
对 desk 来说，更重要的抽象层其实是：
- `same-underlier`；
- `multi-spread`；
- `market-neutral`；
- `mean reversion`。

所以它不是：
- filter；
- regime；
- 纯 risk overlay；
- 或“解释 ETH/FX 关系”的综述。

它是一条可以独立站住的 **relative-value / stat-arb raw alpha**。

## 3. 来源信息
### 3.1 主来源
- **Authors**：Hongshen Yang, Avinash Malik
- **Year**：2024
- **Title**：*Optimal Market-Neutral Multivariate Pair Trading on the Cryptocurrency Platform*
- **Venue**：*International Journal of Financial Studies*, 12(3), 77
- **DOI**：<https://doi.org/10.3390/ijfs12030077>
- **Readable URL**：<https://www.mdpi.com/2227-7072/12/3/77>
- **Preprint URL**：<https://arxiv.org/abs/2405.15461>
- **PDF URL**：<https://arxiv.org/pdf/2405.15461.pdf>
- **Repo URL**：N/A（文中未提供公开代码仓库）

### 3.2 数据源
- **Data Source**：Kraken historical OHLCVT
- **Public URL**：<https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data>
- **公开性**：公开可下载
- **更新频率**：交易所历史 K 线 / 成交统计数据，按所选 bar 频率聚合
- **最小可复现实验口径**：同一底层资产在多个 quote / venue / synthetic legs 上，构造相对价差并做 bar 级回归策略。

## 4. 论文到底做了什么
## 4.1 交易对象不是“两种不同币”，而是“同一币的 quote bucket”
论文选的是 Kraken 上同一个底层资产 **ETH**，对四种法币 quote：
- `ETH/USD`
- `ETH/CAD`
- `ETH/GBP`
- `ETH/EUR`

于是能形成 `C(4,2)=6` 条 spread：
- USD:CAD
- USD:GBP
- USD:EUR
- CAD:GBP
- CAD:EUR
- GBP:EUR

翻成人话：
**作者不是在赌 ETH 和 BTC 谁会重连，而是在赌“同一个 ETH，被不同 quote 体系映射出来的相对错位会回归”。**

这点对我们很重要，因为它更像：
- 同币跨 venue；
- 同币 spot-perp；
- 同币 calendar；
- 同币现货直价 vs 合成价。

## 4.2 screening / formation：先验证这个 bucket 真的有相关性与协整基础
作者先用 **`2018-01-01 ~ 2020-01-01`** 的 ETH quote 数据做 formation / screening，按滚动一周去看相关性和 cointegration。

论文 Table 2 给了很直观的基础盘：
- `USD:CAD`
  - `1m` 平均相关 **`0.978`**，cointegration 命中率 **`77.8%`**
  - `5m` 平均相关 **`0.998`**，cointegration 命中率 **`100.0%`**
- `CAD:EUR`
  - `5m` 相关 **`0.980`**，cointegration **`94.1%`**
  - `60m` 相关 **`0.969`**，cointegration **`98.6%`**
- `GBP:EUR`
  - `5m` cointegration **`98.0%`**
  - `60m` cointegration **`91.3%`**

这说明：
**这个 bucket 的 spread 不是瞎编的，至少在 formation 期里，它确实长期呈现“相关且多数时间可视作可回归关系”。**

## 4.3 signal：核心不是 distance，而是 spread z-score 偏离
论文比较了两类东西：
- baseline：**Distance Method (DM)**
- 作者主方法：**Optimal Trading Technique (OTT)**

真正该拿走的不是 DM，而是 OTT 里的这条 raw alpha 逻辑：
1. 先把同一底层资产在多个 quote 下的价格序列标准化；
2. 对每条 spread 计算相对偏离；
3. 当某条 spread 的 z-score 超过开仓阈值时，
   - 做多便宜腿
   - 做空昂贵腿；
4. 当 spread 回到更窄的 close band 时平仓。

论文用的是 **threshold × spread standard deviation** 的开平仓机制。
最赚钱的 grid-search 阈值（Table 3）是：
- `1m`: open=`11σ`, close=`9σ`
- `5m`: open=`9σ`, close=`7σ`
- `60m`: open=`7σ`, close=`6σ`

这些阈值看上去很大，但别误读成“9σ 神奇参数”。
它本质表达的是：
**这个 same-underlier bucket 要吃的是很明显的离群偏差，不是轻微噪音摆动。**

## 4.4 position logic：多条 spread 可以同时触发，所以不能再用“两腿 all-in”的老写法
这是论文最值钱的部分之一。

在普通两资产 pairs 里，信号一来，常见做法是：
- long loser
- short winner
- 这笔单单独处理。

但在 multispread bucket 里会出现：
- `USD:GBP` 触发
- `USD:CAD` 同时触发
- `GBP:EUR` 也可能触发

这时就会有：
- 某个 currency 在不同 spread 中既被 long 又被 short；
- 多条腿重叠；
- 可以互相 net 掉一部分仓位和手续费。

论文明确指出：
**multivariate 的真正增量不是“spread 变多了”，而是“多个 spread 同时触发时，资本分配本身变成了 alpha 生存的一部分”。**

## 4.5 sizing / risk：bi-objective convex optimization 不是 alpha 本体，而是组合层核心组件
论文的 optimizer 目标是：
- **最大化 expected profit**
- **最小化 covariance-based risk**

其 expected profit 不是纯历史均值，而是把：
- 每个 quote 的平均收益 `r`
- 每条 spread 的均值回复速度 `mr`
结合起来，形成 pair-level expected profit。

目标函数再减去 `λ × portfolio variance penalty`。

关键点：
- **alpha 本体** 仍然是 spread mean reversion；
- **optimizer** 是 sizing / risk / capital allocation 层；
- 但因为 multispread 同时触发，**这个 sizing layer 不再只是“锦上添花”，而是策略是否可执行的核心部件**。

论文还加了三个很实用的约束：
1. 单 pair 的 long/short 权重不能超过可用资金；
2. 单一货币层面的总占用不能超过 100%；
3. 回到 ETH 单位后，long 与 short 保持 market-neutral（并考虑交易成本微调）。

翻成人话：
**它不是让你在每条 spread 上各自下注，而是把整个 bucket 当成一个受资金占用约束的 market-neutral 组合来下单。**

## 4.6 交易成本与市场中性假设
成本假设：
- 统一使用 **`0.1%` 每笔 long/short order** 的 flat fee。

论文强调两点：
- 这个策略交易频繁，所以成本很伤；
- 但它尽量避免持有中间 crypto，本意是让组合尽量 market-neutral，而不是裸持有 ETH 趋势风险。

对 desk 而言，这意味着：
- **raw alpha 是有的**；
- 但它能否活下来，高度取决于：
  - fee tier
  - maker/taker mix
  - overlapping legs 能否净额化
  - 实盘滑点。

## 5. 最值得 desk 拿走的，不是 ETH/fiat 特例，而是 “same-underlier multispread OS”
如果只把这篇论文记成“ETH 对法币做多配对”，价值不大。

**真正该拿走的是这三层：**

### 5.1 raw alpha 层：same-underlier relative-value mispricing
这个最容易迁移：
- 不是 ETH/USD vs BTC/USD 这种跨资产；
- 而是同一资产的不同映射路径短时错价。

这天然更适合 desk 的：
- `spot vs perp`
- `perp vs perp cross-venue`
- `front vs back`
- `direct cross vs synthetic cross`

### 5.2 portfolio layer：重叠 spread 统一净额化
很多 raw alpha 回测都默认“每条腿单独开平”，
但同标的多路径里，真实情况往往是：
- 多条 spread 会同时给出方向；
- 很多腿能互相抵消；
- 不做净额化，手续费和名义敞口会被虚增。

论文把这件事明确写成了优化问题，这对实盘特别有用。

### 5.3 risk-preference λ：把同一 alpha 拉成一条 risk/return frontier
论文不是只给一个固定仓位，而是给：
- `λ=2`：更保守
- `λ=1`：中性
- `λ=0.5`：更激进

这给 desk 的启发是：
**很多 same-underlier alpha 未必要靠“换新信号”提升收益，先把 entry 不变、只改 capital allocator，可能就能把策略从普通提升到可部署。**

## 6. 结果里哪些数字最值得记
## 6.1 full-cycle：`5m` 是论文主结果里最像 desk 可迁移的一档
在 `2021-01-15 ~ 2022-10-01` full-cycle，参与资产为 `USD/CAD/GBP/EUR against ETH`：

### OTT（0.1% fee）
- `1m, λ=1`：**`14.87%`**
- `5m, λ=1`：**`15.49%`**
- `60m, λ=1`：**`5.00%`**

### DM（0.1% fee）
- `1m`：`5.33%`
- `5m`：`0.60%`
- `60m`：`3.93%`

这说明：
- 作者主方法不是“稍微好一点”；
- 在 `5m` 上对 baseline 是**显著优势**；
- 而且 **`5m` 比 `60m` 更像甜点区**，这对 short-cycle desk 友好得多。

## 6.2 bull：不是只有熊市避险才赚钱，bull 里也能跑
在 `2021-01-01 ~ 2022-01-01` bull market：
- `5m, λ=1, TC=0.1%`：**`36.75%`**
- 对照 DM：**`19.89%`**
- `1m, λ=1`：`39.85%`
- `60m, λ=1`：`14.18%`

也就是说，
**这条 alpha 不是“只能靠大跌时回归”的熊市特供，它在强趋势 bull 里也能活。**

## 6.3 bear：在 ETH 跌 `-61.84%` 的环境里仍能保正
在 `2022-01-01 ~ 2023-01-01` bear market：
- Buy & Hold：**`-61.84%`**
- `5m, λ=1, TC=0.1%`：**`+4.99%`**
- `1m, λ=1`：`+9.57%`
- `60m, λ=1`：`+9.01%`

这再次说明它的收益来源更像：
- 市场中性 relative-value；
- 而不是单边方向暴露。

## 6.4 risk / Sharpe：最激进的 λ=0.5 反而给出最好 Sharpe
Table 8：
- full-cycle
  - `DM`: Sharpe **`-0.41`**, σ=`0.082`
  - `OTT λ=2`: Sharpe **`0.44`**, σ=`0.104`
  - `OTT λ=1`: Sharpe **`0.68`**, σ=`0.193`
  - `OTT λ=0.5`: Sharpe **`1.11`**, σ=`0.343`
- bull
  - `OTT λ=1`: Sharpe **`2.66`**, σ=`0.126`
- bear
  - `OTT λ=1`: Sharpe **`0.16`**, σ=`0.082`

这里最有意思的是：
**在作者样本里，更激进的 allocator 不只提高收益，连 Sharpe 都提高了。**
这提示我们：
- alpha 本体也许没那么弱；
- 很多利润是被 conservative sizing 压掉的。

## 6.5 trading metrics：不是“年化好看但靠一两笔大单”
full-cycle + `λ=1` + `0.1% fee` 的 Table 9：
- `1m`
  - trade count：**`13,790`**
  - 胜率：`53.2%`
  - avg holding：`4.52h`
- `5m`
  - trade count：**`12,166`**
  - 胜率：**`54.4%`**
  - win/loss ratio：**`1.19`**
  - avg loss：`-$8.67`
  - avg win：`$9.21`
  - avg holding：**`5.09h`**
- `60m`
  - trade count：`1,906`
  - 胜率：`52.6%`
  - avg holding：`16.10h`

这说明策略更像：
**高频率但单笔优势不夸张，靠稳定正期望和腿间净额化生存。**

## 6.6 交易成本真的是生死线
最直观的一组：
- full-cycle `5m, λ=1`
  - `0 fee`: **`44.98%`**
  - `0.1% fee`: **`15.49%`**
- full-cycle `1m, λ=1`
  - `0 fee`: `40.03%`
  - `0.1% fee`: `14.87%`

这轮最不能忽视的结论不是“5m 很强”，而是：
**只要净额化做不好、成本模型写轻了，这条 alpha 会从可交易直接掉回论文收益幻觉。**

## 6.7 Appendix A：同样骨架迁移到 BTC / SOL 仍有结果
作者还在 `2020-10-01 ~ 2024-04-01` 做了 ETH/BTC/SOL 的扩展测试（15m/60m/720m，参与法币为 USD/GBP/EUR）。

Table A2 在 `15m + 0.1% fee + λ=1`：
- ETH：**`22.66%`**
- BTC：**`18.24%`**
- SOL：**`7.42%`**

对应风险指标：
- ETH：σ=`0.151`, Sharpe=`1.24`
- BTC：σ=`0.159`, Sharpe=`0.90`
- SOL：σ=`0.032`, Sharpe=`1.07`

这对 desk 的意义是：
**它不是 ETH 专属现象；但越往流动性差、走势更极端的币种迁移，alpha 会明显变脆。**

## 7. 这轮对当前 desk 的直接意义
## 7.1 它补的不是“又一篇 pairs”，而是同标的相对价差这条原型
当前 digest 池里已经有很多：
- 不同币的 cointegration pairs；
- cross-sectional reversal / momentum；
- funding / basis carry；
- PCA residual stat-arb；
- cross-venue spread。

但这篇论文的新增值在于：
**它把“同一底层资产的多路径价差回归”单独写成了一条完整策略，并把重叠腿优化分配明确建模。**

所以它更像是：
- `spot-perp / perp-perp / calendar / synthetic cross` 的共用母版；
- 而不是又一条 generic 两资产 pairs 变体。

## 7.2 为什么它比继续补一个 overlay 更值得
因为它直接服务于：
- **raw alpha 素材池**；
- **relative-value / stat-arb 复现池**；
- **完整策略组件拆解**；
- **资本分配层研究**。

如果今天继续写一个 crowding gate 或 macro veto，当然也能加知识；
但和这篇相比，**对“下一步能不能马上测一个新 raw alpha”帮助没这么直接。**

## 8. 对 `1m / 3m / 5m / 15m` 的 desk 化映射
## 8.1 最自然的映射不是照抄 ETH 法币，而是改成同标的多路径 bucket
对于我们，最自然的映射对象是：
- **单 venue**：`spot vs perp`、`front vs back`
- **跨 venue**：`Binance perp vs Bybit perp`、`Binance spot vs OKX perp`
- **合成路径**：`ALTBTC 直价 vs ALTUSDT / BTCUSDT 合成价`

也就是说，论文里的法币 quote bucket 只是载体；
**真正可迁移的是 same-underlier multispread 框架。**

## 8.2 bar 频率如何映射到 `1m / 3m / 5m / 15m`
论文是 `1m / 5m / 60m`。
对 desk 我更建议：
- `15m`：做主回测频率，先验证策略是否 still alive；
- `5m`：做主信号频率，因为论文里 5m 是最像甜点区的一档；
- `3m`：做“更积极但仍可控”的压缩测试；
- `1m`：主要留给执行与净额化更新，不建议一开始就拿它做最终策略频率。

原因很简单：
- 论文的 `1m` 虽有收益，但成本压力极大；
- 我们真实 crypto 环境比 Kraken ETH 法币更 noisy；
- 所以先在 `5m/15m` 站住，再压到 `3m/1m` 更稳。

## 8.3 论文里的 threshold 不能直接照搬，但“极端偏离才动”这个精神应该保留
论文的最佳阈值达到 `7σ~11σ`，这在 perp 市场未必应原样照抄。
更合理的 desk 化做法是：
- 先试 rolling z-score `2.0 / 2.5 / 3.0 / 4.0`
- 再试 percentile entry（如 `97.5% / 99%`）
- 再比较跨腿净额化前后，信号是否仍然赚钱。

该保留的是：
**同标的多路径错价，只有在明显异常偏离时才值得付成本去收敛。**

## 9. 局限与踩坑
### 9.1 场景比 desk 真实环境更“干净”
论文场景是：
- 同一交易所；
- 同一底层资产；
- 主要是 quote 体系差异；
- 没有典型跨 venue transfer / latency / funding settlement 风险。

所以它天然比真实 perp/cross-venue 好做。

### 9.2 成本模型仍然偏粗
统一 `0.1%` flat fee：
- 对某些 maker 场景可能偏高；
- 对双腿不同时成交、滑点不对称、排队失败场景又可能偏低。

### 9.3 阈值有数据挖掘风险
论文明确做了 retrospective grid search 来找最赚钱的 `open_threshold / close_threshold`。
这能给我们参数起点，
但不能直接当 live 最优参数照抄。

### 9.4 市场制度差异
法币 quote bucket 的错误定价机制，和：
- perpetual funding
- mark/index 机制
- ADL/强平链
- cross-venue inventory frictions
并不完全相同。

所以它更像**结构原型**，不是现成 prod 配方。

## 10. 可复刻的最小实验
### 实验 A：先做 same-underlier 双腿 baseline
- **对象**：BTC / ETH / SOL 的 `spot-perp` 或 `perp-perp cross-venue`
- **bar**：`5m` 主频，补 `15m` 与 `3m`
- **spread**：
  - 价格差 / 对数价差
  - 或 annualized basis diff
- **entry**：rolling z-score `2.5 / 3.0 / 4.0`
- **exit**：回到 `0~0.5σ`
- **sizing**：equal-dollar market-neutral
- **cost**：至少三档 round-trip friction：`4 / 8 / 15 bps`

先回答：
**same-underlier mispricing 在我们现在可拿到的公共数据下，到底有没有 after-cost alpha。**

### 实验 B：从双腿升级到 bucket-neutral multispread
在同一标的上放入三到四条路径，例如：
- `Binance perp`
- `Bybit perp`
- `OKX perp`
- `spot synthetic`

然后比较：
1. **pair-by-pair 独立开仓**
2. **统一 optimizer 净额化**

关键指标：
- net exposure
- capital utilization
- realized fee drag
- after-cost Sharpe
- concurrent-leg overlap ratio

这一步专门验证：
**论文最值钱的 optimizer layer 到底是不是实盘增量。**

### 实验 C：把 λ 当成 sizing frontier，而不是信号参数
固定信号，只改 allocator：
- `λ_high`
- `λ_mid`
- `λ_low`

观察：
- return
- volatility
- Sharpe
- max drawdown
- fill pressure

如果 desk 版本也出现“更激进 allocator 连 Sharpe 都更高”，那说明：
**alpha 本体比我们想象得更强，问题更多在执行层与容量层。**

### 实验 D：做 honest cost ablation
最少要拆四层：
1. maker-only fantasy
2. maker/taker 混合
3. 双腿不同时成交
4. overlap netting 前 vs 后

因为这篇论文已经明确告诉我们：
**这条策略不是先看 gross alpha，再顺手加成本；而是成本从第一天就是主角。**

## 11. 下一步怎么测
1. **先做 `same-underlier` baseline，不要上来就跑 generic pairs。** 这篇最有价值的就是同标的多路径错价，不是跨币 cointegration。
2. **优先测 `5m + 15m`，`3m` 次之，`1m` 最后。** 论文结果和成本敏感性都在提醒我们，不要一上来冲最细 bar。
3. **一定做“独立 pair 开仓” vs “统一 optimizer 净额化”对照。** 这决定我们是不是只是在重做旧 pairs，还是在复现它真正的新东西。
4. **先用最液态的大币。** BTC/ETH/SOL 或主流 perp venue 足够；别一开始就扩到小票。
5. **把资金占用和重叠腿暴露写进回测。** 否则很多 bucket strategy 回测只是名义上 market-neutral，实际不是。

## 12. 一句话给当前项目的结论
**这篇 2024 IJFS 论文值得进池，不是因为它又证明了“配对交易有用”，而是因为它把一条很适合 short-cycle desk 迁移的 raw alpha 骨架写清了：`same-underlier multispread mean reversion` 负责出信号，`optimizer-based netting/sizing` 负责让这条信号在多腿重叠与成本压力下仍有机会活下来。**

## 13. 来源链接
- DOI：<https://doi.org/10.3390/ijfs12030077>
- Journal page：<https://www.mdpi.com/2227-7072/12/3/77>
- arXiv：<https://arxiv.org/abs/2405.15461>
- PDF：<https://arxiv.org/pdf/2405.15461.pdf>
- Kraken historical OHLCVT：<https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data>
