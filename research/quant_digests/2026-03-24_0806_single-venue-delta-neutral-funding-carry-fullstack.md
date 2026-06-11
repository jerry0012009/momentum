# 别把 spot-perp 对冲只当 basis 回归：这份 2026 新仓库更该先测的是「单 venue delta-neutral funding carry」完整 raw alpha
- 时间：2026-03-24 08:06 UTC
- 类型：2026 GitHub 新仓库 + 近 5 年定价论文 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：在单一交易所做 `long spot + short perp`（或反向）赚取资金费率（funding carry），并用 basis 漂移约束风险
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/relative-value/stat-arb/spot-perp/delta-neutral/event-driven/crypto/1m/3m/5m/15m/repo/paper
- 证据类型：仓库工程证据 + 论文定价地基 + 公共数据快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 不是 filter，而是“资金费率现金流本体（funding carry）”**，basis 只是它的侵蚀项和风险项。

主看 2026 新仓库 `SohamMahale/crypto-arbitrage-project`（含 `src/backtester.py`）：它把策略拆成可复刻闭环——`basis + funding` 收益分解、成本扣减、年度与月度分布。再用近 5 年定价论文补地基：为什么 perp 要靠 funding 机制锚定，以及为什么“看起来无风险”的 carry 在现实里会被成本与偏离路径吃掉。

## 2. 核心结论
- **一句话核心结论：** 对我们 desk 来说，这条线最值得 intake 的不是“跨 venue 巨大套利幻想”，而是**单 venue、可执行、可审计的 funding carry 完整策略骨架**。
- **一句话它怎么证明：** 仓库给出 2022–2025 实盘口径回测分解（收益/成本/basis），我再用 Binance 公共数据做 120 天 funding+basis 快检，确认“carry 有，但不厚，且会被 basis 漂移和成本明显侵蚀”。

关键数据点（本轮）：
1. 仓库报告（BTCUSDT, 2022–2025）给出：`4Y CAGR 6.47%`、`平均年化 6.97%`、`2024 年 11.49%`，并明确“20% 常态化不现实”。
2. 本地快检（Binance 公共数据，最近 120 天，360 次 8h funding）：正 funding 占比 `70.3%`，平均每 8h `0.00216%`（按该均值折算年化约 `2.39%`）。
3. 同期若连续持有 `short perp + long spot`，funding 累计约 `+0.7766%`，但 basis 漂移项约 `-0.2237%`，合计只剩 `+0.5529%`（120 天毛收益口径）。

## 3. 为什么和当前项目有关
- 这是 `carry / basis / relative-value` 家族的 **raw alpha 本体**，不是“只会解释行情”的 overlay。
- 它能直接落到完整策略组件：
  - entry：funding 阈值 + basis 限制
  - exit：持有窗/收益目标/风险触发
  - sizing：按资金费率强度与流动性分层
  - risk：basis 漂移、费率反转、流动性冲击
  - cost：现货+永续双腿手续费与滑点
- 与 `1m/3m/5m/15m` 关系：
  - alpha 决策频率是 funding 时钟（8h 事件驱动）；
  - 1m/3m/5m/15m 用于执行切片、进出场和成本控制（不是伪装逐根方向预测）。

## 3.5 策略拆解（必填）
- 方向属性：relative value / carry（market-neutral）
- 基础 alpha：`funding_cashflow - basis_drift - trading_cost`
- regime：高杠杆拥挤（funding 极端）与低波动平静期的收益密度不同
- filter / veto：
  - 仅在 `funding_rate >= threshold`（如 5 bps/8h 档）启用
  - `|basis_z|` 过高禁开（避免“赚 carry、亏漂移”）
  - 重大事件窗（CPI/FOMC 等）降杠杆或禁开
- risk / sizing / execution overlay：
  - 头寸按 funding 档位分层（低/中/高）
  - 设 `basis widening stop`
  - 1m/3m TWAP 分批对冲，避免一次性冲击。

## 4. 可复刻的最小实验
### 4.1 数据源、公开性、更新频率
- Binance USDⓈ-M `fundingRate`（公开 REST，无需私钥读取历史）
- Binance Spot `klines`（公开 REST）
- 更新频率：funding 8h；价格可到 1m（可映射 1m/3m/5m/15m 执行）

### 4.2 最小实验口径（先 15m）
- 标的：`BTCUSDT`（spot + perp）
- 信号：
  - `funding_signal = funding_rate_8h`
  - `basis_t = mark_t/spot_t - 1`
- 交易规则（样例）：
  - entry：`funding_rate >= 5 bps/8h` 且 `|basis_z| < 1.5`
  - direction：`short perp + long spot`
  - exit：持有 1~3 个 funding 周期，或 `basis` 扩大超阈值立即止损
- 成本：至少做 `6/10/14 bps` 三档 round-trip 压力测试
- 先看指标：`post-cost expectancy`、`carry/basis/cost 三项归因`、`容量约束后净收益`

## 5. 下一步怎么测（必须）
1. **做 funding 档位分层回测**：0~5bps、5~10bps、10bps+ 三档分开看成本后边际。  
2. **做持有时长网格**：1/2/3 个 funding 周期，找“收益-风险-资金占用”最优点。  
3. **把 15m 信号下钻到 1m 执行**：比较一次性吃单 vs TWAP 切片的真实侵蚀。  
4. **加入 basis 扩大止损**：验证是否能显著降低“carry 正但净值回撤大”的尾部风险。  
5. **扩展 ETH/SOL**：检查是否存在更厚 carry 或更好容量，不要只盯 BTC 单币。

## 6. 风险与保留意见
- 仓库口径偏“月度汇总”，对短周期执行与冲击成本仍偏乐观，必须做 1m/3m 级别再估。  
- funding 是离散现金流，不是稳定票息；拥挤平仓时 basis 反向扩大会吞噬 carry。  
- 单 venue 虽降低跨交易所运维复杂度，但也带来交易所单点与流动性时段风险。  
- 若只看“正 funding 比例”，不看成本与 basis 漂移，容易把低质量机会误判为 alpha。

## 7. 来源
1. **Soham Mahale (2026). _crypto-arbitrage-project_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/SohamMahale/crypto-arbitrage-project  
   - Repo URL: https://github.com/SohamMahale/crypto-arbitrage-project
2. **Park, H., Choi, M., & Lim, A. E. B. (2025). _Designing funding rates for perpetual futures in cryptocurrency markets_. arXiv.**  
   - Venue: arXiv (q-fin.MF / q-fin.PR)  
   - DOI: https://doi.org/10.48550/arXiv.2506.08573  
   - Readable URL: https://arxiv.org/abs/2506.08573  
   - Repo URL: N/A
3. **He, S., Manela, A., Ross, O., & von Wachter, V. (2024, v6). _Fundamentals of Perpetual Futures_. arXiv.**  
   - Venue: arXiv (q-fin.PR)  
   - DOI: https://doi.org/10.48550/arXiv.2212.06888  
   - Readable URL: https://arxiv.org/abs/2212.06888  
   - Repo URL: N/A
4. **Binance Developers (2026). _USDⓈ-M Futures API: Get Funding Rate History_.**  
   - Venue: Official API Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History  
   - Repo URL: N/A

## 8. 本地复现产物
- `reports/artifacts/quant_digests/funding_carry_singlevenue_20260324_0805/metrics.json`
- `reports/artifacts/quant_digests/funding_carry_singlevenue_20260324_0805/funding_basis_timeseries.csv`
