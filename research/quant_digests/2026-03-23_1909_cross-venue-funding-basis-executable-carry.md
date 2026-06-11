# 别把 funding/basis 监控面板只当看板：这份 2026 新仓库更值钱的是“可执行跨 venue carry 排名”这条 raw alpha 骨架
- 时间：2026-03-23 19:09 UTC
- 类型：2026 GitHub 新仓库 + 公开交易所 API 最小快检
- 主题类型：raw alpha
- 基础 alpha：cross-venue carry（同一币种在不同 venue 的 `funding 差 + basis 差`，扣成本后做 market-neutral 对冲）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/relative-value/stat-arb/cross-venue/market-neutral/execution-capacity/cost/1m/3m/5m/15m
- 证据类型：仓库工程证据 + 公共 API 快检

> 先回答 base alpha：这篇东西的 base alpha 不是“监控页面”，而是**跨 venue carry 差值本体**——`funding_diff + basis_diff - 全部执行成本`。

## 1. 这次看了什么
这次主看 2026 新仓库 **Razrocks/Funding-Basis---Strategy-Monitor**。和常见“只看 funding 排行榜”不同，这个仓库把可交易性直接写进公式：
- 不只看 funding，还把 basis（mark-index premium）并入；
- 不只看毛收益，还把 fees / slippage / borrow 显式扣掉；
- 不只看数值高低，还加 execution capacity（10bps 深度）与 trap tags（funding spike / OI shock / basis inversion）。

对当前 desk 来说，这条线最有价值的是：它是 **carry/raw alpha 主体**，不是把 funding 继续降级成 veto 配件。

## 2. 核心结论
- **一句话核心结论：** 这份仓库最值得复现的不是 dashboard，而是“`funding+basis` 的可执行 pair ranking 引擎”；它能直接产出 entry/exit/sizing/risk/cost 的完整策略骨架。  
- **一句话它怎么证明：** 仓库给了可运行 API + 前端 + 风险事件流 + 成本假设；我再用 Binance/Hyperliquid/dYdX 公共接口按同口径跑了最小快检，验证“同一 alpha 在不同持有期/滑点假设下生死分裂”。

3 个关键数据点（本轮）：
1. 仓库默认是 **每 30 秒**轮询三家 venue，并在 API 里直接给 cross-venue arb 排名（不是离线报告）。
2. 仓库默认成本假设：Binance/Hyperliquid/dYdX taker 费率约 **4 / 2.5 / 5 bps**，默认仓位 **$25,000**，容量阈值 **10 bps**。  
3. 本地快检（同口径）显示强烈成本敏感：
   - 若用 **1 天持有 + 10bps/side 滑点压力**，`BTC/ETH/SOL` 的 best pair 年化净边全为负（best 约 **-75.29% APR**）；
   - 若改为 **7 天持有 + 3bps/side**，best pair 转正：`BTC` 约 **+29.26% APR**、`ETH` 约 **+9.07% APR**、`SOL` 约 **+42.50% APR**（均为模型化年化近似，非实盘收益承诺）。

## 3. 为什么和当前短周期 desk 直接相关
- 这条线补的是 **raw alpha 素材池里的 carry/basis**，不是再给 breakout/EMA 加一个解释层。
- 它可以直接拆成完整策略组件：
  - **entry**：`net_carry_after_cost > entry_threshold`
  - **exit**：`net_carry` 回落/反转，或达到最大持有 funding 窗口
  - **sizing**：按 execution capacity + 质量分数（quality score）分档
  - **risk**：trap tags 触发减仓/禁开（funding spike / OI shock / basis inversion）
  - **cost**：fee + slippage + borrow 显式入账
- 对 `1m/3m/5m/15m` 的关系也清楚：
  - alpha 本体是 funding/basis carry（低频结算）；
  - 短周期主要用于 **执行、容量和风险监控**，而不是硬伪装成逐根方向信号。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / market-neutral carry
- 基础 alpha：同币跨 venue 的 `funding_diff + basis_diff` 在成本后仍为正
- regime：资金费分化持续、盘口深度可成交、basis 未快速反向时更友好
- filter / veto：funding 异常尖峰、OI 冲击、basis 倒挂、盘口容量不足、数据延迟异常
- risk / sizing / execution overlay：
  - 容量约束下限仓（participation cap）
  - 质量分数低于阈值不做
  - 先 maker 后 taker，跨 venue 价差/容量不足时不强开

## 4. 外部数据口径（公开性 / 频率 / 最小复现实验）
### 数据源与公开性
- Binance Futures 公共接口（`premiumIndex`）
- Hyperliquid 公共 `info` 接口（`metaAndAssetCtxs`）
- dYdX v4 indexer 公共接口（`perpetualMarkets`）
- 均为公开可拉取，无需私钥（读模式）

### 更新频率
- 仓库默认 30 秒轮询；
- 可聚合/映射到 `1m/3m/5m/15m` 执行监控层。

### 最小可复现实验
- 标的：`BTC/ETH/SOL`
- venue：Binance + Hyperliquid + dYdX
- 信号：`gross = funding_diff + basis_diff`
- 成本：`roundtrip fee + slippage`，并按持有期折算年化成本
- 输出：pair 级 `gross/cost/net` 排名 + 事件标签触发记录

## 5. 下一步怎么测（直接执行）
1. **先做成本-持有期二维网格**：`hold_days × slippage`，找出 `net>0` 的稳定区域，而不是只看单点。  
2. **把 dYdX 预测 funding 与已实现 funding 分开回放**：避免“预测值当已实现”高估。  
3. **容量一致性测试**：在固定 participation cap 下重算净边，验证“信号 edge → 可成交 edge”衰减。  
4. **接入 5m 风控回放**：把 trap tags 写成强规则（减仓/停机），评估 tail 风险削减是否值得。  
5. **实盘前门槛**：要求 OOS 下 `post-cost net > 0`、`capacity 通过`、`事件窗口回撤可控` 三项同时满足。

## 6. 风险与保留意见
- 该仓库偏“监控+评分引擎”，不是现成执行系统；仍需自建下单与对账层。  
- dYdX 端 funding 有预测成分，若直接当 realized 处理会高估收益。  
- 年化净边对持有期和滑点极敏感；短持有高冲击下，edge 可能迅速归零。  
- 跨 venue 还有转账、保证金调度、限仓与系统延迟风险，不能只看纸面 pair ranking。

## 7. 来源
1. **Razrocks. (2026). _Funding-Basis---Strategy-Monitor_. GitHub repository.**  
   - Repo URL: https://github.com/Razrocks/Funding-Basis---Strategy-Monitor  
   - Readable URL: https://github.com/Razrocks/Funding-Basis---Strategy-Monitor  
2. **He, S., Manela, A., Ross, O., & von Wachter, V. (2022/2024). _Fundamentals of Perpetual Futures_. SSRN / arXiv.**  
   - DOI: https://doi.org/10.2139/ssrn.4301150  
   - Readable URL: https://arxiv.org/abs/2212.06888  
   - Repo URL: N/A
3. **Binance USDⓈ-M Futures API（公开）**  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price  
4. **Hyperliquid API Docs（公开）**  
   - Readable URL: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint  
5. **dYdX v4 Indexer API（公开）**  
   - Readable URL: https://docs.dydx.xyz/indexer-client/http

## 8. 本地复现产物
- `reports/artifacts/quant_digests/funding_basis_monitor_20260323_1906/snapshot_pairs.csv`
- `reports/artifacts/quant_digests/funding_basis_monitor_20260323_1906/sensitivity.csv`
