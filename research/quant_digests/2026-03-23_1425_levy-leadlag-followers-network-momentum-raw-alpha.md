# 别把“谁先动谁后动”只当解释：这份 2026 新仓库更适合先复现的是 Lévy lead-lag followers continuation 这条 raw alpha
- 时间：2026-03-23 14:25 UTC
- 类型：2026 GitHub 新仓库 + 方法论文 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：跨币种 lead-lag（领导币先动）驱动的 followers 同向跟随（continuation）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/stat-arb/lead-lag/network-momentum/levy-area/hermitian/crypto/5m/15m
- 证据类型：工程证据 + 论文方法证据 + 本地最小快检（可复现）

## 1. 这次看了什么
先回答 base alpha：**这次的基础 alpha 不是 filter，也不是风控 overlay，而是“leaders 先动后，followers 在短窗口内同向延续”的可交易信号本体。**

主看 2026 新仓库 **mateofrqt/Crypto-LeadLag-Strategy**（Lévy area + Hermitian clustering + live bot 骨架），并用其引用的方法论文做地基（Bennett et al., 2022；Li & Ferreira, 2025）。和我们最近几篇更偏 residual MR / funding carry 不同，这条更像 **cross-sectional network momentum**：先识别“谁是领涨/领跌组”，再交易“跟随组的短窗延续”。

## 2. 核心结论
- **一句话核心结论：** 这条线值得进 raw alpha 池，且在我们本地 `15m/5m` 的最小快检里，followers continuation 在短持有窗有正毛边，不是纯概念。  
- **一句话证明方式：** 用公开 Binance perp K 线做 rolling Lévy lead-lag 打分，按 leaders 当根收益决定方向，再交易 followers 篮子，直接统计每笔 bps 与命中率。  
- 本地 `15m` 快检（10 币，rolling window=30 bars，leaders/followers 各 2 币，1461 笔）结果：
  - `H=1`：gross **+19.21 bps/笔**，hit **82.2%**
  - `H=4`：gross **+15.33 bps/笔**，hit **62.9%**
  - `H=8`：gross **+16.49 bps/笔**，hit **57.8%**
- 本地 `5m` 映射（1457 笔）结果：
  - `H=1/3/6`：gross 分别 **+9.76 / +9.40 / +9.44 bps/笔**；若粗扣 `8 bps`，仍有约 **+1.76 / +1.40 / +1.44 bps**
  - `H=12`：gross **+6.26 bps**，扣 `8 bps` 转负，提示持有过长可能被摩擦吞噬。
- 在 `15m-H4` 下按 leader impulse 绝对值分三档：
  - low 档 gross **-1.17 bps**
  - high 档 gross **+34.48 bps**（hit **73.3%**）
  说明这条 alpha 天然适合加一个 **impulse-strength gate**，不是全时段等权开机。

## 3. 为什么和当前项目直接相关
- 它直接扩充了当前最需要的 **raw alpha 素材池**（cross-sectional / relative-value / stat-arb 方向），不是继续在 breakout/retest 上内循环。  
- 能拆成完整策略组件：
  - entry：rolling Lévy 打分后选 leaders/followers，leaders 当根同向触发
  - exit：固定持有 `H` 或 followers 回撤条件
  - sizing：按 follower |score| 加权 + 组合杠杆上限
  - risk：事件黑窗、leader 冲击阈值、单币权重上限
  - cost：maker/taker、滑点、funding、换手上限
- 与 `1m/3m/5m/15m` 的关系清楚：`15m` 先做 first verdict，`5m/3m` 主要做“是否还能活过成本”的压力测试。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值（基于 lead-lag 排序的 network momentum）
- 基础 alpha：leaders 先动后，followers 在短窗口同向延续
- regime：跨币种共振不弱、leader 冲击中高、且非极端新闻跳空期更友好
- filter / veto：`|leader impulse|` 分层门；低冲击（low tercile）默认 veto
- risk / sizing / execution overlay：按 |score| 权重、单币上限、组合杠杆上限、参与率 cap、事件时段降杠杆

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** lead-lag continuation 的可交易性主要来自“冲击强时段”；弱冲击时段应减仓或不做。  
- **可计算定义：**  
  1) rolling 30-bar Lévy matrix；2) row-mean score 排 leaders/followers；3) leaders 当根均值收益定方向；4) 交易 followers 篮子。  
- **最小回测切口：** Binance USDT perp（公开 API），10~20 币，`15m` 主检 + `5m` 成本压力检。  
- **先看 4 个指标：** post-cost bps/笔、hit rate、turnover/day、capacity@participation cap。  
- **下一步最先做：** 在 `15m-H4` 上只保留 leader impulse 中/高两档，再做 cost ladder（4/8/12 bps）与币池裁剪（高流动 6~8 币）对照。

## 5. 风险与保留意见
- 这次快检是代理口径，不含完整订单簿冲击、资金费时点与撮合约束，结论只能算 first verdict。  
- 仓库本身很新（2026，stars 少），可贵在结构完整，不等于已被广泛验证。  
- lead-lag 在极端共振（全市场同涨同跌）时容易塌缩，需要事件黑窗与冲击阈值门控。  
- 若后续加上真实成本与执行约束后边际显著下降，应把它降级为“条件型 raw alpha”（只在 high-impulse regime 开机）。

## 6. 来源
1. **Fourquet, M. (2026). _Crypto-LeadLag-Strategy_. GitHub repository.**  
   - Repo URL: https://github.com/mateofrqt/Crypto-LeadLag-Strategy  
   - Readable URL: https://github.com/mateofrqt/Crypto-LeadLag-Strategy
2. **Bennett, S., Cucuringu, M., & Reinert, G. (2022). _Lead-lag detection and network clustering for multivariate time series with an application to the US equity market_. arXiv (stat.ML / q-fin.ST).**  
   - DOI: `10.48550/arXiv.2201.08283`  
   - Readable URL: https://arxiv.org/abs/2201.08283
3. **Li, L., & Ferreira, W. (2025). _Follow the Leader: Enhancing Systematic Trend-Following Using Network Momentum_. arXiv (q-fin.TR).**  
   - DOI: `10.48550/arXiv.2501.07135`  
   - Readable URL: https://arxiv.org/abs/2501.07135
4. **ARahimiQuant (2023). _lead-lag-portfolios_. GitHub repository（方法实现参考）.**  
   - Repo URL: https://github.com/ARahimiQuant/lead-lag-portfolios

## 7. 本地复现产物
- `reports/artifacts/quant_digests/leadlag_network_momentum_20260323/summary_15m.csv`
- `reports/artifacts/quant_digests/leadlag_network_momentum_20260323/summary_5m.csv`
- `reports/artifacts/quant_digests/leadlag_network_momentum_20260323/trade_proxy_15m.csv`
- `reports/artifacts/quant_digests/leadlag_network_momentum_20260323/impulse_bucket_15m_H4.csv`
- `reports/artifacts/quant_digests/leadlag_network_momentum_20260323/direction_split_15m.csv`
- `reports/artifacts/quant_digests/leadlag_network_momentum_20260323/meta.json`
