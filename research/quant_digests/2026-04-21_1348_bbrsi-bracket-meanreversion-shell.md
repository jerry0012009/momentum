# 别把这份 multi-strategy bot 只读成“双策略大杂烩”：对 short-cycle crypto desk，更该先拆的是「BB 触带 × RSI 极值确认 × 2%/4% bracket exit」这条完整 raw alpha 壳
- 时间：2026-04-21 13:48 UTC
- 类型：GitHub / repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：当价格显著偏离自身短期均值、同时 RSI 已进入极端区间时，下一段更容易先向均值回吐；交易上就是 `close <= lower Bollinger Band & RSI<25 -> long`，`close >= upper Bollinger Band & RSI>75 -> short`，随后用固定 `2%` 止损、`4%` 止盈和反向信号平仓
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：mean-reversion / bollinger-band / RSI / bracket-exit / stop-loss / take-profit / Binance USDⓈ-M / 15m / 5m
- 证据类型：工程经验 + repo rule shell + public-data first probe

## 1. 这次看了什么
这次看的是 2026 GitHub repo **PatrickSebastine / mean-reversion-trading-bot**。repo 表面上同时写了 mean reversion 和 momentum 两条线，但对我们更有价值的其实是它把一条 **最朴素、最容易快复现的 BB+RSI 均值回复完整策略壳** 写全了：`15m`、`20` 期 Bollinger、`RSI14`、`RSI<25 / >75` 入场、`2%` 硬止损、`4%` 硬止盈、反向信号平仓、外加账户级 daily loss circuit breaker。对 short-cycle desk 来说，这比“又一个指标组合”更重要，因为它已经把 `entry / exit / risk / sizing / kill-switch` 摊成了可直接复做的 baseline。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：不是“布林带会反弹”这种空话，而是 **短窗过度偏离后的价格回吐**。RSI 在这里不是第二条 alpha，而是用来过滤“只是正常下跌/上涨”与“已经进入极端拉伸”的确认层。
- repo 真正值得拿的不是指标本身，而是 **完整 shell**：`BB+RSI` 给入场，`2%/4%` bracket 直接定义盈亏比，反向信号给兜底退出，账户日亏损阈值当组合层熔断。
- 我用 repo 自带的 `8` 个币（`BTC/ETH/SOL/XRP/DOGE/ADA/AVAX/LINK`）做 Binance USDⓈ-M public-data portability probe 后，结论不是“全池普适可做”，而是 **存在很强的 symbol pocket 分化**：
  - `15m` 全池共 `209` 笔，gross 约 `-12.22 bps/笔`，粗扣 `8 bps` round-trip 后约 `-20.22 bps/笔`
  - 但 `15m` 上 `SOL` 与 `DOGE` 明显更厚：`SOL` 约 `+51.48 bps/笔`、`DOGE` 约 `+59.56 bps/笔` gross；`BTC` 也还有 `+13.14 bps/笔`
  - `5m` 直接平移后更差：全池 `209` 笔 gross 约 `-18.60 bps/笔`；不过 `BTC` 仍有 `+9.26 bps/笔`、`XRP` 约 `+22.92 bps/笔` 的 pocket
- 更值得注意的是，这条线 **并不主要靠大量 TP 命中赚钱**。例如 `5m BTC` 的 TP 命中率只有 `4%`，但 reversal exit 占了 `56%`；说明对 short-cycle desk 来说，真正该继续优化的可能不是再把 TP 放远，而是 **更细的出场与 child execution**。

## 3. 为什么和当前项目有关
这轮值得写，因为它补的是 **“最简单、最完整、可立刻做 first verdict 的单资产 MR baseline”**。我们最近虽然已经写过不少 MR / pairs / basis 方向，但这篇的价值在于：
1. 它不是相对价值多腿，而是最容易在 `5m/15m` 直接拉起的一腿策略；
2. 它把 `base alpha / confirmation / bracket exit / circuit breaker` 边界写得很干净；
3. 它天然适合作为后续 `maker-first`、`time-stop`、`volatility veto`、`symbol router` 的母壳。

## 4. 策略拆解
- 方向属性：单资产 / 逆势 / mean reversion
- 基础 alpha：价格短窗过度偏离后向均值回吐
- regime：更像震荡或尖刺后回补环境，不适合趋势单边扩散时硬抄底摸顶
- filter / veto：RSI 极值确认；后续最该补的是 `trend veto / vol regime veto / symbol-specific admission`
- risk / sizing / execution overlay：`2%` SL、`4%` TP、反向信号退出、账户级日亏损熔断、仓位按信号强度缩放

## 5. 可复刻的最小实验
### 实验目标
验证这条线到底是：
- A. 可以做成 **selective symbol router** 的 raw alpha，还是
- B. 只是“看起来完整、但必须强依赖更细过滤”的 baseline 壳。

### 最小实验口径
1. universe 固定 `BTC/ETH/SOL/XRP/DOGE/ADA/AVAX/LINK`
2. 周期先跑 repo 原版 `15m`，再测 `5m` child transfer
3. entry：`BB20(2.0)` + `RSI14 < 25 / > 75`
4. exit：`2%` SL、`4%` TP、反向信号平仓；再加一版 `8/16/24 bars timeout`
5. friction ladder：`4 / 8 / 12 bps` round-trip
6. 分层看 `symbol contribution / TP rate / reversal rate / mean hold bars / trend-regime breakdown`

## 6. 这轮我保留的判断
这份 repo 不该被读成“又一个双策略 demo”，因为它其实给了一个非常清楚的 **均值回复完整策略壳**。但 public probe 也很直白：

> **BB+RSI 这条 raw alpha 不是全池稳定印钞机，更像“少数 symbol pocket 仍有边、全池硬铺会被成本和趋势环境一起打穿”的 selective MR baseline。**

换句话说，值得继续搬的不是“全币通用 BB+RSI”，而是 **BB+RSI 作为一腿 MR 母壳，再往上叠 symbol router / trend veto / timeout / maker-first execution**。

## 7. 下一步怎么测
- 先做 **symbol router**：只留 `BTC/SOL/DOGE/XRP` 这类当前 gross 更厚的币，看 trade count 掉多少、净值有没有明显改善。
- 做 **趋势否决**：例如 `EMA200` 同向单边趋势内禁止逆势开仓，检验是否能砍掉 `ETH/ADA/XRP 15m` 这类明显被 stop 打穿的样本。
- 做 **timeout exit**：现在不少盈利靠 reversal exit 而不是 TP，下一轮应对照 `8/16/24 bars` 超时平仓，看看能否减少长持仓拖累。
- 若 cost 后开始接近平衡，再补 **maker-first / passive re-entry / spread filter**；若仍显著为负，就把它降级为“只服务 selective overshoot router 的 baseline”，不要急着实盘化。

## 8. 来源
- PatrickSebastine (2026), **mean-reversion-trading-bot**. GitHub repo. Repo URL: <https://github.com/PatrickSebastine/mean-reversion-trading-bot>
- Readable README URL: <https://github.com/PatrickSebastine/mean-reversion-trading-bot/blob/master/README.md>
- Source audit依据：`README.md`、`config.yaml`、`trading_engine.py`、`overnight_trader.py`
- 本地 artifact：
  - `reports/artifacts/quant_digests/2026-04-21_patrick_meanreversion_probe_summary.csv`
