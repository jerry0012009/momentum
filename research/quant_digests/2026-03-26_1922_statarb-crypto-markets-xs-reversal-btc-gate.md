# 别把 2026 market-neutral repo 只读成“139 币 12h 高 Sharpe”：更该先拆的是「adaptive shock-threshold XS reversal + BTC crash gate」完整 raw alpha，但 15m transfer 先判负
- 时间：2026-03-26 19:22 UTC
- 类型：2026 GitHub 新仓库 + README/source 审阅 + Binance Futures 公共 `15m` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：**在横截面内，对过去若干 lookback 上“绝对收益超过自适应分位阈值”的币做反手（loser-long / winner-short），按线性衰减持有，并用 BTC regime gate / inverse-vol / 组合层风险约束管理 crash 与集中度。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/market-neutral/adaptive-threshold/shock-reversal/btc-regime-gate/linear-decay/inverse-vol/portfolio-risk/repo/binance/perpetual/15m/5m/1h/cost-turnover
- 证据类型：repo README/front-page claim 审阅 + 当前公开数据最小 transfer

## 1. 这次看了什么
先回答一句：**这篇东西的 base alpha 是什么？**

不是“风险控制做得很全”，也不是“多策略组合后 Sharpe 很高”。**它的 alpha 本体，是 universe-level 的横截面 shock reversal：谁在最近几段里涨跌得过分，就在 market-neutral 篮子里反着做。**

主材料是 GitHub 仓库：
- **carlo855 (2026), _StatArb-Crypto-Markets_**
- Readable URL：`https://github.com/carlo855/StatArb-Crypto-Markets`
- Repo URL：`https://github.com/carlo855/StatArb-Crypto-Markets`

这份 repo 的首页 claim 很吸睛：
- **2.07 Sharpe**
- **20% MDD**
- **31% annual return at 15% volatility**
- **139 altcoins / 3.5 years / 12-hour bars / net of transaction costs**

但真正值得 intake 的，不是把 headline 直接搬过来，而是它把一条**可以独立落地的 cross-sectional raw alpha**拆得很具体：

1. 在横截面里做 **multi-lookback reversal ensemble**；
2. 不是固定阈值，而是用 **rolling percentile of absolute returns** 做 adaptive shock trigger；
3. 信号触发后不是一把梭，而是 **linear decay holding**；
4. 在组合层加 **BTC regime gate**，避免大盘下坠时继续机械抄底；
5. 再叠 **inverse BTC vol scaling / per-coin cap / vol targeting / drawdown deleveraging**。

翻成人话：**repo 真正能服务我们 desk 的，不是“一个回测很好看的 12h stat-arb 组合”，而是“一条可以拆成 entry/exit/sizing/risk/cost 的横截面 reversal 完整骨架”。**

## 2. 核心结论
### 2.1 这轮最该 intake 的是 raw alpha，不是 headline combo
repo 自己其实已经把风险写得很诚实：
- README 明说 **mean reversion OOS Sharpe ~6 很可能不可信**，高概率受 survivorship bias 影响；
- 也明说 **momentum OOS Sharpe ~-2**，像是 in-sample 优化过头；
- 成本只用了 **固定 20 bps**，没有做更完整的 fee / slippage / impact 敏感性分析。

所以这轮不该学的是：
- “31% 年化 / 2.07 Sharpe 所以直接可上”；
- “mean reversion + momentum combo 才是完整答案”。

更该学的是：
- **把 mean reversion leg 单拎出来，当作可复现 raw alpha；**
- **把 BTC gate、inverse-vol、vol targeting 看成生存层，而不是 alpha 本体。**

### 2.2 对当前 desk，最值钱的是“shock-thresholded XS reversal”这条线
这条线有三个优点：

1. **alpha 本体说得清。**
   不是 vague 的“市场回归均值”，而是：
   - recent move 超出 rolling shock quantile；
   - 横截面 market-neutral 反手；
   - 线性衰减持仓。

2. **天然可 market-neutral。**
   对短周期 desk，这比单币“抄底/摸顶”更适合做成本、beta、集中度治理。

3. **风险层和 alpha 层可以分开测。**
   先测 raw reversal 有没有 gross edge；
   再测 BTC gate / top-k / carry-over 持仓 / vol targeting 到底是救活还是添噪音。

### 2.3 它和昨天那篇 `adaptive percentile shock reversal` 不是重复主题
昨天 intake 的那篇更像：
- **single-asset / time-series**
- 针对单币自己的 shock fade
- 重点在单条信号的触发与持仓衰减

这份 repo 更像：
- **cross-sectional / market-neutral**
- 在整组 alt universe 里做 rich-vs-cheap / winner-vs-loser 反手
- 自带 **BTC regime gate + portfolio risk shell**

也就是说：**共用了“adaptive shock + decay”这类设计语言，但 alpha 层级不同。前者是单币时间序列，后者是横截面统计套利。**

## 3. 为什么它和当前 desk 直接相关
如果按本轮选题规则问一句：

- **这篇东西的 base alpha 是什么？**

答案很清楚：
- **cross-sectional short-term reversal / relative-value raw alpha**。

所以它不是 filter、不是 regime、也不是纯 overlay。

而且它补的是当前 desk 仍值得继续堆厚的那类素材：
- `mean reversion`
- `cross-sectional / relative value`
- `market-neutral`
- `entry/exit/sizing/risk/cost` 可以一次写全

这比再多补一篇“宏观/外部数据只能做 gate”的材料，更贴当前阶段。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / market-neutral / short-term mean reversion
- 基础 alpha：
  - 对资产 `i`，计算多个 lookback 上的最近收益 `ret(i, L)`
  - 若 `|ret(i, L)|` 超过 rolling absolute-return percentile threshold，则触发反手方向信号 `-sign(ret)`
  - 多 lookback ensemble 聚合
  - 横截面去均值、绝对权重归一，得到 long-short 篮子
- regime：
  - primary：`BTC short SMA > BTC long SMA` 才开仓
  - optional：calm-vs-stress 用 BTC realized vol 做放缩
- entry：bar close 生成权重，`next bar` 执行
- exit：持仓按线性衰减逐步退出，或在新信号覆盖时 rebalance
- sizing：
  - cross-sectional `demean + abs-normalize`
  - per-coin gross cap
  - optional inverse-BTC-vol scaling
- risk：
  - BTC crash gate
  - per-coin cap
  - portfolio vol target
  - drawdown deleveraging
- cost：
  - 这条线的关键不只是方向对不对，而是 **shock trigger 稀疏度 × decay 持有期 × rebalance turnover**

## 4. 当前 `15m` transfer check：短周期 desk 先不该直接照搬
为了避免只复述 repo，我做了一个更贴 desk 的最小迁移。

### 4.1 数据与口径
- 数据源：Binance USDⓈ-M Futures 公共 `15m` K 线
- 窗口：最近 **120 天**
- 可交易 universe：`ETH/BNB/SOL/XRP/DOGE/ADA/AVAX/LINK/LTC/DOT/TRX/SUI/TAO/HYPE`
- 参考大盘：`BTCUSDT`
- 迁移方式：
  - lookbacks：`8/16/32/64` bars
  - trigger：过去 `30d` rolling `|return|` 的 **90% 分位阈值**
  - 持仓：**16 bar linear decay**
  - 权重：横截面 **demean + abs-normalize**
  - 执行：`next bar`
- 成本口径：单边 **2 bps** baseline

产物目录：
- `reports/artifacts/quant_digests/statarb-crypto-markets-transfer_20260326_1922/summary.json`

### 4.2 结果一：不加 BTC gate 时，15m 上是“负 edge + 高换手”
`always-on` 版本：
- **gross ≈ -0.409 bps/bar**
- **gross Sharpe ≈ -3.97**
- **turnover ≈ 11.04x/day**
- **net @ 2 bps/side ≈ -0.639 bps/bar**

这说明至少在当前这版 Binance perp `15m` proxy 下，**repo 那套横截面 reversal 不是直接缩放就能活。**

### 4.3 结果二：BTC 4h>24h gate 有帮助，但远远不够
加一个很轻的 BTC regime gate：`BTC 4h SMA > 24h SMA` 才允许持仓。

结果变成：
- **gross ≈ -0.296 bps/bar**
- **gross Sharpe ≈ -3.85**
- **turnover ≈ 6.28x/day**
- **active fraction ≈ 43.6%**
- **net @ 2 bps/side ≈ -0.427 bps/bar**

翻成人话：
- gate 确实把 turnover 从 `11.0x/day` 压到 `6.3x/day`；
- 也把损失削薄了一截；
- **但还没到“从负变正”的程度。**

### 4.4 这轮 transfer 给出的诚实结论
所以 desk 现在更该记住的是：

1. **repo 的 raw alpha 骨架是清楚的；**
2. **但 12h alt-universe 的故事，不能直接压缩到 15m perp；**
3. **BTC gate 是必要条件，但不是充分条件；**
4. **短周期要活下来，下一步必须从“稀疏化 + 降换手”入手，而不是继续优化 headline Sharpe。**

## 5. 对 desk 的真正 intake 应该是什么
### 5.1 不要 intake 整个 headline combo，先 intake mean-reversion branch
repo 其实已经提示了最合理的读法：
- momentum leg 在 OOS 里明显更脆；
- mean reversion leg 至少有一个清楚可复现的 signal family；
- 但 repo 自己的高 Sharpe 读数带明显 survivorship bias 警报。

所以这轮应该 intake 的是：
- **shock-thresholded XS reversal raw alpha skeleton**

而不是：
- “2026 又一个高 Sharpe stat-arb 组合”。

### 5.2 真正需要 desk 化的不是更复杂，而是更稀疏
当前 15m transfer 失败，不像是“reversal 逻辑完全错误”，更像是：
- 触发太频繁；
- 标的太宽；
- bar-bar 权重变化太密；
- 组合层的安全壳不够救这种高换手迁移。

也就是说，这条线如果还有希望，突破口更可能在：
- **稀疏 entry**
- **top-k 只做最极端 shock**
- **延长持有、减少 rebalance**
- **symbol pre-filter**

而不是继续堆更多 portfolio cosmetics。

## 6. 下一步怎么测
这里必须给可执行的下一步，而不是“以后再看”。

1. **先做 extreme-only top-k 版本。**
   不要每次 shock 都打。下一轮优先测：
   - 每个 bar 只做 `|score|` 最大的 top `2~4` 个币；
   - 其余资产不参与。

2. **把 15m rebalance 改成 `hold 8~24 bars` 的稀疏调仓。**
   当前 `16 bar linear decay` 仍然太勤。下一轮测：
   - 新信号触发后锁定最短持有期；
   - 非必要不在每根 bar 重排全组合。

3. **加 symbol admission filter，而不是全市场一锅端。**
   repo 用的是 volume-based universe，但对短周期还不够。优先测：
   - 只保留成熟主流 perp；
   - 去掉高跳空、高 funding、持续低深度币。

4. **把 BTC gate 继续升级成“crash veto + vol compression allow”双层。**
   当前只用了 `4h>24h` 的单层门。下一轮可以测：
   - `BTC gate` 只负责 veto；
   - `BTC realized vol percentile` 决定是否 size-down。

5. **画 break-even cost curve。**
   当前只测了 `2 bps/side`。下一轮至少画：
   - `0.5 / 1 / 2 / 3 bps/side`
   - 看这条线究竟死在 signal 还是死在 turnover。

6. **把 15m 和 1h 一起做迁移边界图。**
   这类 12h 原型很可能不是 15m 最合适，反而更接近 `1h → 4h`。要尽快确认它到底是：
   - 真有短周期可迁移边；
   - 还是只能留在更慢频的 stat-arb 素材池。

## 7. 风险与保留意见
- repo headline 指标是 **repo front-page claim**，本轮没有独立重跑原始 notebook；
- README 已主动提示 survivorship bias / overfitting / 单一成本模型等问题；
- 我的 transfer check 是 **Binance perp 15m proxy**，不等于对 repo 的严格 replication；
- 这轮更值得关注的不是 annualized 大数，而是：
  - **bps/bar**
  - **turnover/day**
  - **BTC gate 能否把负 edge 拉回到接近 0**
- 当前证据下，这条线对 `15m` 还不能判成 ready；更像一条**值得继续稀疏化测试的 raw alpha skeleton**。

## 8. 来源
1. **carlo855. (2026). _StatArb-Crypto-Markets_. GitHub repository.**
   - Readable URL: `https://github.com/carlo855/StatArb-Crypto-Markets`
   - Repo URL: `https://github.com/carlo855/StatArb-Crypto-Markets`
2. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 9. 本地相关产物
- Digest：`research/quant_digests/2026-03-26_1922_statarb-crypto-markets-xs-reversal-btc-gate.md`
- Artifact：`reports/artifacts/quant_digests/statarb-crypto-markets-transfer_20260326_1922/summary.json`
- Page URL（build/publish 后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-26_1922_statarb-crypto-markets-xs-reversal-btc-gate.html`
