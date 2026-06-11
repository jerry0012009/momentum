# Strategy Review (bot2)

Time: 2026-03-23 03:17 UTC

## 本轮一句话判断
`Paper / 待开启自动运行` 继续为空；已自跑 paper runner 未见顶板定义的真实 interrupt。Scout 这边，`Rank 140` 已正式退出默认 primary，`Rank 143` 已 park，因此本轮应把主资源切到剩余 active 池里最靠前、且最近确有新增 evidence 的 **`Rank 14b`**，并只再给它 **1 次 cheapest decisive cut** 预算。

## 1) 必检：Repo / 最近日志 / cron
### Repo
- 分支：`master`
- 工作区：dirty（大量 modified + untracked 产物 / 页面 / 脚本）
- 结论：本轮只维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，不碰无关脏文件。

### 最近 `research/optimization_loop/`
- `2026-03-23_0314_rank140-active-compare-exit.md`
- `2026-03-23_0248_rank143-orb-phase-clean-replication.md`
- `2026-03-23_0220_rank143-orb-phase-intake.md`
- `2026-03-23_0207_rank142-cost-retention-cut.md`
- `2026-03-23_0151_rank142-pattern-gate-intake.md`

### 最近 `research/strategy_review/`
- `2026-03-23_0224_strategy-review.md`
- `2026-03-23_0135_strategy-review.md`
- `2026-03-22_2358_strategy-review.md`
- `2026-03-22_2314_strategy-review.md`
- `2026-03-22_2206_strategy-review.md`

### 当前 cron（desk 相关）
- `bot2-strategy-review-40m`：enabled，当前运行中
- `bot3-momentum-auto-opt-13m`：enabled，最近一轮 `error`（`TODO` 精确替换失配），当前再次运行中
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`
- `bot7-quant-digest-30m`：enabled，最近 `ok`
- `bot6-park-reframe-2h`：enabled，最近 `ok`
- `Rank32b live maintenance`：enabled，最近 `ok`

结论：
- 没有来自 `Paper / 正在自动运行` runner 的真实 interrupt；
- `bot3` 最近一轮的报错更像 **顶板文本漂移导致的 edit 失配**，不是 paper runner 异常；本轮先把顶板重新收紧到稳定口径，不把已自跑 paper 拉回 `Next 3`。

## 2) Desk 核心回答（authoritative）
### Paper / 待开启自动运行
- `empty`
- 当前没有任何 Scout 候选够格升到 `P3`

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`：host cron autopilot / 15m monitor + due refresh
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`：manual narrow paper lanes / 20m refresh
- `Rank 139`：independent hosted pilot runner
- `Rank 122`：paper sidecar / low-frequency monitoring

读法不变：以上都属于 background autonomous paper；无真实 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 时，不进入 `Next 3`。

### Scout 当前 active 排序与 P0~P4
1. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / current Scout primary / keep_P1 / evidence strengthened`
2. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / not default primary`
3. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / budget used`
4. `Rank 112 / basis dislocation short veto`
   - `P1 / weak candidate / evidence_pool / budget used`
5. `Rank 111 / abnormal-return event clock`
   - `P1 / evidence_pool / budget used`
6. `Rank 143 / ORB phase retest state-machine + score gate`
   - `P0 / park / evidence only`
7. `Rank 142 / hammer-engulf retest quality gate`
   - `P0 / park / evidence only`
8. `Rank 141 / bounce polarity not-shared gate`
   - `P0 / park`
9. `Rank 137 / Rank 138 / Rank 127`
   - `P0 / park / evidence pool`
10. `Rank 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. `Run 1 = Rank 14b` 的最后 1 次 cheapest decisive cut
   - 只回答：它到底只是“靠砍单换来少亏/局部小正 pocket”，还是能形成更干净的 shared long-veto 读法；若仍不能改层级，下一轮必须退出 primary。
2. `Run 2 = Rank 140 / Rank 125 / Rank 112 / Rank 111` 中当前最有杠杆的一条
   - 默认优先继续做能改变 `P1 -> park / keep_P1` 的 cheapest decisive cut。
3. `Run 3 = next P-level action / fresh intake reserve / cheap decisive fallback`
   - 继续遵循 `P2->P3 verdict > P1 一次便宜诚实检查 > fresh intake > tiny-live plumbing fallback`。

## 3) 为什么这轮要切到 Rank 14b
- `Rank 140` 在 `01:05 -> 01:18 -> 01:40 -> 03:14` 这一串动作后，最便宜且最能改 verdict 的问题已经基本问完；结论稳定在 `keep_P1 / active compare anchor / 不再作为默认 primary`。
- `Rank 143` 虽然一度接棒 primary，但 `02:48` 的最小 clean replication 已经把它正式打回 `P0 / park`。
- 剩余 active 池里，`Rank 14b` 是位置最靠前、且最近确实有新增 formalized evidence 的候选：
  - `6bps` 从 `-16.36bps` 改善到 `+3.80bps`
  - 但 `trade_retention=59.62%`
  - `ETH` 仍明显拖累
  - `10/15bps` 仍为负
- 这正符合 desk brief 对 `P1` 的纪律：可以再给 **1 次便宜诚实检查**，但不能无限续命。

## 4) 本轮对 TODO 顶板的实际改动
1. 保持 `Paper / 待开启自动运行 = empty`
2. 保持所有自跑 paper runner 只作背景资产，不进入 `Next 3`
3. 把 `Rank 14b` 升为当前 Scout primary
4. 保留 `Rank 140` 为 `active compare anchor / not default primary`
5. 明确 `Rank 143 / Rank 142` 均已回到 `P0 / park`
6. 把 `Next 3` 收紧为：`Rank 14b -> next active Scout -> fresh intake/cheap fallback`

## 5) 风险与不确定性
- `Rank 14b` 仍是 `P1`，不是 `P2`，更不是 `P3`；本轮只是把它拿来做最后一刀诚实检查，不是把它写成 paper launch 候选。
- `bot3` 最近一轮的 `TODO` edit 失配说明顶板文案不宜频繁做大段漂移；后续应继续保持最小局部改动。
- 若 `Rank 14b` 下一刀仍不能给出层级变化，下一轮必须切到 `Rank 125 / 112 / 111` 或 fresh intake reserve，不能再把同一 `P1` 写成 primary。
