# 别把这份 2024 carry/momo/breakout repo 只读成“因子拼盘练习”：对 short-cycle desk，更该先测的是「24h funding-decile × breakout tilt × trade-buffer basket」这条完整 raw alpha

- 时间：2026-04-01 19:40 UTC
- 类型：2024 GitHub repo + notebook rendered output + blog audit（`README.md` + `stat-arb-backtest.ipynb` + Analytic Musings Part I）
- 主题标签：raw-alpha/cross-sectional/relative-value/carry/funding-predictor/breakout-tilt/trade-buffer/market-neutral/binance/perpetual/top30-liquid/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：2024 GitHub repo source audit + notebook 回测输出 + blog 研究笔记（工程证据为主）

- 主题类型：raw alpha
- 基础 alpha：**在 Binance 液态 perp 截面里，`过去 24h funding` 不是只用来“收租”，它本身就能当作下一期相对收益预测器；更具体地说，是做 `high-funding winners vs low-funding laggards` 的 market-neutral 截面书，`20d breakout` 只负责给组合加时间序列 tilt，`10d momo` 只是弱辅助。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
### 一句话核心结论
**这轮最该 intake 的，不是 repo 表面的“carry + momentum + breakout 三因子混搭”，而是里面最清楚的一条 raw alpha：`24h funding decile` 对 liquid perp 的下一期横截面相对收益有持续预测力，而 `breakout tilt + trade buffer + fee shell` 已经把它落成了完整可交易骨架。**

### 一句话它是怎么证明的
- **研究侧**：作者先在 `2019–2024`、约 `260` 个 Binance perp 里，滚动选出 top `30` 流动性 universe，比较 decile return、IC 和 decay，结果是 **carry/funding 的 IC 最强且最 sticky**，breakout 次之，momentum 最弱。
- **工程侧**：repo 的 notebook 直接把这条线写成含 funding accrual、交易费用和 no-trade buffer 的回测；渲染输出显示 `2020-03-12` 到 `2024-02-12` 的组合在 `15bps` 交易成本和 `5%` trade buffer 下，仍有 **`179.0%` 累计收益、`19.8%` 年化、`Sharpe 1.00`、`MaxDD -27.2%`**。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这次 **base alpha 很清楚，而且是 raw alpha**，不是 filter 假装成 alpha。

核心不是经典的 spot-perp cash-and-carry，也不是“看到 funding 正就去收租”。

这里真正可拆出来的 alpha 是：
1. **把最近 `24h funding` 当作 perp 横截面强弱信号**；
2. 在 liquid universe 里，**高 funding 的 perp 往往对应更强的后续相对收益**；
3. 用 long-short market-neutral 方式交易这个相对强弱，而不是赌大盘方向；
4. 再让 `20d breakout` 给组合一个可解释的时间序列 tilt，帮助组合在明显单边期别过于逆势中性。

所以它更准确的归类是：
- `raw alpha`
- 更细一点是：`cross-sectional / relative-value / carry-as-predictor`

这里的 breakout 重要，但**不是 alpha 本体**；它更像 `ts overlay / tilt`。`10d momo` 则更像弱辅助特征。

## 3. 为什么这轮值得写，而不是继续堆一个泛 carry 摘要
这轮值得写，原因恰好在于它补的是**一条和最近 desk intake 的“收租式 carry”不同的 raw alpha**：

1. **它不是纯 funding harvest，而是 funding 作为预测器。**
   最近 desk 已经积累了不少 `funding / basis` 线索，但很多偏向“谁付钱、谁收钱”的 carry shell；这份 repo 值得补，因为它把 funding 当成**横截面 alpha 信号**，而不是只当 coupon。
2. **它和当前学习主线形成互补。**
   现在项目文档里，Jerry 的显式学习主线仍偏 `trend / breakout / ATR / volume confirmation`；这份材料刚好补一条**正交的 raw alpha**，但又保留 breakout 这个熟悉组件，衔接成本低。
3. **它已经自带完整策略骨架。**
   不是只有 feature plot；它把 `universe / signal / weighting / buffer / fee / funding accrual / turnover` 都写进了 notebook，能直接变成复现实验。
4. **它很适合 desk 化 transfer。**
   论文式结果常常停在日频 decile；这份 repo 已经证明：即便原始研究是 daily rebalance，真正落地时也可以诚实拆成 `15m 信号刷新 / 5m 执行 / 1m~3m 排程`。

## 4. 这次看了什么来源
### 4.1 主工程来源
- **Author / Repo owner**：Ryan Chew
- **Year**：2024
- **Title / Repo**：*Crypto-Stat-Arb*
- **Repo URL**：<https://github.com/ryanczm/Crypto-Stat-Arb>
- **Readable URL**：<https://github.com/ryanczm/Crypto-Stat-Arb>
- **关键文件**：
  - `README.md`
  - `stat-arb-backtest.ipynb`

### 4.2 配套研究说明
- **Author**：Ryan Chew
- **Year**：2024
- **Title**：*Crypto Stat Arb: Quantifying & Combining Alphas*
- **Venue**：Analytic Musings（blog research note）
- **DOI**：N/A
- **Readable URL**：<https://analytic-musings.com/2024/03/10/crypto-stat-arb-I/>

### 4.3 证据边界说明
- README、blog 和 notebook 是可直接阅读的；
- repo README 提到 Part II blog，但当前更稳定可核的主证据其实是 **GitHub 渲染后的 `stat-arb-backtest.ipynb` 输出**；
- 这不是同行评审论文，因此应把它定位为 **高信号工程来源**，不是学术定论。

## 5. 这份 repo 真正给了 desk 什么
### 5.1 Universe 定义很干净：不是随便挑币，是 rolling liquid universe
作者先从约 `260` 个 Binance perpetual futures 出发，去掉 stablecoin 合约，然后每个时点只保留：

- **30-day rolling dollar volume 前 30 名**

这点很重要，因为它天然解决了两个短周期 desk 常见坑：
- 别在 illiquid 尾部币里把 funding alpha 看成免费午餐；
- 别把固定币池 survivorship 当成 alpha。

### 5.2 三个特征里，真正该排第一的是 carry
repo/blog 用的三个简单特征是：
- **Carry**：过去 `24h funding rate`
- **Breakout**：靠近 `20d high` 的程度
- **Momentum**：过去 `10d return`

作者自己做 decile、IC 和 decay 后，给出的最关键信息不是“组合起来真好看”，而是：

1. **carry decile 对下一期截面 return 的解释力最强**；
2. **carry IC 更 sticky**，不是只亮一下；
3. **breakout 在 ts 上比 xs 上更有用**；
4. **momentum 最弱、最 noisy**；
5. **carry 与 breakout / momentum 相关性低**，说明它不是简单重复 trend 家族。

这恰好回答了 bot7 现在最看重的问题：
**base alpha 是什么？**

答案就是：**funding/carry predictor 本身。**
不是 breakout，不是 momo，也不是“综合因子”这个空词。

### 5.3 组合方式很朴素，但足够可复制
Part I 里作者先给了固定权重组合：
- `0.5 * carry`
- `0.2 * momentum`
- `0.3 * breakout`

这里最值得 desk 学的不是具体数字，而是排序逻辑：
- carry 最重，因为证据最强；
- breakout 次重，因为可以给组合 net tilt；
- momo 最轻，因为只是弱增强。

这很适合作为 desk 第一版 ablation 顺序：
- 先跑 `carry-only`
- 再加 `breakout tilt`
- 最后再看 `momo` 值不值得留

## 6. notebook 已经把它落成完整策略
### 6.1 策略壳子
GitHub 渲染 notebook 显示，Part II 实际跑的不是粗糙 frictionless plot，而是一个已经包含：
- target weights
- actual positions
- funding accrual
- fixed commission
- no-trade buffer
- turnover analysis
- pyfolio tear sheet

的完整回测壳。

### 6.2 最值得记住的硬数据
GitHub notebook 渲染输出里，`2020-03-12` 到 `2024-02-12`、共 `68` 个月样本，对应结果是：

- **Annual return：`19.8%`**
- **Cumulative returns：`179.0%`**
- **Annual volatility：`20.0%`**
- **Sharpe ratio：`1.00`**
- **Calmar ratio：`0.73`**
- **Max drawdown：`-27.2%`**

而回测壳子里明确写了：
- **commission = `0.0015`**（即约 `15bps` 交易额）
- **trade buffer = `0.05`**
- 标题明确说明：**Weighted 30-day rolling regression Carry/Momo/Breakout**

翻成人话：
- 这不是没成本的教学图；
- 作者已经尝试用 `30d rolling regression` 做动态 expected-return weighting；
- 且承认如果不加 trade buffer，turnover 会太高。

### 6.3 这条策略最 desk-like 的地方：trade buffer 不是附件，而是生死线
repo 里最值得偷的其实不是 feature engineering，而是这段：

**如果当前持仓权重距离目标权重不到某个 buffer，就不交易。**

这非常适合短周期 desk，因为很多横截面/relative-value 组合并不是死在 signal，而是死在：
- 每根都想 rebalance；
- turnover 爆炸；
- fee + slippage 把 edge 吃光。

所以这里的 no-trade buffer 应该直接当成**完整策略的一部分**，不是美化器。

## 7. 对当前 `1m / 3m / 5m / 15m` desk 的正确读法
### 7.1 这条线服务短周期，但不是逐根 1m 主信号
更诚实的拆法是：

- **raw alpha 层**：`24h funding-decile` 的截面强弱
- **ts tilt 层**：`20d breakout`
- **弱增强层**：`10d momo`
- **执行/成本层**：`5% trade buffer` + `5m/1m` 排程执行

也就是说：
- 它当然能服务 `1m/3m/5m/15m` desk；
- 但方式不是“每根 1m 给你 long/short”；
- 而是“每 `15m` 或 `5m` 更新一次 basket target，再用更细频率去低冲击执行”。

### 7.2 这条线和当前主线怎么接
当前学习地图里，Jerry 还在系统化吸收：
- trend / breakout
- ATR / vol regime
- volume confirmation

这份材料刚好让主线从“只会看结构型单币 alpha”扩到：
- **cross-sectional / relative-value raw alpha**
- 但仍保留 `breakout` 作为可解释模块

所以它不是跑偏，而是**在不丢掉熟悉组件的前提下，补一条更市场中性的 alpha 家族**。

## 8. 策略拆解（按 desk 口径重述）
- **方向属性**：横截面 / 相对价值 / 市场中性为主，允许 breakout 带来轻微 net tilt
- **基础 alpha**：`24h funding` 作为 liquid perp 下一期截面相对收益预测器
- **regime**：`20d breakout` 可作为 risk-on / trend-on 期的组合倾斜器
- **filter / veto**：top-30 rolling volume universe；lagged signal；trade buffer；最少有效 universe 数量
- **risk / sizing / execution overlay**：绝对权重归一；rolling regression expected-return weighting；交易成本 `15bps`；buffer `5%`；`5m/1m` 分批执行

## 9. 最小可复现实验（下一步怎么测）
### 9.1 研究假设
**H1：** 在 Binance liquid perp 截面里，`24h funding` 对下一期相对收益仍有可迁移到 `15m/5m` 的预测力。  
**H2：** `breakout tilt` 能提升 gross，但真正决定能否活下来的，是 `trade buffer × 成本壳`。  
**H3：** `momo` 很可能只是边际增强，第一轮可以被 carry-only 或 carry+breakout 打败。

### 9.2 数据源与公开性
- **数据源**：Binance USDⓈ-M perpetual klines / funding history / quote volume
- **公开性**：公开可得
- **更新频率**：价格可到 `1m`；funding 通常 `8h` 一次，可在两次 funding 之间 forward-fill 到 `15m/5m`
- **最小可复现实验口径**：
  - universe：滚动 `30d` quote volume top `30`
  - bar：先用 `15m`，再下钻 `5m`
  - signal：`carry_z`、`breakout_norm`、`momo_z`
  - ranking：截面 rank / zscore

### 9.3 first-pass 实验设计
先不要直接复刻全部 rolling regression，按 desk 速度先做 3 组：

1. **A：carry-only market-neutral**
   - 每 `15m` 更新一次 score
   - `score = z(last_24h_funding)`
   - long top bucket / short bottom bucket
2. **B：carry + breakout**
   - `score = 0.7 * carry + 0.3 * breakout`
3. **C：carry + breakout + momo**
   - 用 repo 原始 spirit：`carry > breakout > momo`

统一壳：
- `next bar` 执行
- gross 归一
- `trade buffer` 跑 `0 / 2% / 5% / 7%`
- fee ladder 跑 `4 / 8 / 12 / 15 bps`
- 先看：净收益、MDD、post-cost、turnover、positive-window ratio

### 9.4 先测什么，不先测什么
**先测：**
- carry-only 是否独立成立
- breakout 是否真的提高 after-cost
- buffer 是否有 hump-shaped sweet spot

**先不测：**
- 复杂 ML
- 过细的 1m 直接重平衡
- 先上几十个币再调参到花

## 10. 风险与限制
1. **这不是论文级严谨证据。** repo/blog 更像工程研究笔记。
2. **作者自己承认 feature exploration 有 lookahead bias 风险。** 所以真正该信的是带 lag、带 fee、带 buffer 的 backtest 壳，而不是 decile plot 本身。
3. **daily 研究往 intraday transfer 时，funding 更新稀疏是核心现实问题。** 这意味着它更像 `15m/5m basket refresh alpha`，不是 ultra-fast scalp。
4. **carry predictor 和 pure carry harvest 不是一回事。** recent desk 笔记里两者要严格分开，不然容易把逻辑读串。

## 11. 一句话结论
**如果 bot7 这轮要给 desk 补一条“能独立复现、还能直接长成完整策略”的 raw alpha，这份 2024 repo 里最值得拿走的，不是三因子 headline，而是：`24h funding` 作为横截面 raw alpha，本体很清楚；`breakout` 作为 tilt 很自然；`trade buffer` 则是让它从研究图变成可交易组合的关键。**
