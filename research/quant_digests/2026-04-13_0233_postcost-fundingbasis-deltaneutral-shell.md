# 别把这份 funding-rate repo 只读成课程项目：对 short-cycle desk，更该先拆的是「positive funding × rich-perp spread × post-cost label」这条完整 delta-neutral raw alpha 壳

- 时间：2026-04-13 02:33 UTC
- 类型：2026 GitHub repo source audit（GitHub API metadata + `README.md` + `docs/features.md` + `docs/labels.md` + `docs/baselines.md` + `docs/signals.md` + `docs/backtest.md` + `configs/models/baseline.yaml` + `configs/labels/default.yaml` + `configs/backtests/default.yaml` + `src/funding_arb/features/builders.py` + `src/funding_arb/labels/generator.py`）+ Binance public `15m` portability probe
- 主题标签：raw-alpha/carry/funding/basis/delta-neutral/stat-arb/spot-perp/post-cost-label/complete-shell/1h-state/5m-15m-execution/binance/repo/public-data/cost/risk
- 证据类型：repo 证据 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**当 perp 相对 spot 明显偏贵、且最近 funding 仍维持正值时，做 `short perp + long spot`，同时赚 funding carry 与 basis 收敛；repo 的关键升级不是“又一个 funding 阈值”，而是把它明确写成 `post-cost net return` 标签、统一信号层与完整 backtest 壳。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = `positive funding + rich perp-vs-spot spread` 这组状态，意味着 `short perp / long spot` 这笔 delta-neutral 交易的未来净收益更可能为正；repo 真正值钱的地方，是把这件事直接写成“成本后还能不能赚钱”的可训练、可回测、可执行壳。**

翻成人话：
- perp 太贵，说明合约腿被挤得更热；
- funding 还是正的，说明“做空 perp 这条腿会收钱”这件事还没结束；
- 如果之后 spread 往 spot 收敛，你会再赚一层 basis 回归；
- 所以这不是纯 filter，也不是纯解释，它本身就是一条 **carry / basis / relative-value raw alpha**。

## 2. 这次看了什么

### 主来源（repo）
- **Author / Owner：** MengerWen
- **Year：** 2026
- **Title：** *Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates>
- **Repo URL：** <https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates>
- **GitHub metadata：**
  - created: `2026-03-19`
  - pushed: `2026-04-10`
  - description: hybrid DeFi prototype for delta-neutral arbitrage in crypto perpetual futures

### 本轮重点读取的 repo 证据
1. `docs/features.md`
2. `docs/labels.md`
3. `docs/baselines.md`
4. `docs/signals.md`
5. `docs/backtest.md`
6. `configs/models/baseline.yaml`
7. `configs/labels/default.yaml`
8. `configs/backtests/default.yaml`
9. `src/funding_arb/features/builders.py`
10. `src/funding_arb/labels/generator.py`

这轮不是把 repo 当“课程项目工程展示”看，而是先问：

> **里面到底有没有一条能被我们 desk 直接拿来做最小实验的完整 raw alpha 壳？**

答案是：**有。**
而且比“谁 funding 高就去空谁”更完整，因为它已经把：
- 数据口径
- 特征组
- 目标标签
- 规则基线
- 统一信号层
- backtest 成本模型

全部串起来了。

## 3. repo 里最值得拿走的，不是黑箱模型，而是这条完整策略定义

### 3.1 数据层已经够直接
repo 默认数据就是：
- Binance public REST
- `BTCUSDT`
- spot + perpetual + funding
- 默认研究频率：`1h`
- 默认样本：`2021-01-01` 到 `2026-04-07`

这很重要，因为它意味着：
- **公开可得**；
- 不需要私有成交回放；
- 不需要 proprietary venue feed；
- 至少在 research layer，上手成本很低。

### 3.2 它把 carry / basis 写成了明确特征
repo 的 feature 设计里，最核心的是两组：

#### Funding 组
- `funding_rate_bps`
- `funding_mean_8h / 24h / 72h / 168h`
- `funding_zscore_*`
- `funding_positive_share_*`

#### Basis / spread 组
- `spread_bps = ((perp_close / spot_close) - 1) * 10000`
- `spread_zscore_72h`
- `spread_deviation_*`
- `spread_reversion_signal_*`

再往上它还做了 interaction / state：
- `positive_funding_regime = 1{funding_mean_24h > 0}`
- `wide_spread_regime = 1{|spread_zscore_72h| > 1}`
- `funding_x_spread_bps`

这套写法的价值在于：
- 它不是抽象地说“funding 可能有用”；
- 而是把 **carry persistence、basis dislocation、risk state** 全变成了能直接进模型、进回测的字段。

## 4. 这条 raw alpha 在 repo 里到底是怎么落地的？

### 4.1 最朴素的 rule baseline 已经把核心想法说透了
`configs/models/baseline.yaml` 里给了三个 rule baseline：

1. `funding_threshold_2bps`
   - `funding_rate_bps >= 2.0`
2. `spread_zscore_1p5`
   - `spread_zscore_72h >= 1.5`
3. `combined_funding_spread`
   - `funding_rate_bps >= 1.0`
   - `spread_zscore_72h >= 1.5`
   - `positive_funding_regime == 1`

对我们 desk 最值得先拿的，就是第三条：

> **`positive funding` 和 `rich spread` 要同时成立，才做 `short perp + long spot`。**

这比单看 funding 或单看 basis 更诚实，因为：
- 只有 funding 高，不代表 spread 还有回归空间；
- 只有 spread 宽，不代表空 perp 这条腿还有 carry 补贴；
- 两者同向，才像真正的 delta-neutral 机会状态。

### 4.2 repo 没把它停留在“规则触发”
更值钱的地方在 label 层。

`configs/labels/default.yaml` 和 `src/funding_arb/labels/generator.py` 里，repo 明确把目标定义成：
- `target_future_net_return_bps_8h`
- `target_future_net_return_bps_24h`
- `target_is_profitable_8h / 24h`
- `target_is_tradeable_8h / 24h`

而且净收益定义得很清楚：

```text
future_net_return_bps
= perp_leg_return_bps
+ spot_leg_return_bps
+ funding_return_bps
- estimated_cost_bps
```

成本也不是口头说说，而是显式进标签：
- taker fee
- slippage
- gas cost
- optional other friction
- optional borrow cost

默认成本参数对应到 repo 回测壳，大约是：
- `taker_fee_bps = 5`
- `slippage_bps = 3`
- `gas_cost_usd = 2`
- `position_notional = 10000`

也就是 roughly：
- `4 * (5 + 3) + 2/10000*10000 ≈ 32.2 bps`

这点很关键：

> **repo 的升级，不是“我也觉得 funding carry 可能有 alpha”；而是“这笔交易扣完成本后，到底还能不能留下正净收益”，并把这件事做成统一标签。**

### 4.3 backtest 壳已经是完整的
`configs/backtests/default.yaml` 给的执行壳已经很清楚：
- direction: `short_perp_long_spot`
- entry delay: `1` bar
- execution price: `open`
- holding window: `24h`
- maximum holding: `48h`
- exit on signal off: `true`
- fixed notional: `10000 USD`
- explicit fees / slippage / gas

所以这不是“研究直觉卡片”，
而是已经具备：
- entry
- exit
- sizing
- risk
- cost

的完整策略原型。

## 5. 对 short-cycle desk，真正有用的读法是什么？

不是直接说：
- “这个 repo 是 1h 的，所以和我们无关”；

而是要改写成：

> **repo 提供的是一个慢状态的 carry/basis admission shell；短周期 desk 要做的，不是强行把核心逻辑改成逐根 `1m/3m/5m` 主信号，而是把它当成 `1h state`，再下沉到 `15m/5m` 执行层。**

也就是说：
- **base alpha 仍然是 carry + basis convergence；**
- 但 `1m/3m/5m/15m` 更适合承担：
  - 触发细化
  - 进场时点优化
  - funding event 前后的 execution router
  - 滑点控制与撤单逻辑

## 6. 我做了一个最小 `15m` portability probe：结果很诚实

### 6.1 数据口径
- **市场：** Binance public spot + USDⓈ-M perpetual + funding
- **symbol：** `BTCUSDT / ETHUSDT / SOLUSDT`
- **样本：** 最近 `120d`
- **频率：** `15m`
- **最小翻译信号：**
  - `last_funding_bps >= 1.0`
  - `spread_zscore_72h >= 1.5`
  - `positive_funding_regime == 1`
- **方向：** `short perp + long spot`
- **入场：** next-bar open
- **成本压力：**
  - `20 bps total`
  - `32.2 bps repo-like`

### 6.2 本地 artifacts
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_menger_funding_basis_shell_probe.py`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_menger_funding_basis_shell_probe/fetch_status.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_menger_funding_basis_shell_probe/trade_log.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_menger_funding_basis_shell_probe/summary.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_menger_funding_basis_shell_probe/summary_8h_fixed.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_menger_funding_basis_shell_probe/summary_24h_fixed.csv`

### 6.3 关键结果：直接翻成 `15m` threshold shell，**不过线**
#### repo 风格的 `signal-off` 直译版（3 个 symbol 聚合）
- 交易数：**`78`**
- 平均持有：**`1.32` bars**（约 `20` 分钟）
- 平均 funding 收入：**`0.91 bps`**
- `20 bps total` 下平均单笔净收益：**`-18.87 bps`**
- `32.2 bps repo-like` 下平均单笔净收益：**`-31.07 bps`**

#### 固定持有 `8h` 也没救回来
- 交易数：**`30`**
- `20 bps total` 下平均单笔净收益：**`-18.40 bps`**
- 平均 funding 收入：**`0.21 bps`**

#### 固定持有 `24h` 仍然不够
- 交易数：**`19`**
- `20 bps total` 下平均单笔净收益：**`-17.10 bps`**
- 平均 funding 收入：**`0.57 bps`**

## 7. 这组结果说明了什么？

### 7.1 它不是“repo 没价值”
相反，这个 probe 恰好说明：

> **repo 值钱的部分，不是朴素阈值本身，而是“post-cost label + ranking model + unified signal/backtest shell”这一整套研究框架。**

因为在 `15m` 上直接把规则硬翻下来，会出现两个问题：
1. **持有太短**
   - `signal-off` 直译版平均只拿了 `1.32` 根 bar；
   - funding 根本来不及积累；
2. **spread 还没来得及真正收敛，成本已经先吃掉了 gross edge**

### 7.2 对 short-cycle desk 的正确读法，不是“马上上这条 15m 规则”
而是：
- **把 repo 当成 slow-state / label-engineering shell；**
- 再把 `5m / 15m` 用在 execution 和 event-time router 上。

换句话说：
- 它提供的是“什么状态值得做 delta-neutral carry/basis trade”；
- 不是现成保证能过线的 `15m` 裸 threshold 信号。

## 8. 所以这轮应该把它放在研究池里的什么位置？

我的判断是：

### 8.1 它仍然属于 `raw alpha`
因为它的 base alpha 很清楚：
- 不是仅做过滤；
- 不是只做风控；
- 不是只解释为什么 funding 会动；
- 而是明确指向：
  - **做哪条腿**
  - **赚哪两层收益**
  - **在什么状态下做**

### 8.2 但它更像“完整研究壳 + 慢状态 alpha”，而不是已经 deskified 的 fast lane 赢家
这也是为什么它值得写：
- 它补的是 `carry / funding / basis / delta-neutral` 这条 **完整 shell 素材**；
- 不是再写一篇泛泛的“funding 很重要”；
- 但它当前不应该被误报成：
  - “现成可上 `15m` 裸信号”。

## 9. 与当前 `1m / 3m / 5m / 15m` 的关系

最合理的 desk 化映射是：

### `1h` 负责状态
- funding persistence
- spread extremeness
- carry regime
- post-cost expected return ranking

### `15m / 5m` 负责执行
- funding settlement 前后窗口切入
- 微反抽失败再进
- spread 再次放宽时进，而不是追已经回归一半的腿
- maker / passive fill 优先
- event-time stop / time stop

所以它和短周期 desk 的关系不是“无关”，
而是：

> **它更像 carry/basis 家族的上层录取器与完整研究壳，下层执行再交给 `15m / 5m`。**

## 10. 下一步怎么测

1. **别再用裸 threshold 当最终版，改测 ranking signal**
   - 直接照 repo 路线，把 `target_future_net_return_bps_8h / 24h` 当主目标；
   - 先用 ridge / logistic baseline；
   - 再看 LSTM 是否真能提升排序质量。

2. **把进入时点改成 funding event-time router**
   - 重点测 funding 前 `30m / 60m / 120m`；
   - 看 edge 是出现在 funding 前、funding 后，还是 spread 二次放宽时。

3. **把 `1h state` 下沉成 `15m / 5m` execution shell**
   - 只在 `1h` state 合格时允许入场；
   - `15m` 上要求 spread 再次扩张或 micro lower-high / micro fade；
   - 避免刚触发就追在回归路上。

4. **补更贴近交易的外生字段**
   - premium index / mark-price dislocation
   - open interest
   - event proximity
   - venue liquidity proxy

5. **把成本假设改成 maker-first / mixed execution**
   - 这条壳对 taker 成本非常敏感；
   - 如果 future version 连 maker-first 都救不回来，就更该诚实降级。

## 11. 一句话带走

> **这份 2026 funding-rate repo 值钱的，不是“funding 高就空”这句老话，而是它把 `positive funding × rich perp spread` 这条 delta-neutral carry/basis raw alpha，写成了公开数据可复现、成本后可打标签、信号层与回测层统一的完整研究壳；但我这轮 `15m` public-data probe 也很明确地告诉我们：别把它误读成现成 fast-lane 裸信号，当前更诚实的用法是把它当 `1h state / post-cost ranking shell`，再下沉到 `5m/15m` 做执行。**
