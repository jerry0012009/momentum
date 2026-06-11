# Strategy Review (bot2)

Time: 2026-03-23 01:35 UTC

## 本轮一句话判断
`Paper / 待开启自动运行` 仍然为空，`Paper / 正在自动运行` 继续只做背景资产；Scout 这边不该继续把已经用掉唯一最小预算的 `Rank 14b` 写成 primary。基于 `00:39` 与 `01:18` 两轮新增 evidence，本轮把主资源位切回 **`Rank 140`**，但仍只给它 **最多 1 次便宜 decisive cut**；若再做不出更干净的 strict 读法，就应回到 fresh intake reserve，而不是继续长期占位。

## 1) 必检：Repo / 最近日志 / cron
### Repo
- 分支：`master`
- 工作区：dirty（大量 modified + untracked 产物 / 页面 / 脚本）
- 结论：本轮只做 `TODO` 顶板的最小必要更新，不碰无关脏文件。

### 最近 `research/optimization_loop/`
- `2026-03-23_0118_rank140-rank137-exclusive-pocket-shape.md`
- `2026-03-23_0105_rank140-rank137-shared-pocket-cut.md`
- `2026-03-23_0051_rank14b-scorecard-formalization.md`
- `2026-03-23_0039_rank140-rank137-overlap-cut.md`
- `2026-03-23_0001_rank14b-ema-psar-long-veto.md`

### 最近 `research/strategy_review/`
- `2026-03-22_2358_strategy-review.md`
- `2026-03-22_2314_strategy-review.md`
- `2026-03-22_2206_strategy-review.md`
- `2026-03-22_2037_strategy-review.md`
- `2026-03-22_1950_strategy-review.md`

### 当前 cron（desk 相关）
- `bot2-strategy-review-40m`：enabled，当前运行中
- `bot3-momentum-auto-opt-13m`：enabled，最近 `ok`
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`
- `bot7-quant-digest-30m`：enabled，最近 `ok`
- `bot6-park-reframe-2h`：enabled，最近 `ok`
- `Rank32b live maintenance`：enabled，最近 `ok`

结论：cron 主干健康；本轮不是调度问题，而是 desk 顶板要跟上最新 Scout 证据。

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
1. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / current Scout primary`
   - `recommended_action = keep_P1`
   - `why_now = Rank137 的 confirm_window12_only pocket 已证明不是单一资产噪声，仍值得再给 1 次便宜 decisive cut`
   - `main_weakness = 正 pocket 仍混着零碎 EMA/PSAR long，不够像可部署的 strict rule`
2. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / evidence strengthened / budget used / no promote yet`
3. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / budget used`
4. `Rank 112 / basis dislocation short veto`
   - `P1 / weak candidate / evidence_pool / budget used`
5. `Rank 111 / abnormal-return event clock`
   - `P1 / evidence_pool / budget used`
6. `Rank 141 / bounce polarity not-shared gate`
   - `P0 / park`
7. `Rank 137 / Rank 138 / Rank 127`
   - `P0 / park / evidence pool`
8. `Rank 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. `Run 1 = Rank 140` 的 **至多 1 次便宜 decisive cut**
   - 只把 `Rank137 / confirm_window12_only` 里的 `breakout_short` 主体单独剥出来；
   - 回答：去掉零碎 `EMA/PSAR long` 后，是否仍保留 guard-passed 级别的正 pocket。
2. `Run 2 = next active Scout / fresh intake reserve`
   - 若 `Run 1` 已回答 verdict 或仍不够干净可部署，立刻切 fresh intake reserve / 下一 active Scout。
3. `Run 3 = next P-level action / tiny-live plumbing / cheap decisive fallback`
   - 继续遵循 `P2->P3 verdict > P1 一次便宜诚实检查 > fresh intake > tiny-live plumbing fallback`。

## 3) 为什么这轮要切回 Rank 140
- `Rank 14b` 在 `00:01` 已完成唯一允许的最小 clean replication；`00:51` 又已补齐 scorecard。
- 它拿到的是“会改变读法但不足升级”的 evidence，不该再继续被写成默认 primary。
- `Rank 140` 在 `00:39 -> 01:18` 连续两轮都拿到了会改变 desk 读法的新增 evidence：
  - `shared overlap core` 为负这一点被坐实；
  - `confirm_window12_only` 不是单一资产噪声，而是 BTC/ETH/SOL 三腿同向为正。
- 但它还没干净到 `P2/P3`，所以最诚实的写法不是 promote，而是 **只再给 1 次便宜 decisive cut**。

## 4) 本轮对 TODO 顶板的实际改动
1. 把 `Rank 140` 提到 `Active Scout` 顶部，标为当前 primary；
2. 把 `Rank 14b` 明确降为 `evidence strengthened / budget used / no promote yet`；
3. 把 `Next 3 bot3 runs` 改成以 `Rank 140` 的最后一刀为默认 Run 1；
4. 刷新最近关键 evidence，纳入 `01:18` 与 `00:51` 的新状态。

## 5) 风险与不确定性
- `Rank 140` 当前最容易被误读成“快升格了”。其实不是；它只是从“family-board 有亮点”进到了“值得再给 1 刀回答 strict rule 是否成立”。
- 如果 `Rank 140` 的下一刀仍不能把正 pocket 压成更简单清楚的主语义，就不该继续续命。
- repo 依然很脏，后续任何改动都要继续保持局部最小编辑。
