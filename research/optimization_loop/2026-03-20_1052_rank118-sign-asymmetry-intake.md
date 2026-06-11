# 2026-03-20 10:52 UTC · Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate / source intake

## 本轮上下文
- 触发：bot3 13m desk auto loop
- Run 1 结果：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，仍为 `Paper Seat / EMA = running paper / waiting_not_due`
- 最近 due：美股 1d+1wk 约 9.1h；Crypto 1d+1wk 约 13.1h；A 股 lane 更晚
- `manual_narrow_paper_last_run_summary.json`：未见新的 `P3 status-changing event` 插队理由
- 顶板上一轮状态：`Rank 117` 已直接 `park / evidence pool`，因此本轮合法主动作必须回到 fresh intake，而不是回头续磨旧 `P1`

## 为什么这次选这个
当前 active Scout 的边际价值排序已经被顶板收紧成：`Rank 118 > Rank 119 > 旧 P1 evidence_pool > Rank 117 park > P3 continuity sidecar`。

这轮选 `Rank 118`，不是因为它已经最像下一条 paper candidate，而是因为它最像**值得给 1 次 clean replication 预算**的 fresh intake：
- 它直接服务当前三条主线共有的问题：15m follow-up 不该默认都按 continuation 放行；
- 它不是发明新 trigger，而是先把现有 trigger 收紧成 `direction-aware + regime-aware` 的 admission / veto 层；
- 它比 `Rank 119 / PSAR trailing role fail-safe` 更贴近当前 desk 的主阻塞，因为当前更缺的是更诚实的 follow-up gate，而不是 exit role 的额外澄清。

## 做了什么
1. 再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，确认 `EMA` 仍真实 `waiting_not_due`，没有伪 refresh。
2. 依据 `research/quant_digests/2026-03-20_0823_intraday-sign-asymmetry-jump-fomc-gate.md`，把该方向正式冻结为 **`Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate`**。
3. 完成两条轻量诚实守门：
   - `trade on`：只做既有 setup 的 direction-aware + regime-aware 放行门，不单独开仓；
   - `trade off`：若主要改善来自砍样本或事后挑 pocket，就直接 park。
4. 把 lookahead / leakage 约束写死：
   - `predictor_sign` 只能由 signal 当根及之前、滚动过去窗口的已完成 bar 估计；
   - `no-jump` 只能用 signal 前可见 jump proxy；
   - `no-FOMC` 只能用事先公开会议日程；
   - 后续 clean replication 必须统一到 `signal 当根及之前数据 + next-bar open + no-overlap`。
5. 产出 reader-facing artifact：
   - `reports/artifacts/literature/scout_rank118_intraday_sign_asymmetry_nojump_nofomc_source_intake_card.csv`
   - `reports/site/reading/repo_scout/rank118_intraday_sign_asymmetry_nojump_nofomc_source_intake.html`
6. 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，把当前 `Scout Seat` 主位和 `Next 3` 前推到 `Rank 118 clean replication next`。

## 当前硬结论
**`Rank 118 = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：这条线值得拿 **1 次最小 clean replication** 预算，但它当前只配先当现有 follow-up 的 `direction-aware + no-jump / no-FOMC` gate，不配单独升成新 alpha，也不配抢 `Live Seat`。

## 证据 / 验证
- 本轮最小验证不是重跑大回测，而是确认当前动作是否合法、且 source 是否过了两条诚实守门。
- `EMA due-check` 已再次如实返回：全 desk 当前没有 `due-now / overdue` lane，因此切去 `Scout Seat` 合法。
- digest 证据清楚支持这条线至少值得 intake：论文明确指出 crypto intraday relation 里 continuation 与 reversal 并存，且在 `no-jump / no-FOMC` 子样本中更强。
- 同时，这些证据也不足以直接升格：因为 desk 口径还没验证它在 `BTC/ETH/SOL 15m + next-bar open + no-overlap` 下，不是单纯靠砍样本换外观改善。

## 风险 / 边界
- 论文主口径偏 `5m -> hour`，落到 desk 的纯 `15m` 实现后，sign pocket 结构可能变化。
- `no-jump / no-FOMC` 很容易演化成“样本越来越少”的漂亮过滤器；下一轮 clean replication 必须重点盯 `trade_retention`。
- 这条线绝不能偷渡成全新的独立时段 alpha，只能先作为现有 setup 的 admission / veto gate。

## 下一步建议
- `Run 1 = EMA due-check only`
- 若仍 `waiting_not_due`：
  - `Run 2 = 只给 Rank 118 1 次最小 clean replication`
  - 固定 1 条 archetype（优先 breakout-short follow-up 或 fib_retest_long）
  - 统一比较 `baseline / sign_gate_only / sign_gate_plus_blackout`
- 若 clean replication 只显示“样本变少”，没有更诚实地降低 `false-follow / false-hold`，就直接 `park`
- 若在至少 2 个 symbol 上能改善且 retention 没塌，再补 1 个真正会改变级别的最小检查（默认优先 `成本 / 交易数稳定性`）

## Commit hash
- 未提交。
- 原因：repo 当前有大量与本轮无关的既有脏文件；本轮只安全写入了与 `Rank 118` source intake 直接相关的最小文件，不适合混提。
