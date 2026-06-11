# 别把 pairs 只做成 bar-close z-score：这份 2026 新仓库更该先测的是「cointegration spread + OBI veto + 成本生存线」完整骨架
- 时间：2026-03-24 09:14 UTC
- 类型：2026 GitHub 新仓库 + Binance 公共数据最小快检 + 近 5 年论文地基
- 主题类型：raw alpha
- 基础 alpha：cointegration spread 偏离后的均值回归（pairs / stat-arb / relative value）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/obi/microstructure/execution/cost/1m/3m/5m/15m/repo
- 证据类型：工程证据 + 本地最小快检（可复现）

## 1) 先回答：这篇东西的 base alpha 是什么？
**base alpha = pair spread 的短周期均值回归**，不是 OBI 本身。  
OBI 在这份材料里更像 **entry veto / execution gate**（避免在盘口不配合时硬开仓）。

## 2) 这次看了什么
这次主看仓库：**Samarth Chaudhary (2026), `Crypto_Stat-Arb_HFT_Model`**。  
它把一条可落地的策略链路拆得很完整：
- Python 研究层：`data_loader.py`（1m 数据）、`analyzer.py`（相关+协整筛对）、`optimizer.py`（参数搜索）
- C++ 执行层：`main.cpp`（实时 z-score + OBI 条件 + 下单队列）

我额外做了一个 **1m 最小快检**（Binance USDⓈ-M 公共数据，1500 根）来验证：
- 这条 raw alpha 在“回归命中率”上是否存在；
- 但在成本后是否还能活。

## 3) 核心结论（给 desk 的短答案）
- **一句话核心结论：** 这条线值得进池，但它的关键不是“会不会回归”，而是“成本前看起来不错、成本后大概率死亡”，所以必须把 `OBI/执行/费用` 当主约束，不是装饰层。  
- **一句话证明方式：** 仓库代码给出完整规则（entry/exit/filter/execution），我用同口径 1m 公共数据做最小复核，看 hit-rate、持有时长和成本生存线。

关键数据点（repo + 本地快检）：
1. **repo 固化策略池为 22 对 pairs**（`strategies.json`），且当前导出参数几乎统一：`window=60`、`entry_z=2.0`、`exit_z=0.0`、`stop_z=4.0`。  
2. 我的 1m 快检里，这 22 对共触发 **532 笔**，`z=2/0/4` 规则下 **TP 命中率约 85.8%**，**中位持有约 27 分钟**（看起来“会回归”）。  
3. 但按双腿归一化后，**毛收益仅 +0.78 bps/笔**；一旦加入现实费用梯度（哪怕 **8 bps/笔**），净值变成 **-7.22 bps/笔**，成本生存线直接失守。

## 4) 为什么和当前短周期（1m/3m/5m/15m）直接相关
- 这是独立 raw alpha（pairs mean reversion），能补当前素材池，不是再给单边趋势线加附件。  
- 它天然适配我们更快周期：
  - `1m/3m`：适合事件密集与执行约束评估；
  - `5m/15m`：适合降低噪音与交易频率，先过成本门。  
- repo 已经把策略结构写成完整组件，可直接拆成：
  - entry：`|z| > entry_z`
  - exit：回归到 `exit_z` 或触发 `stop_z`
  - sizing：按 `hedge_ratio` 做双腿配比
  - risk/filter：`MAX_SAFE_Z`、OBI 条件
  - cost/execution：固定费率假设 + C++ 低延迟执行框架

## 4.5) 策略拆解（必填）
- 方向属性：relative-value / stat-arb（市场中性）
- 基础 alpha：协整 spread 偏离后的回归
- regime：pair 关系稳定、噪音可控、点差可交易时更有效
- filter / veto：盘口 OBI 不配合则拒绝开仓；极端 z 值跳过
- risk / sizing / execution overlay：双腿对冲配比、stop_z、最小名义金额检查、下单队列解耦

## 5) 最小可复现实验（可直接开测）
### 数据口径（公开可得）
- 数据源 1：Binance USDⓈ-M `fapi/v1/klines`
  - 公开性：公开接口
  - 更新频率：1m
- 数据源 2：Binance USDⓈ-M `fapi/v1/depth`
  - 公开性：公开接口
  - 更新频率：可秒级轮询（repo 示例为 1s）

### 最小实验设计
1. 用 repo 的 22 对 pairs，先在 `1m` 复刻 `z=2/0/4`；
2. 输出三条线：
   - hit-rate（TP 先于 SL）
   - bps/笔（毛）
   - bps/笔（净，费用梯度 8/12/16/20 bps）
3. 把通过 1m 成本门的 pair 再迁移到 `3m/5m/15m`，比较“频率下降是否换来净边际提升”。

## 6) 风险与保留意见
- 当前 repo 的“高性能执行”亮点主要是工程层（延迟、吞吐），不是已公开的实盘绩效证明。  
- `analyzer.py` 注释有口径不一致（`MAX_HALF_LIFE = 240` 注释写“4小时”，但代码在 `1h` 重采样后再换算，实际语义接近 240 小时上限），复刻前应先统一单位。  
- 快检已经提示：**高 hit-rate ≠ 可交易 alpha**。若不把成本、滑点、吃单比例、成交延迟写进 admission gate，会出现“看起来对，交易上亏”的假阳性。

## 7) 下一步怎么测（具体动作）
1. **先做 pair admission**：在 22 对里按 `gross bps/笔` 与 `net bps/笔` 分层，保留 top 20% 做二轮。  
2. **加 OBI veto A/B**：同一对 pair 比较“不开 OBI veto vs 开 OBI veto”，只看净 bps 与回撤。  
3. **时间尺度迁移**：对存活 pair 跑 `1m→3m→5m→15m`，定位成本最优频段。  
4. **执行约束显式化**：加入 taker 比例、最大 participation、挂撤单失败率，重算净边际。

## 8) 本地产物
- `reports/artifacts/quant_digests/hft_pairs_obi_probe_20260324/pair_probe_summary.csv`
- `reports/artifacts/quant_digests/hft_pairs_obi_probe_20260324/pair_probe_pnl_bps.csv`
- `reports/artifacts/quant_digests/hft_pairs_obi_probe_20260324/meta.json`

## 9) 来源
1. **Samarth Chaudhary. (2026). _Crypto_Stat-Arb_HFT_Model_. GitHub Repository.**  
   - Repo URL: https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model  
   - Readable URL: https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/blob/main/README.md
2. **Palazzi, R. B. (2025). _Trading Games: Beating Passive Strategies in the Bullish Crypto Market_. Journal of Futures Markets.**  
   - DOI: `10.1002/fut.70018`  
   - Readable URL: https://doi.org/10.1002/fut.70018
3. **Engle, R. F., & Granger, C. W. J. (1987). _Co-integration and Error Correction: Representation, Estimation, and Testing_. Econometrica.**  
   - DOI: `10.2307/1913236`  
   - Readable URL: https://www.jstor.org/stable/1913236
