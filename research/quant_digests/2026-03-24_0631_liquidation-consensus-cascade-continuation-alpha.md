# 别把 liquidation map 只当风险看板：这份 2026 新仓库更该先测的是「Funding + OI 背离 + 鲸鱼清算簇共识」级联延续 raw alpha
- 时间：2026-03-24 06:31 UTC
- 类型：2026 GitHub 新仓库 + 交易所公开 API 文档 + 代码规则拆解
- 主题类型：raw alpha
- 基础 alpha：当 `funding` 极端、`OI` 在 `4h` 内快速堆积且价格未同步、并且价格靠近高密度清算簇时，未来 `5m~30m` 更容易出现同向强制平仓级联，适合做**延续**而非先验抄底
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/liquidation/funding/open-interest/whale-clusters/cascade/continuation/event-driven/crypto/1m/3m/5m/15m
- 证据类型：仓库 README + 配置与信号/执行代码 + 官方 API 文档

## 1. 这次看了什么
先回答 base alpha：**这是 raw alpha，不是 filter。**

这轮选题来自 2026 新仓库 `wilsontiger2222/liquidation-hunter`。它最值得我们 desk 先拿来做最小实验的点，不是“liquidation map 能不能当风险提示”，而是：

**把 crowding（funding）+ 脆弱持仓堆积（OI 背离）+ 清算密度（cluster proximity）合成一个可交易的级联延续信号。**

它已经给了完整策略骨架：`entry / exit / sizing / risk / timeout / mode(alert/paper/live)` 全有，适合直接映射到 `1m/3m/5m/15m` 的快速复现流水线。

## 2. 核心结论（先给结论）
- **一句话结论：** 这条线应进入 raw-alpha 素材池，且优先作为“事件驱动延续策略”验证，不要先降级成仅做 veto/filter。
- **为什么：** 该仓库信号层和执行层耦合完整，参数少、可解释性强、能快速做 first verdict。

关键数据点（来自公开代码/配置，非我方独立业绩复核）：
1. 触发阈值：`funding_rate_threshold = 0.0005 (0.05%)`，`oi_delta_threshold = 5% (4h)`，`liquidation_proximity = 1.5%`，`min_confidence = 0.6`。  
2. 信号权重：`funding 0.35 + oi_divergence 0.30 + liquidation 0.35`，三路共识后按加权方向出信号。  
3. 风险与持仓：`position_size = 20%`、`max_positions = 3`、`TP=2%`、`SL=1%`、`timeout=30m`，轮询粒度 `30s`。

## 3. 为什么和当前项目直接相关
- 它直接补的是 **raw alpha 候选**（event-driven / continuation），不是纯解释层。  
- 与当前 desk 的短周期目标匹配：信号形成可在 `1m/3m/5m`，兑现窗口可放在 `5m~30m`。  
- 与最近积累形成互补：我们已有多条 trend / lead-lag / basis 线，这条补的是 **crowding -> forced flow** 家族。

## 3.5 策略拆解（必填）
- 方向属性：event-driven liquidation continuation alpha  
- 基础 alpha：拥挤方向在脆弱结构下更易触发同向强平链式反应，价格短窗内延续概率上升  
- 触发层：
  - Funding 极端（正 funding 偏向做空，负 funding 偏向做多）
  - OI 在 `4h` 内显著上升但价格跟不上（脆弱背离）
  - 距离高密度清算簇不超过 `1.5%`
- 聚合层：三路信号加权投票，置信度过 `0.6` 才下单
- 执行层：
  - 单笔资金：总资金 `20%`
  - 并发上限：`3` 笔
  - 止盈止损：`+2% / -1%`
  - 超时退出：`30m`
- 成本层：仓库未给严谨交易所分档成本模型，需在我方复现时补齐 maker/taker/冲击三档

## 4. `1m / 3m / 5m / 15m` 映射
- `1m`：用于事件监控与信号确认（建议最细观测层）。
- `3m`：可做去噪确认，减少单根 wick 误触发。
- `5m`：推荐主形成窗（与 crowding/背离逻辑最匹配）。
- `15m`：推荐主兑现窗之一（`15m/30m` 两档比较）。

对 desk 的实操定位：
**`5m formation -> 15m/30m monetization` 的级联延续策略。**

## 5. 数据源、公开性与最小可复现实验口径
### 5.1 数据源与公开性
1. Hyperliquid Info API（公开）
   - `metaAndAssetCtxs`（funding / OI 等）
   - `clearinghouseState`（钱包持仓、杠杆、清算价）
   - `frontendOpenOrders`（可见触发单/条件单）
2. Binance USDⓈ-M Futures 公共接口（公开）
   - Open Interest
   - Funding Rate History
3. （可选）公开 liquidation heatmap 网站作交叉验证（CoinGlass/HyperDash 等）

### 5.2 更新频率
- 可按 `30s~1m` 拉取并重算；能直接映射 `1m/3m/5m/15m` 最小实验。

### 5.3 最小实验（第一版）
- 标的：`BTC, ETH`（先小集合）
- formation：`5m` 主窗（同时保留 `1m` 监控）
- 信号：沿用仓库阈值先跑基线
- 进场：signal bar close 后 next bar open
- 出场：`TP/SL/timeout(30m)` 三重退出
- 成本：先跑 `6/12/20 bps round-trip` 三档压力测试

## 6. 下一步怎么测（必须）
1. **A/B 测试 alpha 本体**：
   - A 组：只用 funding+OI
   - B 组：funding+OI+liquidation cluster（完整）
   比较 `hit rate / avg post-cost return / MFE/MAE`，确认清算簇是否真增益。
2. **延续 vs 反转 双出口**：
   同一入场下测试“延续持有 15m/30m”与“逆向均值回归 5m/15m”，避免把结构性反转误当延续。
3. **阈值网格**：
   `funding 0.03/0.05/0.08%`、`OI 3/5/8%`、`proximity 1.0/1.5/2.0%`，看边际稳健区而非单点最优。
4. **可交易性压力测试**：
   加入滑点随波动/成交量扩张规则；若收益只在低成本假设下成立，先留素材池，不升 shadow。
5. **伦理与合规约束**：
   README 提到的 “nudge trade” 不进入我方实验范围；仅做被动跟随，不做任何主动触发级联行为。

## 7. 风险与保留意见
- 仓库很新（2026-02 创建，star/fork 仍低），社会验证不足。  
- README 给出的胜率/盈亏比属于作者口径，需独立复核。  
- 钱包样本选择可能存在选择偏差（只跟踪“已知鲸鱼”）。  
- 交易成本与成交冲击是最大不确定项，尤其在真正的 cascade 时刻。

## 8. 来源
1. **wilsontiger2222 (2026). _liquidation-hunter_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/wilsontiger2222/liquidation-hunter  
   - Repo URL: https://github.com/wilsontiger2222/liquidation-hunter
2. **wilsontiger2222 (2026). _README.md / config.yaml / main.py / src/signals/*.py / src/execution/paper_executor.py_.**  
   - Venue: GitHub (repository code)  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/wilsontiger2222/liquidation-hunter/master/README.md  
   - Repo URL: https://github.com/wilsontiger2222/liquidation-hunter
3. **Hyperliquid Docs (2026 snapshot). _Info endpoint API_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint  
   - Repo URL: N/A
4. **Binance Developers. _USDⓈ-M Futures Market Data: Open Interest_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest  
   - Repo URL: N/A
5. **Binance Developers. _USDⓈ-M Futures Market Data: Get Funding Rate History_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History  
   - Repo URL: N/A
6. **Ruan, Q. (2025). _Perpetual Futures Contracts and Cryptocurrency Market Quality_. SSRN Electronic Journal.**  
   - Venue: SSRN (Working Paper)  
   - DOI: https://doi.org/10.2139/ssrn.5323703  
   - Readable URL: https://www.ssrn.com/abstract=5323703  
   - Repo URL: N/A
