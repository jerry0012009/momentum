# Hyperliquid HIP-3（2026 新 repo）：把 mark-vs-oracle 极端偏离做成可直接落地的短周期 raw alpha
- 时间：2026-04-03 08:08 UTC
- 类型：GitHub repo
- 主题类型：raw alpha
- 基础 alpha：`same-underlier mark-vs-oracle premium` 的极端偏离会在短时间内向 oracle 收敛，可做成 percentile-gated mean reversion
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：relative-value / stat-arb / basis / mark-vs-oracle / premium / mean-reversion / hyperliquid / HIP-3 / percentile-threshold / time-stop / 1m / 3m / 5m / 15m
- 证据类型：repo 内回测结果 + 策略源码证据 + 公共数据口径

**先回答 base alpha：这篇东西的 base alpha 很清楚，不是“市场故事”，而是“永续标记价格相对 oracle 的短时超涨/超跌会回归”，可直接写成入场、出场、仓位和止损规则。**

## 1) 这次看了什么
看了 2026 新仓库 `andreaambrosio/hype-backtesting`，重点读了：
- `README.md`
- `src/strategies/basis_reversion.py`
- `config/settings.yaml`
- `research/run_hip3_analysis.py`

这套框架主打 Hyperliquid / HIP-3 相关策略，直接把 `premium = (mark - oracle) / oracle` 当成可交易对象，不只是做监控面板。

## 2) 核心结论（给 desk 的版本）
- **一句话核心结论**：对带 oracle 锚的永续/合成资产，`mark-vs-oracle premium` 的尾部偏离本身就是一条独立 raw alpha，而不是只能当 risk overlay。
- **repo 里最有价值的证据**：在 90 天、小时级 Hyperliquid 数据上，`Basis Dislocation Reversion` 是仓库 9 个策略里表现最好的一个：**+3.88% return，Sharpe 4.52，Sortino 6.16，299 trades**。
- **最适合 desk 的细节**：仓库明确写到 HIP-3 Silver 曾出现 **463 bps** 的 mark-vs-oracle gap，**>400 bps 仅持续 95 秒**，随后 **19 分钟内回到 <50 bps**。这说明真正该做的不是慢吞吞地看 funding，而是抓“极端 premium pocket 的快速收敛”。
- **源码不是空话**：策略把入场、缩容、止损、time stop 都写死成规则，而不是只给一张漂亮图。

## 3) 为什么和当前项目有关
这条线补的是 **same-underlier relative-value / stat-arb raw alpha 素材池**，而且比“再写一篇泛 pairs”更值钱，原因有三个：
1. **base alpha 很纯**：只依赖同一资产的 mark 和 oracle，不需要复杂 pair-selection。
2. **公开数据可拿**：Hyperliquid 公共 API 可直接拿 candles / funding / premium，无需付费数据。
3. **天然适配短周期**：repo 虽然主跑 `1h`，但作者自己举的最强 pocket 是秒到分钟级收敛，这反而更适合我们先做 `1m/3m/5m/15m` 最小实验。

## 3.5) 策略拆解（必填）
- 方向属性：双向 mean reversion（premium 太高做空 perp，premium 太低做多 perp）
- 基础 alpha：`premium = (mark - oracle) / oracle` 的极端偏离向 0 回归
- regime：优先在 oracle 锚定还可信、盘口未失真、premium 处于尾部分位时交易
- filter / veto：
  - 只做 `|premium| > rolling q90/q95`
  - 若 premium 连续扩张且成交/盘口深度恶化，先 veto
  - 宏观大事件、预言机异常、停牌/指数源异常时禁做
- risk / sizing / execution overlay：
  - 仓位随偏离幅度放大，但设上限
  - 必须带 `time stop`，因为这类 alpha 最怕“不回归还继续磨”
  - 成本要显式扣 taker fee + 滑点，不能把 premium 收敛幅度全当净利润

## 4) repo 里最值得抄的参数骨架
### 4.1 策略源码默认版（`basis_reversion.py`）
- 入场：`abs(premium_bps)` 大于 `max(50bps, rolling 95% 分位)`
- 出场：收敛到 `10bps` 内
- 最长持有：`60 bars`
- 仓位：`base_position_pct = 10%`，随偏离幅度放大，最高 `25%`
- 止损：继续朝不利方向再走 `200bps`

### 4.2 repo 研究脚本的实盘化调参版（`run_hip3_analysis.py`）
作者在主分析脚本里把口径调得更接近真实 HL 小 premium 环境：
- 入场：`3bps` 或 `rolling q90`，取更高者
- 出场：`1bps`
- 最长持有：`24 bars`
- 基础仓位：`12%`
- 最大仓位：`25%`
- 止损：`50bps`
- 回测成本：`2bps commission + 1bps slippage`

这很重要：**真正可迁移的不是某个绝对 bps，而是“rolling percentile + time-boxed exit + capped scaling”这个骨架。**

## 5) 给 1m / 3m / 5m / 15m desk 的最小实验
### 研究假设
Hyperliquid 上带 oracle 锚的 perp / HIP-3 资产，`premium` 的极端偏离在分钟级存在可交易回归；alpha 核心不在 funding，而在 **短时 pricing dislocation**。

### 最小可复现实验口径
**数据源**：Hyperliquid 公共 API
- `candles` / OHLCV
- `funding history` 或带 `premium` 字段的数据
- 若字段不齐，可直接自己算：`premium = (mark_price - oracle_price) / oracle_price`

**更新频率**：可下采样到 `1m / 3m / 5m / 15m`

**先测资产**：
- 先从 `BTC / ETH` 做低摩擦 sanity check
- 再上更容易出现错价的 HL 特色资产 / HIP-3 标的

### 信号定义（建议先做最小 honest 版）
1. 计算 `premium_bps`
2. 做 rolling 分位：
   - `q_hi = rolling_q90(abs(premium_bps), 96 bars)`
   - `q_lo` 不需要单独算，直接用负号对称处理
3. 入场：
   - `premium_bps > max(3, q_hi)` → 做空 perp
   - `premium_bps < -max(3, q_hi)` → 做多 perp
4. 出场：
   - `abs(premium_bps) < 1bps` 平仓
   - 或持有超过 `N bars`（1m 先测 15/30/60；5m 先测 3/6/12）
5. 止损：
   - 入场后 premium 再恶化 `1.5~2.0x entry_threshold`
   - 或价格 hit `oracle-gap stop`

### 先测 4 组组合
- `1m × 96-bar percentile`
- `3m × 64-bar percentile`
- `5m × 48-bar percentile`
- `15m × 48-bar percentile`

### 先看 3 个指标
- 成本后 `net pnl / turnover`
- `entry premium → exit premium` 的平均压缩幅度
- 按资产分组后的稳定性（不能只靠单一妖币）

## 6) 这条线最容易犯的错
- **把它误读成 funding carry**：这条 alpha 的核心不是收 funding，而是 premium pocket 自身的回归。
- **把绝对阈值抄死**：`3bps` 在 BTC/ETH 和在小币/HIP-3 资产上不是同一回事，必须做 rolling percentile。
- **忽略预言机/指数异常**：如果 oracle 本身跳了，mark 回归 oracle 不代表有 alpha，只代表你在追坏锚。
- **忘记 time stop**：这类策略最怕“判断对方向、死于慢收敛和成本”。

## 7) 我对 desk 的结论
如果今天只允许加 1 条新的 relative-value 原型进研究池，我会把这条记成：

> **`oracle-premium percentile fade × time-boxed exit`**

它的优先级高于再补一个泛泛 pairs 变体，因为：
- base alpha 更干净；
- 公共数据更容易拿；
- 可以很快下沉到 `1m/3m/5m/15m` 做 honest 最小实验；
- repo 已经给出完整策略骨架与成本壳，不用从 0 编 entry/exit/risk。

## 8) 下一步怎么测
1. 先拉 Hyperliquid 近 30~90 天 `1m/5m` premium 数据；
2. 对 `BTC/ETH + 2~4 个 HL 特色资产` 跑 `rolling q90/q95` 的 symmetric fade；
3. 固定成本为 `2bps fee + 1bps slippage`，先测 `time stop` 对收益的影响；
4. 再加一层 `oracle integrity veto`：oracle 跳变超过 rolling P99 时禁做；
5. 最后比较两种 sizing：`fixed size` vs `premium-scaled size`。

## 9) 来源
### 仓库
- Andrea Ambrosio. (2026). *hype-backtesting*.
- 类型：GitHub repo
- Repo URL: `https://github.com/andreaambrosio/hype-backtesting`
- GitHub API metadata: `https://api.github.com/repos/andreaambrosio/hype-backtesting`
- README: `https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/README.md`
- 策略源码：`https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/src/strategies/basis_reversion.py`
- 研究脚本：`https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/research/run_hip3_analysis.py`
- 配置：`https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/config/settings.yaml`

### 公共数据口径
- Hyperliquid public API base: `https://api.hyperliquid.xyz`
- Repo 说明的数据源：Hyperliquid API（candles, funding rates, premium, HIP-3 vault data），无需 key
