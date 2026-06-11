# 别把这份 2026 pairs repo 只读成“94% 胜率神话”：对 short-cycle crypto desk，更该先拆的是「1-week rolling OLS residual fade」，copula 只适合当可选 gate

- 时间：2026-04-26 00:28 UTC
- 类型：GitHub repo source audit（`README.md` + `Pair Trading final.py`）+ Binance USDⓈ-M public-data portability probe（`ETH/BNB`、`SOL/AVAX`、`LINK/UNI`、`ARB/OP`，`15m`）
- 主题类型：**raw alpha**
- 基础 alpha：**高相关 pair 的 rolling-OLS 残差若偏离到历史尾部，后续更容易发生 leader 回落 / laggard catch-up；repo 里的 copula 分支更适合当 conditional admission，而不是主 alpha 本体。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**是，但必须重做成本与 pair admission，不能照搬 README 胜率。**
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / rolling-ols / residual-zscore / copula / 15m / 5m / repo / public-data / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
这轮看的是 **Manan Rawat (2026)** 的 GitHub repo **`Crypto_pairs`**。repo 的表面卖点是“40 币、780 对、top-20 平均胜率 94.34%”；但真正对我们 desk 有价值的，不是这个 headline，而是它把策略拆成了两个层：
1. **主 alpha**：`1-week rolling OLS residual fade`
2. **旁支 gate**：用 copula 条件概率决定“这次 spread 偏离值不值得做”

作者自己的代码也说明了主次关系：可实际跑完、并给出 top pairs 的，是 rolling OLS + cointegration + spread mean reversion；copula 部分反而在 README 里明确承认 **RAM 开销过大、实时可用性不足**。

## 2. 一句话核心结论
**这份 repo 最值得 desk 拿走的，不是“copula 很高级”，而是一个更朴素也更能快速复现的 raw alpha 壳：`1-week rolling OLS residual z-score fade`；但它不是普适 alpha，更像只在少数强同主题 pair 上存在 pocket。**

## 3. 它是怎么证明这件事的
repo 先把 `40` 个币两两配对，做 `780` 组训练期筛选：
- 用 `60/40` train-test split；
- 对每对资产跑 rolling OLS，比较 `15min` 到 `1week` 不同窗口；
- spread 偏离均值 `1σ` 以上就入场，回到均值就平仓；
- 再按训练期 PnL 与 cointegration p-value 排 top pairs；
- 最后才把 copula 拿来做 conditional probability refinement。

repo 报告称：**`1-week` rolling window 一直最强**，top-20 平均 success rate 约 **94.34%**。但这更像“训练后挑出来的最优池”，不能直接当 short-cycle 可移植结论。

## 4. 为什么和当前项目有关
这条线跟当前 `momentum` 的关系很直接：
- 它补的是 **raw alpha 素材池**，不是纯 filter；
- 它属于 desk 现在需要持续补的 **pairs / stat-arb / relative-value** 分支；
- 它给了一个完整策略骨架：`admission -> entry -> exit -> pair selection -> optional gate`；
- 即便 copula 不实用，rolling OLS residual fade 本体依然可以独立进 first verdict。

## 4.5 这轮 portability 快检
我额外做了一个 Binance USDⓈ-M `15m` 快检，先不碰 repo 那个巨 universe，只看四组更像 desk 会真的交易的 liquid-ish pairs：`ETH/BNB`、`SOL/AVAX`、`LINK/UNI`、`ARB/OP`。

结果很像“**有 pocket，但不普适**”：
- 按 repo 最像的 **`1-week ≈ 672 根 15m bars`** lookback，若设 `|z|>1.5`、`max_hold=24 bars`，四组 pooled 共 **15 笔**，平均 gross 约 **+36.92 bps/笔**，按四腿 taker **16 bps** 粗扣后约 **+20.92 bps/笔**；
- 但这个 pooled 结果主要由 **`ARB/OP`** 拉动：同参数下它有 **6 笔**、平均 gross 约 **+127.57 bps/笔**；`LINK/UNI` 也有 **2 笔**、约 **+49.35 bps/笔**；
- 反过来，若把 `ARB/OP` 去掉，剩余三组平均 gross 只剩约 **+6.70 bps/笔**，粗扣成本后约 **-9.30 bps/笔**；说明这不是“拿任何高相关大币 pair 都能跑”的通用模板。

所以更诚实的 desk 读法是：**raw alpha 本体存在，但默认要先做 pair admission，再谈 copula gate；不要反过来把 copula 当主角。**

## 5. 策略拆解（必填）
- 方向属性：相对价值 / pairs / 均值回复
- 基础 alpha：rolling OLS 残差极端偏离后的 spread 回归
- regime：同主题、强相关、叙事同步但短时错位的 pairs 更友好；相关性断裂时失效
- filter / veto：cointegration / rolling correlation / event blackout；copula 只适合做二层 conditional gate
- risk / sizing / execution overlay：双腿总成本预算、max-hold、残差继续扩张止损、pair concentration cap

## 6. 可复刻的最小实验
### 最小实验 A：先测 raw alpha 本体
- 标的：`ARB/OP`、`LINK/UNI`、`SOL/AVAX`、`ETH/BNB`
- 周期：`15m` 主实验，`5m` 子执行
- 定义：rolling OLS 残差 z-score；`|z|>1.5/2.0` 入场，`z` 回到 `0` 或 `max_hold=12/24/48` 出场
- 先看：`net bps/trade`、`trade count`、`pair dispersion`

### 最小实验 B：再测 copula 值不值得当 gate
- 不先让 copula 直接决定方向；
- 只在 raw alpha 已触发后，再问：copula conditional probability 极端时，后续 `net bps/trade` 是否更高、左尾是否更短。

## 7. 风险与保留意见
1. **README 的 94% 胜率不可直接信**：那是训练后 top-pair 展示，不是成本后、全池、实时 admission 的真实可交易胜率。
2. **样本选择偏差明显**：repo 先找最优窗口、再排最优 pair，本来就容易把“局部好看”放大。
3. **copula 分支工程成本高**：作者自己都写了 RAM 问题，所以它更像研究旁支，不该抢 raw alpha 主位。
4. **short-cycle 成本约束很硬**：双腿开平总共有四个 one-way trade，若单边成本上到 `4bps+`，很多普通 pocket 会被直接吃掉。

## 8. 我对这条线的判断
这轮最值得保留到研究池里的，不是“copula pairs trading”这个大词，而是更窄、更诚实的一句：

> **先把 `1-week rolling OLS residual fade` 当 raw alpha 壳来测；若它只在少数 pair 上活着，就把 copula、funding、OI、事件黑名单都放到二层 admission，而不是一上来就迷信高维 dependence 建模。**

这对当前 desk 是有用的，因为它直接补的是：
- `pairs / stat-arb` 的可复现 alpha 壳；
- `raw alpha -> pair admission -> optional nonlinear gate` 的研究顺序；
- 一个适合快速做 `15m -> 5m child execution` 的最小实验入口。

## 9. 文件与页面
- 研究笔记：`research/quant_digests/2026-04-26_0028_oneweek-ols-pairfade-copulagate.md`
- Probe artifact：`reports/artifacts/quant_digests/2026-04-26_pairs_repo_oneweek_ols_probe_summary.csv`
- Probe trades：`reports/artifacts/quant_digests/2026-04-26_pairs_repo_oneweek_ols_probe_trades.csv`
- 预期页面（发布后）：<https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-26_0028_oneweek-ols-pairfade-copulagate.html>
- 索引页：<https://jp.jerrypsy.top/momentum/reading/quant_digests/report.html>

## 10. 来源
1. **Manan Rawat. (2026). _Crypto_pairs_. GitHub.**
   - Repo URL: <https://github.com/Manan-Rawat/Crypto_pairs>
   - README: <https://raw.githubusercontent.com/Manan-Rawat/Crypto_pairs/main/README.md>
   - Strategy code: <https://raw.githubusercontent.com/Manan-Rawat/Crypto_pairs/main/Pair%20Trading%20final.py>

2. **Binance USDⓈ-M Futures public klines**
   - API docs: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
   - This digest portability probe used recent `15m` public klines for `ETHUSDT / BNBUSDT / SOLUSDT / AVAXUSDT / LINKUSDT / UNIUSDT / ARBUSDT / OPUSDT`.
