# 2026-03-20 10:39 UTC · Rank 117 / ADX<18 range handoff / source intake -> park

## 本轮上下文
- 触发：bot3 13m desk auto loop
- Run 1 结果：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，仍为 `Paper Seat / EMA = running paper / waiting_not_due`
- 最近 due：美股 1d+1wk 约 9.3h；Crypto 1d+1wk 约 13.3h；A股 lane 更晚
- repo 状态：`branch=master`，`dirty_files≈1761`
- 最近 runs：今日 `research/optimization_loop` 已有约 `30` 条日志；最新几条是 `Rank 116 clean replication -> park`、`Rank 116 intake`、`Rank 115 clean replication -> park`
- `manual_narrow_paper_last_run_summary.json`：本轮核对未见新的 `P3 status-changing event` 插队理由

## 为什么本轮主资源给 Rank 117
这轮不是去找“最可能升 paper candidate”的线，而是先找“最能减少 desk 误判”的线。

在当前 fresh source 里，三条候选的边际价值大致是：
1. `ADX<18 range handoff`：最快给出 hard verdict，直接回答 `anti-chop` 能不能自动升级成 `range mean-reversion handoff`
2. `intraday sign-asymmetry + no-jump/no-FOMC`：更像下一条需要正式 intake 的 paper gate，但这轮还没拿号
3. `PSAR trailing role`：更像 exit-role 澄清，边际价值略低于先把 anti-chop 误读压掉

因此本轮先把 `ADX<18 range handoff` 正式拿顺序号为 `Rank 117`。

## intake + 诚实守门
### trade on
- 它最多只配当：当三条主线被 anti-chop 拦下后，一个候选的 `range handoff` 思路
- 最小骨架：`1H ADX<18 + 15m BB/RSI extreme + next-candle confirm`
- 不能单独开仓，不能脱离 base context 变成新 alpha

### trade off
- 如果 `ADX<18` 只说明“不该追趋势”，而没有稳定翻成 `值得反手做回归`，就必须停在 `skip / size-down`
- 不允许把 anti-chop 误写成自动反手模块

### lookahead / leakage
- ADX / BB / RSI / confirm 都必须只用当根及之前已完成 bar
- 若真要接 desk，也必须冻结到 `signal 当根及之前数据 + next-bar open + no-overlap`
- 不能用后面 4~8 bar 是否真回中轨来回填当前标签

## 当前硬结论
直接 `park / evidence pool`，不进 clean replication queue。

### 关键证据
- `range_adx<18` 事件池：`4-bar mean-reversion signed return ≈ -5.43bps`
- 同批事件 continuation proxy 反而约 `+5.43bps`
- 以 BB 中轨当最小 `TP1`：`4 bars ≈ 11.9%`，`8 bars ≈ 20.0%`
- 跨资产不一致：`BTC≈-0.75bps` 近打平，但 `ETH≈-10.40bps`、`SOL≈-4.96bps`

### 对 desk 的实际含义
- `breakout-short`：low-ADX 可以继续当 `skip short follow-up`，但不能自动变反手 fade
- `Fib retest_hold`：sideways 不等于自动回中枢，仍应保留 `hold / invalidate / timeout` 判决
- `EMA / PSAR raw alpha`：避免本体 edge 还没坐实，就提前长出一套“趋势不行切回归”的并行系统

## 本轮交付
### reader-facing
- `reports/site/reading/repo_scout/rank117_adx18_range_handoff_source_intake.html`

### artifact
- `reports/artifacts/literature/scout_rank117_adx18_range_handoff_source_intake_card.csv`

### board update
- 已把 `TODO.md` 顶部 desk board 更新为：`Rank 117` 直接 park，下一顺位改成 `Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate`

## 下一轮建议
- `Run 1 = EMA due-check only`
- 若仍 `waiting_not_due`：
  - `Run 2 = Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate source intake + 两条轻量诚实守门`
  - 若 `Rank 118` hard-fail：切 `Rank 119 / PSAR trailing role fail-safe`
- 不再给 `Rank 117` replication 预算，除非未来另开更苛刻的 conditioned handoff
