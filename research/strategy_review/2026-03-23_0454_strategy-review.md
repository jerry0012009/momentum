# Strategy Review (bot2)

Time: 2026-03-23 04:54 UTC

## 本轮一句话判断
本轮 desk 需要做的不是再改 `Paper`，而是把 `Scout` 顶板跟最新 decisive evidence 对齐：`Rank 145` 已完成 frozen-threshold A/B 且确认 **`keep_P1 / budget used / no promote`**，因此不应继续占默认 primary；当前最诚实的首位应切到 **`Rank 144`**，并只保留 **1 次最小 clean replication** 预算。

## 1) 必检：repo / 最近日志 / cron / runner 状态
### Repo
- `git status` 显示 workspace 仍然很脏（大量 modified/untracked 研究产物、页面、脚本）。
- 本轮只维护 `docs/TODO.md` 顶部 desk board，不做额外 cleanup。

### 最近 `research/optimization_loop/`
- `2026-03-23_0438_rank145-frozen-threshold-ab.md`
- `2026-03-23_0423_rank145-equity-dd-throttle-intake.md`
- `2026-03-23_0404_rank144-vol-commonality-intake.md`
- `2026-03-23_0351_stale-scout-queue-reset.md`
- `2026-03-23_0329_rank14b-family-cut.md`

### 最近 `research/strategy_review/`
- `2026-03-23_0358_strategy-review.md`
- `2026-03-23_0317_strategy-review.md`
- `2026-03-23_0224_strategy-review.md`
- `2026-03-23_0135_strategy-review.md`
- `2026-03-22_2358_strategy-review.md`

### 当前 cron / timers（desk relevant）
- crontab 中仍有 `EMA paper autopilot / 15m`。
- systemd timer：
  - `momentum-rank32b-canary-phase6.timer` 正常推进，最近一次 `04:51:33 UTC`
  - `momentum-rank139-hosted-pilot-refresh.timer` 正常推进，最近一次 `04:38:03 UTC`

### Autonomous runner 抽查
- `EMA / PSAR raw alpha focus`
  - `ema_paper_autopilot_status.json` 仍存在，未见显式 `error/stale` 信号。
- `Rank 32b`
  - `phase6_status.json`：`last_run_utc = 2026-03-23T04:51:34Z`
  - `latest_evaluated_bar_time = 2026-03-23T04:45:00Z`
  - `mode = live_canary`
  - `system_health = warn_external_account`
  - 当前未见顶板定义的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 证据，因此**不触发 interrupt**。
- `Rank 139`
  - timer 正常；未见 hosted pilot blocking anomaly。

结论：`Paper / 正在自动运行` 仍然没有需要抢占 `Next 3` 的真实 interrupt。

## 2) 本轮 authoritative answers
### Paper / 待开启自动运行
- `empty`
- 本轮没有任何 Scout 候选升到 `P3`

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- `Rank 139`
- `Rank 122`

保持原口径：健康时都属于 background autonomous paper，不写进默认 `Next 3`。

### Scout 当前 active 排序与 P0~P4
1. `Rank 144 / intraday volatility commonality asymmetric follow-up gate`
   - `P1 / keep_P1 / fresh intake admitted / not-shared / breakout-short follow-up bias`
   - 当前只配 **1 次最小 clean replication**，不升 `P2`
2. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / budget used / no promote / 退出默认 primary`
3. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / budget used / 不再作为默认 primary`
4. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / 不再作为默认 primary`
5. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / budget used`
6. `Rank 112 / basis dislocation short veto`
   - `P1 / keep_P1 / budget used`
7. `Rank 111 / abnormal-return event clock`
   - `P1 / keep_P1 / compare 价值高于继续单独烧预算`
8. `Rank 143 / Rank 142 / Rank 141 / Rank 137 / Rank 138 / Rank 127 / Rank 136...113`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. `Run 1 = Rank 144`
   - 执行它唯一剩余的 **最小 clean replication**（冻结 commonality 阈值、做 BTC/ETH/SOL 分资产拆分、明确接到 breakout-short router 的前后置位置）
2. `Run 2 = Rank 140 compare anchor`
   - 只允许做 **最短 decisive compare**；若 `Rank 144` 不能升层，就回到 `Rank 140 / Rank 111` 这条 compare 链
3. `Run 3 = next fresh intake reserve / cheap decisive fallback`
   - 若没有新的 guard-pass reserve，则不要回头把 `Rank 145` 或其它 exhausted P1 再写成 primary

## 3) 为什么本轮必须改顶板
上一轮 `03:58` 复核时，`Rank 145` 仍是最新 fresh reserve；但 `04:38` 的 frozen-threshold A/B 已经给了**真正改变 routing 的 decisive evidence**：
- 它在本地共享代理上一次都没触发；
- 因此不能继续被写成 desk 默认 Run 1；
- 同时 `Rank 144` 在 `04:04` 已完成 fresh intake，且仍保留 1 次明确、可界定的最小 replication 预算。

如果此时不改顶板，就会让 `Next 3` 继续指向一个已被证伪为“当前不该继续占 primary”的 P1，这和 brief 的 desk routing 纪律冲突。

## 4) desk-level final call
- `recommended_action = update board minimally`
- `why_now = Rank 145 已拿到 decisive evidence 并退出默认 primary；Rank 144 是当前唯一还保留 1 次明确预算的 active Scout`
- `main_weakness = Rank 144 仍只是 proxy-level evidence，下一刀若不能改变层级，就也应退出默认 primary`

## 5) 本轮交付
- 已更新：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 本轮日志：`research/strategy_review/2026-03-23_0454_strategy-review.md`
