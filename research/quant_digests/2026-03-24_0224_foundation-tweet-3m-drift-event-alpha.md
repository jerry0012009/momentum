# 别把情绪分数当主角：foundation tweet 后 3 分钟漂移才是可交易事件 alpha（先做事件池，不做全网情绪）
- 时间：2026-03-24 02:24 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：官方/基金会账号发布“信息型推文”后，相关币种在 `t1~t3` 分钟存在可统计检验的正向漂移（event-driven momentum）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（需先加成本与成交约束）
- 主题标签：event-driven/momentum/twitter/x/foundation/1m/3m/5m/15m/execution/cost/crypto
- 证据类型：论文证据

## 1. 这次看了什么
读了一篇可直接转成短周期事件策略的论文：不做“全网情绪因子”，而是只盯官方账号推文，研究发布后 15 分钟内价格路径，并把条件直接落成可执行交易算法。

## 2. 核心结论（含关键数字）
- **base alpha 很明确**：推文后的最强反应在前 3 分钟，`t2` 最显著。表 2 给出均值：`t1=0.000080`、`t2=0.000146`、`t3=0.000077`（约 0.8/1.46/0.77 bps）。
- 统计上，`t1~t3` 相对后续窗口有显著差异，尤其 `t2` 对大量窗口比较达到 `p<0.0001`（配对双尾 t 检验）。
- 全样本平均累计收益峰值约 `0.04%`（t10），**低于文中 Binance 费率 0.075%**，说明“裸做全部事件”不可交易。
- 但条件化后出现可交易 pocket：
  - 技术/合作类词（如 announce/partnered/launches）15 分钟内最大累计收益约 `0.005`；
  - 交易所相关词（如 binance/bitfinex）最大累计收益约 `0.0043`；
  - 低发帖频率账号（历史发帖 <200）15 分钟最大累计收益 `0.0017`，明显高于高频账号组（>500，仅 `0.00045`）。
- 论文明确指出：**情绪极性本身不是主驱动**；更有信息的是“内容质量 + 词义 + 账号行为特征”。

## 3. 为什么和当前项目有关
我们当前在补短周期可复现 raw alpha 素材池，这篇属于可独立运行的一条：
- 不是 breakout/retest 的派生滤网，而是独立事件驱动 alpha；
- 天然贴合 `1m/3m/5m/15m`（事件后分钟级持有）；
- 可直接接入现有执行/成本框架（成交约束、滑点、超时退出）。

一句话核心结论：**推文本身不是 alpha，推文后的“前 3 分钟价格漂移 + 条件化事件筛选”才是 alpha。**

一句话证明方式：**作者用 1 分钟级价格 + 推文逐条对齐，做 15 分钟事件窗统计与条件分组检验（含 p-value 矩阵）。**

## 3.5 策略拆解（必填）
- 方向属性：事件驱动顺势（超短持有）
- 基础 alpha：`foundation tweet -> t1~t3 正向漂移`
- regime：仅在高流动性时段 + 盘口可成交时启用
- filter / veto：只留信息型推文（技术升级/上所/合作），剔除 retweet/quote 与低信息噪声文本
- risk / sizing / execution overlay：
  - 单笔风险上限 + 事件并发上限；
  - taker 费 + 半价差 + 冲击成本后才允许开仓；
  - 超时（3/5/15m）强平，防止事件衰减后回吐。

## 4. 可复刻的最小实验（1m/3m/5m/15m）
**研究假设**：在可交易成本口径下，信息型官方推文事件在 `1m~5m` 仍有正期望；`15m` 主要用于超时退出而非追求更大漂移。

**可计算定义**：
1. 事件源：币种官方 X/基金会账号（先做 BTC/ETH/SOL/BNB 及其生态币）。
2. 事件过滤：非 retweet/quote；文本命中信息词典（launch/listing/upgrade/partnership/mainnet 等）。
3. 入场：事件时间戳后首个可成交分钟（或 20~40 秒内）按 taker 执行。
4. 出场：`+3m` 主退出，`+5m` 备选；`+15m` 超时硬退出；并加 `-k*ATR(1m)` 保护止损。
5. 成本：手续费 + 半价差 + 冲击（按盘口深度/参与率分层）。

**最小回测切口**：
- 资产：10~20 个高流动币（优先 perp 或现货深度足够的主币+龙二）。
- 频率：1m bar（评估 1m/3m/5m/15m 持有窗）。
- 样本：最近 6~12 个月，按月滚动 OOS。

**先看 2 个指标**：
- 成本后 `event expectancy (bps/event)`；
- `hit rate @3m` 与 `MAE/MFE`（判断是快进快出还是需延长持有）。

## 5. 风险与保留意见
- 论文样本主要是 2018 年（alt/BTC 现货结构），对当前 perp 主导市场需重估。
- X/Twitter API 规则变化较大，实时抓取延迟和覆盖率会影响可交易性。
- 新闻扩散与“先知交易”可能让 alpha 向更短时延塌缩。
- 条件挖掘容易过拟合，必须做时间滚动 + 币种分层验证。

## 6. 来源
- Jeleskovic, V., & Mackay, S. (2023). *Intraday Trading Algorithm for Predicting Cryptocurrency Price Movements Using Twitter Big Data Analysis*. arXiv (q-fin.CP).
  - DOI: `10.48550/arXiv.2401.00603`
  - Readable URL: `https://arxiv.org/abs/2401.00603`
  - PDF URL: `https://arxiv.org/pdf/2401.00603.pdf`
  - Repo URL: 未公开（文中描述实现为 R + Twitter API + Binance API）
- Binance Spot API docs: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints`
- X API docs: `https://developer.x.com/en/docs/twitter-api`
