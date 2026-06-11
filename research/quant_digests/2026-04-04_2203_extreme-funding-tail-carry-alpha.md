# 别把这份 2026 funding-arb repo 直接当成“APR>5 就开”的 carry 脚本：对 short-cycle desk，更该先测的是「extreme-funding-only × boundary-time entry / fee-churn veto」这条 raw alpha

- 时间：2026-04-04 22:03 UTC
- 类型：2026 GitHub 新 repo source audit（`CLAUDE.md` + `config/settings.py` + `src/strategy/funding_arb.py` + `scripts/backtest.py`）+ Binance USDⓈ-M 公共 funding history 最小复现
- 主题类型：raw alpha
- 基础 alpha：**当同标的 perp funding 处于足够高的正值时，做 `long spot + short perp` 收 funding；但这条 alpha 不能按“APR>5% 就持续开着”去跑，而要缩成“只做极端正 funding 尾部 + 靠近 funding boundary 的低周转收息”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/spot-perp/same-underlier/delta-neutral/extreme-apr-only/funding-boundary/fee-churn-veto/binance/btc/eth/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：开源 repo 规则审计 + 公共 funding API 快速复现

## 1. 这次看了什么
这轮主看的是一个很新的仓库：

- **tomvdrslt (2026), _funding-rate-arbitrage-bot_**
  - GitHub repo：<https://github.com/tomvdrslt/funding-rate-arbitrage-bot>
  - GitHub API 元数据显示：仓库创建于 **2026-03-13**，描述是 **“Delta-neutral crypto bot collecting perpetual futures funding payments”**

我之所以把它捞进来，不是因为“funding carry”这个词有多新，而是因为它把一条**完整可执行策略**写得非常明白：
- 数据源：Binance public funding history
- entry / exit：APR 阈值状态机
- sizing：固定仓位上限
- risk：日亏损、总回撤、交易所暴露度 kill-switch
- cost：双腿进出费

这符合我们本轮优先级里最值钱的那一档：

> **不是解释 carry 为什么存在，而是直接给出一个能写成策略回测/实盘壳子的 raw alpha。**

但 desk 真正该 intake 的，不是 repo 表面那句“APR > 5% 就开”。

真正值钱的结论反而是：

> **正 funding carry 这条 raw alpha 只有在极端正 funding 尾部、并且你能把周转压得足够低时，才更像一条能留下净收益的 alpha；默认 5%/3% 阈值状态机会被手续费来回磨死。**

## 2. 先回答：这篇东西的 base alpha 是什么？
先把最关键的问题说透。

### 2.1 base alpha 不是 filter，也不是 overlay
这条东西的 base alpha 很明确：

> **base alpha = 同标的、delta-neutral 的正 funding carry。**

也就是：
- perp funding 为正；
- 做 `long spot + short perp`；
- 方向风险尽量互相对冲；
- 主要赚的是 funding payment，而不是赌价格方向。

所以它不是“拿 funding 当行情过滤器”；
它本身就是一条独立可交易的 **carry / funding raw alpha**。

### 2.2 但它不是逐根 `1m/5m` 方向预测
这里必须老实一点：
- funding 主时钟天然是 **8h**；
- 它不是每根 `1m/3m/5m/15m` 都有独立预测力的那种方向型 signal。

对 short-cycle desk 来说，正确读法是：
- **alpha 本体：** funding carry
- **短周期价值：** 用 `1m/3m/5m/15m` 做入场择时、basis 监控、滑点控制、临近 funding 边界的执行优化

也就是说：

> **这是“慢 alpha，快执行”的 raw alpha，不是伪装成逐 bar 主信号的低频变量。**

## 3. repo 里到底写了什么硬规则
repo 的策略骨架非常直接。

### 3.1 entry / exit 规则
`src/strategy/funding_arb.py` 写的是：
- funding < 0 且当前持仓中 → `EXIT`
- funding < 0 且没持仓 → `NO_TRADE`
- 已持仓且 APR < `min_exit_apr` → `EXIT`
- 未持仓且 APR >= `min_entry_apr` → `ENTER`
- 已持仓且 APR >= `min_exit_apr` → `HOLD`

默认阈值来自 `config/settings.py`：
- `MIN_FUNDING_ENTRY_APR = 5.0`
- `MIN_FUNDING_EXIT_APR = 3.0`

翻成人话：

> **repo 认为：只要正 funding 年化够到 5%，就值得开 delta-neutral carry；跌破 3% 或转负，就离场。**

### 3.2 sizing / risk / polling
同一个配置文件里还给了：
- 单资产最大仓位：`20%` 组合资金
- 交易所最大暴露：`50%`
- 日亏损停机：`3%`
- 总回撤停机：`15%`
- delta 再平衡阈值：`2%`
- funding poll interval：`3600s`

这意味着它不是单纯“看 funding 的 notebook”，而是已经把：
- **entry / exit**
- **仓位**
- **risk kill-switch**
- **execution cadence**

都写成了一个完整壳子。

### 3.3 backtest 成本假设
`scripts/backtest.py` 里把每次进场/离场的双腿费用都写死成：
- `ENTRY_FEE_PCT = 0.0014`
- `EXIT_FEE_PCT = 0.0014`

也就是：
- 一次开仓成本 ≈ **14 bps of notional**
- 一次平仓成本 ≈ **14 bps of notional**

而 funding 收益则按：
- `annualized_apr = funding_rate_8h × 3 × 365 × 100`

这套假设简单，但足够做最小 sanity check。

## 4. 这份 repo 真正值钱的，不是“carry 存不存在”，而是它暴露了 fee-churn 问题
repo 的 aspirational checkpoint 写得挺乐观：
- 跑 `BTC` 730 天回测，**希望**看到 annualized return > 5%、Sharpe > 1、MDD < 15%

但我更关心的是：

> **如果我们按它源码里最朴素的 5%/3% 阈值和成本口径直接复现，结果到底活不活？**

于是我直接抓了 Binance 公共 funding history，按 repo 的规则快跑了一遍。

数据源：
- Binance Open Platform：**Get Funding Rate History**  
  <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History>

口径：
- 标的：`BTCUSDT`, `ETHUSDT`
- 样本：近 `365d` / `730d`
- 资金：`10,000`
- 持仓：`20%` 组合 notional
- 费用：开/平各 `14 bps`（沿用 repo）
- 规则：完全复刻 `APR >= entry` 进，`APR < exit 或 funding < 0` 出

## 5. 最关键的 4 个数据点
### 5.1 默认 `5% / 3%` 阈值，在 BTC/ETH 上都被手续费磨成负收益
近 `730d` 的最小复现结果：

#### BTCUSDT
- 平均 annualized APR：**5.80%**
- 满足 `APR >= 5%` 且 funding 非负的窗口占比：**54.7%**
- 交易次数：**422** 次
- 累计 funding 收入：**$230.65**
- 累计费用：**$1181.60**
- 组合总回报：**-9.51%**
- 最大回撤：**9.56%**

#### ETHUSDT
- 平均 annualized APR：**6.00%**
- 满足 `APR >= 5%` 且 funding 非负的窗口占比：**57.6%**
- 交易次数：**414** 次
- 累计 funding 收入：**$248.01**
- 累计费用：**$1159.20**
- 组合总回报：**-9.11%**
- 最大回撤：**9.16%**

一句话总结：

> **不是 funding 不够高，而是默认阈值导致周转太多，费用远大于 funding。**

### 5.2 把 entry 提高到 `10%`、exit 提到 `5%`，仍然没救活
近 `730d`：

#### BTCUSDT
- 收益：**-3.71%**
- 交易次数：**194**
- funding：**$172.06**
- fees：**$543.20**

#### ETHUSDT
- 收益：**-3.61%**
- 交易次数：**196**
- funding：**$187.30**
- fees：**$548.80**

这说明“把阈值随便往上抬一点”还不够。

### 5.3 只有进入极端正 funding 尾部，carry 才开始勉强翻正
当阈值进一步抬到 `entry=15% / exit=8%`：

#### BTCUSDT
- 总回报：**+0.41%**（730d）
- 交易次数：**6**
- funding：**$58.13**
- fees：**$16.80**

#### ETHUSDT
- 总回报：**+0.54%**（730d）
- 交易次数：**6**
- funding：**$70.80**
- fees：**$16.80**

但这个“翻正”有两个现实含义：
1. **它只是在极端 funding 尾部才像个 alpha；**
2. **它很慢、很稀疏，不该被误读成高频主引擎。**

### 5.4 极端 funding 尾部本来就很少
近 `730d`，满足条件的窗口占比：

#### BTCUSDT
- `APR >= 5%`：**54.7%**
- `APR >= 10%`：**30.4%**
- `APR >= 15%`：**2.60%**
- `APR >= 20%`：**1.74%**

#### ETHUSDT
- `APR >= 5%`：**57.6%**
- `APR >= 10%`：**31.6%**
- `APR >= 15%`：**4.06%**
- `APR >= 20%`：**2.51%**

这组数字很重要，因为它告诉我们：

> **真正有净边际的 funding carry，不是“大多数正 funding”，而是“极少数极端正 funding”。**

## 6. 对我们 desk 最有价值的重构读法
### 6.1 不要把它继续当成“全天开着”的 carry bot
如果按 repo 默认读法：
- 每小时轮询；
- 只要 APR >= 5% 就开；
- 跌破 3% 就平；

那更像是在制造：
- 高频开平仓；
- 低净 funding；
- 高 fee churn。

这不适合 short-cycle desk。

### 6.2 更适合我们的读法：extreme-funding-only
对 desk 更值钱的 branch idea 是：

> **只做极端正 funding 尾部，把 carry 从“常开仓”改成“事件驱动的稀疏收息”。**

也就是：
- alpha 本体仍然是正 funding carry；
- 但只在 `APR >= 15%`、甚至 `>= 20%` 的极端窗口里考虑入场；
- `1m / 3m / 5m / 15m` 只负责把这笔慢 alpha 做得更便宜、更稳。

### 6.3 短周期真正该干的事是 execution，不是假装逐 bar 预测
对 `1m / 3m / 5m / 15m`，最合理的工作不是：
- 用 funding 直接预测下一根 K 线涨跌；

而是：
- 监控 funding boundary 前后的 spot-perp basis 漂移；
- 选择更便宜的入场时点；
- 检查 funding 极端是否已经被 mark premium 过度透支；
- 控制进出场的 taker 成本和再平衡次数。

翻成人话：

> **这条 alpha 的 edge 在 funding，本地化收益在 execution。**

## 7. desk 化后的最小实验：直连 `1m / 3m / 5m / 15m`
### 7.1 第一轮不要再跑“全天候 5/3 carry”
直接比较 4 本书：

1. **Repo baseline**  
   - `entry=5%`, `exit=3%`
2. **Higher threshold**  
   - `entry=10%`, `exit=5%`
3. **Extreme-only**  
   - `entry=15%`, `exit=8%`
4. **Boundary-timed extreme-only**  
   - 仍用 `15%/8%`，但只允许在下一个 funding 结算前 `30~60min` 内建仓，结算后固定持有 `1` 个 funding window 或到 `APR/basis` 失真时离场

### 7.2 执行层直接落到 `5m / 15m`
建议第一版：
- `15m`：决定是否允许开仓
- `5m`：做具体进场择时
- `1m / 3m`：只在第二轮评估 maker/taker 可行性时再细化

### 7.3 加一个我们 desk 更需要的 veto
第一轮最值得加的不是复杂 ML，而是一个很土但很有用的 veto：

> **如果 funding 很高，但 spot-perp basis 在最近 `3 × 5m` 里还在持续扩大，就先不追；等 basis 停止继续拉大，再进 carry。**

原因很简单：
- funding 很可能已经被 premium 预支；
- 你若在 premium 扩张末端追进去，收的 funding 可能不够补 mark-to-market / 进出成本。

### 7.4 第一轮要看的不是 Sharpe，而是 funding/fee 比
核心报表先看：
- 总 funding 收入
- 总 fees
- `funding / fees`
- 交易次数
- 每次 funding event 的净收益分布
- 持仓占用时间占比
- 单次入场到下一次 funding 的 basis 回撤/扩张

因为这条线最容易死在：

> **方向没错，但净收益被费用和入场时机吃干净。**

## 8. 这轮最关键的“下一步怎么测”
1. **先把 repo baseline 和 extreme-only 拉开跑。**  
   不要把 `5/3` 和 `15/8` 混在一起讲“carry 行不行”；先确认问题到底出在 funding 本身，还是出在周转。

2. **把“全天持有”改成“围绕 funding boundary 的事件持有”。**  
   第一轮最值得测的是：结算前 `30/60/90 min` 建仓，结算后持有 `1` 个 funding 窗口，看看 net funding/fee 比是否明显改善。

3. **先只做 BTC / ETH。**  
   这条线的关键不在 universe 扩张，而在确认：高流动主币上极端 funding 尾部是否真的能留下稳定净收益。

4. **明确把 borrow / maker-taker / rebalance 算干净。**  
   这类策略最怕“paper 上收 funding，实盘里全吐给手续费和腿间偏差”。

5. **若 extreme-only 仍然太稀疏，再考虑跨 venue。**  
   单 venue 尾部 carry 若信号太少，第二阶段才值得去做 cross-venue funding ranking / fee-coverage routing；别一上来就把问题复杂化。

## 9. 为什么这轮仍值得进研究池
尽管 carry 家族最近已经有积累，但这篇仍值得收，因为它补的是一个很具体、也很实用的 desk lesson：

> **raw alpha 没错，但默认策略壳会把 raw alpha 跑死。**

这和“carry 不存在”完全是两回事。

对我们的素材池来说，它提供的不是又一个“正 funding 就收息”的老故事，而是一个更有用的命题：

> **在公开 funding 数据、完整策略壳和明确成本假设下，`positive funding carry` 只有在极端尾部 + 低周转执行里才更像可留下净值的 raw alpha。**

这正适合后面继续拆：
- boundary-time entry
- basis expansion veto
- cross-venue fee coverage
- maker-first execution
- event-level sizing

## 10. 资料与来源
1. **tomvdrslt (2026), _funding-rate-arbitrage-bot_.** GitHub repository.  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/tomvdrslt/funding-rate-arbitrage-bot>  
   - Repo URL: <https://github.com/tomvdrslt/funding-rate-arbitrage-bot.git>

2. **Repo metadata (GitHub API).**  
   - URL: <https://api.github.com/repos/tomvdrslt/funding-rate-arbitrage-bot>

3. **Repo strategy spec (`CLAUDE.md`).**  
   - Raw URL: <https://raw.githubusercontent.com/tomvdrslt/funding-rate-arbitrage-bot/master/CLAUDE.md>

4. **Repo config (`config/settings.py`).**  
   - Raw URL: <https://raw.githubusercontent.com/tomvdrslt/funding-rate-arbitrage-bot/master/config/settings.py>

5. **Repo signal logic (`src/strategy/funding_arb.py`).**  
   - Raw URL: <https://raw.githubusercontent.com/tomvdrslt/funding-rate-arbitrage-bot/master/src/strategy/funding_arb.py>

6. **Repo backtest (`scripts/backtest.py`).**  
   - Raw URL: <https://raw.githubusercontent.com/tomvdrslt/funding-rate-arbitrage-bot/master/scripts/backtest.py>

7. **Binance Open Platform, _Get Funding Rate History_.**  
   - Venue: Binance Open Platform  
   - DOI: N/A  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History>

## 11. 一句话结论
> **这条 raw alpha 不是“APR>5 就无脑开”的常开 carry，而更像“只做极端正 funding 尾部、围绕 funding boundary 低周转收息”的稀疏事件型 carry。默认状态机的真正敌人不是 funding 不够高，而是 fee churn。**
