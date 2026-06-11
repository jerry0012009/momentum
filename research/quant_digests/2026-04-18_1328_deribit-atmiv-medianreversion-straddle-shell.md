# 别把这份 Deribit thesis repo 只读成“期权学位作业”：对 short-cycle desk，更该先测的是「ATM IV 偏离自身长跑中位数 × delta-neutral straddle 回归」这条 options raw alpha 壳
- 时间：2026-04-18 13:28 UTC
- 类型：2021 MSc thesis repo source audit（2025 仍有维护痕迹）+ Deribit 公共 `5m` DVOL / perp portability probe
- 主题类型：raw alpha
- 基础 alpha：短天期 ATM implied volatility 相对其自身滚动中位数出现极端偏离后，后续更倾向向长期中枢回归；因此可在 **IV 偏低时做多 delta-neutral ATM straddle、IV 偏高时做空 delta-neutral ATM straddle**，赚取隐波回归而非方向预测。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / options / implied-volatility / mean-reversion / delta-neutral / straddle / volatility-trading / deribit / btc / eth / 5m / 15m / repo / thesis / public-data / cost / risk
- 证据类型：repo 源码 + 公开数据 portability probe

## 1. 这次看了什么
这次看的主材料是 GitHub 仓库：
- **Matteo Bottacini (2021)**, *Cryptocurrency Derivatives Pricing and Delta-Neutral Volatility Trading*（USI MSc thesis repo）
- Repo：<https://github.com/bottama/cryptocurrency-derivatives-pricing-and-delta-neutral-volatility-trading>
- Readable URL：<https://github.com/bottama/cryptocurrency-derivatives-pricing-and-delta-neutral-volatility-trading/blob/main/README.md>

我重点看了：
- `README.md`
- `DeltaHedging/README.md`
- `DeltaHedging/reports/delta-neutral-trading-strategy.md`
- `DeltaHedging/src/variables.py`
- `DeltaHedging/src/utils.py`
- `DeltaHedging/src/backtest.py`

repo 的核心不是“预测 BTC 下一根涨跌”，而是：
> **用 Deribit option chain 的 ATM IV 偏离做 long/short straddle，再用标的做 delta hedge。**

这和我们 4/15 那篇 `IV vs RV carry` 不是一回事：
- **那篇的 base alpha**：`IV 高于 trailing RV -> short vol carry`
- **这篇的 base alpha**：`IV 偏离自身长跑中枢 -> IV mean reversion`

也就是说，这篇不是再写一遍 `IV-RV carry`，而是补一个更“纯隐波时序回归”的 options raw alpha 壳。

## 2. 先回答：这篇东西的 base alpha 是什么？
一句话：

> **短天期 ATM implied vol 对其自身 long-run value 有均值回归；当 IV 处于分布左尾时做多波动率，当 IV 处于分布右尾时做空波动率，再用 perp / underlying 做 delta-neutral。**

所以它是：
- 不是 filter
- 不是 regime gate
- 不是单纯 risk overlay
- 而是一个可以独立下单、独立回测的 **options raw alpha**

## 3. repo 真正在交易什么
### 3.1 源码里的信号骨架
`DeltaHedging/src/utils.py` 的做法很直接：
1. 取 Deribit option data；
2. 从 `instrument_name` 解析 strike / maturity；
3. 每 `5min` 对齐时间戳；
4. 对 call 侧计算：
   - `target_iv = df_calls['mark_iv'].median()`
   - `difference = mark_iv - target_iv`
5. 按 `difference` 分位数给信号：
   - `difference <= q(0.5 - quantile_iv)` → **long vol**
   - `difference >= q(0.5 + quantile_iv)` → **short vol**

默认参数在 `variables.py`：
- `lag = 1` → 信号后 **5 分钟**入场
- `quantile_iv = 0.4` → 实际是取 **10% 左尾 / 10% 右尾**
- `fee = 0.06`
- `margin = 0.5`
- `transaction_cost = 0.06`

### 3.2 交易结构不是“看 IV”，而是“做 straddle + delta hedge”
`backtest.py` 里把交易拆成 3 条腿：
- long/short call
- long/short put
- underlying 对冲腿

再通过 option delta 合成出 underlying 对冲权重，形成 **delta-neutral straddle**。所以这不是抽象的“vol score”，而是完整策略壳：
- 有 entry
- 有持仓延续逻辑
- 有 short leg collateral / margin 假设
- 有交易成本
- 有组合净值

### 3.3 desk 化后最值得保留的那部分
repo 原版是一个**对称 long-vol / short-vol**框架。
但对我们这个 short-cycle desk，最值得先拆出来测的不是“完整照抄对称版”，而是：

> **先保留“IV 偏高 → short delta-neutral straddle”这半边，long-vol 那半边先不要默认相信。**

原因不是主观偏好，而是我下面用 Deribit 公共数据做的 `5m` 便携性快检里，**rich-IV short-vol 的证据显著强于 cheap-IV long-vol**。

## 4. public-data portability probe：先不拉整条 option chain，也能先验一下这条思路
### 4.1 数据源、公开性、更新频率
这轮最小实验没有直接回放全链 option mid，而是先用公开 Deribit 数据做 portability probe：

1. **Deribit volatility index API**
   - Endpoint：`public/get_volatility_index_data`
   - 公开性：公开可得
   - 更新频率：可分钟级抓取
   - 用途：作为 BTC / ETH 短天期隐波状态代理（DVOL / ETHVOL）

2. **Deribit perpetual chart API**
   - Endpoint：`public/get_tradingview_chart_data`
   - 公开性：公开可得
   - 更新频率：`5m`
   - 用途：给后续 realized move 做 proxy

### 4.2 最小实验口径
我取了 **近 14 天 Deribit 公共数据**，把 DVOL / ETHVOL 从 `1m` 聚合到 `5m`，并和 `BTC-PERPETUAL` / `ETH-PERPETUAL` 的 `5m` 收盘价对齐。

定义：
- `iv_z_1d = (IV - rolling_median_1d) / rolling_std_1d`
- 若 `iv_z_1d <= -1`：记为 **cheap IV / long vol** 候选
- 若 `iv_z_1d >= +1`：记为 **rich IV / short vol** 候选
- 观察窗口：
  - `12 bars = 1h`
  - `48 bars = 4h`

我看两个 proxy：
1. **IV mean-reversion proxy**：
   - `side * next_iv_change`
   - long-vol 希望后续 IV 上升；short-vol 希望后续 IV 下降
2. **realized-gap proxy**：
   - `side * (next_abs_return - implied_1sigma_move)`
   - long-vol 希望后续 realized move 超过隐波给出的预期；short-vol 希望 realized move 低于隐波定价

产出文件：
- `reports/artifacts/quant_digests/2026-04-18_deribit_dvol_mr_summary.csv`
- `reports/artifacts/quant_digests/2026-04-18_deribit_dvol_mr_events.csv`

### 4.3 结果：对称 long/short 不值得直接照抄，rich-IV short-vol 更像 desk first branch
#### BTC
- **cheap IV / long vol**（`n=1175`）
  - `1h` IV mean-reversion proxy：`-0.013 vol pts`，win rate `42.6%`
  - `1h` realized-gap proxy：`-14.9 bps`，win rate `20.0%`
  - `4h` IV mean-reversion proxy：`-0.006 vol pts`，win rate `39.3%`
  - `4h` realized-gap proxy：`-29.8 bps`，win rate `20.1%`
- **rich IV / short vol**（`n=851`）
  - `1h` IV mean-reversion proxy：`+0.042 vol pts`，win rate `56.2%`
  - `1h` realized-gap proxy：`+19.6 bps`，win rate `81.9%`
  - `4h` IV mean-reversion proxy：`+0.174 vol pts`，win rate `70.0%`
  - `4h` realized-gap proxy：`+36.8 bps`，win rate `82.0%`

#### ETH
- **cheap IV / long vol**（`n=1079`）
  - `1h` IV mean-reversion proxy：`+0.003 vol pts`，win rate `43.6%`
  - `1h` realized-gap proxy：`-31.4 bps`，win rate `12.6%`
  - `4h` IV mean-reversion proxy：`+0.015 vol pts`，win rate `42.5%`
  - `4h` realized-gap proxy：`-56.2 bps`，win rate `17.5%`
- **rich IV / short vol**（`n=1029`）
  - `1h` IV mean-reversion proxy：`+0.017 vol pts`，win rate `52.3%`
  - `1h` realized-gap proxy：`+32.3 bps`，win rate `85.6%`
  - `4h` IV mean-reversion proxy：`+0.044 vol pts`，win rate `55.6%`
  - `4h` realized-gap proxy：`+51.5 bps`，win rate `81.3%`

### 4.4 first verdict
如果只问“这条 repo 原样是否能直接照抄成对称 long/short vol 策略？”

我的答案是：**不建议。**

如果问“它里面有没有值得我们 desk 单独 intake 的 raw alpha 分支？”

我的答案是：**有，而且优先是 rich-IV short delta-neutral straddle 这半边。**

更直白地说：
- `cheap-IV long-vol`：这轮公开数据快检里明显偏弱
- `rich-IV short-vol`：BTC 最强，ETH 次之
- 所以值得落地的 first branch 更像：
  - **BTC 优先**
  - **5m 监控、1h~4h 持有 / 早退**
  - **IV rich admission → short delta-neutral straddle**

## 5. 为什么这轮值得写它，而不是继续补一个通用 filter
因为它满足当前优先级最高的一档：

1. **能清楚回答 base alpha 是什么**
   - 不是“状态确认”
   - 不是“风控层”
   - 就是隐波偏离后的回归

2. **可独立复现**
   - Deribit public API 可以先做 proxy 版
   - 再往前一步就能直接切到 option chain / ATM straddle mid

3. **可直接落地成完整策略**
   - 交易对象：next Friday / `5d~9d` short-dated ATM straddle
   - 对冲对象：BTC / ETH perp
   - 时钟：`5m` 监控 + `1m~5m` delta refresh
   - 成本：option bid-ask + option fee + perp hedge fee + funding + 滑点

4. **补的是当前池子里相对少的一块**
   - 最近 raw alpha 很多是 `spot/perp relative-value / order-flow / momentum / microstructure`
   - 这篇补的是 **options-vol mean reversion**，不是同类重复

## 6. desk 化后的最合理策略定义
### 6.1 我建议的第一版，不要照搬对称 long/short
**主题类型：raw alpha**

**基础 alpha：**
`ATM IV rich to its own rolling median -> forward IV / realized move tends to underperform implied pricing -> short delta-neutral straddle has edge`

### 6.2 交易对象
- 交易所：Deribit
- 合约：BTC 优先，其次 ETH
- 期权：next Friday 或 `5d~9d` 到期 ATM straddle
- 对冲：对应 perp

### 6.3 entry
先用更 desk 化的 admission，而不是 repo 那种全体分位数照抄：
- `IV_z_1d >= +1.0` 或更严格 `+1.5`
- 只做 **short vol** 第一版
- 尽量避开宏观大事件前 `2~4h`
- 若 skew / term-structure 异常撕裂，先 veto

### 6.4 exit
- 主动止盈：`IV_z_1d` 回落到 `0~0.5`
- 时间止盈：持有 `1h~4h` 后强制评估
- 到期约束：剩余到期 `<24h` 不留仓
- 风险止损：
  - 单腿 / 组合 gamma 损失超阈值
  - realized move 明显超过 entry implied move
  - perp hedge 滑点 / funding 恶化

### 6.5 sizing
别按名义本金裸卖；按以下三层控：
- target vega
- max gamma / max gap loss
- max hedge turnover

### 6.6 主要成本
- option spread
- option taker / maker fee
- perp hedge fee
- funding
- 高频对冲滑点

## 7. 这条 alpha 和 `1m/3m/5m/15m` 的关系
不要因为它是 options 就误判成“和 short-cycle desk 无关”。

更准确的理解是：
- **alpha 定义层**：`5m` 最合适
- **对冲层**：`1m~5m`
- **风险 veto / 早退层**：`5m/15m`

也就是说，它不是逐 bar 方向预测，但完全是 **short-cycle execution + risk management** 驱动的完整策略。

## 8. 风险与保留意见
1. **这轮 still 是 proxy，不是真正 option fill-PnL**  
   还没进入真实 mid / spread / depth / fill rule 回放。

2. **short vol 怕 jump / event risk**  
   即便平均 edge 为正，也容易被单次爆波吞掉。

3. **DVOL 不是你成交的那张 straddle**  
   下一步必须切到固定到期、固定 moneyness 的真实 option chain。

4. **cheap-IV long-vol 这半边暂时不要先信**  
   至少这轮 `5m` portability probe 没给出支持。

## 9. 下一步怎么测
### 9.1 第一优先：把 DVOL proxy 升级成真实可交易壳
1. 拉 Deribit option chain；
2. 固定 `5d~9d` 到期、ATM straddle；
3. 每 `5m` 记录：
   - straddle mid-IV
   - straddle mid price
   - bid-ask spread
   - delta / gamma / vega
4. 用 perp 做 `1m~5m` delta hedge 回放真实 PnL。

### 9.2 只先跑 3 个版本
- **A**：repo 对称版（cheap long / rich short）
- **B**：desk 版 rich-IV only short
- **C**：desk 版 rich-IV short + macro/event veto

### 9.3 这 6 个表必须一起出
- gross expectancy
- net expectancy
- max drawdown
- hedge turnover
- spread paid / fill ratio
- event-window loss attribution

### 9.4 若要保留 long-vol，只允许作为二阶段分支
cheap-IV long-vol 先不要作为主策略；只有在以下条件成立时再开二阶段：
- 便宜 IV 多发生在 event aftermath / panic-compression 后
- 且随后 realized move 确实抬升
- 且 option spread 没把 edge 吃光

## 10. 来源信息（尽量写清）
### 主来源
- **Author**: Matteo Bottacini
- **Year**: 2021（repo 在 2025 仍有可见更新痕迹）
- **Title**: *Cryptocurrency Derivatives Pricing and Delta-Neutral Volatility Trading*
- **Venue**: Master of Science thesis, Università della Svizzera italiana (repo 自述)
- **Readable URL**: <https://github.com/bottama/cryptocurrency-derivatives-pricing-and-delta-neutral-volatility-trading/blob/main/README.md>
- **Repo URL**: <https://github.com/bottama/cryptocurrency-derivatives-pricing-and-delta-neutral-volatility-trading>

### 本轮 public-data probe 用到的公开接口
- Deribit volatility index API: <https://docs.deribit.com>
- Deribit public API base: <https://www.deribit.com/api/v2/public/get_volatility_index_data>
- Deribit chart API base: <https://www.deribit.com/api/v2/public/get_tradingview_chart_data>

## 11. 一句话结论
**这篇东西可以进池，但别照抄成“对称 long/short vol 教程”。对 short-cycle crypto desk，更值得先落地的是：`BTC rich-IV relative-to-own-history -> short delta-neutral ATM straddle` 这条 options raw alpha 分支。**
