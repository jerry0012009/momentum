# 别把这份 2026 新 repo 的高 Sharpe README 当结论：对 short-cycle desk，更该先确认的是「dual-SuperTrend flip × EMA50 × volume gate」这条 15m raw alpha，但按源码现状几乎不触发

- 时间：2026-04-04 10:50 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `src/strategy.py` + `docs/METHODOLOGY.md`）+ Binance Spot 公共 `15m` recent-window portability probe（`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`, 2026-01-04 ~ 2026-04-04）
- 主题类型：raw alpha
- 基础 alpha：**快慢双 SuperTrend 同向、且价格站在 `EMA50` 正确一侧并伴随放量时，顺着 `15m` 趋势方向开仓；随后用 `1.8 x ATR` 止损、`3.5 x ATR` 止盈、fast SuperTrend trailing stop 和 `20` 根 time stop 去抓短周期延续。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/single-asset/dual-supertrend/ema/volume-confirmation/atr-stop/time-stop/repo/public-data/binance/15m/5m/3m/1m/cost/source-audit
- 证据类型：repo 源码证据 + 公共数据最小便携性快检

## 1. 这次看了什么

这轮我刻意没有再补 pairs / carry / OFI，而是补一条**看起来像完整 15m 趋势 raw alpha 壳**的新 repo：双 SuperTrend 顺势开仓，ATR 动态止盈止损，外加 volume / volatility filter。它之所以值得 intake，不是因为 README 上那串高 Sharpe 数字，而是因为它理论上确实覆盖了 entry / exit / sizing / cost 四个核心部件；但源码和 README 的口径冲突很大，而且我按公开 Binance `15m` 数据做 recent-window 复现后，结果是 **90 天内 4 个主流币一笔都没打出来**。所以这轮真正值得留下的不是“高 Sharpe CTA 已验证”，而是：**这是一条 base alpha 清楚、但当前实现明显还没过 source-audit 的趋势 raw alpha 候选。**

## 2. 先回答最重要的一句：base alpha 是什么？

一句话版：

> **base alpha 就是：当快慢双 SuperTrend 同向翻转、价格站上/跌破 EMA50、且量能放大时，顺势追一段 15m 趋势延续。**

这条线非常明确：

1. 用 fast SuperTrend 抓较早的方向翻转；
2. 用 slow SuperTrend 避免太快、太噪的假翻转；
3. 用 `EMA50` 确保不是逆大方向去追；
4. 用成交量过滤避免在太干的 bar 里下手；
5. 再用 ATR 止损/止盈和 time stop 把持仓收敛成完整策略。

所以它不是 filter，不是 overlay，也不是 execution-only 技巧；

> **它本身就是一条完整的 trend / momentum raw alpha。**

## 3. repo 真正给了哪些完整策略部件

### 3.1 Entry：快慢双 SuperTrend + EMA50 + 放量确认

`src/strategy.py` 里真正会触发开仓的条件是：

- `bull_flip` / `bear_flip`：fast SuperTrend 方向翻转；
- `st_slow_dir` 与 fast flip 同向；
- `close > ema50` 才能做多，`close < ema50` 才能做空；
- `volume >= 1.2 x SMA20(volume)`；
- `atr_pct < 3%`，即不在高波动状态。

换成人话：

> **它不是“只要 SuperTrend 翻了就追”，而是要求趋势方向、均线方向、量能状态一起同意。**

### 3.2 Exit：ATR 止损、ATR 止盈、fast ST trailing、20-bar 超时

repo 的退出层其实挺完整：

- 止损：`1.8 x ATR`
- 止盈：`3.5 x ATR`
- trailing stop：用 fast SuperTrend line 动态抬/压止损
- time stop：`20` 根 `15m` K，也就是最多大约 `5` 小时
- 若 fast ST 反向 flip，也直接出场

这意味着它不是只有入场，没有退场；而是一条可以完整写进回测器的策略定义。

### 3.3 Sizing / Cost：2.5% 风险、低波放大 1.2x、显式 fee/slippage

源码里 sizing 也是成体系的：

- 每笔基础风险：`2.5%` 账户权益
- 若 `ATR% < 1.5%`，仓位乘 `1.2`
- 否则正常仓位；高波直接跳过
- 成本口径：`4 bps` fee + `1 bp` slippage

这对 desk 来说很重要，因为它至少承认：

> **short-cycle 趋势 alpha 不是只看胜率，得把交易成本写进 PnL。**

## 4. 这份 repo 最大的问题：口径严重不一致，源码比 README 紧得多

这轮最值得记住的，不是策略名字，而是**repo 的三套规则根本没对齐**。

### 4.1 GitHub repo 简介、README、代码各说各话

我看到至少三套版本：

- **GitHub repo 简介**：`ST(10,3)` + `ST(21,2)`，`ADX > 22`，risk per trade `1%`
- **README / METHODOLOGY**：`ST(8,2.5)` + `ST(18,2)`，EMA50，`ATR% < 3%`，volume `> 1.2 x SMA20`，risk per trade `2.5%`
- **源码**：基本跟 README 版本一致，但又没有实现 README 里强调的 `fee_adjusted_edge > 0.15%`

也就是说：

> **repo claim 说得最满，README 次之，真正执行的是第三套更窄、更简化的逻辑。**

### 4.2 代码里有些“写了像有、其实没用”的部件

`src/strategy.py` 里还有几个很说明问题的点：

- `rsi` 算了，但根本没参与信号；
- `min_edge` 参数定义了，但没进入 entry 判断；
- README 说有 `1h trend bias`，代码里没有；
- README / repo 简介里提到 `ADX`，代码里没有；
- `__main__` 只打印“Expected Performance”，并不会真的拉数据回测。

所以正确读法不是“这份 repo 已经验证了一个完整 alpha”，而是：

> **它给了一个完整 raw alpha 壳的轮廓，但实现和宣传明显没对齐。**

### 4.3 连回测主函数都有可复现性问题

我直接按源码调用 `run_backtest(raw_ohlcv)` 时，函数会因为缺少 `high_vol` 等信号列报错；要先手动对每个 DataFrame 调 `generate_signals()` 才能跑下去。

这不是什么大 bug，但它说明一件事：

> **repo 目前更像 research draft，而不是已经打磨好的可直接复现实验。**

## 5. Recent-window portability probe：按源码现状，90 天里 4 个币 0 笔交易

我用 Binance Spot 公共 `15m` OHLCV，按 repo 当前源码逻辑做了一版 recent-window 便携性快检：

- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- 区间：`2026-01-04 10:49 UTC ~ 2026-04-04 10:49 UTC`
- 每个标的 bar 数：`8640`
- 先跑 `generate_signals()`，再跑 repo 自带 `run_backtest()`
- 结果工件：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/supertrend_recent_90d_probe/summary.json`

### 5.1 总结果：`0` trades，不是收益低，而是根本不开火

总结果非常直接：

- 总交易数：`0`
- 胜率：`0`
- 净 PnL：`0`
- Sharpe：`0`
- Max Drawdown：`0`

这个结果的含义不是“它稳”，而是：

> **当前代码在 recent 90d 的主流币 `15m` 样本上，几乎没有产生可交易信号。**

### 5.2 信号密度诊断：真正卡住的是 flip，不是高波过滤

四个币的诊断几乎一模一样：

- `BTCUSDT`：`bull_flip = 2`，`bear_flip = 3`，`long_signal = 0`，`short_signal = 0`
- `ETHUSDT`：`bull_flip = 2`，`bear_flip = 3`，`long_signal = 0`，`short_signal = 0`
- `SOLUSDT`：`bull_flip = 2`，`bear_flip = 3`，`long_signal = 0`，`short_signal = 0`
- `BNBUSDT`：`bull_flip = 3`，`bear_flip = 3`，`long_signal = 0`，`short_signal = 0`

与此同时：

- volume filter 通过率大约只有 `25% ~ 27%`
- 但 high-vol bar 几乎没有：`BTC 0`、`ETH 1`、`SOL 9`、`BNB 1`
- `ATR%` 中位数也只在 `0.31% ~ 0.49%`

所以这轮 probe 最重要的结论不是“波动太大所以做不了”，而是：

> **当前实现里，SuperTrend flip 本身就已经极少发生；真正的瓶颈在 SuperTrend 的实现/参数口径，而不是 ATR 风险门槛。**

### 5.3 这对 desk 来说反而是好事：很快就知道问题在哪

这类 source-audit 的价值就在这里。

如果 recent 90d 跑出来是“有很多交易但收益一般”，下一步还得继续拆交易成本、择时质量、持仓效率。

但现在不是。现在的问题更基础：

> **它在 public data 上根本没有 firing density。**

这反而让下一步清楚很多：先别谈 PnL，先谈“这套实现到底是不是 canonical SuperTrend”。

## 6. 这条主题为什么仍值得进研究池

虽然 recent probe 直接把 repo 当前实现判成了“几乎不触发”，但这条主题仍然值得 intake，原因是：

1. **base alpha 很清楚**：就是 trend continuation，不是 filter；
2. **策略骨架完整**：entry / exit / sizing / cost 都有；
3. **失败方式也很清楚**：不是玄学，是 source-audit 能直接定位的问题；
4. **它补的是 trend raw alpha 家族的一个具体壳**，而不是又一个泛泛“趋势可能有效”。

所以它的正确 desk 定位不是“已验证 alpha”，而是：

> **高优先级 source-debug 候选：如果 canonical 化后能恢复正常 signal density，它才配进入正式复现池。**

## 7. 它和 `1m / 3m / 5m / 15m` 的关系怎么理解

### 7.1 这条线的原生时间尺度就是 `15m`

不要被“短周期”三个字带偏。这份 repo 的原生持有和过滤尺度其实不短：

- fast ST `8 x 15m` ≈ `2` 小时
- slow ST `18 x 15m` ≈ `4.5` 小时
- `EMA50 x 15m` ≈ `12.5` 小时
- time stop `20 x 15m` ≈ `5` 小时

所以它天然更像：

> **`15m` 上做入场，持有几小时的 trend continuation 壳。**

### 7.2 如果要迁到 `5m`，必须保时间长度，不要保 bar 数

若未来要往 `5m` 迁，正确做法不是继续用 `8/18/50/20` 这组 bar 数，而是保住时间跨度：

- fast ST：`8@15m` → 约 `24@5m`
- slow ST：`18@15m` → 约 `54@5m`
- EMA：`50@15m` → 约 `150@5m`
- max hold：`20@15m` → 约 `60@5m`

否则你测到的根本不是同一条 alpha。

### 7.3 `1m / 3m` 现在不该直接上

在当前版本里，连 `15m` 信号密度都几乎为零，没必要直接把它压到 `1m / 3m`。

更合理的用法是：

- 先在 `15m` 修好 canonical 逻辑；
- 若能稳定出信号，再把 `15m` 状态降级成 `1m / 3m` execution gate；
- 不要在尚未确认“会不会开火”之前，就急着做更快级别的迁移。

## 8. 我对这条材料的结论

### 8.1 值得 intake 吗？
**值得，但只能作为“待修的 raw alpha 壳” intake。**

### 8.2 现在能直接当完整策略复现吗？
**不能。**

原因非常具体：

1. repo 简介 / README / 代码三套参数不一致；
2. `min_edge`、`ADX`、`1h bias` 等 claim 没有在代码里落地；
3. recent 90d probe 显示 `0` trades；
4. `run_backtest()` 本身还要求先手工生成信号列，复现链条不够自洽。

### 8.3 最准确的 desk 化定位

我会把它定位成：

> **趋势 raw alpha 的“代码审计优先级高于回测优先级”的候选。先修 canonical spec，再谈收益。**

## 9. 下一步怎么测

### 实验 A：先做 canonical spec 对齐，不要继续在三套规则上空转

第一步不是调参，而是统一规范：

- 到底用 `ST(10,3)/(21,2)` 还是 `ST(8,2.5)/(18,2)`？
- 到底 risk per trade 是 `1%` 还是 `2.5%`？
- `ADX` 和 `fee-adjusted edge` 到底是策略一部分，还是 README 装饰？

如果这一步不做，后面的任何回测都没有意义。

### 实验 B：把 repo 的 SuperTrend 实现和 canonical 版本逐 bar 对账

这是下一步最重要的技术实验。

最小口径：

- 标的：`BTCUSDT 15m`
- 区间：最近 `90d`
- 对比：repo 当前实现 vs TradingView / `pandas-ta` / 自己重写的 canonical SuperTrend
- 核对指标：
  1. bull/bear flip 次数
  2. 每次 flip 的时间戳是否一致
  3. `st_fast_dir` / `st_slow_dir` 的持续段长度

通过条件不是 PnL，而是：

> **在主流币 90d 样本里，翻转次数不能只有 2~3 次这种“近乎冻结”的状态。**

### 实验 C：若 canonical 化后恢复 signal density，再补一次真实 cost backtest

只有当 signal density 恢复正常，才值得继续做下一层：

- 成本：`4 / 8 / 12 bps` round-trip
- 标的：`BTC / ETH / SOL / BNB`
- 风险：`1% / 2.5%`
- hold：`10 / 20 / 30` bars

重点不是追最高 Sharpe，而是回答：

> **这条 trend alpha 在主流币 `15m` 上扣成本后有没有连续存活的 pocket。**

### 实验 D：若 `15m` 成立，再做 `5m` 保时长迁移

迁移第一版我会只做一件事：

- fast / slow / EMA / hold 全部按时间长度等比下放到 `5m`
- 不改 alpha 定义，不混入别的 filter

目的：

> 先判断“这条 alpha 的时钟是否可细化”，而不是一上来就把它改造成另一条策略。

## 10. 参考资料

1. **jaswanthobbu645-hub. (2026). _tightened-supertrend-alpha_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/jaswanthobbu645-hub/tightened-supertrend-alpha>  
   - Repo URL: <https://github.com/jaswanthobbu645-hub/tightened-supertrend-alpha>

2. **Repo source files used in this digest**  
   - README: <https://raw.githubusercontent.com/jaswanthobbu645-hub/tightened-supertrend-alpha/main/README.md>  
   - Strategy code: <https://raw.githubusercontent.com/jaswanthobbu645-hub/tightened-supertrend-alpha/main/src/strategy.py>  
   - Methodology: <https://raw.githubusercontent.com/jaswanthobbu645-hub/tightened-supertrend-alpha/main/docs/METHODOLOGY.md>

3. **Binance Spot API documentation / market data path used in portability probe**  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Kline docs: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>  
   - Endpoint used: <https://api.binance.com/api/v3/klines>
