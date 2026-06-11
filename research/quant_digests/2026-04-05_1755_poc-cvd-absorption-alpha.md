# 别把这份 2026 VPVR+CVD repo 只读成 volume-profile 指标脚本：对 short-cycle desk，更该先测的是「1H POC-proximal price/CVD absorption × 15m child execution」这条 raw alpha

- 时间：2026-04-05 17:55 UTC
- 类型：repo / source audit
- 主题标签：raw-alpha/mean-reversion/single-asset/volume-profile/poc/cvd-divergence/absorption/htf-anchor/child-execution/binance-futures/1h/15m/5m/3m/1m/repo/public-data/cost/risk
- 证据类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `vpvr_cvd_backtest_v2.py` + `vpvr_cvd_validation_suite.py` + `vpvr_cvd_trailing_test.py` + `vpvr_cvd_grid_search.csv` + `configs.json`）

- 主题类型：raw alpha
- 基础 alpha：**价格在 rolling volume-profile 的 POC 附近出现“价格路径与 CVD 方向相反”的 absorption 时，短期更容易向 POC / 局部公允区回摆**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但当前更像 **1H 母信号**，不宜把同一参数直接压缩到 `15m/5m`

## 1. 这次看了什么
这次看的是一个 2026-03-21 创建、今天还在更新的 GitHub repo：`breloom22/VPVR-CVD`。它表面上像一个“VPVR + CVD divergence”脚本，但真正值得 intake 的不是指标名，而是它把一条**可完整复现的单资产 raw alpha**写得很清楚：

1. 先用 rolling VPVR 找最近一段成交量重心 `POC`；
2. 再看最近若干 bar 里，**价格斜率**和 **CVD 斜率**是否明显反着走；
3. 只有在价格与 POC 的距离、蜡烛实体大小都过关时才允许入场；
4. 出场不用花哨 trailing，而是固定 TP/SL。

一句话先下判断：**base alpha 是清楚的，它不是 filter 冒充 alpha；但 repo 自己已经明确给出一个很重要的 transfer boundary——这条 edge 主要活在 crypto `1H`，直接压到 `15m/30m` 是会失效的。**

## 2. 为什么这轮值得看它
先回答一句：**这篇东西的 base alpha 是什么？**

> **POC 附近的 absorption mean reversion。**

也就是：

> **当价格还在“成交量公允区”一侧附近，但主动成交流（CVD）继续朝相反方向挤压，说明被动流动性在吸收，随后更容易出现回摆。**

这条线值得看，不是因为 `VPVR` 或 `CVD` 这两个词看起来高级，而是因为它补的是当前池子里相对少一点的一类 raw alpha：

- 不是 funding / basis / pairs；
- 不是单纯 RSI / MFI / breakout；
- 而是 **volume-profile 锚点 × signed-flow divergence** 的单资产 absorption 壳。

而且 repo 已经把：
- entry
- exit
- sizing
- fee
- TP/SL grid
- walk-forward
- timeframe transfer check

都写成了源码或验证脚本，不是只有一张收益截图。

## 3. 来源与材料
### 3.1 仓库信息
- Author / Repo：`breloom22/VPVR-CVD`
- Year：2026
- Repo title：`VPVR + CVD Divergence Strategy`
- GitHub URL：<https://github.com/breloom22/VPVR-CVD>
- Created at：`2026-03-21 04:11:27 UTC`
- Updated at：`2026-04-05 14:10:51 UTC`
- Repo description：`VPVR + CVD divergence strategy for Binance Futures — smart money absorption detection`

### 3.2 这份 repo 里最关键的文件
- `README.md`
- `vpvr_cvd_backtest_v2.py`
- `vpvr_cvd_validation_suite.py`
- `vpvr_cvd_trailing_test.py`
- `vpvr_cvd_grid_search.csv`
- `configs.json`

### 3.3 数据公开性
- 交易数据路径：Binance Futures 公共 K 线 + `data.binance.vision` 公共 aggTrades
- CVD 两种口径：
  - **real taker CVD**：按 `aggTrades.is_buyer_maker` 逐笔聚合
  - **CLV proxy CVD**：按 K 线 close location value 近似
- 可复现性：高；即使不跑原 repo，也能很快在 Binance 公共 `1h / 15m / 5m` 数据上重做

## 4. 这条 base alpha 到底是什么
### 4.1 源码里的信号定义
`vpvr_cvd_backtest_v2.py` 里，核心判定不是神秘黑盒，而是很朴素的四层条件：

#### A. 先算 rolling POC
- `vpvr_lookback = 50`
- `vpvr_num_bins = 50`
- 在最近 50 根 bar 的价格区间里分桶，找 volume 最大的桶作为 `POC`

#### B. 再算 divergence
源码 `detect_divergence()`：
- 取最近 `div_lookback` 根 bar
- 分别对 `price_window` 与 `cvd_window` 做线性回归斜率
- 再用各自窗口标准差标准化
- 阈值：`MIN_SLOPE = 0.1`

判定：
- `bullish_absorption`：`price_slope_norm > 0.1` 且 `cvd_slope_norm < -0.1`
- `bearish_absorption`：`price_slope_norm < -0.1` 且 `cvd_slope_norm > 0.1`

翻成人话：
- 价格往上，但 CVD 往下，说明**主动卖压还在打，价格却没被打下去**；
- 价格往下，但 CVD 往上，说明**主动买压还在追，价格却推不上去**。

这就是典型的 **absorption / adverse-selection** 读法。

#### C. 再加 POC 距离与实体过滤
主验证配置在 `vpvr_cvd_validation_suite.py` 里写成：
- `div_lookback = 7`
- `min_body_atr = 0.7`
- `poc_min_atr = 0.3`
- `poc_max_atr = 2.5`

也就是：
- 离 POC 太近不做；
- 离 POC 太远也不追；
- 蜡烛实体太小不做。

#### D. 最终方向条件
在 `run_backtest_fast()` 里：
- `cp < poc` 且 `bullish_absorption` → `long`
- `cp > poc` 且 `bearish_absorption` → `short`

注意这一步很关键：

它不是单纯做 divergence，也不是单纯做 POC fade，而是：

> **只有当价格站在 POC 某一侧，且同侧出现“流动性吸收”型 divergence 时，才赌向 POC / 公允区回归。**

### 4.2 用 desk 语言翻成人话
这条 alpha 的内核可以写成一句：

> **POC-proximal absorption fade**

比“CVD divergence”更准确，因为真正起约束作用的是三件事一起成立：
1. **有公允锚点**（POC）
2. **有方向错配**（price vs CVD）
3. **错配发生在可交易距离内**（0.3~2.5 ATR）

所以这不是泛泛的“订单流分歧”，而是一条更具体的单资产 raw alpha。

## 5. repo 真正证明了什么
### 5.1 README 给出的主配置结果
README 主配置写的是：
- 标的：`BTC + ETH + SOL`
- 样本：`365d`
- 周期：`1H`
- 杠杆：`10x`

主结果：
- Trades：`86`
- Win Rate：`47.7%`
- Profit Factor：`2.316`
- Return：`+144.8%`
- Sharpe：`3.55`
- Max Drawdown：`-9.9%`

如果只看 README，这已经足够把它归成：

> **可独立复现、可完整落地的 raw alpha 候选。**

### 5.2 但它最值钱的不是收益截图，而是 transfer boundary
README 还明确写了几条比“高收益”更有价值的结论：

- **CLV approximation is sufficient**：真实 aggTrades CVD 没有明显优于 OHLCV 的 CLV proxy
- **Crypto 1H is the only profitable timeframe**：`15m / 30m / 2h / 4h` 全部 `PF < 1.0`
- **Strategy does not transfer to stocks**：Nasdaq `1H` 多数也不行
- **Fixed TP/SL beats trailing stops**：ATR trailing 全部跑输固定止盈止损
- **3-fold walk-forward**：所有 OOS fold 的 PF 都大于 1

这几句的价值很高，因为它们等于帮我们省掉了一堆无效内循环：

- 不要先默认“更高频一定更强”；
- 不要默认“真实逐笔 CVD 一定碾压 K 线 proxy”；
- 不要默认“trailing stop 一定更聪明”。

### 5.3 grid search 也透露出一个实盘信号
`vpvr_cvd_grid_search.csv` 里，PF 最高的极端参数组虽然能到 `2.37`，但只有 `7` 笔交易；
而 repo 最后落到主配置附近的更稳组合，是：
- `div_lb = 7`
- `body_atr = 0.7`
- `poc_min = 0.3`
- `poc_max = 2.5`

这说明作者自己也意识到：

> **真正可用的不是“最尖的 in-sample 顶格 PF”，而是 trade count、稳定性和 OOS 生存线。**

这点和当前 desk 的学习主线是对齐的。

## 6. 对当前 short-cycle desk 的真正启发
### 6.1 不要把它硬抄成 15m standalone
repo 自己已经给答案了：

> **这条壳在 1H 活，在 15m/30m 不活。**

所以如果这轮把主题写成“15m 直接照抄 VPVR+CVD 就能跑”，那是误读。

更合理的 short-cycle 读法是：

> **把 1H absorption 当母信号，把 15m 当子执行层。**

也就是说，对我们现在的 `1m / 3m / 5m / 15m`，它的第一落点不是“缩频”，而是：
- `1H` 负责判 state
- `15m` 负责更好 entry / timeout / risk

### 6.2 哪 3 个组件最值得拆出来
#### A. `distance_to_POC`
当前价格距 `1H rolling POC` 多远：
- 过近：没 edge
- 过远：可能已经成趋势，不该硬 fade

#### B. `price_vs_CVD slope disagreement`
这个 repo 最值钱的不是“CVD 数值”，而是：

> **价格路径与成交流路径是否背离。**

这可以服务：
- 单资产回摆
- maker adverse-selection veto
- breakout exhaustion 否决

#### C. `body / ATR impulse filter`
源码要求 `min_body_atr = 0.7`，说明作者并不想抓“慢慢磨”的背离，而是想抓：

> **已经有足够实体推进、但推进里出现 absorption 的 bar。**

这很适合拿去服务现有 fast fade / mean-reversion 壳。

## 7. 这轮最重要的判断：它为什么仍值得进研究池
如果只看“能不能直接做 15m standalone”，这条线不是当前最优先。

但如果问：**它为什么比继续补一个普通 breakout / pairs 题更值得看？**

我的答案是：

1. **它补的是目前池子里相对少见的 alpha 形态：** volume-profile 锚点 × absorption；
2. **它不是纯概念，已经是完整策略壳：** entry / exit / TP/SL / fee / validation 都在源码里；
3. **它自带强 transfer-boundary 信息：** 明确告诉你“不要机械缩频”；
4. **即便 standalone 只活在 1H，它仍能服务 `15m` 子执行与 shared gate。**

所以这轮我会把它归成：

- **一级：raw alpha 候选**
- **二级：HTF parent signal for short-cycle execution**

而不是简单降级成“一个 filter”。

## 8. 下一步怎么测
### 8.1 最小实验 1：先做 `1H parent -> 15m child`
不要直接把 repo 参数压到 `15m`；先做：

**Parent（1H）：**
- 50-bar rolling POC
- `div_lb = 7`
- `body_atr >= 0.7`
- `0.3 <= dist_to_POC / ATR <= 2.5`
- bullish / bearish absorption state

**Child（15m）：**
- 只在新 `1H` state 触发后的前 `4` 根 `15m` 内允许进场
- 进场方式对比：
  1. next-open
  2. first pullback toward 15m VWAP
  3. first failed extension + close back inside micro range
- time stop：`4~8` 根 `15m`
- 成本：`2 / 4 / 6 bps` round-trip

先回答一个简单问题：

> **同样的 1H state，用更聪明的 15m 进场，能不能把 repo 的 1H edge 带进 short-cycle？**

### 8.2 最小实验 2：测它能不能当 shared gate
拿现有两类壳先叠：

1. **5m downward impulse fade**
   - 只在 `1H bullish_absorption & price < POC` 时开多
2. **maker / passive liquidity shell**
   - 遇到 `price-vs-CVD disagreement` 时，降低顺势追价，优先 maker

要测的不是方向胜率，而是：
- fail rate 是否下降
- adverse-selection 是否下降
- 持仓时间是否缩短

### 8.3 最小实验 3：CLV proxy 是否真的够用
repo 一个很实用的 claim 是：

> **real aggTrades CVD 没有明显优于 CLV proxy。**

这对 desk 很重要，因为如果 CLV 足够，`15m / 5m` 最小实验就不必先背逐笔数据负担。

建议直接并排：
- `CLV CVD`
- `signed aggTrades delta`
- `signed trade-count imbalance`

如果三者在 `1H parent -> 15m child` 里差别不大，优先保留最便宜口径。

### 8.4 最小实验 4：不要忘记负迁移验证
既然 repo 已明确说 `15m / 30m / 2h / 4h` 都不行，desk 下一步不能只找“能赢”的改法，也要保留：
- direct `15m clone`
- direct `5m clone`

作为负对照。

如果 direct clone 继续死，而 `1H parent -> 15m child` 能活，这本身就是研究结论。

## 9. 这篇东西最后怎么归档
### 9.1 主题归类
- 主题类型：`raw alpha`
- 更细归类：`single-asset absorption / volume-anchor mean reversion`

### 9.2 与当前短周期（1m/3m/5m/15m）的关系
- **不是**：`15m` 直接照抄的现成成品
- **更像**：`1H` 母信号 + `15m` 子执行
- `5m / 3m / 1m` 当前不建议直接压缩；先当 execution refinement，不当 primary signal

### 9.3 是否进入当前优先复现队列
我的建议：
- **进入 raw alpha 素材池**
- **进入 HTF-parent / LTF-child 实验优先队列**
- **不进入 15m direct-clone 高优先实盘队列**

## 10. 来源链接
1. **breloom22 (2026). _VPVR + CVD Divergence Strategy_. GitHub Repository.**
   - Author: breloom22
   - Year: 2026
   - Title: VPVR + CVD Divergence Strategy
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/breloom22/VPVR-CVD>
   - Repo URL: <https://github.com/breloom22/VPVR-CVD>

2. **Source file: `vpvr_cvd_backtest_v2.py`**
   - Title: VPVR + CVD Divergence Backtest v2
   - Readable URL: <https://github.com/breloom22/VPVR-CVD/blob/main/vpvr_cvd_backtest_v2.py>
   - Raw URL: <https://raw.githubusercontent.com/breloom22/VPVR-CVD/main/vpvr_cvd_backtest_v2.py>

3. **Source file: `vpvr_cvd_validation_suite.py`**
   - Title: VPVR + CVD Validation Suite
   - Readable URL: <https://github.com/breloom22/VPVR-CVD/blob/main/vpvr_cvd_validation_suite.py>
   - Raw URL: <https://raw.githubusercontent.com/breloom22/VPVR-CVD/main/vpvr_cvd_validation_suite.py>

4. **Source file: `vpvr_cvd_trailing_test.py`**
   - Title: VPVR + CVD Strategy -- Trailing Stop Comparison Test
   - Readable URL: <https://github.com/breloom22/VPVR-CVD/blob/main/vpvr_cvd_trailing_test.py>
   - Raw URL: <https://raw.githubusercontent.com/breloom22/VPVR-CVD/main/vpvr_cvd_trailing_test.py>

5. **Validation artifact: `vpvr_cvd_grid_search.csv`**
   - Readable URL: <https://github.com/breloom22/VPVR-CVD/blob/main/vpvr_cvd_grid_search.csv>
   - Raw URL: <https://raw.githubusercontent.com/breloom22/VPVR-CVD/main/vpvr_cvd_grid_search.csv>

## 11. 最短版结论
这份 2026 repo 的 **base alpha 是清楚的**：`POC-proximal price/CVD absorption fade`。它不是一个 filter 冒充 alpha，而是一条能被完整复现的单资产 raw alpha 壳。

但 repo 真正最值钱的结论不是“收益很好”，而是：

- `1H` 能活；
- `15m / 30m / 2h / 4h` 直接压缩会死；
- `CLV proxy` 大概率就够；
- 固定 `TP/SL` 比 trailing 更稳。

所以这轮对 desk 最值得做的，不是照抄 `15m VPVR+CVD`，而是立刻去测：

> **`1H absorption parent signal × 15m child execution`**

如果这条桥接能活，它就不是普通的 1H 策略，而是能进入当前 short-cycle 组件库的一条新母信号。