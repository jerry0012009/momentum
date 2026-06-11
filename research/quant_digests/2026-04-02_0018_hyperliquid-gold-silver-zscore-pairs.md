# 别把这份 2026 Hyperliquid metals repo 只读成“商品对 demo”：对 short-cycle desk，更该先测的是「15m Gold/Silver ratio z-score fade × asymmetric threshold × cooldown shell」这条 pairs raw alpha

- 时间：2026-04-02 00:18 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/pairs/relative-value/stat-arb/mean-reversion/gold-silver/ratio-spread/zscore/asymmetric-threshold/cooldown/hyperliquid/15m/repo/public-data/cost
- 证据类型：2026 GitHub repo source audit（`README.md` + `config.py` + `strategy.py` + `data_manager.py` + `trading.py` + `risk_manager.py` + GitHub API metadata）

- 主题类型：raw alpha
- 基础 alpha：Gold/Silver 相对价格比率在短周期上出现极端偏离后，倾向向滚动均值回归；因此做 `long cheap leg / short rich leg` 的 ratio-spread fade
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = 15m Gold/Silver ratio 的极端偏离回归。**

更具体地说：
- 定义 `spread = SILVER / GOLD`；
- 用过去 `24` 根 `15m` K 线算 rolling mean/std；
- 当 `zscore` 明显偏离零轴时，做相对便宜腿、空相对贵腿；
- 等价差回到中枢附近后平仓。

所以它首先是一条 **raw alpha（relative-value / pairs mean reversion）**，不是纯 filter，也不是单纯 execution 讨论。

## 2. 为什么这一轮值得写它
最近 digest 池里，pairs 方向已经积了不少 **cointegration / OU / funding / basis**。继续补当然可以，但这份 repo 的边际价值在于：

1. **它把 pairs alpha 简化成了最便宜的一层：ratio z-score。**
   不先上 Johansen、不先上 Kalman，也不先搞复杂 hedge ratio，而是先问最基本的问题：
   **“一个直接可交易的相对价格比，是否已经足够给出 15m 的均值回归边？”**

2. **它直接是 `15m`。**
   不需要先把日频论文硬压缩到分钟级，repo 本身就把 bar size 放在 `15m`，和 desk 当前默认口径是对齐的。

3. **它提供了一套很适合当 benchmark 的壳子。**
   如果这条最简单的 ratio-spread shell 都能跑出东西，那么后面再加 cointegration、vol scaling、cost-aware sizing 才有意义；如果连这层都不行，就别急着上更复杂的统计套利壳。

换句话说，这轮值得 intake 的不只是“金银也能配对”，而是：
**它给了我们一个能快速 A/B 的超轻量 pairs baseline。**

## 3. 这次看了什么
### 3.1 主来源
- **Author / Repo owner**：`braveheartcc33`
- **Year**：2026
- **Title**：*HyperHedge* / *Hyperliquid silver/gold pairs trading strategy with Z-score*
- **Venue**：GitHub repository
- **DOI**：无
- **Readable URL**：<https://github.com/braveheartcc33/hyperhedge>
- **Repo URL**：<https://github.com/braveheartcc33/hyperhedge>

### 3.2 GitHub 元数据
- `created_at`: `2026-03-26T00:45:58Z`
- `pushed_at`: `2026-03-26T16:57:18Z`
- `language`: Python
- `description`: `Hyperliquid silver/gold pairs trading strategy with Z-score`

### 3.3 它到底交易什么
repo 交易的是 Hyperliquid 上的：
- `xyz:SILVER`
- `xyz:GOLD`

数据抓取直接走 **Hyperliquid public `candleSnapshot` API**，默认：
- `INTERVAL = "15m"`
- 单次取 `500` 根 K 线
- 主循环默认 `--interval 60`，即每 `60s` 刷一次状态

这意味着它的最小复现实验门槛很低：**公开数据、15m bar、轮询即可。**

## 4. repo 里最值得 desk 拿走的硬规则
## 4.1 signal 很简单：24 根 15m 的 ratio z-score
`config.py` 里核心参数写得非常直白：
- `INTERVAL = 15m`
- `LOOKBACK = 24`
- `ENTRY_SHORT = 2.0`
- `ENTRY_LONG = -2.5`
- `EXIT_THRESH = 0.1`

翻成人话：
- 用最近 `24 x 15m = 6h` 的 spread 历史做滚动标准化；
- 当 `z > 2.0` 时，认为 `SILVER / GOLD` 比率太高，做 **空 Silver / 多 Gold**；
- 当 `z < -2.5` 时，认为比率太低，做 **多 Silver / 空 Gold**；
- 当价差回到中枢附近就平仓。

## 4.2 这份 repo 最值得注意的不是 z-score，而是“不对称”
它不是对称的 `±2` 入场：
- 正向偏离阈值：`+2.0`
- 负向偏离阈值：`-2.5`

平仓也不完全对称：
- 做空 Silver 的仓位：`z < +0.1` 就关；如果从入场 z-score 起算，**回落超过 50%** 也提前止盈
- 做多 Silver 的仓位：`z > -0.1` 就关

这很像一个 desk 里常见、但论文里不一定会写得这么实的判断：
**同一条价差，两边的回归速度和可交易性未必一样，阈值不必强行镜像。**

## 4.3 sizing 不是风光霁月的最优解，但足够做第一轮 admission test
`get_position_size()` 里写的是固定资金占用：
- `position_pct = 0.8`
- 即总资金的 `80%` 用于该组配对
- 两条腿各分一半 notional

默认资金 `10000` 时，相当于：
- 可用资金 `8000`
- 每条腿 `4000`
- 再按实时价格换算成数量

这不是生产级 sizing，但对第一轮研究反而有利，因为它让问题更清楚：
**先看 alpha 本体，再看 sizing 优化。**

## 4.4 它带了两个很实用的小风控：cooldown + leg alignment
repo 还有两个比“入场条件本身”更值得拿走的小部件：

1. **平仓后冷却 `10` 轮**
   - 主循环默认每分钟跑一次
   - `10` 轮大约就是 `150` 分钟内不重开同向/反向新仓（因为信号基于 `15m` bar，实际效果更接近跨多个轮询窗口的冷却）

2. **仓位对齐检查**
   - `MAX_POSITION_IMBALANCE = 0.1`
   - 若两条腿只成交一边，或两边仓位不平衡，会触发 risk check

对 short-cycle desk 来说，这两个部件都很有现实意义：
**很多 pairs 回测不是死在 signal，而是死在重开过快和双腿失衡。**

## 5. 这条线和当前项目为什么直接相关
这不是“商品研究跑题”。

更准确地说，它和当前项目直接相关的地方在于：

1. **它仍然是 relative-value / pairs raw alpha。**
   只是把底层标的换成了 Hyperliquid 上可交易的 Gold/Silver，而不是 crypto-crypto 或 perp-perp。

2. **它提供了一个比 cointegration 更轻的基线。**
   我们最近已经收了很多重统计壳：ADF、Johansen、OU、Kalman、copula、basis normalization……
   这份材料的价值恰恰在于提醒：
   **先用最轻的 spread-z shell 做 benchmark，可能更容易分清 alpha 到底来自哪里。**

3. **它天然能迁移到 crypto-native pairs。**
   例如之后完全可以把同一壳子搬到：
   - BTC/ETH
   - ETH/SOL
   - 同主题 beta pair
   - spot/perp proxy ratio

也就是：
**这份 repo 最值钱的，未必是 Gold/Silver 这对资产本身，而是“15m ratio-z pairs shell”这套最小策略骨架。**

## 6. 但要诚实：为什么我把“可直接落地完整策略”写成“否”
因为它虽然已经给了：
- entry
- exit
- sizing
- 仓位对齐风控
- 实盘轮询框架

但还缺两块 production 必需品：

1. **明确的成本模型**
   - repo 里没有把手续费、滑点、资金费率明确写进回测层
   - 因此我们没法直接判断 after-cost edge

2. **正式的历史回测报告**
   - README 更像系统文档，不是完整绩效报告
   - 所以目前它更适合归类为 **“高可复现 raw alpha 候选”**，而不是“已验证可上线策略”

这不减分，反而是它适合研究池的原因：
**逻辑够清楚，复现够快，但还没到可以直接信它赚钱的程度。**

## 7. desk 化后的最小实验，我建议怎么做
## 7.1 实验 A：先原样复刻 Hyperliquid Gold/Silver 15m shell
目标不是赚多少钱，而是先回答：
**这种最简单的 ratio-z shell，在公开 15m 数据上是否有 gross edge。**

建议口径：
- 市场：Hyperliquid `xyz:GOLD` / `xyz:SILVER`
- bar：`15m`
- spread：`silver_close / gold_close`
- signal：repo 原样 `lookback=24`
- entry：`z > 2.0` / `z < -2.5`
- exit：`+0.1 / -0.1` + 做空腿 `50%` 回落止盈
- sizing：先 equal-notional，两腿各 `50%` of deployed capital
- cost：至少跑 `5 / 10 / 15 bps` 三档 friction ladder
- 评估：Sharpe、Calmar、MDD、trade count、holding time、两边方向拆分

## 7.2 实验 B：把同一壳子迁移到 crypto-native pairs
如果实验 A 连 gross 都不行，就先别迁移；
如果 experiment A 至少显示出可见的回归边，再做这一层：

- 候选 pairs：`BTC/ETH`、`ETH/SOL`、`BTC/total-alt basket proxy`
- 仍先不用 cointegration，只跑 ratio-z
- 目的：看简单壳子在 crypto-native 资产上是否也成立

这一步非常关键，因为它能告诉我们：
**最近很多 pairs edge，到底需要重统计工具，还是简单 spread 标准化就够。**

## 7.3 实验 C：把“不对称阈值”当成主要研究对象，而不是附属细节
我会优先扫这个而不是先扫 100 个别的参数：
- `(+2.0, -2.5)`
- `(+2.0, -2.0)`
- `(+2.5, -2.0)`
- `(+2.5, -2.5)`

因为这份材料真正有信息量的部分，不是“z-score 可做”，而是：
**两边阈值不对称，可能比很多 fancy filter 更重要。**

## 8. 下一步怎么测
**下一步先不要急着加 cointegration / Kalman / OU。先做一个最干净的 A/B：`simple ratio-z shell` vs `heavy stat-arb shell`。**

具体顺序我建议：
1. 原样复刻 Hyperliquid Gold/Silver `15m` 版本；
2. 补一层最基础成本，先看 gross / net 分离；
3. 只扫不对称阈值与 cooldown，不先乱加其他 filter；
4. 若 simple shell 有边，再迁移到 crypto-native pairs；
5. 最后才比较它是否值得升级成 cointegration / OU / dynamic hedge ratio。

一句话版：
**先验证“最轻的 ratio-z pairs 壳子”能不能活，再决定是否值得把更多研究预算花在更重的统计套利层。**

## 9. 一句话结论
这份 2026 Hyperliquid repo 最值得 intake 的，不是“金银配对”这个表面题材，而是：
**它把一条可直接落到 `15m` 的 relative-value raw alpha，压缩成了一个极轻量、可快速复现的 ratio-z baseline；而对当前 desk 来说，最该先测的正是这个 baseline 能不能在成本后活下来。**

## 10. 来源链接
1. **braveheartcc33. (2026). _hyperhedge_. GitHub repository.**  
   Repo: <https://github.com/braveheartcc33/hyperhedge>
2. **README / 系统文档**：<https://raw.githubusercontent.com/braveheartcc33/hyperhedge/main/README.md>
3. **配置文件**：<https://raw.githubusercontent.com/braveheartcc33/hyperhedge/main/config.py>
4. **策略逻辑**：<https://raw.githubusercontent.com/braveheartcc33/hyperhedge/main/strategy.py>
5. **数据层**：<https://raw.githubusercontent.com/braveheartcc33/hyperhedge/main/data_manager.py>
6. **交易层**：<https://raw.githubusercontent.com/braveheartcc33/hyperhedge/main/trading.py>
7. **风控层**：<https://raw.githubusercontent.com/braveheartcc33/hyperhedge/main/risk_manager.py>
