# 别把这份 2026 高星 repo 只读成通用交易 bot：对 short-cycle desk，更该先测的是「session VWAP σ-band fade」这条单资产 raw alpha
- 时间：2026-04-07 19:02 UTC
- 类型：GitHub / source audit（`README.md` + `shared_strategies/spot/strategies.py` + `backtest/backtester.py` + repo metadata）
- 主题类型：raw alpha
- 基础 alpha：日内价格相对 **session VWAP** 的大幅偏离会向均值回归；更具体地说，是 `close - session_vwap` 的滚动 σ 偏离在液态币上存在可交易的 fade 机会。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：mean-reversion / single-asset / vwap / intraday / spot-perp-transfer / 1m / 3m / 5m / 15m / repo / cost / risk
- 证据类型：工程证据

## 1. 这次看了什么
看的是 `richkuo/go-trader`（2026-02 创建，2026-04-07 仍在更新，约 77 stars）里被埋在“大而全交易 bot”下面的一条小策略：`vwap_reversion`。源码把它写得很直接：按日重置 VWAP，默认 `entry_std=1.5`、`exit_std=0.2`，当价格跌破 `VWAP - 1.5σ` 时给多头信号，涨破 `VWAP + 0.2σ` 时给空头/平多信号；配套 backtester 默认吃 `10 bps` 手续费 + `5 bps` 滑点，并挂着组合 kill switch 与策略冷却。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值钱的不是“又一个多市场 bot”，而是把 **session VWAP 偏离均值回复** 明确写成了一个能马上迁到 `1m/3m/5m/15m` 的原始 alpha 壳。
- **一句话证明方式：** 证据不是论文表格，而是源码里把 anchor、band、entry/exit、成本和风控口径都写死了——它已经是一个可复跑、可立刻做 first verdict 的工程样本。
- 它和普通 rolling-mean z-score MR 的差别在于：均值锚点不是过去 N 根收盘均值，而是**当日成交量加权中心（VWAP）**；这更像“日内偏离交易”，而不是纯统计平滑。
- `entry_std=1.5` / `exit_std=0.2` 这个默认壳，本质是在赌：**远离 VWAP 的瞬时失衡，常比趋势延续更短命**；先用远端入场、近中心出场，把盈亏比交给回归距离，而不是赌大趋势。
- repo 自带的 backtester 默认是 `0.1%` commission + `0.05%` slippage；这很粗，但反而适合 desk 做第一轮 friction ladder：如果在这种偏严口径下都站不住，就别急着往 live 走。
- 对我们当前研究池，它补的是一个**单资产、anchor-based、非 pairs / 非 funding / 非 cross-sectional** 的 raw alpha 缺口，适合和后续 trend gate、liq veto、session map 做解耦组合。

## 3. 为什么和当前项目有关
这条线值得收进 `momentum`，因为它不是“解释型 overlay”，而是一条能独立下单的单币 raw alpha：
- 它补的是 **mean reversion** 素材池，而不是继续在 breakout / lead-lag / carry 上内循环；
- 它对数据要求低：只要 OHLCV 就能先做最小实验，不需要先拿深度盘口或外部链上数据；
- 它天然能迁到 `1m/3m/5m/15m`，尤其适合 BTC/ETH/SOL 这种高流动标的；
- 后续若要增强，也很清楚：先在 alpha 本体上做 first verdict，再叠加 regime/filter（如 ADX、funding、流动性时段、波动分位）。

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 单资产
- 基础 alpha：`session VWAP deviation mean reversion`
- regime：优先在**非单边趋势、流动性正常、不是消息冲击后第一段加速**的环境中使用
- filter / veto：可后加 `ATR/realized vol 过高 veto`、`news/event veto`、`low-liquidity slot veto`
- risk / sizing / execution overlay：固定风险仓位或 vol-target；优先 taker-in / taker-out 做 first verdict，再比较 maker-passive 版本；日内 flat，避免隔夜 carry/funding 污染

## 4. 可复刻的最小实验
**研究假设：** 对 liquid crypto，价格一旦偏离当日 VWAP 达到 `1.5σ~2.0σ`，短时间内更容易回到 VWAP 附近，而不是继续无条件漂移。

**可计算定义：**
- 用 `1m` 原始 K 线先算 `session_vwap_t = cumsum(tp*vol) / cumsum(vol)`，UTC 日切重置；
- `sigma_t = rolling_std(close - session_vwap, 20)`；
- Long：`close < vwap - k*sigma`；Short：`close > vwap + k*sigma`；
- Exit 先测三版：`touch vwap`、`touch 0.2σ 内带`、`8 bar time stop`。

**最小回测切口：**
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT` perp 或 spot
- 周期：`1m -> 3m/5m/15m` 聚合；但 **VWAP 必须先用 1m 原始数据算**，不要直接拿 15m bar 算假 VWAP
- 样本：先跑 `2024-01-01 ~ 2026-04-07`
- 成本：先做 round-trip `4 / 8 / 12 / 20 bps` friction ladder

**最该先看：**
1. 成本后每笔期望 / 每日 turnover；
2. 不同持有时长下的回归完成率（尤其 `<= 8 bars` 是否占大头）。

## 5. 风险与保留意见
- repo 现成调度主要跑 `1h`，而 desk 想测的是 `1m/3m/5m/15m`；**信号思想能迁，但参数不能直接照抄**。
- session VWAP 是强路径依赖锚点；若遇到单边趋势日，价格可能长时间“贴着偏离继续走”，fade 很容易被趋势拖死。
- UTC 日切未必是最优 session 切法；对 crypto 24/7 市场，亚洲/欧洲/美盘切法都值得单独对照。
- 仅用 OHLCV 算 VWAP，会把真实逐笔成交结构压扁；第一轮可先做，但后续若 edge 接近成本线，必须补 trade-level VWAP 与 microstructure veto。
- repo 的 backtester 默认更像单腿 spot 壳；若 desk 走 perp 对称 long/short，需要自己把 `sell_cross` 明确拆成 short entry，而不只是平多。

## 6. 来源
- richkuo. (2026). *go-trader*.
  - Repo URL: `https://github.com/richkuo/go-trader`
  - Readable URL: `https://github.com/richkuo/go-trader/blob/main/README.md`
- richkuo. (2026). `shared_strategies/spot/strategies.py`.
  - Strategy snippet URL: `https://github.com/richkuo/go-trader/blob/main/shared_strategies/spot/strategies.py`
- richkuo. (2026). `backtest/backtester.py`.
  - Backtester URL: `https://github.com/richkuo/go-trader/blob/main/backtest/backtester.py`
