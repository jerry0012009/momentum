# 别把这份 2025 repo 只读成 ML basis demo：对 short-cycle desk，更该先测的是「spot-perp basis state × funding-pressure × delta-neutral flip」完整 raw alpha
- 时间：2026-04-04 15:25 UTC
- 类型：2025 GitHub repo source audit（`main.py` + `robbie/main.py` + `robbie/research.ipynb`）+ 2025 arXiv 摘要 grounding
- 主题类型：raw alpha
- 基础 alpha：**同标的 spot-perp basis 的未来 `6h` 变化，能被当前 basis level / z-score / basis momentum / funding pressure / ETH cross-basis 等状态变量部分预测；据此做 `long basis = long perp + short spot` 或 `short basis = short perp + long spot` 的 delta-neutral 头寸，吃的是 basis drift / reversion 本身，而不是裸方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/basis/spot-perp/delta-neutral/xgboost/lstm/ensemble/funding-pressure/basis-zscore/vol-targeting/time-stop/drawdown-stop/btc/eth/binance/1h/15m/5m/3m/1m/repo/paper/public-data/cost/risk
- 证据类型：开源代码仓 + 训练 notebook + arXiv 摘要

## 1. 这次看了什么
这轮我故意没再补一篇“又一个 pairs / copula / OFI 变体”，而是收一条**不同家族的 raw alpha**：

- **Robbie Walmsley / Rbach24 (2025)**，GitHub repo：`CryptoMeanBasisReversionStrat`
  - Repo URL：<https://github.com/Rbach24/CryptoMeanBasisReversionStrat>
  - 最近提交：`b86fa60`，提交时间 `2025-11-17T19:10:31-05:00`
  - 关键文件：
    - <https://raw.githubusercontent.com/Rbach24/CryptoMeanBasisReversionStrat/main/main.py>
    - <https://github.com/Rbach24/CryptoMeanBasisReversionStrat/blob/main/robbie/main.py>
    - <https://github.com/Rbach24/CryptoMeanBasisReversionStrat/blob/main/robbie/research.ipynb>
- **Hyungbin Park, Minhyung Choi, Anran E. B. Lim (2025)**，*Designing funding rates for perpetual futures in cryptocurrency markets*
  - arXiv：<https://arxiv.org/abs/2506.08573>
  - DOI：<https://doi.org/10.48550/arXiv.2506.08573>

我这次要 intake 的不是“机器学习能不能统治 basis 交易”这种空话，而是 repo 里已经写出来的一条**完整可下场的 delta-neutral basis shell**：

> **用 basis / funding / cross-asset 状态去预测下一段 basis 会扩大还是收敛，然后切换 `long basis` 或 `short basis` 书。**

这点很关键，因为它符合这轮优先级里最值钱的那档：
**可独立复现、可直接落地为完整策略（entry / exit / sizing / risk / cost）的 raw alpha。**

## 2. 这条东西的 base alpha 到底是什么
先把 base alpha 说清楚：

> **base alpha = spot-perp basis 的短期状态依赖型可预测性。**

不是：
- 单纯收 funding；
- 单纯赌方向；
- 单纯看到 basis 大就机械均值回归。

而是：
1. 先把当前市场状态压成一组特征：
   - `basis`
   - `basis_mean_48h`
   - `basis_std_48h`
   - `basis_zscore`
   - `basis_change_1h`
   - `basis_change_24h`
   - `basis_momentum`
   - `funding_rate / funding_pressure`
   - `eth_basis / ethbtc_ratio`
   - spot / perp return、波动、量比、时段信息
2. 预测未来 `6h` 的 `basis_change`；
3. 若预测 basis 上行，开 **long basis**：`long perp + short spot`；
4. 若预测 basis 下行，开 **short basis**：`short perp + long spot`；
5. 用 time stop / drawdown stop / conviction threshold 把它收成完整策略。

所以这不是 filter，也不是 overlay 伪装货；它本身就是一条**delta-neutral raw alpha**。

## 3. 为什么这条分支现在值得补进素材池
因为它补的是我们当前库里相对少的一块：

- 不是传统 `positive basis only` carry；
- 不是只做 `basis z-score` 单阈值回归；
- 不是跨币 pair / basket；
- 而是**同标的、同 venue、双腿对冲下的 basis state classifier / regressor**。

翻成人话：

> **这条线在问的不是“basis 长期有没有回归”，而是“在这个状态下，接下来几小时的 basis 更可能扩还是收”。**

这比“正 funding 就一直收”更像交易策略，比“basis 偏太多就反手”也更完整，因为它已经明确把：
- entry
- exit
- sizing
- drawdown stop
- time stop
- fee / slippage

全塞进代码里了。

如果这条壳跑得动，它会自然长出两条 desk 很实用的旁支：
1. **basis state routing**：什么状态下做 widening，什么状态下做 convergence；
2. **execution-aware veto**：同一个预测，在 `1m/3m/5m/15m` 哪个执行层最不容易被成本吃掉。

## 4. repo 里真正值钱的硬信息

### 4.1 不是一个 feature toy，而是一条完整策略壳
`robbie/main.py` 里的 richer 版本，已经把策略骨架写得很完整：

- **目标 horizon**：`prediction_horizon = 6`（小时）
- **lookback**：`168h`
- **LSTM sequence_length**：`24`
- **模型**：`XGBoost + LSTM ensemble`
- **conviction**：`tanh(ensemble_pred * 10)`
- **开仓阈值**：`conviction_threshold = 0.05`
- **平仓阈值**：`exit_conviction_threshold = 0.025`
- **最长持有**：`12h`
- **单笔最大回撤止损**：`5%`
- **最大杠杆**：`2x`
- **波动率 cap**：`0.5`
- **费用假设**：`maker 2bps / taker 4bps / slippage 2bps`
- **交易所最小 notional**：`5 USDT`

这意味着它不是“只有 alpha 没有壳”，而是已经天然适合被 desk 拆成：
- signal layer
- sizing layer
- kill-switch layer
- cost layer

### 4.2 feature set 对 short-cycle desk 很友好
training notebook 里定义了 **26 个特征**，最重要的几类是：

#### A. basis 本体
- `basis`
- `basis_mean_48h`
- `basis_std_48h`
- `basis_zscore`
- `basis_change_1h`
- `basis_change_24h`
- `basis_momentum`

#### B. funding / carry pressure
- `funding_rate`
- `funding_rate_ma24h`
- `funding_rate_std24h`
- `funding_rate_change_1h`
- `funding_pressure`

#### C. cross-asset context
- `eth_basis`
- `ethbtc_ratio`

#### D. price / vol / volume state
- spot / perp `1h` return
- spot / perp `24h` return
- spot / perp `24h` vol
- spot / perp volume ratio
- `hour_of_day`
- `day_of_week`

这组特征的好处是：

> **绝大部分都能直接映射到 `15m/5m` 版本，不需要私有数据，也不需要 order-book depth 才能开工。**

### 4.3 notebook 至少给了“作者打算怎么验”的门槛
`robbie/research.ipynb` 里没有保存最终输出，但它把作者想要满足的训练门槛写得很明确：

- `prediction_horizon = 6` 小时
- 训练窗口：建议至少 **2 年 hourly** 数据（示例 `2020-01-01 ~ 2023-12-31`）
- XGBoost 目标：
  - `n_estimators = 100`
  - `max_depth = 3`
  - `learning_rate = 0.05`
  - `subsample = 0.8`
  - `colsample_bytree = 0.8`
- notebook 中还写了硬断言：
  - `test_mse < 0.001`
  - `test_dir_acc > 0.52`

这些断言**不等于已经被证明达成**，但至少说明作者 intended benchmark 是：

> **如果 6h basis 方向准确率没有超过 52%，这条线在他自己的标准里都不算过关。**

对我们来说，这已经足够做第一轮 replication gate。

## 5. 这条东西最重要的 source-audit 发现

### 5.1 repo 根目录版本和 `robbie/` 版本不一致，不能盲跑
这是我这轮最在意的点。

根目录 `main.py` 是一个简化版 `RandomForestClassifier` 策略；而 `robbie/main.py` 是更完整的 `XGB + LSTM ensemble` 版本。两者不只是复杂度不同，**连交易方向的实现都不一致**：

- 根目录版：`pred == 1`（未来 basis 上升）时，代码却执行 `short future / long spot`
- `robbie/` 版本：`conviction > 0` 时执行 `long perp / short spot`

也就是说：

> **根目录版和 notebook / richer main 的 target 定义并不完全同向，直接抄根目录版有信号符号写反的风险。**

这件事很重要，因为它决定了这份 repo 不能被当成“开箱即用结论”，而应被读成：
- **好的地方**：完整壳和 feature map 很值钱；
- **危险的地方**：canonical version 必须先选定，根目录版大概率不能直接拿来生产化。

### 5.2 funding 特征在数据不可得时会被置零
`robbie/main.py` 里如果 funding data 不可用，会把以下特征全置为 `0.0`：
- `funding_rate`
- `funding_rate_ma24h`
- `funding_rate_std24h`
- `funding_rate_change_1h`
- `funding_pressure`

这意味着：

> **如果你复现时没把 funding 历史真正接进来，策略会从“basis + funding state alpha”退化成“basis-only alpha”，结果不是同一条东西。**

### 5.3 sizing 规则对短周期移植时需要降杠杆
源码的 sizing 是：
- 先用 `expected_move / realized_vol` 算 `move_vol_ratio`
- 再乘 `|conviction|`
- 最后把 position value 截断在 `[5%, 50%] portfolio` 之间

这个壳对 `1h` 也许还能接受，但如果直接搬到 `15m / 5m`，很容易太激进。

所以这条线虽然是完整策略，但在 short-cycle desk 上，**第一件事不是卷模型，而是先缩 sizing。**

## 6. 对 `1m / 3m / 5m / 15m` 的最小可复现实验怎么做

### 6.1 数据源
全部公开可得：
- Binance Spot klines（`BTCUSDT`, `ETHUSDT`）
- Binance USDⓈ-M perpetual klines / mark price klines（`BTCUSDT`, `ETHUSDT`）
- Binance funding rate history

### 6.2 第一版频率建议
我不建议一上来就冲 `1m` 训练。

更合适的是：
- **训练 / 发现层**：`15m`
- **执行层**：`5m` 或 `1m`

把原 repo 的 `1h` 时钟改写成：
- `48h mean/std` → `12h mean/std`（即 `48` 根 `15m` bar）
- `6h horizon` → `8` 根 `15m` forward basis change
- `24h return/vol` → `96` 根 `15m` 聚合
- funding 特征用**最近一次 funding 值前向填充**

### 6.3 baseline 要怎么设
第一版至少对比三条：

1. **plain basis z-score MR**
   - `basis_z > +z` 做 short basis
   - `basis_z < -z` 做 long basis

2. **funding-only sign rule**
   - funding 明显正：偏向 short basis / carry
   - funding 明显负：偏向 long basis 或空仓

3. **repo 版 basis-state model**
   - 用简化版 `XGBoost` 即可，不必一开始就上 LSTM
   - `pred > q80` 做 long basis
   - `pred < q20` 做 short basis
   - 其余空仓

### 6.4 交易壳建议
先用最朴素的：
- **entry**：预测分位超过阈值
- **exit**：预测回到中性区 / horizon 到期 / max adverse move 触发
- **sizing**：固定美元 notional，先别学 repo 里的高杠杆 vol sizing
- **cost**：双腿各算 fee + 保守滑点
- **risk**：
  - funding shock veto
  - basis gap veto
  - 单边腿成交量不足 veto

## 7. 为什么它比继续补传统 basis / carry 更值得
因为这次补的是一个更一般化的母壳：

> **不是“basis 大了就回”，也不是“funding 正了就拿”，而是把 basis 交易写成可分类的状态空间问题。**

这会同时服务两类后续研发：
1. **raw alpha 主线**：basis widening / narrowing 的双向交易；
2. **shared gate 支线**：把 `basis_state` 当成别的策略的 veto / sizing router。

而且它跟现在 desk 的 `1m/3m/5m/15m` 节奏是兼容的：
- 信号可以慢一点；
- 执行可以快一点；
- 结构上也足够简单，第一版不需要私有逐笔数据。

## 8. 下一步怎么测

### Step 1：先做 `15m` 的无 LSTM 最小复刻
不要一开始就复刻整个 ensemble。

先做：
- `XGBoost`
- 只保留 `basis / basis_z / basis_change / funding / eth_basis / ethbtc_ratio`
- target = `8` 根 `15m` 之后的 basis change

先回答一个最硬的问题：

> **在成本后，这组状态变量能不能把 future basis move 的方向准确率推到 `>52%` 左右？**

### Step 2：做 `state bucket` 归因
重点看四个桶：
- 高正 z + 高 funding pressure
- 高正 z + 低 funding pressure
- 高负 z + 高 funding pressure
- 高负 z + 低 funding pressure

想看清楚：
- 哪些桶更像 continuation；
- 哪些桶更像 mean reversion。

这一步会决定你最后是做单一 basis MR，还是做双向 state router。

### Step 3：把 `robbie/` 版和根目录版做 sign audit
这一步必须做，不然后面全是脏结论。

至少确认：
- target label 符号
- pred 符号
- `long basis / short basis` 的真实盈亏方向
- funding cashflow 在回测里有没有加对

### Step 4：单独测 funding 特征的增量价值
做两个模型：
- `basis-only`
- `basis + funding`

如果 funding 版没有稳定增量，那就别把策略复杂化。

### Step 5：执行层再下钻到 `5m / 1m`
只有当 `15m` discovery 层先过关，再做：
- maker 优先 vs taker 直接吃
- 事件后延迟 `1 bar / 2 bar` 再入场
- funding 结算前后 `30m / 60m` 特殊处理

## 9. 我对这条题的结论
如果把 repo 当成“已验证 ML alpha”，那是高估；
但如果把它当成 **一条已经把 signal / sizing / risk / cost 写成完整骨架的 basis raw alpha 候选**，它是合格的，而且值得进研究池。

最重要的是：

1. **base alpha 清楚**：spot-perp basis future change 的可预测性；
2. **可以独立复现**：公开数据足够；
3. **可以直接落地成完整策略**：源码已经把 entry/exit/sizing/risk/cost 写出来；
4. **和当前短周期 desk 直接相关**：先做 `15m discovery + 5m execution` 非常自然；
5. **有明确下一步**：先做 sign audit，再做 `basis-only vs basis+funding` 的 15m 最小复刻。

我会把这条东西定义成：

> **“basis state classification / regression” 这条 delta-neutral raw alpha 母壳。**

它不是当前素材池里最硬的一条，但足够新、足够完整、足够能快速验证，值得收。

## 10. 参考来源
1. **Rbach24 / Robbie Walmsley (2025). _CryptoMeanBasisReversionStrat_. GitHub.**  
   Repo：<https://github.com/Rbach24/CryptoMeanBasisReversionStrat>
2. **Raw source – simplified root version**  
   <https://raw.githubusercontent.com/Rbach24/CryptoMeanBasisReversionStrat/main/main.py>
3. **Raw source – richer strategy version**  
   <https://github.com/Rbach24/CryptoMeanBasisReversionStrat/blob/main/robbie/main.py>
4. **Training notebook**  
   <https://github.com/Rbach24/CryptoMeanBasisReversionStrat/blob/main/robbie/research.ipynb>
5. **Park, H., Choi, M., & Lim, A. E. B. (2025). _Designing funding rates for perpetual futures in cryptocurrency markets_. arXiv.**  
   DOI：<https://doi.org/10.48550/arXiv.2506.08573>  
   URL：<https://arxiv.org/abs/2506.08573>

## 11. 文件与页面
- Digest：`research/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.html`
