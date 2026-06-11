# 别把这份 2026 新 repo 只读成“4h 组合回测好看”：对 desk 更该先测的是「trend continuation × pullback re-entry × correlation-budget shell」完整 raw alpha
- 时间：2026-03-29 22:42 UTC
- 类型：2026 GitHub 新仓库 + README/source audit + repo 内置回测/validation 输出复核
- 主题类型：raw alpha
- 基础 alpha：**bull-regime breakout continuation**；pullback 只是同一条趋势 alpha 的更优再进场层，不是另起一条独立 alpha
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/pullback/continuation/single-asset/portfolio-shell/correlation-gate/risk-budget/pyramiding/majors/15m/5m/1m/3m/repo/paper/public-data/cost
- 证据类型：源码规则 + repo 报告的回测/走前验证结果

## 1. 这次看了什么
这次看的是 **azuzxx9-jpg（2026）** 的 GitHub 仓库 **Quant Trade System v1**。它表面上像一个“4h 多币种趋势系统”，但真正对 desk 有价值的，不是它的年化曲线截图，而是它已经把一条 **可直接拆成 entry / exit / sizing / risk / cost** 的 raw alpha 骨架写全了：

- alpha 本体是 **bull regime 里的 breakout continuation**；
- pullback sleeve 不是另起炉灶，而是给同一条趋势 alpha 提供 **回撤再进场**；
- 更关键的是，repo 已经把很多 desk 真会碰到的东西显式工程化了：**相关性闸门、sleeve risk budget、组合 gross exposure、drawdown 降杠杆、score-based sizing、partial take-profit、ATR trail、pyramiding**。

这比“又一篇解释 trend 为什么有效”的材料更值得进当前素材池，因为它天然就是一套 **完整策略模板**。

## 2. 核心结论
- **一句话结论**：这篇东西的 base alpha 很清楚——**顺着 bull regime 的方向，等 20-bar 突破 + 波动扩张 + 多窗口动量共振，再追同向 continuation**；pullback 只是在趋势还没坏时，用更便宜的位置把同一条 alpha 再做一遍。
- repo 的 trend sleeve 条件很直接：`close > SMA20 > SMA50`、`ADX >= 18`、ATR% 进入近 120 bar 的较高分位、`close` 突破过去 20 bar 高点、`ret20 > 3%`、`ret60 > 5%`。这不是“AI 黑箱”，就是一条可复现的短中窗趋势 continuation state machine。
- pullback sleeve 也很清楚：强趋势背景 (`ADX >= 22`) 下，价格相对 `SMA20` 有一定深度回撤但还没跌穿 `SMA50` 太多，`RSI` 回到 `30~44`，再等一个 rebound bar 重新抬头。**所以 pullback 在这里是 trend alpha 的 entry refinement，不是均值回归本体。**
- 更值钱的是组合外壳：repo 不是“信号来了就全上”，而是显式设置 `risk_per_trade=1.05%`、`max_portfolio_risk=5.5%`、`max_positions=8`、`max_gross_exposure=1.40`，并按 sleeve 分配 `72% trend / 28% pullback` 的风险预算，还用 `90` bar rolling correlation 做候选剔除。这一层对 desk 很实用，因为很多短周期 trend 信号不是死在方向错，而是死在**相关性拥挤 + 同质仓位叠太满**。
- exit 也不是一句“止盈止损自己调”：trend sleeve 在 `2.2R` 先减半、止损抬到 break-even，然后用 `5 ATR` trailing stop 持有趋势，并允许在 `2R` 后做一次金字塔加仓；pullback sleeve 则更短，直接配 `1.8 ATR` target、`56` bar time stop。**这是完整策略，不是只给 entry。**
- repo 报告的 4h 结果本身也值得参考，但只能当“结构有效”的证据，不能直接当 desk 预期：从 `10,000` 到 `28,508.16`，总回报 `185.08%`，最大回撤 `-9.16%`，`389` 个 trade events，trade profit factor `2.4769`；9 个 walk-forward 窗口的平均回报 `2.99%`、平均 PF `1.852`，但中位回报只有 `-0.10%`。这说明它**有 raw edge，也有明显 regime dependence**。

## 3. 为什么和当前项目有关
这轮更该补的是 **可独立落地的 raw alpha**，而不是再补一个解释型 gate。这个 repo 值得写，原因是：

- 最近 intake 里 pairs / carry / relative-value 已经很多，这份材料正好补回 **single-name trend continuation** 这条能直接上线做最小实验的主线；
- 它不是“只会说趋势有效”，而是把 **趋势 alpha + pullback 再进场 + 组合相关性预算** 一次性打包，适合直接拆成 desk 组件；
- 代码已经把很多容易被忽视的实盘细节写出来：drawdown 到 `12%/18%` 自动把风险系数降到 `0.75/0.50`；BTC/ETH 的 symbol scalar 只给 `0.45`，主动压低大币拥挤风险；candidate rank 里直接给高相关标的扣分；
- 它和 `1m/3m/5m/15m` 的关系也清楚：**不是照搬 4h 参数，而是照搬 state machine。** 对短周期 desk，最应该迁移的是“趋势状态 + 突破确认 + pullback 再进场 + 相关性闸门”这套结构，而不是生搬 `ret20 > 3%` 这组 4h 数字。

## 3.5 策略拆解（必填）
- 方向属性：单币趋势 continuation，组合层面做多币种筛选与预算控制
- 基础 alpha：bull-regime breakout continuation
- regime：`close > SMA20 > SMA50` 且 `ADX >= 18`；pullback sleeve 额外要求 `ADX >= 22`
- filter / veto：ATR% 波动扩张分位过滤、候选评分下限、90-bar 平均相关性阈值、cooldown、持仓上限、gross exposure 上限、sleeve risk/notional budget
- risk / sizing / execution overlay：
  - 单笔风险基线 `1.05%`
  - 组合总风险 `5.5%`
  - gross exposure `1.40x`
  - score-based sizing `0.90~1.25x`
  - drawdown scalar：回撤超 `12%` 降到 `0.75x`，超 `18%` 降到 `0.50x`
  - cost 假设：`fee_rate = 4 bps`，进出场 slippage 各 `5 bps`
  - exit：trend `2.2R` partial + `5 ATR` trail + `96` bar time stop；pullback `1.8 ATR` target + `56` bar time stop

## 4. 可复刻的最小实验
先别把它当“4h 系统移植到 5m”，而要当成**状态机迁移**：

- **研究假设**：在主流 perp universe（BTC / ETH / SOL / BNB / XRP / AVAX）里，`15m` 与 `5m` 依然存在可交易的 **trend continuation pocket**；真正能迁移的不是原 repo 的绝对收益阈值，而是“regime → breakout → continuation / pullback re-entry → 相关性预算”的逻辑链。
- **数据源**：Binance / Bybit / OKX 公共 perp klines（公开可得）；不需要专有数据，先从 OHLCV 就能起步。
- **最小实验口径**：
  1. `15m` 做第一轮，`5m` 做第二轮；
  2. 沿用 `SMA20 / SMA50 / ATR20 / ADX14 / RSI14`；
  3. bull regime 继续要求 `close > SMA20 > SMA50` 与 `ADX >= 18`；
  4. breakout 继续用 `close > HH20.shift(1)`；
  5. **但把 `ret20 / ret60` 从固定百分比改成 rolling quantile gate**，例如要求 `ret20` 高于近 30 天同频分布的 `70%` 分位、`ret60` 高于 `65%` 分位，避免把 4h 的 `3%/5%` 生搬到 15m/5m；
  6. pullback sleeve 改成 ATR 归一口径：`close - SMA20` 落在 `[-1.8, -0.6] ATR` 区间、`close >= SMA50 - 0.8 ATR`、`RSI 30~44`、再等一根 rebound bar。
- **entry / exit**：
  - entry：信号 bar 收盘确认，下一 bar 开盘进；
  - trend exit：先测 repo 原版 `2.2R partial + ATR trail`；
  - pullback exit：先测固定 `1.5~1.8 ATR` target；
  - 两条 sleeve 都保留 `time stop`，优先看 `24/48/96 bar` 三档。
- **sizing / risk / cost**：
  - 先复刻 repo 的风险壳：单笔风险 `1%`、组合风险 `5~6%`、gross exposure `1.2~1.4x`；
  - 先做两层 friction：`low-friction`（maker 偏多）与 `repo-friction`（4bps fee + 5/5bps slippage）；
  - 保留 correlation gate，但把阈值网格化：`0.70 / 0.82 / 0.90`。
- **先看什么**：
  1. trend sleeve 单独的 signal density 与 hold-time；
  2. pullback sleeve 是否真的提升 entry quality，还是只是把趋势信号重复做一遍；
  3. correlation gate 打开/关闭后，净收益与 tail loss 有没有明显改善；
  4. `15m` 与 `5m` 哪个在成本后更诚实。

## 5. 风险与边界
- repo 的原始证据全部来自 **4h 多币种回测**，不能直接推断到 `5m/15m`；这篇值得 intake 的，是结构与组件，不是原始收益数字。
- 它目前只有 **long sleeves**，没有对称 short leg。对 desk 来说，这意味着第一轮更像“多币顺势 alpha + 组合预算控制”，不是标准 market-neutral book。
- pullback sleeve 很容易被误读成 mean reversion。这里要钉死：**它不是跌了就抄底，而是在 bull regime 未破坏时，对同一条趋势 continuation 做更便宜再进场。**
- 相关性闸门是这篇最值得搬的部分之一，但也最容易被误调：阈值太紧会错过强趋势群发，太松又会把组合做成同一笔 BTC beta 的不同名字。
- repo 的 fee/slippage 比较粗；正式 desk 版必须分开估计 maker / taker、队列损失、夜间流动性空洞，不然 5m 很容易被纸面 edge 欺骗。

## 6. 来源
1. **azuzxx9-jpg (2026), _Quant Trade System v1_**  
   - Venue: GitHub repository  
   - DOI: N/A  
   - Readable URL: https://github.com/azuzxx9-jpg/quant-trade-system-v1  
   - Repo URL: https://github.com/azuzxx9-jpg/quant-trade-system-v1  
   - 关键源码：  
     - https://raw.githubusercontent.com/azuzxx9-jpg/quant-trade-system-v1/main/README.md  
     - https://raw.githubusercontent.com/azuzxx9-jpg/quant-trade-system-v1/main/main.py  
     - https://raw.githubusercontent.com/azuzxx9-jpg/quant-trade-system-v1/main/src/strategies/trend_long.py  
     - https://raw.githubusercontent.com/azuzxx9-jpg/quant-trade-system-v1/main/src/strategies/pullback_long.py  
     - https://raw.githubusercontent.com/azuzxx9-jpg/quant-trade-system-v1/main/src/portfolio.py
2. **Xu, Li, Singh, Li (2023/2024 working paper), _Cross-Market Intraday Time-Series Momentum_**  
   - Venue: SSRN / working paper  
   - DOI: https://doi.org/10.2139/ssrn.4651331  
   - Readable URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4651331  
   - Repo URL: N/A
3. **Moskowitz, Ooi, Pedersen (2012), _Time Series Momentum_**  
   - Venue: Journal of Financial Economics  
   - DOI: https://doi.org/10.1016/j.jfineco.2011.11.003  
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X11002613  
   - Repo URL: N/A

## 7. 下一步怎么测
第一步不要整套移植，也不要一上来就在 `1m` 硬怼。

1. 先在 `15m` 主流 perp 上把 **trend sleeve 单独跑出来**，只测 `bull regime + breakout + quantile-momentum gate`；
2. 再加 pullback sleeve，看它是提高胜率/盈亏比，还是只是提高换手；
3. 保留 repo 的 **correlation-budget shell** 做 on/off 对照，验证它到底是在减噪，还是在白白砍掉最好机会；
4. 只有当 `15m` 在 conservative friction 下还能留边，才下钻到 `5m`；
5. 如果 `5m` 成本后崩掉，就别再执着追更快频，直接把这条线定位成 **`15m` 主信号 + `5m` execution timing**，而不是硬说它是 1m alpha。
