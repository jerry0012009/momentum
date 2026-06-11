# 2026-03-23 03:51 UTC · stale scout queue reset（Rank 125 / 112 / 111）

## 本轮先做了什么
- 已先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 已按 interrupt 规则检查当前可见 runner 状态：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_autopilot_status.json` -> `waiting_not_due`，未见 `stale / error / refresh 失步 / red-watch`
  - `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/hosted_pilot_refresh_last_run.json` -> `ok=true`，未见 hosted pilot blocking anomaly
- 因此本轮没有 interrupt，不能去碰已自动运行的 paper runner。

## 为什么本轮不继续在 Rank 125 / 112 / 111 里硬选一个
顶板当前 `Next 3` 还写着：
- 下一轮默认切到 `Rank 125 / Rank 112 / Rank 111` 中最有杠杆的一条

但回读这三条各自最近的 authoritative artifact / log 后，已经能确认：
- `Rank 125`：`keep_P1 / budget used`
- `Rank 112`：`keep_P1 / honest veto signal`，且已 `budget used`
- `Rank 111`：`keep_P1 / event-clock gate has honest signal`，且已 `budget used`

而 desk 自己写的规则又是：
> 若某个 `P1` 候选连续 2 轮没有层级变化、且没有新增 decisive evidence，默认退出 Scout 主资源位，切到下一 active Scout / fresh intake reserve。

所以当前真正过期的，不是这三条策略本身，而是顶板里还残留的旧队列指令。

## 本轮 desk-level 最小结论
### 1) `Rank 125 / 112 / 111` 这组旧队列，已经不该继续占默认 Run 1
它们都已经完成各自最后一刀最小检查：
- `Rank 125` 问清了成本 / 交易数稳定性，但不足升 `P2`
- `Rank 112` 问清了 basis 极端 veto 的 honest signal，但不足升 `P2`
- `Rank 111` 问清了 event-clock / timeout gate 的 honest signal，但不足升 `P2`

继续从三者里强行再选一个，只会把 bot3 拉回近义重复劳动。

### 2) 三者里，保留价值最高的是 `Rank 111`，但也只是 compare/evidence，不是默认 primary
按现有证据的边际价值排序：
1. `Rank 111`：对 `follow-up / timeout` 有最清楚的 honest signal，且读法最容易迁移到别的 family
2. `Rank 125`：shared veto/confirm 仍有一点保留价值，但增益更分散、trade retention 下滑更明显
3. `Rank 112`：basis 极端 veto 有料，但更窄、更像 breakout_short 的局部 overlay

但这只是 **evidence / compare 价值排序**，不是继续给默认预算的理由。

### 3) 当前更诚实的默认动作，应切到 `fresh intake reserve`
因为：
- `Rank 14b / 140 / 125 / 112 / 111` 全都已经形成稳定 desk 口径；
- 其中没有哪一条正处在“再补 1 刀就能从 `P1 -> park / P2 / P3`”的状态；
- 按顶板规则，主资源此时应回到 `fresh intake reserve`，而不是继续磨已 exhausted 的 active Scout。

## 轻量 scorecard（stale queue reset）
- `usefulness = medium`
- `time_stability = n/a（本轮未新跑稳定性，仅做 queue reset）`
- `cross_asset_stability = weak_to_medium（取决于具体候选；三者都不足 promote）`
- `cost_trade_stability = weak_to_medium（Rank 125 最明确，但仍不足 promote）`
- `deployability = low`

### hard-fail flags
- `no_pending_cheapest_decisive_cut_left`
- `all_three_are_budget_used_or_effectively_exhausted`
- `top_board_queue_is_stale`
- `none_is_one-step-away_from_P2_or_P3`

### recommended_action
- `Rank 111 = keep_P1`
- `Rank 125 = keep_P1`
- `Rank 112 = keep_P1`
- **desk-level next action = park stale queue, switch default Run 1 to fresh intake reserve**

### why_now
如果不先把顶板里的过期 queue reset 掉，后续 13 分钟轮次会继续在 `125 / 112 / 111` 之间假装还有一刀可做，造成系统性空转。

### main_weakness
这不是新增 replication，而是 desk routing 修正；它解决的是“下一轮该做什么”，不是直接产出新的 alpha verdict。

## 本轮对 TODO 顶板的最小建议写法
- 明确 `Rank 125 / 112 / 111` 都已 `budget used`
- 把 `Next 3` 从“继续三选一”改为：
  1. `Run 1 = fresh intake reserve（或当前最短 compare，前提是真能改 verdict）`
  2. `Run 2 = Rank 140 / Rank 111 作为 compare anchor，不再当默认 primary`
  3. `Run 3 = 若 fresh intake guard-pass，则只给 1 次最小 clean replication；否则再回 cheap decisive fallback`

## 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0351_stale-scout-queue-reset.md`
- 顶板：最小局部 reset `Next 3 bot3 runs`
