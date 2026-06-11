# 别把 pairs 只做单对 z-score：这篇因子模型论文更值钱的是“多对冲篮子 + stationary-F2 gate”的 stat-arb 骨架
- 时间：2026-03-23 22:31 UTC
- 类型：论文 + 工程仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：cross-sectional / relative-value stat-arb（用公共因子拆出共同趋势后，交易相对价差的均值回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但需先过短周期成本与换手生存线）
- 主题标签：raw-alpha/stat-arb/pairs/relative-value/dynamic-factor/stationary-gate/regime/cost/turnover/crypto/5m/15m
- 证据类型：论文证据 + 工程实现启发 + 本地快检

## 1) 这次看了什么
先回答 base alpha：**不是“预测单币方向”，而是“剥离共同趋势后做相对价差回归”**。主材料是 Figá‑Talamanca, Focardi, Patacca (2021) 的动态因子 + 多 pair 市场中性框架；工程侧补了一份可快速改成 crypto 的开源 stat-arb 引擎（OLS / Rolling / Kalman 三路对照）。

## 2) 核心结论
- **一句话核心结论：** 对我们 desk，更值得抄的不是“某一对 coin 的 z-score 阈值”，而是**先做 common-trend 拆分，再只在 `F2` 仍稳定时开多空篮子**。  
- **一句话证明方式：** 论文先做 cointegration + 动态因子估计，再把交易收益映射到第二因子（stationary 因子）并给出含交易费后的累计表现；我补了 15m 最小快检验证可迁移边界。

3 个关键数据点（论文 + 本地）：
1. 论文在 BTC/ETH/LTC/XMR（日频，2016–2019）中识别到两因子结构：`λ1≈0.9962`（接近单位根）与 `λ2≈0.9823`（更偏平稳）。  
2. 论文报告在其样本期内，含交易费后策略净累计收益仍为正（文中 Table 6，`c=0.2` 时 net 统计优于 `c=0` 的高换手版本）。  
3. 我用 Binance 15m（BTC/ETH/LTC/XRP，近 3000 bars）做“逐 bar 重平衡”的 toy 迁移，结果 **gross 仅 +0.08 bps/bar、net -15.92 bps/bar**（按 16 bps round-trip 口径）——说明短周期里先被成本打穿，不能直接照搬。

## 3) 为什么和当前 desk 直接相关
这条线属于可独立复现的 raw alpha（relative-value / stat-arb），不是继续给 breakout/retest 做附件过滤。并且它天然能拆成完整策略组件：
- entry：由因子分解后的相对价差偏离触发；
- exit：价差回归、超时退出、或 regime 失效退出；
- sizing：按 beta/因子暴露做 market-neutral 配比；
- risk：`stationary-F2 gate` + 结构失效停机；
- cost：显式交易费/滑点/资金费率口径。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / market-neutral / mean-reversion
- 基础 alpha：多币共同趋势可被因子吸收，剩余相对价差存在回归段
- regime：仅在第二因子仍可视为平稳（或足够远离单位根）时交易
- filter / veto：`|λ2-1|` 过小、结构突变、成本超阈值时 veto
- risk / sizing / execution overlay：beta-neutral 权重、换手上限、成交成本闸门、分批执行

## 4) 可复刻最小实验（5m/15m 起步）
- 数据源：Binance Spot Klines（公开可得）
- 公开性：公开 REST，无私钥
- 更新频率：1m/3m/5m/15m 都可直接拉取
- 最小口径：`BTC/ETH/LTC/XRP`，滚动窗 `L=960`（15m 约 10 天）估计两因子；仅当 `λ2 < 0.995` 且成交成本假设可覆盖时开仓
- 首看指标：
  1) gross/net bps per traded bar；
  2) turnover（每 bar 换手腿数）；
  3) `λ2` 分布与收益条件分布（检验 stationary gate 是否真有信息）

## 5) 下一步怎么测（直接可执行）
1. **先做门控再做 alpha**：把 `stationary-F2 gate` 从单阈值升级为分桶（`λ2<0.98 / 0.98~0.995 / >=0.995`），比较每桶净收益。  
2. **降换手版本优先**：从“逐 bar 重平衡”改为“信号翻转才调仓 + 最大持有 bars”，先测试成本生存线。  
3. **5m→3m 下钻只对通过 15m 的币篮子**：先过 15m net>0 的币篮子再下钻，不做全池盲扫。  
4. **补全实盘口径成本**：手续费、滑点、maker/taker 混合、资金费率（若迁移到 perp）四档敏感性。

## 6) 风险与保留意见
- 论文主证据是日频与 2016–2019 环境，直接外推到 2026 高频会失真。  
- PCA 近似的 toy 迁移会天然压低因子相关性，不等价于论文完整估计流程。  
- 若不控制换手，short-cycle stat-arb 很容易“毛利为正、净利为负”。

## 7) 来源
1. **Figá‑Talamanca, G., Focardi, S., & Patacca, M. (2021). _Common dynamic factors for cryptocurrencies and multiple pair-trading statistical arbitrages_. Decisions in Economics and Finance.**  
   - DOI: `10.1007/s10203-021-00318-x`  
   - Readable URL: https://doi.org/10.1007/s10203-021-00318-x
2. **Sung, E. (2026). _statistical-arbitrage-engine_ (GitHub repository).**  
   - Repo URL: https://github.com/eddiesung111/statistical-arbitrage-engine
3. **Binance Spot API Docs (Klines).**  
   - Readable URL: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data

## 8) 本地产物
- `reports/artifacts/quant_digests/dynamic_factor_multispread_probe_20260323/bar_results.csv`
- `reports/artifacts/quant_digests/dynamic_factor_multispread_probe_20260323/summary.json`
