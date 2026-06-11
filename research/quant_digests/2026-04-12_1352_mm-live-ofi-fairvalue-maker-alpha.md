# 别把 mm-live 只读成“Avellaneda-Stoikov 做市框架”：对 short-cycle desk，更该先拆的是「OFI × Kalman fair value shift」这条 raw alpha，但整套 maker 壳还不能直接宣称过线

- 时间：2026-04-12 13:52 UTC
- 类型：2026 GitHub repo source audit（GitHub API metadata + `README.md` + `scripts/collect_and_test_edge.py` + `scripts/run_benchmark.py` + `src/mm_live/signals/fair_value.py` + `src/mm_live/signals/imbalance.py` + `src/mm_live/strategy/quoting.py` + `src/mm_live/research/imbalance_prediction.py` + `src/mm_live/research/benchmark.py`）+ Binance live public-data probe（WebSocket `depth@100ms + trade`）
- 主题类型：raw alpha
- 基础 alpha：**订单簿买卖盘失衡（OFI / imbalance）会在接下来几百毫秒到几秒里继续影响 mid 的方向；repo 真正值得 desk intake 的，不是“会不会用 A-S 报价”，而是 `fair_value = Kalman(mid) + α·imbalance` 这条可检验的微观结构 alpha。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/microstructure/order-flow/OFI/kalman/fair-value/market-making/avellaneda-stoikov/inventory-risk/binance/btcusdt/100ms/500ms/1s/5s/1m/3m/repo/live-public-data/cost/risk
- 证据类型：真实源码仓库 + 可运行 live edge test + live benchmark

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = 短时订单簿失衡会推动未来 mid 朝同方向再走一小段。**

如果这句答不清，`mm-live` 最多只能算做市工程壳；但这轮 source audit 之后，我认为它的 base alpha 是清楚的：

- `src/mm_live/signals/imbalance.py` 明确把信号定义成：
  - top-N depth imbalance
  - `raw = (bid_vol - ask_vol) / (bid_vol + ask_vol)`
  - 再做 EMA 平滑
- `src/mm_live/signals/fair_value.py` 直接把 alpha 写进 fair value：
  - `fair_value = Kalman(mid) + imbalance_alpha * imbalance`
- `scripts/collect_and_test_edge.py` 不是只打印故事，而是**先采样，再回归检验 `imbalance -> future return`**。

翻成人话：

> 它赌的不是“长期趋势”，也不是“均线金叉”，而是 **盘口里买盘比卖盘更厚时，接下来很短一段时间价格更容易继续往上挪一点；反之亦然。**

这就是 raw alpha，本体非常明确。

## 2. 为什么这轮值得看它

### 2.1 它不是 README 驱动的假仓库
GitHub API 元数据显示：

- repo：`Aliipou/mm-live`
- 作者：**Ali Pourrahim**
- 创建：`2026-03-23`
- 最近更新：`2026-04-12`
- GitHub：<https://github.com/Aliipou/mm-live>
- stars：`3`

虽然 star 不高，但这轮它比很多 launcher / README-only 仓库强得多，因为它有：

- `src/mm_live/` 下完整模块分层
- `research/` 里的 edge test / benchmark / markout / stress test
- `risk/limits.py`、`execution/`、`feed/` 这些可审计源码
- `tests/` 目录，不是只有截图和口号

也就是说：

> **它不是“有人讲了一套故事”，而是“有人把信号、报价、风险、研究验证管线都写出来了”。**

### 2.2 它更像“alpha 先验 + 做市壳”，不是单纯 textbook A-S
README 虽然强调 Avellaneda-Stoikov，但真正能给 desk 拿走的东西不是公式本身，而是这条拆法：

1. 先证明短时 OFI 是否真的预测 future mid；
2. 再把这个 edge 塞进 fair value；
3. 再决定要不要把它变成 maker quote skew / directional filter / taker router。

这比很多“直接回测做市收益曲线”的 repo 更诚实。

## 3. repo 里最值得搬走的 4 个结构件

## 3.1 `imbalance.py`：alpha 本体很朴素，但定义够干净
`OrderFlowImbalance` 的核心非常简单：

- 看前 `depth_levels=5` 档；
- 计算 `(bid_vol - ask_vol) / (bid_vol + ask_vol)`；
- 用 `ema_alpha=0.2` 平滑；
- 输出范围在 `[-1, +1]`。

这点反而是优点。它没有一上来就堆复杂 ML，而是先回答：

> **盘口厚度偏向哪边，短时 drift 会不会跟着偏哪边？**

这是 desk 最容易复现、最容易二次加工的一类 microstructure alpha。

## 3.2 `fair_value.py`：repo 最关键的一句其实是这个
代码里直接写的是：

```python
fair_value = Kalman(mid) + imbalance_alpha * imbalance
```

默认 `imbalance_alpha = 2.0`。翻成人话：

- Kalman 负责把 noisy mid 先压平；
- imbalance 负责给这个 fair value 一个短时方向偏移。

所以这里真正的研究价值不是“Kalman 好不好看”，而是：

> **把盘口失衡从纯解释变量，提升成真正参与定价的 fair-value shifter。**

## 3.3 `quoting.py`：A-S 报价只是在给 alpha 找可执行外壳
`AdaptiveQuoteEngine` 里核心结构是：

- `reservation = fair_value - inventory * gamma * sigma^2 * T`
- `delta = ...`（A-S half spread）
- high vol widening
- imbalance skew
- inventory 到限时单边报价

也就是说，repo 的交易层不是在重新发明 alpha，而是在做三件事：

1. **把 raw alpha 变成 reservation price 偏移**；
2. **把库存风险压回去**；
3. **把 quote spread 做成 state-dependent，而不是死宽度。**

这对我们 desk 的启发是：

> OFI 可以单独做 directional alpha，也可以只做 maker 价格偏移；两者不要混成一团。

## 3.4 `research/imbalance_prediction.py`：先统计检验，再谈 production
这部分我很喜欢。它不是先讲 PnL，而是先做：

- 收集 `(timestamp, imbalance, mid)`
- 对 `100ms / 500ms / 1s / 5s` 做 `future_return ~ imbalance` 回归
- 输出 `r / R² / t-stat / p-value / beta`

这跟很多 repo 最大的区别是：

> **它先问“信号有没有预测力”，再问“策略能不能赚”。**

这很适合当前 desk 的 intake 节奏。

## 4. public live probe：alpha 本体是成立的，但完整 maker 壳暂时不能直接认领
本地 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/mm_live_ofi_edge_probe_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/mm_live_ofi_edge_probe_2026-04-12.json`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/mm_live_benchmark_probe_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/mm_live_benchmark_probe_2026-04-12.json`

### 4.1 我怎么测的
我没有只停在 README，而是实际做了两步 live probe：

#### Probe A：repo 自带 OFI edge test
环境：
- 本地 venv 安装 repo
- 运行：
  - `python scripts/collect_and_test_edge.py --duration 30 --symbol btcusdt`
- 数据：Binance 公共 WebSocket
  - `btcusdt@depth@100ms`
  - `btcusdt@trade`

#### Probe B：repo 自带 strategy benchmark
运行：
- `python scripts/run_benchmark.py --n-ticks 1000 --symbol btcusdt`

比较三条线：
- `AdaptiveQuoteEngine`
- `FixedSpreadMaker`
- `NaiveMaker`

注意：

> 这不是交易所真实成交回报。它是 repo 自己定义的同口径 live tick + fill simulation benchmark，所以能说明“相对可行性”，不能直接当真钱表现。

### 4.2 好消息：OFI 的短时预测力在这次 live probe 里非常明显
`30s` 的 BTCUSDT live probe，完成样本约 `1377` 个。结果：

- `100ms`: `r ≈ +0.554`, `R² ≈ 0.307`, `t ≈ 24.66`, `p ≈ 1.75e-111`
- `500ms`: `r ≈ +0.644`, `R² ≈ 0.414`, `t ≈ 31.17`, `p ≈ 7.92e-162`
- `1s`: `r ≈ +0.536`, `R² ≈ 0.287`, `t ≈ 23.53`, `p ≈ 3.87e-103`
- `5s`: `r ≈ +0.479`, `R² ≈ 0.229`, `t ≈ 20.23`, `p ≈ 7.64e-80`

最强的是 `500ms` 这一档。

翻成人话：

> **在这次实时样本里，盘口失衡不是噪音，而是真会在接下来几百毫秒到几秒里继续推着 mid 往同方向走。**

所以如果只问：

> `OFI × fair value shift` 这条 base alpha 存不存在？

我的答案是：**存在，而且这次 public live probe 证据不弱。**

### 4.3 坏消息：直接把它包成默认 maker 壳，这次短样本没跑赢 baseline
`1000` ticks live benchmark 的结果是：

- `FixedSpreadMaker`：`PnL ≈ -3.47`, `Sharpe ≈ -3881.82`, `197` fills
- `AdaptiveQuoteEngine`：`PnL ≈ -5.33`, `Sharpe ≈ -4425.44`, `373` fills
- `NaiveMaker`：`PnL ≈ -9.62`, `Sharpe ≈ -5092.36`, `447` fills

repo 自己也打印了：

> `WARNING: Model underperforms baseline`

这说明什么？

说明这次 probe 下：

1. **alpha 本体成立，不等于完整 maker 壳马上成立；**
2. `AdaptiveQuoteEngine` 的 spread 更窄（平均约 `4.40` 美元，对比 baseline 的 `10.0`），fill 更多，但短样本里 adverse selection / inventory path 可能更吃亏；
3. 至少不能因为 README 好看，就直接把它当“可上线完整策略”打勾。

所以这轮 4 个字段里，我把：

- `是否可独立复现` 写 **是**
- `是否可直接落地完整策略` 写 **否**

这是更诚实的写法。

## 5. 这东西和我们 `1m / 3m / 5m / 15m` 的关系是什么？
它原始设计明显更偏：

- 秒级到数秒级
- maker / quote skew
- 微观结构 alpha

所以它**不是**最自然的 `15m` 主信号。

更合理的 desk 读法是两层：

### 5.1 第一层：把它当 `1m` 以下的 raw alpha 母体
也就是：

- 用 OFI / microprice / vol urgency 预测 very-short-horizon drift；
- 先验证它在 `BTC / ETH / SOL` 上是否稳定；
- 再决定它是做 taker，还是做 maker skew。

### 5.2 第二层：把它降采样成 `1m/3m` 的 admission / veto
例如：

- 过去 `60s` 的 OFI-EMA 是否与 `1m` bar close 方向一致；
- 若 `OFI` 与 bar return 背离，则 veto 某些追价 continuation；
- 若 `OFI` 与 microprice 同向极强，则允许更激进的 next-bar continuation / maker join。

翻成人话：

> **这套东西更像给我们现有 `1m/3m` 书加一个“盘口同不同意”的 microstructure vote，而不是把它粗暴抬到 `15m` 上当主 alpha。**

## 6. 这轮真正值得复用的，不只是信号，还有研究流程
这 repo 最值得学的部分，其实有两层。

### 6.1 先证明信号，再做策略
顺序应该是：

1. `signal -> future return` 统计检验
2. `signal -> fair value shift`
3. `fair value -> quote skew or directional entry`
4. 最后才看 PnL

这比直接“先画权益曲线”更适合我们现在的 intake 方式。

### 6.2 把 alpha 和壳拆开
当前 repo 给我们的最好启发不是“照抄参数”，而是：

- `OFI / microprice / vol clustering` 是 alpha 候选层
- `A-S quote / inventory cap / drawdown breaker` 是执行与风险壳

这意味着后续我们完全可以：

- 保留 alpha，本轮先不保留 maker 壳；
- 先在 `1m/3m` directional / router 实验里验证 alpha；
- 等 alpha 站住，再决定是否挂回 maker execution。

## 7. 数据源、公开性、更新频率、最小可复现实验口径
### 7.1 数据源
- Binance 公共 WebSocket：`depth@100ms`、`trade`
- 公开性：**公开可得，无需 API key**
- 更新频率：`100ms` 级别深度 + 实时成交

### 7.2 最小可复现实验
最小复现并不需要整套做市系统，只需要：

1. 实时订阅 `depth@100ms + trade`
2. 维护 top-5 bid/ask depth
3. 计算 `imbalance`
4. 记录 `mid[t]`
5. 回看 `mid[t+100ms / 500ms / 1s / 5s]`
6. 跑 OLS：`future_return ~ imbalance`

如果这一步都不成立，就没必要谈后面的 A-S 壳。

### 7.3 对 desk 的最小迁移版本
若我们不想先碰秒级撮合，可以先做：

- 把 `100ms` OFI 聚合到 `1m`
- 特征：`mean/std/last/max OFI`, `microprice-mid`, `vol urgency`
- 标签：未来 `1m/3m/5m` mid 或 close return

这就能和现有 short-cycle 研究栈对上。

## 8. 一句话结论

> **`mm-live` 最值得 intake 的不是做市公式，而是“先用 OFI 证明 very-short-horizon drift，再决定怎么交易它”这条研究路径；这次 live probe 里 alpha 本体成立，但默认 maker 壳还不该直接宣称可上线。**

## 9. 下一步怎么测
我建议下一步不要直接继续抠 A-S 参数，而是走这三步：

### Step 1：做 `1m/3m/5m` 降采样 portability
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 特征：
  - `ofi_ema_1s`
  - `ofi_ema_5s`
  - `microprice_dev`
  - `vol_urgency`
- 目标：预测未来 `1m / 3m / 5m` return sign 或 bps
- 成本梯度：`2 / 4 / 8 / 12 bps`

### Step 2：做两个壳的 honest 对照
同一套 alpha，分别测试：

1. **directional taker shell**
   - `score > th` 做多
   - `score < -th` 做空
   - 固定时间退出

2. **maker skew shell**
   - 只改 reservation price / quote skew
   - 不碰 inventory 规则

这样才能知道：

> 是 alpha 本身强，还是只在 maker 壳里才有意义。

### Step 3：把它当 shared microstructure veto 接回现有书
优先尝试把它挂到我们已有的：

- intraday continuation
- short-horizon mean reversion
- event-driven next-bar books

做法是：

- 入场前看 `OFI` 是否同向确认；
- 或在逆向强 OFI 时直接 veto。

这可能比“另开一套纯秒级 maker 系统”更快出 first verdict。

## 10. 来源信息
### 主来源（repo）
- **Author:** Ali Pourrahim
- **Year:** 2026
- **Title:** *mm-live*
- **Venue:** GitHub
- **DOI:** 无
- **Readable URL / Repo URL:** <https://github.com/Aliipou/mm-live>

### repo 内引用的学术母体
- Avellaneda, M., & Stoikov, S. (2008). *High-frequency trading in a limit order book.* Quantitative Finance.
- Stoikov, S. (2018). *The micro-price: a high frequency estimator of future prices.* Quantitative Finance.

### 本轮实际审计文件
- `README.md`
- `scripts/collect_and_test_edge.py`
- `scripts/run_benchmark.py`
- `src/mm_live/signals/imbalance.py`
- `src/mm_live/signals/fair_value.py`
- `src/mm_live/strategy/quoting.py`
- `src/mm_live/research/imbalance_prediction.py`
- `src/mm_live/research/benchmark.py`
- `src/mm_live/strategy/cross_venue.py`
- `src/mm_live/risk/limits.py`
