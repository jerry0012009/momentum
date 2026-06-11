# 别把这篇 OI 论文只读成“交易所数据质量批评”：对 short-cycle desk，更该先拆的是「OI-Volume 失衡冲击 × 短窗延续」这条 raw alpha

- 时间：2026-04-16 18:18 UTC
- 类型：2024 *Ledger* 论文全文 + Binance USDⓈ-M `5m` public-data portability probe（BTC/ETH/SOL，29d）
- 主题类型：raw alpha
- 基础 alpha：`|ΔOI价值|/成交额` 异常放大（OIV shock）后，顺着当根价格方向做短窗延续（`+5m/+15m`）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/event-driven/microstructure/open-interest/volume-imbalance/oiv-shock/continuation/1m/3m/5m/15m/binance-perpetual/paper/public-data/cost/risk
- 证据类型：论文机制约束 + public-data probe

## 1) 这次看了什么
- **Authors**：Ioannis Giagkiozis, Emilio Said  
- **Year**：2024  
- **Title**：*Reconciling Open Interest with Traded Volume in Perpetual Swaps*  
- **Venue**：*Ledger* (Vol. 9)  
- **DOI**：<https://doi.org/10.5195/ledger.2024.325>  
- **Readable URL**：<https://ledgerjournal.org/ojs/ledger/article/view/325>  
- **Repo URL**：N/A

论文核心约束是：在同一时间窗内，`|ΔOI|` 不应系统性大于该窗成交量（文中 Eq.1 / Eq.5 的思想）。
对 desk 来说，最值钱的不是“谁在 misreport”，而是把这条约束转成**可交易事件因子**：

> 当 `|ΔOI价值|/成交额`（OIV ratio）突然冲高时，市场往往处在强仓位重配/强制成交/拥挤换手窗口，短窗方向延续概率上升。

## 2) base alpha 先说清
这篇东西在本轮被定义为：

> **raw alpha（事件驱动）**：`OIV shock` 触发后，按当根价格方向在 `5m~15m` 做 continuation。

注意：
- 论文原文本体是“数据一致性与市场结构”研究，不直接给交易规则；
- 但它给了一个很强的可复现统计约束，我们把它映射成短周期可执行信号。

## 3) 最小可复现实验（本轮已跑）
- 数据源（全部公开）：
  - Binance USDⓈ-M OI 历史：`/futures/data/openInterestHist`
  - Binance USDⓈ-M K线：`/fapi/v1/klines`
- 频率：`5m`
- 样本：`BTCUSDT / ETHUSDT / SOLUSDT`
- 区间：近 `29d`（每币 `8352` bars）
- 定义：
  - `OIV ratio = |Δ(sumOpenInterestValue)| / quoteVolume`
  - 冲击事件：`OIV ratio >= 各币自身P95`
  - 方向：当根 `ret_5m` 的符号
  - 评估：`dir * ret_fwd_5m` 与 `dir * ret_fwd_15m`

## 4) 关键数据点（3条）
1. **冲击事件并不稀有但足够“尖峰”**：三币统一约 `5.0%` bars 触发（`418/8352`）；`OIV ratio` 的 `P95` 约 `0.76~0.86`。  
2. **事件后方向延续为正且在 15m 更强**：
   - BTC：`+0.77 bps (5m)`，`+1.86 bps (15m)`
   - ETH：`+0.30 bps (5m)`，`+2.58 bps (15m)`
   - SOL：`+1.09 bps (5m)`，`+2.83 bps (15m)`
3. **`OIV ratio > 1` 在 Binance 也会出现**（近29d）：
   - BTC `2.02%`，ETH `3.20%`，SOL `2.13%` bars；
   说明该约束在实盘流里存在“偶发超限”，可作为冲击/异常状态识别器，而非只用于审计论文讨论。

## 5) entry / exit / sizing / risk / cost（可直接落地壳）
- **Entry**：
  1) `OIV ratio >= P95`（滚动更新，建议 14~30 天窗口）；
  2) 当根绝对收益 `|ret_5m| >= rolling P60`（过滤噪声）；
  3) 做 `sign(ret_5m)` 方向。
- **Exit**：
  - 主退出：`+3 bars`（15m）
  - 提前退出：若下一根出现反向 `ret_5m` 超过 `entry_bar_move * 0.8` 则立即平仓
- **Sizing**：
  - `size ∝ min(1, (OIV_ratio/P95 - 1) / 1.5)`
  - 单笔 notional cap：组合净值 `0.35%~0.60%` 风险预算
- **Risk**：
  - 交易时段 veto：大新闻窗口（CPI/FOMC）前后可降杠杆
  - 连续 3 笔亏损进入 cooldown（30~60min）
- **Cost 假设（first pass）**：
  - taker round-trip 先按 `6~10 bps` 分层压测；
  - 若 edge 仅 `1~3 bps`，默认转 maker-first 或降频，只做 top-decile 冲击。

## 6) 为什么这轮值得进研究池
- 它不是 funding/basis/pairs 的重复叙事，而是**仓位流-成交流失衡**这条独立事件轴；
- 能直接服务至少两类 raw alpha：
  1) 作为独立 continuation alpha；
  2) 作为 trend/pairs 的执行 admission（只在 OIV 冲击状态开仓）。

## 7) 下一步怎么测（必须项）
1. **频率下钻**：同口径转 `1m/3m`，验证 edge 是“瞬时冲击”还是“15m 才显现”。  
2. **跨所对照**：同样计算 Bybit/OKX（若能拿到稳定 OI+trade 数据流），验证“高争议交易所”是否信号更强但噪声更大。  
3. **执行分层**：`taker-only` vs `maker-first` vs `hybrid`，比较净值与成交率，避免把纸面 edge 误判为可上线。  
4. **与现有 alpha 组合测试**：
   - 给 trend book 做 `OIV shock admission`；
   - 给 MR book 做 `OIV shock veto`（避免逆势接飞刀）。

## 8) 本轮产物
- `reports/artifacts/quant_digests/oi_volume_imbalance_probe_2026-04-16_summary.csv`
- `reports/artifacts/quant_digests/oi_volume_imbalance_probe_2026-04-16_top_events.csv`
- `reports/artifacts/quant_digests/oi_volume_imbalance_probe_2026-04-16_summary.json`

## 9) 来源
1. Giagkiozis, I., & Said, E. (2024). *Reconciling Open Interest with Traded Volume in Perpetual Swaps*. Ledger, 9.  
   DOI: <https://doi.org/10.5195/ledger.2024.325>  
   Readable URL: <https://ledgerjournal.org/ojs/ledger/article/view/325>
2. arXiv preprint/full text page: <https://arxiv.org/abs/2310.14973> ; <https://arxiv.org/html/2310.14973v2>
3. Binance USDⓈ-M Open Interest History API（public）: <https://fapi.binance.com/futures/data/openInterestHist>
4. Binance USDⓈ-M Klines API（public）: <https://fapi.binance.com/fapi/v1/klines>
