# 别把 perp 偏离只看 `mark-oracle`：这篇近 5 年论文更该先测的是「theory-adjusted fair-value gap (ρ)」短周期均值回归 raw alpha
- 时间：2026-03-24 07:02 UTC
- 类型：近 5 年论文（arXiv v6, 2024）+ 交易所公开数据 + DeFi 公开利率
- 主题类型：raw alpha
- 基础 alpha：当永续价格相对理论公允价 `F* = λS`（`λ=κ/(κ-(r-r'))`）出现极端偏离时，偏离 `ρ` 会向 0 回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（支持双边；spot short 不可用时可退化为单边 long-spot-only）
- 主题标签：raw-alpha/mean-reversion/relative-value/stat-arb/perpetual/fair-value/funding-rate/random-maturity-arbitrage/binance/aave/1m/3m/5m/15m/paper
- 证据类型：论文证据（主）+ 工程可复现（交易所公开 API）

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 不是 filter，而是“永续价格偏离理论公允价后的均值回归”本体。**

这次不再把 perp 偏离只读成 `mark-oracle` 单指标，而是用 He et al. (2024 v6) 的 no-arbitrage 框架，把信号统一成 `ρ`：
- `ρ > 0`：永续相对现货“偏贵”
- `ρ < 0`：永续相对现货“偏便宜”
- `|ρ|` 大到超过成本边界时，做回归交易（回到 0）

## 2. 核心结论
- **一句话结论：** `theory-adjusted fair-value gap (ρ)` 可以作为可独立复现、可完整落地的短周期 raw alpha 骨架，而不是只做解释变量。  
- **一句话怎么证明：** 论文给出闭式 no-arbitrage 价格与成本边界（Proposition 1/2），并在 Binance 小时级样本上用阈值交易验证了成本后仍有显著 Sharpe。

关键数据点（论文口径）：
1. 样本：Binance `1h`，5 个币（BTC/ETH/BNB/DOGE/ADA），最早从 `2020-01-08` 到 `2024-03-11`。  
2. 偏离幅度：`|ρ|` 均值约 `0.57~0.88`（年化百分比点），且跨币种共振明显（例如 `corr(ρ_BTC,ρ_ETH)≈0.89`）。  
3. 高成本层下，数据驱动随机到期套利策略仍有正 Sharpe：`BTC 2.00`、`ETH 2.59`、`BNB 4.79`（Table 11）；同时论文报告 `|ρ|` 约每年收敛 `11%`，全样本累计约 `44%`，说明 edge 在衰减但未消失。

## 3. 为什么和当前 desk 直接相关
- 这是 **raw alpha**（mean reversion / relative value / stat-arb），直接扩充素材池。  
- 能直接映射 `1m/3m/5m/15m`：交易所公开 API 可拿现货、永续、资金费率；Aave 可拿稳定币借贷利率。  
- 组件拆解天然完整：
  - entry：`|ρ|` 越过成本边界+统计阈值
  - exit：`ρ` 回归到 0 或超时
  - sizing：按 `|ρ|` 强度分级
  - risk：偏离继续扩张止损、时钟黑窗、MDD kill-switch
  - cost：显式手续费+滑点+资金费率

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 统计套利 / 均值回归（双边）  
- 基础 alpha：`ρ_t = κ(f_t-s_t) - (r_t-r'_t)` 的极端值回归到 0  
- regime：高拥挤（过去收益高）时 `ρ` 更易偏正；趋势加速段需更保守阈值  
- filter / veto：
  - 资金费率结算时刻（Binance: `00:00/08:00/16:00 UTC`）前后 1~2 根 bar 可设黑窗
  - 极端清算/深度塌陷时暂停
- risk / sizing / execution overlay：
  - `size ∝ max(0, |ρ|-ρ_open)`，并设单笔/单币上限
  - `max_hold`（如 3~8 bars）防“应回不回”
  - 双边版本 + long-spot-only 退化版本并行评估

## 4. 可复刻的最小实验
### 4.1 数据源、公开性、更新频率
- Binance USDⓈ-M/Spot（公开）：
  - perp/spot klines（`1m/3m/5m/15m`）
  - funding rate / premium index
- Aave（公开）：稳定币借贷利率（可小时级快照并向前填充到 5m/15m）
- 公开性：均公开可得
- 更新频率：可映射到 `1m/3m/5m/15m`

### 4.2 最小回测口径（先 5m，再 15m）
- 资产：`BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT`
- 定义：
  - `f=ln(F_perp)`, `s=ln(S_spot)`
  - `κ=3*365`（8h 结算对应年化强度）
  - `r'≈0`（论文口径）
  - `ρ_t ≈ κ(f-s) - r_t`
- 入场：`|zscore(ρ)| >= 2.0` 且 `|ρ|` 超过成本边界 `ρ_u/ρ_l`
- 出场：`ρ` 首次穿越 0 或 `max_hold=6 bars`
- 成本：先跑 `6/10/14 bps` 三档 round-trip
- 先看指标：`Net Sharpe` + `持仓时长分布(OtC)`

## 5. 下一步怎么测（必须）
1. **先做论文同口径 sanity check（1h）**：确认 `ρ` 分布、相关性、边界触发频率大体一致。  
2. **再压到 15m/5m**：比较 `z_in/z_out/max_hold` 网格，找“成本后仍正”的稳定平台，不追单点最优。  
3. **双边 vs 单边**：分别评估 unrestricted 与 long-spot-only（现实 spot short 约束）。  
4. **结算时钟敏感性测试**：对 `00/08/16 UTC` 前后黑窗做 ablation，看是否显著改善尾部亏损。  
5. **实盘门槛**：要求 OOS `Net Sharpe > 0.8`、`MDD < 12%`、且在 `成本+50%` 压测下不翻负。

## 6. 风险与保留意见
- 论文主样本是 `1h`，直接下钻到 `1m/3m` 可能被噪声与冲击成本吞噬。  
- `ρ` 需要借贷利率输入，Aave/交易所利率口径不一致会带来估计偏差。  
- 极端单边行情中，偏离可长期不回归，必须用超时与止损治理。  
- 该类 edge 已出现“随时间收敛”迹象，需持续滚动监控而非一次定参数。

## 7. 来源
1. **He, S., Manela, A., Ross, O., & von Wachter, V. (2024). _Fundamentals of Perpetual Futures_ (v6). arXiv Working Paper.**  
   - DOI: `10.48550/arXiv.2212.06888`  
   - Readable URL: `https://arxiv.org/abs/2212.06888`  
   - Repo URL: `N/A`
2. **Binance Developers. (2026). _USDⓈ-M Futures API Docs (Kline / Premium Index / Funding Rate)_. Official Documentation.**  
   - DOI: `N/A`  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`  
   - Repo URL: `N/A`
3. **Aave. (2026). _Aave V3 Interest Rate / Reserve Data (for borrow-supply proxy)_. Official Documentation.**  
   - DOI: `N/A`  
   - Readable URL: `https://docs.aave.com/developers/`  
   - Repo URL: `N/A`