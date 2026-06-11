# 别把这份 2026 live market-making repo 只读成“工程化 A-S 引擎”：对 short-cycle desk，更该先保留的是「microprice 偏移 × top-book imbalance 共振 → 几秒级 mid 漂移」这条 raw alpha，再把 Kalman fair value / adaptive quoting 包成完整策略壳

- 时间：2026-04-17 18:35 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `main.py` + `src/mm_live/signals/imbalance.py` + `src/mm_live/signals/fair_value.py` + `src/mm_live/signals/microprice.py` + `src/mm_live/signals/composite.py` + `src/mm_live/strategy/quoting.py` + `src/mm_live/execution/simulator.py`）+ Binance 公共深度 live probe（BTCUSDT，240s，top20，1s sampling）
- 主题类型：raw alpha
- 基础 alpha：**如果 best bid / ask 队列权重推出来的 `microprice` 已经高于 mid，且 top-book bid depth 也明显大于 ask depth，那么未来几秒 mid-price 更容易继续往上漂；反向同理。Kalman fair value 更像降噪与定价中枢，不是最强 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / microstructure / microprice / order-book-imbalance / queue-pressure / fair-value / kalman / avellaneda-stoikov / maker / market-making / quote-skew / binance / repo / public-data / 1m / 3m / 5m
- 证据类型：GitHub repo 实现 + 本地 live public-data sanity probe

## 1. 这次看了什么
主材料是一个 2026 新仓：

- **Author / Maintainer：** Aliipou
- **Year：** 2026
- **Title：** *mm-live*
- **Venue：** GitHub repo（事件驱动 market making engine，含 Binance/OKX feed、Kalman fair value、OFI / microprice / vol clustering、adaptive Avellaneda-Stoikov quoting、paper simulator、risk controls）
- **DOI：** N/A
- **Readable URL：** <https://github.com/Aliipou/mm-live>
- **Repo URL：** <https://github.com/Aliipou/mm-live>

先把一句话讲清楚：

> **这份仓最值得 intake 的，不是“我们也做一个 A-S 做市框架”，而是 repo 把一条可直接解释的 ultra-short raw alpha 拆得很清楚：`inside queue pressure + near-book imbalance` 会先于几秒级价格微漂移，而 fair value / adaptive spread / inventory control 是把它包装成 live strategy 的外壳。**

也就是说，这轮最值得保留到素材池里的第一层不是“做市引擎”本身，而是：
- **microprice 相对 mid 往上偏时，说明 inside bid queue 更厚，价格更容易往上挪；**
- **top-book imbalance 同向时，这种短时漂移更可信；**
- **Kalman fair value 负责把噪声 mid 平滑成可挂单中枢，但 alpha 本体更接近 queue pressure。**

## 2. 核心结论
### 2.1 一句话结论

> **这是条可以独立成型、也能直接封装进完整 maker shell 的 microstructure raw alpha：`microprice deviation × imbalance consensus -> short-horizon drift`。repo 提供的 A-S quoting、vol regime、inventory limit，是把这条 alpha 变成交易系统的第二层。**

### 2.2 一句话它是怎么证明的

> **repo 代码把 fair value、microprice、OFI、adaptive quote 和 simulator 全部接在一起；我又用 Binance 公共深度做了 240 秒 live probe，结果显示 `microprice deviation` 和 `top5 imbalance` 对未来 `1s/5s/10s` 的 mid return 都有一致方向性，而“Kalman fair-value gap 单独拿出来”反而明显更弱。**

### 2.3 为什么值得进素材池
- 它仍然是 **raw alpha**，不是单纯 execution 补丁；base alpha 可以一句话说清；
- repo 给的是 **完整可落地壳**：signal / quote placement / inventory / volatility regime / paper simulator / risk cap 都在；
- 它和今天早些时候那类“纯 OBI 厚薄”相比，多了一层很实用的 desk 读法：
  - **单看平滑 fair value 不够；**
  - **inside-queue 的 microprice 偏移，才更像最该优先保留的 alpha anchor。**

## 3. repo 里最值钱的 4 层结构
### 3.1 第一层：microprice 不是花哨名词，它就是“队列压力版的公允价”
`src/mm_live/signals/microprice.py` 里写得很直白：

- `microprice = (ask * bid_size + bid * ask_size) / (bid_size + ask_size)`
- 当 best bid queue 明显厚于 ask queue 时，`microprice > mid`
- 当 ask queue 更厚时，`microprice < mid`

翻成人话：

> **如果最优买一后面排了更厚的队，市场短时间里更像“有人在下方托着价格”，所以真实短时公允价会更偏向 ask 那边。**

这比只看 mid 更接近真实的 ultra-short directional edge。

### 3.2 第二层：OBI / OFI 是确认层，不只是同义反复
`src/mm_live/signals/imbalance.py` 用 top-N depth 算：

- `imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)`
- 默认对 top `5` 档做汇总
- 再做 EMA 平滑
- 再用 `alpha_impact` 把 imbalance 转成 fair-value shift

我的读法：

> **microprice 更偏 inside queue；imbalance 更偏近端深度分布。两者不是一回事，但如果它们同向，那个方向更值得你去偏置报价。**

也就是说，这不是“多算一个指标凑热闹”，而是 **queue pressure 的双视角确认**。

### 3.3 第三层：Kalman fair value 是定价中枢，不该被误读成 alpha 本体
`src/mm_live/signals/fair_value.py` 的定义是：

- `fair_value = Kalman(mid_price) + alpha * imbalance`

这一层很重要，但我的 desk 读法跟 README headline 稍有不同：

> **Kalman 更像把 noisy mid 变成可交易的报价中心；真正决定你该把 quote 往哪边挪的，仍然主要是 queue pressure（microprice / imbalance）本身。**

这轮 live probe 也支持这个读法：
- `microprice deviation` 和未来回报相关性稳定为正；
- `imbalance` 也有相似效果；
- **但 `fair_value - mid` 单独做排序时，方向性明显更弱。**

### 3.4 第四层：Adaptive A-S 才是把 alpha 变成“系统”的那层壳
`src/mm_live/strategy/quoting.py` 和 README 给的是完整做市翻译：
- 用 `fair_value` 当报价中心；
- 用 dual EWMA volatility 决定 spread 宽度；
- 用 imbalance skew 决定 bid/ask 偏向；
- 用 inventory cap / one-sided quoting 限制持仓；
- 用 simulator 和 risk loop 接回 paper/live execution。

翻成人话：

> **raw alpha 回答的是“短时更可能往哪边漂”；A-S 壳回答的是“既然更可能往这边漂，我应该把哪边挂近一点、哪边挂远一点、仓位别做爆”。**

## 4. 我补的 Binance 公共深度 live probe
### 4.1 数据源、公开性、更新频率、最小实验口径
- **数据源：** Binance Spot 公共 `api/v3/depth`
- **公开性：** 完全公开可得
- **更新频率：** 这里按 `1s` 轮询抓 `top20 depth`
- **标的：** `BTCUSDT`
- **样本：** `240` 个样本，约 `240s`
- **最小可复现实验口径：**
  1. 每秒抓一次 `top20` depth；
  2. 算 top5 imbalance、best-level microprice、Kalman fair value；
  3. 看当前指标分位极端值，对未来 `1s / 5s / 10s` mid return 的影响；
  4. 先做 signal-only sanity check，再考虑 quote simulator。
- **artifact：**
  - `reports/artifacts/quant_digests/2026-04-17_kalman_imbalance_fairvalue_probe.py`
  - `reports/artifacts/quant_digests/2026-04-17_kalman_imbalance_fairvalue_probe_samples.csv`
  - `reports/artifacts/quant_digests/2026-04-17_kalman_imbalance_fairvalue_probe_summary.json`

### 4.2 关键数字
先看 repo 最想表达的几层信号，哪层更像真 alpha：

#### （1）`microprice deviation = microprice - mid`
- **1s horizon：** 高分位桶平均 `+0.336 bps`，低分位桶平均 `-0.216 bps`，top-bottom spread `+0.552 bps`
- **5s horizon：** 高分位桶平均 `+0.790 bps`，低分位桶平均 `-0.229 bps`，spread `+1.019 bps`
- **10s horizon：** 高分位桶平均 `+1.306 bps`，低分位桶平均 `-0.075 bps`，spread `+1.381 bps`
- **相关性：** `corr ≈ 0.205 / 0.184 / 0.185`

#### （2）top5 imbalance
- **1s horizon：** 高分位桶 `+0.318 bps`，低分位桶 `-0.216 bps`，spread `+0.534 bps`
- **5s horizon：** 高分位桶 `+0.778 bps`，低分位桶 `-0.229 bps`，spread `+1.008 bps`
- **10s horizon：** 高分位桶 `+1.306 bps`，低分位桶 `-0.075 bps`，spread `+1.381 bps`
- **相关性：** `corr ≈ 0.203 / 0.180 / 0.181`

#### （3）Kalman fair-value gap = `fair_value - mid`
- **1s horizon：** top-bottom spread `-0.185 bps`
- **5s horizon：** top-bottom spread `+0.014 bps`
- **10s horizon：** top-bottom spread `+0.130 bps`
- **相关性：** `corr ≈ -0.019 / 0.009 / 0.012`

### 4.3 我对这些数字的读法
这轮最值得记住的不是“所有东西都有效”，而是：

> **repo 里最强、最能直接迁移到公开盘口实验上的，并不是平滑后的 fair-value gap，而是更原生的 queue-pressure 信号：`microprice deviation` 与 `imbalance`。**

这对 desk 的意义很大，因为它直接告诉我们：
- **Kalman 层适合当中枢/去噪；**
- **microprice / imbalance 更适合当 admission / skew anchor；**
- **如果只拿 `fair_value - mid` 当主排序，edge 反而容易被平滑掉。**

## 5. 对我们 desk 的正确读法
### 5.1 这轮为什么归到 `raw alpha`
因为它的 base alpha 可以直接说清：

> **inside queue pressure 和近端深度失衡，会先于几秒级 mid 漂移。**

这本身就是一个独立 raw alpha；quote skew / spread control 只是执行壳。

### 5.2 和 `1m / 3m / 5m / 15m` 的关系
- **1m / 3m：** 最自然，适合做 maker quote skew、child-order veto、入场 refinement；
- **5m：** 不适合把它当 bar-close 主因子硬做，但很适合做 `entry timing / execution admission`；
- **15m：** 更适合当执行 veto 或仓位微调，不适合伪装成 15m 主驱动 alpha。

### 5.3 它服务于哪些 raw alpha
这条东西不只服务 market making：
1. **ultra-short maker alpha：** 直接决定 bid/ask 哪边更该 aggressive；
2. **shock continuation / lagger catch-up 的 execution admission：** 盘口不顺风就别追；
3. **mean reversion / spread fade 的入场 refinement：** 先等 microstructure 不再逆着你，再挂单。

## 6. 策略拆解（必填）
- **方向属性：** 单资产 / microstructure / ultra-short directional edge，执行形态偏 maker
- **基础 alpha：** microprice 偏移与 near-book imbalance 共振，先于短时 mid-price 漂移
- **regime：** 高噪声、撤单密集、盘口深度虚胖、重大事件前后，edge 易衰减
- **filter / veto：** 最小有效深度、最小稳定 spread、撤单率 / 刷新稳定性、事件窗禁做、极端 vol widening
- **risk / sizing / execution overlay：** A-S half-spread、inventory skew、one-sided quoting、position cap、drawdown breaker、maker-first / taker fallback 限制

## 7. 下一步怎么测
别直接跳完整 live deployment，先做 4 个更决定性的最小实验：

1. **consensus signal test**
   - 不是单看 `microprice` 或单看 `imbalance`，而是只在两者同向且都进极端分位时开信号；
   - 核心看：future `1s/3s/5s/10s` drift 是否更集中，trade count 是否明显下降。

2. **WebSocket L2 版本**
   - 当前只是 `1s` REST 轮询；
   - 下步要用 Binance 增量深度流，测 `100ms~500ms` 刷新下，edge 会不会更强，还是会被噪声吞掉。

3. **maker simulator 版本**
   - 用 repo 的 quote/simulator 结构，把 `microprice/imbalance consensus` 接到 bid/ask skew；
   - 至少比较三档：`mid symmetric` / `imbalance-only skew` / `microprice+imbalance consensus skew`。

4. **跨资产 portability**
   - 同口径跑 `ETHUSDT / SOLUSDT`；
   - 看这是 BTC inside-book 独有，还是 liquid majors 都有。

最该先盯两个指标：
- **极端高低分位的 future mid-return 差值是否在成本前稳定为正；**
- **引入 maker fill / cancel risk 后，edge 还能剩多少。**

## 8. 风险与保留意见
- 这轮 live probe 只有 `240s`，只是 sanity check，不是稳健回测；
- REST 轮询会漏掉亚秒级盘口变化，真实信号应以增量 WebSocket 为准；
- 这类 alpha 对 spoofing、cancel-replace、交易所撮合细节很敏感；
- 目前证据更支持它做 **ultra-short quote skew / admission**，不支持把它夸大成独立 `15m` bar alpha。

## 9. 来源
1. **Aliipou. (2026). _mm-live_. GitHub Repository.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/Aliipou/mm-live>
   - Repo URL: <https://github.com/Aliipou/mm-live>
2. **Aliipou. (2026). _README.md / main.py / src/mm_live/signals/*.py / src/mm_live/strategy/quoting.py / src/mm_live/execution/simulator.py_.**
   - README: <https://raw.githubusercontent.com/Aliipou/mm-live/main/README.md>
   - main.py: <https://raw.githubusercontent.com/Aliipou/mm-live/main/main.py>
   - imbalance.py: <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/signals/imbalance.py>
   - fair_value.py: <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/signals/fair_value.py>
   - microprice.py: <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/signals/microprice.py>
   - composite.py: <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/signals/composite.py>
   - quoting.py: <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/strategy/quoting.py>
   - simulator.py: <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/execution/simulator.py>
3. **Binance Spot Market Data API.**
   - Depth endpoint: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#order-book>
