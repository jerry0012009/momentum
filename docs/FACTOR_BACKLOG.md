# Factor Backlog（候选因子池与研究队列）

> 目标：把当前 `momentum` 项目中的研究对象整理成**可分层、可排序、可执行**的 backlog。
>
> 说明：
> - `CANDIDATE_FACTOR_POOL.md` 负责讲框架与方法；
> - 本文件负责给出“现在到底先做谁”的队列。

---

## 1. 统一评估口径

### 必看指标
- 净收益（Net Return）
- 最大回撤（Max Drawdown）
- 成本后收益（Post-cost Return）

### 逐步补充的稳健性口径
- Cross-market
- OOS split
- Rolling windows
- Positive asset ratio / positive window ratio

### 统一状态
- `SCOPED`：定义已清楚
- `PROTOTYPED`：已有代码 / 脚本
- `REVIEWED`：已有报告与结论
- `KEEP`：保留在主候选池
- `DROP`：证据弱，暂不继续
- `PARKED`：非当前主线，但保留

---

## 2. 当前候选池优先级（v0.1）

## P0：下一轮最值得推进

| 因子 / 模块 | 层级 | 当前状态 | 当前项目对应 | 当前判断 | 下一步动作 |
|---|---|---|---|---|---|
| EMA 结构 | 方向过滤 | `PROTOTYPED` + `KEEP` | 已在 `ema_donchian_breakout` 中承担方向层 | 是当前短周期趋势模板里最清楚、最可解释的方向过滤之一 | 后续单独抽出做“EMA 结构 vs MA slope / 快慢线”对比 |
| Donchian breakout | 触发 | `REVIEWED` + `KEEP` | `src/momentum/signals/ema_donchian_breakout.py` | 裸 breakout 很弱，但作为触发层很有价值 | 保留为触发模板，不单独继续炼丹 |
| Pullback recovery confirmation | 确认增强 / 二次进场 | `REVIEWED` + `KEEP` | `pullback_recovery_confirmation` 系列文档/报告/脚本 | 当前是值得重点回看的高价值候选之一 | 与 EMA / 趋势方向层重新组合，做更结构化复刻 |
| ATR position sizing | 风险控制 | `SCOPED` | 当前只讲透概念，尚未独立实验 | 是从“会止损”走向“会控波动”的关键一步 | 做独立实验：固定仓位 vs ATR 仓位缩放 |
| Volatility regime filter | 环境边界 / 风险控制 | `PROTOTYPED` + `KEEP` | 已有 ATR ratio 分位过滤 baseline A/B | 值得从“附属过滤器”提升为正式候选 | 抽象成独立因子卡，补 cross-market / rolling |
| Endpoint NWE + confirmed extrema foundation | 结构识别底层 / 非 alpha 成果 | `KEEP` | `endpoint_nadaraya_watson.py` / `confirmed_extrema.py` | 当前优先保留成熟可复用底层；平滑与 extrema 对齐外部成熟逻辑，通道/突破业务层暂缓 | 继续做可视化、来源审计、与外部实现对照 |

---

## P1：第二梯队，适合在 P0 后推进

| 因子 / 模块 | 层级 | 当前状态 | 当前项目对应 | 当前判断 | 下一步动作 |
|---|---|---|---|---|---|
| Multi-timeframe momentum | 方向过滤 / alpha 原型 | `REVIEWED` + `KEEP` | `multi_tf_momentum` | 已完成基线研究，但当前不宜继续围绕旧 baseline 微调 | 作为参考底座保留，等待和新候选重新组合 |
| MA slope | 方向过滤 | `SCOPED` | 尚未独立建模 | 很适合作为 EMA 结构的对照组 | 做理论卡片，后续进入轻量复刻 |
| Volume spike / volume recovery | 确认增强 | `SCOPED` / `PROTOTYPED` | 项目里已有 volume 类研究基础 | 与 breakout / pullback 结合价值高 | 先补因子卡片，再决定单独实验还是并入确认层 |
| Market risk-on / risk-off gate v2 | 环境门控 | `REVIEWED` + `KEEP` | `market_risk_on_off_filter.py` | v1 角色定位已清楚，但还不够成熟 | 暂不直接升级；先进入候选池管理，等待更强设计 |
| trailing stop 变体 | 出场 | `SCOPED` | 概念已掌握，但尚无独立实验 | 非常适合做“收益分布塑形”对照 | 未来做出场专项实验 |

---

## P2：保留，但当前不宜重投入

| 因子 / 模块 | 层级 | 当前状态 | 当前项目对应 | 当前判断 | 当前动作 |
|---|---|---|---|---|---|
| Price-volume divergence（当前 baseline） | 确认增强 / 反向警报 | `REVIEWED` + `PARKED` | `price_volume_divergence` | 当前证据偏弱，更像有思路但证据不足的过滤器 | 暂不继续深挖 |
| Swing-point divergence | 确认增强 | `SCOPED` | 尚未正式实现 | 可做，但优先级不高 | 先保留在队列 |
| Trend/choppy first baseline gate | 环境门控 | `REVIEWED` + `KEEP` | `trend_regime_filter.py` | 证明“环境过滤有价值”，但仍是弱有效过滤器 | 保留结论，不继续围绕 baseline 微调 |
| Box consolidation | 触发 / 结构 | `REVIEWED` + `PARKED` | `box_consolidation` | 是独立旁支，不是当前主线 | 保留成果，当前先不推进 |
| Up/down wave | 结构 / 节奏 | `REVIEWED` + `PARKED` | `up_down_wave` | 有研究价值，但和当前主线距离较远 | 保留成果，当前先不推进 |
| Regime triplet | 研究框架 / 状态分析 | `REVIEWED` + `KEEP` | `regime_triplet` | 更像“分析框架”，不是直接下单因子 | 用作辅助评估，不作为当前单因子主攻方向 |

---

## 3. 当前项目中的“已验证模板”与“待拆解组件”

### 已验证模板（保留）
- `multi_tf_momentum`
- `ema_donchian_breakout`
- `pullback_recovery_confirmation`
- `trend_regime_filter`
- `market_risk_on_off_filter`

这些对象的价值，不一定是“已经能直接上实盘”，而是：
- 已经形成了某一层的可解释原型；
- 能反哺候选池，帮助我们判断下一步该重点补哪一层。

### 待拆解为正式候选卡片的组件
- EMA 结构
- MA slope
- Donchian breakout
- 连续收盘确认
- 回踩确认
- ATR position sizing
- trailing stop
- volatility regime filter

说明：这些组件很多已经“存在于模板里”，但还没有完全被抽象成可独立比较的候选对象。

---

## 4. 下一轮研究的执行规则

### 规则 1：一次只推进 1~2 个 P0
不要同时做 5 个新对象。

### 规则 2：优先补空缺层级
如果当前方向层很多、风险层很少，就优先补风险层。

### 规则 3：先做可解释，再做复杂
优先：EMA / breakout / pullback / volatility / ATR sizing
晚于：复杂背离 / 复杂组合 / ML

### 规则 4：不围绕弱 baseline 炼丹
当前重点不是把现有 baseline 参数继续抠细，而是建立更好的候选池和研究队列。

---

## 5. 现在就可以执行的下一步

### 方案 A（最推荐）
- 补 `ATR position sizing` 因子卡
- 做固定仓位 vs ATR 仓位缩放的单项对照实验

### 方案 B
- 补 `Pullback recovery confirmation` 因子卡
- 把它重新放回“方向过滤 + 触发 + 确认增强”的框架下重述

### 方案 C
- 补 `Volatility regime filter` 因子卡
- 从附属过滤器升级为正式候选对象

---

## 6. 维护方式

每完成一轮研究后，必须回写本文件：
- 状态是否变化（`SCOPED -> PROTOTYPED -> REVIEWED -> KEEP/DROP`）
- 当前判断是否变化
- 是否进入下一轮组合实验

如果一个对象已经有明确结论但当前不在主线，就标记为 `PARKED`，不要让 backlog 无限膨胀。
