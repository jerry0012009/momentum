# 别把 PCA stat-arb 只读成“降维作业”：对 short-cycle crypto desk，更该先拆的是「PCA common-factor residual overextension × zero-cross fade」这条 raw alpha
- 时间：2026-04-21 21:20 UTC
- 类型：2026 GitHub repo source audit（`README.txt` + `src/pca_engine.py` + `src/s_score.py` + `src/strategy.py` + `src/backtester.py`）+ Binance USDⓈ-M public-data portability probe（8 liquid majors，`15m/5m`）
- 主题类型：raw alpha
- 基础 alpha：用 rolling PCA 抽出 crypto 横截面的共同因子，把每个币对共同因子的解释部分剥掉；当某个币的 idiosyncratic residual 短期极端偏离时，做 **residual mean reversion fade**：残差过低做多、残差过高做空，等 z-score 回到中性区或超时退出
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / relative-value / stat-arb / PCA / eigenportfolio / residual / OU / mean-reversion / zero-cross / Binance perpetual / 15m / 5m / repo / public-data / cost
- 证据类型：repo 工程骨架 + 经典论文地基 + public-data first probe

## 1. 这次看了什么
这轮主来源是一个 2026 更新的 GitHub 研究仓：**sophie-lan / crypto-pca-statarb**。repo 描述很直接：把 **Avellaneda & Lee (2010)** 的 PCA statistical arbitrage 框架搬到 crypto assets 上，流程包括：

1. rolling PCA factor construction；
2. regression residual extraction；
3. OU parameter estimation；
4. s-score generation；
5. rule-based trading and backtesting。

一句话先回答本轮选题门槛：

> **这篇东西的 base alpha 是什么？**
>
> **答：是 PCA common-factor residual mean reversion。**
>
> 翻成人话：先把“大家一起涨跌”的横截面共同因子拿掉，再交易某个币相对共同因子的短期过冲回归。

这不是 filter，也不是 regime gate。PCA 只是去噪和中性化工具，真正的 raw alpha 是：**残差偏离后回归**。

### 来源
- **Repo**：sophie-lan (2026), *crypto-pca-statarb*
- **Repo URL**：<https://github.com/sophie-lan/crypto-pca-statarb>
- **Readable URL**：<https://github.com/sophie-lan/crypto-pca-statarb/blob/main/README.txt>
- **关键代码**：
  - `src/pca_engine.py`
  - `src/residual_model.py`
  - `src/ou_estimator.py`
  - `src/s_score.py`
  - `src/strategy.py`
  - `src/backtester.py`
- **经典地基**：Avellaneda, M. and Lee, J.-H. (2010), *Statistical Arbitrage in the U.S. Equities Market*, Quantitative Finance. DOI: `10.1080/14697680903124632`

## 2. repo 里真正可交易的壳是什么
repo 的结构很适合 desk intake，因为它不是只给一个“相关性热力图”，而是把 stat-arb 完整链条拆出来了：

### 2.1 factor construction
`src/pca_engine.py` 的默认参数：
- rolling PCA window：`240` 小时；
- universe：top-40 token；
- 对 log return 做标准化；
- 用相关矩阵提取前两个 PC；
- 用 eigenvector / volatility 形成 eigenportfolio；
- 生成 `F1/F2` factor returns。

这一步的作用不是预测，而是回答：

> 当前横截面里，最主要的共同涨跌方向是什么？

### 2.2 residual + OU + s-score
repo README 写明：先做 regression-based residual extraction，再估计 OU 参数，再生成 s-score。`src/s_score.py` 里把 residual 累计成 `X_t`，再用：

```text
s = (X_t - m) / sigma_eq
```

其中 `m` 是 OU 均值，`sigma_eq` 是均衡标准差。

人话就是：
- 残差不看单根噪音，而看累计偏离；
- 偏离越远，越像“短期 idiosyncratic dislocation”；
- 用 OU 均值回复框架把它变成可交易的 z-score。

### 2.3 entry / exit rule
`src/strategy.py` 的默认阈值很清楚：
- `s <= -1.25`：buy open；
- `s >= +1.25`：sell open；
- long 到 `s >= -0.75` 平；
- short 到 `s <= +1.0` 平；
- 每个 token 固定 `trade_size = 1.0`。

如果翻成 desk 版本：
- **entry**：残差 z-score 极低，long；残差 z-score 极高，short；
- **exit**：残差回到中性附近就走；
- **sizing**：最小版本等权 / capped notional；后续可用 residual strength + volatility 做缩放；
- **risk**：PCA 已经先去共同因子，但还要补单币上限、流动性门槛、成本 ladder；
- **cost**：repo 明确说 transaction costs and slippage are not modelled，这正是我们 first probe 必须补的地方。

## 3. 为什么这条壳和最近 digest 不算重复
最近已经写过不少 stat-arb / pairs / residual 类主题，但这轮有一个明确新增量：

### 3.1 它不是固定 pair，也不是只对 BTC residualize
- cointegration / pairs：通常先选一对币，交易 pair spread；
- BTC residualization：通常只剥掉 BTC 一个 anchor；
- **PCA residual**：每一轮都从整个 universe 里抽 common factors，允许共同因子随市场结构变化。

对 crypto 短周期，这一点有意义：有些时段是 BTC 领涨领跌，有些时段是 SOL / meme / AI / L2 主题带动。固定 BTC anchor 可能漏掉主题 beta，而 PCA 更像自动提取“当前市场最主要的共振方向”。

### 3.2 它补的是 raw alpha 素材池里的 cross-sectional RV 线
这条不是 breakout / trend / OI confluence / market-making execution 壳，而是明确补：
- mean reversion；
- cross-sectional relative value；
- stat-arb；
- residual alpha。

这正好符合当前 bot7 的 intake 目标：不要只在单币技术形态里内循环。

## 4. repo 的不足：别直接照搬原始回测
repo 自己也写得很诚实：

> Transaction costs and slippage are not modelled. All backtest results assume zero fees and perfect execution at hourly close prices.

所以这份 repo 对我们最有价值的不是它的图，而是工程骨架：
- PCA factor / eigenportfolio 怎么算；
- residual 怎么转成 OU / s-score；
- signal threshold 怎么写成可复现规则；
- backtester 至少做了 next-period position shift，避免最粗的 lookahead。

但对于 `5m/15m` crypto，原始版本必须先过三关：
1. 成本；
2. turnover；
3. universe stability。

## 5. 我们自己的 `15m/5m` public-data first probe
### 5.1 probe 口径
我用 Binance USDⓈ-M public klines 做了一个轻量迁移实验，目标不是宣称已经复刻 repo，而是先回答：**这条 residual fade 壳在 `15m/5m` 上有没有 gross 边，扣粗成本后离可交易差多远？**

- 市场：Binance USDⓈ-M perpetual
- universe：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`
- 周期：`15m` 与 `5m`
- `15m` 参数：
  - PCA window：`96` bars（约 1 天）
  - regression window：`72` bars
  - residual z-score window：`192` bars
  - entry：`|z| >= 2.0`
  - exit：回到 `|z| <= 0.5` 或最多持有 `8` 根
- `5m` 参数：
  - PCA window：`144` bars（约 12 小时）
  - regression window：`120` bars
  - residual z-score window：`288` bars
  - entry：`|z| >= 2.2`
  - exit：回到 `|z| <= 0.5` 或最多持有 `12` 根
- execution：下一根用持仓收益粗近似，top-1 long + top-1 short admission；
- cost：每笔 round trip 粗扣 `8 bps`。

产物：
- `reports/artifacts/quant_digests/pca_statarb_probe_summary_2026-04-21.csv`
- `reports/artifacts/quant_digests/pca_statarb_probe_detail_2026-04-21.csv`

### 5.2 结果
核心数字：

| interval | bars | trade_count | gross_mean_bps/bar | gross_cum_pct | gross_sharpe | gross_bps/trade | rough_net_bps/trade | win_rate | avg_hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `15m` | `1656` | `580` | `+0.827` | `+14.49%` | `10.997` | `+2.28` | `-5.72` | `57.24%` | `1.38` bars |
| `5m` | `1984` | `494` | `+0.183` | `+3.63%` | `7.674` | `+1.07` | `-6.93` | `53.64%` | `1.45` bars |

### 5.3 first verdict
这轮 first probe 的结论很清楚：

- **有 gross alpha 迹象**：`15m` 与 `5m` 的 gross 都是正的，且 win rate 略高于 50%；
- **但原始 entry/exit 太急，单笔边太薄**：平均持仓只有约 `1.4` 根 bar，粗扣 `8 bps` 后每笔明显负；
- **更适合作为 admission / selector 的父信号，而不是直接 market-order 高频进出**。

所以本轮不应该把它判成“可直接 naked 上线”。更准确的 intake 是：

> **PCA residual overextension 是一条值得保留的 raw alpha 候选；但要进入实盘候选池，必须先把 exit 改慢、提高 entry band、加 maker-first / batch rebalance 来降低 turnover。**

## 6. 这条 alpha 的第一性逻辑
这条壳能成立，不靠神秘模型，靠三件事：

1. crypto 横截面里大部分短期波动是共同因子：BTC beta、sector beta、risk-on/off；
2. 如果某个币剥掉共同因子后仍然极端偏离，很多时候是 idiosyncratic order-flow / liquidity shock；
3. 这种 idiosyncratic shock 比 market-wide shock 更容易短期均值回复。

换句话说，这条 alpha 不是“币跌多了就买”。它是：

> **在整个市场共同波动解释不了的部分里，找最极端的短期偏离。**

这比普通 RSI / BB touch 更像 stat-arb，也更适合和已有 single-asset alpha 做组合。

## 7. 策略拆解（按 desk 可落地口径）
### 7.1 entry
每个 `15m` 父信号点：
1. 用最近 `1~3` 天的 `15m` returns 做 rolling PCA；
2. 提取前 `1~3` 个 common factors；
3. 对每个币回归自身收益到 common factors；
4. 取 residual 的 rolling z-score / OU s-score；
5. `z <= -entry_band`：long residual loser；
6. `z >= +entry_band`：short residual winner；
7. 同一时点只拿 top-1 / top-2 最极端，避免组合太散。

### 7.2 exit
最小版本：
- residual z-score 回到 `±0.5` 内平；
- 或 max-hold 到 `4~12` 根强平。

但本轮 probe 显示 exit 太快会被 cost 吃掉，所以下一版更建议：
- entry band 提到 `2.5 / 3.0`；
- exit 改成 zero-cross 或 `time-bucket rebalance`；
- 不要一回到 `0.5` 就全平，先测 partial exit。

### 7.3 sizing
最小版本：
- top-1 long / top-1 short 等权；
- 单币 notional cap；
- gross exposure cap。

增强版本：
- size ∝ `min(|z|, z_cap)`；
- 再除以短期 realized vol；
- 最后做 dollar-neutral / beta-neutral。

### 7.4 risk
必须补的 risk layer：
- liquidity gate：quote volume / spread / depth；
- factor exposure cap：组合对 PC1/PC2 的残留暴露不要太大；
- kill-switch：连续亏损或共同因子剧烈跳变时暂停；
- event veto：CPI/FOMC/ETF 流入流出极端日降低杠杆。

### 7.5 cost
这条策略最大风险就是 turnover。下一轮必须做：
- `0 / 2 / 4 / 6 / 8 / 10 bps` friction ladder；
- maker-first vs taker-only；
- `5m` child execution 是否能改善 `15m` parent 的成交；
- round-trip trade count 与 holding time frontier。

## 8. 和当前 `1m/3m/5m/15m` 短周期研发的关系
我的判断：

- `15m` 更适合作为 parent signal；
- `5m / 3m` 更适合作为 child execution / confirmation；
- `1m` 不适合直接重算 PCA 主信号，容易被噪音和手续费打爆；
- 如果要上更快周期，应该只用 `1m/3m` 来做 maker-first、taker-veto、order-book confirmation。

这条 alpha 对当前素材池的价值主要有两个：
1. **独立 stat-arb raw alpha**：PCA residual fade；
2. **shared selector**：告诉其他策略“当前哪个币相对共同因子最过冲”。

## 9. 下一步怎么测
1. **先做 `15m parent + 5m child execution`。**
   父信号保持 PCA residual z-score，不改 alpha 本体；child 只负责：
   - maker-first 等 `1~3` 根；
   - 若 price 没回归再 cross；
   - 比较 taker-only 与 maker-first 的 net bps/trade。

2. **扫 entry / exit frontier。**
   至少测：
   - entry band：`1.5 / 2.0 / 2.5 / 3.0`；
   - exit：`0.5 / 0 / opposite-cross`；
   - max-hold：`4 / 8 / 16 / 32` bars。
   目标不是最高 gross，而是找到 `net_bps/trade > 0` 的区域。

3. **把 universe 扩到 12~20 个 liquid perp。**
   PCA 策略需要横截面宽度。8 个币只够 sanity check，不够 production admission。

4. **补 PC exposure diagnostics。**
   每次开仓后检查组合对 PC1/PC2 的暴露；如果 residual 策略最后仍然暴露在 PC1 上，说明所谓 market-neutral 是假的。

5. **和 BTC-residual fast reversal 做 A/B。**
   同一 universe、同一 cost ladder 下比较：
   - BTC residualization；
   - PCA 2-factor residualization；
   - PCA + BTC explicit factor。
   这会直接回答：PCA 的复杂度有没有真正换来更干净的 alpha。

## 10. 风险与提醒
- repo 原始回测没有交易成本，不能直接相信收益图；
- 本轮 quick probe 的 gross 很漂亮，但单笔边太薄，扣粗成本后明显不够；
- PCA factor 可能过拟合最近横截面结构，rolling window 要做 OOS split；
- crypto universe 变化很快，top-N universe 必须 causal，不能用未来 liquidity；
- 这条策略如果不控 turnover，会从 stat-arb 变成给交易所打工。

## 11. 结论
这轮我会把它放进研究池，但不是以“马上实盘”的形式，而是以 **raw alpha skeleton / stat-arb parent signal** 的形式保留。

最短判断：

> **PCA residual fade 能提供清楚的 cross-sectional mean-reversion raw alpha；`15m` first probe 有 gross edge，但当前退出太快、单笔太薄，下一步必须围绕 entry band、holding time、maker-first execution 和 cost ladder 做 admission。**
