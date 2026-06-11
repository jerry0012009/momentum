# 别把跨所价差只写成“两两搬砖”：这篇 2024 SSRN 更该先拆的是「multi-venue 中位价离群回归」这条 short-cycle raw alpha

- 时间：2026-04-23 10:53 UTC
- 类型：2024 SSRN 论文 metadata audit（Crossref/OpenAlex/Semantic Scholar）+ 多交易所公开盘口 `2s` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**同一资产在多交易所同时报价时，单一 venue 对“全市场中位价”出现短时离群，通常会向中位价回归；交易上做 `short rich venue / long cheap venue` 的 cross-venue relative-value spread close。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/cross-venue/median-consensus/outlier-reversion/law-of-one-price/spot-perp/perp-perp/1m/3m/5m/15m/paper/public-data/cost/risk
- 证据类型：paper metadata + public API live probe

## 1) 这次看了什么
主线材料：
- **Jingrui Li, Ruming Liu (2024)**
- **Title：** *Pricing and Arbitrage Across 80 Cryptocurrency Exchanges*
- **Venue：** SSRN Electronic Journal
- **DOI：** `10.2139/ssrn.4816710`
- **Readable URL：** <https://doi.org/10.2139/ssrn.4816710>
- **Repo URL：** 未检索到官方公开仓库（N/A）

辅助材料（执行层参考，不是本轮 base alpha）：
- **Kristína Okasová, Kristián Košťál (2024)**
- **Title：** *Using Machine Learning for Predicting Arbitrage Occurrences in Cryptocurrency Exchanges*
- **Venue：** 2024 IEEE ICBC
- **DOI：** `10.1109/ICBC59979.2024.10634339`
- **Readable URL：** <https://doi.org/10.1109/ICBC59979.2024.10634339>
- **Repo URL：** 未检索到官方公开仓库（N/A）

先把 base alpha 说清楚：
> **这条线的 base alpha 不是“某两家交易所瞬时价差”本身，而是“某个 venue 对全市场共识价（median）的离群 + 回归”。**

也就是说，它不是传统 pair-only 搬砖视角，而是 **breadth-consensus 视角**：
- 两两价差会被偶然噪声误导；
- “对全市场中位价离群”的信号更稳、更像真实错价。

---

## 2) 一句话结论 + 怎么证明
- **一句话核心结论：** 对 short-cycle desk，跨所套利更值得先做成“离群 venue 回归到多 venue 中位价”的 raw alpha，而不是只盯单一 pair spread。
- **一句话证明方式：** 先用 2024 SSRN（80 exchanges）给出研究主线，再用公开 API 做 `2s` 实时快检，验证“离群点下一步收敛”在当下盘口里是否仍可观察。

---

## 3) 本轮最小快检（公开数据，实时）
### 3.1 数据口径
- 资产：`BTCUSDT`, `ETHUSDT`
- 交易所：`Binance / OKX / Bybit / KuCoin / MEXC`
- 数据：各所 top-of-book（bid/ask），取 `mid=(bid+ask)/2`
- 频率：每 `2s` 抓一次，共 `36` 轮（约 72 秒）
- 指标：
  - `median_mid_t`：同时刻五所中位价
  - `dev_bps_{venue,t} = (mid_{venue,t}/median_mid_t - 1) * 1e4`
  - 每轮取 `|dev|` 最大者为“离群 venue”
  - 看该 venue 下一轮 `|dev|` 是否压缩（1-step convergence）

产物：
- `reports/artifacts/quant_digests/2026-04-23_1049_xvenue_median_outlier_probe_raw.csv`
- `reports/artifacts/quant_digests/2026-04-23_1049_xvenue_median_outlier_probe_summary.csv`

### 3.2 关键结果（3 个数据点）
1. **BTC 离群总体较薄**：全样本 `median |dev| = 0.187 bps`，`p95 |dev| = 0.994 bps`。  
2. **ETH 离群更厚**：全样本 `median |dev| = 0.411 bps`，`p95 |dev| = 1.513 bps`。  
3. **离群后下一步收敛存在，但强度有资产差异**：
   - BTC：`1-step compress rate = 57.1%`，下一轮仍 `>1bp` 仅 `14.3%`
   - ETH：`1-step compress rate = 54.3%`，下一轮仍 `>1bp` 高达 `74.3%`

翻成人话：
- BTC 更像“离群很快被抹平”；
- ETH 更像“离群更常见，且会拖更久”，因此更适合 `1m/3m` 的执行壳去吃。

---

## 4) 为什么这条线对当前 desk 有直接价值
- 它是 **raw alpha（relative-value / stat-arb）**，不是纯 filter。
- 能直接映射到你当前周期：
  - `1m/3m`：做信号主执行（离群回归）
  - `5m/15m`：做 regime / risk throttle（只在有足够离群厚度时开闸）
- 相比“只盯 A-B 两所价差”，它天然更抗单所噪声：
  - 用中位价当共识锚，能降低“某一所盘口异常”导致的误触发。

---

## 5) 可直接落地的完整策略壳（entry/exit/sizing/risk/cost）
## 5.1 Entry（入场）
对每个时刻 t：
1. 计算各 venue 的 `dev_bps`；
2. 找 `rich = argmax(dev_bps)`，`cheap = argmin(dev_bps)`；
3. 若 `dev_bps(rich) - dev_bps(cheap) >= theta_enter` 且两腿流动性通过门槛，则开仓：
   - short rich
   - long cheap

建议初始阈值：
- BTC：`theta_enter = 1.0 ~ 1.2 bps`
- ETH：`theta_enter = 1.5 ~ 2.0 bps`

## 5.2 Exit（出场）
- 主出场：`spread_gap <= theta_exit`（如 `0.3~0.5 bps`）
- 保护止损：`spread_gap >= theta_stop`（如入场阈值的 `1.8~2.2x`）
- 时间止损：`max_hold = 1m/3m/5m`（按资产分桶）

## 5.3 Sizing（仓位）
- `size ~ min(edge_after_cost / vol_1m, per_venue_cap, symbol_cap)`
- 按 `|gap|` 强弱分档（弱/中/强三档），不要固定手数
- 对单 venue 设库存上限，避免“只在某所越滚越大”

## 5.4 Risk（风控）
- 任何单腿未成交或成交偏离超阈值，立刻降级/撤单
- 交易所健康状态异常（API/延迟/盘口跳空）直接全局 veto
- 资金费率窗口前后降杠杆（避免 funding 噪声主导 spread）

## 5.5 Cost（成本）
必须单独建 friction ladder：
- `4 / 8 / 12 bps` round-trip
- maker-fill-rate 分层（25% / 50% / 75%）

若 `post-cost` 在 `8 bps` 后已为负，则这条线只能保留为“执行观察层”，不应继续占主研究资源。

---

## 6) 与已有 cross-venue 研究的区别（避免重复）
这轮不是重复“Binance vs Bybit 两两价差回归”，而是明确换成：
- **多 venue 共识锚（median）**
- **离群 venue 识别**
- **breadth-first 的回归交易框架**

这条改写更接近 80-exchange 论文标题表达的核心，也更适合做后续 `router`：先判断“谁离群”，再决定交易哪一对腿，而不是先固定腿再找机会。

---

## 7) 下一步怎么测（必做）
1. **把快检扩成 7~14 天连续抓取**（优先 WS，至少 `1s~2s` 级），按 UTC 时段分层。  
2. **A/B 测试：pair-only zscore vs median-outlier**，比较 `net bps/trade`、`fill-adjusted winrate`、`tail loss`。  
3. **做资产分层阈值**：BTC/ETH/SOL 不共用一个 `theta_enter`。  
4. **加执行可行性门槛**：盘口深度、最小可成交名义、单腿滑点上限。  
5. **把信号映射到 perp-perp 可交易腿**，重算含 funding 的真实净值；若只在 spot 可见而在 perp 不可交易，要明确降级。

---

## 8) 数据源公开性与最小复现实验口径
- Binance Spot bookTicker：公开 REST，秒级可取
- OKX Spot ticker：公开 REST，秒级可取
- Bybit Spot tickers：公开 REST，秒级可取
- KuCoin Spot level1：公开 REST，秒级可取
- MEXC Spot bookTicker：公开 REST，秒级可取

最小复现实验：
- 同步抓五所同标的 top-of-book；
- 计算 `median + venue dev_bps`；
- 统计离群下一步回归概率与回归幅度；
- 再套入成本与成交门槛，判断是否保留为可交易 alpha。

---

## 9) 风险与保留意见
- 这轮主论文目前受 SSRN 反爬限制，**正文不可直读**，本轮证据以 metadata + 实时快检为主，强度低于 full-text audit。
- 快检样本很短（约 72 秒），只用于确认“有没有可观测离群回归现象”，不能代替正式回测。
- 真正生死线仍在执行层：延迟、挂撤能力、单腿风险、费率等级。

---

## 10) 来源
1. **Li, J., & Liu, R. (2024). _Pricing and Arbitrage Across 80 Cryptocurrency Exchanges_. SSRN Electronic Journal.**
   - DOI: <https://doi.org/10.2139/ssrn.4816710>
   - Readable URL: <https://doi.org/10.2139/ssrn.4816710>
   - Repo URL: N/A（未检索到官方公开仓库）
2. **Okasová, K., & Košťál, K. (2024). _Using Machine Learning for Predicting Arbitrage Occurrences in Cryptocurrency Exchanges_. 2024 IEEE ICBC.**
   - DOI: <https://doi.org/10.1109/ICBC59979.2024.10634339>
   - Readable URL: <https://doi.org/10.1109/ICBC59979.2024.10634339>
   - Repo URL: N/A（未检索到官方公开仓库）
3. **本地实时快检产物**
   - `reports/artifacts/quant_digests/2026-04-23_1049_xvenue_median_outlier_probe_raw.csv`
   - `reports/artifacts/quant_digests/2026-04-23_1049_xvenue_median_outlier_probe_summary.csv`
