# 别把这个 2026 新仓里的 `mean_reversion_crypto.py` 只读成“又一个布林带指标”：对 short-cycle crypto desk，更该先拆的是「Bollinger band 极端偏离 × RSI 同向确认 × realized-vol 缩放」这条完整 raw alpha 壳
- 时间：2026-04-24 20:15 UTC
- 类型：GitHub Repo
- 主题类型：raw alpha
- 基础 alpha：单资产短周期均值回归。价格触及 Bollinger 上下轨后，不是立刻机械反手，而是要求 RSI 同步进入超买/超卖区，再按偏离中轨的幅度决定信号强弱，并用 realized vol 做仓位缩放。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / single-asset / mean-reversion / bollinger-band / rsi / realized-vol / vol-target / btc / eth / sol / 5m / 15m / repo / cost / risk
- 证据类型：GitHub repo README + strategy source code

## 1. 这次看了什么
这次看的是 **zwmjj (2026), `kuant-strategies`** 这个新 repo 里的 `strategies/mean_reversion_crypto.py`。

虽然仓库本身是个“25+ 策略大礼包”，但这轮真正值得单独拆出来的，不是整个框架，而是其中这条非常明确的 crypto mean-reversion 壳：

- `20` 窗口 Bollinger band
- `14` 周期 RSI
- 价格触及上/下轨才触发候选信号
- RSI 必须同步进入超买/超卖区才放行
- 信号强度按“离中轨有多远”来缩放
- 最终仓位再乘上 `target_vol / realized_vol` 的波动率缩放

对当前 desk 来说，这比继续写一篇“泛 pairs 教程”更值得：它是 **可独立复现、可直接压到 `5m/15m`、而且 entry/exit/sizing 都写得很白** 的 raw alpha 壳。

## 2. base alpha 先说清楚
这篇东西的 **base alpha 很清楚**：

**短周期价格过度偏离后的均值回归。**

不是 overlay，不是纯 risk module，也不是“用 RSI 做解释”。
真正的 alpha 本体是：
1. 价格偏离滚动均值太远；
2. 偏离已经大到触碰 Bollinger 外轨；
3. RSI 也同步进入极端区；
4. 于是押注下一段回到中轨附近，而不是继续追单边扩张。

所以这条线属于很标准的：
**single-asset / mean-reversion / oscillator-confirmed fade**。

## 3. 上游代码到底写了什么
源码里的关键信号定义非常直白：

### 3.1 入场条件
- **做多**：`close <= lower_band` 且 `RSI < 30`
- **做空**：`close >= upper_band` 且 `RSI > 70`

也就是说，作者没有把“碰下轨就多、碰上轨就空”写成裸信号，而是多加了一层 RSI 共振确认，尽量过滤掉“刚开始趋势扩张”的假反转。

### 3.2 信号强度
源码不是只输出 `+1 / -1`，而是先算：

`abs(close - mid) / (upper - lower)`

也就是：**离中轨越远，信号越强**。然后把强度截断在 `[0, 1]`，避免极端值把仓位炸穿。

### 3.3 仓位缩放
接着它又算一层 realized vol：

`vol_scale = target_vol / realized_vol`

默认：
- `vol_window = 20`
- `target_vol = 0.50`
- `max_vol_scale = 2.0`

于是最终信号是：

`final_signal = raw_signal * vol_scale`

翻成人话就是：
- 市场越炸，自动缩仓
- 市场越平，允许把仓位稍微放大
- 但最多只放到 `2x`

### 3.4 默认标的
默认是三大高流动性币：
- `BTC/USD`
- `ETH/USD`
- `SOL/USD`

这点很重要：它不是拿一堆 illiquid 小币硬凑回测，而是从最容易落地的 liquid majors 起步。

## 4. 为什么这条线对当前 desk 有意义
最近几篇 digest 已经连续覆盖了：
- pairs / stat-arb
- funding / carry
- EMA 趋势跟随

所以这轮更需要补的是：**一个和这些主线互补、但仍然是 raw alpha 的单资产 mean reversion 壳。**

这条 repo 线的价值主要在 4 点：

### 4.1 它不是“只有信号，没有策略壳”
这里已经明确写了：
- 入场：上下轨 + RSI 极值
- 强度：按偏离中轨的距离定大小
- sizing：按 realized vol 缩放
- universe：BTC/ETH/SOL
- backtest entrypoint：`backtest_mean_reversion(data_dict, **kwargs)`

所以这不是一段只能拿来做灵感摘录的伪代码，而是可以直接映射到 desk pipeline 的完整策略骨架。

### 4.2 它天然适合做 `15m` 主信号
Bollinger + RSI 这类信号，最怕被噪声淹没；但放在 `15m` 做主信号，再让 `5m` 做 child execution，通常比直接在 `1m` 裸跑更接近可交易形态。

### 4.3 它刚好能和现有 trend / carry / pairs 形成互补
- 当 trend 壳赚钱时，这条 fade 壳常常会吃亏；
- 但当市场进入震荡、回归、局部 overshoot 状态时，反而是这类信号更容易留下 edge。

也就是说，它很适合做成 **和趋势 sleeve 互补的短周期 mean-reversion sleeve**。

### 4.4 它比“只做 RSI 极值”更像可交易版本
单看 RSI 极值，很容易在强趋势里连着抄底抄到手断；
而这里至少加了两层约束：
- 必须已经偏离到 Bollinger 外轨
- 高波动时自动缩仓

这至少让它从“教科书指标信号”更接近“可跑的策略壳”。

## 5. 策略拆解（必填）
- 方向属性：single-asset / mean-reversion
- 基础 alpha：Bollinger band 外轨极端偏离后的回归
- confirmation：RSI 同步进入超买/超卖区
- sizing：偏离中轨越远，名义信号越强；realized vol 越高，仓位越小
- risk / execution：上游源码里已有 vol targeting，但 fee/slippage 没在这个文件里显式展开；desk 落地时需要接入统一 friction ladder 与 time-stop
- 推荐 desk 映射：`15m` 生成信号，`5m` 执行进出与滑点控制

## 6. 对 short-cycle crypto 的 desk 读法
这条线最值得抄的，不是“布林带 + RSI”这四个字，而是它的 **三段式结构**：

1. **先定义极端偏离**：不是随便跌了就买，而是得先到 band 外侧；
2. **再做方向确认**：RSI 也要同步极端；
3. **最后做风险归一化**：高波动环境自动缩仓。

这三步合起来，其实就是一个很适合短周期 crypto 的思路：

**先找 overshoot，再确认不是普通噪声，最后避免在最危险的时候下最大仓。**

这比很多“只要碰 band 就反手”的老派写法成熟得多。

## 7. 可复刻的最小实验
### 最小研究假设
**在 Binance/Bybit 等 liquid perp 上，`15m` 级别的 Bollinger 极端偏离，如果再叠加 RSI 共振与 realized-vol 缩仓，是否能形成 fee 后仍存活的单资产 mean-reversion 壳。**

### 最小实验口径
1. 标的：先跑 `BTCUSDT / ETHUSDT / SOLUSDT perp`
2. 主频：`15m`
3. 子执行：`5m`
4. 参数起点：
   - `bb_window = 20`
   - `bb_std = 2.0`
   - `rsi_period = 14`
   - `rsi_oversold = 30`
   - `rsi_overbought = 70`
   - `vol_window = 20`
   - `target_vol = 0.50`
   - `max_vol_scale = 2.0`
5. 入场：
   - `close <= lower` 且 `RSI < 30` → 下一根开多
   - `close >= upper` 且 `RSI > 70` → 下一根开空
6. 出场先用最朴素版本：
   - 价格回到中轨附近就平
   - 或 RSI 回到中性区间（如 `45~55`）就平
   - 或固定 `N` 根 time-stop 平仓
7. 成本：先跑单边 `2 / 4 / 6 / 10 bps` friction ladder

### 第一轮先看什么
- fee 后 Sharpe
- hit rate 与 payoff ratio
- 平均持仓 bars
- 单币 vs 多币合并后的稳定性
- 强趋势日 / 横盘日的收益分布

## 8. 下一步怎么测
1. **先做最朴素的中轨回归版本**：
   - band 外轨触发
   - RSI 共振确认
   - 到中轨平仓
   不要一上来加太多 regime 条件。

2. **做三个关键对照**：
   - A：只用 Bollinger，不加 RSI
   - B：Bollinger + RSI
   - C：Bollinger + RSI + vol scaling
   这样才能看出 edge 到底来自哪一层，不会把全部功劳都算到一个大杂烩上。

3. **测趋势环境里的伤害有多大**：
   这类策略最大的敌人不是普通噪声，而是单边趋势扩张。要单独切分：
   - ADX 高 vs 低
   - 过去 `N` 根单边净涨跌绝对值高 vs 低
   看它是不是只在 range regime 里活。

4. **把单资产版和组合版分开看**：
   BTC/ETH/SOL 各自可能风格很不一样。先看单币是否存活，再决定要不要合成 equal-weight 或 inverse-vol basket。

5. **如果 `15m` 可活，再往 `5m` 压缩；如果 `5m` turnover 爆炸，就停在 `15m signal + 5m execution`。**

## 9. 风险与保留意见
- 这条线本质上仍然是经典均值回归；新意主要在“RSI 共振 + vol 缩仓”的组合，而不是理论突破。
- 源码文件里没有把 fee/slippage 细节完全展开，所以落地时不能偷懒，必须补 desk 自己的 friction 假设。
- 在真正强趋势行情里，这类策略很容易连续逆势接刀；因此是否加入 trend veto，会是第二轮实验的重点，但那应该被定位成 **filter**，不是 alpha 本体。
- repo 里展示的是日级/通用框架写法，移植到 `5m/15m` 时，持仓时长、触发频率和手续费压力都要重新核对，不能直接照搬结果口径。

## 10. 一句话总结
**这份 2026 repo 最值得 desk 吸收的，不是“布林带和 RSI 又双叒叕能交易”，而是把“极端偏离后的回归”写成了一个 entry/confirmation/sizing 都很完整、且能直接压到 `15m/5m` 做最小实验的 mean-reversion raw alpha 壳。**

## 11. 来源
- Author / Year / Title / Venue
  - zwmjj. (2026). *kuant-strategies*. GitHub Repository.
  - Title: `mean_reversion_crypto.py` inside `kuant-strategies`
  - Venue: GitHub
  - DOI：无
  - Readable URL：https://github.com/zwmjj/kuant-strategies
  - Repo URL：https://github.com/zwmjj/kuant-strategies
- Raw source used
  - README：https://raw.githubusercontent.com/zwmjj/kuant-strategies/main/README.md
  - Strategy source：https://raw.githubusercontent.com/zwmjj/kuant-strategies/main/strategies/mean_reversion_crypto.py
