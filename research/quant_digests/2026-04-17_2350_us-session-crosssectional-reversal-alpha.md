# US equity session 附近的 cross-sectional intraday reversal：spot crypto 的时间窗反转 raw alpha，但当前更像低冲击 pocket 而不是可直接放大的主策略
- 时间：2026-04-17 23:50 UTC
- 类型：GitHub / notebook source audit
- 主题类型：raw alpha
- 基础 alpha：固定日内时间窗里的横截面反转——做多 15:30–16:00 ET 或 09:30–10:00 ET 表现最差币，做空同期表现最好币，持有接下来的 30–45 分钟
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/intraday/time-of-day/us-session/spot-crypto/reversal/15m/5m/cost/risk/repo/public-data
- 证据类型：工程经验

## 1. 这次看了什么
看了 **BNeillDickey (2026)** 的 GitHub repo **intraday-crypto-reversal-project**，核心是 1 个完整 notebook：用 Binance spot 25 币 `15m` 数据，测试 US equity open / close 附近的固定时间窗横截面反转，并把 commission、spread、sqrt-impact 分开建模。

## 2. 核心结论
- **base alpha 很清楚：不是趋势，不是 breakout，而是“固定时段的 losers-bounce / winners-fade 横截面反转”。** close-window 版用 `15:30–16:00 ET` 做信号，`16:15–17:00 ET` 持有；morning 版用 `09:30–10:00 ET` 做信号，`10:15–10:45 ET` 持有。
- **gross edge 不弱。** close-window test gross Sharpe `7.45`、平均 `+24.0 bps/day`；morning gross Sharpe `7.29`、平均 `+22.8 bps/day`。两套信号日度 PnL 相关性只有 `0.121`，说明更像两个相邻但不完全同源的 session-flow pocket。
- **成本把它打穿，主因不是手续费，而是冲击成本。** close-window 在 test 里：commission `14.0 bps/day`、spread `7.4 bps/day`、impact `97.0 bps/day`、total `118.4 bps/day`；gross 还活着，但 full-model net Sharpe 直接掉到 `-24.22`。
- **这不是“alpha 不存在”，而是“alpha 太薄，不能用当前仓位/流动性假设硬吃”。** 扣完 commission+spread 后 close-window 仍有 `+2.6 bps/day` 余量，但 impact 单项就比 gross alpha 大约高 `4x`。
- **对我们 desk 的真正价值，不是照抄全币篮子 spot 版，而是把它当成“时间窗 raw alpha 母板”。** 适合继续往 `更高流动性标的 / 更少腿数 / 更小 participation / perp majors / 5m finer timing` 方向压缩实现。

## 3. 为什么和当前项目有关
这篇东西补的是我们最近 digest 相对少碰的一块：**时间窗型 raw alpha**。它不是又一个泛 mean reversion，也不是把 external data 硬包装成主信号，而是明确告诉我们：
- 某些 alpha 的核心不是价格形态，而是 **一天里哪个时段发生了什么流**；
- 这类 alpha 天生适合做 `1m/3m/5m/15m` 最小实验，因为 entry/exit 是固定窗口，不需要复杂状态机；
- 即便原始实现 cost-dead，它也能为后续的 session gate、liquidity veto、basket compression、major-only 版本提供非常清楚的母体。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 逆势
- 基础 alpha：US session 特定 30 分钟窗口内的 loser-bounce / winner-fade
- regime：优先看 US open / close 附近、流动性明显抬升但未过度拥堵的时段
- filter / veto：ADV / volume filter、最大 participation cap、只做 majors、只保留单边最极端 decile、必要时加 market-beta neutral
- risk / sizing / execution overlay：小仓位、限价/被动成交优先、按 ADV 或 quote volume 缩放、超出冲击预算直接 veto

## 4. 可复刻的最小实验
- **研究假设**：在 Binance USDⓈ-M majors 上，US open / close 附近的短窗横截面 loser-bounce 仍可能存在，但只在“高流动性 + 低 participation + 少数腿”条件下可保留部分成本后 alpha。
- **可计算定义**：
  1. Universe：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA` 或更窄；
  2. 以 `15m` 先做母版：close signal=`15:30–16:00 ET` 收益排名，hold=`16:15–17:00 ET`；morning signal=`09:30–10:00 ET`，hold=`10:15–10:45 ET`；
  3. 每天只做 bottom 1~2 vs top 1~2，等权或按近 30d dollar volume 反比缩放；
  4. 再下钻到 `5m`：测试 `15:30–15:45 → 15:45–16:15`、`15:45–16:00 → 16:00–16:30` 两种更细切口。
- **最小回测切口**：Binance USDⓈ-M，`15m` 为主、`5m` 为精修；样本先取最近 `180~365d`，只看 liquid majors。
- **先看哪 1~2 个指标**：`post-cost mean bps/day`、`impact-aware Sharpe`。如果这两个不过线，不值得继续扩 universe。

## 5. 风险与保留意见
- 当前 repo 的强结果主要在 **spot 中小币横截面**，这和我们 desk 更常用的 liquid perp majors 不是同一执行环境，不能直接外推。
- 这类时间窗 alpha 很容易被 **拥挤、时段性 spread 扩大、成交不均匀** 吃掉；所以 gross 好看不代表可做。
- notebook 的 strongest claim 是“信号真实但难交易”，不是“这里有一条现成 production 策略”。
- 更实际的改写方向可能不是扩全市场，而是 **压缩到少量最液体合约 + 更细时间分辨率 + 更保守 participation cap**。

## 6. 来源
- BNeillDickey. (2026). *intraday-crypto-reversal-project*. GitHub.
- Repo URL: `https://github.com/BNeillDickey/intraday-crypto-reversal-project`
- Notebook URL: `https://raw.githubusercontent.com/BNeillDickey/intraday-crypto-reversal-project/main/Intraday_Crypto_Reversal_Project.ipynb`
- Supporting refs cited in notebook:
  - Heston, S., Korajczyk, R., & Sadka, R. (2010). *Intraday Patterns in the Cross-Section of Stock Returns*. Journal of Finance.
  - Bogousslavsky, V. (2016). *Intraday Trading Patterns and the Role of the Systematic Risk Factors*. Review of Financial Studies.
  - Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). *Market Intraday Momentum*. Journal of Financial Economics.
