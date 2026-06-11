# 别把这篇 2025 Informer 论文只读成“Transformer 打败 MACD”：对 desk 更该先测的是「direction-aware loss × thresholded long/short state machine」BTC 单币 raw alpha
- 时间：2026-03-29 23:25 UTC
- 类型：2025 arXiv 全文 PDF + 本地全文抽取 + 公开 GitLab 复现框架审阅
- 主题类型：raw alpha
- 基础 alpha：**BTC 单币短窗 directional drift**——用最近一段价格路径、波动、时间特征与低频风险状态去预测下一 bar 收益，并只在预测幅度足够大时进入 `long / short / flat` 状态机
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/directional/next-bar/threshold-state-machine/direction-aware-loss/gmadl/informer/btc/binance/5m/15m/30m/1m/3m/paper/repo/public-data/cost
- 证据类型：全文规则 + 表格级结果 + 公开代码仓库

## 1. 这次看了什么
这次看的是 **Filip Stefaniuk, Robert Ślepaczuk (2025)** 的 arXiv 论文 **_Informer In Algorithmic Investment Strategies on High Frequency Bitcoin Data_**，以及作者公开的 GitLab 复现仓库。论文研究对象很集中：

- 标的：`BTC/USDT`
- 数据：Binance 公共 kline
- 频率：`5m / 15m / 30m`
- 核心动作：先预测下一 bar return，再把预测值映射成 `long / short / flat`
- 对照组：Buy & Hold、MACD、RSI、Informer+RMSE、Informer+Quantile、Informer+GMADL

如果只把它读成“Informer 比传统指标强”，价值其实一般；但对当前 desk 真正值钱的是，它把一条 **可直接写成 entry / exit / cost / 评估框架** 的短窗 directional alpha 讲清楚了，而且还给出一个很重要的 desk 启发：

> **在高频/更短 bar 上，问题不只是模型好不好，而是 loss function 有没有把“方向”和“大波动尾部样本”学对。**

换句话说，这篇东西更像一张 **direction-aware loss / abstain threshold / 高频成本生存** 的实验卡，而不是一篇“再上更大模型”的论文。

## 2. 核心结论
- **一句话结论**：这篇东西的 base alpha 很清楚——**BTC 存在可交易的短窗 directional drift**，但必须先做 **预测幅度阈值过滤**，只在模型认为下一 bar 有足够净边时才入场；而在更短频率上，普通 RMSE 训练出来的预测会越来越“缩到 0 附近”，最后被成本吃死。
- 论文最关键的不是 Informer 本身，而是 **GMADL（Generalized Mean Absolute Directional Loss）** 这一类 direction-aware loss。作者的结论非常直接：
  - `RMSE` 模型到了更高频会因为怕大错，输出越来越保守，很多预测都小到过不了手续费；
  - `Quantile` 版则过度活跃，频繁交易，被成本拖死；
  - **`GMADL` 版反而随着频率提高表现更好。**
- 全样本测试期（2019-08-21 到 2024-07-24，滚动 `24m in-sample + 6m out-of-sample`，共 6 个窗口）里，**GMADL Informer** 的总体验证结果是：
  - `30m`：`ARC 31.79%`，`MD 53.35%`，`IR** 0.516`，`811` 次交易；
  - `15m`：`ARC 49.65%`，`MD 47.39%`，`IR** 0.987`，`362` 次交易；
  - `5m`：`ARC 115.88%`，`MD 32.66%`，`IR** 7.552`，`846` 次交易。
- 对照的 **Buy & Hold** 基本不变：
  - `30m`：`ARC 13.12%`，`MD 77.20%`
  - `15m`：`ARC 13.10%`，`MD 77.23%`
  - `5m`：`ARC 13.14%`，`MD 77.31%`
  也就是说，论文里最强分支不是“更大收益换更大回撤”，而是 **在 5m 上同时抬高收益、显著压低回撤**。
- 更有意思的是 **RMSE vs GMADL 的频率方向完全相反**：
  - `RMSE Informer (30m)` 还有 `ARC 40.37%`；
  - 到 `15m` 只剩 `ARC 14.93%`；
  - 到 `5m` 直接掉到 `ARC -13.88%`，而且整段只交易 `16` 次。
  这不是“模型弱”，而是 **目标函数让模型在高频里不敢出手**。
- 论文用了严格的滚动样本评估，还对优于 B&H 的策略做了 t-test；`GMADL (5m/15m/30m)` 全部在 `p < 0.01` 下拒绝“IR 不优于 B&H”的原假设。

## 3. 为什么和当前项目有关
这轮应该优先补 **可独立复现的 raw alpha**，而不是再补一层解释型 filter。这篇东西值得进素材池，原因有四个：

1. **频率非常贴 desk。** 它不是日频论文硬往分钟上套，而是直接在 `5m / 15m / 30m` 上做；
2. **base alpha 清楚。** 它不是“端到端黑箱配收益曲线”，而是很明确的 `next-bar return forecast -> thresholded state machine`；
3. **完整策略口径齐。** 论文明确写了持仓状态、手续费、滚动样本拆分、阈值网格、交易次数、long/short 占比；
4. **最值得偷的分支不是 Informer，而是 loss + gate。** 这意味着我们不必第一步就复现 Transformer，也能先做一个 desk 版最小实验。

更直接地说，这篇东西给 desk 的不是“用 Informer 才能赚钱”，而是：

> **短周期 directional alpha 要想穿过成本，核心也许不是把模型做得更复杂，而是让训练目标和交易目标一致：方向对、尾部样本对、没把所有预测都缩成 0。**

## 3.5 策略拆解（必填）
- 方向属性：BTC 单币 long/short/flat directional strategy
- 基础 alpha：短窗 `next-bar directional drift`
- regime：无单独硬性市场 regime；但输入中显式加入了 `VIX / Fed Funds / Fear&Greed / hour / weekday`，本质上是在把宏观风险状态与时钟状态喂给预测器
- filter / veto：
  - **预测幅度阈值** 是核心 admission gate；
  - 若预测值不过阈值，则保持 `flat` 或维持旧仓；
  - 高频下最重要的 veto 其实就是 **成本阈值**：预测小到不足覆盖 fee/slippage，就不应交易。
- risk / sizing / execution overlay：
  - 论文原始设定是 **单标的、满仓、不可分仓**；
  - 允许 `long / short / flat` 三状态；
  - 仓位切换按上一 bar 收盘成交；
  - 每次 position change 收 `0.1%` 交易费；
  - 到期必须平仓；
  - 论文没有额外止损/波动目标层，核心风控来自 **阈值过滤 + 可空可平**。

## 4. 论文里真正值得 desk 先偷哪一段
我不建议第一步就全量复现 Informer。对当前 desk，最应该先偷的是下面这个更小、更诚实的分支：

### **direction-aware loss × thresholded state machine**
也就是：
1. 用近端价格路径与少量状态变量预测下一 bar return；
2. 但训练目标不要只最小化 MSE/RMSE，而要更强调 **方向正确性 + 大振幅样本**；
3. 交易时不连续调仓，而是通过阈值把预测映射成 `long / short / flat`；
4. 只在预测足够大、扣成本后还有边时出手。

这比“复现 Informer 架构细节”更适合 desk 的原因是：
- 可快速实验；
- 更容易 ablation；
- 更容易移植到 `1m / 3m / 5m / 15m`；
- 更容易回答：**edge 到底来自模型结构，还是来自 loss / threshold / abstain 机制？**

## 5. 可复刻的最小实验
### 5.1 先复现什么
先不要上全套 Informer。先做一个 **两模型对照 + 同一状态机** 的最小实验：

- 标的：`BTCUSDT` perp（Binance / OKX 任一公共可得）
- 频率：先 `15m`，再下钻 `5m`，最后才考虑 `3m`
- 训练框架：滚动 `24m train+val / 6m test`
- 预测目标：下一 bar return
- 模型对照：
  1. `baseline`：线性 / LightGBM / 小型 MLP + `MSE`
  2. `direction-aware`：同样特征、同样架构，但把 loss 改成 **强调方向与大振幅样本** 的 GMADL-like 目标

### 5.2 特征先怎么抄
第一版不需要花哨，直接抄论文里最能迁移的一组：
- OHLCV
- 当前 return
- `1h / 1d / 7d` realized vol
- `SMA / EMA / MACD / RSI / Bollinger` 比率化特征
- `hour / weekday`
- 若数据方便，再加：`fear & greed`、`VIX`、`Fed Funds` 的 last-known value

这里最重要的是：**保持特征集不变，先只改 loss。** 这样才能把“方向型 loss 是否真能救高频 edge”单独测出来。

### 5.3 entry / exit
直接沿用论文的状态机思路：
- `enter long`: 预测 return `> +threshold`
- `enter short`: 预测 return `< -threshold`
- `exit long`: 预测回落到 `exit_long`
- `exit short`: 预测回升到 `exit_short`
- 若无 exit 条件，则持有到反向信号或样本结束

论文阈值网格就是很好的起点：
- `enter long`: `0.001 ~ 0.007`
- `enter short`: `-0.001 ~ -0.007`
- `exit long`: `-0.001 ~ -0.007`
- `exit short`: `0.001 ~ 0.007`

也就是 roughly `10~70 bps` 的预测收益门槛。这个口径对 `5m/15m` 很重要，因为它天然在问：**模型给出的边，够不够覆盖 frictions？**

### 5.4 sizing / risk / cost
论文是满仓，但 desk 第一轮更稳的做法：
- sizing：先 `1x notional` 固定仓，不加杠杆，不做仓位放大
- 单标的只允许一个方向持仓
- 成本至少做两档：
  - `paper-like`: round-trip `20 bps`（近似论文 `0.1%` 单次换仓）
  - `desk-like`: maker/taker + slippage 分开估，先测 `4 / 8 / 12 bps` round-trip
- 风险：
  - 连续亏损 / 波动急升时可加一个 `vol veto`，但放在第二轮；
  - 第一轮先别加太多 overlay，免得把 raw alpha 本体洗掉。

### 5.5 最先看什么
先盯四个问题：
1. **direction-aware loss 是否真的比 MSE 在 `5m/15m` 更能留住非零预测？**
2. 预测值分布有没有从“全缩在 0 附近”变成“尾部更厚、可过成本门槛”？
3. 同样阈值下，交易次数、hit rate、avg trade、holding time 怎么变？
4. 若方向型 loss 的优势只出现在高 friction 前，那它不是 alpha；若在保守 friction 后还活，那才值得往下钻 `3m/1m`。

## 6. 风险与边界
- **这篇东西是单币 raw alpha，不是组合 alpha。** 当前价值在于补一张 BTC directional card，不是给出可直接扩到 whole-book 的统一框架。
- 论文的最好结果出现在 `BTC/USDT` 单标的，不能自动外推到 ETH 或 alt；
- 论文用的是 Binance spot kline，desk 真跑 perp 时还要重新计 funding、盘口深度、夜间滑点；
- 低频外生变量（VIX、Fed、Fear&Greed）在论文里是 last-known value，别把它们误读成高频主信号；它们更像状态增强特征；
- 最重要的一点：**如果复现实验发现 edge 主要来自阈值稀疏交易，而不是 loss 改进，那真正该搬的是 admission rule，不是 Informer。**

## 7. 来源
1. **Stefaniuk, Filip; Ślepaczuk, Robert (2025), _Informer In Algorithmic Investment Strategies on High Frequency Bitcoin Data_**  
   - Venue: arXiv  
   - DOI: N/A  
   - Readable URL: https://arxiv.org/abs/2503.18096  
   - PDF URL: https://arxiv.org/pdf/2503.18096.pdf  
   - Repo URL: https://gitlab.com/FilipStefaniuk/wne-msc-thesis
2. **Michańków et al. (2024), GMADL loss related reference cited by the paper**  
   - Venue: paper-cited loss design reference inside the study  
   - DOI / readable URL: see bibliography in arXiv paper  
   - Repo URL: N/A
3. **Zhou et al. (2021), _Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting_**  
   - Venue: AAAI / arXiv lineage  
   - Readable URL: https://arxiv.org/abs/2012.07436  
   - Repo URL: https://github.com/zhouhaoyi/Informer2020
4. **Supplementary implementation repo cited by the paper**  
   - Repo URL: https://github.com/martinwhl/Informer-PyTorch-Lightning

## 8. 下一步怎么测
1. **先不复现全套 Informer，先复现同一状态机下的 `MSE vs direction-aware loss` 对照。**
2. 第一轮只做 `BTCUSDT 15m`；若成本后还活，再做 `5m`；`3m/1m` 放到最后。 
3. 先固定特征集，只改 loss；再固定 loss，只改阈值网格，避免把“模型差异”和“admission 差异”混成一团。 
4. 若 `direction-aware loss` 主要把预测分布尾部拉开、并显著改善成本后 avg trade，这条线就值得继续；反之就把结论写死：**真正值钱的是 threshold abstain，不是复杂模型。**
5. 如果 `15m` 存活而 `5m` 崩掉，别硬追更快频；直接把它定位成 **`15m` 主 directional alpha + `5m` execution timing`**，而不是伪装成 1m 高频 edge。