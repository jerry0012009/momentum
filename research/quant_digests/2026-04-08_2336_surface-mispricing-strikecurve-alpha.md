# 别把这份 prediction-market repo 只读成数据基础设施：对 short-cycle desk，更该先测的是 `same-event strike surface mispricing × fair-value recross / time-stop`
- 时间：2026-04-08 23:36 UTC
- 类型：GitHub / 工程实现
- 主题类型：raw alpha
- 基础 alpha：`same-event multi-strike surface mispricing mean reversion`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：prediction market / relative value / stat-arb / surface fitting / strike ladder / mean reversion / Polymarket / 1m / 5m / 15m
- 证据类型：工程经验 / source audit

## 1. 这次看了什么
这次看的是 `pawelsibyl/marketlens-python`。我重点审了 `README.md`、`examples/backtest_surface.py`、`examples/backtest_limit_orders.py`、`examples/microstructure.py`、`src/marketlens/helpers/surface.py`。它最值得 intake 的，不是“能回放 Polymarket L2”这件事，而是 repo 已经把 **同一事件多 strike 合约的曲线错价** 写成一条可直接回测的 raw alpha。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值钱的不是 prediction market 数据接入，而是把“同 expiry、同标的、不同 strike 的价格必须落在一条单调 survival curve 上”这件事，直接翻成了 **可交易的相对价值 alpha**。
- **一句话证明方式：** 证据主要来自 repo 的 `backtest_surface.py`：它先用全 sibling books 拟合单调曲线，再比较单个合约的 `fair_mid` 和市场 `mid`，只有当 edge 够厚才交易，并配上时间止损与仓位上限。
- `backtest_surface.py` 的最小规则非常清楚：`edge >= 0.02`（至少 2 美分错价）才开仓，单笔 `stake=100`，`max_positions=1`，`max_hold=6h`，并要求 `min_volume=2000`、`min_step=5`、`max_spot_distance_pct=0.2`。
- `surface.py` 不是拍脑袋平滑，而是把 sibling 合约的 raw mids 先转成 survival probabilities，再做 **isotonic / PAVA 单调修正**，输出每个 strike 的 `fair_mid` / `fair_yes` / `fair_no`。这意味着 alpha 本体不是“猜方向”，而是“市场内部横截面定价不一致”。
- repo 还给了两个很实用的壳层：`backtest_limit_orders.py` 展示了 **midpoint 附近挂单、fill 后再平仓** 的 maker-ish 执行框架；`microstructure.py` 则把 `spread_bps / imbalance / best bid-ask / microprice` 拉成特征矩阵，说明这条 raw alpha 还可以继续叠一层 entry timing。
- 对 desk 来说，这比继续在单一 breakout/retest 上内循环更有价值：它属于 **相对价值 / stat-arb 原料池**，而且原始数据、定价约束、最小规则都公开可得。

## 3. 为什么和当前项目有关
这条线和当前 short-cycle desk 的关系很直接：
- 它是独立的 raw alpha，不是纯 filter：`same-event strike surface mispricing`
- 它天然 market-neutral / relative-value，能补我们当前素材池里 prediction-market 方向的“多 strike 曲线错价”空缺
- 它可以先做 `1m/5m` 最小实验，再决定是否接更细的 tick / queue / maker fill
- 它还能复用到其他 binary / barrier / range 市场，不只限于某一个 BTC 15m 事件

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / 横截面均值回归
- 基础 alpha：`同一 expiry 下多 strike 合约的 market mid 偏离拟合后的单调 survival fair value`
- regime：更适合同一事件下 strike 梯子完整、成交不太薄、离结算还有足够时间的窗口
- filter / veto：低成交额过滤、过远离 spot 的 strike 过滤、最小 strike step、edge 不到 2c 不做
- risk / sizing / execution overlay：单笔固定 stake、最大持仓数限制、`max_hold=6h` 时间止损、可接 midpoint limit-order 执行与 microstructure timing

## 4. 可复刻的最小实验
**研究假设：** 如果同一事件的多 strike 价格应该落在一条单调曲线，但市场暂时把某一档 strike 定得过高/过低，那么这档合约随后会向曲线公平值回归。

**最小定义：**
1. 数据源：Polymarket 同一 expiry 的 BTC/ETH minute-hourly recurring markets，全 sibling order books / mids；spot 参考可用 Binance 或 Chainlink。公开可得，更新频率可到 tick，也可先聚合到 `1m`。
2. 每分钟做一次曲线拟合：按 repo 逻辑把各 strike `mid` 转成 survival probabilities，并用 isotonic/PAVA 强制单调。
3. 信号：`edge = fair_mid - market_mid`；`edge >= +2c` 做多，`edge <= -2c` 做空，或做 paired long-short basket。
4. 退出：`fair-mid recross`、时间止损（先照 repo 用 `6h`），或事件前最后 `N` 分钟强制平仓。
5. 最先看：`post-cost edge capture / trade`、`fill ratio`；第二层再看 paired vs unpaired 的回撤差异。

## 5. 风险与保留意见
- 这条线最怕 **梯子不全**：若同 expiry 下可交易 strikes 太少，拟合曲线会不稳。
- prediction market 的真问题不只是 fair value，还包括 **盘口很薄、队列优先、临近结算时跳价**，所以裸 midpoint backtest 会偏乐观。
- 若只能单边做 YES/NO 而不能成对对冲，策略会从相对价值退化成半方向暴露。
- 低频事件日历本身不是问题，但它不是逐根 trend alpha；更适合定位成 **事件内短窗 stat-arb**，不要伪装成全天候信号。

## 6. 来源
- `pawelsibyl`. **marketlens-python**. GitHub repo.
  - Repo URL: `https://github.com/pawelsibyl/marketlens-python`
  - Source-audited files: `README.md`, `examples/backtest_surface.py`, `examples/backtest_limit_orders.py`, `examples/microstructure.py`, `src/marketlens/helpers/surface.py`
- Public data interfaces referenced by the repo
  - MarketLens API docs: `https://api.marketlens.trade/v1/docs`
  - Polymarket data context: `https://polymarket.com/`
