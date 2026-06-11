# 别把这份 funding-rate repo 继续只读成 ML admission：对 short-cycle desk，更该先测的是「positive funding × spread-zscore 共振」这条规则型 delta-neutral raw alpha
- 时间：2026-04-15 00:58 UTC
- 类型：GitHub / repo source audit
- 主题类型：raw alpha
- 基础 alpha：当 perp 资金费率显著为正、且 perp 相对 spot 仍明显偏贵时，`short perp + long spot` 的 delta-neutral 头寸更可能同时兑现 `funding carry + basis convergence`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：carry / funding / basis / delta-neutral / relative-value / stat-arb / rule-baseline / binance / btc
- 证据类型：工程证据（repo 文档 + 配置 + source audit + robustness report）

## 1. 这次看了什么
先回答 base alpha：**这不是“又一个 funding 预测模型项目”，而是一条可以直接说清楚的相对价值 raw alpha——当 `funding_rate_bps` 足够高、`spread_zscore_72h` 也够高时，说明 perp 不只是“收租高”，而且相对 spot 还处在偏贵状态，此时做 `short perp + long spot`，赚的是 funding + basis 回归的组合。**

这轮主看的是 2026 GitHub repo `MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates` 里更接近“可执行 baseline”的部分，而不是继续盯着深度学习 headline：
- `configs/models/baseline.yaml`
- `src/funding_arb/models/baselines.py`
- `docs/labels.md`
- `docs/backtest.md`
- `reports/robustness/binance/btcusdt/1h/report.md`
- `reports/data_quality/binance/btcusdt/1h/report.md`

repo 默认数据口径是 **Binance / BTCUSDT / 1h**。数据质量报告给出的底层环境也很重要：
- 样本 `46152` 条，覆盖 `2021-01-01 ~ 2026-04-07`
- funding 事件 `3092` 次
- `funding_rate_bps` 均值 `0.06966`，极值 `-11.1953 ~ 24.8993`
- 正 funding 占比 `0.878719`
- `spread_bps` 均值 `-1.534091`
- `funding_rate_bps` 与 `spread_bps` 相关性只有 `0.1697`

这组统计本身就在提醒：**正 funding 很常见，但“高 funding”不等于“perp 仍然足够贵”，所以 funding carry 单腿筛选不够，必须叠 basis / spread 条件。**

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值得 desk intake 的，不是 “DL 能不能赢”，而是它把一条可解释的规则型 baseline 写得很完整：`positive funding + rich perp spread` 共振时，做 `short perp + long spot` 的 delta-neutral stat-arb。
- **一句话证明方式：** 我直接看了 baseline config、规则实现、label 定义、backtest 规则和 robustness 报告，发现 repo 最清楚、最可迁移的其实就是 `combined_funding_spread` 这条规则基线。

### 2.1 规则基线到底怎么写的
`configs/models/baseline.yaml` 里有三条核心规则：
1. `funding_threshold_2bps`
2. `spread_zscore_1p5`
3. `combined_funding_spread`

其中最值得拿来做 desk baseline 的是第三条。源码 `src/funding_arb/models/baselines.py` 里实现得很直白：
- `funding_margin = funding_rate_bps - funding_threshold_bps`
- `spread_margin = spread_zscore_72h - spread_threshold`
- `decision_score = funding_margin + spread_margin`
- `signal_threshold = 0.0`
- 真正开仓条件不是“和大于 0 就行”，而是 **`funding_margin >= 0` 且 `spread_margin >= 0`**
- 若设置 `regime_column`，还要再叠加 `positive_funding_regime == 1`

默认参数也已经给出来：
- `funding_threshold_bps: 1.0`
- `spread_threshold: 1.5`
- `regime_column: positive_funding_regime`
- rule search 允许在 funding 阈值 `[0.5, 1.0, 1.5, 2.0]`、spread 阈值 `[1.0, 1.25, 1.5, 1.75]` 上做验证集搜索

这意味着 repo 并不是在说“黑箱模型才能抓到 funding alpha”，恰恰相反：**它先把 base alpha 用最朴素的规则写清楚，再让 ML / DL 去判断哪些样本更值得做。**

### 2.2 这条 alpha 的完整策略骨架是齐的
这也是这轮比纯文献摘要更有用的地方。repo 里 entry / exit / cost / sizing 都有明确实现：
- 默认方向：`short_perp_long_spot`
- 固定每腿 notional：`position_notional_usd`
- 信号在 `t` 观察，默认在 `t+1` 的 `open` 执行（`entry_delay_bars`）
- exit 支持：`signal_off`、`holding_window`、`maximum_holding`、`stop_loss_bps`、`take_profit_bps`
- 标签不是裸价格涨跌，而是未来 holding window 的 **post-cost net return**
- 成本显式建模：四腿 taker fee + slippage，再加 gas / borrow 等摩擦

所以这条线不是“指标片段”，而是一个可直接迁成 desk 最小实验的完整 skeleton。

### 2.3 但公开结果并不强，别把 zero-trade winner 当 alpha
repo 的诚实之处也在这里：**当前公开 `BTCUSDT 1h` 结果更像可复现 research intake，不像现成 production alpha。**

robustness report 里，`test` split 的 family comparison 有个很典型的误读风险：
- `combined_funding_spread`：`7` 笔交易，`cumulative_return = -0.002328`，平均每笔约 `-33.26 bps`
- `logistic_regression`：`3` 笔交易，`cumulative_return = -0.00105`
- `Deep Learning / lstm`：`0` 笔交易，但表头里却显示 `Best family under the base test-period configuration: Deep Learning`

这就是典型 **zero-trade winner / threshold issue**：
- 按累计收益排序，`0` 交易会看起来“最好”
- 但从 alpha 角度看，这不代表模型更强，只代表它几乎没给出可执行信号

所以这轮更合理的结论不是“DL > Rules”，而是：
1. **base alpha 可以明确表达**；
2. **规则 baseline 已足够构成最小可复现实验**；
3. **当前公开样本很 sparse，而且 BTCUSDT 1h 下并未跑出强结果。**

## 3. 为什么和当前项目有关
这条线和当前 desk 直接相关，原因有三层：

1. **它是 raw alpha，不是泛 filter。**
   base alpha 非常明确：`short rich perp + long spot`，赚 funding + basis convergence。

2. **它能直接映射到 short-cycle 研发，但不能假装成逐 bar directional signal。**
   真正自然的映射方式是：
   - `15m`：做主信号 / admission 层
   - `5m / 3m / 1m`：做子执行、排队、入场优化
   而不是把 funding 这种低频经济机制硬扭成 `1m` K 线方向预测。

3. **它补的是“规则型 baseline + 完整回测骨架”，不是再重复写一次 ML admission。**
   对 desk 来说，先把最可解释的 baseline 跑通，比上来就讨论 LSTM 更值钱。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / carry / delta-neutral
- 基础 alpha：`positive funding + positive spread dislocation` 共振时，`short perp + long spot` 更可能在未来持有窗兑现 `funding carry + basis convergence`
- regime：`positive_funding_regime == 1`
- filter / veto：`funding_rate_bps` 必须过阈值、`spread_zscore_72h` 必须过阈值；若用 repo 完整框架，还可叠 `min_expected_return_bps` / `confidence` / `shock` 过滤
- risk / sizing / execution overlay：next-bar open 执行；单策略同时最多一笔；固定每腿 notional；可用 `holding_window / maximum_holding / stop_loss_bps / take_profit_bps` 收口

## 4. 可复刻的最小实验
### 4.1 先做哪一版
最值得先做的是 **`15m` 主信号 + `5m` 子执行**，不是先做 `1m` 方向预测。

原因很简单：
- funding / basis 机制本身不是 `1m`-native alpha
- 但它完全可以作为 `15m` 级别的 raw alpha / admission shell
- 然后用更细颗粒度去优化 entry legging 与成本

### 4.2 最小实验口径
- 交易对：Binance `BTCUSDT` perp + `BTCUSDT` spot
- 主频率：`15m`
- 执行子频率：`5m`（若有能力再下钻 `3m/1m`）
- 主信号定义：
  - `funding_rate_bps >= 1.0`
  - `spread_zscore_72h >= 1.5`
  - `positive_funding_regime == 1`
- 时间映射：
  - `72h` z-score 在 `15m` 上对应 `288` 根 bar
  - `24h` hold 在 `15m` 上对应 `96` 根 bar
- 开仓：信号在 bar close 确认后，下一根 `15m` 或下一组 `5m` 子 bar 分批执行
- 平仓：先测三种——`signal_off`、固定 `24h`、`8h funding boundary 后退出`

### 4.3 一定要做的对照组
至少要同时跑这三组：
1. `funding-only`
2. `spread-only`
3. `combined_funding_spread`

因为这轮最关键的问题不是“模型谁更强”，而是：**到底是 funding 单独有用，还是一定要 funding 与 basis 共振才有 edge。**

### 4.4 先看哪些指标
先不要被 Sharpe 带跑，优先看：
- `net bps / trade`
- `trade count`
- `funding contribution` vs `basis convergence contribution`
- `cost ladder`（`1 / 2 / 4 / 6 bps`）
- `8h funding boundary` 前后分层表现

### 4.5 下一步怎么测
- **第一步：** 先在 `15m` 上复写 repo 规则 baseline，不加任何 ML。
- **第二步：** 把 exit 从“固定 24h”拆成 `signal_off`、`max_hold`、`post-funding exit` 三套，找哪种更接近真实 carry/basis 兑现节奏。
- **第三步：** 若 `15m` 有毛边，再只把 `5m/3m/1m` 用作 execution child layer：例如限制在 spread 回落一点、或 funding boundary 前后固定窗口入场，别把更快频率误当成新的主 alpha。
- **第四步：** 如果 BTC 仍然交易稀疏，再扩到 `ETHUSDT`、`SOLUSDT`，但前提是 spot/perp 数据同样公开可拿、成本口径能统一。

## 5. 风险与保留意见
- **当前公开结果偏弱。** 这条线现在更像“可复现 skeleton”，不是已经跑通的 desk alpha。
- **BTCUSDT 单资产太稀疏。** repo 的公开 baseline 在 test split 里交易笔数非常少，说明信号覆盖率不是小问题，而是主问题。
- **容易被 zero-trade 配置误导。** 任何 robustness / family comparison，只要出现 `0` trade winner，都不能直接当策略结论。
- **低频经济机制别伪装成高频方向。** 若后续下钻到 `1m/3m`，最合理的定位是 execution / scheduler，不是把 funding 机制硬解释成逐 bar directional predictor。

## 6. 来源
- MengerWen. (2026). *Deep Learning-Based Delta-Neutral Statistical Arbitrage on Perpetual Funding Rates*. GitHub Repo.  
  Repo URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
- MengerWen. (2026). *configs/models/baseline.yaml*.  
  Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/blob/main/configs/models/baseline.yaml`
- MengerWen. (2026). *src/funding_arb/models/baselines.py*.  
  Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/blob/main/src/funding_arb/models/baselines.py`
- MengerWen. (2026). *docs/labels.md*.  
  Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/blob/main/docs/labels.md`
- MengerWen. (2026). *docs/backtest.md*.  
  Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/blob/main/docs/backtest.md`
- MengerWen. (2026). *reports/robustness/binance/btcusdt/1h/report.md*.  
  Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/blob/main/reports/robustness/binance/btcusdt/1h/report.md`
- MengerWen. (2026). *reports/data_quality/binance/btcusdt/1h/report.md*.  
  Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/blob/main/reports/data_quality/binance/btcusdt/1h/report.md`

## 7. 本地产物
- Digest：`research/quant_digests/2026-04-15_0058_positivefunding-spreadzscore-deltaneutral-baseline.md`
