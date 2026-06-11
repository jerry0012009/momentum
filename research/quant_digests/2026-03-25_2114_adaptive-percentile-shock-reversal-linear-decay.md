# 别把 repo 里的高 Sharpe 直接搬到 perp：这份 2026 新仓库更该先测的是「多 lookback 自适应阈值 shock-reversal + 线性衰减持仓」raw alpha
- 时间：2026-03-25 21:14 UTC
- 类型：2026 GitHub 新仓库（研究 notebook）+ 代码级 source audit + Binance Futures 公共 `15m/1h/4h` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**单币在多个短 lookback 上出现“超过自身历史分位阈值”的极端涨跌后，后续若存在部分回归，就可以把这些反向信号在多币篮子里聚合成 market-neutral shock-reversal 组合；`BTC regime gate / inverse-BTC-vol scaling` 只是 gate 与 sizing，不是 alpha 本体**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/time-series/shock-reversal/adaptive-percentile/multi-lookback/linear-decay/btc-regime-gate/inverse-vol/binance/perpetual/15m/1h/4h/repo
- 证据类型：仓库代码证据 + notebook 输出审计 + 本地公共数据快检

> 先回答 base alpha：**这不是 filter，不是“BTC 趋势门控”的包装。base alpha 本体是 thresholded time-series shock-reversal——先抓“这根/这几根涨跌已经超出自己常态”的币，再赌它短窗内部分回归。** 值得写它，是因为最近 intake 里 `pairs / residual / loser-basket / carry / trend` 已经不少，但还缺一张更朴素、可快速 first-verdict 的 **“自适应阈值极端波动回归”** 卡。

## 1. 这次看了什么
这次主看一个**今天刚创建**的新仓库：
- **`carlo855/StatArb-Crypto-Markets` (GitHub, created at `2026-03-25T15:30:54Z`)**

仓库 headline 写得很猛：
- description 直接写 **`2.07 Sharpe, 20% MDD, 31% annual return`**；
- README 说它在 **12h bars、~200 个 Binance USDT 对、3.5 年样本** 上，把 **mean reversion + momentum** 两条线组合成一个 market-neutral 组合；
- 但对当前 desk 来说，最值得单拎出来先测的，不是组合层，也不是 vol targeting，而是它的 **mean reversion 主体**：
  1. 多个短 lookback（如 `1/3/6/12`）并行看过去收益；
  2. 用**滚动绝对收益分位数**做自适应阈值，而不是写死 `x%`；
  3. 信号不是一下子开/关，而是**持有几根并线性衰减**；
  4. 最后才叠 `BTC SMA gate` 和 `inverse BTC vol scaling`。

换成人话：
- 它不是“今天跌了就抄底”；
- 而是“如果这次波动已经超过这枚币自己最近一段时间的常态，而且这种极端在多个短时钟都被看到，那就给一个会逐步衰减的反向仓位”。

这条线和最近几篇 `24h loser basket` 或 `high-RV loser bucket` 不完全一样。那些更像**横截面排序反转**；这篇更像**每个币先做 own-shock 检测，再把多个单币反转信号拼成组合**。

## 2. 一句话核心结论
- **一句话核心结论：** 这份新 repo 真正值得偷的，是“多 lookback 自适应阈值 shock-reversal + 线性衰减持仓”这条原始 alpha 骨架；但 repo headline 的高 Sharpe 目前不能直接信，且把它直接压到 `15m/1h` perp 上，当前样本先是明显负的。  
- **一句话它怎么证明：** 我一边审仓库 notebook 的存量输出与参数写法，一边把其中最可迁移的 mean-reversion 骨架翻成 Binance USDⓈ-M 公共 `15m/1h/4h` proxy，结果发现：**gate 只能减伤，不能救活；真正可继续研究的，是“更慢 formation clock + 更诚实 universe + 更强 friction audit”**。

## 3. 3 个最关键的数据点
1. **repo 自带结果很亮眼，但证据要降级。** notebook 存量输出里，`MR (OOS)` 竟然报到 **Sharpe `5.981`**，组合 `Combined (OOS)` 也报 **Sharpe `2.896`**；但 README 自己就明确写了 **survivorship bias 可能很重**，而 notebook 代码还把测试期硬写成 **`test_end = '2026-06-30'`**——这相对当前时间属于未来日期，所以这些 headline 结果现在不能当成 clean evidence。  
2. **把核心 MR 骨架直接翻到 Binance perp `15m`，毛边就已经不对。** 我用 `BTC + 9` 个大币候选、按 quote-volume 留下 **7 个高流动 alt perps**，在 **`11029` 根 `15m` bar（2025-12-01 ~ 2026-03-25）** 上跑 repo 风格的 `lookbacks=[1,3,6,12] + pctile=94 + hold=2`：  
   - **0 bps**：累计收益约 **`-30.83%`**，Sharpe 约 **`-3.06`**  
   - **2 bps**：累计收益约 **`-49.75%`**，Sharpe 约 **`-5.87`**  
   - **6 bps**：累计收益约 **`-73.49%`**，Sharpe 约 **`-11.44`**  
   这说明对我们最关心的短周期 perp，**当前直接 transfer 不是“有点薄”，而是方向上就先判负**。  
3. **gate 有帮助，但只是减伤；如果这条线有生命，更像在更慢时钟上。** 同一骨架下：  
   - 去掉 `BTC gate` 后，`15m / 2bps` 从 **`-49.75%`** 进一步恶化到 **`-65.23%`**；  
   - 但即便保留 gate，`1h` 也仍约 **`-45.01%` / Sharpe `-4.76`**；  
   - 到 **`4h`** 才缩窄到 **`-6.88%` / Sharpe `-0.46`**。  
   读法很明确：**`BTC gate` 更像 damage control，不是 alpha body；如果这条 shock-reversal 有可迁移性，也更可能在慢于 `15m/1h` 的 formation clock 上。**

## 4. 为什么它仍然值得进研究池
### 4.1 它服务的是哪类 raw alpha
- 分类：**time-series / cross-asset aggregated mean reversion raw alpha**
- 不是：
  - 纯横截面 loser/winner 排名
  - 纯 filter / regime overlay
  - 纯风险管理或资金费附属层

### 4.2 它补的是哪块缺口
最近 digest 里已经有很多：
- `24h loser basket reversal`
- `high-RV loser bucket`
- `beta-neutral residual MR`
- `pairs / dynamic factor / spread MR`
- `single-asset oversold / VWAP / envelope MR`

但还比较少一类更朴素、适合快速 first-verdict 的骨架：
- **不先做 pair selection；**
- **不先做横截面双排序；**
- 而是直接问：**“一枚币刚刚的波动，是否已经对它自己来说太极端？”**

这条线如果成立，后面能接很多我们已经在研究的二层组件：
- `BTC risk-on/off gate`
- vol throttle
- maker/taker execution split
- no-trade band
- market-neutral gross scaling

## 5. desk 化后的完整策略骨架
### 5.1 角色拆解（必填）
- 方向属性：market-neutral / short-horizon mean reversion
- 基础 alpha：多 lookback 自适应阈值下的 own-return shock reversal
- entry：
  - 对每个币算 `lb ∈ {1,3,6,12}` 的过去收益；
  - 若 `|ret_lb|` 超过该币滚动 `abs(ret_lb)` 的高分位阈值，就触发反向信号
- exit：
  - 默认不是一刀平，而是持有 `h` 根并**线性衰减**；
  - 或改成 `z-score 回落 / half-life 到期 / adverse extension stop`
- sizing：
  - 多个 lookback 信号平均；
  - 组合 gross 固定为 `1.0`；
  - 单名权重 cap
- filter / gate：
  - `BTC short SMA > BTC long SMA` 时才允许满配或开机
  - 极端高 BTC vol 时降杠杆
- risk / cost：
  - `2 / 4 / 6 / 10 bps` friction ladder
  - no-overlap path
  - 单名 participation cap

### 5.2 最小可执行版本
1. 选 `20~40` 个高流动 perp；
2. 对每个币独立算 own-return shock threshold；
3. 每 `15m` 或 `1h` 更新一次信号；
4. 对触发信号的币做反向仓位，并做 gross normalization；
5. 加 `BTC gate`、vol throttle、成本；
6. 看它是不是能从“很多小反转”里留下 net edge。

## 6. 本地最小快检：把 repo 的 MR 主体翻成 perp desk proxy，结果长什么样？
### 6.1 数据与口径
- 数据：Binance USDⓈ-M Futures 公共 K 线
- 样本：`2025-12-01 00:00 UTC ~ 2026-03-25 21:00 UTC`
- 候选宇宙：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT / XRPUSDT / DOGEUSDT / ADAUSDT / LINKUSDT / LTCUSDT / AVAXUSDT`
- 流动性过滤：按样本中位 `quote_volume` 取前 `80%`，实际留下 **7** 个高流动 alt perp
- repo proxy：
  - `lookbacks=[1,3,6,12]`
  - `pctile=94`
  - `pctile_window=180`
  - `hold_periods=2`
  - `BTC gate` 与 `inverse BTC vol scaling` 按 repo 风格保留

### 6.2 结论先说
**对 short-cycle perp desk，这条线当前最诚实的 verdict 不是“差一点就能上线”，而是“15m/1h direct transfer 先判负；若要继续，只值得往更慢 formation clock 与更干净 universe 审计去推”。**

### 6.3 为什么会这样
我觉得至少有 4 个可能原因：
1. **repo 的 headline 很可能被 universe 偏差放大。** README 已经承认 dead-coin / delisting survivorship 是 major issue。  
2. **12h research clock 不能机械压缩到 15m。** 一个在更慢时钟上看“是否过度反应”的信号，直接下钻到 15m，常会把噪音误当 edge。  
3. **当前 universe 太偏 majors。** 自适应 shock-reversal 若更依赖“更会过冲的小币”，在大币 perp 上本来就可能不够厚。  
4. **线性衰减持仓本身会带来较高持续换手。** 我这组快检里平均 turnover 约 **`0.324` gross / bar**，对 15m 来说已经不便宜。

## 7. 这条线现在该怎么放进研究池
我的判断：**值得保留，但必须降级 headline，升格 source audit。**

也就是：
- **该保留的不是 repo 报出来的高 Sharpe；**
- **该保留的是“adaptive threshold + multi-lookback + linear decay”这条 alpha skeleton。**

当前更诚实的标签应该是：
- `raw alpha skeleton / honest transfer failed on 15m-1h majors`
- 而不是：
- `已经可部署的短周期 perp alpha`

## 8. 下一步怎么测（必须）
1. **先做 point-in-time universe / dead-coin 审计。** 这是第一优先级，不解决它，repo headline 没有讨论价值。  
2. **把 formation clock 拉慢，再用快执行。** 更像该测：`4h or 12h shock detection → 15m execution / slicing`，而不是每根 `15m` 都重新估计。  
3. **把 long-loser 与 short-winner 分开。** 极端上涨后的继续逼空，常让 short 侧更脆；要先看是不是只有 `long oversold rebound` 那一腿还活着。  
4. **把 `BTC gate` 明确降级成 damage-control layer。** 下一轮应做 `raw alpha only`、`+BTC gate`、`+inv-vol` 三组 A/B，而不是再把 gate 写成 alpha 本体。  
5. **做 no-overlap portfolio path + friction ladder。** 至少跑 `2 / 4 / 6 / 10 bps`，并记录 `avg_turnover / participation / active_ratio`。  
6. **扩 universe，再做 liquidity split。** 当前只是 7 个高流动 perp；若 shock-reversal 只在 mid-liquidity bucket 才有边，就不该继续拿大币样本下结论。  
7. **和现有 reversal intake 做正交性检查。** 直接对比：
   - `24h loser basket`
   - `high-RV loser bucket`
   - `single-asset oversold bounce`
   看 adaptive-threshold shock-reversal 到底是不是新 edge，还是只是旧 reversal 的另一种写法。

## 9. 风险与保留意见
- 这是**新 repo**，不是成熟论文；方法清楚，但证据强度天然低于“论文 + 代码 + clean replication”三件套。  
- repo README 已明确提醒 survivorship bias；这一点不是小瑕疵，而是 headline 是否可信的核心。  
- notebook 测试期写到未来日期，这让存量输出更应视作 `stored result / weak evidence`。  
- 我这里的快检是 **desk transfer 审计**，不是 repo 精确复现；它能告诉我们“短周期 perp 上先别盲信”，但不能直接证明更慢时钟一定无效。  
- 如果后续做完 PIT universe、4h/12h formation、no-overlap 和 cost ladder 之后，结果仍然过不了 `2~4 bps`，这条线就该留在 research shelf，而不是继续占用复现预算。

## 10. 来源
1. **carlo855 (2026). _StatArb-Crypto-Markets_. GitHub repository.**  
   - Venue: GitHub repository  
   - DOI: 无  
   - Readable URL: `https://github.com/carlo855/StatArb-Crypto-Markets`  
   - Repo URL: `https://github.com/carlo855/StatArb-Crypto-Markets`  
   - Evidence note: repo metadata 显示创建时间 `2026-03-25T15:30:54Z`；description 直接写 `2.07 Sharpe, 20% MDD, 31% annual return ... on 12-hour bars`。  
2. **carlo855 (2026). _Statistical Arbitrage in Cryptocurrencies_ (Jupyter notebook in repo).**  
   - Readable URL: `https://github.com/carlo855/StatArb-Crypto-Markets/blob/main/Statistical%20Arbitrage%20in%20Cryptocurrencies.ipynb`  
   - Repo URL: `https://github.com/carlo855/StatArb-Crypto-Markets`  
   - Evidence note: notebook 代码包含 `mean_reversion_v3()`、stored outputs、以及 README 中提到的 survivorship-bias caveat；同时存在 `test_end='2026-06-30'` 这类当前不可 clean 复验的 future-date 设定。  
3. **Lehmann, B. N. (1990). _Fads, Martingales, and Market Efficiency_. Quarterly Journal of Economics, 105(1), 1–28.**  
   - Venue: QJE  
   - DOI: `10.2307/2937816`  
   - Readable URL: `https://doi.org/10.2307/2937816`  
   - Repo URL: 无  
   - 作用：提供“极端短期涨跌后存在 overreaction / reversal”这一类 alpha 母体。  
4. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 11. 本地产物
- `reports/artifacts/quant_digests/adaptive-percentile-xs-reversal_20260325_2109/summary.csv`
- `reports/artifacts/quant_digests/adaptive-percentile-xs-reversal_20260325_2109/frequency_compare.json`
- `reports/artifacts/quant_digests/adaptive-percentile-xs-reversal_20260325_2109/meta.json`

## 12. 一句话 verdict
**进研究池，但只按“adaptive-threshold shock-reversal 骨架”保留；repo headline 先降级，`15m/1h` perp 直接迁移当前先判负。**
