# 别把 EMA slope 继续当 15m 原始入场键：`NTZ re-entry` 更像 breakout-short / Fib / EMA-PSAR 的 shared fail-fast veto
- 时间：2026-03-19 21:10 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/ema-slope/no-trade-zone/state-machine/fail-fast/veto/repo/crypto/5m/15m
- 证据类型：工程证据（仓库源码 + 仓库自带回测报告）

## 1. 这次看了什么
这次看的主来源是 GitHub 仓库 **asaflu / bitcoin-ema-analyzer (2026)**。它的重点不是“再发明一个 EMA 交叉”，而是把 `EMA slope` 明确写成一个 **三状态机**：`BULL / BEAR / NTZ(no-trade zone)`，并且把“回到 NTZ”当成退出条件。

## 2. 核心结论
- **一句话核心结论**：对 5m/15m desk，更该偷的是“`NTZ 出入状态` 这层 veto 逻辑”，不是把这个仓库当 15m 直接开仓 alpha。  
- **一句话证明方式**：源码里 `ema_slope.py` 直接把信号写成“越过 ±阈值才开仓、回到阈值内就平仓”的状态机；仓库报告里的 timeframe 对照显示该框架在低周期（含 15m、5m）明显恶化。  
- 从 `backtest_report_20260209_082259.html` 的 timeframe 对照看：`15m total_return≈-14.63%`、`5m≈-28.17%`，而 `4h≈+41.37%`、`1d≈+11.15%`（同一报告口径）。这更像“高周期趋势状态特征”，不是低周期裸信号。  
- 仓库参数表的高分组合（如 `smooth_bars=3, ma_length=15, ntz=5`）对应 `total_return≈180.09%, win_rate≈35%, max_drawdown≈-24.46%`，说明它的边际收益主要来自“少量趋势段捕捉 + 低胜率大盈亏比”，并不天然等价于 15m continuation 可执行性。  
- 源码层面还有一个关键现实：`engine.py` 实际只完整支持 long 进出（`SELL` 被当作平多分支），所以它更像“方向状态实验框架”，不是可直接照搬的双向实盘引擎。

## 3. 为什么和当前项目有关
它和三条收口线是直接相关的：
1. **V3 breakout-short follow-up**：突破后若 slope 快速回到 `NTZ`，可直接记为 follow-up 衰竭，提前 veto/减仓。  
2. **Fib retest_hold**：回踩后不是“触位就算守住”，而是要求 slope 从 `NTZ→趋势侧` 的再出带确认。  
3. **EMA / PSAR raw alpha focus**：把 EMA slope 从“入场主键”降级为“状态闸门”；PSAR 更适合继续做 HTF 方向锚，二者角色更清晰。

## 4. 可复刻的最小实验
### 研究假设
在 15m crypto 上，`NTZ re-entry veto` 作为共享覆盖层，能降低假延续损耗（尤其 4~8 bars 内反抽反杀），即使不提高胜率，也应改善成本后回撤与尾部亏损。

### 一个可计算定义（接现有三条线）
- 先算：`ma = EMA(close, L)`；`raw = ma - ma.shift(s)`；`slope_norm = 100 * raw / (rolling_max(raw,n)-rolling_min(raw,n))`。
- 定义状态：`slope_norm > +θ => BULL`；`< -θ => BEAR`；否则 `NTZ`。
- 共享 veto 规则：
  - 多头 setup（Fib hold / EMA continuation）触发后，若 `N` 根内重回 `NTZ`，则立即失效；
  - 空头 setup（breakout-short follow-up）触发后，若 `N` 根内由 `BEAR` 回 `NTZ`，同样失效；
  - `N ∈ {2,4,6}`，`θ ∈ {8,10,12}` 做小网格。

### 最小回测切口
- 资产：BTC/ETH/SOL perp
- 周期：15m（执行），可加 5m 做入场细化
- 样本：最近 120~180 天
- 成本：`6/10 bps per side`
- 对照：
  1) baseline（三条线原规则）
  2) baseline + static slope gate
  3) baseline + **NTZ re-entry veto**（本轮主测）

### 最先看 3 个指标
1. `post_cost_return`  
2. `max_drawdown` 与 `left-tail(5% trade pnl)`  
3. `false_follow_through_4bars`（触发后 4 根内反向失效占比）

## 5. 风险与保留意见
- 这是仓库工程证据，不是同行评审论文证据；结论应视为“高质量实现启发 + 待本地复核”。
- 仓库报告的回测口径与我们当前 15m perp 成本口径不完全一致，不能直接拿收益数字做外推。
- `slope` 归一化会受滚动窗口极值影响；不同波动 regime 下阈值可迁移性有限，需做 `θ` 稳定性检查。
- 若 `NTZ` 设得过宽，会把 trade density 压到不可用；若过窄，又退化成“几乎一直交易”。

## 6. 来源
1. asaflu. (2026). *bitcoin-ema-analyzer*. GitHub repository.  
   - Repo URL: https://github.com/asaflu/bitcoin-ema-analyzer
2. asaflu. (2026). *EMA slope state machine implementation* (`indicators/ema_slope.py`).  
   - Readable URL: https://raw.githubusercontent.com/asaflu/bitcoin-ema-analyzer/main/indicators/ema_slope.py
3. asaflu. (2026). *Backtesting engine* (`backtesting/engine.py`).  
   - Readable URL: https://raw.githubusercontent.com/asaflu/bitcoin-ema-analyzer/main/backtesting/engine.py
4. asaflu. (2026). *Comprehensive backtest report* (`backtest_report_20260209_082259.html`).  
   - Readable URL: https://raw.githubusercontent.com/asaflu/bitcoin-ema-analyzer/main/backtest_report_20260209_082259.html
