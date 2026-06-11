# 2026-03-20 09:10 UTC · Rank 115 / same-clock intraday RVOL volume gate source intake

## 本轮结论
- `Run 1 / EMA due-check first` 已实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：全 desk 继续 `waiting_not_due`
  - 美股 `1d+1wk -> 2026-03-20 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-21 00:00 UTC`
  - 创业板ETF `1d -> 2026-03-23 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T09:03:58Z` = `new_closed_trades_appended=0`
- 因而本轮合法主动作回到 `fresh intake`
- 重新比较 active Scout / fresh source 边际价值后，本轮正式冻结：
  - **`Rank 115 / same-clock intraday RVOL volume gate`**
- 当前 hard verdict：
  - **`guard-passed / admit_to_clean_replication_queue`**

## 为什么这轮选 Rank 115
相对当前允许动作：
1. `Rank 112 / basis dislocation short veto`：已是 `P1 weak candidate / evidence_pool / budget used`
2. `Rank 111 / abnormal-return event clock`：已是 `P1 evidence_pool / budget used`
3. `Rank 114 / pullback -> two-sided breakout window verdict`：上一轮已压回 `P0 / park / evidence pool`
4. fresh source 里，`2026-03-20 08:51` 的 same-clock RVOL 同时满足：
   - repo-based
   - 直接服务 `5m/15m crypto`
   - 已有 Binance 公共数据快检
   - 修的是当前多条 setup 共用的 volume gate honest measurement，而不是再造一个新 alpha

所以它是本轮最便宜、最可能改变下一轮 desk judgment 的 fresh intake。

## 本轮完成内容
### 1. Source intake + 两条轻量诚实守门
冻结口径：
- 它**不是独立 alpha**，也不是新参数模板
- 它只回答现有 setup 的 `volume confirm / dry-down` 该不该放行
- 做法是把 `rolling RVOL` 改成 **`same-clock RVOL`**：当前 bar 的 volume 只和历史同一 `HH:MM` 的已完成 bar 比
- 可挂到：
  - `breakout-short follow-up`
  - `Fib retest_hold`
  - `EMA/PSAR volume gate`
- 但都只能先做 shared confirmation layer，不能单独开仓

### 2. Honesty gate
已写死：
- `slot_rvol` 只能用 signal 当根及之前、同 symbol、同 `HH:MM` 的历史已完成 bar 构造
- 禁止拿未来同 slot 均量回填
- 下一轮 clean replication 强制统一到：
  - `next-bar open`
  - `no-overlap`
- 阈值与 lookback 只能在训练段冻结，再到测试段验证
- 若事件窗（如 `jump / FOMC`）打穿 slot baseline，必须如实标 `blackout / excluded`

## 新增产物
- `reports/artifacts/literature/scout_rank115_same_clock_intraday_rvol_source_intake_card.csv`
- `reports/site/reading/repo_scout/rank115_same_clock_intraday_rvol_source_intake.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 已追加本轮 authoritative write-back

## 当前 desk 写回
- `Paper Seat = EMA / 创业板ETF 1d primary anchor / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 顺序更新为：
  - `Rank 115 / same-clock intraday RVOL volume gate`（`P1 / guard-passed / clean replication next`）
  - `Rank 112 / basis dislocation short veto`（`P1 weak candidate / evidence_pool / budget used`）
  - `Rank 111 / abnormal-return event clock`（`P1 evidence_pool / budget used`）
  - `Rank 114 / pullback -> two-sided breakout window verdict`（`P0 / park / evidence pool`）
  - `Rank 113 / alpha-beta abstain / profit-window`（`P0 / park / evidence pool`）

## Next 3
- `Run 1 = EMA due-check first`
- `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 115 1 次最小 clean replication`
- `Run 3 = 若 Rank 115 clean replication hard-fail / exhausted，则回 fresh intake（优先 RECENT_PAPER_SEEDS / quant_digests / validated shortlist）；只有 fresh intake 也 exhausted 后，才允许 tiny-live plumbing fallback`

## 最小验证
- 已实际运行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 `require-due` 等待态（退出码 `2`），符合当前 desk 状态
- 已生成 reader-facing 页面与 CSV artifact
- 未处理 git 工作区里与本轮无关的大量脏文件；本轮只做 selective write-back
