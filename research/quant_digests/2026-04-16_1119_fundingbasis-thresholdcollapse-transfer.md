# 别把这个 deep-learning funding 仓只读成“模型竞赛”：对 short-cycle desk，更该先拆的是「basis 失衡回归 × funding carry」以及“阈值塌缩”这条 admission 教训

- 时间：2026-04-16 11:19 UTC
- 类型：GitHub repo source audit + Binance public-data portability quick check
- 主题类型：raw alpha
- 基础 alpha：`short perp + long spot`，做 rich-basis 回归并叠加正 funding carry
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/relative-value/stat-arb/carry/funding/basis/delta-neutral/threshold-search/binance/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：工程证据 + 公共数据快检

## 1. 这次看了什么
这次审的是 `MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`（2026），重点看了 `configs/labels/default.yaml`、`src/funding_arb/models/baselines.py`、`src/funding_arb/features/builders.py`，以及仓库自带回测产物（`strategy_metrics.csv`、`combined_strategy_metrics.csv`、`baseline_metrics.csv`）。另外做了一个 Binance 公共数据快检（spot/perp `15m` + funding）。

## 2. 核心结论
- **一句话核心结论**：这条 alpha 的“方向”是对的（rich-basis 回归 + carry），但仓库默认阈值在 OOS test 上几乎塌成“无交易”，说明它目前更像可复刻的研究壳，而不是可直接上线策略。
- **一句话证明方式**：直接看 repo 自带 OOS 指标 + 用 Binance 公共 `15m` 数据做最小 portability 复算，结果都指向“gross 有小边际、成本后易被吃掉”。
- 仓库 `strategy_metrics.csv` 的 `test` split 中，多个规则（`logistic_*`、`elastic_net_regression`、`combined_funding_spread`）`trade_count=0`；只有 `spread_zscore_1p5` 有 200 笔，但 `cumulative_return=-0.0647`，`total_fees_usd=4000`，净值明显被摩擦打穿。
- `combined_strategy_metrics.csv`（combined 口径）里某些规则看起来是正收益（如 `logistic_l1` 仅 3 笔、`cumulative_return=0.003553`），但这更像样本混合口径下的“好看截图”，不等于 OOS 可交易稳定性。
- 我们的 Binance `15m` 快检（近约 31 天、`basis_z>1.5 & funding>0`）得到：信号约 91 次，价差回归均值约 `+1.57 bps`，单次 funding 约 `+0.24 bps`，合计 `gross ~ +1.81 bps`；若按约 `8 bps` 单边摩擦估算，净值仍显著为负。
- **最值得复用点**：不是它的“深度学习模型名”，而是它把 label、阈值搜索、成本项、回测流水线都写成了可替换组件，适合我们直接拿来做 `admission / veto / cost ladder` 的工程母板。

## 3. 为什么和当前项目有关
这条线仍然属于我们当前最优先补充的 `raw alpha` 池（relative-value / stat-arb / carry / funding / basis）。它的价值不在“现成可上”，而在于给了一个很清楚的研究事实：**base alpha 可以成立，但若 admission 与执行层没过成本线，结果会从“paper edge”直接塌成“0 交易或负净值”**。这对 `1m/3m/5m/15m` 研发是高价值反例。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 + 均值回归（价差逆势）
- 基础 alpha：`perp 相对 spot 过贵（basis 富）时，short perp / long spot，赚价差回归 + funding carry`
- regime：正 funding、basis 偏离显著、且流动性/冲击成本可控时
- filter / veto：`expected_edge_bps > fee+slippage buffer`、盘口深度阈值、stale quote veto、资金费率临近切换时段限流
- risk / sizing / execution overlay：delta-neutral notional cap、单腿滑点上限、最大持有时长（8h/24h）、异常波动 kill-switch、分层减仓而非一次性平仓

## 4. 可复刻的最小实验
- 研究假设：`basis_z` 极端 + 同向 funding 的组合，能在短周期执行层产生可扣成本的净回归收益。
- 可计算定义（先做最小版）：
  - 状态层（`1h`）：`basis_z_72h > 1.5` 且 `funding_bps > 0`
  - 执行层（`15m/5m/3m/1m`）：下根开盘执行 `short perp + long spot`，当 `basis_z < 0.3` 或持有到 `8h` 强平
- 最小回测切口：Binance `BTCUSDT`，先跑最近 120 天，再扩到 365 天；`15m` 先做基线，再下钻到 `5m/3m/1m` 看执行改进空间。
- 最先看 2 个指标：
  1) `post-cost avg pnl bps / trade`（必须 > 0）
  2) `trade_count × capacity`（防止“只剩几笔好看交易”）

## 5. 风险与保留意见
- 当前仓库主数据基本集中在单资产与单交易所口径，跨资产泛化证据不足。
- funding 是离散结算（常见 8h），而执行在分钟级，若不做事件时钟对齐，容易高估 carry。
- 阈值搜索很容易产生 validation 漂亮、test 归零的塌缩，需要强制加入最小成交笔数与稳定性约束。
- 这类策略对费用、冲击、借贷/转仓细节极敏感，不应用“未扣全成本”的结果做上线依据。

## 6. 来源
- MengerWen. (2026). *Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates*. Venue: GitHub Repository.
- DOI: N/A
- Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
- Repo URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
- API metadata: `https://api.github.com/repos/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
- Public data docs: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History`、`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
