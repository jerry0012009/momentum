# Rank444 — Audit Notes

## 审计优先级

按阻断性从高到低排列。P0 级问题不修复，其他审计结果不可信。

---

## P0 — 数据入口（Data Entry）

**问题：** 数据未固化，每次运行实时拉取

**涉及代码：**
- `rank444_rsi_bb_backtest.py` → `fetch_yfinance()`, `fetch_akshare_stock()`, `fetch_akshare_futures()`
- `rank444_full_backtest.py` → `fetch_yf()`, `fetch_akshare_futures()`

**风险：**
- yfinance 历史数据会被 Yahoo 静默修正（dividend/split adjustments）
- akshare 不同版本返回格式可能变化
- 今天跑的结果，明天重跑可能不同

**审计要求：**
- [ ] 固化当前使用的数据为 parquet
- [ ] 生成 manifest.json（含 downloaded_at, symbols, commit_sha）
- [ ] 验证重跑一致性

---

## P0 — 数据复权与时间区间

**问题：** 复权方式不透明，时间区间不统一

**涉及代码：**
- yfinance: `auto_adjust=True` → 自动前复权，但具体算法未文档化
- akshare A股: `adjust="qfq"` → 前复权
- akshare 期货: 无复权

**风险：**
- `auto_adjust=True` 会修改 OHLCV 所有字段（不只是 close）
- 不同数据源的复权逻辑不同，跨市场比较可能不公平
- 时间区间不一致（A股3年 vs 期货2022年起 vs 美股3-15年）

**审计要求：**
- [ ] 文档化 yfinance auto_adjust 的具体行为
- [ ] 统一时间区间或明确说明差异原因
- [ ] 验证复权前后价差是否合理

---

## P0 — RSI / Bollinger 计算

**问题：** 指标计算与回测耦合，无法独立审计

**涉及代码：**
- `calc_rsi(series, period=7)` — 使用 `ewm(com=period-1)` 平滑
- `calc_bollinger(series, period=20, mult=2.0)` — 使用 `rolling(period).mean()` + `rolling(period).std()`

**具体审计点：**
- [ ] RSI 使用 `ewm(com=period-1)` 而非 Wilder 标准的 `ewm(alpha=1/period)`，两者等价吗？→ 验证：`com=period-1` 时 `alpha = 1/period`，确实等价 ✓
- [ ] BB 使用 `rolling(period).std()` 默认 `ddof=1`（样本标准差），是否应该用 `ddof=0`？
- [ ] 指标计算的 warmup period：RSI 需要 7 bars，BB 需要 20 bars，但 `dropna()` 只丢弃 NaN，不保证前 20 根 bar 的 RSI 已稳定
- [ ] 无独立的 factor_values.parquet 产物

---

## P0 — signal_time 与 execution_time

**问题：same-bar signal + execution = 乐观偏差**

**涉及代码（v1）：**
```python
for i in range(1, len(df)):
    row = df.iloc[i]
    # 开仓
    if row["rsi"] < rsi_limit and row["close"] < row["bb_lower"]:
        shares = int(initial_capital * (1 - commission) / row["close"])
        position = {"entry_price": row["close"], ...}
```

**问题分析：**
- 信号判断和执行价格都在同一根 bar 的 `close` 上
- 真实交易中，RSI 和 BB 的值要等到 bar 收盘才能确定
- 以收盘价成交意味着"看到信号的同时就以该价格成交"——这在日线上几乎不可能
- **正确的假设应该是：** `signal_time = close[t]`, `execution_price = open[t+1]`

**审计要求：**
- [ ] 将 execution_price 改为 `open[t+1]`
- [ ] 对比 same-bar vs next-bar 的收益差异
- [ ] 如果差异 > 10%，标记当前结果为"optimistic baseline"

---

## P1 — same-bar close execution 风险

**详细分析：**

这是一个 P0 问题的子项，但值得单独说明。

当前回测假设：
1. Bar t 收盘 → 计算 RSI(t) 和 BB(t)
2. 如果 RSI(t) < 30 AND close(t) < BB_lower(t) → 以 close(t) 买入

真实情况：
1. Bar t 收盘 → 计算 RSI(t) 和 BB(t)（需要等 bar 结束）
2. 看到信号 → 下单（需要时间）
3. 最快成交在 bar t+1 的 open

**影响估算：**
- 对于日线级别，close → next open 的平均跳空约为 0-5bps
- 但在极端行情中（信号触发时），跳空可能 20-50bps
- 净效果：回测收益可能被高估 5-15%

---

## P1 — 手续费和滑点

**当前成本模型：**
- 手续费：0.1% 单边（`COMMISSION_RATE = 0.001`）
- 滑点：**未建模**
- Spread：**未建模**
- 资金成本：**未建模**

**缺失项：**

| 成本项 | 状态 | 影响 |
|--------|------|------|
| 手续费 | ✓ 已建模 | 0.1% 单边，对 A股/美股偏低 |
| 滑点 | ✗ 未建模 | 日线级别约 5-20bps |
| Spread | ✗ 未建模 | 取决于标的流动性 |
| 资金费率 | N/A | 非永续合约 |
| 印花税（A股） | ✗ 未建模 | 卖出 0.05% |

**审计要求：**
- [ ] 加入至少 5bps 默认滑点
- [ ] A股加入卖出印花税 0.05%
- [ ] 做敏感性分析：0/5/10/20bps 滑点下的收益变化

---

## P1 — PnL / Drawdown / Sharpe 计算口径

### PnL 计算（v1）

```python
gross_pnl = shares * (exit_price - entry_price)
net_pnl = gross_pnl - entry_cost - exit_cost
pnl_pct = (exit_price / entry_price - 1) * 100
```
→ 逐笔计算，无复利效应

### PnL 计算（v2）

```python
cum = (1 + tdf["net_pnl_pct"] / 100).cumprod()
total_ret = (cum.iloc[-1] - 1) * 100
```
→ 复利计算 ✓

### Drawdown 计算（v1）

```python
cum_pnl = tdf["net_pnl"].cumsum()
equity = initial_capital + cum_pnl
running_max = equity.cummax()
drawdown = (equity - running_max) / running_max * 100
```
→ 基于逐笔累计 PnL，**不是逐 bar 权益曲线**。只在有交易时更新权益，空仓期权益不变。这低估了最大回撤。

### Drawdown 计算（v2）

```python
eq = cum.cummax()
dd = (cum - eq) / eq * 100
```
→ 基于逐笔复利净值，同样不是逐 bar。

### Sharpe 计算（v1 & v2）

```python
sharpe = tdf["pnl_pct"].mean() / tdf["pnl_pct"].std() * sqrt(252 / avg_hold_days)
```
→ **Trade-level simplified Sharpe**，非标准。标准做法是用逐日（或逐 bar）收益率序列计算年化 Sharpe。

**审计要求：**
- [ ] 重新计算 bar-level equity curve
- [ ] 基于 equity curve 计算标准 Sharpe
- [ ] 明确标注当前 Sharpe 为 "trade-level_simplified_sharpe"
- [ ] 对比两种 Sharpe 的差异

---

## P2 — 参数网格和选择偏差

**v2 参数网格：**

| 参数 | 候选值 | 数量 |
|------|--------|------|
| RSI period | [5, 7, 10, 14] | 4 |
| RSI limit | [25, 30, 35] | 3 |
| BB period | [15, 20, 25] | 3 |
| BB mult | [1.5, 2.0, 2.5] | 3 |
| **总组合** | | **108** |

**v3 参数网格：** 750 组合（扩展版本）

**选择偏差风险：**
- 144/750 种组合中选最优 → 存在数据窥探（data snooping）
- 报告中使用默认参数 (7, 30, 20, 2.0) 的结果，但未说明这是"事后选择"还是"先验选择"
- 如果是事后选择最优参数，真实 OOS 表现可能显著低于回测

**审计要求：**
- [ ] 明确默认参数 (7, 30, 20, 2.0) 的选择依据（先验 vs 事后）
- [ ] 做 combinatorial purged cross-validation 或 walk-forward validation
- [ ] 计算 deflated Sharpe ratio（考虑参数搜索空间）
- [ ] 报告参数敏感性热力图

---

## P3 — 其他审计点

### 回测引擎一致性

v1 和 v2 的 backtest() 函数有细微差异：
- v1: `shares = int(initial_capital * (1 - commission) / row["close"])` — 有股数计算
- v2: 无股数，只算 pnl_pct — 百分比收益

两个版本对同一标的可能产出不同结果。需要验证一致性。

### 出场逻辑 bug

`close_gt_open` 出场模式已被 fresh intake memo 标记为 bug：
- "阳线即卖"在日线上过于频繁
- 频繁换手导致手续费侵蚀
- 不代表有效的交易逻辑

### 年化收益计算

```python
years = max((last_date - first_date).days / 365.25, 0.01)
annual_return_pct = ((1 + total_return_pct / 100) ** (1 / years) - 1) * 100
```
→ 使用 `total_return_pct`（简单累加）做复利年化，在 v1 中不一致。v2 使用 cumprod 更正确。
