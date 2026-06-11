# 别把“机器学习”当黑箱：这篇近 5 年材料里更值钱的是 `lagged technical regression` 可独立复现 raw alpha 骨架
- 时间：2026-03-23 16:50 UTC
- 类型：近 5 年论文/项目报告 + 开源复现仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：用滞后技术特征（短窗动量/波动/时段）预测下一小段收益方向与强度，并做阈值化多空交易
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/lagged-regression/technical-features/intraday/cost/turnover/execution/repo/paper/crypto/1m/3m/5m/15m
- 证据类型：论文/项目证据 + 工程复现证据 + 本地最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“滞后技术特征 -> 下一段收益预测”本体**，不是 filter/overlay。

这次主看 **Brown, Ling, Sawhney (2021)** 的项目论文 *Cryptocurrency Alpha Models via Intraday Technical Trading*，并补看其被引用的开源复现仓库（Cornell Quant Fund, 2022）。我关心的不是“哪种模型最强”这句 headline，而是它提供了一条对 desk 很实用的 **可落地策略骨架**：
- 用价格/波动/时间特征做可解释预测（不是纯黑箱）
- 用阈值把“弱预测”过滤掉，控制交易频率
- 把 `entry/exit/sizing/risk/cost` 一起写成可回测单元

## 2. 核心结论
- **一句话核心结论：** 这条 raw alpha 在短周期上“有毛边”，但成本极敏感；要活下来，核心不在换更复杂模型，而在“阈值降频 + 执行降成本 + 参与率约束”。
- **一句话证明方式：** 论文用同一数据口径对比 pairs 与多种模型，并把 lagged linear regression 落成可交易回测；我再用 Binance 15m 公共数据做最小快检验证“毛利存在但净值易被成本吃掉”。

关键数据点（1~3 条）：
1. 论文报告中，**lagged linear regression Sharpe = 3.34**（优于 RNN LSTM 2.64、XGBoost 1.54、pairs 1.30）。
2. 同文对 pairs 的 OOS 表现提示明显衰减（文中示例测试 Sharpe 约 **0.11**，且收益较薄）。
3. 本地 15m 快检（BTCUSDT, 约 4500 根, 1-bar horizon, 6 bps/side）：**gross +0.41 bps/bar，但 net -1.14 bps/bar**，说明信号边际不足以直接覆盖交易成本。

## 3. 为什么和当前项目直接相关
- 这是 **raw alpha 素材池补充**（不是 breakout/retest 的派生过滤器）。
- 它天然可拆成完整策略：
  - entry：预测值超过上阈值做多，低于下阈值做空
  - exit：下一持有窗平仓或反向信号切换
  - sizing：固定名义仓位/波动目标仓位
  - risk：止损、最大回撤、最大持仓时间、参与率上限
  - cost：手续费 + 滑点 + 换手冲击
- 可直接映射到 `1m/3m/5m/15m`：把“小时级窗口”按 bar 数等比例压缩即可做最小实验。

## 3.5 策略拆解（必填）
- 方向属性：短周期趋势/动量（预测驱动）
- 基础 alpha：`E[r_{t+1}|X_t]`，其中 `X_t` 为滞后技术特征（MA/vol/momentum/time-of-day）
- regime：高波动/高噪声期需抬高阈值，低流动时降杠杆或停机
- filter / veto：预测强度不足（中间分位）、成交成本超预算、盘口深度不足时不交易
- risk / sizing / execution overlay：固定风险预算、参与率上限、maker 优先、分批成交、换手约束

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** 预测型 raw alpha 在 15m 有可测毛利，但只有在“低换手 + 低成本 + 强信号阈值”下，净值才可能转正。
- **最小定义：**
  - 数据：Binance USDT perp 公共 klines（公开可得，更新频率高）
  - 标的：先 `BTC/ETH/SOL`，再扩到 8~20 个高流动币
  - 周期：`15m` 起步，再下钻 `5m/3m/1m`
  - 特征：`MA(5/10/20/50/100)`、`vol(10/20/50)`、`mom(5/10/20)`、时段特征
  - 标签：`next k-bar return`（先 k=1,2,4）
  - 交易：上/下分位阈值（如 0.7/0.3）触发多空；中间分位空仓
- **先看 4 个指标：** `post-cost bps/bar`、`turnover/day`、`hit ratio by prediction decile`、`capacity@participation cap`。
- **下钻顺序：** 先在 15m 找净值存活 pocket，再搬到 5m/3m；若 15m 无法成本后转正，不进入 1m。

## 5. 风险与保留意见
- 论文属于项目/工作论文口径，非严格期刊实盘评估；需谨慎外推。
- 原文结果高度依赖样本区间与交易所微观结构；跨交易所迁移会掉效。
- 预测型策略最常见失效点是：信号薄、换手高、交易成本和冲击被低估。

## 6. 来源
1. **Brown, A., Ling, J., & Sawhney, A. (2021). _Cryptocurrency Alpha Models via Intraday Technical Trading_. Project paper / preprint (Stanford-affiliated).**
   - Authors / Year / Title / Venue: Amanda Brown, Jonathan Ling, Arjun Sawhney / 2021 / Cryptocurrency Alpha Models via Intraday Technical Trading / Project Paper (Preprint)
   - DOI: N/A
   - Readable URL: https://jonathan-ling.github.io/artefacts/2021.06%20Intraday%20technical%20trading%20for%20cryptocurrencies%20-%20paper.pdf
   - Repo URL: N/A
2. **Cornell Quant Fund. (2022). _BlockchainSP2022_ (replication-style notebook repo referencing the above paper). GitHub Repository.**
   - Authors / Year / Title / Venue: Cornell Quant Fund / 2022 / BlockchainSP2022 / GitHub Repository
   - DOI: N/A
   - Readable URL: https://github.com/Cornell-Quant-Fund/BlockchainSP2022
   - Repo URL: https://github.com/Cornell-Quant-Fund/BlockchainSP2022

## 7. 本地复现产物
- `reports/artifacts/quant_digests/lagged_regression_intraday_20260323/summary.csv`
- `reports/artifacts/quant_digests/lagged_regression_intraday_20260323/test_signals.csv`
- `reports/artifacts/quant_digests/lagged_regression_intraday_20260323/meta.txt`
