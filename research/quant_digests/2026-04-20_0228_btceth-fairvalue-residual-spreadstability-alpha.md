# BTC/ETH 双锚公平价残差回归（spread stability gate）——repo 直读 + Binance 5m/15m portability probe

**Base alpha（一句话）**：把山寨币价格先用 `BTC + ETH` 两腿回归成“公平价”，当残差 `z-score` 偏离过大时做反向回归（低于公平价做多，高于公平价做空），并用 `spread stability`、波动、成交额、funding 做准入门槛。

- 主题类型：**raw alpha**
- 基础 alpha：**beta-neutral residual mean reversion（BTC/ETH 双锚公平价偏离回归）**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**是**（仓库已有完整壳；但当前参数在我们的 first probe 下未过线）

---

## 1) 为什么这轮选它（而不是继续做旧题）

这份 2026 新仓库不是纯“信号看板”，而是把以下链条都写出来了：

1. `feature_engine.py`：
   - 对每个 alt 做滚动回归：`log(alt) ~ a + b1*log(BTC) + b2*log(ETH)`
   - 产出 `residual_log`、`z_score`、`spread_stability_score`
2. `signal_engine.py`：
   - 明确入场门槛（`zscore_entry`、波动率、成交额、稳定度、funding）
   - 成本口径（`fee_bps`）
3. `backtest.py`：
   - 有仓位、换手、手续费、回测统计
   - 还能叠加 regime / bias overlay（但那是旁支，不是本体 alpha）
4. `data_ingestion.py`：
   - 公开可拿的数据口径（Binance Kline + funding）

=> 它符合这轮“优先补可独立复现 raw alpha 壳”的约束。

---

## 2) Source audit（核心证据）

### 2.1 仓库元数据
- Authors: `joanduso`
- Year: `2026`（created_at: `2026-03-13`, pushed_at: `2026-04-01`）
- Title: `crypto-relative-value-engine-`
- Venue: GitHub Repository
- DOI: N/A
- Readable URL: <https://github.com/joanduso/crypto-relative-value-engine->
- Repo URL: <https://github.com/joanduso/crypto-relative-value-engine->

### 2.2 与本题直接相关的源码
- `feature_engine.py`
- `signal_engine.py`
- `backtest.py`
- `interval_profiles.py`
- `data_ingestion.py`
- `quant_engine/opportunity_engine.py`

### 2.3 与本题的关系（旁支 vs 本体）
- 本体（raw alpha）：**残差偏离回归**。
- 旁支（可选 overlay）：新闻、ETF flow、MVRV、SOPR、BTC bias/regime。  
  这些更适合作为 gate / sizing / veto，不该伪装成逐根主信号。

---

## 3) 我们的最小可复现实验（public data）

## 数据源与公开性
- 数据源：Binance 历史公开月度 K 线归档（`data.binance.vision`）
- 市场：USDⓈ-M perpetual
- 标的：`BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, DOGEUSDT`
- 公开性：公开可下载，无私有 key
- 更新频率：交易所原生 K 线（5m / 15m）

## 实验口径（尽量贴仓库）
- 公平价回归：`log(alt)` 对 `log(BTC), log(ETH)` 滚动 OLS
- 信号：残差 `z-score`
- 入场：`|z| >= 2.0`（反向）
- 出场：`|z|` 回落至 `0.5` 或超时
- 成本：双边 `4 bps`（简化）
- 版本 A（Base）：仅残差回归
- 版本 B（Stable60）：加 `spread_stability` 前 40% 过滤（保留稳定度更高样本）

> 注：为了保证 5m 也有足够 warmup，5m 与 15m 都使用 2025-01~2025-03 三个月数据。

---

## 4) 结果（first verdict）

## 15m（2025-01~03）
- Base：
  - net return **-19.77%**
  - max DD **-20.70%**
  - Sharpe **-6.48**
  - trades **143**
- Stable60（加稳定度门槛）：
  - net return **-11.09%**
  - max DD **-12.13%**
  - Sharpe **-6.85**
  - trades **60**

## 5m（2025-01~03）
- Base：
  - net return **-21.95%**
  - max DD **-23.07%**
  - Sharpe **-4.06**
  - trades **277**
- Stable60：
  - net return **-15.33%**
  - max DD **-16.74%**
  - Sharpe **-3.87**
  - trades **117**

## 解读（人话版）
- 这条 alpha **不是“无效”**，而是“这个默认参数组合在我们口径下还不够可交易”。
- `spread_stability` 有价值：它明显降了回撤和换手，但目前还没把净收益拉正。
- 这说明本题更像“可落地策略壳 + 待校准参数”，而不是“可直接上线的现成 edge”。

---

## 5) 为什么它仍值得留在素材池

1. **base alpha 清楚**：不是讲故事，是可计算的 residual z-score。  
2. **工程壳完整**：entry / filter / cost / ranking / backtest 都有。  
3. **可扩展到 1m/3m/5m/15m**：
   - 通过 `interval_profiles.py` 思路，保持“统计窗口按天数等价”，不是硬套同一 bars 数。
4. **旁支能拆分复用**：BTC bias / news / onchain 可以独立做 overlay，不污染主信号定义。

---

## 6) 下一步怎么测（必须做）

按优先级建议 4 步：

1. **先做 admission 重标定（15m→5m）**
   - 网格：`z_entry ∈ {1.2,1.5,1.8,2.0}`，`z_exit ∈ {0.2,0.5,0.8}`
   - 目标：把“trade count / turnover / post-cost return”拉到可生存区。

2. **把 funding 从硬阈值改成惩罚项**
   - 当前硬 veto 可能切掉太多均值回归机会；改为 `score penalty` 再看净效应。

3. **做横截面路由，不做全标的平均**
   - 每根 bar 只做 top-k（按 edge_after_fees + stability），而不是三币平均摊开。

4. **把 1m/3m 作为子执行层，不直接复刻主信号**
   - 主信号仍用 5m/15m；1m/3m 只做 limit placement / 分批成交 / timeout。

---

## 7) 给当前 desk 的结论

- 这轮主题属于 **raw alpha（relative value / mean reversion）**，满足“补充 raw alpha 素材池”的目标。  
- 但 first probe 给出的结论是：**策略壳可复用，参数未过线**。  
- 所以它当前状态应标为：**KEEP（工程壳）+ RE-CALIBRATE（参数）**，而不是直接升到 production candidate。

---

## References

1. joanduso (2026). *crypto-relative-value-engine-* (GitHub repository).  
   - Repo: <https://github.com/joanduso/crypto-relative-value-engine->
   - Key files:
     - <https://raw.githubusercontent.com/joanduso/crypto-relative-value-engine-/main/feature_engine.py>
     - <https://raw.githubusercontent.com/joanduso/crypto-relative-value-engine-/main/signal_engine.py>
     - <https://raw.githubusercontent.com/joanduso/crypto-relative-value-engine-/main/backtest.py>
     - <https://raw.githubusercontent.com/joanduso/crypto-relative-value-engine-/main/interval_profiles.py>
     - <https://raw.githubusercontent.com/joanduso/crypto-relative-value-engine-/main/data_ingestion.py>

2. Binance Public Data (monthly futures klines)  
   - Portal: <https://data.binance.vision/>
