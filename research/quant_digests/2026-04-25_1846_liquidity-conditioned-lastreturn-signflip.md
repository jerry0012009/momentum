# 别把这篇 2021 liquidity 论文只读成“日频 reversal 统计”：对 short-cycle crypto desk，更该先回答的是「同样是过去 24h 涨跌，liquid majors 和更广币池到底该顺着做还是反着做」

- 时间：2026-04-25 18:46 UTC
- 类型：2021 论文 metadata / abstract audit（OpenAlex + Crossref）+ Binance Spot public-data portability probe（`1h` parent / `24h` lookback，`20` 币固定 universe）
- 主题类型：raw alpha
- 基础 alpha：**横截面里，过去一段时间跌得最狠的币，后面未必继续弱；在某些 liquidity bucket 里反而更容易反弹，而另一类 bucket 里则可能继续延续。换句话说，alpha 不是“单纯 momentum”或“单纯 reversal”，而是“last-return sign conditioned on liquidity”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（至少可落成一个 parent alpha shell；子执行与成本仍需另补）
- 主题标签：raw-alpha/cross-sectional/relative-value/momentum/mean-reversion/liquidity-conditioned-sign-flip/24h-return/1h-parent/15m-child/paper/public-data/cost/risk
- 证据类型：论文证据 + public-data portability probe

## 1. 先回答：这篇东西的 base alpha 是什么？
这篇材料的 **base alpha 不是“liquidity 因子”本身**，也不是纯解释型市场结构。

它真正的 raw alpha 是：

> **把横截面里“刚刚涨过 / 刚刚跌过”的币分开看，下一段该跟还是该反着做，取决于它处在哪个 liquidity bucket。**

翻成人话：
- 同样是“过去 24h 大涨/大跌”，
- 有些币更像会继续走，
- 有些币更像会回吐 / 反弹，
- **liquidity 决定的是这个信号该取 momentum 号，还是取 reversal 号。**

所以它不是纯 filter；它是一个 **可交易的 cross-sectional raw alpha router**。

---

## 2. 这次看了什么
主来源是一篇 published paper：

- **Authors**：Adam Zaremba, Mehmet Hüseyin Bilgin, Huaigang Long, Aleksander Mercik, Jan Jakub Szczygielski
- **Year**：2021
- **Title**：*Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets*
- **Venue**：*International Review of Financial Analysis*
- **DOI**：`10.1016/j.irfa.2021.101908`
- **Readable URL**：<https://doi.org/10.1016/j.irfa.2021.101908>
- **OpenAlex entry**：<https://openalex.org/W3206440720>（若 URL 失效，可按 DOI 搜）
- **Repo URL**：无

OpenAlex abstract 给出的核心结论很清楚：
- 基于 **3600+ coins** 的日频样本，
- **前一日跌得更多的币，后面显著跑赢前一日涨得更多的币**；
- 但作者进一步认为，这个现象主要来自 **大量低流动性币的 illiquidity reversal**；
- 少数 **largest / most tradeable coins** 反而更偏向 **momentum**，不是 reversal。

也就是说，这篇 paper 真正有价值的地方，不只是“crypto 里有 reversal”，而是：

> **同一个 `last return` 信号，在不同 liquidity bucket 里可能要反着解释。**

这很适合做 desk 的 alpha router 素材。

---

## 3. 为什么这题值得优先于继续堆别的 breakout / pairs
因为它补的是一个很基础、但对实盘特别关键的问题：

> **“上一段涨跌”这个最朴素的信号，到底该顺着做还是反着做？**

如果这个问题没答清：
- 你做横截面轮动时，可能把本该 reversal 的东西当 momentum；
- 你做 loser/winner spread 时，可能把 short leg 放在最不该 short 的 bucket；
- 你把一个 signal 下沉到 `15m/5m` 时，也可能把 parent alpha 的方向用反。

它跟我们已有材料的区别是：
- 之前更像是在回答 **不同 horizon / bucket 会不会换符号**；
- 这篇更明确地把 **liquidity** 点名成 sign flip 的候选主因；
- 所以它更像一个 **“怎么给 cross-sectional alpha 决定方向”** 的结构件。

---

## 4. 论文核心结论，翻成人话
论文 abstract 的核心信息可以压成四句：

1. **看“前一天涨跌”就已经有预测力。**
2. 在更广、更杂、流动性更差的币池里，**昨天跌得多的，今天更容易反弹**。
3. 这种 reversal 不是因为它天生高明，而更可能是因为 **illiquidity / temporary price pressure**。
4. 真正最大、最好交易的少数币，**不一定走 reversal，反而更像 momentum**。

所以它不是一句“crypto 有 reversal”就结束，而是：

> **last-day return 是个很强的 predictor，但必须先回答“你在对谁用”。**

---

## 5. 策略拆解（必填）
### Base alpha
- `cross-sectional last-return continuation/reversal`
- 也可以写成：`liquidity-conditioned winner/loser sign router`

### Entry
- 每个 rebal 时间点，计算过去一段窗口（论文是 `1d`；short-cycle 版本可先用过去 `24h`）的横截面收益；
- 在某个 liquidity bucket 内做排序；
- 若该 bucket 被定义为 reversal bucket：`long losers / short winners`；
- 若该 bucket 被定义为 momentum bucket：`long winners / short losers`。

### Exit
- 固定持有 `1h / 4h / 8h / 24h` 做第一轮 parent 测试；
- 真要下沉到 short-cycle，可改为 `1h parent` 选币 + `15m` child 执行。

### Sizing
- bucket 内等权；
- 或者 inverse-vol / dollar-neutral；
- 实盘先限制单币权重上限，避免 illiquid tails 把组合拖翻。

### Risk / cost
- 先做 long-short market-neutral 口径，避免把 beta drift 误当 alpha；
- 真实交易前必须补：成交额门槛、最小日均成交量、单币权重 cap、借币 / short 可得性、child execution 成本。

---

## 6. 我做的最小 portability probe
### 6.1 数据与口径
因为论文是日频广覆盖样本，但我们服务的是 short-cycle crypto desk，所以我先做了一个 **诚实但收敛的 parent-alpha 快检**：

- 数据源：Binance Spot public klines
- 公开性：公开可得，无 key
- 更新频率：`1h`
- universe：固定 `20` 币
  - **liquid majors**：`BTC ETH SOL XRP BNB DOGE ADA TRX LINK AVAX`
  - **较次一级 liquid mids**：`LTC DOT ATOM ETC BCH UNI APT FIL AAVE NEAR`
- 样本：最近 `1000` 根 `1h` bar（约 `2026-03-15 ~ 2026-04-25`）
- signal：过去 `24h` 收益排序
- 组合：每次 `long bottom-2 / short top-2`（reversal）或反过来（momentum）
- 持有：`1h / 4h / 8h / 24h`
- 说明：这一步先看 **signal sign**，还没扣真实交易成本；它是 parent alpha 快检，不是可直接实盘的最终回测。

### 6.2 结果
#### A) liquid majors bucket（10 币）
- **reversal, hold 1h**：平均 **`+2.7 bps/次`**，hit `52.0%`，t≈`2.33`
- **reversal, hold 4h**：平均 **`+10.7 bps/次`**，hit `55.3%`，t≈`4.30`
- **reversal, hold 8h**：平均 **`+19.5 bps/次`**，hit `54.0%`，t≈`5.21`
- **reversal, hold 24h**：平均 **`+50.5 bps/次`**，hit `54.4%`，t≈`7.95`

对应的 **momentum 版本在 liquid majors 上是镜像为负**：
- `4h`：`-10.7 bps/次`
- `8h`：`-19.5 bps/次`
- `24h`：`-50.5 bps/次`

#### B) 次一级 mids bucket（10 币）
- 不论做 momentum 还是 reversal，结果都接近 0，显著性弱：
  - **momentum, hold 4h**：`+3.0 bps/次`，t≈`0.84`
  - **reversal, hold 4h**：`-3.0 bps/次`
  - **momentum, hold 24h**：`+7.5 bps/次`，t≈`0.88`
  - **reversal, hold 24h**：`-7.5 bps/次`

### 6.3 这组结果最重要的含义
这一步给我的结论，不是“论文错了”，而是：

1. **论文的日频广覆盖结论，不能直接当成 liquid-major intraday 结论来抄。**
2. 在我们更关心的 **可交易 majors** 里，最近这段样本下，`过去24h涨跌` 在 `1h->4h/8h/24h` 上更像 **reversal**，不是 momentum。
3. 在我选的这组 mid bucket 里，信号反而不够厚，说明 **“流动性越差越强 reversal”** 这个故事，落到可交易 Binance 实盘 universe 时未必自动成立。

翻成人话：

> **这篇 paper 对 desk 最有用的，不是“照抄 low-liquidity reversal / high-liquidity momentum”这句结论，而是保留它的方法论：先按 liquidity 分桶，再决定同一个 last-return signal 到底取 momentum 号还是 reversal 号。**

---

## 7. 和 `1m / 3m / 5m / 15m` 的关系
它不是天然逐笔 micro alpha，但很适合做 **parent alpha / router**：

- `1h` 评估过去 `24h` 横截面强弱；
- 决定某个 bucket 当前该走 `loser->winner fade` 还是 `winner continuation`；
- 再把具体入场拆到 `15m` / `5m`：
  - 例如只在 child bar 的 pullback / spread 收窄时成交；
  - 或只在 child microstructure 不恶化时开仓。

所以它最自然的定位不是“`1m` 主信号”，而是：

> **给 short-cycle cross-sectional 策略提供一个方向路由器。**

---

## 8. 下一步怎么测
### 最小可复现实验（下一轮应优先做）
1. **做 rolling liquidity bucket**，不要只用固定 20 币名单。  
   - 用最近 `7d/14d` 的 dollar volume 动态分 bucket；
   - 看 sign flip 是否稳定，而不是被静态名单偶然决定。

2. **把 parent / child 分开。**  
   - parent：每 `1h` 计算过去 `24h` 横截面 return；
   - child：在 `15m` 上只做更便宜的分批执行；
   - 核心指标：`implementation shortfall` 是否把 parent 的 edge 吃光。

3. **补 cost ladder。**  
   - 先粗扣 `4/8/12/16 bps` round-trip；
   - 看 liquid-major reversal 在 `4h/8h` 上是否还能留下正 edge。

4. **分 long leg / short leg 归因。**  
   - 论文提示 reversal 可能主要由 loser 端驱动；
   - 要验证我们这里是不是也是 **long loser leg** 贡献了大部分 edge，short winner 只是拖累。

5. **加 funding / perp premium veto。**  
   - 若 parent alpha 搬到 perp，上层可再加 crowding veto；
   - 看能不能把“本来是反弹，但 crowding 已极端”的坏样本剪掉。

---

## 9. 这篇材料的最终 verdict
### 值得保留的部分
- **值得保留。**
- 不是因为它证明了某个固定方向永远有效，
- 而是因为它提醒我们：
  - `last return` 是强 predictor；
  - 但它的 **方向** 不是固定的；
  - **liquidity bucket 是决定方向的关键上下文。**

### 不该误读的部分
- 不要把它误读成：“crypto 就是做前一日 loser reversal。”
- 更不要误读成：“largest coins 一定是 momentum，illiquid coins 一定是 reversal。”

对我们这轮 public-data 快检，更诚实的表述是：

> **paper 提供的是“先分 bucket、再决定符号”的框架；而在最近 Binance 可交易 majors 上，`24h return` 到 `1h/4h/8h/24h` 的 parent 信号更像 reversal，不像 momentum。**

这正是它值得进研究池的原因：
- 它不是固定招式，
- 而是一个 **能直接服务多个 cross-sectional alpha 的 sign router 母件**。

---

## 10. 来源
- Zaremba, A., Bilgin, M. H., Long, H., Mercik, A., & Szczygielski, J. J. (2021). *Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets*. *International Review of Financial Analysis*.
- DOI：`10.1016/j.irfa.2021.101908`
- Readable URL：<https://doi.org/10.1016/j.irfa.2021.101908>
- OpenAlex metadata / abstract：<https://openalex.org/W3206440720>
- Repo URL：无
