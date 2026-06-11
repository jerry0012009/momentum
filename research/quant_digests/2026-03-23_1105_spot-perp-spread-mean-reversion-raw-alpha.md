# 别把 funding / basis 继续只写成 overlay：这份 2025 新 repo 更适合先复现的是 spot-perp spread mean reversion 这条 raw alpha
- 时间：2026-03-23 11:05 UTC
- 类型：2025 GitHub 仓库 + perp 定价论文 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：spot-perp relative-value / spread mean reversion（资金费与基差约束下的同资产价差回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/spot-perp/spread-mean-reversion/funding/basis/carry/binance/repo/paper/crypto/1m/5m/15m
- 证据类型：工程证据 + 论文证据 + 本地快检（可复现）

## 1. 这次看了什么
这次主看 **dvirnyak (2025)** 的开源仓库 *arbitrage_research*，重点不是三角套利或 LSTM 花活，而是更适合我们 desk 先落地的 **spot-perp spread mean reversion**。先把 base alpha 说清楚：**同一标的的现货与永续价差会被 funding / arbitrage 机制往回拽，所以可以做 delta-neutral 的“价差回归”，而不是继续把 basis 只当 breakout 的 veto。**

## 2. 核心结论
- **一句话核心结论：** 对当前 desk，更值钱的新素材不是“再找一个方向过滤器”，而是把 **spot-perp spread 回归** 升级成独立 raw alpha 家族。
- **一句话证明方式：** repo 直接把 crypto spot-vs-perp 和股票 stat-arb 放一起比，结论是 crypto 这条线更稳定；我又用 Binance 公共 `5m` 数据做了快检，极端 z-score 后下一根出现回归的概率在主流币上相当高。
- 仓库最值得复用的不是 LSTM 本身，而是更底层的 3 个骨架：**同资产配对**、**spread 度量**、**delta-neutral 执行**。模型最多是二阶段增强层，不该一上来喧宾夺主。
- 本地快检（近 `928` 根 `5m`，BTC/ETH/SOL）里，`z_t` 与下一根 spread 变化的相关系数约 **-0.52 ~ -0.54**；说明 spread 越偏，下一根越倾向往回走。
- 当 `z > 1.5` 时，下一根 spread 压缩概率：`BTC 85.2% / ETH 90.9% / SOL 89.2%`；当 `z < -1.5` 时，下一根向上回归概率：`BTC 83.1% / ETH 89.0% / SOL 80.5%`。
- 一个很粗的无成本 `5m` banded toy strategy（`entry=|z|>1.5`，`flat=|z|<0.25`）在样本内录得 gross 累计约 **+125bps / +125bps / +147bps**；这不代表可实盘，但至少说明 raw alpha 本体值得进 first-verdict，而不是只停在 overlay 层。

## 3. 为什么和当前项目直接相关
- 它补的是我们当前明显缺口：**relative value / stat-arb / carry-basis** 这一整支 raw alpha，而不是继续围着 breakout / retest 做旁支过滤器。
- 它天生就是一条 **完整策略骨架**：entry、exit、配对仓位、杠杆上限、成本项、风险缓冲都能单独定义。
- 对 `1m/3m/5m/15m` 也友好：不是要求全天方向判断，而是盯 **spread 偏离 → 回归** 这件更局部、更短持有的事；非常适合先做 `5m` 验证，再下钻 `1m/3m`。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / delta-neutral mean reversion
- 基础 alpha：`spread_t = (perp_t - spot_t) / spot_t` 偏离 rolling fair value 后向均值回归
- regime：仅在 funding 机制正常、盘口/成交额充足、现货与永续同步可交易时开机
- filter / veto：极端事件时段、借币不可得、基差异常但盘口太薄、跨市场时间戳不同步、费用/资金费不够覆盖
- risk / sizing / execution overlay：dollar-neutral 或 beta-neutral 配比、保证金缓冲、持仓时限、费用/滑点/资金费显式入账、必要时只做单边最强偏离币

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** 在主流币上，spot-perp spread 的极端偏离不是纯噪音，至少在 `5m` 有可交易的短周期回归；若成本后还能活，再往 `1m/3m` 下钻。
- **最小定义：**
  - 标的：`BTC/ETH/SOL` 现货 vs Binance USDT perp
  - spread：`(perp - spot) / spot`
  - 标准化：`72` 根 `5m` rolling z-score（约 6 小时）
  - 入场：`z > 1.5` 做 `long spot + short perp`；`z < -1.5` 反向
  - 出场：`|z| < 0.25` 或 `max_hold = 12` bars
- **最小回测切口：** 先跑最近 `60~90` 天 `5m`，再加双边手续费、滑点、资金费；若仍有正期望，再看 `1m/3m` 是否只是把毛利换成噪音。
- **先看 4 个指标：** `post_cost_expectancy`、`holding_time`、`reversion hit ratio`、`capital_tied_up / margin_usage`。

## 5. 风险与保留意见
- 这条 alpha 最容易被 **手续费、借币/现货腿摩擦、保证金占用** 吃掉；gross 有边，不等于 net 有边。
- funding/basis 机制会“拉回价格”，但并不保证每次都按我们想要的速度回归；持仓时限和风险缓冲必须单独建。
- repo 里还有 LSTM，但当前优先级应是：**先验证 raw spread 本体，再讨论预测器是否有增益**。
- 本地快检只有最近一小段样本，且未扣真实成本；它只能证明“值得进 first verdict”，不能证明“已经 ready for paper/live”。

## 6. 来源
1. **dvirnyak. (2025). _arbitrage_research_. GitHub repository.**
   - Repo URL: https://github.com/dvirnyak/arbitrage_research
   - Readable URL: https://github.com/dvirnyak/arbitrage_research
2. **He, S., Manela, A., Ross, O., & von Wachter, V. (2022/2024). _Fundamentals of Perpetual Futures_. SSRN / arXiv.**
   - DOI: `10.2139/ssrn.4301150`
   - Readable URL: https://arxiv.org/abs/2212.06888
3. **Binance Open Platform. Funding / Mark Price endpoints.**
   - Funding History: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History
   - Mark Price: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price

## 7. 本地复现产物
- `reports/artifacts/quant_digests/spot_perp_spread_mr_20260323/summary_5m.csv`
- `reports/artifacts/quant_digests/spot_perp_spread_mr_20260323/threshold_reversion_5m.csv`
- `reports/artifacts/quant_digests/spot_perp_spread_mr_20260323/BTCUSDT_spot_5m.csv`
- `reports/artifacts/quant_digests/spot_perp_spread_mr_20260323/BTCUSDT_perp_5m.csv`
- `reports/artifacts/quant_digests/spot_perp_spread_mr_20260323/ETHUSDT_spot_5m.csv`
- `reports/artifacts/quant_digests/spot_perp_spread_mr_20260323/ETHUSDT_perp_5m.csv`
- `reports/artifacts/quant_digests/spot_perp_spread_mr_20260323/SOLUSDT_spot_5m.csv`
- `reports/artifacts/quant_digests/spot_perp_spread_mr_20260323/SOLUSDT_perp_5m.csv`
