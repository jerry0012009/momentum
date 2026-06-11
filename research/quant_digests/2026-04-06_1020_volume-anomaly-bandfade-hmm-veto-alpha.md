# 别把这份 2025/2026 HMM thesis repo 只读成“危机熔断器”：对 short-cycle desk，更该先测的是「2.5σ band stretch × broad volume anomaly fade」，再把 HMM 当 crash veto

- 时间：2026-04-06 10:20 UTC
- 类型：2025/2026 GitHub thesis repo source audit（GitHub API metadata + `README.md` + `VEBB.txt` + `reactive_vebb.py` + `regime_detection.py` + `optimization_results.csv` + `multi_year_results.csv`）
- 主题类型：raw alpha
- 基础 alpha：**单资产 BTC 在 `15m` 上出现足够深的带外偏离（更像 `20-bar, 2.5σ` 的 stretch）且同时伴随“广义放量”时，后续更容易回到中轨；HMM 不是 alpha 本体，只是危机状态下的禁开仓 / 强平 veto。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/single-asset/btc/bollinger-band/volume-anomaly/vebb/hmm/regime-veto/circuit-breaker/15m/5m/3m/1m/repo/public-data/cost/risk
- 证据类型：repo 源码 + 参数网格 + 年度结果；属于工程证据，且源内存在指标口径不一致，适合偷结构，不适合直接信 headline 收益

## 1. 这次看了什么

这次看的是一个 **2025-12 创建、2026-01 更新** 的公开 GitHub thesis repo：**`AbeneilMagpantay/Adaptive-HMM`**。它表面上的 headline 是：

> 用 **Gaussian HMM** 给 BTC 的均值回归策略加一个危机 regime circuit breaker，尽量避免在 2025 这类高波动阶段被反复打脸。

但如果按我们当前 desk 的 intake 优先级来读，这份材料真正值得先收进素材池的，不是 “HMM 很高级”，而是更朴素的这一句：

> **base alpha = 带外 stretch 之后，不是立刻无脑抄底摸顶；而是只在“真的有异常参与度”的时候，去赌向中轨的回摆。**

这让它和最近几轮已经补过的 breakout / carry / pairs / OBI continuation 不同：
它补的是一个**单资产、可直接落地、偏反转侧**的 raw alpha 壳，而且天然可以拆成 `raw alpha + regime veto` 两层。

## 2. 核心结论

一句话版：

> **先把 HMM 放一边，这个 repo 最值钱的不是“预测 regime”，而是告诉我们：BTC 的 band-fade 是否成立，关键不在更精细的 `vol_z` 数值，而在“是否真的出现了宽口径的成交量异常”以及“是否避开危机状态”。**

它怎么证明这点？

- `optimization_results.csv` 给了 **729 组** 参数网格；
- 最优一簇结果几乎都落在 **`bb_mult = 2.5`、`atr_sl = 1.5`、`atr_tp = 1.5`**；
- **`vol_z = 1.5 / 2.0 / 2.5` 的平均值和最优值完全一样**，`cooldown 10 / 20 / 50` 影响也很小；
- 反而 `bb_mult` 从 `1.5 → 2.0 → 2.5` 时，平均收益明显改善（均值约 `-0.737% → -0.256% → -0.065%`）；
- `multi_year_results.csv` 又显示它非常吃 regime：`2018 +16.66%`、`2021 +11.22%`、`2023 +4.73%`、`2025 +2.84%`，但 `2024 -12.89%`，说明**这不是“永远有效的买跌卖涨”**，而是必须配状态过滤。

翻成人话：

1. **别把 volume z-score 阈值神化**——在这份实现里，它更像“有没有放量”的布尔确认，而不是一个需要精修到小数点后一位的核心参数；
2. **真正的 raw alpha 是更深的 band stretch + 异常参与度后的回摆**；
3. **HMM 的正确定位是 veto，不是主信号。**

## 3. 为什么这轮值得现在补它？

结合最近 digest 进展，我们已经连续补了不少：

- breakout / squeeze / conditional drift
- carry / funding / basis
- pairs / RV / cross-sectional
- LOB / order-flow / maker

但 **“单资产 mean reversion 的完整策略壳”** 相对还是少一点，尤其是这种：

- 不是纯 oversold 教程；
- 有明确定义的 `entry / exit / stop / cost / regime veto`；
- 能直接映射到 `15m`，再下钻到 `5m / 3m` 做 child execution；
- 而且还能服务别的反转类 alpha，作为 **shared admission layer**。

所以它不是在重复老 Bollinger Band 话题，而是在补一个更 desk-friendly 的判断：

> **如果 band-fade 要活下来，最先该测的不是 HMM 多厉害，而是 “stretch 要多深 + 放量口径怎么定义 + 哪些 regime 必须直接不做”。**

## 4. repo 里最该偷走的，不是 thesis 结论，而是这套拆法

### 4.1 raw alpha 本体：`2.5σ` stretch 比 `1.5σ/2.0σ` 更像样

参数网格给的最直接信息就是：

- `bb_mult = 2.5` 的均值和最优值都显著优于 `2.0` 和 `1.5`；
- 这说明对 BTC 这种波动资产，**浅 band touch 很容易只是趋势中的正常呼吸，不够形成可交易的 overextension。**

对 short-cycle desk 来说，这比“再找一个新指标”更重要：
**很多反转 alpha 死，不是因为反转不存在，而是 entry 太浅。**

### 4.2 admission layer：volume 要宽口径，不要迷信单一 z-score

repo 有两套实现：

- Python 回测脚本偏简单：`band touch + vol_z > 2`；
- Pine 版本已经进化成更宽的 volume family：`percentile / z-score / ratio / OBV` 的组合确认。

再结合 729 组网格，最有价值的启发反而是：

> **把“有没有异常参与度”做成宽口径 admission，可能比不断微调 `vol_z` 阈值更重要。**

这很适合我们 desk：
可以把 volume confirmation 设计成 shared module，后面既能接在这个 band-fade 上，也能接到别的 breakout-fail / exhaustion-fade / overreaction-revert 上。

### 4.3 overlay：HMM 要被当成 crash veto，不要伪装成 alpha

`reactive_vebb.py` 里 HMM 用的是：

- `gk_vol`（Garman-Klass volatility）
- `hurst`
- `log_ret`

训练 `3-state GaussianHMM`，然后：

- 只在最低波动 state 开仓；
- 若离开 safe regime 就强平；
- 若 `gk_vol` 超过训练样本 99 分位，触发 circuit breaker。

这层设计对我们有价值，但必须老实定位：

- **它服务于 raw alpha；**
- **它不是独立赚钱因子；**
- **它的 KPI 更该看 max drawdown、trade count collapse、crash-period loss containment，而不是单独年化。**

## 5. source audit：这份材料能用，但不能照抄业绩

这里必须记一笔：**repo 内部绩效口径不完全一致。**

例如：

- README 摘要写的是：volume filter 在 2024 calibration 里把 Profit Factor 从 `0.90 → 1.79`，但 2025 OOS 仍然 `-8.65%`；HMM 再把损失压到 `-1.30%`，并把回撤使用压低 `98.7%`。
- 但 `multi_year_results.csv` 又显示 `2025 +2.84%`；
- `metrics.json` 还是另一组接近持平的小结果。

这通常意味着：

- 不同脚本 / 不同样本窗口 / 不同 sizing 口径混在了一起；
- thesis narrative 和 repo 导出的最终表不完全同版。

所以这轮 digest 的结论不是“这 repo 已经证明能赚钱”，而是：

> **它已经足够证明我们该先复现一个 clean 的 `band stretch + broad volume anomaly + crisis veto` 壳。**

## 6. 对 `1m / 3m / 5m / 15m` 的最小实验怎么测

### 6.1 先做一个干净版 raw alpha

第一轮别急着上 HMM，先测 raw alpha：

- 标的：`BTCUSDT perp`
- 主周期：`15m`
- 入场：
  - long：`close <= lower_band(20, 2.5σ)` 且 `volume_percentile_100 >= 70`
  - short：`close >= upper_band(20, 2.5σ)` 且 `volume_percentile_100 >= 70`
- 出场：
  - 第一优先：回到中轨；
  - 备用：`1.5 ATR` 止损 / `1.5 ATR` 止盈；
  - time stop：`8~12 bars`
- 成本：双边 taker `4~5 bps` + 1 tick 滑点

先回答三个问题：

1. 不加 HMM 时，这条 raw alpha 还有没有正的 pre-cost drift？
2. 这条 edge 是只在 long 端活，还是 long/short 对称？
3. `2.5σ` 是否真的比 `2.0σ` 更稳，而不是只减少 trade count？

### 6.2 再把 regime veto 接上去

第二轮再接 overlay：

- 用 `15m` 数据训练 3-state HMM；
- 特征先从最简单的 `GK vol + rolling Hurst + log return` 开始；
- 只做两种动作：
  - `regime != safe`：禁新开仓
  - `GK vol > train_p99`：强平 / size=0

看三件事：

- trade count 是否被砍得太狠；
- 2024/2025 这类坏 regime 的回撤有没有显著改善；
- 改善来自真实 veto，还是单纯因为“不交易了”。

### 6.3 再下钻到 `5m / 3m / 1m`

最实用的 child execution 版本是：

- `15m` 负责生成 raw alpha 方向；
- `5m / 3m` 负责挑更好的入场价；
- `1m` 只做 execution veto（例如再破前低 / 前高就不接）。

也就是说，这条线最自然的映射不是“直接在 1m 上重新训一套 BB”，而是：

> **`15m` 定 stretch，`5m/3m` 吃回摆。**

## 7. 一句话结论

如果只拿一句结论走，我会写成：

> **这份 HMM thesis repo 最值得复现的，不是 HMM 本身，而是一个更朴素、也更可复刻的壳：`深 band stretch × 宽口径放量 admission → 向中轨回摆`；HMM 只负责在最坏 regime 里说“不做”。**

## 8. 来源与引用

1. **AbeneilMagpantay (repo owner) / 作者姓名在 README 中匿名化 (2025/2026), _Algorithmic Trading on Bitcoin with Market Microstructure Resilience Testing_**  
   - Venue: GitHub thesis repository / embedded thesis manuscript  
   - DOI: 无  
   - Readable URL: https://github.com/AbeneilMagpantay/Adaptive-HMM  
   - Repo URL: https://github.com/AbeneilMagpantay/Adaptive-HMM  
   - GitHub API metadata: https://api.github.com/repos/AbeneilMagpantay/Adaptive-HMM

2. **Core source files audited**  
   - README: https://raw.githubusercontent.com/AbeneilMagpantay/Adaptive-HMM/main/README.md  
   - Pine strategy: https://raw.githubusercontent.com/AbeneilMagpantay/Adaptive-HMM/main/VEBB.txt  
   - Python backtester: https://raw.githubusercontent.com/AbeneilMagpantay/Adaptive-HMM/main/reactive_vebb.py  
   - Regime detector: https://raw.githubusercontent.com/AbeneilMagpantay/Adaptive-HMM/main/regime_detection.py  
   - Optimization grid: https://raw.githubusercontent.com/AbeneilMagpantay/Adaptive-HMM/main/optimization_results.csv  
   - Multi-year summary: https://raw.githubusercontent.com/AbeneilMagpantay/Adaptive-HMM/main/multi_year_results.csv
