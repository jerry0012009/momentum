# 别把这份 2026 repo 只读成“trend 打败 mean reversion”：对 short-cycle desk，更该先保留的是「liquid-major 横截面 loser→winner fade 基线」这条 raw alpha
- 时间：2026-04-15 01:13 UTC
- 类型：GitHub / repo source audit（README + notebook source/output + embedded report tables）
- 主题类型：raw alpha
- 基础 alpha：对 liquid-major crypto 横截面，先算最近 `L` 根收益并做横截面去均值；然后 **买入最近相对落后者、卖出最近相对领先者**，赌的是短周期 relative-value mean reversion，而不是单资产方向预测
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-sectional / relative-value / mean-reversion / loser-winner / market-neutral / turnover / slippage / binance-spot / 1h / 15m / 5m / repo / public-data / cost / risk
- 证据类型：工程证据（repo README + notebook源码/内嵌输出 + GitHub metadata）

## 1. 这次看了什么
先回答 base alpha：**这不是“趋势和反转谁赢”的课堂比较题，而是一条可独立抽出来的 raw alpha——对一篮子 liquid majors，做最近相对 loser vs winner 的横截面均值回复。**

这轮主材料是 2026 GitHub repo `mhtkrmz/crypto-alpha-comparison`。repo headline 是 `Crypto Momentum vs Mean Reversion`，但对 desk 更有价值的 intake 其实是其中那条 **cross-sectional mean-reversion baseline**，因为它把：
- 数据口径
- 信号定义
- 组合优化
- 换手惩罚
- slippage 估计
- 固定 cap vs self-financing 口径差异

都放在了同一个 notebook 里，结构很完整，适合拿来当 **short-cycle relative-value baseline**。

repo 的公开环境也比较干净：
- 资产池：`BTCUSDT / ETHUSDT / BNBUSDT / XRPUSDT / ADAUSDT / DOGEUSDT`
- 数据：Binance spot `1h`
- 样本：`2022-01-01 00:00:00 UTC ~ 2026-03-15 15:00:00 UTC`
- 每个资产 `36,832` 根 bar，缺失修复几乎可以忽略（每个品种只补了 `1` 根）
- 统一成本框架：Roll 为主、Corwin-Schultz 为 fallback，最后汇总成 one-way scalar slippage `8.6777 bps`

所以这不是“只靠 README 讲故事”的 repo；它至少给了一个足够透明的 baseline skeleton。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 short-cycle desk 保存下来的，不是“trend beat MR”这句结论本身，而是那条 **无额外花哨 filter 的 liquid-major XS loser→winner fade baseline**。
- **一句话 first verdict：** 这条 baseline **结构上完全可复现，甚至可直接落地成完整策略骨架，但当前公开结果也很明确——它最大的敌人不是预测定义，而是 turnover 与成本。**

### 2.1 raw alpha 到底怎么写
notebook 里的 mean-reversion 信号定义非常直接：

1. 对每个资产算最近 `L` 根的对数收益：
   - `short = log(P_t / P_{t-L})`
2. 对每个时点做横截面去均值：
   - `cs = short - mean(short across assets)`
3. 做波动标准化并通过 `tanh` 截断：
   - `z = cs / (sigma_t * sqrt(L))`
   - `signal = -tanh(z)`
4. 再 **shift 1 根 bar**，避免 lookahead
5. 最后把 `signal * sigma1` 映射成 expected-return 向量 `mu`

repo 在网格搜索里给 mean-reversion 测了：
- `MR_LOOKBACK_GRID = [4, 8, 12, 24]`
- `TURNOVER_PENALTY_GRID = [0.02, 0.05, 0.10]`

最终被 validation 选中的参数是：
- `selected_lookback_bars = 24`
- `selected_turnover_penalty = 0.10`
- `risk_aversion = 15.0`
- `cov_shrink = 0.25`
- `vol_cov_window_bars = 168`

翻成人话就是：**repo 自己最后也承认，短 lookback 反转太容易把换手打爆，所以被选出来的是更慢、更钝一些的 `24h` 横截面 loser/winner fade。**

### 2.2 它为什么算“完整策略骨架”
这轮我把它归为“可直接落地完整策略 = 是”，原因不是它已经 profitable，而是因为 repo 把完整骨架基本补齐了：

- **entry：** 每根 bar 依据上一步计算出来的 `mu_t` 重新解目标权重
- **signal timing：** 明确 `shift(1)`，即只用 `t-1` 之前能知道的信息
- **sizing / allocator：**
  - 每根 bar 解：
    - `max mu'w - 0.5*lambda*w'Sw - 0.5*kappa||w-w_prev||^2`
    - 约束：`||w||_1 <= 1`
  - 再乘 `GROSS_CAP = 100,000 USDT`
- **neutrality：** mean-reversion 分支里会再对 `mu` 去均值，保持近似 market-neutral
- **risk：** rolling covariance + shrinkage + risk aversion
- **turnover control：** `kappa` 显式惩罚 `||w-w_prev||`
- **cost：** one-way slippage scalar `s = 8.6777 bps`
- **performance accounting：** 同时给 fixed-cap 和 equity-protected/self-financing-like 口径

所以这不是一个“只有信号、没有执行壳”的 idea，而是一条很适合拿来做 **desk baseline / ablation anchor / negative control** 的完整 shell。

### 2.3 公开结果：问题不是信号没法定义，而是 turnover 太贵
repo notebook 的验证/测试与成本结果非常说明问题。

先看 mean-reversion 被选中的参数在 validation / test：
- validation Sharpe：`-1.207`
- validation cumulative PnL：`-69,135.87 USDT`
- validation avg turnover：`7,460.50 USDT / bar`
- test Sharpe：`+0.623`
- test cumulative PnL：`+17,714.81 USDT`
- test avg turnover：`6,246.84 USDT / bar`

这组数本身就在提醒：**它不是那种 validation、test 都顺的稳健 alpha，而是明显带着 regime/样本依赖。**

再看全样本成本归因：
- mean-reversion gross PnL：`-141,850.67 USDT`
- total turnover：`245.06M USDT`
- estimated slippage cost：`212,658.24 USDT`
- net PnL（fixed 100k cap 口径）：`-354,508.91 USDT`
- cost drag = `149.92%` of `|gross PnL|`

翻成人话：**这条 baseline 甚至不是“有 gross edge 但被成本吃掉”，而是 gross 已经不强，成本再补一刀，直接把它打成负教材。**

更关键的是 notebook 还主动暴露了 accounting 风险：
- 在 `fixed_100k_cap` 口径下，trend 看起来 net 还能赚 `+243,432.38 USDT`
- 但到了 `equity_protected_cap`（更接近 self-financing）口径，trend 和 MR 最终都接近把 `10,000 USDT` 初始资本亏穿
- mean-reversion 的 first nonpositive net equity time：`2022-10-29 08:00 UTC`

所以这个 repo 的真正教育价值不是“trend 永远赢”，而是：**同样一套统一 optimizer 下，plain XS reversal 在 liquid majors 里很容易先死于换手，而固定 gross cap 会让策略看起来比真实 live 账户强。**

## 3. 为什么和当前项目有关
这条线和当前 desk 直接相关，不是因为它马上能上 production，而是因为它正好补我们现在最需要的一块：

1. **它是明确的 raw alpha。**
   base alpha 非常清楚：`cross-sectional loser-bounce / winner-fade`。

2. **它是“无复杂 filter”的基线。**
   我们最近 intake 里不少 reversal / pairs / XS 主题都带筛选层、状态层、admission 层。这个 repo 的价值恰恰在于：先给你一条 **plain baseline**，方便之后做增量对照。

3. **它能自然映射到 `15m/5m`。**
   虽然原始 repo 是 `1h`，但它的数学结构完全可以平移到更短周期：
   - `15m`：做主信号与组合层
   - `5m / 3m / 1m`：做 child execution / queueing / cost control

4. **它帮我们识别“反转为什么死”。**
   不是所有失败都没价值。对于 desk 来说，一条失败得很透明的 baseline，经常比一条写满 filter、却说不清 base alpha 的策略更有研究价值。

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / relative-value / market-neutral
- 基础 alpha：最近一段时间相对跑输的资产，下一段时间更容易对相对跑赢者做均值回复
- regime：repo 原版没有额外 regime gate；它本质上就是 plain baseline
- filter / veto：主要不是市场状态 filter，而是通过 `tanh` 截断、covariance、risk aversion、turnover penalty 来限制极端权重与过度换手
- risk / sizing / execution overlay：L1 gross-cap 约束、shrunk covariance、turnover penalty、slippage scalar；真正的主风险不是方向错，而是 **换手过高 + 真实资本约束**

## 4. 可复刻的最小实验
### 4.1 desk 化映射
这条线最自然的 short-cycle 映射不是“把 1h notebook 原封不动搬到 1m”，而是：
- **主 alpha 频率：`15m`**
- **子执行频率：`5m`**（有余力再下钻 `3m/1m`）

对应关系：
- 原版 `24 x 1h` lookback 约等于 `24h`
- 若迁到 `15m`，第一版就用 `96 x 15m` lookback
- 若迁到 `5m`，同等时间窗大约是 `288 x 5m`

也就是说：**先保持“经济时间”不变，再压缩 bar 频率；不要一上来把 `24` 根机械地改成 `24 x 15m`，那会把 alpha 本体改掉。**

### 4.2 最小实验口径
第一版建议：
- 市场：Binance USDⓈ-M 或 spot（先以 perp 更贴 desk）
- 资产池：先从 `BTC / ETH / BNB / XRP / ADA / DOGE / SOL` 这类 liquid majors 开始
- 主信号：
  - `ret_L = log(P_t / P_{t-L})`
  - `cs_ret = ret_L - cross-sectional mean(ret_L)`
  - `z = cs_ret / (sigma_1 * sqrt(L))`
  - `signal = -tanh(z)`
- 约束：近似 market-neutral，`gross <= 1`
- 组合：先复刻 repo 的 `risk_aversion + turnover_penalty + shrunk covariance`
- 成本：至少跑 `2 / 4 / 6 / 8 bps` roundtrip ladder

### 4.3 必做对照组
至少同时跑这四组：
1. **plain XS reversal baseline**（完全照 repo 思路）
2. **top-liquidity admission**（只留流动性前半区）
3. **session pocket**（只做某些日内窗口）
4. **child-execution 版**（`15m` 信号，`5m` 分批进场）

因为这轮最关键的问题不是“MR 有没有定义”，而是：**plain baseline 到底死在 alpha 本身，还是死在可交易性与执行。**

### 4.4 先看哪些指标
这条线不要先被 Sharpe 带跑，先看：
- `net bps / rebalance`
- `turnover / gross exposure`
- `holding horizon`
- `winner leg` 与 `loser leg` 的分腿贡献
- `cost-as-%-of-gross-PnL`
- `fixed-cap` vs `equity-linked` 口径差异

原 repo 的一个很强信号就是：
- mean-reversion 平均持有大约 `29.4` 根 `1h` bar（约 `1.23` 天）
- 但换手依然高到 `6.65k USDT / bar` 量级

这恰好说明：**不是你想象中的 ultra-HFT 才会死于 turnover；中低频 XS rebalance 同样会。**

### 4.5 下一步怎么测
- **第一步：** 先在 `15m` 上原样复刻 plain baseline，保持“经济时间窗”一致，即先试 `96 x 15m` lookback。
- **第二步：** 不加 fancy filter，先只做 `cost ladder + universe admission`，看看 edge 是否只是被低流动性腿拖死。
- **第三步：** 若 plain baseline 仍然明显不过线，再只加一层最便宜的结构性修补：
  - `top-liquidity admission`
  - `min spread / min quote volume veto`
  - `rebalance threshold`（小信号不调仓）
- **第四步：** 如果修补后仍不行，就把它降级成 **negative-control baseline**，以后凡是新的 XS reversal / pairs / lagger-catch-up 主题，都必须先对比它。

## 5. 风险与保留意见
- **这是完整骨架，不是现成可上线 alpha。** 可执行与可赚钱是两回事。
- **公开结果已经偏负面。** 这点反而要正视，别把 repo headline 翻译成“trend good, MR bad”然后就草草带过。
- **fixed gross cap 很会美化结果。** 对任何 short-cycle 组合策略，都必须额外看 equity-linked/self-financing 口径。
- **迁到 `15m/5m` 不保证更好。** 更高频只会让 turnover 更敏感；除非 child execution 真能明显降成本，否则直觉上只会更难。
- **这条线最适合的定位可能不是 production shell，而是 ablation anchor。** 但这依然很值钱，因为它能帮 desk 分清“哪些额外 filter 真有增量”。

## 6. 来源
- Mehmet Kurmaz. (2026). *crypto-alpha-comparison*. GitHub Repo.  
  Repo URL: `https://github.com/mhtkrmz/crypto-alpha-comparison`
- Mehmet Kurmaz. (2026). *Crypto Momentum vs Mean Reversion*. README.  
  Readable URL: `https://raw.githubusercontent.com/mhtkrmz/crypto-alpha-comparison/main/README.md`
- Mehmet Kurmaz. (2026). *Code.ipynb*. GitHub Notebook.  
  Readable URL: `https://github.com/mhtkrmz/crypto-alpha-comparison/blob/main/Code.ipynb`
- Mehmet Kurmaz. (2026). *Report.pdf*. GitHub bundled report.  
  Readable URL: `https://github.com/mhtkrmz/crypto-alpha-comparison/blob/main/Report.pdf`
- GitHub API metadata: repository created `2026-03-30`, description `Systematic crypto trading study: trend-following vs mean-reversion.`

## 7. 本地产物
- Digest：`research/quant_digests/2026-04-15_0113_liquidmajor-xs-loserwinner-fade-baseline.md`
