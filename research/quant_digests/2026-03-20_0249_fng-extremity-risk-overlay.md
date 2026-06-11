# 别把 Fear & Greed 当 15m 方向信号：`sentiment extremity` 更像三条收口线共用的 risk overlay（size / veto 层）
- 时间：2026-03-20 02:49 UTC
- 类型：论文 + GitHub + 外部公开数据 + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/fear-greed/sentiment/regime/filter/risk-overlay/position-sizing/paper/repo/crypto/15m
- 证据类型：论文证据 + 工程证据 + 本地代理快检

## 1. 这次看了什么
这轮主看 Farzulla (2026) 的新论文与同名仓库：**The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets**。核心不是拿 F&G 去猜下一根涨跌，而是把“情绪极端日”当成不确定性和交易摩擦更高的环境标签。这个旁支想法很适合当前 desk：直接做 `breakout-short / Fib retest_hold / EMA-PSAR` 的共享风控层。

## 2. 核心结论
- **一句话核心结论**：`Fear & Greed` 在 15m 更适合作为低频 `regime/risk overlay`（仓位、确认、否决），不该伪装成逐根主信号。
- **一句话怎么证明**：论文与 repo 都把“极端情绪 = 更高不确定性/价差”作为主命题；本地快检也显示极端日未来 4h 路径波动显著更大，但对 breakout continuation 方向并不稳定可预测。

### 2.1 论文侧可直接拿来用的点（近 5 年新材料）
- 样本扩展到 `2018-02 ~ 2026-01`（文中给出 `N=2,896`）。
- 报告了显著的 extremity premium：`p < 0.001`，`Cohen's d = 0.21`。
- 不确定性到价差方向 Granger 统计显著：`F = 211`。
- 文中也明确提醒：该效应对函数形式敏感，且 F&G 含有波动成分，不能把它当“纯情绪方向预测器”。

### 2.2 本地 15m 代理快检（BTC/ETH/SOL，近 1 年）
将 daily F&G 贴到 `15m` bars，观察未来 `4h`（16 bars）：
- 在 `extreme_fear + extreme_greed` 合并样本下，`future realized abs move` 相对 neutral **+28.65%**（0.04116 vs 0.03199）。
- `extreme_fear` 相对 neutral：`future realized abs move` **+28.95%**。
- `extreme_greed` 相对 neutral：`future realized abs move` **+20.51%**，且路径效率（净位移/路径波动）约 **-5.17%**。

> 解释：极端日“更吵、更贵、更容易放大滑点/尾部风险”，支持它做 risk overlay。

### 2.3 与 breakout follow-up 的贴合验证（最小 Donchian 代理）
在 20-bar close-breakout 的 4h 代理里：
- neutral 的 failure rate 约 `85.28%`；
- extreme_fear 约 `84.25%`；
- extreme_greed 约 `80.81%`（样本较小，仅 99）。

这组结果**不支持**“极端情绪日=统一方向否决”。更稳妥的落点是：
- 用作 `size-down / risk-budget`，
- 而不是硬性 direction veto。

## 3. 为什么和当前三条收口线直接相关
这题不是绕路：它可以给三条线共用同一个低频风控外壳。
- `V3 breakout-short follow-up`：极端日优先降仓/提确认阈值，避免把 continuation 判定放在高噪声环境里。
- `Fibonacci confirmation / retest_hold`：极端日保留 setup，但提高 hold 确认标准（例如 retest 后再破结构点才放行）。
- `EMA / PSAR raw alpha focus`：raw alpha 不变，先把极端日 exposure 缩小，降低成本与尾部噪声的放大效应。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
`F&G extremity` 作为日级 overlay 可以改善 15m 策略的回撤与左尾，而不必依赖其方向预测能力。

### 可计算定义
- Daily regime：
  - `extreme_fear <= 25`
  - `extreme_greed >= 75`
- Overlay：
  - `size_multiplier = 0.7`（极端日）
  - `size_multiplier = 1.0`（其他日）
- 可选附加：极端日把 admission 门槛提高一档（例如多加一个 close-confirmed 条件），但先不改主信号本体。

### 最小回测切口
- 资产：`BTC/ETH/SOL perp`
- 周期：`15m`（执行可下钻 `5m`）
- 样本：最近 `180~365d`
- 成本：`6/10/15 bps per side`
- 三臂：
  1) baseline（现有三线规则）
  2) baseline + extremity size overlay（本轮核心）
  3) baseline + extremity size overlay + stricter confirmation（可选）

### 优先观察指标
1. `post_cost_return`
2. `max_drawdown`
3. `left-tail (p5 trade pnl)`
4. `turnover / trade_count`（防止“靠少交易看起来变好”）

## 5. 风险与保留意见
- 这是外部低频数据（daily），天然不适合逐根 15m 方向触发。
- 论文与 repo 本身也提示了“与波动成分纠缠”的识别问题，不能过度宣称“纯情绪因果”。
- `extreme_greed` 在近一年样本里观测偏少（本地快检约 99 个 breakout 事件），需要滚动扩样验证。

## 6. 来源（论文 / 仓库 / 外部数据）
1. Farzulla, M. (2026). *The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets*. arXiv (q-fin.ST).
   - Authors: Murad Farzulla
   - Year: 2026
   - Title: The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets
   - Venue: arXiv / Dissensus AI Working Paper (DAI-2510)
   - DOI: `10.48550/arXiv.2602.07018`
   - Readable URL: <https://arxiv.org/abs/2602.07018>
   - Repo URL: <https://github.com/studiofarzulla/sentiment-microstructure-abm>
2. studiofarzulla. (2026). *sentiment-microstructure-abm*. GitHub repository.
   - Authors: studiofarzulla
   - Year: 2026
   - Title: sentiment-microstructure-abm
   - Venue: GitHub
   - DOI: `10.5281/zenodo.17989810`（仓库 README 标注）
   - Readable URL: <https://raw.githubusercontent.com/studiofarzulla/sentiment-microstructure-abm/master/README.md>
   - Repo URL: <https://github.com/studiofarzulla/sentiment-microstructure-abm>
3. Alternative.me. (public API). *Crypto Fear & Greed Index*.
   - 数据源：<https://api.alternative.me/fng/?limit=0&format=json>
   - 公开性：公开 HTTP API，无需 key
   - 更新频率：日更（daily）
   - 最小复现实验口径：按 UTC 日期把 daily F&G regime 贴到 15m bars，作为 day-level overlay（size/filter），不做逐根方向信号。
4. Binance Spot Market Data API. *Kline/Candlestick Data*.
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>
   - 用途：构建 BTC/ETH/SOL 15m 本地代理快检。

## 7. 本轮落地产物
- `reports/artifacts/quant_digests/fng_extremity_overlay_proxy_2026-03-20.csv`
- `reports/artifacts/quant_digests/fng_extremity_breakout_proxy_2026-03-20.csv`
