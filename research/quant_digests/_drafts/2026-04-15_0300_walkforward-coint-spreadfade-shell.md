# walk-forward 协整配对 spread fade 完整壳
- 时间：2026-04-15 03:00 UTC
- 类型：GitHub / portability probe
- 主题类型：raw alpha
- 基础 alpha：cointegrated spread mean reversion（协整价差均值回复）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / walk-forward / cointegration / z-score / cost / risk
- 证据类型：工程经验 + repo 内置回测 + 公开行情 portability probe

## 1. 这次看了什么
这次看的是 2026 GitHub 仓库 **atharvajoshi01 / crypto-stat-arb**。它不是那种只给一个 `z-score > 2` 的课堂级 pairs 示例，而是把一条 **可直接拆成 entry / exit / sizing / risk / cost / walk-forward** 的完整 stat-arb 壳写全了：先做相关性预筛，再做 Engle-Granger 协整、半衰期过滤、rolling hedge ratio、`|z|>2` 入场、`|z|<0.5` 离场、`|z|>4` 止损、单对最大权重 `20%`、组合回撤熔断 `15%`、波动率目标 `10%`、并把 round-trip 成本显式写成 `40 bps`。

**一句话核心结论：** 这份 repo 最值钱的不是它的收益截图，而是它把「pair admission → spread signal → 组合中性化 → 风控 → walk-forward OOS」串成了一个可直接搬去 desk 做 first verdict 的完整骨架。  
**一句话证明方式：** 证据主要来自 repo 自带的 OOS 结果表 + 源码参数定义 + 我补的 Binance USDⓈ-M `15m` 轻量 portability probe。

## 2. 核心结论
- **base alpha 很清楚**：不是“相关性高就做配对”，而是 `log(P_A) - beta * log(P_B)` 这条 spread 在历史上可回复，然后做 `z-score fade`。
- repo 的最大优点是**诚实**。它给的真实数据结果并不好看：Kraken `11` 币、`2021-2026` 样本里，OOS（`2025-02` 到 `2026-01`）raw annual return 约 `-18.8%`、risk-managed 约 `-15.7%`，Sharpe 约 `-2.56 / -2.27`，但 BTC correlation 只有 `0.03`。也就是说，**中性化是真的，赚钱没有被硬吹出来**。
- repo 里 synthetic 环境最佳参数大致是 `entry_z=2.5 / exit_z=0.5 / cost=20bps`，最佳 Sharpe 约 `1.40`；说明这条线在“理想摩擦”里是有骨架的，但真实市场里首先输给成本和可交易 pair 稀缺度。
- 仓库公开列出的 pair 里，`SOL/DOGE`、`ETH/DOT`、`ETH/ATOM` 的 half-life 约 `8.4 / 10.1 / 11.3` 天；这很适合日频或更慢的 execution shell，但未必天然能平移到 desk 的 `5m/15m`。
- 我补的 Binance USDⓈ-M `15m` naive probe（`11` 个 liquid majors、约 `120d`）里，只筛到两个勉强像样的候选：`BTC/ETH` 与 `BTC/SOL`。`BTC/ETH` gross 累计约 `+2.13%`，但按 `8bps` 成本后变成约 `-2.97%`；`BTC/SOL` gross 累计约 `+5.40%`，但 `8bps` 后也掉到约 `-1.77%`。结论很直接：**短周期里这条壳不是完全没生命，但 taker 成本会先把它打穿。**

## 3. 为什么和当前项目有关
当前 bot7 的优先级不是再看一个“相关性配对教程”，而是补一个 **能直接落地完整策略** 的 raw alpha skeleton。这个 repo 正好满足：
- raw alpha 本体明确：`cointegrated spread fade`
- entry / exit 清楚：`2.0 / 0.5 / 4.0`
- sizing 清楚：按 `1 / (1 + |beta|)` 做双腿中性化
- risk 清楚：单对权重上限、组合 DD halt、vol target、定期 recoint
- cost 清楚：双腿双边 round-trip 成本显式写入

换句话说，它比很多“pair 论文”更适合直接进入我们 desk 的 **复现素材池**：不是因为它已经赚钱，而是因为它已经把一整套可否证、可删改、可替换的组件写清楚了。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / market-neutral
- 基础 alpha：协整 spread 的均值回复
- regime：repo 里有低波 / 常态 / 危机分层，以及 crisis 下的 exposure 调整
- filter / veto：相关性预筛、ADF 协整检验、half-life 区间筛选、pair health re-check
- risk / sizing / execution overlay：dollar-neutral sizing、单对权重上限、组合 DD 熔断、vol scaling、显式交易成本

## 4. 可复刻的最小实验
**研究假设**：`15m` 上如果继续沿用“先挑 pair，再做 spread fade”的骨架，edge 可能还在，但只能活在更低摩擦执行里。  
**可计算定义**：
1. universe：Binance USDⓈ-M liquid majors（先从 `BTC/ETH/SOL/XRP/ADA/DOGE/LINK` 起）  
2. pair admission：过去 `30d-45d` 的相关性 + Engle-Granger + half-life 过滤  
3. signal：rolling beta spread 的 `z-score`，`|z|>2` 入场，`|z|<0.5` 离场，`|z|>4` stop  
4. sizing：`1/(1+|beta|)` 做双腿资金分配，组合层再加 gross cap  
5. cost ladder：先看 `4 / 8 / 12 bps` 三档有效成本

**最小回测切口**：
- 资产：`BTC/ETH/SOL` 优先，再扩到 `DOGE/LINK/AVAX`
- 周期：先 `15m`，再压到 `5m`
- 样本：近 `120d-180d`
- 最该先看：`post-cost avg bps/trade`、`trade count`；如果这两个不过线，别急着做更复杂的 regime 层

## 5. 风险与保留意见
- 这类 stat-arb 最大敌人通常不是“信号完全失效”，而是 **换手 × 双腿成本 × 可交易 pair 稀缺**。
- repo 的真实 OOS 结果为负，说明“中性化”不等于“有 alpha”；如果只抄壳不重做 admission / execution，容易复制出一个干净但赔钱的系统。
- 我补的 Binance probe 是 **naive portability check**：为了快速验证，没有做完整 ADF / Johansen / walk-forward recoint，只能说明方向，不该当正式 verdict。
- 如果 `15m` 在 `4-8bps` 仍然不过线，这条线下一步应优先转向：
  - 更低摩擦的 maker-ish close
  - 更稀疏的 pair admission
  - 或直接改做 basket / relative-value router，而不是硬压参数

## 6. 来源
- Atharva Joshi. (2026). *crypto-stat-arb*. GitHub repo.
  - Repo URL: `https://github.com/atharvajoshi01/crypto-stat-arb`
- 关键源码：
  - `cryptoarb/config.py`
  - `cryptoarb/pairs.py`
  - `cryptoarb/signals.py`
  - `cryptoarb/portfolio.py`
  - `cryptoarb/backtest.py`
  - `cryptoarb/risk.py`
  - `examples/real_data_backtest.py`
- 本地 portability probe：
  - 脚本：`reports/artifacts/quant_digests/2026-04-15_crypto_statarb_walkforward_probe.py`
  - 结果：`reports/artifacts/quant_digests/2026-04-15_crypto_statarb_walkforward_probe_summary.json`
  - 表格：`reports/artifacts/quant_digests/2026-04-15_crypto_statarb_walkforward_probe_summary.csv`
