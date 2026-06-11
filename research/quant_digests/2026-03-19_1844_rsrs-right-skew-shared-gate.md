# 别把支撑阻力强度只当“过/不过”：`RSRS right-skew score` 更像三条收口线共用的 **veto + sizing overlay**（不是二元入场键）
- 时间：2026-03-19 18:44 UTC
- 类型：GitHub 仓库 + 本地代理快检
- 主题标签：breakout-short / fibonacci / retest-hold / ema / psar / rsrs / support-resistance-strength / regime / veto / position-sizing / repo / crypto / 15m
- 证据类型：仓库规则证据 + 本地 15m 代理快检

## 1) 这次看了什么
这次选的是一个较新的复现仓库：**Alannimoon (2026) `Replication_Everbright_Securities`**。它复现的是光大证券的 RSRS 市场择时框架，核心不是“又发明一个触发器”，而是把“支撑/阻力强度”从二元条件改成**连续分数**：

- 先在滚动窗口回归：`high ~ low`，取斜率 `β`（`rsrs_slope`）
- 再做滚动标准化得到 `z-score`
- 再乘 `R²` 得 `modified_score`
- 再乘 `β` 得 **`right_skewed_standard_score`**

对应代码可直接读：
- `data_processing.py`（斜率、z-score、R²、right-skew 计算）
- `strategy.py`（阈值入场/离场，含 volume/price 过滤变体）
- `config.py`（典型参数：`n=16/18`，`m=300/600`，阈值 `0.7`）

## 2) 核心结论（给 desk 的一句话）
**这条线更像“共享风险覆盖层”（veto + sizing），不适合直接当三条收口线的二元入场开关。**

原因：在我们 15m crypto 代理快检里，它能明显降回撤、减亏，但如果硬做二元 gate，会引入明显的交易切换摩擦。

## 3) 本地 15m 代理快检（BTC/ETH/SOL，120d，next-bar open，6 bps/side）
我先用最小可复现口径，把 `RSRS right-skew > 0.7` 接到 `EMA20>EMA50` 方向层上做快检（只做 long 侧代理）。

### 3.1 基线 vs 二元硬 gate
- **Baseline（EMA20>EMA50）**
  - `mean_total_return = -15.66%`
  - `mean_max_drawdown = -31.01%`
  - `positive_asset_ratio = 0/3`
- **Hard gate（EMA 且 RSRS_right>0.7）**
  - `mean_total_return = -5.27%`
  - `mean_max_drawdown = -20.71%`
  - `positive_asset_ratio = 1/3`
  - 但 `mean_trade_events: 112 -> 224`，`mean_turnover: 223 -> 448`（切换摩擦明显上升）

### 3.2 为什么会“减亏但更抖”
`RSRS right-skew` 在 15m crypto 上分布非常偏：
- `score > 0.7` 约 **17.2%** bars
- `score < -0.7` 仅 **0.4%** bars

这说明它在短周期上更像“正向趋势确认器”，而不是对称的多空切换器。把它硬塞成 on/off gate，容易在阈值附近抖动，放大换手。

## 4) 为什么它直接服务三条收口线
这轮主题和三条线是直接相关的，而且优先级高于继续补“新形态名词”：

1. **`V3 final-verdict / breakout-short follow-up`**
   - 当 `RSRS_right` 明显偏强（例如 >0.7）时，短侧 follow-up 更应先降仓或 veto，避免逆结构硬追。
2. **`Fibonacci confirmation / retest_hold`**
   - Fib 回踩“守住”可以把 RSRS 当结构强度附加条件（不是 Fib 主信号），用于区分“有结构支撑” vs “仅触位反弹”。
3. **`EMA / PSAR raw alpha focus`**
   - RSRS 更适合做 EMA/PSAR 的 **risk overlay**（仓位层）而非入场层，优先减少成本后磨损。

## 5) 下一步怎么测（最小实验，直接可跑）
### 实验 A（优先）：共享 veto，而非 shared trigger
在三条收口线各自触发逻辑不变的前提下，只加一层：
- `RSRS_right > q70`：禁止新增 short（或 short 半仓）
- `RSRS_right < q30`：禁止新增 long（或 long 半仓）

对照组：无 RSRS。
主看：`post_cost_return / max_dd / turnover / veto_hit_rate`。

### 实验 B：三档仓位（更贴合 overlay 角色）
把 RSRS 映射为仓位权重，而非开关：
- low：`0.5x`
- mid：`1.0x`
- high：`1.25x`（上限可封顶）

主看：`cost-adjusted expectancy` 与 `drawdown per trade` 是否同时改善。

### 实验 C：短侧对照（避免 right-skew 偏置）
因 `right-skew` 负尾过稀，短侧建议并行比较：
- `right_skew_score`
- `modified_score`（不乘 slope）
- `plain z-score`

主看：短侧 `false_follow_rate` 与 `time_to_failure`。

## 6) 风险与边界
- 该仓库是 **repo 复现项目**，不是正式期刊论文；它提供的是“可实现规则骨架”，不是可直接搬用的 crypto 结论。
- 本轮是 120d/15m 三资产快检，不是完整 OOS 结论。
- 当前结果已经提示：**RSRS 在我们场景更像风险覆盖层，而非二元信号层**；若后续实验不支持，也应快速降级，不续命。

## 7) 来源（尽量完整）
### Source A（主）
- Authors: **Alannimoon**
- Year: **2026**
- Title: **Replication_Everbright_Securities**
- Venue: **GitHub repository (Python)**
- DOI: **N/A**
- Readable URL: `https://github.com/Alannimoon/Replication_Everbright_Securities`
- Repo URL: `https://github.com/Alannimoon/Replication_Everbright_Securities`

### Source B（被复现对象，仓库内附 PDF）
- Authors: **未在仓库元数据中清晰标注（待补）**
- Year: **未标注（待补）**
- Title: **《基于阻力支撑相对强度（RSRS）的市场择时》**
- Venue: **光大证券研究报告（sell-side report）**
- DOI: **N/A**
- Readable URL: `https://github.com/Alannimoon/Replication_Everbright_Securities/blob/main/%E3%80%90%E5%85%89%E5%A4%A7%E8%AF%81%E5%88%B8%E3%80%91%E5%9F%BA%E4%BA%8E%E9%98%BB%E5%8A%9B%E6%94%AF%E6%92%91%E7%9B%B8%E5%AF%B9%E5%BC%BA%E5%BA%A6(RSRS)%E7%9A%84%E5%B8%82%E5%9C%BA%E6%8B%A9%E6%97%B6.pdf`
- Repo URL: `https://github.com/Alannimoon/Replication_Everbright_Securities`

---
本轮本地快检产物：
- `reports/artifacts/quant_digest_rsrs_gate_2026-03-19/aggregate.csv`
- `reports/artifacts/quant_digest_rsrs_gate_2026-03-19/aggregate_with_state.csv`
- `reports/artifacts/quant_digest_rsrs_gate_2026-03-19/asset_summary.csv`
- `reports/artifacts/quant_digest_rsrs_gate_2026-03-19/asset_with_state.csv`
