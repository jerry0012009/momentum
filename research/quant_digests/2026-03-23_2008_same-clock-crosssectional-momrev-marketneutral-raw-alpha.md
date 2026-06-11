# 别把 intraday clock 只当 filter：这份仓库更适合先复现「同钟横截面短反转 + 长动量」market-neutral raw alpha
- 时间：2026-03-23 20:08 UTC
- 类型：GitHub 仓库（近 5 年）+ 论文线索
- 主题类型：raw alpha
- 基础 alpha：同一日内时钟槽位（same-clock）上的横截面收益排序效应：短窗反转 + 长窗动量
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/market-neutral/intraday/momentum/reversal/same-clock/session-effect/repo/crypto/1m/3m/5m/15m
- 证据类型：工程经验（仓库 notebook 可复现）+ 论文证据（方向一致）

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 不是过滤器，而是“同一时钟位置上的横截面可预测性”本体**。  
本轮主看仓库 **MateoPedro/StatArb (2023)** 的完整 notebook：把 10 个币（BTC/ETH/BNB/ADA/XRP/SOL/DOT/LTC/AVAX/MATIC）做 market-neutral 横截面排序，在不同 lookback 下拆出两条腿：
- 短窗（1–2 天）偏**反转**
- 长窗（9–21 天）偏**动量**
再做组合加权，形成可直接交易的完整策略骨架。

## 2. 核心结论
- **一句话结论：** 对 crypto 日内横截面而言，“短窗反转 + 长窗动量”可以在同一框架内并存，且可合成为可交易的 market-neutral raw alpha。
- **一句话证明方式：** 仓库在同一 notebook 里给出了信号构造、时段切分、成本处理、组合加权与回归检验（含 alpha t-stat）的完整链路。

可直接抄走的 3 个关键数据点（来自仓库 README/Notebook 输出）：
1. 组合策略年化 **Sharpe ≈ 2.03**，最大回撤 **≈ 8.66%**（README 报告口径）。
2. Notebook 输出的组合统计：年化收益 **16.70%**、年化波动 **8.21%**、Sharpe **2.0347**。
3. 对 BTC 基准回归中，alpha t-stat **≈ 2.0537**，信息比率 **≈ 1.9772**，显示并非简单 beta 暴露。

## 3. 为什么和当前 desk 直接相关
- 这是 **raw alpha 候选**，而不是又一层 veto/filter。
- 与我们当前 `1m/3m/5m/15m` 研发节奏兼容：
  - 把“小时槽位”改成“15m 槽位（96 格）/5m 槽位（288 格）”即可平移；
  - 信号只依赖公开 OHLCV，可快速最小复现。
- 它能补齐素材池的“**横截面 + 相对价值 + market-neutral**”方向，避免只在单资产 breakout/retest 体系内循环。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 市场中性
- 基础 alpha：same-clock 横截面排序效应（短窗反转 + 长窗动量）
- regime：工作日活跃时段更稳；低流动性时段信号衰减
- filter / veto：
  - 交易时段白名单（优先高流动性时段）
  - 成交额阈值与最小可成交深度阈值
- risk / sizing / execution overlay：
  - 每个时钟槽位做 rank-demean + L1 归一化（天然 dollar-neutral）
  - 组合层做 vol target + 单币权重上限
  - 成本显式计入双边手续费 + 滑点 + 资金费率（perp）

## 4. 可复刻的最小实验（面向 1m/3m/5m/15m）
**研究假设**：同一 clock slot 上，短窗横截面收益偏反转、长窗偏动量；两者混合优于单腿。

**可计算定义（15m 版）**：
1. Universe：Binance USDT-M perp，按近 30 天成交额选 Top30。
2. 对每个 slot `s∈{0..95}`，收集过去 `N` 天该 slot 的收益均值 `avg_ret_{i,s,N}`。
3. 横截面打分：`rank -> demean -> L1 normalize` 得到权重 `w_{i,s,N}`。
4. 短窗腿：`N=1..2` 取反转方向；长窗腿：`N=9..21` 取动量方向。
5. 组合：先腿内 Sharpe 权重，再腿间做 50/50 或 rolling Sharpe 权重；每个 slot 持有 1 bar。

**最小回测切口**：
- 周期：先 `15m`，再下钻 `5m`；`3m/1m` 仅做高成本压力测试。
- 样本：近 180 天，walk-forward（train 90d / test 30d）。
- 成本：阶梯 2/5/10 bps + 资金费率。

**先看 2 个指标**：
- 成本后 Sharpe（Net Sharpe）
- turnover 与容量（ADV participation）

## 5. 风险与保留意见
- 仓库样本币种较少、时间段有限，外推前需做更长样本与多交易所复核。
- same-clock 策略对时区、交易时段和流动性结构敏感，换市场后可能失真。
- 论文主线（Wen et al., 2022）与该思路一致，但本轮可读到的是 DOI 元数据与二手页面，后续仍应补全文复核细节。

## 6. 下一步怎么测（直接可执行）
1. **先跑 15m Top30**：验证“短反转 + 长动量”混合是否稳定优于单腿。  
2. **再跑 5m Top50**：检查 alpha 是否因噪声放大而退化，并画 `edge→cost` 衰减曲线。  
3. **加执行约束**：加入单币参与率上限（如 ADV 5%）与单时钟最大换手，确认可交易性。  
4. **组合对接**：与现有 carry / basis / residual MR 组合，优先看相关性下降后的组合 Sharpe 提升。

## 7. 来源
1. **MateoPedro. (2023). _StatArb: Market-Neutral Crypto Strategy_. GitHub repository.**  
   - Repo URL: https://github.com/MateoPedro/StatArb  
   - Notebook URL: https://raw.githubusercontent.com/MateoPedro/StatArb/main/Project%20.ipynb
2. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_. The North American Journal of Economics and Finance.**  
   - DOI: `10.1016/j.najef.2022.101733`  
   - Readable URL: https://doi.org/10.1016/j.najef.2022.101733
3. （同主题 working paper 线索）**Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). SSRN version.**  
   - DOI: `10.2139/ssrn.4080253`  
   - Readable URL: https://doi.org/10.2139/ssrn.4080253
