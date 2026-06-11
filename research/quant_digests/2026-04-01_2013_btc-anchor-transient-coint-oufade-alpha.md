# 别把这份 2026 BTC-anchor notebook 只读成普通 pairs 作业：对 short-cycle desk，更该先测的是「BTC anchor × transient cointegration shortlist × walk-forward OU fade」这条完整 raw alpha

- 时间：2026-04-01 20:13 UTC
- 类型：2026 GitHub notebook source audit（`NUSiQF Project (Crypto).ipynb` + GitHub rendered output + GitHub API metadata）
- 主题类型：raw alpha
- 基础 alpha：**BTC 锚定的相对价值均值回复**；先在大市值币里用 rolling Engle–Granger / half-life 做 `BTC-其他币` 的 transient cointegration shortlist，再对 Kalman hedge ratio 残差做 OU `z-score fade`。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/btc-anchor/transient-cointegration/kalman/ou/walk-forward/train-positive-sharpe/regime-gate/binance-spot/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：GitHub notebook 源码 + rendered output + GitHub API metadata（repo-based）

## 1. 这次看了什么
这轮看的不是论文，而是一份 **2026-01 创建、2026-04-01 还在更新** 的单 notebook 仓库：`weisiang1218/nusiqf-crypto`。它把一条完整的短周期 crypto pairs 骨架明着写出来了：

1. 先从 **CoinGecko 大市值名单 + Binance USDT 上市对** 构一个 exploratory universe；
2. 下载 **Binance 15m spot close**；
3. 只做 **BTC 对其他大币** 的 anchor pairs；
4. formation 窗口里先做 **rolling Engle–Granger cointegration screen**；
5. 再做 **Kalman hedge ratio + OU fit**；
6. 只保留 **训练窗 Sharpe > 0 且训练 PnL > 0** 的参数；
7. 下一段 test 窗才允许交易，而且回测里明确用了 **one-bar execution lag**。

一句话说，它不是“泛 pairs 教学笔记”，而是一个已经带上 **entry / exit / sizing / cost / walk-forward** 的完整 raw alpha blueprint。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这轮的 **base alpha 很清楚**：

- 不是 regime filter 本身；
- 不是 Kalman 本身；
- 不是 cointegration screen 本身；
- 而是 **BTC-anchored spread mean reversion**。

翻成人话：
**把 BTC 当公共锚，去找那些和 BTC 在最近一段时间里暂时仍有协整/回复结构的大币；一旦相对价差偏离 OU 均值太多，就做 long cheap / short rich，赌 spread 回来。**

所以这轮应被定性为：
- `raw alpha`
- `pairs / stat-arb / relative value / mean reversion`

而 rolling cointegration shortlist、half-life gate、train-positive acceptance，更像这条 raw alpha 的 **research gate + trade admission shell**。

## 3. 为什么这轮值得 intake，而不是继续把 pairs 写成同一张卡
最近 desk 已经 intake 过不少 pairs / stat-arb 主题；这轮还值得写，是因为它补的不是“又一个固定 pair z-score”，而是三个更 desk-like 的组件：

1. **BTC anchor 读法。** 不是全市场 pair 两两暴力扫描，而是先把 BTC 当公共风险锚，再看 alt 相对 BTC 的可交易偏离。
2. **transient selection。** 不是要求 pair 永久稳定，而是承认 crypto 里很多关系只是阶段性存在，所以先做 rolling shortlist，再做下一段 test。
3. **只交易训练窗里活过的参数。** notebook 明写：只有当训练窗 `Sharpe > 0`、`PnL > 0`、`min_train_trades >= 2` 时，下一段窗口才给交易资格。

这对当前 bot7 的优先级是加分项：
- base alpha 清楚；
- 可独立复现；
- 直接是完整策略，不只是一个 filter；
- 并且很适合快速做 `15m signal / 5m execution refinement` 的最小实验。

## 4. 最值得记住的硬数据
### 4.1 notebook 的总组合结果
rendered output 里给出一张最关键的 summary table：

- **Transient Coint + Regime Filter**：`Final Equity = 10466.66`，`Sharpe = 2.090`，`Max Drawdown = -0.062`
- **Transient Coint w/o Regime Filter**：`Final Equity = 4304.87`，`Sharpe = -18.467`，`Max Drawdown = -0.634`
- **Buy & Hold BTC**：`Final Equity = 7765.81`，`Sharpe = -1.594`，`Max Drawdown = -0.383`

也就是说，至少在这份 notebook 的演示里：
**同样是 BTC-anchor pairs，本体能不能活，很大程度取决于“只在 spread 还像可回复过程时才允许开仓”这层 gate。**

### 4.2 最好的两个 anchor pair
pair-level table 里最亮眼的是：

- **BTC-AVAX**：`Final Equity = 11977.89`，`Total PnL = 1977.89`，`Sharpe = 9.40`，`MaxDD = -1.36%`，`1` 笔 trade，`4` 个 traded windows
- **BTC-LINK**：`Final Equity = 11577.94`，`Total PnL = 1577.94`，`Sharpe = 5.66`，`MaxDD = -2.68%`，`3` 笔 trades，`9` 个 traded windows
- **BTC-ZEC** 也还活着：`Final Equity = 10078.71`，但 edge 已明显薄很多

这很像一种 desk 可接受的现实：
**不是每个 BTC-anchor pair 都能交易，真正有价值的是“动态 shortlist + 少数好 pair + 低频但干净的交易窗口”。**

### 4.3 交易壳子已经写得很完整
notebook 默认参数里，最值得 desk 直接偷走的是：

- **bar frequency：** `15m`
- **train / test：** `25d train`（`24*4*25 = 2400` bars）+ `1d test`（`96` bars）
- **entry / exit 网格：** `entry_z = 1.5 / 2.0 / 2.5`，`exit_z = 0 / 0.5 / 1.0`
- **min hold：** `8 / 16` bars
- **stop：** `stop_z = 4.0`
- **half-life 上限：** `max_halflife = 24*4*2`（约 `2` 天）
- **cost：** `fee_rate = 0.0004` + `slippage_bps = 1.0`
- **execution：** `one-bar lag`
- **sizing：** `initial_capital = 10,000`，`leverage = 3.0`，`alloc = 1.0`

这说明它不是只停在“pair 相关性好像不错”的研究笔记，而是已经长成了一个能直接翻译成策略卡的原型。

## 5. 为什么和当前 `momentum` 项目有关
当前 desk 最近 intake 里，虽然已经积累了不少 raw alpha，但很多是：
- 单币 directional；
- funding / basis / carry；
- microstructure directional；
- 或者更传统的 cross-sectional relative strength。

这份材料的价值在于：
**它补的是“BTC 作为公共锚的相对价值 sleeve”，而不是再加一条单币方向腿。**

对 `momentum` 当前主线的直接意义有三层：

1. **raw alpha 素材池扩张**：这是一条能独立成卡的 pairs raw alpha；
2. **共享研究方法可复用**：walk-forward、train-positive acceptance、one-bar lag、cost-first，这些壳子可直接迁移到其他 alpha；
3. **与当前 desk 的 15m/5m 节奏匹配**：pair selection 可以慢一点，execution 可以快一点。

如果要一句话概括：
**这份 notebook 最值钱的，不是“BTC-AVAX 表现最好”，而是它把 crypto pairs 从固定 pair 研究，推进成“rolling shortlist → freeze params → next-window trade”的 desk 版工作流。**

## 3.5 策略拆解（必填）
- **方向属性：** 相对价值 / pairs / stat-arb / 均值回复
- **基础 alpha：** BTC-anchor spread 的 OU `z-score fade`
- **regime：** spread 在最近 rolling window 内仍满足 stationarity + half-life 可交易
- **filter / veto：** transient cointegration shortlist、`train_sharpe > 0`、`train_total_pnl > 0`、`min_train_trades >= 2`、`max_halflife` 约束
- **risk / sizing / execution overlay：** Kalman beta、`stop_z = 4.0`、`min_hold`、one-bar lag、`4 bps fee + 1 bp slippage`、组合层等权汇总

## 6. 和当前 `1m / 3m / 5m / 15m` 的关系
### 6.1 这条线更像“15m 做主信号，5m/3m 做执行”，不是 1m 主 alpha
来源本身用的是 **15m spot close**，不是 tick，不是 L2，也不是 funding clock 套利。
所以最合理的迁移是：

- **15m**：pair discovery refresh + signal bar
- **5m / 3m**：入场排程、双腿执行、maker/taker fallback
- **1m**：只做 child-order / legging 监控，不先拿来做 pair selection

如果第一刀就把它压成 `1m` 高频 pairs，大概率是在主动把 noise 和 fee 放大。

### 6.2 这条 alpha 适合先从 perp proxy 做，不要直接照搬 source 的 spot 壳
source 用的是 Binance spot close，而且 notebook 也明确承认：
- funding 没建模；
- liquidation / richer execution frictions 没建模；
- universe construction 可能有 survivorship / availability bias。

所以 desk 的正确读法不是“直接信 notebook 收益”，而是：
**把它当 high-signal repo blueprint，然后用 liquid perp proxy 重做 first verdict。**

## 7. 可复刻的最小实验
### 7.1 研究假设
**H1：** 在 liquid perp universe 里，`BTC-anchor transient pairs` 在 `15m` 上仍能形成 after-cost 的 spread MR。  
**H2：** 真正决定这条线能否活下来的，不是 entry_z 精调，而是 `shortlist gate + train-positive acceptance + cost shell`。  
**H3：** `5m/3m` 的价值主要在 execution refinement，而不是替代 `15m` 主筛选。  

### 7.2 最小回测切口
- **资产：** BTC 对 `15~20` 个 liquid majors / upper-mid（ETH / SOL / XRP / LINK / AVAX / LTC / ADA / DOGE / BNB ...）
- **周期：** 先 `15m`；若存活，再下钻 `5m`
- **样本：** 最近 `180 ~ 365` 天
- **数据：** Binance / Bybit / OKX 永续 close；第一版可只用 close，不急着上盘口
- **formation / test：** 先直接照 source：`25d train + 1d test`

### 7.3 一个可计算定义
1. 先对 `BTC-coin` 做 rolling Engle–Granger；
2. 只保留 `p < 0.10` 且 `half-life < 2 days` 的 pairs；
3. 对 surviving pairs 估 Kalman beta；
4. 对 spread fit OU，算 `z-score`；
5. `|z| >= 2.0` 入场，`|z| <= 0.5` 出场，`|z| >= 4.0` 止损；
6. 必须 `one-bar lag` 执行；
7. 成本先跑 source 基线，再跑一组更现实的 fee ladder。

### 7.4 第一轮最该先看的 2 个指标
- **成本后收益 / 成本后 Sharpe 是否仍为正**
- **positive-window ratio**（不是只看一两个好 pair）

第二层再补：
- max drawdown
- trade count
- 组合层相关性拥挤度
- gate on/off 的 ablation

### 7.5 下一步怎么测
1. **先复刻 source 壳，不要先发明新 pair discovery。** 先用 `BTC anchor + 25d/1d + z-score fade` 做第一版。
2. **把 regime gate 单独 ablation。** 这份 notebook 最有研究价值的地方，就是 gate on/off 差异极大；先验证这件事是不是可转移。
3. **把 spot → perp 的迁移风险单独测。** 尤其要补 funding、双腿 fee 和 legging risk。
4. **先看 15m after-cost 是否活。** 如果 15m 不活，就别幻想 1m/3m 会更容易救活。
5. **先做 BTC-anchor，再决定要不要扩到 cluster-anchor。** 第一刀别把问题复杂化。

## 8. 风险与保留意见
1. **这只是单 notebook 仓库，不是论文，也不是成熟生产框架。**
2. **来源用的是 spot 数据。** 真正搬到 perp 时，funding 和 execution friction 可能会显著改写结果。
3. **notebook 的 summary table 有可疑点。** 例如总组合表里 `Total PnL` / `Number of Trades` / `Win Rate` 是 `NaN`，而 pair-level 细表又有这些数字；说明 reporting layer 可能有 bug。
4. **部分 screening 统计也显得不太一致。** 某些 pair 的 `screen_selected_green_frac_mean = 0.0`、`last_p_value_mean = 1.0`，但又显示多次被 transient coint 选中，这需要复核 notebook 计算逻辑。
5. **BTC anchor 可能把市场 beta 暗中带进来。** 如果 BTC 自身 regime 大幅切换，pair spread 不一定还是纯 relative-value。

所以最合理的定位是：
**高信号 repo blueprint，不是已闭环验证。**

## 9. 来源
- **Author / Maintainer：** `weisiang1218`
- **Year：** 2026
- **Title：** *BTC-Anchored Crypto Pairs Trading*（notebook title）
- **Venue：** GitHub repository notebook
- **DOI：** N/A
- **Readable URL：** <https://github.com/weisiang1218/nusiqf-crypto>
- **Repo API metadata：** <https://api.github.com/repos/weisiang1218/nusiqf-crypto>
- **Notebook（raw）：** <https://raw.githubusercontent.com/weisiang1218/nusiqf-crypto/main/NUSiQF%20Project%20(Crypto).ipynb>

### notebook 内部明确写到的数据源 / 方法线索
- **Universe source：** CoinGecko market-cap list + Binance USDT listings
- **Price source：** Binance `15m` spot close prices
- **Core methods：** rolling Engle–Granger screening、Kalman hedge ratio、OU fit、walk-forward train/test、one-bar lag、fee + slippage shell

## 10. 一句话结论
**如果这轮只记一件事，不要记“BTC-AVAX 很强”；要记的是：这份 2026 notebook 把 pairs raw alpha 从固定 pair 静态回归，推进成了“BTC anchor shortlist → train-positive freeze → next-window OU fade”的完整工作流，这比再多一个泛 pairs 结论更值得 desk 立刻复现。**
