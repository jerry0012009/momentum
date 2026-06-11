# 2026-03-19 08:35 UTC — Rank 85 fresh pullback → reclaim re-arm gate source intake

## 本轮先核对的 desk 状态
- repo 工作区存在大量与本轮无关的脏文件；本轮未做 commit，也未混提无关改动。
- 先实际执行了：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前**没有**新的 `due-now / overdue lane`
  - 最近守门顺序：`美股约 11.4h 后到点 > Crypto 约 15.4h 后到点 > 创业板ETF 1d 约 22.4h 后到点`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-19T08:35:53Z`
  - `new_closed_trades_appended=0`
  - 结论：当前没有需要 bot3 抢主资源处理的 `P3` 异常

## 本轮只认领的主点
- **主点：`Scout Seat / Rank 85 / fresh pullback → reclaim re-arm gate` 的 source intake + 两条轻量诚实守门**
- 紧邻子点：同步把 `Rank 84 / volume-price interaction admission layer` 明确记成邻近后备，而不是本轮并开。

## 为什么本轮是 Rank 85
这轮重新比较当前 active Scout 的边际价值：
1. **Rank 85 / fresh pullback → reclaim re-arm gate**
   - `08:27/08:28 UTC` 顶板已把 `Rank 83` 明确压回 `park / evidence_pool`
   - 当前默认主资源位已切到 `Rank 85 > Rank 84 > 其他 fresh source`
   - 它直接服务三条主线共同缺的 `armed → reclaim → reset` 再上膛问题，比继续给 `Rank 82 / 80 / 81` 续命更符合当前 desk 纪律
2. **Rank 84 / volume-price interaction admission layer**
   - 邻近后备，但本轮不应越序抢跑
3. **Rank 83 / Rank 82 / Rank 80 / Rank 81**
   - 当前都不再占默认 fast-lane：`Rank 83` 已 park；`Rank 82 / 80 / 81` 只留在 `P1 evidence_pool`

## 本轮冻结的 source-intake 口径
- 候选：`Rank 85 / fresh pullback → reclaim re-arm gate`
- 来源：`Adamski13/trend-pullback-system`
- 核心迁移：
  - 不把 continuation / retest 的再进场写成“信号还亮着就继续追”
  - 而是把 repo 里的 `armed → reclaim → reset` 状态机冻结成三条主线共用的 `re-arm` 资格层
  - 当前 desk 迁移优先偷的是状态机语义，不是日线 `200 SMA + 21 EMA` 参数本身

### 两条轻量诚实守门
1. **trade on / trade off 已可清楚写成规则**
   - `trade on`：
     - `armed_long = bias_long 且 close < ema21`（或触达 Fib 回踩区后落回 EMA 下方）
     - `trigger_long = armed_long 且 close > ema21`
     - `armed_short = bias_short 且 close > ema21`
     - `trigger_short = armed_short 且 close < ema21`
     - 一旦触发，`armed_*` 立即清空；没有新的 fresh pullback，不允许连续再进
   - 首轮 desk 迁移只把它当 shared `re-arm gate`：base setup 继续负责方向与价位，re-arm gate 只回答“有没有资格再打一枪”
2. **无明显 lookahead / repaint / data leakage**
   - repo 的状态机是因果式：先记录一次 fresh pullback，再等 reclaim，触发后立即 reset
   - 首轮只允许使用 signal 当根及之前可得的 EMA / Fib / ATR 与 pullback extreme
   - desk 统一执行口径仍是：`signal 当根及之前数据 + next-bar open + no-overlap`
   - 不允许把后续 continuation 结果、未来 swing 确认或日线回测结论倒灌回当前 re-arm 状态

## 本轮 hard verdict
- **`Rank 85 / fresh pullback → reclaim re-arm gate = guard-passed / admit_to_clean_replication_queue`**

### 为什么不是继续空转或回头做 P3 continuity
- `Run 1` 已被实际脚本证明仍是 `waiting_not_due`
- 顶板明确要求：若 `Run 1` 只是 waiting，不得空转，必须切到 `Run 2`
- 当前 `P3` 托管位没有暴露需要 bot3 主资源补救的异常

### 为什么也不是先做 Rank 84
- 当前板上明确的 active Scout 顺序已经收口为 `Rank 85 > Rank 84 > 其他 fresh source`
- `Rank 85` 比 `Rank 84` 更直接回答三条主线共同缺的 `re-arm` 问题，本轮不应越序

## 产物
- artifact:
  - `reports/artifacts/literature/scout_rank85_fresh_pullback_rearm_source_intake_card.csv`
- reader-facing:
  - `reports/site/reading/repo_scout/rank85_fresh_pullback_rearm_source_intake.html`
- 顶板已更新：
  - `docs/TODO.md` 中 Scout 分级与 `Next 3 bot3 runs`

## 对顶板的更新结论
- `Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转）`
- `Run 2 = 若 Rank 85 已 guard-passed 且 EMA 仍 waiting_not_due，则只给它 1 次最小 clean replication`
- `Run 3 = 若 Rank 85 clean replication 直接 hard-fail / park，则改做 Rank 84 / volume-price interaction admission layer source intake；若 Rank 85 未硬 fail 但 verdict 仍不足，则只允许给它 1 个 truly verdict-changing 的最小检查`
- `P3 continuity` 继续只算低频 sidecar，不得默认抢占 Scout 主资源

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 已实际运行，确认当前仍无 due-now / overdue lane
- 读回 `docs/TODO.md`，确认最新 seat 分级与 `Next 3` 已写回
- 读回 intake artifact 与 reader-facing HTML，确认路径已落盘

## 备注
- 本轮没有追新 bar、没有伪造 refresh。
- 本轮没有重跑 clean replication，只做 source intake + honesty gate 冻结。
- 工作区存在大量历史脏文件与未跟踪产物；本轮未尝试整理、提交或覆盖这些无关改动。
