# 别把这份 MEXC pump bot 只读成“追涨提醒器”：对 short-cycle crypto desk，更该先测的是「短窗 price burst × volume burst」这条 cross-sectional raw alpha
- 时间：2026-04-18 11:40 UTC
- 类型：GitHub repo source audit + Binance Spot `1m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：`短窗价格急拉且成交量同步放大的币，在接下来几个 1m bar 里更容易继续漂移`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / event-driven / momentum / pump / attention / volume-burst / Binance / MEXC / 1m / 3m / 5m / repo / public-data / cost / risk
- 证据类型：repo audit + public-data probe

## 1. 这次看了什么
这轮看的是 GitHub 仓 `bpawnzZ/MEXC-Pump-Bot`（2025）。源码几乎都在 `pumpBot.py`：它每 `10s` 拉一次 MEXC swap ticker，盯的是三个很朴素的东西——**相对价格变化、总价格变化、成交量变化**，然后把当前最像“正在被点火”的币打出来。

它没有回测器，也没有完整下单壳，但 base alpha 很清楚：**短窗 attention burst 会不会带来后续几根 bar 的 continuation**。这不是 filter，也不是 overlay，而是一条能单独成立的 raw alpha 假设。

## 2. 核心结论
- **一句话核心结论**：repo 值钱的不是“抓 pump”这层话术，而是它给了一个很容易映射到 `1m/3m/5m` 的 raw alpha 骨架：`price burst + volume burst -> next few bars drift?`
- **一句话证明方式**：我直接审了 `pumpBot.py` 的事件筛选逻辑，再把它移植成 Binance Spot `1m` 的 cross-sectional top-burst 实验，检查 next `1/3/5/10m` 的 forward return。
- repo 里的事件定义很粗，但很诚实：上一拍到这一拍，若价格变化和成交量变化都明显抬升，就把这枚币记成“异动”。
- 我用 Binance Spot `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK` 近 `14d` 的 `1m` 公共数据做 portability probe，映射规则为：`ret1>0`、`ret1_z>1`、`quote_volume_z>1`、`vol_ratio>1.2`，然后每分钟只选 score=`ret1_z+quote_volume_z` 最高的那一枚。
- 结果并不支持“看到短窗拉升就追”的裸 continuation：全样本 `2231` 笔，next `1/3/5m` gross 约 **`-0.16 / -0.58 / -0.65 bps`**；即便拉到最强 `q75` 子样本（`558` 笔），next `1/3/5m` 也只有 **`-0.09 / -1.68 / -0.64 bps`**。
- 更细看会发现：它也不是纯粹瞬时反转。两档样本到 next `10m` 才略转正，gross 约 **`+0.36 bps`**（全样本）和 **`+0.94 bps`**（`q75`），但离可交易还差得远；若粗扣 `8bps`，仍明显为负。
- 所以这轮 first verdict 很直接：**“分钟级异动榜首继续冲” 这条裸 raw alpha 在当前主流现货大币上不厚**；比直接追涨更有价值的，反而是把它改写成 **router / veto / delayed-follow-through filter**。

## 3. 为什么和当前项目有关
它和 `momentum` 的关系不在于“又多了一个涨幅榜工具”，而在于它补了一块我们研究池还不算多的方向：**极短 attention / flow shock 的横截面事件信号**。这类线索天然适合 `1m/3m/5m`，而且未来可继续接到：
- 新币/小币的异常成交量监控
- 上所、公告、社媒热度后的 cross-sectional router
- breakout / news / liquidation 之后的“要不要追第二脚” veto

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 事件驱动 / 顺势候选
- 基础 alpha：`短窗 price burst × volume burst 会带来 follow-through`
- regime：小币、低流动性币、外部催化更明确的时段可能更强；大币常更快被均值回复和做市吸收
- filter / veto：只保留高分位 burst、只做公告/上所/链上催化后的事件、避开 funding/盘口明显反向挤压的时刻
- risk / sizing / execution overlay：固定 time stop、只做 top1/topN、按 burst score 或成交额容量分级、对过宽点差和过低深度直接 veto

## 4. 可复刻的最小实验
- 研究假设：若某币在本分钟同时出现显著价格抬升和成交量抬升，则 next `1/3/5/10m` 存在 continuation pocket。
- 可计算定义：
  - `ret1 = close/close[-1]-1`
  - `ret1_z`：`60m` 滚动 z-score
  - `quote_volume_z`：`60m` 滚动 z-score
  - `vol_ratio = quote_volume / quote_volume[-1]`
  - 事件：`ret1>0 & ret1_z>1 & quote_volume_z>1 & vol_ratio>1.2`
  - 每分钟只取 score=`ret1_z+quote_volume_z` 最高的那一枚
- 最小回测切口：Binance Spot `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`，`1m`，近 `14d`。
- 最该先看：`next 1/3/5m gross bps` 和 `win rate`；第二步再看事件分层后的 `next 10m`。
- **下一步怎么测**：不要继续在大币上裸追榜首。先把样本切成两层：`(a) 事件后 1m 不追、改在第 2 根 pullback/hold above VWAP 再进`，`(b) 只保留 burst 后 order-book / trade-count 继续扩张的样本`，再比较 next `3/5/10m` 是否从当前负值翻正。

## 5. 风险与保留意见
- 这份 repo 没有真正的回测层，更多是实时扫描器；因此它给的是信号胚子，不是完整策略。
- 我这轮 probe 用的是 Binance 大币现货代理，不是 MEXC swap 原场景；这有助于做 portability 判断，但不代表小币 pump 生态下结果相同。
- attention burst 很容易和做市回补、价差扩张、假突破混在一起，所以“看到异动就追”通常会先死在 execution 与 slippage。
- 因而这轮我仍把它记为 **raw alpha 候选**，但更像**事件路由层 / 二次确认层的母板**，不是现成 production shell。

## 6. 数据源与公开性
- repo：GitHub 公开仓，源码主要在 `pumpBot.py`。
- 价格数据：Binance `data.binance.vision` Spot `1m` daily klines，公开可得。
- 更新频率：repo 原始场景约 `10s` ticker；本轮 portability probe 用 `1m` bar。
- 最小可复现实验口径：按分钟生成 cross-sectional burst score，取 top1，统计 next `1/3/5/10m` 收益。

## 7. 来源
- bpawnzZ. (2025). *MEXC-Pump-Bot*. GitHub.
- Repo URL: `https://github.com/bpawnzZ/MEXC-Pump-Bot`
- Readable files: `README.md`, `pumpBot.py`
- Public market data: `https://data.binance.vision/data/spot/daily/klines/`
- Local artifacts:
  - `reports/artifacts/quant_digests/2026-04-18_mexc_pump_crosssection_events.csv`
  - `reports/artifacts/quant_digests/2026-04-18_mexc_pump_crosssection_events_q75.csv`
  - `reports/artifacts/quant_digests/2026-04-18_mexc_pump_crosssection_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-18_mexc_pump_crosssection_summary.json`
