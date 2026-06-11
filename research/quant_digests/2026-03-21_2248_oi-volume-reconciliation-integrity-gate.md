# OI 先过“可对账”再谈 alpha：用 |ΔOI| ≤ Volume 做 15m funding/OI/basis overlay 的 data-integrity gate
- 时间：2026-03-21 22:48 UTC
- 类型：论文（可全文）+ 本地公共数据最小快检
- 主题标签：open-interest/funding/basis/data-quality/sanity-check/regime/filter/risk-overlay/crypto/5m/15m
- 证据类型：论文证据 + 工程快检

## 1) 这次看了什么
Ioannis Giagkiozis & Emilio Said 在 *Ledger* (2024) 的论文 **《Reconciling Open Interest with Traded Volume in Perpetual Swaps》**：用一个“会计约束”去检验不同交易所永续合约 **OI(open interest)** 报告是否可信。

它对我们 desk 的意义很直接：我们最近多次把 `funding / OI / basis` 当三条收口线（breakout-short / Fib retest_hold / EMA-PSAR）的 shared overlay；但 **如果 OI 数据本身在短周期不可对账**，任何“OI gate”都可能只是把数据供应商的噪声当信号。

## 2) 核心结论（能直接拿来用的点）
- **硬约束（核心）**：在任意时间区间内，OI 的绝对变化不可能超过该区间内的成交量。
  - 用 notional 口径写就是：\(|\Delta OI\_value| \le Volume\_quote\)。
  - 一旦出现 \(|\Delta OI| > Volume\)，只能解释为：OI 或 Volume（或两者）在数据口径/时间戳/漏报上出了问题。
- **论文主发现**：作者用 tick-by-tick 数据连 7 家衍生品所，发现 **部分大所存在系统性 OI “不可对账”**；也有交易所更像“延迟报清算/强平消息”，导致短窗不一致、长窗趋于一致。
- **对 5m/15m 的落地读法**：
  - OI/funding/basis 更像 `regime gate / filter / sizing overlay`，不是逐根 15m 的主信号；
  - 且在进入我们任何 `crowding breadth / basis dislocation / funding extremity` 规则之前，必须先加一层 **OI–Volume 可对账守门**（否则会把“错位/漏报”当成 crowding shock）。

## 3) 为什么和当前三条收口线有关
- **V3 breakout-short follow-up**：我们常用 OI/funding 做“拥挤/挤仓/反身性”风险提示；但 OI 若短周期错位，会把 follow-up verdict 写歪（误判为“加仓/减仓”）。
- **Fibonacci confirmation / retest_hold**：retest 阶段本来就稀疏，如果 OI 报告有系统跳变，会把“回踩期仓位变化”误当成确认/否决条件。
- **EMA / PSAR raw alpha focus**：若未来把 OI 作为参与度 gate（比如 `OI > OI-SMA`），那它首先必须满足 data-integrity；否则就是把数据延迟当趋势参与度。

## 4) 可复刻的最小实验（5m/15m 快速验证口径）
### 4.1 研究假设
对任何交易所/数据源：如果 OI 与成交量在同一时间边界、同一单位下是自洽的，则应近似满足：
\[
excess\_t = \max(|OI\_t - OI\_{t-1}| - Volume\_t,\; 0) \approx 0
\]
短窗如果出现非零 excess，但在更长窗（1h/4h）会消失，则更像“延迟/错位”；若长窗仍持续非零，则更像“口径/漏报/误报”。

### 4.2 本地最小快检（Binance 公共端点，BTCUSDT）
我用 Binance futures 公共接口做了最小对账（OI= `sumOpenInterestValue`，Volume= kline `quoteVol`，按 openTime 对齐）：
- **5m（最近约 41.5 小时，n=499）**：违约比例约 **2.81%**（14/499）。
- **15m（最近约 5.2 天，n=499）**：违约比例约 **0.60%**（3/499）。
- 把同一批 5m 数据聚合到 **1h / 4h** 后，违约比例变为 **0%**。

解读：这更像论文里说的“短窗错位/延迟一致性”，不必立刻否定 Binance OI，但**提醒我们：5m/15m 上不要把 OI jump 当成硬信号**；要么做多尺度一致性 gate，要么对 OI 变化做滞后对齐/容忍带。

### 4.3 我们该先加的 3 个 data-integrity checks（可直接进代码）
1) **守恒违约率（核心）**
   - `excess_t = max(abs(delta_oi_value) - quote_volume, 0)`
   - `viol_t = 1[excess_t > 0]`
   - 输出：rolling `viol_rate`、`max_excess_ratio = max(excess/volume)`

2) **多尺度一致性（区分延迟 vs 系统问题）**
   - 对同一数据同时算 `5m/15m` 与聚合 `1h/4h` 的 `viol_rate`。
   - 若短窗高、长窗≈0：标记 `delay_like`；若长窗也高：标记 `structural_bad_feed`。

3) **“孤立 OI jump”异常（避免把数据跳当 crowding shock）**
   - `z_oi = delta_oi / rolling_std(delta_oi, W)`
   - 若 `|z_oi|>6` 但 `|ret|` 与 `|delta_basis|` 同时很小，则标记 `oi_jump_suspect`，该 bar 的 OI 信号不参与 overlay。

## 5) 风险与保留意见
- 这个不等式是“理论上必须成立”的守恒约束，但落到实际 API 会被 **时间戳边界、OI 采样时刻、block trade/强平推送延迟、volume 口径差** 影响；所以更合理的用法是：
  - 把它当 **数据质量红旗/权重门控**，而不是直接把 `excess>0` 解释成交易行为本身。
- 若未来我们要把 OI 纳入三条收口线的 shared overlay，建议先把这一层做成统一的 `oi_integrity_score`（0~1），再决定是 `veto` 还是 `size-down`。

## 6) 来源
- Giagkiozis, I., & Said, E. (2024). *Reconciling Open Interest with Traded Volume in Perpetual Swaps.* **Ledger**, 9, 1–15.
  - Related DOI: https://doi.org/10.5195/ledger.2024.325
  - arXiv:2310.14973v2 (PDF 可得): https://arxiv.org/abs/2310.14973
  - arXiv PDF: https://arxiv.org/pdf/2310.14973v2
