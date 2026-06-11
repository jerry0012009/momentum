# 别把这份 2026 新 repo 只读成链上课程项目：对 short-cycle desk，更该先测的是「7d funding carry gate × delta-neutral 对冲壳」这条完整 carry raw alpha
- 时间：2026-04-03 11:08 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `docs/strategy.md` + `docs/market_regimes.md` + `backtest/run_backtest.py` + `report/final_report.md`）+ 2026 SSRN 新文献 metadata grounding（Crossref）
- 主题类型：raw alpha
- 基础 alpha：**funding carry（同标的现货多头 + 永续空头）**；赚的是“正 funding 持续支付”，不是价格方向；`7d annualized funding > hurdle` 时持仓，否则空仓
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/spot-perp/same-underlier/delta-neutral/gate-threshold/regime/5m/15m/3m/1m/repo/paper/public-data/cost/risk
- 证据类型：repo 策略代码与回测结果（主）+ 新文献摘要元数据（辅）

## 1) 先回答：这篇东西的 base alpha 是什么？
一句话：

> **base alpha 就是“做空 perp 收 funding + 现货对冲方向风险”的 carry，不是 filter。**

也就是：
- **Alpha 本体**：funding/carry
- **Regime/Gate**：`7d 滚动年化 funding` 是否高于门槛
- **Execution/Risk 壳**：入出场成本、持仓上限、资金利用率、回撤约束

这满足本轮优先级里“raw alpha 可独立复现并可落地完整策略”的要求。

---

## 2) 为什么这轮选它（而不是继续写另一篇 breakout/retest）
这份新 repo（`SAGISaiKrishna/crypto-arbitrage-strategy`，创建于 2026-03-26，最近更新 2026-04-03）给的不是纯解释，而是一条几乎完整的策略骨架：
- entry：`carry gate`（`7d rolling annualized funding > 250 bps`）
- exit：gate 失效即平仓回现金
- sizing：按资本与入场价格确定对冲规模
- risk：显式讨论 margin/liquidation/funding reversal
- cost：每次进出扣 `0.20%` 交易成本

对 desk 的价值在于：
- 我们已有很多 trend/MR 卡；
- 这张卡补的是 **carry/funding 这条不同收益来源**，可与现有方向性 alpha 低相关拼接。

---

## 3) 来源与可追溯信息
### A. 主来源（repo）
- **Authors / Owner：** SAGISaiKrishna
- **Year：** 2026
- **Title：** `crypto-arbitrage-strategy`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/SAGISaiKrishna/crypto-arbitrage-strategy>
- **Repo URL：** <https://github.com/SAGISaiKrishna/crypto-arbitrage-strategy>
- **GitHub metadata：** created `2026-03-26T20:12:05Z`, updated `2026-04-03T05:32:50Z`, pushed `2026-04-03T04:46:37Z`

### B. 文献 grounding（近 5 年）
1. **Cao, Luo, Cheng, Dong (2026)**, *Anatomy of Cryptocurrency Perpetual Futures Returns*, SSRN preprint, DOI: `10.2139/ssrn.6365329`  
   - Readable URL: <https://www.ssrn.com/abstract=6365329>
2. **Gornall, Rinaldi, Xiao (2025)**, *Funding Payments Crisis-Proofed Bitcoin's Perpetual Futures*, SSRN preprint, DOI: `10.2139/ssrn.5036933`  
   - Readable URL: <https://www.ssrn.com/abstract=5036933>

> 注：本轮 paper 作为机制与因子空间的辅助 grounding；策略可复现实体主要来自 repo 代码。

---

## 4) repo 里最关键的可复现策略定义（不是概念）
基于 `docs/strategy.md` 与 `backtest/run_backtest.py`：

### 4.1 Entry / Exit
- **Entry gate**：`7-day rolling annualized funding > 250 bps`
- **Exit gate**：跌回门槛下方就平仓（回现金）
- gate 信号做了 lag，避免直接 look-ahead

### 4.2 PnL 分解
每小时：
- spot leg PnL
- perp short leg PnL（方向相反）
- funding PnL（主要收益来源）
- 进出场交易成本

策略强调：价格腿大体对冲，净收益应主要来自 funding。

### 4.3 成本与门槛
- 交易成本假设：每次进出 `0.20%`
- hurdle 250 bps 的解释：机会成本 + 交易成本缓冲

### 4.4 风险
- 资金费反转（正 funding 变负）
- 杠杆腿的保证金/清算风险
- 无再平衡时的对冲漂移

---

## 5) 关键数据点（来自 repo 文档/脚本）
可直接拿来做“先验可信度”检查的 5 个数：
1. 回测区间：Bybit 2021–2026，约 1h 频率长期样本
2. 报告净收益：`+$18,442`（初始 `$10,000`）
3. 报告年化：`35.2%`
4. 报告最大回撤：`-13%`
5. 持仓占比：约 `79%` 时间在场、`21%` 现金空仓

同时 repo 也承认：
- 结果对 2021 高 funding 环境依赖较高；
- 2022–2026 Sharpe 明显更低（文档给出约 `0.4` 量级）。

这对 desk 很重要：不是“稳定印钞 alpha”，而是 **regime 敏感的 carry alpha**。

---

## 6) 与当前 short-cycle（1m/3m/5m/15m）的关系（必须说清）
这个 alpha 的经济驱动偏慢（funding 结算节奏通常是 8h），所以**不应伪装成逐根 1m 主信号**。正确落地方式是：

- **主 alpha 频率**：`5m/15m` 决策壳（是否在场、仓位多少）
- **执行频率**：`1m/3m` 只做入场优化与冲击控制（maker/taker、分批）
- **持有周期**：小时到天级（由 gate 决定），不是几根 K 的快进快出

换句话说：
> 这条 alpha 在 short-cycle 体系里是“可高频执行的慢驱动 raw alpha”，不是“超短预测信号”。

---

## 7) 最小可复现实验（可直接开工）
## 实验 A（优先）：15m carry gate 版（完整策略）
**标的**：`ETHUSDT`（先单币，再扩到 BTC/SOL）  
**数据**：
- 现货价格（公开可得，交易所 API）
- perp 价格 + funding（公开可得，交易所 API）
- 频率：15m bars + funding clock

**信号**：
- `carry_score_t = annualized_rolling_funding(7d, lagged) - cost_hurdle`
- 入场：`carry_score_t > 0`
- 离场：`carry_score_t <= 0` 或 funding 转负并持续

**仓位**：
- `target_notional = capital * w`
- `w = clip(k / realized_vol_1d, 0, w_max)`（波动越大仓位越小）

**风控**：
- 单腿保证金利用率上限
- funding 急剧反转硬阈值（例如 24h 累计转负）
- time-stop（连续 N 天 carry 不达标则离场）

**成本**：
- maker/taker 两套（如 4/8 bps 与 8/16 bps）
- 明确考虑换仓频率与门槛敏感性

**验收指标**：
- 净收益、回撤、Calmar
- 收益分解：funding / basis / residual delta
- 与 BTC/ETH 方向性策略的相关性（组合价值）

## 实验 B（次优先）：5m 执行 veto 层
在 A 的基础上仅新增 execution veto，不改 alpha 本体：
- 盘口冲击或瞬时滑点超阈值时，延迟入场到下一个 5m 桶
- 比较“立即入场 vs veto 入场”的净边际

目标：确认这条慢驱动 carry 在 short-cycle execution 下是否更耐成本。

---

## 8) 这条策略的 desk 化拆解
可以直接拆成三块组件，方便接入现有框架：

1. **Raw alpha 组件（必须保留）**
   - funding carry gate
2. **Regime/filter 组件（可替换）**
   - 门槛从固定 250 bps 改为动态 hurdle（成本+波动+容量）
3. **Risk/Execution 组件（强烈建议增强）**
   - 5m 执行 veto、分批成交、资金利用率上限、熔断

---

## 9) 本轮结论（给研究池的落地口径）
这轮不是在讲“funding 是什么”，而是确认了一个**可独立复现且可直接落地完整策略**的 raw alpha 候选：

> **delta-neutral funding carry（spot-perp）+ clear gate + clear cost + clear risk。**

它最适合当前 desk 的位置是：
- 作为与趋势/MR 低相关的第三收益腿；
- 用 `15m` 做策略层开关，用 `5m/1m` 做执行优化；
- 先跑单币 ETH，再扩成多币 carry 组合与资金分配。

若 A/B 两个最小实验通过，这条就可以从 digest 进入“可排期复现”列表。