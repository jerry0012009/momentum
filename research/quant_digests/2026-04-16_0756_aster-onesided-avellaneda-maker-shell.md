# 别把这份 Aster 做市仓只读成 Avellaneda 教材：对 short-cycle desk，更该先拆的是「one-sided inventory-flip × trend-biased quote capture」这条完整 raw alpha 壳

- 时间：2026-04-16 07:56 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `market_maker.py` + `backtester.py` + `calculate_avellaneda_parameters.py` + `intensity.py` + GitHub API metadata）
- 主题类型：raw alpha
- 基础 alpha：**在超短微结构里做 spread capture，但不是双边同时挂单；而是用 trend bias 决定当前只做一侧开仓，持仓后切到减仓侧，靠 quote edge + inventory 回归完成一轮 alpha 闭环**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（complete shell）
- 主题标签：raw-alpha/maker/market-making/microstructure/one-sided/inventory-flip/avellaneda-stoikov/supertrend/crypto-perpetual/aster/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 代码证据 + 工程实现证据

## 1) 先回答：这篇东西的 base alpha 是什么？

一句话：**base alpha 不是“Avellaneda 公式”本身，而是“trend-biased 的单侧挂单 + inventory 反向回补”的微结构价差捕获。**

也就是：
- 平仓/空仓阶段：根据趋势只在一侧挂单拿 inventory；
- 有仓阶段：只在减仓侧挂单，把 inventory 逐步 flatten；
- 中间用动态 spread、价格刷新阈值、最小下单约束和风控门槛控制可交易性。

## 2) 来源信息（repo-based）

- Authors / Maintainer：GitHub `djienne`
- Year：2025-2026（`created_at=2025-09-24`, `pushed_at=2026-04-16`）
- Title：*ASTER_Market_Making*
- Venue：GitHub Repository
- DOI：N/A（仓库）
- Readable URL：<https://github.com/djienne/ASTER_Market_Making>
- Repo URL：<https://github.com/djienne/ASTER_Market_Making>

策略母体（方法地基）：
- Avellaneda, M., & Stoikov, S. (2008). *High-frequency trading in a limit order book*. Quantitative Finance.
- DOI：<https://doi.org/10.1080/14697680701381228>
- Readable URL：<https://api.crossref.org/works/10.1080/14697680701381228>

## 3) 为什么它和已有 maker digest 不重复

这份仓库最不一样的点不是“又一个 A-S”，而是**明确 one-sided at a time**：
1. 不是同时 bid/ask 两边被动做市；
2. 先按趋势偏置拿仓，再只做减仓侧；
3. 代码里把“先清仓再开新方向”写成显式状态机。

这更接近“maker 执行壳 + directional bias alpha”的混合体，和纯 OFI/microprice 双边报价路线不同。

## 3.5) 策略拆解（必填）

- 方向属性：**单资产 + 微结构 spread capture（带方向偏置）**
- 基础 alpha：**`trend-biased single-side quote edge`**
- regime：SuperTrend 方向判定（默认周期更新）
- filter / veto：
  - symbol 必须可交易（TRADING）
  - 最小下单名义与最小数量检查
  - 动态 spread 夹在 `5~200 bps`（配置护栏）
- risk / sizing / execution overlay：
  - 仓位默认按余额 `20%`（`DEFAULT_BALANCE_FRACTION=0.2`）
  - `POSITION_THRESHOLD_USD=15` 控制显著持仓逻辑
  - 最小价格变动阈值 `1bp` 才重挂（减少无效撤单）
  - 订单生命周期保底刷新 `60s`

## 4) 可直接复用的关键工程点（1~3 个关键数据点）

1. **参数优化不是拍脑袋**：`backtester.py` 对 `gamma` 做网格搜索，并同时扫 `9` 个时间视野（5m, 15m, 30m, 1h, 2h, 4h, 8h, 12h, 24h）。
2. **风控护栏写进参数链路**：动态 spread 计算后强制 clamp 到 `5~200 bps`，避免极端参数把报价推到不可执行区。
3. **数据采集可公开复现**：`data_collector.py` 用公开 WebSocket 抓 trade/orderbook（无需私钥），先完成参数估计，再驱动 live quoting。

## 5) 与 `1m/3m/5m/15m` 的关系

这条壳本质是秒级执行，但可以按 desk 节奏拆层：
- `1m/3m`：做 micro-regime 与交易密度过滤（是否开机、是否收缩仓位）；
- `5m/15m`：做趋势偏置主判定（是否只做多侧/只做空侧）；
- 秒级层：仅负责挂撤单执行与 inventory 回补。

所以它不是“必须上 HFT 才能用”；可以先用 `5m/15m` 管方向，用更高频层做执行。

## 6) 最小可复现实验（可快速开跑）

- 数据源：Aster public trade + depth（公开可得）
- 资产：先 `BTCUSDT`
- 样本：近 14~30 天
- 频率映射：
  - 执行回放：5s
  - 方向门控：`5m`（主）+ `15m`（对照）
- A/B 设计：
  1) one-sided + supertrend（repo 原版）
  2) same spread same risk，但去掉 trend gate（检验 gate 是否真增益）
- 成本：maker/taker 两档 + 撤单成本近似
- 先看指标：
  1) 成本后每轮 inventory cycle 的期望收益；
  2) inventory 偏离持续时长（是否常卡在单边仓位）。

## 7) 风险与保留意见

1. 交易所特异性较强（Aster API/撮合特征），跨 venue 迁移要重标定。
2. one-sided 模式在单边急行情下可能出现“只拿仓、难减仓”的库存拖尾。
3. 若深度数据只有 top-N snapshot（非完整本地簿），对真实排队成交率会偏乐观。

## 8) 下一步怎么测（本轮后直接动作）

1. **先做 2×2 开关实验**：`trend gate on/off` × `one-sided/two-sided`，看真实增益来自哪里。
2. **把 `5m/15m` gate 接到同一执行层**，比较 trade count、inventory half-life、post-cost PnL。
3. **增加 worst-inventory timeout**：若持仓超过阈值时间未回补，强制减仓，避免库存僵死。
4. **做 friction ladder**：在 `4/8/12 bps` 三档下看策略是否仍存活，再决定是否进入复现池下一阶段。

---

## 参考

1. GitHub Repo: `djienne/ASTER_Market_Making`  
   <https://github.com/djienne/ASTER_Market_Making>
2. Avellaneda, M., & Stoikov, S. (2008). *High-frequency trading in a limit order book*. Quantitative Finance.  
   DOI: <https://doi.org/10.1080/14697680701381228>
3. Crossref metadata for DOI  
   <https://api.crossref.org/works/10.1080/14697680701381228>
