# 别把 EMA / PSAR raw alpha 继续写成“零阈值开关”：`adaptive no-trade band` 更像 15m 的成本存活层
- 时间：2026-03-19 02:10 UTC
- 类型：论文
- 主题标签：ema / psar / raw-alpha / transaction-cost / threshold / no-trade-band / filter / crypto / 15m
- 证据类型：论文证据（**摘要 + DOI/Crossref/OpenAlex 元数据；非全文级**）

## 1. 这次看了什么
这次主看同一作者组的一条连续研究线：
- **Svogun, D., & Rudys, V. (2024)**，*Optimizing the moving average trade rule for cryptocurrencies: implications of band size and transaction costs*（Applied Economics Letters）
- 对照前作：**Svogun, D., & Rudys, V. (2023)**，*An Adjustable-Band Moving Average Tradingalgorithm for Cryptocurrencies*（SSRN）

可迁移点不是“再找一组神奇均线参数”，而是：**给 MA/EMA 触发加“可调 band（no-trade 带）”**，把很多边缘噪声交易先拦掉，再谈方向 alpha。

## 2. 核心结论
- **一句话核心结论：** 对 crypto 均线规则来说，`band` 不是装饰，而是决定“成本后还能不能活”的核心开关。  
- **一句话证明方式：** 2024 文献在摘要里直接比较 `adjustable band` 与 `fixed band`，并在含交易成本语境下给出三条结论（性能分化、最优 band 高于常见基准、可调 band 超越“只把固定 band 调高”）。
- 具体可用信息（来自 2024 摘要）：
  1) `adjustable band` 在“技术分析有效年份”更强、在无效年份更弱（像杠杆化暴露）；
  2) 最优 band **显著高于常见 0% / 1%** 的固定设定；
  3) 可调 band 的价值不只是在“找到更高固定阈值”，在 `>0` 交易成本下仍有额外信息价值。

## 3. 为什么和当前项目有关
这轮最直接服务的是 **`EMA / PSAR raw alpha focus`**：
- 你现在卡点不是“再加一个新指标”，而是 **EMA/PSAR 太容易在边界附近反复触发、被手续费和滑点磨损**。
- 这条文献线给的不是 headline alpha，而是更适合 desk 的旁支想法：**把 `band` 当 admission filter / no-trade 区**。

对另外两条收口线也有直接映射：
- `V3 breakout-short follow-up`：只有当价格脱离 EMA 中轴达到 band 要求，才允许继续追 follow-up，减少假延续。
- `Fibonacci confirmation / retest_hold`：回踩后若收盘仍落在 no-trade 带内，先不认定“守住”；先等“脱带”再确认。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
在 15m 上，把 EMA/PSAR 从“碰线就触发”改为“必须脱离动态 band 才触发”，能提升成本后质量（哪怕交易次数下降）。

### 最小实验口径（可一晚跑完）
- 资产：BTC / ETH / SOL perpetual
- 周期：15m
- 样本：近 180 天
- 成本：统一 `fee + slippage`（沿用现有 friction 配置）

### 三组对照
1. **Raw 组**：`close` 穿越 `EMA34`（或 PSAR flip）即触发。  
2. **Fixed-band 组**：`band = {0.10%, 0.20%}`。  
3. **Adaptive-band 组**：`band_t = max(0.10%, q * ATR14/close)`，`q ∈ {0.5, 1.0, 1.5}`。  
   - 多头需 `close > EMA34 * (1 + band_t)`；空头反向。

### 优先观察 4 个指标
- `post_cost_return`
- `return_per_trade`
- `trades_per_day`
- `false_follow_through_ratio`（触发后 N 根内回到 band 内的比例）

### 一条简单保留规则
若相对 Raw 组：
- `post_cost_return` 不降或上升，且
- `trades_per_day` 下降（例如 ≥20%）并伴随 `return_per_trade` 提升，
则把 adaptive band 进入三条线共用 filter 候选。

## 5. 风险与保留意见
- 当前证据主要来自摘要/元数据，不是全文深读；结论强度应标记为“可执行假设”，不是“已复现事实”。
- 论文里的“有效年份更强、无效年份更弱”提示 band 可能放大 regime 暴露，需配合现有 regime gate，避免把 band 当万能稳定器。
- 该思路本质是**交易抑制层**，不是独立主信号；不要把它误用成“单独开仓 alpha”。

## 6. 来源
1. Svogun, D., & Rudys, V. (2024). *Optimizing the moving average trade rule for cryptocurrencies: implications of band size and transaction costs*. **Applied Economics Letters**.  
   - DOI: https://doi.org/10.1080/13504851.2024.2394211  
   - Readable URL: https://www.tandfonline.com/doi/full/10.1080/13504851.2024.2394211  
   - Repo URL: 未提供（未见官方公开仓库）
2. Svogun, D., & Rudys, V. (2023). *An Adjustable-Band Moving Average Tradingalgorithm for Cryptocurrencies*. **SSRN Electronic Journal**.  
   - DOI: https://doi.org/10.2139/ssrn.4663472  
   - Readable URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4663472  
   - Repo URL: 未提供（未见官方公开仓库）
