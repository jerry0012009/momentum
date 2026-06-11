# 别把 Donchian+ATR 当“天然可用”：这份 2025 CTA breakout 新仓库更像完整 raw alpha 骨架，但要先过成本生存线
- 时间：2026-03-23 21:40 UTC
- 类型：近 5 年新仓库 + 公开交易所数据最小快检
- 主题类型：raw alpha
- 基础 alpha：trend / breakout（Donchian 向上突破后的趋势延续）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/breakout/donchian/atr/chandelier/volume/cost-survival/repo/crypto/5m/15m
- 证据类型：仓库代码规则 + 本地公开数据快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“价格突破过去 N 根高点后，趋势在短周期继续延续”**，不是 filter。

本轮选题来自新仓库 **yukai1625/freqtrade-strategy-portfolio (2025)** 的 `CTAAggressiveBreakout`：
- entry：`close` 突破 `Donchian High` + 量能过滤
- exit：慢 Donchian 退场 + ATR Chandelier 止损 + 极端拉升止盈
- risk：基础止损 + ATR 动态止损
- cost：仓库未给真实成交成本建模（这正是我们要快检的重点）

## 2. 核心结论
- **一句话结论：** 这套 Donchian+ATR 是“可独立复现、可完整落地”的 raw alpha 骨架，但在近 90 天 Binance 5m 公共数据上，默认参数与简化成本下**尚未过成本生存线**。
- **一句话证据：** 我按仓库逻辑做了 4 币 5m 代理回测（BTC/ETH/SOL/BNB，next-bar open 执行，双边费滑合计约 6bps），默认与两组变体都为负。

关键数据点（本地快检）：
1. 默认参数跨 4 币合并：`trades=1350`，`avg_trade_net=-12.48 bps`，`win_rate=26.96%`。
2. 默认参数单币中最差为 `SOLUSDT`：`mean_net=-16.40 bps/trade`。
3. 参数更严格（`breakout_len=30, exit_len=70, atr_mult=4.0, vol_mult=1.1`）后虽有改善，但仍 `variant mean_net=-9.28 bps`（仍未转正）。

## 3. 为什么和当前项目有关
- 这是 **raw alpha 本体**，不是再做一层解释型 gate；能直接补我们素材池里“可执行 trend breakout 全链路模板”。
- 同时它给了很明确的实盘拆件接口：
  - `entry`（突破+量能）
  - `exit`（慢退场+fail-fast）
  - `risk`（ATR stop）
  - `cost`（后续接真实 taker/maker、滑点、冲击模型）
- 对 `1m/3m/5m/15m` 的意义：骨架可迁移，但成本与交易频次必须重估，不能直接平移。

## 3.5 策略拆解（必填）
- 方向属性：顺势（trend following）
- 基础 alpha：突破过去 N bar 高点后，延续段的 drift 捕获
- regime：中高波动且有连续趋势段时更友好
- filter / veto：量能过滤（`volume > vol_sma * vol_mult`）
- risk / sizing / execution overlay：ATR Chandelier 止损、慢 Donchian 退出、极端拉升止盈；后续需接入仓位上限与成本分层

## 4. 可复刻的最小实验（公开数据口径）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源：Binance USDⓈ-M Futures `fapi/v1/klines`
- 公开性：公开可获取（无需私钥）
- 更新频率：支持 `1m/3m/5m/15m`
- 本轮最小实验：
  - 标的：BTC/ETH/SOL/BNB
  - 周期：5m
  - 样本：近 90 天
  - 执行：信号后 next-bar open
  - 成本：单边 `fee 2bps + slippage 1bps`

### 4.2 下一步怎么测（必须）
1. **先做周期压缩测试**：同一骨架在 `15m`、`5m`、`3m`、`1m` 比较 `post-cost expectancy` 与 `turnover/day`，找成本后仍有边的“频率甜点区”。
2. **加入 regime gate（不改 base alpha）**：仅在 `realized-vol` 中位分位带（例如 30%~70%）开机，验证是否能显著减少高噪音假突破。
3. **做执行诚实化**：拆 maker/taker 占比与 participation cap，输出“信号 edge → 成交 edge”衰减曲线。
4. **保留 raw alpha 身份**：若加 gate 后才存活，需明确记账为“breakout raw alpha + regime/filter”，而不是把 gate 伪装成 alpha 本体。

## 5. 风险与保留意见
- 这是公开数据代理快检，不是交易所逐笔成交重建；对真实冲击成本仍偏乐观。
- 当前结果提示：该策略不是“默认即用”，更像需要严格成本治理与时段/状态筛选的候选骨架。
- 本轮结论是“可进研究池但暂不上线”，不是“彻底否决 Donchian breakout 家族”。

## 6. 来源
1. **yukai1625 (2025). _freqtrade-strategy-portfolio_. GitHub repository.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://github.com/yukai1625/freqtrade-strategy-portfolio
   - Repo URL: https://github.com/yukai1625/freqtrade-strategy-portfolio
2. **yukai1625 (2025). _cta_aggressive_breakout.py_. GitHub source file.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://raw.githubusercontent.com/yukai1625/freqtrade-strategy-portfolio/main/strategies/cta_aggressive_breakout.py
   - Repo URL: https://github.com/yukai1625/freqtrade-strategy-portfolio/blob/main/strategies/cta_aggressive_breakout.py
3. **Binance Developers. USDⓈ-M Futures API - Kline/Candlestick Data.**
   - Venue: Official API Docs
   - DOI: N/A
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 7. 本地复现产物
- `reports/artifacts/quant_digests/cta_aggressive_breakout_20260323/summary_default.csv`
- `reports/artifacts/quant_digests/cta_aggressive_breakout_20260323/variant_compare.csv`
- `reports/artifacts/quant_digests/cta_aggressive_breakout_20260323/meta.json`
- `reports/artifacts/quant_digests/cta_aggressive_breakout_20260323/trades_*_5m.csv`