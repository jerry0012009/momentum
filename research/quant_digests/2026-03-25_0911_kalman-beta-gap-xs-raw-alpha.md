# 别把 alt 对 BTC 的 β 偏离只当风险归因：这份 2026 新仓库更值得先测的是「Kalman β-gap 横截面 raw alpha」，但短周期先被换手吃掉
- 时间：2026-03-25 09:11 UTC
- 类型：2026 GitHub 新仓库 + Binance Futures 公共 `5m/15m` K 线最小快检 + 经典 Kalman / dynamic-beta 文献地基
- 主题类型：raw alpha
- 基础 alpha：cross-sectional / relative-value —— alt 对 BTC 的短窗 realized beta 相对 Kalman beta 的偏离会回归；低于“应有 beta”的币倾向补涨，高于“应有 beta”的币倾向回吐
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前 `5m/15m` 裸做口径下未过 turnover / cost 生存线）
- 主题标签：raw-alpha/cross-sectional/relative-value/beta-gap/kalman/dynamic-beta/market-neutral/alt-btc/cost-survival/turnover/binance/perpetual/5m/15m/repo/paper
- 证据类型：仓库代码 + 公共行情最小快检 + 经典文献地基

## 1. 这次看了什么
先回答 base alpha：**不是 filter，本体就是一条横截面 raw alpha**。

这次主看的是 **VedantUpasani46/Alpha-Research-Discovery** 里 `alpha_10_kalman_dynamic_beta.py` 这条分支。它不是再去猜“BTC 下一根涨跌”，而是问：

> **同一时刻，哪些 alt 对 BTC 的反应“过头了”，哪些“反应不够”？**

仓库原始写法是日频股票/crypto 通用版，但对我们 desk 更值钱的不是照抄日频，而是把它翻成短周期 desk 语言：

- 用 `BTCUSDT` 作为 market proxy；
- 对每个 alt 估 `β_Kalman`（更平滑、更像“应有 beta”）；
- 再用短窗 realized beta 去看它此刻到底是 **over-reacted** 还是 **under-reacted**；
- 做横截面多空，而不是做单币方向预测。

这正好补当前素材池里相对少的一块：**不是 return-only momentum / reversal，也不是 funding/basis/pairs，而是“市场敏感度错位”的 relative-value raw alpha。**

## 2. 核心结论
- **一句话结论：** 这条线在 Binance perp 的 `5m/15m` 上，**横截面排序信息是有的，但“每根 bar 都重平衡”的裸做法会被换手和成本先吃掉**；因此它更像一条值得继续推进的 **event-driven / thresholded raw alpha 候选**，而不是可以直接全天候硬跑的现成成品。
- 我按仓库同构思路，把它压到 Binance USDT perp 公共数据上做了最小快检：
  - 市场腿：`BTCUSDT`
  - 交易腿：`ETH / SOL / XRP / BNB / DOGE / ADA / LINK / AVAX / LTC / TRX`
  - `15m` 主样本近 **45d**，`5m` 补样本近 **18d**
  - `15m` 用 `12 bars` 的 realized beta，`5m` 用 `24 bars`
  - 信号：`alpha_i,t = -rank(beta_realized_i,t - beta_kalman_i,t)`
  - 组合：每根 bar 做 top/bottom `30%` 等权 long-short，round-trip 成本先按 **8 bps**
- 关键数据点（本地最小快检）：
  1. **`15m` 1-bar 持有：** mean IC 约 **`+1.38%`**，IC 正值占比约 **`51.8%`**；但 naive long-short **net 约 `-2.36 bps/bar`**。  
  2. **`15m` 4-bar 持有：** mean IC 反而升到 **`+1.77%`**，IC 正值占比约 **`52.5%`**；但 net 仍约 **`-1.78 bps/bar`**。  
  3. **`5m` 口径：** mean IC 大致仍在 **`+1.23% ~ +1.33%`** 区间，但 naive long-short net 约 **`-1.39 ~ -1.55 bps/bar`**，说明信号不是完全没边，问题主要出在 **频率 × 换手 × 成本**。
- 翻成人话：**它不像“完全伪信号”，更像“有排序力，但你如果每根都追着调仓，就先把 edge 交给手续费和滑点”。**

## 3. 为什么和当前项目直接相关
- 这条 intake 仍然满足当前优先级：**raw alpha > filter / regime / overlay**。base alpha 很清楚，不需要伪装成 gate。
- 它补的是当前 desk 里一个还没堆厚的方向：
  - 不是单资产方向；
  - 不是 funding/basis/价差回归；
  - 也不是普通 return momentum / loser reversal；
  - 而是 **“市场 beta 错位 → 横截面补涨/回吐”** 这类相对价值信号。
- 这也让它比继续补一篇 funding/basis 更值得：**它扩的是 raw-alpha 家族的维度，而不是在现有家族里继续内卷。**
- 另外，它天然可拆成完整策略组件：
  - entry：按 `β-gap` 排序建仓
  - exit：固定持有 `1/2/4 bars` 或直到 `β-gap` 回到零附近
  - sizing：横截面等权 / inverse-vol / beta-neutral
  - risk：BTC 冲击黑窗、单币权重上限、流动性过滤
  - cost：fee + spread + re-hedge turnover 显式入账

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / market-neutral / relative-value
- 基础 alpha：
  - 若某币 `beta_realized < beta_kalman`，说明它相对 BTC **短窗反应偏慢**，倾向补涨；
  - 若某币 `beta_realized > beta_kalman`，说明它 **短窗反应偏头**，倾向回吐。
- 最小公式：
  - `beta_gap_i,t = beta_realized_i,t - beta_kalman_i,t`
  - `signal_i,t = -rank(beta_gap_i,t)`
- entry：
  - 每个 bar 只在 `|beta_gap_z| >= z_enter` 的币上参与；
  - long 最低 `beta_gap` 分位，short 最高 `beta_gap` 分位；
  - 第一轮别做全量轮动，优先测 `top/bottom 2~3 names + threshold`。
- exit：
  - 固定持有 `1/2/4 bars`；
  - 或 `beta_gap` 回到 0 附近即平；
  - 可加 `time stop`，避免把短周期 relative-value 拖成方向暴露。
- sizing：
  - 第一轮 `equal-notional`；
  - 第二轮加 `inverse-vol` 或 `beta-neutral gross cap`；
  - 单币上限建议先 `<= 25% gross`。
- risk：
  - BTC 极端单 bar 冲击时先单独分 bucket，不和常规 bar 混算；
  - 流动性不足币种排除；
  - 若 cross-sectional dispersion 太低则不开机。
- cost：
  - 这条线对换手敏感，必须把 `4 / 8 / 12 bps` 做成显式成本阶梯；
  - 若未来走 event-driven 版本，再单独复核“触发次数下降后 net 是否转正”。

## 4. 可复刻的最小实验
### 数据源、公开性、更新频率、最小实验口径
- 数据源：Binance USDⓈ-M Futures Kline API
- 公开性：公开可得，无需私钥
- 更新频率：分钟级；本次直接映射到 `5m / 15m`
- 最小实验口径：
  - 市场代理：`BTCUSDT`
  - alt 横截面：`ETH,SOL,XRP,BNB,DOGE,ADA,LINK,AVAX,LTC,TRX`
  - `15m`：近 `45d`
  - `5m`：近 `18d`
  - `beta_realized` 窗口分别为 `12 bars (15m)`、`24 bars (5m)`
  - `beta_kalman` 使用仓库同构的一维 Kalman beta 滤波

### 这次本地最小快检结果
- `15m`：
  - hold `1 bar`：IC ≈ **`+1.38%`**，IC hit ≈ **`51.8%`**，net LS ≈ **`-2.36 bps/bar`**
  - hold `2 bars`：IC ≈ **`+1.24%`**，net LS ≈ **`-2.29 bps/bar`**
  - hold `4 bars`：IC ≈ **`+1.77%`**，net LS ≈ **`-1.78 bps/bar`**
- `5m`：
  - hold `1 bar`：IC ≈ **`+1.23%`**，net LS ≈ **`-1.39 bps/bar`**
  - hold `2 bars`：IC ≈ **`+1.33%`**，net LS ≈ **`-1.39 bps/bar`**
  - hold `4 bars`：IC ≈ **`+1.30%`**，net LS ≈ **`-1.55 bps/bar`**
- 当前 naive 口径下，**高 BTC 波动 bar 并没有自动把它救活**：例如 `15m` hold `1 bar` 时，高 BTC 波动 bucket 的 net 仍约 **`-2.72 bps/bar`**，并不优于低波动 bucket。

### 这组结果最值得怎么读
- **不是“没信号”**：IC 稳定小正，说明横截面排序信息在。
- **也不是“直接能跑”**：每根 bar 都换仓的实现，把这点排序力在成本前就消耗掉了。
- 所以当前最诚实的定位是：
  - `raw alpha candidate`：**是**
  - `完整策略骨架`：**有**
  - `当前全时段裸跑可直接上`：**否**
  - `下一步优先工作`：**threshold / holding / turnover surgery**

## 5. 下一步怎么测
1. **先做 thresholded，而不是全天候每根都调。**
   - 直接测 `|beta_gap_z| >= 1.0 / 1.5 / 2.0`；
   - 只交易最极端的 `2~3` 个名字；
   - 看触发次数下降后，net 是否从负转正。
2. **把 exit 从“固定 bar”改成“回归完成即走”。**
   - 当 `beta_gap` 回到 `[-0.25σ, +0.25σ]` 就平；
   - 对照固定持有 `1/2/4 bars`，看能否减少无效持仓与反复换手。
3. **做 `beta-neutral / sector-neutral` 版本。**
   - 当前只是横截面等权多空；
   - 下一轮应约束组合对 BTC 的残余 beta，确认 edge 来自 idiosyncratic beta-gap，而不是组合残留 market exposure。
4. **做流动性过滤和参与率约束。**
   - 先只保留高成交额 perp；
   - 看是否是尾部币拖高了换手、压扁了可交易性。
5. **把 `15m` 做成主战场，`5m` 只做补充。**
   - 当前 `15m` 的 IC 更稳定、持有 `4 bars` 也更像有持续性；
   - `5m` 先别硬上，除非 threshold 版能显著减少重平衡。

## 6. 风险与保留意见
- 主来源是 **2026 新仓库**，不是已发表的 crypto intraday beta-gap 论文；因此这里更像“repo-based raw alpha intake + 本地最小复核”，不是对某篇学术论文的逐式复刻。
- Kalman beta 这类状态变量对 `Q/R` 设定敏感；这次先用仓库默认思路，没有做超参数网格。
- 当前复核只用 **Binance 单 venue perp**；若未来扩到多 venue，结果可能变化。
- 现在最关键的 honesty point 已经很明确：
  - **排序力在；**
  - **全时段裸做不行；**
  - 所以下一步不是“再讲理论”，而是直接做 **turnover gate / event trigger / exit surgery**。

## 7. 来源
1. **Vedant Upasani (2026). _Alpha-Research-Discovery_ — GitHub repository.**
   - Author: Vedant Upasani（GitHub: `VedantUpasani46`）
   - Year: 2026（repo observed updated `2026-03-23`）
   - Title: `Alpha-Research-Discovery`
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/VedantUpasani46/Alpha-Research-Discovery`
   - Repo URL: `https://github.com/VedantUpasani46/Alpha-Research-Discovery`
   - Relevant file: `https://raw.githubusercontent.com/VedantUpasani46/Alpha-Research-Discovery/master/alpha_10_kalman_dynamic_beta.py`

2. **Kalman, R. E. (1960). _A New Approach to Linear Filtering and Prediction Problems_. Journal of Basic Engineering.**
   - Authors: Rudolf E. Kalman
   - Year: 1960
   - Venue: `Journal of Basic Engineering`
   - DOI: `10.1115/1.3662552`
   - Readable URL: `https://doi.org/10.1115/1.3662552`
   - Repo URL: `N/A`

3. **Faff, R., Hillier, D., & Hillier, J. (1998). _Time-varying Beta Risk of Australian Industry Portfolios: An Exploratory Analysis_. Journal of Business Finance & Accounting.**
   - Authors: Robert Faff, David Hillier, John Hillier
   - Year: 1998
   - Venue: `Journal of Business Finance & Accounting`
   - DOI: `10.1111/1468-5957.00209`
   - Readable URL: `https://doi.org/10.1111/1468-5957.00209`
   - Repo URL: `N/A`

4. **本地最小快检 artifact（2026-03-25）**
   - `reports/artifacts/quant_digests/kalman_beta_deviation_probe_20260325/summary.csv`
   - `reports/artifacts/quant_digests/kalman_beta_deviation_probe_20260325/run_meta.txt`
   - `reports/artifacts/quant_digests/kalman_beta_deviation_probe_20260325/run_probe.py`
