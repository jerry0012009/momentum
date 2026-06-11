# 别把这个 2025 新 repo 只读成“暴跌抄底神话”：对 short-cycle crypto desk，更该先回答的是「1h 急跌 × 成交量放大 × 24h bounce」这条 raw alpha 壳，到底能不能诚实地下沉到 `15m/5m`

- 时间：2026-04-25 17:36 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `src/strategy.py` + `src/backtester.py` + `results/backtest_results.csv` + `results/performance_metrics.json`）+ Binance USDⓈ-M public-data portability probe（`BTC/ETH/SOL/AVAX`，`1h` parent）
- 主题类型：raw alpha
- 基础 alpha：**单币在 1 小时内出现显著下跌，且这一下跌伴随成交量明显放大时，短期更容易出现“恐慌后反弹”；交易上对应 `price-shock mean reversion / oversold bounce`，再配上固定持有期与成本约束。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 给了完整壳；但对子周期可移植性仍要诚实降级）
- 主题标签：raw-alpha/single-asset/mean-reversion/price-shock/volume-spike/oversold-bounce/fixed-hold/1h/24h/15m/5m/repo/public-data/cost/risk
- 证据类型：repo source audit + repo result audit + public-data portability probe

## 1. 先回答：这篇东西的 base alpha 是什么？
这次不是在讲“volume confirmation”这种纯过滤层，也不是在讲“止损怎么设”这种 overlay。

**base alpha 很清楚：**
> 当某个币在很短时间内出现明显下跌，而且这一下跌不是安静地下去，而是带着明显放大的成交量时，市场更可能处在短时恐慌 / 过度反应状态；后面 8~24 小时更容易出现反弹。

所以它属于 **raw alpha / 可落地完整策略壳**，不是单纯的 filter。

---

## 2. 这次看了什么
主来源是 GitHub 仓 `skylarshi123/crypto-stat-arb`。虽然 repo 名字叫 stat-arb，但它真正实现的不是经典 pairs，而是一条很直白的 **单币 oversold bounce**：

- `1h return <= -2%`
- 同时 `当前成交量 >= 过去 24h 平均成交量的 1.5x`
- 做多
- 持有 `4 / 8 / 12 / 24h`
- round-trip 成本固定按 `40 bps` 扣减（作者写成每边 20 bps）

来源信息：
- Author / Year / Title / Venue：Skylar Shi (2025), *Cryptocurrency Statistical Arbitrage Strategy*, GitHub repo
- Repo URL：<https://github.com/skylarshi123/crypto-stat-arb>
- Readable URL（README）：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/README.md>
- 关键实现：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/src/strategy.py>
- 回测逻辑：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/src/backtester.py>
- 结果文件：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/results/backtest_results.csv>
- 指标汇总：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/results/performance_metrics.json>
- DOI / Venue：无（repo 项）

这类 repo 对当前 desk 有价值，不是因为“结果看起来很猛”，而是因为它把一个很常见、但经常只停留在口头的假设，写成了完整可执行壳：
- signal 定义清楚
- 持有期清楚
- 成本口径清楚
- 输出 trades / metrics 也齐全

---

## 3. 一句话结论
- **一句话核心结论：** 这份 repo 值得保留进素材池，因为它把「急跌 + 放量后的短时反弹」写成了一条可独立复现的 raw alpha 壳；但用 Binance USDⓈ-M 公共数据做更长样本诚实快检后，结论变成：**只有 `24h` 持有在成本后还勉强为正，`4h/8h/12h` 都是负的**，所以它更像 `1h parent -> 8~24h bounce`，而不是可直接下沉成 `15m/5m` 主信号。
- **翻成人话：** “暴跌后会弹一下”这件事不是完全胡扯，但真正能留下来的 edge 更慢、更吃持有期；你要是想直接拿去做 `5m` 抄底，多半会先被噪音和手续费狠狠干掉。

---

## 4. repo 自己是怎么证明它有效的
repo 的信号定义写在 `src/strategy.py` 里，核心阈值非常朴素：
- `price_drop_threshold = -0.02`
- `volume_ratio_threshold = 1.5`
- `volume_lookback_hours = 24`

也就是：
- 过去 1 小时跌幅至少 `-2%`
- 当前成交量至少是过去 `24h` 均量的 `1.5x`

回测器 `src/backtester.py` 再去测试 `4 / 8 / 12 / 24h` 固定持有期，并显式扣掉 `40 bps` round-trip 成本。

repo 自带 `results/backtest_results.csv` 的结论是：
- `4h`：`25` 笔，net `-12.60%`，胜率 `24.0%`
- `8h`：`23` 笔，net `-17.60%`，胜率 `39.1%`
- `12h`：`23` 笔，net `-0.38%`，胜率 `47.8%`
- `24h`：`22` 笔，net `+34.33%`，胜率 `72.7%`

`results/performance_metrics.json` 进一步把 `24h` 持有写成：
- total return：`34.33%`
- avg trade return：`1.56%`
- win rate：`72.7%`
- max drawdown：`8.24%`
- num trades：`22`
- sample：`20` 个交易日、`2,884` 个小时数据点

repo 想传达的意思很直接：
> 不是所有下跌都值得接，但“急跌 + 放量”的那类更像短时过冲；反弹不是马上发生，而更像在 `24h` 附近才真正长出来。

---

## 5. 为什么这和当前 desk 有关
这条线符合本轮最重要的优先级：

1. **它是 raw alpha，不是纯解释。**
2. **它能独立复现，不依赖难拿的外部数据。**
3. **entry / exit / cost 都很清楚。**
4. **它自然连接我们现在更该补的 mean reversion 素材池。**

更重要的是，它还补了最近研究里的一个缺口：
- 我们已经看过很多 `cross-sectional loser→winner fade`、`pairs spread fade`、`OFI microburst`；
- 但“**单币 price-shock bounce**”这种更朴素、可直接当 desk 原料的东西，反而没在今天这轮 intake 里单独拆清楚。

所以这题比继续去绕旧 breakout / 旧 queue 派生方向更值。

---

## 6. 策略拆解（必填）
### Base alpha
- `price-shock mean reversion / oversold bounce`
- 本质上是在赌：急跌时的被动砍仓、恐慌成交、短时失衡，会在后面一段时间里回补一部分。

### Regime
- 更适合：
  - 非灾难级单边崩盘，而是“短时过冲、随后回归”的环境
  - 流动性较好、反身性较强的主流币
- 不适合：
  - 真正的 news-driven trend day
  - 连续踩踏、单边失速的 regime

### Filter / veto
- repo 自带的 `volume spike` 其实就是第一层 filter：
  - 没有放量的跌，不一定是恐慌，可能只是正常波动
- 对 desk 来说还可再加：
  - funding / OI crowding veto
  - 不接重大事件后的第一刀
  - 只做日内 realized vol 极端但非连续崩盘的样本

### Risk / sizing / execution overlay
- repo 用固定 round-trip `40 bps`
- 当前更合理的实盘化版本应该补：
  - maker / taker 分层
  - 波动率缩放仓位
  - 同时信号数上限
  - time-stop + failure-to-bounce stop

---

## 7. repo 结果里最值得信、也最该怀疑的地方
### 值得记住的部分
repo 至少诚实地证明了一件事：
- **持有期是关键超参数，而且短持有并不工作。**

这是很有价值的，因为很多“抄底反弹”直觉会默认：
- 跌完马上弹
- 最多几根 K 就结束

但 repo 给出的恰好是反过来的图景：
- `4h/8h` 不行
- `12h` 接近打平
- `24h` 才明显转正

### 最该怀疑的部分
但 repo 的证据强度也有限：
1. 样本很短，只有 `20` 个交易日；
2. universe 很小，只看 `BTC / ETH / SOL / AVAX`；
3. 成本口径虽有，但仍然是统一常数，不是更真实的流动性分层；
4. README 把它包装成 “stat-arb”，其实更像单币反转，不要被命名误导。

所以 repo 更像一个 **高信号研究起点**，不是可以直接照搬的生产 verdict。

---

## 8. 我的 public-data portability probe（关键）
我补了一个更诚实的快检：
把 repo 同样的规则，直接映射到 Binance USDⓈ-M 公共 `1h` K 线上，扩样本看它是不是只是一段短期巧合。

### 8.1 数据与口径
- 数据源：Binance USDⓈ-M public klines
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / AVAXUSDT`
- 区间：`2025-12-01 ~ 2026-04-25`
- parent 频率：`1h`
- 信号：
  - `1h return <= -2%`
  - `volume / rolling_24h_avg >= 1.5`
- 持有期：`4 / 8 / 12 / 24h`
- 同一币不重叠持仓
- 成本：round-trip 固定 `40 bps`

### 8.2 结果
本地快检结果如下：

- `4h`：`106` 笔，gross `-35.19%`，net `-77.59%`，胜率 `33.0%`
- `8h`：`100` 笔，gross `-17.29%`，net `-57.29%`，胜率 `41.0%`
- `12h`：`96` 笔，gross `+6.19%`，net `-32.21%`，胜率 `44.8%`
- `24h`：`93` 笔，gross `+53.90%`，net `+16.70%`，胜率 `48.4%`

对应的直觉解读是：
1. **短 bounce 不稳定。** `4h/8h` 不是“被成本吃掉”，而是 gross 就已经明显偏负；
2. **12h` 仍然不够。** gross 微正，但 net 仍为负，说明 edge 很薄；
3. **24h` 还有一点活口。** 但优势远没有 repo 自带结果那么夸张；
4. **这条线不是高胜率抄底，而更像低到中胜率、靠右尾反弹撑回报。**

这比 repo README 那个“72.7% 胜率”更接近 desk 该接受的现实口径。

---

## 9. 这组快检真正说明了什么
最重要的结论不是“repo 错了”，而是：

> **这条 alpha 存在，但它更像 `1h parent shock -> 24h rebound`，不太像 `15m/5m` 直接可交易的主信号。**

也就是说，它对当前 short-cycle desk 的正确读法不是：
- “以后看到 15m 暴跌就去接”；

而是：
- “把 1h shock 当父级别事件，再去看 `15m/5m` 能不能做更便宜、更干净的 child execution。”

这和我们最近不少 digest 的结论一致：
- 很多 alpha 的 **方向判断** 可以在慢级别成立；
- 但真正要下到短周期，常常应该下沉的是 **入场优化 / execution veto**，而不是把父级别信号硬压缩成更快主信号。

---

## 10. 对当前 desk 最有价值的读法
所以这篇 digest 最值得保留到素材池里的，不是“volume spike 证明抄底有效”，而是下面这句：

> **急跌 + 放量 这套逻辑可以保留成 mean-reversion 父级别事件标签，但短周期 desk 应优先研究的是 `shock-parent / child-entry` 结构。**

可直接复用的部分：
- `-2% in 1h` 这种 event 定义
- `volume ratio >= 1.5` 这种朴素放量条件
- `24h` 左右才显著优于更短持有期的经验
- 同币不重叠持仓的 state rule

不该直接照抄的部分：
- 把它包装成“高胜率 stat-arb”
- 直接下沉成 `5m` 抄底主策略
- 无脑认为 volume spike 一定是利多 bounce

---

## 11. 最小实验怎么做
如果下一轮要真把它推进到 desk 可验证层，我建议做下面这个最小实验：

### 方案：`1h shock parent -> 15m child entry`
1. **父事件定义**
   - `1h return <= -2%`
   - `1h volume ratio >= 1.5`

2. **子级别执行（15m 或 5m）**
   只在父事件出现后的接下来 `2~8` 根子 bar 里找入场：
   - 第一种：跌势停止、出现第一次 higher low
   - 第二种：重新站回短均线 / VWAP
   - 第三种：微观成交冲击衰减后再接

3. **退出规则**
   - `time-stop = 8h / 12h / 24h`
   - 或者回补到父事件跌幅的一定比例就出

4. **成本分层**
   - `2 / 4 / 6 bps` 三档
   - maker-first 与 taker-only 分开看

这样做，才能回答 desk 真正关心的问题：
- 这条 alpha 的 edge 在哪里？
- 是事件标签本身有用，还是只是“持久反弹”这个更慢逻辑有用？
- short-cycle execution 能不能把它从薄 edge 变成可交易 edge？

---

## 12. 下一步怎么测（必须）
下一步最值得直接测这 4 件事：

1. **把 fixed-hold 改成 child-execution 结构。**  
   不是信号出来就立刻接，而是只把 `1h shock` 当事件标签；真正入场放到 `15m/5m`。

2. **把 `-2%` 阈值做成按币种波动分位数自适应。**  
   BTC 的 `-2%` 跟 AVAX 的 `-2%` 不是同一件事；更合理的是用 rolling vol / ATR 标准化 shock。

3. **把 volume spike 拆成“恐慌成交”与“趋势启动”两类。**  
   例如加上 funding、OI、CVD、连续大阴线数量，区分这次放量到底更像 capitulation 还是 trend continuation。

4. **先只做多、先砍掉最差 regime。**  
   对这类 bounce 信号，真正该避免的不是“错过一点利润”，而是接在真正持续崩盘里。先加 regime veto，比盲目调参数更重要。

---

## 13. 风险与边界
- 这条线目前**不是**可以直接上线的 `5m/15m` 主 alpha；
- repo 自带结果偏亮眼，但扩样本后明显降温；
- 这类策略最大的风险不是“胜率低一点”，而是接到真正的崩盘延续；
- 如果没有 regime veto / child execution，它很容易从“反弹捕捉”变成“下跌接飞刀”。

---

## 14. 本地实验产物
- `reports/artifacts/quant_digests/2026-04-25_meanreversion_volspike_binance_portability_summary.csv`
- `reports/artifacts/quant_digests/2026-04-25_meanreversion_volspike_binance_portability_trades.csv`

如果后面要继续复现，这两个文件已经足够作为下一轮 `shock-parent / child-entry` 的起点。