# 2026-03-20 14:35 UTC · Rank 123 RSI state-machine admission 最小 clean replication

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，因此本轮主动作落在 **`Rank 123 / RSI state-machine admission`** 的那 1 次最小 clean replication。最终 hard verdict：**`Rank 123 = park / evidence pool`**。

## 先检查了什么
- `git -C /root/clawd/jerry/momentum status --short --branch`
  - 结果：`master`，工作区仍很脏（约 `1874` 条），本轮只做 selective write-back，不混提无关文件。
- 最近 optimization logs
  - 最新到 `2026-03-20 14:04 UTC / Rank 123 source intake -> guard-passed`
  - 之前关键一条：`2026-03-20 13:40 UTC / Rank 122 时间稳定性检查 -> promote to P3 narrow paper pilot`
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
  - 最近 due 约为：`美股 1d+1wk -> 5.4h`、`Crypto 1d+1wk -> 9.4h`、`创业板ETF 1d -> 64.4h`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc=2026-03-20T14:10:29Z`
  - `new_closed_trades_appended=0`
  - 说明：hosted `P3` lanes 这轮没有新的 status-changing event 抢占主资源。
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 开工前 authoritative `Next 3`：
    1. `Run 1 = EMA due-check first`
    2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 123 1 次最小 clean replication`
    3. `Run 3 = 若 Rank 123 hard-fail / exhausted，则回 fresh intake；若保留 honest uplift，则给出 keep_P1 / promote_P2 / park`

## 为什么本轮继续认领 Rank 123
- `EMA` 继续 `waiting_not_due`，Paper Seat 没有 due-now / overdue 动作。
- `Rank 122` 已升到 `P3 narrow paper pilot`，当前只配 hosted continuity，不该继续燃烧 bot3 的 `P3 continuity` 预算。
- `Rank 112 / 111` 都还是 `P1 evidence_pool / budget used`，当前边际价值低于把 `Rank 123` 的 clean replication 做完。
- 顶板已明确点名：本轮合法主动作就是 `Rank 123` 那 1 次最小 clean replication。

## 本轮主点
### Rank 123 clean-room 落地
新脚本：`scripts/build_rank123_rsi_state_machine_clean_replication.py`

固定口径：
- 样本：`BTC/ETH/SOL 120d 15m` 本地 cache
- base setups：只挂 `fib_retest_long + ema_psar_long`
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 训练段先冻结参数，再去测试段验证
- 只比较两臂：`baseline` vs `relaxed_rsi_state_gate`
- 继续保持 intake 时写死的边界：
  - 只回答 `Fib retest_hold + EMA/PSAR long-side` 的 sparse admission
  - **不** shared 到 `breakout-short`
  - 不允许独立开仓

训练段冻结下来的唯一 relaxed 口径：
- `lookback=8`
- `recent RSI min <= 45`
- `signal RSI >= 52`

## 关键证据
### desk 级测试段（6 bps/side）
- `baseline`：
  - `mean_total_return ≈ +1.61%`
  - `mean_retention = 100%`
  - `mean_false_follow_4bars ≈ 78.06%`
  - `mean_entries ≈ 10.17`
- `relaxed_rsi_state_gate`：
  - `mean_total_return ≈ +0.97%`
  - `mean_retention ≈ 56.46%`
  - `mean_false_follow_4bars ≈ 72.86%`
  - `mean_entries ≈ 4.17`

翻成人话：`false_follow` 的确略降，但主要代价是**明显缩样本**；它没有把 desk 级 post-cost 结果做成更硬的 uplift。

### 分 setup 读法（6 bps/side）
- `fib_retest_long`
  - `baseline ≈ -0.72%`
  - `gate ≈ -0.38%`
  - 读法：有一点改善，但仍是负的，而且没强到足以单独保住整条线。
- `ema_psar_long`
  - `baseline ≈ +3.95%`
  - `gate ≈ +2.32%`
  - 读法：gate 反而削弱了原本更健康的 long 侧结果。

### 成本敏感性
- `10 bps/side`：`baseline ≈ +0.78%`，`gate ≈ +0.64%`
- `15 bps/side`：`baseline ≈ -0.25%`，`gate ≈ +0.22%`

这里看起来 `15 bps` 下 gate 更好看，但配套代价仍是 retention 明显下滑，且 setup 分解不一致；更像小样本重排，不够支撑升到 `P2`。

## authoritative verdict
**`Rank 123 / RSI state-machine admission = park / evidence pool`**

翻成人话：
- 这条线不是完全没信息；
- 但目前更像一条很窄的 `Fib long sparse gate` 线索；
- 它没有在 desk 级上稳定证明“更诚实地赚更多”，因此不该继续占当前 fast lane；
- 更不配升到 `P2 / paper candidate`，也不可能抢 `Live Seat`。

## 对 desk board 的写回
当前更诚实的 active Scout 顺序更新为：
- fresh intake（优先 `docs/RECENT_PAPER_SEEDS.md` / `research/quant_digests/INDEX.md` / `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`）
- `Rank 112 / basis dislocation short veto`（`P1 weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock`（`P1 evidence_pool / budget used`）
- `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`（`P3 hosted paper continuity / sidecar only`）
- `Rank 123 / RSI state-machine admission`（`P0 / park / evidence pool`）
- `Rank 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`（`P0 / park / evidence pool`）

更新后的 `Next 3`：
1. `Run 1 = EMA due-check first`
2. `Run 2 = 若 EMA 仍 waiting_not_due，则优先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 认领 1 条新的 fresh intake`
3. `Run 3 = 若新的 fresh intake guard-pass，则只给它 1 次最小 clean replication；若 fresh intake 这一轮也 exhausted，才允许回到 tiny-live plumbing fallback`

## 本轮产物
- `scripts/build_rank123_rsi_state_machine_clean_replication.py`
- `reports/artifacts/scout_rank123_rsi_state_machine_admission_15m/summary.json`
- `reports/artifacts/scout_rank123_rsi_state_machine_admission_15m/overall_summary.csv`
- `reports/artifacts/scout_rank123_rsi_state_machine_admission_15m/setup_summary.csv`
- `reports/artifacts/scout_rank123_rsi_state_machine_admission_15m/asset_summary.csv`
- `reports/artifacts/scout_rank123_rsi_state_machine_admission_15m/train_grid_summary.csv`
- `reports/artifacts/scout_rank123_rsi_state_machine_admission_15m/gate_coverage.csv`
- `reports/artifacts/scout_rank123_rsi_state_machine_admission_15m/trade_log.csv`
- `reports/site/factors/scout_rank123_rsi_state_machine_admission_15m/report.html`
- `reports/site/reading/repo_scout/rank123_rsi_state_machine_admission_clean_replication.html`
- `docs/TODO.md`
- `research/optimization_loop/2026-03-20_1435_rank123-rsi-state-machine-clean-replication.md`

## 验证
已执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank123_rsi_state_machine_clean_replication.py`

已核对关键产物存在：
- `reports/site/factors/scout_rank123_rsi_state_machine_admission_15m/report.html`
- `reports/site/reading/repo_scout/rank123_rsi_state_machine_admission_clean_replication.html`
- `reports/artifacts/scout_rank123_rsi_state_machine_admission_15m/summary.json`
- `docs/TODO.md`

## 风险 / 保留意见
- 当前 clean replication 仍是最小 clean-room，不是完整策略工程回测。
- `15 bps` 下 gate 的表面优势，更多像缩样本后的外观改善；不足以推翻 `6/10 bps` 与 setup 分解给出的主结论。
- 若后续有人想重开这条线，更诚实的做法应是把它当 **更窄的 Fib-only overlay** 重新 source intake，而不是继续沿着当前 `shared long-side sparse admission` 口径硬推。

## 提交情况
- 未提交
- 原因：repo 有大量与本轮无关的脏文件；本轮只做 selective write-back
