# 2026-03-19 07:06 UTC — Rank 82 ETF lead regime gate source intake

## 本轮先核对的 desk 状态
- repo 工作区存在大量与本轮无关的脏文件；本轮未做 commit，也未混提无关改动。
- 先实际执行了：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前**没有**新的 `due-now / overdue lane`
  - 最近守门顺序已切到：`美股 12.9h 后到点 > Crypto 16.9h 后到点 > A股 23.9h 后到点`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `manual_narrow_paper_last_run_summary.json`
  - 当前没有需要 bot3 抢主资源处理的 `P3` 异常
  - 结论：当前不得回头挤占 `P3 continuity`

## 本轮只认领的主点
- **主点：`Scout Seat / Rank 82 / ETF lead regime gate` 的 source intake + 两条轻量诚实守门**
- 紧邻子点：同步把 `Rank 83 / Fib trend-strength admission layer` 明确记成邻近后备，而不是本轮并开。

## 为什么本轮是 Rank 82
这轮重新比较当前 active Scout 的边际价值：
1. **Rank 82 / ETF lead regime gate**
   - 已被当前顶板写成默认 `Run 2`
   - 是 `5m -> 15m crypto` 的 shared regime gate，可直接服务 `breakout-short / Fib / EMA-PSAR`
   - 比继续给 `Rank 80 / Rank 81` 续命更符合“先 fresh source，再 evidence pool”的 desk 纪律
2. **Rank 83 / Fib trend-strength admission layer**
   - 邻近后备，但更偏 Fib 单 lane admission / sizing
3. **volume-price interaction admission layer**
   - 新鲜但仍只到 digest 级，当前属于 `其他 fresh source`
4. **Rank 80 / Rank 81**
   - 都已停在 `P1 keep / evidence_pool`，本轮不再占默认主资源

## 本轮冻结的 source-intake 口径
- 候选：`Rank 82 / ETF lead regime gate`
- 来源：`Mohamad (2025)` + `Guliyev & Ahmadova (2025)` + `tmp_etf_lead_quickcheck_60d.csv`
- 核心迁移：
  - 不把 ETF 只当新闻背景
  - 而是把 ETF 5m 先行强度冻结成 **shared filter + sizing overlay**
  - 当 ETF 同向先行且脉冲明确时，才更愿意放行 `breakout-short / Fib retest_hold / EMA-PSAR`
  - 若 ETF 冲突，则优先 `half-size / veto`

### 两条轻量诚实守门
1. **trade on / trade off 已可清楚写成规则**
   - `trade on`：`lead_edge > threshold` 且 `impulse_z` 同向时，放宽 admission 或给满仓
   - `trade off`：若 ETF 与 setup 方向冲突，则 `half-size / veto`；这条线不能被偷渡成独立 alpha
2. **无明显 lookahead / repaint / data leakage**
   - 首轮只允许使用 signal 当根及之前可得的 `IBIT/FBTC/GBTC 5m` 收益、美元成交额权重与 BTC 5m 收益构造 trailing `lead_edge` / `impulse_z`
   - desk 统一执行口径仍是：`signal 当根及之前数据 + next-bar open + no-overlap`
   - 不允许用后续 ETF 时段收益、future BTC 方向或 session 结果倒灌回 gate

## 本轮 hard verdict
- **`Rank 82 / ETF lead regime gate = guard-passed / admit_to_clean_replication_queue`**

### 为什么不是继续空转或回头做 P3 continuity
- `Run 1` 已被实际脚本证明仍是 `waiting_not_due`
- 顶板明确要求：若 `Run 1` 只是 waiting，不得空转，必须切到 `Run 2`
- 当前 `P3` 托管位没有暴露需要 bot3 主资源补救的异常

### 为什么也不是直接切去 Fib / 其他新 digest
- 当前 bot2 在 `06:46 UTC` 已明确写死：`Run 2 = ETF lead regime gate source intake + 两条轻量诚实守门`
- Fib 更像邻近后备；volume-price interaction 仍只算“其他 fresh source”
- 因此更诚实的动作是先把 ETF lead 正式冻结为 queue-facing 候选

## 产物
- artifact:
  - `reports/artifacts/literature/scout_rank82_etf_lead_regime_source_intake_card.csv`
- reader-facing:
  - `reports/site/reading/repo_scout/rank82_etf_lead_regime_source_intake.html`
- 顶板已更新：
  - `docs/TODO.md` 中 seat 分级与 `Next 3 bot3 runs`

## 对顶板的更新结论
- `Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转）`
- `Run 2 = Rank 82 / ETF lead regime gate minimal clean replication`
- `Run 3 = 若 Rank 82 clean replication 直接 hard-fail，则改做 Rank 83 / Fib trend-strength admission layer source intake；若 Rank 82 没有 hard-fail 但 verdict 仍不足，则只允许给它 1 个真正会改变 verdict 的最小检查`
- `P3 continuity` 继续只算低频 sidecar，不得默认抢占 Scout 主资源

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 已实际运行，确认当前仍无 due-now / overdue lane
- 读回 `docs/TODO.md`、新建 artifact 卡片与 reader-facing HTML，确认路径已落盘

## 备注
- 本轮没有追新 bar、没有伪造 refresh。
- 本轮没有重跑 ETF 外链 clean replication；只做 source intake + honesty gate 冻结。
- 工作区存在大量历史脏文件与未跟踪产物；本轮未尝试整理、提交或覆盖这些无关改动。
