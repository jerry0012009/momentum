# 别把这个 2026 高星 Binance Futures bot 只读成“又一组指标拼接”：对 short-cycle crypto desk，更该先拆的是「StochRSI 极值回摆 × RSI 方向约束 × MACD 相位翻转」这条 pullback-continuation raw alpha
- 时间：2026-04-23 05:48 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `TradingStrats.py` + `LiveTradingConfig.py`）+ Binance USDⓈ-M public-data portability probe（8 liquid majors，`15m/5m`，近约 `1200` bars）
- 主题类型：raw alpha
- 基础 alpha：**不是看到超卖/超买就反手，而是只在“更大方向仍站在你这边”时，接极值后的相位翻转：上行里接 oversold 回摆做 continuation，下行里接 overbought 回摆做 continuation。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / single-asset / trend-pullback / continuation / stochrsi / macd / rsi / oscillator-confluence / 15m / 5m / repo / public-data / cost / risk
- 证据类型：repo source 证据 + public-data portability probe

## 1. 这次看了什么
这次看的不是论文，而是一个 **2026 新仓库**：`thomasdutraa07/Trading-Bot-for-Binance-Future`。它表面上是一个 Binance Futures 多策略 bot，但如果只把它当“11 个策略菜单”，信息密度其实被浪费了。

这轮我挑出来的不是仓库默认主推的 `tripleEMAStochasticRSIATR`，而是一个对我们 desk 更像 **可独立最小实验** 的旁支策略：`StochRSIMACD`。

先把 base alpha 说清楚：**它不是裸 reversal，也不是裸 trend-following；它要抓的是“趋势中的极值回摆结束点”。**
- 多头：StochRSI 先进入极低区，随后出现向上 cross；但只有当 **RSI 仍在 50 上方**，且 **MACD 刚翻到 signal 上方** 时才准入。
- 空头：StochRSI 先进入极高区，随后出现向下 cross；但只有当 **RSI 仍在 50 下方**，且 **MACD 刚翻到 signal 下方** 时才准入。

这其实是一个很 desk-friendly 的思路：**把 oscillator 极值当“pullback 已接近结束”的候选，但用 RSI 与 MACD 把它限制在顺大方向的一侧。**

## 2. 源码里真正值得保留的东西
仓库里 `TradingStrats.py::StochRSIMACD()` 的逻辑很直接，适合快速移植：
1. 先检查过去 0~3 根里是否出现过 **StochRSI 极值**（多头 `<20`，空头 `>80`）；
2. 当前根要求 **MACD 与 signal 刚发生方向翻转**；
3. 同时要求 **RSI 站在 50 的趋势同向一侧**；
4. 还会避免 oscillator 已经跑到另一端，例如多头时当前 `fastd/fastk` 不能已经冲到 `>80`。

这几个约束叠在一起后，策略表达出来的不是“超卖就买”，而是：
- **上行趋势里的短时过冲回撤结束** → 再顺趋势接回去；
- **下行趋势里的短时过冲反弹结束** → 再顺趋势接回去。

所以它更接近 **trend pullback continuation**，而不是均值回复主壳。

## 3. 为什么它值得进当前素材池
它有 3 个实际优点：

### 3.1 base alpha 很清楚
这条东西的 base alpha 可以一句话说完：
**“趋势没坏，只是局部过冲；等 oscillator 从极值回摆、MACD 相位确认，再顺趋势接续。”**

这比很多“指标拼接策略”更重要——因为能一句话说清 base alpha，才配当 raw alpha 候选。

### 3.2 适合 `15m` 生成信号、`5m` 做 child execution
它天生不是超高频 LOB alpha，更像 `15m` parent decision：
- `15m` 用来等 pullback 完成；
- `5m` 用来控制追价、分批、maker-first / taker fallback。

这跟我们当前 desk 的结构很贴：**不要强迫 `5m` 直接承担全部预测任务。**

### 3.3 仓库本身就带了完整策略壳
`LiveTradingConfig.py` 已经给出：
- leverage
- order size
- max positions
- timeframe
- trailing stop
- 多种 TP/SL 模式（`%` / `ATR` / `Swing`）

所以它不是“只有 entry 没有壳”的半成品。即便 alpha 本身还要再校准，**策略落地接口已经足够完整**。

## 4. 最小 portability probe：这条 alpha 在 Binance `15m/5m` 上有没有留下边
我用 Binance USDⓈ-M 公共 K 线，对 `BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK` 做了一个轻量 probe。

口径：
- 只复刻 `StochRSIMACD` 的 **入场判定**；
- 出场先不复刻仓库里复杂 bracket，而是用 **固定 hold bars** 看信号本身有没有方向性；
- 检查 `5m` 与 `15m`，并对 `hold=2/4/6 bars` 做对照。

### 关键结果
**1）`15m` 明显比 `5m` 更像主信号时间框架。**
- `15m, hold=2`：平均约 **`+7.55 bps/笔`**，胜率 **`55.0%`**
- `15m, hold=4`：平均约 **`+7.67 bps/笔`**，胜率 **`53.5%`**
- `15m, hold=6`：平均约 **`+3.38 bps/笔`**，胜率 **`51.2%`**

**2）`5m` 只在很短持有期还有点味道，拉长就塌。**
- `5m, hold=2`：平均约 **`+1.99 bps/笔`**
- `5m, hold=4`：平均约 **`-1.76 bps/笔`**
- `5m, hold=6`：平均约 **`-2.71 bps/笔`**

**3）这条 alpha 更像“短持有 pullback continuation”，不是长拖仓趋势系统。**
- `15m` 上 `hold=2~4` 明显优于 `hold=6`
- 说明 edge 更集中在 **回摆刚结束后的前几根 bar**，不是“买完一路拿很久”那种壳

### 横截面观感
- `ADA 15m`、`SOL 15m`、`XRP 15m` 这轮表现相对更干净；
- `ETH/LINK 15m` 并不稳，说明这不是“所有主流币无脑通吃”的 universal rule；
- 所以更像一个 **single-asset family shell + symbol router**，而不是全市场同权硬铺。

## 5. 当前 verdict
### 结论先说
**这条东西值得收进 raw alpha 素材池，而且优先定位成：`15m` parent signal 的 pullback-continuation alpha。**

但我不建议把它直接写成“`5m` 高频策略”：
- `5m` 上如果只按信号本体硬打，edge 不够厚；
- `15m` 上信号有味道，`5m` 更适合拿来做 child execution，而不是自己当主预测层。

换句话说，这条东西的合理落位是：
- **主 alpha**：`15m` StochRSI 极值回摆 × RSI 50 同向 × MACD 相位翻转
- **执行层**：`5m` 控追价 / maker-first / 分批 / time-stop

## 6. 怎么把它落成完整策略
一个最小可交易壳可以这么写：

### Entry
- parent timeframe：`15m`
- long 条件：
  - 最近 `0~3` 根出现过 `StochRSI < 20`
  - 当前 `fastk > fastd`
  - `RSI > 50`
  - `MACD > signal` 且刚完成 bullish flip
- short 对称

### Exit
先从最朴素版本开始：
- 主版 time-stop：持有 `2~4` 根 `15m`
- 保护性止损：`1.2~1.8 x ATR(14)`
- 止盈：先试 `0.8~1.2 x ATR(14)` 或 `1R`
- 若 `MACD` 再次反向 flip，可提前平仓

### Sizing / Risk
- 单标的单次风险预算固定；
- 同时持仓数上限 `3~5`；
- 若同一时刻多币同向触发，优先保留：
  - 波动成本更低的币
  - 最近同类信号 markout 更好的币
- 回避 funding / spread / 滑点异常时段

### Cost
这条 alpha 不是超厚边，所以成本不能随便放：
- `15m hold=2~4` 的 gross edge 还行；
- 但如果 child execution 做得差，很容易把 edge 吐回去；
- 所以它天然要求 **maker 优先、追价上限、时间止损**。

## 7. 下一步怎么测
必须继续往下压的，不是“再看一遍指标图”，而是这 4 个测试：

1. **把 `15m` 信号 + `5m` 执行拆开测。**  
   不要再把 `5m` 当主信号；改成：`15m` 触发后，在接下来 `1~3` 根 `5m` 里测试 maker-first / taker fallback / limit-chase 的 markout。

2. **做 symbol router。**  
   当前 probe 已经说明币种间差异很大。下一步不是全铺，而是测：哪些币在这条 alpha 上稳定、哪些只是样本噪声。

3. **给它补一个简单 regime veto。**  
   例如只在 `EMA50` 同向、或 `ADX` / realized vol 不过热时放行，看是否能减少那些“极值回摆失败、直接继续反向扩张”的烂单。

4. **把 fixed-hold 换成 bracket + early-failure exit。**  
   先测 `ATR` 止损 + `1R` 止盈，再加“入场后 `2` 根内若未走出正向扩张则撤退”的 time-fail 逻辑。

## 8. 风险与保留意见
- 这轮优先验证的是 **signal portability**，不是完整逐笔成交仿真；
- 当前样本窗不长，且只覆盖 8 个 liquid majors；
- 仓库是多策略 bot，`StochRSIMACD` 只是其中一支，后续仍要避免“把参数表抄过来就当复现完成”。

但即便如此，这轮已经足够回答最关键的问题：
**它是不是一个能一句话讲清、能快速独立复现、而且在 `15m` 上确实留下方向边的 raw alpha 候选？**

我的答案是：**是。**

## 9. 来源
### Repo metadata
- Authors / Owner: `thomasdutraa07`
- Year: `2026`（repo created `2026-01-02`）
- Title: *Trading-Bot-for-Binance-Future*
- Venue: GitHub repository
- DOI: N/A
- Readable URL: `https://github.com/thomasdutraa07/Trading-Bot-for-Binance-Future`
- Repo URL: `https://github.com/thomasdutraa07/Trading-Bot-for-Binance-Future`

### Inspected files
- README: `https://raw.githubusercontent.com/thomasdutraa07/Trading-Bot-for-Binance-Future/main/README.md`
- Strategy source: `https://raw.githubusercontent.com/thomasdutraa07/Trading-Bot-for-Binance-Future/main/TradingStrats.py`
- Config source: `https://raw.githubusercontent.com/thomasdutraa07/Trading-Bot-for-Binance-Future/main/LiveTradingConfig.py`

### Local artifact
- Probe script: `reports/artifacts/quant_digests/2026-04-23_stochrsi_macd_repo_probe.py`
- Probe result CSV: `reports/artifacts/quant_digests/2026-04-23_stochrsi-macd-pullback-probe.csv`
