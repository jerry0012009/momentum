# 别把这个 2024 toy stat-arb repo 继续当 portfolio optimizer：它唯一还值得救的，其实是「BTC/ETH spread MR × momentum veto」raw alpha
- 时间：2026-03-30 20:05 UTC
- 类型：2024 GitHub repo 源码审阅 + Binance Futures 公共 `15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：BTC/ETH 相对价格偏离（beta-neutral spread z-score）在短窗内回归；但若 spread 仍在同方向加速，则用 momentum veto 跳过入场
- 是否可独立复现：是（repo 原样并不完整，但核心思路可用公开数据 clean-room 重写）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前 `15m` 口径下只有 gross edge，轻微成本后即转负）
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/btc/eth/beta-neutral/spread-zscore/momentum-veto/cost-cliff/binance/perpetual/15m/5m/repo/public-data
- 证据类型：repo 源码 + 本地最小快检

## 1) 这次看了什么
先回答 base alpha：**这条东西的 base alpha 是 BTC/ETH relative-value spread 的短窗均值回归，不是 portfolio optimization，也不是“两个币各做各的方向预测”。**

我这次主看的是 `notaconduit/Statistical-Arbitrage-in-Cryptocurrencies` 这份 2024 更新的公开 repo。它表面上写的是“stat arb + mean reversion + portfolio optimization”，但源码层真正能为我们 desk 提供价值的，不是 README 里的大词，而是一个更小、更诚实的旁支想法：
- 用 **mean reversion** 提供 spread 回归方向；
- 用 **momentum** 不去追方向，而是当 **entry veto**；
- 把这件事压成我们能在 `15m` 上很快复现的 **BTC/ETH beta-neutral spread trade**。

更直白地说：**别照抄 repo 那个“把 BTC/ETH 各自的 mean-reversion 和 momentum 平均起来”的写法；真正值得做最小实验的，是把它翻译成“spread MR × momentum veto”的完整 pairs raw alpha。**

## 2) 核心结论
- **一句话核心结论：** 这条 `BTC/ETH spread MR × momentum veto` 在当前 `15m` 口径下 **有一点 gross edge，但净边极薄，轻微成本就会被打穿**；因此它更适合当 `keep-as-control / reject-for-now` 的 raw-alpha 对照卡，而不是马上升优先级。  
- **一句话证明方式：** 我把 repo 的 `mean_reversion + momentum` 思路改写成 `BTC/ETH` 的 beta-neutral spread z-score 策略，在 Binance Futures 公共 `15m` 数据上做 120 天快检，gross 为正，但从极轻微成本开始就转负。

3 个关键数据点（本地快检）：
1. **带 momentum veto 的 baseline**：近 `120d`、`15m`、`entry |z|>2.0`、`exit |z|<0.5`、`max_hold=8 bars`，**gross `+0.58%`，Sharpe `0.57`，MDD `-1.08%`**。  
2. **成本非常敏感**：同一 baseline 只要加入 `cost_per_turn=0.0001`，结果就变成 **`-0.66%`，Sharpe `-0.66`**；若到 `0.0003`，则是 **`-3.10%`，Sharpe `-3.08`**。  
3. **veto 确实有用，但不够救命**：在 `cost_per_turn=0.0003` 下，不加 veto 时样本内 **322 笔**入场、总回报 **`-16.66%`**；加 veto 后只剩 **62 笔**入场，亏损缩到 **`-3.10%`**，说明 veto 主要作用是压换手与回撤，而不是把薄 edge 变成厚 edge。

## 3) 为什么和当前 desk 直接相关
这不是 filter/overlay 伪装成 alpha；它本身就是一条完整的 **raw alpha**：
- 机理上属于 **relative value / pairs / stat-arb / mean reversion**；
- 能直接拆成 `entry / exit / sizing / risk / cost`；
- 并且特别适合做 `15m → 5m` 的快速 survival check。

更重要的是，它满足这轮用户给的“灵活读法”：
- repo 本体其实写得很玩具，甚至带明显不完整处；
- 但里面 **“mean reversion 负责方向、momentum 负责否决”** 这个旁支，反而比 repo headline 更适合我们 desk；
- 所以这轮不是“照抄 repo 主标题”，而是**从 repo 里拎出真正可做最小实验的 raw alpha 核心**。

## 3.5) 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative-value / market-neutral / mean-reversion
- 基础 alpha：BTC/ETH beta-neutral spread 偏离会在短窗内回归；但若 spread 还在沿入场方向加速，则胜率下降
- entry：
  - 先用 rolling beta 构造 `spread = log(ETH) - beta * log(BTC)`；
  - 对 spread 做 rolling z-score；
  - `z > +2` 做 **short spread**（short ETH / long BTC）；
  - `z < -2` 做 **long spread**（long ETH / short BTC）；
  - 若 spread 最近 `8 bars` 动量仍沿入场方向加速，则 **跳过这次入场**。
- exit：`|z|` 回到 `0.5` 内，或持仓达到 `8 bars` 强平退出
- sizing：按 rolling beta 做 gross-normalized hedge，控制两腿合计 gross ≈ 1
- risk / veto：momentum veto、最大持有时长、beta 失真时不交易、后续可加 funding diff / 波动阈值 / session filter
- cost：显式按每次换仓 gross 变化扣减；本次做了 `0 / 0.0001 / 0.0002 / 0.0003` 四档敏感性

## 4) Repo 层最关键的诚实判断
### 4.1 这份 repo 最大的问题：它不是一个可直接复现的完整实现
源码里至少有三处明显问题：
1. `main.py` 调用了 `data.get_prices()` 与 `portfolio.get_positions()`，但 repo 当前公开文件里并没有对应可运行定义；
2. `portfolio.py` 原始文件本身是不完整的，代码在函数内部就截断了；
3. 所谓 “portfolio optimization” 与 “stat arb” 的关系在实现上并没真正闭环，更像教学型 scaffold。

所以这份 repo **不能当成 production-ready skeleton**。

### 4.2 但它仍有 intake 价值
真正有价值的是它暴露了一个简单但可测试的问题：
- **如果 mean reversion 要做 short-cycle pairs，momentum 更像确认/否决层，而不是并行加权主信号。**

这正是本次 digest 想留下的点。

## 5) 可复刻最小实验（15m 起步）
- 数据源：Binance Futures public kline REST
- 公开性：公开可得，无需 API key
- 更新频率：`1m/3m/5m/15m` 都可直接拉
- 本次最小口径：
  - 标的：`BTCUSDT`、`ETHUSDT`
  - 周期：`15m`
  - 样本：近 `120d`
  - beta 窗口：`96 bars`
  - z-score 窗口：`96 bars`
  - entry / exit：`|z| > 2.0` 入场，`|z| < 0.5` 离场
  - max hold：`8 bars`
  - veto：spread 最近 `8 bars` 若仍沿入场方向加速，则跳过
- 首看指标：`return / Sharpe / MDD / trades / cost sensitivity`

## 6) 下一步怎么测（直接可执行）
1. **先下钻到 `5m`，但别直接照搬参数**：把 `beta/zscore/lookback/hold` 统一按“自然时间”而不是 bar 数重标，验证 veto 是否还能压换手。  
2. **补 funding diff**：这条策略若跑在 perp 上，下一步必须测 `ETH funding - beta*BTC funding` 是否会把本来就很薄的 gross edge 吃掉，或反而提供额外 carry。  
3. **做 session pocket**：只在 `UTC 13:00–17:00` 与 `20:00–24:00` 这种 liquidity 更厚的时段启用，看成本后是否能留下正 pocket。  
4. **把 veto 从“spread 过去 8 bar 动量”升级成两层 gate**：`spread momentum veto + realized vol ceiling`，避免在单边扩散 regime 里一直逆势接刀。  
5. **做 control-card 对照**：和已有 `cointegration spread × beta-consistent sizing`、`fixed-threshold pairs MR` 卡片并排，确认这条线是否只是另一个“gross 微正、净值不过线”的近亲。

## 7) 风险与保留意见
- 这份 repo 的实现质量偏低，**不能把它当源码级证据的正样本**；
- 当前正边只存在于 gross，说明它更像 **execution-sensitive control card**，不是 ready-to-promote 候选；
- 本次快检只用了 price spread，没有把 funding、手续费层级、maker/taker 混合成交显式建进去；
- 若换成更长样本或更精细执行，也许能留出 pocket，但那已经属于下一轮验证，而不是本轮结论。

## 8) 来源
1. **notaconduit (updated 2024-08-25). _Statistical-Arbitrage-in-Cryptocurrencies_. GitHub repository.**  
   - Repo URL: https://github.com/notaconduit/Statistical-Arbitrage-in-Cryptocurrencies
2. **Repo source files inspected directly**  
   - README: https://raw.githubusercontent.com/notaconduit/Statistical-Arbitrage-in-Cryptocurrencies/master/README.md  
   - main.py: https://raw.githubusercontent.com/notaconduit/Statistical-Arbitrage-in-Cryptocurrencies/master/main.py  
   - trading.py: https://raw.githubusercontent.com/notaconduit/Statistical-Arbitrage-in-Cryptocurrencies/master/trading.py  
   - portfolio.py: https://raw.githubusercontent.com/notaconduit/Statistical-Arbitrage-in-Cryptocurrencies/master/portfolio.py
3. **CoinGecko API Docs**（repo 声称的数据来源）  
   - https://docs.coingecko.com/reference/introduction
4. **Binance USDⓈ-M Futures Kline API Docs**（本次最小快检使用）  
   - https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 9) 本地产物
- `reports/artifacts/quant_digests/btc_eth_pair_repo_probe_20260330/summary.json`
- `reports/artifacts/quant_digests/btc_eth_pair_repo_probe_20260330/cost_sensitivity.csv`
- `reports/artifacts/quant_digests/btc_eth_pair_repo_probe_20260330/prices_15m.csv`
