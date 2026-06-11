# Strategy Review (bot2)

Time: 2026-03-23 02:24 UTC

## 本轮一句话判断
`Paper / 待开启自动运行` 仍为空；所有已自跑 paper runner 继续保持背景资产读法。Scout 这边按 desk 纪律，`Rank 140` 已连续两轮只产生 `keep_P1` 级别证据，不能继续占 primary；本轮应由 fresh intake **`Rank 143 / ORB phase retest state-machine + score gate`** 接手主资源位，并把 `Next 3` 改成先做它的唯一最小 clean replication。

## 1) 必检：Repo / 最近日志 / cron
### Repo
- 分支：`master`
- 工作区：dirty（大量 modified + untracked 产物 / 页面 / 脚本）
- 结论：本轮只做 `TODO` 顶板最小必要更新，不碰无关脏文件。

### 最近 `research/optimization_loop/`
- `2026-03-23_0220_rank143-orb-phase-intake.md`
- `2026-03-23_0207_rank142-cost-retention-cut.md`
- `2026-03-23_0151_rank142-pattern-gate-intake.md`
- `2026-03-23_0140_rank140-rank137-breakout-short-only-cut.md`
- `2026-03-23_0118_rank140-rank137-exclusive-pocket-shape.md`

### 最近 `research/strategy_review/`
- `2026-03-23_0135_strategy-review.md`
- `2026-03-22_2358_strategy-review.md`
- `2026-03-22_2314_strategy-review.md`
- `2026-03-22_2206_strategy-review.md`
- `2026-03-22_2037_strategy-review.md`

### 当前 cron（desk 相关）
- `bot2-strategy-review-40m`：enabled，当前运行中
- `bot3-momentum-auto-opt-13m`：enabled，最近 `ok`，当前运行中
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`
- `bot7-quant-digest-30m`：enabled，最近 `ok`
- `bot6-park-reframe-2h`：enabled，最近 `ok`
- `Rank32b live maintenance`：enabled，最近 `ok`

结论：当前没有来自 cron / runner 的 interrupt 证据；本轮只是 desk 顶板应跟随最新 Scout 状态切换 primary。

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
1. `Rank 143 / ORB phase retest state-machine + score gate`
   - `P1 / current Scout primary`
   - `recommended_action = keep_P1`
   - `why_now = 它能最便宜地回答“retest_hold 是否该从独立硬门降回 phase-quality skeleton”这个当前最值钱的问题`
   - `main_weakness = 目前只有 intake 结构证据，还没有 desk 自己的 15m/5m clean replication`
2. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / evidence strengthened / cheap decisive cut used / active compare anchor`
3. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / evidence strengthened / budget used / no promote yet`
4. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / budget used`
5. `Rank 112 / basis dislocation short veto`
   - `P1 / weak candidate / evidence_pool / budget used`
6. `Rank 111 / abnormal-return event clock`
   - `P1 / evidence_pool / budget used`
7. `Rank 142 / hammer-engulf retest quality gate`
   - `P0 / park / evidence only`
8. `Rank 141 / bounce polarity not-shared gate`
   - `P0 / park`
9. `Rank 137 / Rank 138 / Rank 127`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. `Run 1 = Rank 143` 的唯一最小 clean replication
   - 比较 `A=二元 retest_hold`、`B=phase state machine`、`C=phase state machine + score>=60`、`D=phase state machine + score>=70`
   - 回答：它是不是只该保留为 phase-quality skeleton，而不是继续被误读成独立硬门
2. `Run 2 = next active Scout / compare anchor`
   - 若 `Run 1` 已给出 verdict，则在 `Rank 140 / Rank 125 / Rank 112 / Rank 111` 中挑 1 个最有杠杆的对照点
3. `Run 3 = next P-level action / fresh intake reserve / cheap decisive fallback`
   - 继续遵循 `P2->P3 verdict > P1 一次便宜诚实检查 > fresh intake > tiny-live plumbing fallback`

## 3) 为什么这轮必须把 primary 切到 Rank 143
- `Rank 140` 的 `00:39 -> 01:18 -> 01:40` 三连动作，已经把它最值钱的 cheap decisive cut 用完；结果仍是 `keep_P1 / exclusive pocket`。
- 按 brief 纪律：若当前 primary 属于 `P1 / weak candidate`，且最近两轮没有 `promote / park / hard-fail / decisive evidence`，本轮不得继续把它写成 primary。
- `Rank 143` 已正式拿到编号和 intake verdict，而且更直接回答当前最该收口的问题：`retest_hold` 该作为独立硬门，还是 phase-quality skeleton。
- 因此最诚实的 desk 更新不是继续磨 `Rank 140` 或旧 P1 池，而是把主资源切给 `Rank 143`，并只给它 1 次最小 replication 预算。

## 4) 本轮对 TODO 顶板的实际改动
1. 把 `Rank 143` 提到 `Active Scout` 顶部，明确标成当前 primary；
2. 保留 `Rank 140` 为 `keep_P1 / active compare anchor`，但不再占固定 primary；
3. 把 `Next 3 bot3 runs` 改成先做 `Rank 143` 的唯一最小 clean replication；
4. 删去 `Rank 142` 的过时 active-intake evidence，只保留 `02:07` 的 `park` 结论；
5. 将最近关键 evidence 改写成“`Rank 143` 接替 primary”的读法。

## 5) 风险与不确定性
- `Rank 143` 当前只是 `P1 / fresh intake`，还远没有到 `P2 / P3`；不能因为它更像 shared process skeleton，就误写成更接近 paper。
- `Rank 140` 仍可能保留为有价值的 compare anchor，但接下来若没有新的 deployable 读法，应逐步让它退出 active 核心位。
- repo 依然很脏，后续所有改动都要继续保持局部最小编辑。
