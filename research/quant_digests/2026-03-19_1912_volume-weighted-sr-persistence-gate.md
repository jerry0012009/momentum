# 别把 retest / breakout 继续当“碰线就算”：`volume-weighted S/R persistence` 更像 15m 的 shared quality gate
- 时间：2026-03-19 19:12 UTC
- 类型：论文（近 5 年）
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/support-resistance/volume/markov/regime/filter/paper/crypto/15m
- 证据类型：论文证据（全文可得；期刊层级一般，需本地复验）

## 1. 这次看了什么
这轮看的是 **Nikita Martyushev, Vladislav Spitsin, Mark Khairov, Lubov Spitsina (2025)** 的论文 *Modeling Support and Resistance Zones in Financial Time Series with Stochastic and Volume-Weighted Methods*。  
我不把它当“再发明 S/R 画线”，而是抽一个更贴近我们 desk 的旁支：

> **先给 zone 打“可持续性分数”（persistence），再决定 breakout follow-up / retest_hold 要不要放行。**

## 2. 核心结论
1. **一句话核心结论**：对 5m/15m 来说，S/R 更像“带成交量记忆的动态区间”，不是静态线；先做 zone 质量分层，能更诚实地减少假突破/假跌破。  
2. **一句话证明方式**：论文在多资产高频样本（1s/1m，2020-2023）上，对比“传统局部极值法”与“成交量加权 + 聚类 + 马尔可夫状态”方法，给出 Precision/Recall 与 false-break 指标改进。  
3. 关键数据点（论文报告值）：
   - Precision/Recall 相对经典法提升约 **10-16 个百分点**；
   - false breakout 下降约 **12-15%**；
   - 高成交量 zone 的次日 breakout 概率显著更低：**>P90 成交量 zone <18%**，而低于中位数的 zone **>40%**；
   - zone 生命周期中位数约 **1.7-2.5 天**，震荡 + 高量时可延长到 **3-3.5 天**。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：如果“刚跌破”的其实是高持久性 zone，follow-up short 更该慢一步（先看二次确认），避免把高稳定区当成可随手延续。  
- **Fibonacci confirmation / retest_hold**：Fib 位本质就是潜在 S/R 带；把 `0.5/0.618` 放进“zone 持久性 + 量能确认”框架，比“触位即算守住/失守”更稳。  
- **EMA / PSAR raw alpha focus**：EMA/PSAR 继续做触发；`zone_persistence_score` 放在上层做 **admission/veto filter**，优先解决成本后存活问题，而不是再堆触发条件。

## 4. 可复刻的最小实验（5m/15m）
### 4.1 数据与公开性
- 数据源：Binance perpetual OHLCV（含 quote/taker volume，可公开获取）；
- 公开性：公开可得；
- 更新频率：5m/15m；
- 本轮定位：**shared confirmation/filter layer**（不是逐根主信号）。

### 4.2 最小实现（先做这版）
1. 用现有 swing/Fib 锚点先生成候选 S/R zone；
2. 对每个 zone 计算 `zone_persistence_score`（最小版）：
   - `touch_count_lookback`
   - `zone_volume_pct`（触碰窗口成交量分位）
   - `zone_width_atr_norm`
   - `retest_survival_rate`（触碰后 N=4 根未失守）
3. 分三档：`low / mid / high persistence`，仅做 gate：
   - breakout-short follow-up：`high` 档必须额外满足“retest fail + close-confirmed n=2”才放行；
   - fib retest_hold：`low` 档降权或拒绝；
   - EMA/PSAR：仅在 `mid/high` 档允许放大仓位（或降低 no-trade band）。
4. 最先看 2 个指标：
   - `false_break_ratio`（是否下降）
   - `post_cost expectancy`（6/10 bps 下是否改善）

## 5. 风险与保留意见
- 样本主场景是美股/ETF 高频，不是 crypto 24/7；
- 论文包含较重建模（SDE/Markov），我们先做“轻量 proxy 版”验证边际价值，避免一次性工程过重；
- 期刊层级与可复现实证质量需要谨慎看待，建议把它视作“可测框架来源”，不是已验证 production alpha；
- 若 proxy 版在 15m 上不能稳定降低 `false_break_ratio`，应快速 park，不继续扩写复杂模型。

## 6. 来源
1. **Martyushev, N., Spitsin, V., Khairov, M., & Spitsina, L. (2025). _Modeling Support and Resistance Zones in Financial Time Series with Stochastic and Volume-Weighted Methods_. Contemporary Mathematics, 6(6).**  
   - DOI: `10.37256/cm.6620258482`  
   - Readable URL: <https://ojs.wiserpub.com/index.php/CM/article/view/8482>  
   - PDF: <https://ojs.wiserpub.com/index.php/CM/article/download/8482/3732/78934>  
   - Repo URL: `N/A（论文未提供公开代码仓）`
2. **Chan, J. Y. L., Phoong, S. W., Cheng, W. K., & Chen, Y. L. (2022). _Support resistance levels towards profitability in intelligent algorithmic trading models_. Mathematics, 10(20), 3888.**  
   - DOI: `10.3390/math10203888`  
   - Readable URL: <https://doi.org/10.3390/math10203888>  
   - Repo URL: `N/A`
