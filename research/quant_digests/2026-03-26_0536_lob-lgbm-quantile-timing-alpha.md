# 别把 1 秒级方向分类仓库只读成“更高准确率”：这份 2026 新 repo 更该先测的是「LOB 概率边 × 滚动分位阈值」1m/3m 事件驱动 raw alpha
- 时间：2026-03-26 05:36 UTC
- 类型：2026 GitHub 新仓库 + 经典 limit-order-book literature + Binance Futures 公共 `1m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：`1s` 级盘口状态、成交流与失衡特征，可以形成未来几分钟方向概率边；再用 `signal = EWM((p_up - p_down) * (1 - p_mild))` 与滚动分位阈值把它转成可执行的 long-timing 策略
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/lob/lightgbm/probability-edge/rolling-quantile/event-driven/time-series/btc/eth/binance/perpetual/1m/3m/5m/15m/repo/paper/execution
- 证据类型：仓库证据 + 经典论文地基 + 本地快检

> 先回答 base alpha：**这不是 filter，也不是纯 execution 小技巧。base alpha 就是“当前 LOB / trade-flow 微观结构状态 → 接下来几分钟方向边”的单资产 directional raw alpha；repo 真正值钱的是它把这条边完整翻译成了 cost-aware 策略骨架。**

## 1. 这次看了什么
主线材料不是论文，而是一份很新的 GitHub 仓库：

- **kailiu0712 (2026), _-5-min-level-Directional-Prediction-for-Crypto-HFT_**

它的 headline 看起来像“用 1 秒级特征做 BTC 方向分类”，但对我们 desk 更有价值的其实不是分类本身，而是它已经把整条链条补齐了：

1. 原始事件流 / order book 重建
2. `1s` 特征工程
3. 成本感知标签（mild / positive / negative）
4. purged walk-forward 训练
5. 概率输出转 signal score
6. 滚动分位数阈值进出场
7. 明确收费的 long-only 回测

所以它不是“又一个 microstructure explainability notebook”，而是**一个可直接移植到 desk 的超短周期 directional alpha skeleton**。

## 2. 我最关心的不是 headline，而是这 4 个可落地部件
### 2.1 成本感知标签先把小波动踢掉
仓库没有直接把所有未来收益都硬分成涨跌，而是先定义一段 `mild` 中性区：

`max(MILD_RETURN_THRESHOLD, fee_rate * threshold_multiplier)`

这一步很值钱，因为它等于先承认：
**小于手续费门槛的预测，就算方向猜对，也不该被当成可交易 alpha。**

### 2.2 概率边不是直接拿来追价，而是先压成 signal score
仓库的核心不是 `argmax(class)`，而是：

`signal = EWM((prob_positive - prob_negative) * (1 - prob_mild))`

也就是：
- 用 `p_up - p_down` 表示方向边强弱
- 用 `1 - p_mild` 给“远离噪声区”的样本更高权重
- 再做时间平滑，避免每秒翻多翻空

这比“模型分类结果 > 0.5 就开仓”成熟得多。

### 2.3 进出场阈值不是固定常数，而是 lagged rolling quantile
进场与平仓条件不是一个手填阈值，而是：
- `buy`: 当前 `signal_score` 高于过去滚动窗口的 `0.9` 分位
- `close`: 当前 `signal_score` 低于过去滚动窗口的 `0.1` 分位

这非常适合 crypto，因为微观结构分布本来就会随流动性、时段、波动状态漂移。

### 2.4 训练验证至少把最容易犯的 leakage 避开了
仓库不是乱序交叉验证，而是：
- `TimeSeriesSplit(n_splits=5)`
- train/test 之间加 purge gap
- fit/validation 之间也加 purge gap

对这种分钟内 / 秒级标签重叠很严重的问题，这是最起码的诚实做法。

## 3. 关键数值先看 repo 自带结果：原样照搬并不算惊艳，但骨架很有价值
仓库自带 `overall_metrics_*.csv`，给了多组 horizon 的 out-of-sample 汇总。最值得记的不是“准确率”，而是**净收益、毛收益和持有时长怎么变**。

### 3.1 repo 原始结果（Gemini BTC，long-only，fee=10 bps）
- **3m horizon**：`cum_strategy_ret = -3.10%`，`cum_gross_strategy_ret = +0.25%`，`max_drawdown = -4.12%`
- **10m horizon**：`cum_strategy_ret = -3.61%`，`cum_gross_strategy_ret = -1.07%`
- **15m horizon**：`cum_strategy_ret = -0.22%`，`cum_gross_strategy_ret = +1.79%`，`max_drawdown = -2.17%`
- **30m horizon**：`cum_strategy_ret = +0.18%`，`cum_gross_strategy_ret = +2.00%`，`max_drawdown = -2.13%`

### 3.2 这组结果真正说明什么
不是“3m 没边，所以 repo 无用”，而是：

1. **方向信息是有的**：15m/30m 的 gross return 为正，说明模型没完全瞎猜。
2. **执行/成本吞噬很重**：3m/10m 从 gross 到 net 明显被手续费吃掉，说明短 horizon 版本必须靠更好的触发稀疏化、maker/taker 切换或更低 fee 才能活。
3. **repo 其实更像一套 timing stack，而不是现成印钞参数**：最值钱的是“概率边 → 平滑 → 自适应阈值 → 风控”的链条。

换句话说：**它是完整策略候选，但不是“拿来就能在 BTC 上直接抄作业”的完整策略。**

## 3.5 策略拆解（必填）
- 方向属性：单资产 / 时间序列 / 微观结构 directional alpha
- 基础 alpha：
  - top-of-book：`best_bid / best_ask / mid / spread / microprice`
  - 深度与失衡：`imbalance_1 / imbalance_5 / depth ratio / slope / entropy / HHI`
  - 成交与事件流：`signed trade flow / place-cancel-fill counts / passive flow / net order flow`
  - 目标：预测未来 `PREDICTION_HORIZON` 的中间价方向（当前配置为 `180s`）
- entry：当 `signal_score > lagged rolling q90` 时，下一时刻按 `best_ask` 做多
- exit：当 `signal_score < lagged rolling q10` 时，下一时刻按 `best_bid` 平仓
- sizing：repo 里是全仓 / 固定 notional 风格；desk 版应先改成 `score-strength bucket × spread-state × volatility-state` 分层仓位
- risk：
  - `min_hold_seconds`
  - `max_position_notional`
  - spread widening / quote vacuum 直接 kill-switch
  - 极端波动时禁止继续追高频 re-entry
- cost：
  - entry/exit 双边 fee 显式计入
  - 原始结果已经证明：不把 fee 放进去，结论会明显失真

## 4. 为什么这条线和当前 desk 直接相关
它和我们昨天那篇 `3s` microstructure taker alpha 不完全重复，差别在于：

1. **昨天那篇更像“有没有这条边”**；
2. **今天这份 repo 更像“怎么把这条边治理成策略”**。

因此它的价值不在于再证明一次 `OFI / imbalance` 有信息，而在于提供了 3 个我们可以直接拿走的组件：
- 成本感知标签
- 概率边平滑
- 滚动分位阈值治理

这 3 个组件不止能服务单币 BTC，也能服务：
- `1m / 3m` 单资产 event-driven long timing
- 5m 主策略的 execution timing / entry veto
- cross-asset micro alpha 的统一 signal governance

## 5. 本地最小快检：把 repo 思路压到 Binance 公开 `1m` futures K 线后，还剩下多少影子
我没复刻 repo 的完整 1 秒 order book，而是做了一个更便宜的代理快检：

**数据源**：Binance USDⓈ-M Futures 公共 `1m` K 线（`BTCUSDT / ETHUSDT`，最近 10 天）

**代理特征**：
- `taker_imbalance = 2 * taker_buy_base / volume - 1`
- `trade_count_z`
- `ret1_z`
- 再对宽波动 bar 做一个简单 confidence penalty，形成 `score_conf`

### 5.1 结果怎么读
这不是 repo 的正式 replication，只是看：
**如果只能先拿公开便宜数据，repo 的微结构方向边能不能在 `1m/3m/5m/15m` 上留下痕迹？**

### 5.2 快检数字
**ETH 比 BTC 更像能留下可见影子的标的。**

- `ETHUSDT`：`score_conf` 顶部 10% 事件，未来
  - `1m` 平均收益约 **+0.59 bps**
  - `5m` 平均收益约 **+0.83 bps**
  - `15m` 顶/底 decile spread 约 **2.00 bps**
- `ETHUSDT`：若要求信号连续两根 `1m` bar 同向极端（2-bar persistence），未来
  - `1m` 平均约 **+1.21 bps**
  - `3m` 平均约 **+0.72 bps**
- `BTCUSDT`：两根持续强信号后，未来
  - `3m` 平均约 **+0.48 bps**
  - `5m` 平均约 **+0.59 bps**

### 5.3 这组快检最重要的含义
- **有影子，但不厚。** 分钟级代理还能看见方向倾向，尤其 ETH 比 BTC 更明显。
- **一压粗就衰减。** 这说明 repo 的 edge 更适合 `1m/3m` 事件触发或 execution timing，而不是直接改写成一个 bar-close `15m` 主信号。
- **连续性门槛有用。** 2-bar persistence 比单点极值更像能留下可交易的方向边。

## 6. 对 desk 的最合适读法
如果强行把这份 repo 读成“BTC 3m long-only 现成策略”，我觉得不值得。

但如果把它读成下面这三件事之一，就很值得：

### 6.1 `1m / 3m` 事件驱动 long timing raw alpha
当微结构压力连续两个分钟代理或若干秒级片段同向极端时，触发一笔独立 micro-trade。

### 6.2 5m 主策略的 entry timing layer
5m 主策略已经想做多时，不是立刻吃，而是等：
- `signal_score` 回到上分位并持续
- spread / range 没恶化
- taker imbalance 没反转

### 6.3 微结构模型的统一治理模板
以后不管底层是 LASSO、LightGBM、LOB Transformer 还是简单 OFI，都可以统一套：
- 成本感知标签
- `probability edge`
- rolling quantile trigger
- fee/slippage stress

## 7. 下一步怎么测（最应该先做的 4 组实验）
### 7.1 用真 `1s` 公共数据复刻，不要再停在 `1m` 代理
**数据源**：Binance Data Vision `bookTicker` / `aggTrades` / depth snapshots（公开可得）

**标的**：`BTCUSDT / ETHUSDT / SOLUSDT`

**窗口**：最近 `14~30` 天

### 7.2 先测 3 组 horizon，而不是一口气扫大网格
- `30s`
- `90s`
- `180s`

因为 repo 结果已经暗示：太短容易被费用吃掉，太长又会把 micro edge 稀释掉。

### 7.3 先测这 3 个治理变量
1. **persistence gate**：信号连续 `N` 秒同向才开仓
2. **threshold mode**：固定阈值 vs rolling quantile
3. **execution mode**：taker-only vs maker-disabled-in-stress vs hybrid

### 7.4 最关键的评估指标
- `IC(score, future_ret_h)`
- `gross edge per event (bps)`
- `net edge per event`（至少做 `fee / fee+0.5tick / fee+1tick` 三档）
- `events/day`
- `holding-time distribution`
- `spread-conditioned pnl`

## 8. 我现在的判断
**这是一条值得继续 intake 的 raw alpha 线，但当前最合理的定位不是“直接上 BTC 3m long-only”，而是：**

- 对 `1m / 3m`：事件驱动 long timing alpha 候选
- 对 `5m / 15m`：更像 execution timing / admission 组件
- 对策略工程：是一套很像样的 `micro-alpha governance template`

所以它进入研究池的理由不是“repo 绩效惊艳”，而是：
**它把一个本来容易写成黑箱分类器的 raw alpha，拆成了可治理、可 stress、可迁移的完整骨架。**

## 9. 风险与保留意见
- repo 只做 **BTC / long-only / Gemini**，迁移到 Binance perp 和 alt 时，不应默认稳定。
- `1m` 代理快检保留的信息很有限，不能替代真 `1s` LOB replication。
- 微结构信号最怕 latency / queue / spread widening；gross 有边，不代表 net 能活。
- 如果后续 replication 发现 edge 只在极少数 stress pocket 存在，那它更应被降级为 execution component，而不是 always-on alpha。

## 10. 来源
1. **kailiu0712. (2026). _-5-min-level-Directional-Prediction-for-Crypto-HFT_. GitHub repository.**
   - Repo URL: `https://github.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT`
   - README Raw: `https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/README.md`
   - Config Raw: `https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/config.py`
2. **Cont, R., Kukanov, A., & Stoikov, S. (2014). _The Price Impact of Order Book Events_. Journal of Financial Econometrics.**
   - DOI: `10.1093/jjfinec/nbt003`
   - Readable URL: `https://academic.oup.com/jfec/article/12/1/47/816163`
3. **Kolm, P. N., Turiel, J., & Westray, N. (2023). _Deep order flow imbalance: Extracting alpha at multiple horizons from the limit order book_. Mathematical Finance.**
   - DOI: `10.1111/mafi.12413`
   - Readable URL: `https://onlinelibrary.wiley.com/doi/10.1111/mafi.12413`
4. **Binance USDⓈ-M Futures API / public klines**
   - URL: `https://fapi.binance.com/fapi/v1/klines`
   - 数据公开性：公开可得
   - 更新频率：分钟级（正式 replication 应升级到秒级事件流）

## 11. 本地快检产物
- `reports/artifacts/quant_digests/microstructure_lgbm_repo_probe_20260326/summary.csv`
- `reports/artifacts/quant_digests/microstructure_lgbm_repo_probe_20260326/persistence_summary.csv`
- `reports/artifacts/quant_digests/microstructure_lgbm_repo_probe_20260326/btcusdt_1m_10d.csv`
- `reports/artifacts/quant_digests/microstructure_lgbm_repo_probe_20260326/ethusdt_1m_10d.csv`
