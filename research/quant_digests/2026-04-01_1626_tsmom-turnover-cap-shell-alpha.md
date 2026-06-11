# 别把这份 2026 新 repo 只读成“trend-vs-MR 课程作业”：对 short-cycle desk，更该先测的是「vol-normalized TSMOM × turnover-penalized cap allocator」这条完整 raw alpha

- 主题类型：raw alpha
- 基础 alpha：**波动率归一化后的 time-series momentum / trend continuation**；具体就是 `log(P_t / P_{t-L}) / (σ_t * √L)` 经过 `tanh` 压缩后，映射成连续多空目标仓位
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-01 16:26 UTC
- 类型：2026 GitHub 新仓库 source audit（`README.md` + `Code.ipynb` + `Report.pdf` + GitHub API metadata）
- 主题标签：raw-alpha/trend/momentum/time-series/vol-normalized/tanh/turnover-penalized/cap-constrained/multi-asset/binance/majors/btc/eth/bnb/xrp/ada/doge/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：2026 GitHub 新仓库 source audit（README + notebook 公式/回测输出 + repo metadata）

## 1. 这次看了什么
这次主材料不是论文，而是一份 **2026-03-30 创建** 的 GitHub 新仓库：**mhtkrmz (2026), _crypto-alpha-comparison_**。headline 看起来像“趋势 vs 均值回复”的课程项目，但对我们 desk 真正更值得 intake 的，不是它在讲两派孰优孰劣，而是它把一条 **可直接复现的多资产 TSMOM 完整策略骨架** 写得非常清楚：

- 用 Binance 公共 `1h` OHLCV 抓 6 个 liquid majors；
- 把 **log-momentum / realized vol / rolling covariance / turnover penalty / gross cap** 串成同一个目标仓位优化器；
- 用完全相同的组合壳子，公平比较 `trend_following` 和 `mean_reversion`；
- 最后再把 **Roll / Corwin-Schultz** 推出来的滑点估计接到净值端。

翻成人话：
**它不是在说“趋势永远比反转好”，而是在说“如果你真要做短中短周期的多资产 raw alpha，至少该把信号、仓位、换手惩罚、风险协方差、成本放进同一个壳子里比较”。**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这篇 digest 的主角不是 repo 里的 mean reversion 支线，而是它更清楚、也更适合当前 desk 主线的那条 **trend-following raw alpha**：

- 先看某个币过去 `L` 根 bar 的对数收益 `log(P_t / P_{t-L})`；
- 再除以 `σ_t * √L`，把不同币、不同波动状态下的动量强度归一到同一量纲；
- 再用 `tanh` 压缩极端值，避免单个极端趋势把仓位直接拉满；
- 最后得到连续目标收益 `mu = signal * sigma1`，再进入带换手惩罚和风险惩罚的仓位分配器。

翻成人话：
**base alpha 就是“波动率调整后的趋势延续”：涨得又稳又持续的币，应该比刚刚乱冲的币拿到更高的持续性仓位。**

所以这轮它明确属于：
- `raw alpha`
- `trend / momentum`
- `time-series`
- 不是 filter，不是 regime，也不是只能挂靠别的 alpha 才有意义的 overlay。

## 3. 为什么这轮值得写，而不是继续补一个只会服务别人的 gate
结合当前学习主线，这轮值得写有三个原因：

1. **它正好补的是主线缺口。** `LEARNING_TRACK.md` 和 `FACTOR_BACKLOG.md` 里，趋势/动量一直是明确优先级，但当前 backlog 里更偏“方向过滤 / breakout / ATR 概念”，而缺一张真正把 **raw alpha + sizing + risk + turnover + cost** 串起来的完整趋势策略卡。
2. **它不是抽象论文，而是公开 repo。** 数据、公式、参数网格、验证 / 测试切分、成本估计都能直接抄成最小实验。
3. **它提供了一个很值钱的对照。** 在同样的组合壳子下，repo 里的 cross-sectional mean reversion 基本跑不出来，而 TSMOM 至少在 pre-cost / validation 上明显更强。这对 desk 很重要，因为它能帮助我们少走“均值回复幻觉 + 执行壳子没统一”的弯路。

## 4. 这次看的主来源
### 4.1 主来源（repo）
- **Author / Repo owner**：mhtkrmz
- **Year**：2026
- **Title / Repo**：*crypto-alpha-comparison*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：https://github.com/mhtkrmz/crypto-alpha-comparison
- **Repo URL**：https://github.com/mhtkrmz/crypto-alpha-comparison
- **GitHub metadata**：created `2026-03-30T12:20:22Z`，pushed `2026-03-30T12:24:35Z`

### 4.2 这轮实际看的关键文件
- `README.md`
- `Code.ipynb`
- `Report.pdf`

## 5. 这条 raw alpha 在代码里到底怎么定义
### 5.1 数据宇宙非常朴素，但够做 clean replication
repo 从 Binance 公共 `1h` K 线下载这 6 个币：
- `BTCUSDT`
- `ETHUSDT`
- `BNBUSDT`
- `XRPUSDT`
- `ADAUSDT`
- `DOGEUSDT`

样本区间是：
- **2022-01-01 00:00 UTC → 2026-03-15 15:00 UTC**
- 每个币 **36,832 根 `1h` bars**

这很重要，因为它不是拿几周数据讲故事，而是拿了一个跨牛熊、跨 regime 的中等长度样本。

### 5.2 repo 直接把趋势信号公式写出来了
`Code.ipynb` 里的核心函数是：

- `make_trend_mu(close_df, sigma1_df, lookback)`
- 公式：`signal_t ~ tanh( log(P_t / P_{t-L}) / (sigma_t * sqrt(L)) )`
- 然后 **shift 1 bar** 避免 lookahead
- 再映射成 `mu = signal * sigma1`

几个关键点：
1. **不是裸收益排序。** 它先做了波动率归一化，避免高波动币因为“涨跌更猛”天然压过别的币。
2. **不是二元多空。** `tanh` 把仓位信号做成连续值，强趋势拿更大仓位，弱趋势拿更小仓位。
3. **不是只看 signal，不管执行。** 后面它不是简单 equal-weight，而是直接塞进带惩罚项的组合优化器。

### 5.3 组合壳子本身也是这份 repo 最值钱的部分
`run_strategy(...)` 每根 bar 解的问题是：

1. `max_w mu'w - 0.5*lambda*w'Sw - 0.5*kappa||w - w_prev||^2`
2. 约束：`||w||_1 <= 1`
3. 名义仓位：`theta = gross_cap * w`

翻成人话：
- `mu'w`：你想追 alpha
- `lambda*w'Sw`：但要怕波动 / 协方差风险
- `kappa||w-w_prev||^2`：还要怕频繁调仓带来的换手与成本
- `||w||_1 <= 1`：总 gross 暴露不能无限开

这对 desk 的价值非常直接：
**它已经把“信号强度”和“能不能低换手、低冲击地抱住仓位”放到同一层处理。**

### 5.4 参数网格也很适合直接迁移
repo 的固定设置：
- `STARTING_CAPITAL = 10,000 USDT`
- `GROSS_CAP = 100,000 USDT`
- `VOL_COV_WIN = 168`（1 周 `1h` bar）
- `RISK_AVERSION = 15.0`
- `COV_SHRINK = 0.25`
- 训练 / 验证 / 测试切分：`60% / 20% / 20%`

趋势 lookback grid：
- `24 / 72 / 168 / 336` bars

mean reversion lookback grid：
- `4 / 8 / 12 / 24` bars

turnover penalty grid：
- `0.02 / 0.05 / 0.10`

这意味着：
**这份 repo 不是“给你一个结论”，而是直接给你一张能搬到 `15m/5m/3m/1m` 的实验模板。**

## 6. 最值得拿走的硬数据点
### 6.1 validation 上，趋势分支明显比反转分支更像样
repo 在统一壳子下给出的最佳 validation 组合：

**Trend-following**
- best lookback：`336` bars
- best turnover penalty：`0.02`
- `validation_sharpe = 2.5225`
- `validation_cum_pnl_usdt = 223,220`
- `validation_avg_turnover_usdt = 2,533`

**Mean reversion**
- best lookback：`24` bars
- best turnover penalty：`0.10`
- `validation_sharpe = -1.2071`
- `validation_cum_pnl_usdt = -69,136`
- `validation_avg_turnover_usdt = 7,461`

这组数非常值钱，因为它说明在同一 universe、同一 gross cap、同一 risk shell 下：
**反转不但没赢，换手还更高；趋势至少在 validation 上是又强又更省换手。**

### 6.2 test 不是爆炸优秀，但至少没有 validation 那么像幻觉
最佳 locked 参数在 test 上：

**Trend-following**
- `test_sharpe = 0.3430`
- `test_cum_pnl_usdt = 21,368.6`
- `test_avg_turnover_usdt = 2,522.6`

**Mean reversion**
- `test_sharpe = 0.6227`
- `test_cum_pnl_usdt = 17,714.8`
- `test_avg_turnover_usdt = 6,246.8`

这里要注意两点：
1. 反转 test 看起来“意外转正”，但因为 validation 全面为负，所以更像 sample luck，而不是稳健 alpha。
2. 趋势 test sharpe 只有 `0.34`，说明这不是“闭眼就上的神策略”，而是 **值得继续加 friction ladder、改时间尺度、换执行壳子** 的 raw alpha 候选。

### 6.3 它给了一个很实用的滑点标尺
repo 用 Roll / Corwin-Schultz 做了资产级滑点估计，最后选出的统一标尺是：
- **`s = 0.00086777` decimal per trade**
- 也就是 **`8.6777 bps` one-way**

并且 notebook 里展示的资产级估计里，至少可以看到：
- BNB 约 `5.23 bps`
- BTC 约 `5.97 bps`
- ETH 约 `6.92 bps`
- ADA 约 `9.06 bps`
- XRP 约 `10.41 bps`

翻成人话：
**这份 repo 最有价值的一点，不是回测赚了多少，而是它逼你承认“多资产短周期 alpha 的成本壳必须先写进去”。**

### 6.4 全样本净值一上成本，问题立刻暴露
在 Part 4 的 fixed-100k-cap 模式下：

**Trend-following**
- gross total pnl：`333,853 USDT`
- net total pnl：`243,432 USDT`
- total cost：`90,421 USDT`
- avg holding horizon：`70.05` bars（约 `2.92` 天）

**Mean reversion**
- gross total pnl：`-141,851 USDT`
- net total pnl：`-354,509 USDT`
- total cost：`212,658 USDT`
- avg holding horizon：`29.42` bars（约 `1.23` 天）

这组数字的 desk 读法不是“趋势一定稳赚”，而是：
- 趋势分支 **更低换手、持有更久、成本侵蚀更慢**；
- 反转分支 **先天换手更高，成本一上来就被吃死**。

## 7. 对当前 desk，最该偷的不是“趋势赢了”，而是这 3 个具体组件
### 7.1 组件一：vol-normalized momentum，而不是裸 return 排名
这能直接补当前主线里对“多周期动量”的理解：
- 不是看谁涨得多就追谁；
- 而是看谁在 **单位波动风险下** 的趋势更干净。

### 7.2 组件二：turnover penalty 要从第一天就跟 alpha 写在一起
repo 最有启发的一点不是 `Sharpe 2.52`，而是：
**同样的 alpha，如果你不惩罚换手，最终可能只是把 gross edge 全喂给滑点。**

这和当前 `FACTOR_BACKLOG.md` 里强调的 post-cost 评估是完全一致的，而且比“先出信号、后补成本”更像能进实盘候选池的写法。

### 7.3 组件三：用同一 allocator 比 raw alpha，而不是每条策略都带不同壳子
很多 repo 看起来像在比较 signal，实际上比较的是：
- 有的用了更强的仓位控制
- 有的换手更少
- 有的根本没算成本

这份 repo 的好处是：
**它先把壳子固定，再比较 trend vs MR。**
这让“哪条 raw alpha 更值得继续”这个问题变得更干净。

## 8. 这份 repo 为什么仍然不能直接照抄进实盘
### 8.1 时间尺度不是我们现在的默认主战场
repo 的 native 实验是 `1h`。这对当前以 `5m / 15m` 为主、也接受 `1m / 3m` 的 desk 来说，不是最终答案。

但它仍然很有用，因为：
- 公式是 bar-based，可直接缩放到更快周期；
- 组合壳子与成本壳本身就是可以复用的；
- 它更像是一个 **干净、公开、能搬运的骨架**。

### 8.2 资本约束写法有点“作业式”而不是 production-ready
它设：
- initial capital `10k`
- gross cap `100k`

这会让回测读起来更像“固定 gross exposure assignment”，而不是一个真正受保证金 / 爆仓 / 资金曲线约束的 production shell。

所以：
**它是完整策略定义，不等于 production-ready portfolio engine。**

### 8.3 mean reversion 支线不该被误读成“又一条可用候选”
从 validation 来看，这条 cross-sectional MR 在这套壳子里基本是输家。

因此更合理的 desk 读法是：
- 把它当 repo 内的 **对照组**；
- 主 intake 仍然是 **trend-following raw alpha + allocator shell**；
- 而不是“顺手把反转支线也塞进 backlog”。

## 9. 对 `15m / 5m / 3m / 1m` 的最小实验怎么做
### 9.1 先做 `15m`，因为它最像“保留趋势信息但不至于太慢”
第一版最小实验建议：

- universe：`BTC / ETH / BNB / SOL / XRP / ADA`
- bar：`15m`
- signal：
  - `mom_L = log(P_t / P_{t-L})`
  - `z_L = mom_L / (σ_t * √L)`
  - `signal = tanh(z_L)`
  - `mu = signal.shift(1) * sigma1`
- sigma：rolling `1-bar` return std，再 shift 1
- covariance window：`96 / 192` bars
- lookback grid：`96 / 192 / 384 / 672 / 1344` bars
- turnover penalty：`0.02 / 0.05 / 0.10 / 0.20`
- gross cap：先固定成 `1x` 和 `2x` 两档，不要一上来就学 repo 的 `10x`

执行口径：
- 每根 `15m` bar close 计算目标仓位
- 下一根 open 或 next-bar VWAP 调整仓位
- 统一 friction ladder：`2 / 4 / 6 / 8 / 10 bps` one-way
- perp 版本额外扣 funding

### 9.2 再下钻到 `5m`
如果 `15m` 还能留边，再把同一骨架搬到 `5m`：
- lookback 先试 `96 / 288 / 576 / 864`
- covariance window 先试 `96 / 288`
- 重点观察 turnover 是否失控

这里最重要的不是追高 Sharpe，而是看：
**同样的 vol-normalized TSMOM，在更快 bar 上还能不能在成本后留下稳定边。**

### 9.3 `3m / 1m` 不建议直接上 full allocator，先做 alpha-existence
更快周期建议先降级：
- 单币先看 `signal` 分层后的 forward return monotonicity
- 再看 top-quantile vs bottom-quantile 的下一段收益差
- 只有当 alpha-existence 明确存在，再上多资产 allocator

不然会过早把“执行噪音 + 组合噪音 + 成本噪音”全揉在一起。

## 10. 下一步怎么测（必须落地）
### 10.1 第一优先级：把 repo 的 trend 分支单独移植到 desk 默认框架
不是复刻整个 trend-vs-MR 作业，而是只移植：
- `make_trend_mu`
- `run_strategy` 的目标函数结构
- `turnover_penalty`
- `gross cap + friction ladder`

目标：
**先确认“vol-normalized TSMOM + turnover penalty”在 `15m` 上是否仍有成本后生存空间。**

### 10.2 第二优先级：做一个公平对照
用完全同一壳子，只换 alpha：
1. `vol-normalized TSMOM`
2. 当前 desk 自带的 multi-timeframe momentum baseline
3. 一个简单 XS lagged-return continuation baseline

只比较：
- post-cost return
- max drawdown
- avg turnover
- positive asset ratio / positive window ratio

这样才能知道：
**值得搬的，到底是“repo 的 alpha”，还是“repo 的 allocator shell”。**

### 10.3 第三优先级：做 friction cliff 图
最值得先画的不是净值，而是：
- x 轴：one-way bps
- y 轴：net return / Sharpe / turnover-adjusted edge
- 多条曲线：不同 `L`、不同 `kappa`

因为这类策略最怕的不是“均值收益不够高”，而是：
**一旦从 4 bps 滑到 8 bps，就整条曲线掉下悬崖。**

## 11. 一句话结论
**这份 2026 新 repo 真正值得 desk intake 的，不是“趋势赢了反转”，而是那条能直接搬到 `15m/5m` 的完整骨架：vol-normalized TSMOM 信号 + turnover-penalized cap allocator + 明确 friction shell。**

## 12. 它是怎么证明这件事的
**它靠的是公开 Binance 多资产样本上的统一壳子回测与成本估计：先把 trend 和 MR 放进同一优化器比较，再把滑点壳接进去，看谁还能活。**
