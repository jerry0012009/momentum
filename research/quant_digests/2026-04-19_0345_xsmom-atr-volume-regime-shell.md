# 别把这份 cross-sectional momentum repo 只读成“多空排名作业”：对 short-cycle crypto desk，更该先拆的是「relative-momentum top2/bottom2 × ATR+volume confirmation × regime-scaled long-short basket」这条完整 raw alpha 壳
- 时间：2026-04-19 03:45 UTC
- 类型：GitHub repo
- 主题类型：raw alpha
- 基础 alpha：横截面 relative momentum（做多同一时点最强币、做空最弱币）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / momentum / long-short / relative-value / ATR / volume / regime / 15m / 5m
- 证据类型：工程经验

## 1. 这次看了什么
看的是 GitHub 仓库 `codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency`。它原版是 Binance 7 币 `1h` 横截面动量多空：每小时按 relative momentum 排名，做多 top2、做空 bottom2，再叠加 ATR 扩张、放量确认、daily regime score 和简单退出规则。

## 2. 核心结论
- **一句话核心结论**：这份 repo 真正值钱的不是“横截面动量”四个字本身，而是它把 **entry / exit / sizing / regime** 全链条都写出来了，能直接当 short-cycle 复现实验母板。
- **一句话证明方式**：证据主要来自源码规则和我基于 Binance USDⓈ-M 公开数据做的轻量 portability probe，而不是学术统计检验。
- 最像 base alpha 的部分仍然是 **同一时点强者续强、弱者续弱**；ATR 与 volume 更像确认层，regime score 更像 gross exposure 分配层。
- 我把它按相同骨架下压到最近公开数据：`15m` 上做 7 币 basket，粗略按 `4 bps` 单边换手成本估算后，近 `6000` 根 bar 仍从 **+131.6% gross** 降到 **+31.4% net**；但 `5m` 版本近 `5000` 根 bar 从 **+2.7% gross** 直接掉到 **-37.7% net**，说明它更像 `15m` 候选，不像可直接上 `5m` 的 alpha。
- 15m 版本样本内平均换手约 **23.6%/bar**，5m 约 **25.0%/bar**；问题不在“有没有信号”，而在 **5m 成本根本扛不住**。

## 3. 为什么和当前项目有关
这很贴当前 desk：它不是纯 filter，也不是空泛“多因子故事”，而是一条能直接扩充 raw alpha 素材池的 **cross-sectional / relative-value 完整策略壳**。当前 backlog 里趋势、突破、单资产反转已经很多，这个题材能补一条更像“篮子路由”的横截面主线。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / long-short
- 基础 alpha：最近若干 bar 的 relative momentum 排名，买最强、卖最弱
- regime：全市场 regime score（原版是 7 币中站上 20 日均线的占比）
- filter / veto：`ATR > ATR_baseline` + `volume_ratio > 1`
- risk / sizing / execution overlay：regime-scaled gross exposure、top2/bottom2 归一化权重、信号失效/短窗动量恶化退出、成本必须单独加

## 4. 可复刻的最小实验
- 研究假设：`15m` 横截面 relative momentum 在 liquid majors 上还有 pocket，但 `5m` 会被 turnover 和手续费吃掉。
- 可计算定义：每根 bar 用过去 `16 x 15m`（或 `48 x 5m`）收益做横截面排名；long top2 / short bottom2；只在 `ATR(14) > ATR_baseline(20)` 且 `volume / vol_mean20 > 1` 时入场。
- 最小回测切口：Binance USDⓈ-M `BTC/ETH/SOL/BNB/AVAX/LINK/DOGE`，先跑最近 `60d@15m` 与 `20d@5m`；手续费先从 `4 bps` 单边开始，再做 friction ladder（`2/4/6/8 bps`）。
- 最该先看：**post-cost return / Sharpe**，以及 **avg turnover per bar**。如果 15m 只有 gross 好看、net 很快塌掉，就别继续深挖。
- 下一步怎么测：先把 regime 从“日线 MA 占比”改成更贴短周期的 **1h breadth gate**，再做两组 A/B——`纯排名` vs `排名+ATR+volume`，确认真正提供增益的是 base alpha 还是过滤层。

## 5. 风险与保留意见
- 这是 repo 证据，不是论文证据；原作者结果未扣成本，回测表现明显可能偏乐观。
- 我这次 portability probe 只做了轻量近端样本，且用公开 K 线近似 open-to-open 执行，没有盘口冲击与资金费率。
- 该策略天然依赖固定 universe；一旦扩到更多山寨币，pair admission、流动性门槛和借贷/做空约束都会改变结果。
- 现阶段更像 **15m cross-sectional raw alpha shell**，不是 `5m` ready-to-trade 版本。

## 6. 来源
- codein123-afk. (2026). *Cross_Sectonal_Momentum_Cryptocurrency*. GitHub repository.
- Repo URL: `https://github.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency`
- README: `https://raw.githubusercontent.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency/main/README.md`
- Core script: `https://raw.githubusercontent.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency/main/step_1.py`
