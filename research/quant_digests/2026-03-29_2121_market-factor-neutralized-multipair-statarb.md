# 别把 pairs 只做单 pair z-score：这篇 2021 开放获取论文更该先测的是「market-factor neutralized multi-pair stat-arb」完整 raw alpha 骨架
- 时间：2026-03-29 21:21 UTC
- 类型：2021 开放获取论文全文
- 主题类型：raw alpha
- 基础 alpha：**先用共同市场因子把多币价格里的“同涨同跌”剥掉，再对剩下的 stationary 因子做多空排序；本体不是 filter，而是一个可直接交易的 basket relative-value / stat-arb alpha。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/dynamic-factor/cointegration/stationary-factor/market-neutral/multi-pair/5m/15m/paper
- 证据类型：论文全文

> 先回答 base alpha：**这是 raw alpha，不是单纯 filter。** 真正赚钱的底层不是“stationary 因子这个名词”，而是 **把共同市场因子剥离后，对剩余相对价格错位做 market-neutral 多空回归**；regime gate 只是附加条件，用来判定这套 raw alpha 何时该关机。

## 1. 这次看了什么
这次主看 **Gianna Figá-Talamanca, Sergio Focardi, Marco Patacca (2021)** 的开放获取论文 **_Common dynamic factors for cryptocurrencies and multiple pair-trading statistical arbitrages_**（*Decisions in Economics and Finance*）。它研究 `BTC / ETH / LTC / XMR` 在 `2016-01` 到 `2019-11` 的联合价格结构，不是只做单个 pair spread，而是先估一个两因子动态模型：
- `f1` = 共同市场因子（近似 BTC 主导的 integrated factor）
- `f2` = 站在共同因子之外、仍可预测的 stationary factor

最值钱的可复用点有两个：
1. **价格先按 `β_i1` 缩放**，让共同市场因子在 pair spread 里相互抵消；
2. **不是只盯一个 pair**，而是把下一期的 scaled forecast price 排序，直接做一个 top-half short / bottom-half long 的多对冲 market-neutral book。

## 2. 核心结论
- **一句话核心结论：** 对 short-cycle desk 来说，这篇 paper 最值得拿走的不是“动态因子模型”四个字，而是 **“先剥离市场共振，再做 basket 内部相对价值排序”** 这条完整 raw alpha 骨架。
- **一句话它怎么证明：** 作者在滚动三年估计窗 + 2019 日频测试窗里，直接把 `entry / no-trade threshold / regime gate / fee` 全写出来，并展示这套 market-neutral 策略只在第二因子仍 stationary 时赚钱，失效后应主动停机。

更具体地说：
1. **四个币的联合价格并不只是“一根共同趋势线”。** Johansen 检验给出 **3 个 cointegrating vectors**，意味着样本里至少存在 **1 个共同 integrated factor**；继续做动态因子分解后，作者找到 **2 个关键因子**，其中第一因子近似 BTC 主导，第二因子在 `2019-08` 前仍是可交易的 stationary 偏离。
2. **真正的交易边不是单个 spread 名字，而是“共同因子中和后的相对错位”。** 论文把价格写成 `p_i = α_i + β_i1 f1 + β_i2 f2 + ε_i`，再除以 `β_i1`，这样任意 pair 的 scaled spread 主要只剩 `f2` 驱动；这一步很适合 desk 化，因为它天然把“全市场一起抽风”从信号里拆出去。
3. **regime gate 不是锦上添花，而是生死线。** 作者发现 `2019-08-20` 后第二因子不再 stationary，且两个因子相关性升高，于是 `2019-09` 后基本不再交易。也就是说，这篇 paper 的真正含义不是“alpha 永远存在”，而是 **“当共同因子 + 站稳因子这组结构成立时，basket stat-arb 可以开；结构塌了就该关。”**

## 3. 3 个关键数据点
1. **模型参数本身很有辨识度。** 在 `2016-01` 到 `2018-12` 的估计窗里，作者得到：`λ1 = 0.9962`（ADF `p=0.27124`，接近 unit root）、`λ2 = 0.9823`（ADF `p=0.00564`，可视作 stationary），而两因子相关性约 **`0.005`**。这说明“市场主趋势”和“可回归偏离”在那段时期是能分开的。
2. **loadings 明确告诉我们共振腿是谁。** 第一因子对 BTC 的加载 **`β11 = 0.9911`**，几乎就是市场共振腿；第二因子对 ETH 的加载最强，**`β22 = 5.2255`**。对 desk 来说，这很像在告诉我们：**先识别共同 beta 腿，再看谁在共同 beta 之外偏得最多。**
3. **阈值交易确实能改善成本后结果。** 2019 测试窗共 `334` 天；若完全不设阈值（`c=0`），交易 **252** 次，扣 `0.10%` 费用后的净累计收益均值约 **`3031.17`**；设 `c=0.20` 时交易降到 **222** 次，但净累计收益均值略升到 **`3032.97`**。结论不是“`0.20` 神奇最优”，而是：**这种 raw alpha 天生怕换手，必须把 no-trade band 当正式组件来测。**

## 4. 为什么和当前项目有关
当前 desk 最近已经补了不少：
- 单 pair spread
- copula / cointegration / matching
- cross-sectional momentum
- options / funding / synthetic-forward relative value

但还相对少一个素材：
> **不是“挑哪一对”而已，而是“怎么把整个 basket 先做 market-mode neutralization，再统一做相对价值排序”。**

这篇 paper 的价值就在这里：
- 它属于 **raw alpha 池扩容**，不是纯解释型综述；
- 它能直接服务 `1m / 3m / 5m / 15m` 的 **basket stat-arb / relative-value** 主线；
- 它把 `entry / veto / threshold / cost` 写得足够清楚，适合先做最小实验，再决定要不要继续升级成更复杂的 PCA / Kalman / VECM 版本。

## 3.5 策略拆解（必填）
- 方向属性：**相对价值 / stat-arb / market-neutral**
- 基础 alpha：**共同市场因子中和后，stationary 因子驱动的 basket 内部相对错位回归**
- regime：**只在“1 个 integrated factor + 1 个 stationary factor”成立，且两因子低相关时开机**
- filter / veto：**`corr(f1,f2)` 不得过高；第二因子 ADF 不通过时停机；可再加 no-trade threshold `c·σ_v`**
- risk / sizing / execution overlay：**按 `β_i1` 做 scale / hedge；top-half short、bottom-half long；测试 `c=0/0.1/0.2` 的 band；显式计入 maker/taker 成本**

## 5. 可复刻的最小实验
**研究假设：** 在 Binance 永续大市值宇宙里，若先剥离共同市场因子，再对剩余 stationary 偏离做 basket 排序，多空 book 会比“直接按原始收益排序”更像可持续的 relative-value raw alpha。

**一个可计算定义：**
1. 宇宙：`BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LTC` 等流动性最高 perp；
2. 周期：先跑 `15m`，再向 `5m` 和 `1h` 做稳健性对照；
3. 形成窗：`45d~60d` 滚动；
4. 在形成窗里对 log-price 做两因子分解（最小版可先用 `PCA + AR(1)` 近似论文里的 dynamic factor）；
5. 用第一因子 loading 做缩放，得到 scaled prices；
6. 估计下一期 `scaled forecast price`，每根 bar 把宇宙分成 top-half / bottom-half；
7. 仅在 **第二因子 ADF `p<0.05` 且因子相关性低于阈值** 时开仓；
8. `entry`: `|g_{t+1} - v_t| > c·σ_v`；先测 `c ∈ {0, 0.1, 0.2}`；
9. `exit`: 先做 **下一根平仓**、`4 bar`、`16 bar` 三档；
10. 先看两项指标：**成本后 pnl / turnover**，再看 **positive-window ratio**。

> **最该先测的 desk 版本：** `Binance perp 15m` + `60d formation` + `PCA market mode neutralization` + `ADF/corr gate` + `c=0/0.1/0.2`。如果这版连 gross 都站不住，就别急着上更复杂 Kalman；如果 gross 活、净后死，再重点修 no-trade band 和持有期，而不是先堆模型。

## 6. 风险与保留意见
- **样本偏老且偏小。** 论文只看 `4` 个币、日频、`2016-2019`，对今天 perp 市场肯定不是直接照搬；
- **没有官方公开策略仓库。** 这意味着实现细节需要自己补；
- **动态因子在短周期上可能更不稳定。** `1m/3m/5m` 很容易把微观结构噪音也当成“第二因子”；
- **stationarity gate 可能比 alpha 本体更重要。** 若 rolling ADF 一直不稳，这条线更适合作为 `15m/1h` 的中速 stat-arb，而不是超短高速信号；
- **成本是第一约束。** 论文在 `0.10%` fee 下还能保住净收益，但 short-cycle perp 若 taker 占比高，结果会迅速塌掉。

## 7. 下一步怎么测
1. **先做 `PCA 近似版`，别一上来追求完整 Bayesian dynamic factor。** 先验证“market-factor neutralization + basket ranking”这个 raw alpha 核心是否有 transfer。  
2. **把 gate 当主组件，不要当附属过滤器。** 每个 formation window 都记录：第二因子 ADF、因子相关性、交易开机率。  
3. **把持有期展开。** 这条线不一定是 `next-bar` alpha；至少拆 `1 / 4 / 16` bars 三档。  
4. **显式比较三种 baseline：** 原始收益排序、beta-neutralized 排序、beta-neutralized + gate 排序。  
5. **费用要分层。** 至少跑 `2/4/6 bps` 和 `6/10/14 bps` 两组 round-trip 场景。  
6. **若 15m 能活，再往 5m 缩；若 15m 已明显不稳，就把它留在中速 stat-arb 池，不要硬塞成 1m。**

## 8. 文件与产物
- 研究笔记：`research/quant_digests/2026-03-29_2121_market-factor-neutralized-multipair-statarb.md`

## Sources
1. **Figá-Talamanca, G., Focardi, S., & Patacca, M. (2021). _Common dynamic factors for cryptocurrencies and multiple pair-trading statistical arbitrages_. Decisions in Economics and Finance.**  
   - DOI: `10.1007/s10203-021-00318-x`  
   - DOI URL: `https://doi.org/10.1007/s10203-021-00318-x`  
   - Readable URL: `https://link.springer.com/article/10.1007/s10203-021-00318-x`  
   - PDF URL: `https://link.springer.com/content/pdf/10.1007/s10203-021-00318-x.pdf`  
   - Repo URL: `未找到论文官方策略仓库（截至 2026-03-29）`
2. **CoinMarketCap**（论文样本选择说明中引用）  
   - URL: `https://coinmarketcap.com/`
