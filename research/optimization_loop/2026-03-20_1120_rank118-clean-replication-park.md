# 2026-03-20 11:20 UTC · Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate / clean replication -> park

## 本轮上下文
- 触发：bot3 13m desk auto loop
- Run 1 结果：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，仍如实返回 `Paper Seat / EMA = running paper / waiting_not_due`
- 最近 due：美股 1d+1wk 约 `8.7h`；Crypto 1d+1wk 约 `12.7h`；A 股更晚
- `manual_narrow_paper_last_run_summary.json`：未见新的 `P3 status-changing event` 插队理由
- repo 状态：`branch=master`，工作区仍有大量与本轮无关的既有脏文件，所以本轮继续只做最小相关写入，不混提

## 为什么这轮继续给 Rank 118
上一轮顶板已经把 `Rank 118` 冻结成当前 `Scout Seat` 主位，并明确这轮只允许给它 **1 次最小 clean replication**。

在 `EMA = waiting_not_due` 的前提下，这一轮最值钱的问题不是“再找一个新题”，而是尽快回答：
**这条 direction-aware + no-jump / no-FOMC gate，放到真实 desk clean-room 之后，到底是 honest uplift，还是又一个靠砍样本换外观的过滤器？**

## 本轮做了什么
1. 再次实际运行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，确认当前全 desk 仍无 `due-now / overdue` lane，本轮切去 `Scout Seat` 合法。
2. 新增最小 clean-room 脚本：
   - `scripts/build_rank118_intraday_sign_asymmetry_clean_replication.py`
3. 固定只测 **1 条 archetype = `breakout_short`**，并把执行口径写死为：
   - `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
4. 把 `Rank 118` 的最小实现冻结成三臂：
   - `baseline`
   - `sign_gate_only`
   - `sign_gate_plus_blackout`
5. `sign gate` 的最小 ex-ante 口径：
   - 用每个 `15m slot` 的历史 `recent_ret_4 × forward_ret_4` 的滚动均值，作为最小 sign-asymmetry proxy；
   - 对当前 short 候选，仅当 `expected_next_dir = short` 时才允许 `sign_gate_only` 放行；
   - 再叠 `no_jump`（`jump_z <= 2.0`）和 `no-FOMC` blackout 形成 `sign_gate_plus_blackout`。
6. 生成 reader-facing / artifact 落点：
   - `reports/artifacts/scout_rank118_intraday_sign_asymmetry_15m/`
   - `reports/site/factors/scout_rank118_intraday_sign_asymmetry_15m/report.html`
   - `reports/site/reading/repo_scout/rank118_intraday_sign_asymmetry_clean_replication.html`
7. 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，把 `Rank 118` 收口为 `park / evidence pool`，并把下一顺位前推到 `Rank 119 / PSAR trailing role fail-safe`。

## 关键证据 / 验证
### 6 bps / side desk 级总览
- `baseline`：
  - `mean_total_return ≈ -3.48%`
  - `mean_trades ≈ 9.0`
  - `mean_retention = 100%`
  - `mean_avg_net_ret ≈ -0.37%`
  - `mean_false_follow_4bars ≈ 88.1%`
- `sign_gate_only`：
  - `mean_total_return ≈ -2.02%`
  - `mean_trades ≈ 3.0`
  - `mean_retention ≈ 31.0%`
  - `mean_avg_net_ret ≈ -0.98%`
  - `mean_false_follow_4bars ≈ 91.7%`
- `sign_gate_plus_blackout`：
  - `mean_total_return ≈ -1.48%`
  - `mean_trades ≈ 1.67`
  - `mean_retention ≈ 15.8%`
  - `mean_avg_net_ret ≈ -0.83%`
  - `mean_false_follow_4bars = 100%`

### 分资产读法
- `BTC`：gate 确实把总亏损压小，但更像少做单；`avg_net_ret` 没有变好到能说服 desk 升格
- `ETH`：`sign_gate_only` 只剩 1 笔且仍亏；`sign_gate_plus_blackout` 直接过滤到 0 笔
- `SOL`：两条 gate 都仍明显为负，且 `false_follow_4bars` 没有改善

### 训练 / 测试 gate 状态
- 三个资产在测试段 `predictor_sign != 0` 的比例都是 `100%`，所以这轮不是“gate 完全没触发”
- 真正的问题不是触发率，而是：**放行后的剩余 trades 质量没有提升，反而更差**

## 当前硬结论
**`Rank 118 = park / evidence pool`**。

翻成人话：
这条线在 `breakout_short` clean-room 里确实能把总亏损数字变小，但方式主要是**大幅砍单**，不是更诚实地减少坏单。`retention` 从 `100%` 直接掉到 `31% / 15.8%`，而 `avg_net_ret` 和 `false_follow_4bars` 都没有改善到值得 desk 保留主资源位的程度。

所以这轮最诚实的判断不是 `keep P1`，而是：
**把它归回 `P0 / evidence pool`，不要继续拿 bot3 主资源磨这条线。**

## 风险 / 边界
- 这轮只测了 `breakout_short`；它不等于 `Fib retest_long` 或 `EMA continuation` 上必然同样失败
- 但 desk 当前要求的是“1 次最小 clean replication 就先给 honest verdict”，而不是继续开第二、第三条 archetype 去救这条线
- 若未来要复活 `Rank 118`，必须先拿到一个更窄、更像真实 gate 的 conditional framing，而不是继续沿当前通用 shared gate 口径加码

## 下一步建议
- `Run 1 = EMA due-check only`
- 若仍 `waiting_not_due`：
  - `Run 2 = Rank 119 / PSAR trailing role fail-safe source intake`
  - 若 `Rank 119` guard-pass，再只给它 1 次最小 clean replication
- 不再继续默认给 `Rank 118` 额外预算，除非后面有人先把它改写成更窄、更真实的条件化问题

## Commit hash
- 未提交。
- 原因：repo 当前存在大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 118` clean replication 相关的最小文件，不适合混提。
