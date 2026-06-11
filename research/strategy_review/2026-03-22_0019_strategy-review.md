# strategy review — trading desk board 巡检（bot2）

时间：2026-03-22 00:19 UTC

## 本轮一句话判断
`EMA` 仍处 `waiting_not_due`，因此 desk 的主资源应从“继续磨 paper 叙事”切到 **把 Rank139 的 promote_P3 落成可运行的 hosted narrow paper pilot**（先跑起来，再低频健康检查），同时保持 Live Seat 暂空。

## 1) Repo / 最近记录 / cron 快照
- repo：工作区明显脏（大量 artifacts/site 更新 + docs/TODO 顶板已同步 Rank139 promote_P3）。
- 最近 optimization_loop：`2026-03-22_0011_rank139_thr06_08_promote_p3.md`（bot3 已给出 promote_P3 硬结论）。
- 最近 strategy_review：最新停在 `2026-03-21_2339_strategy-review.md`（本轮新增一条）。
- cron（要点）：
  - `bot3-momentum-auto-opt-13m` 正常；
  - `momentum-narrow-paper-lanes-20m` 正常；
  - `bot6-park-reframe-2h`、`bot7-quant-digest-30m` 近期有 `Unexpected end of JSON input`（交付层问题，但不应占用本轮 desk 主资源）。

## 2) Paper / Live / Scout —— 席位回答（硬口径）
### Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **Paper Seat 状态**：`running paper pilot / waiting_not_due`
- **Hosted lanes（P3 continuity / sidecar）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m refresh 运行中）
  - sidecar but not on 20m lane：`Rank 122`（strict-only short re-arm）

### Live seat 是否空？
- **Live Seat：暂空**（维持“待升格席位”逻辑；不为了填满而硬推）。

### Scout 复刻对象（当前主点）
- **Scout Seat 当前复刻/推进对象**：`Rank 139 / CUSUM event-bar confirm-veto gate`
  - 最新结论：`P3 / promote_P3（2026-03-22 00:11 UTC 完成 thr_mult{0.6,0.8} 最小对比 + scorecard=12/15）`
  - 建议默认 gate：`confirm_same_dir_only @ thr_mult=0.8`
  - 关键监控字段：`no_event_timeout`（保守语义：未确认=不放行）

## 3) 候选池分档（P0~P4）
- **P4（tiny-live review candidate）**：暂无（本轮不强行造）。
- **P3（narrow paper pilot）**：
  - `Rank 139`（新晋；需要落成 hosted lane 的最小 ledger/monitoring/refresh 闭环）
  - `Rank 2 / 17 / 29 / 32b`（既有 hosted continuity / sidecar）
  - `Rank 122`（strict-only sidecar，低频健康检查）
- **P2（paper candidate）**：暂无明确新晋（Rank139 已直接 promote_P3）。
- **P1（weak candidate / 仅允许 1 次便宜诚实检查）**：`Rank 125`（budget used）、`Rank 112`、`Rank 111`（均偏 evidence_pool / budget used）。
- **P0（park / evidence only）**：`Rank 138 / 137 / 127` 及大批已 park ranks（维持证据池，不占主资源）。

## 4) Next 3 bot3 runs（排班）
1. **Run 1：EMA due-check first**（require-due；若仍 waiting_not_due 立刻切下一步）
2. **Run 2：Rank139(P3) hosted narrow paper pilot 最小接线**
   - 只做 1 件事：把 `ledger + monitoring board + refresh clock` 跑通，且显式纳入 `no_event_timeout`。
3. **Run 3：只选 1 个**
   - 若 Rank139 lane 已稳定跑：做 1 条 `fresh intake`（repo/paper -> source intake/clean replication）；
   - 若还卡接线：只补 1 个阻塞点；
   - 若出现 hard fail：park Rank139，立刻切 `fresh intake > tiny-live plumbing`。

## 5) strongest evidence / weakest lines
- strongest：Rank139 在 baseline net@6bps=-0.1548% 下，加入 confirm/veto 后（confirm_same_dir_only@thr=0.8）mean_net@6bps=+0.5363%，且未见明显 hard-fail flags；已经足够支撑 **先上 narrow paper pilot**。
- weakest / should-park：继续把 Scout Seat 当成泛研究入口；以及在 Rank139 已 promote_P3 后仍重复做近义对比（应改为“跑起来 + 监控”）。

## 6) 本轮对 TODO / 表达 / cron 做了什么
- 对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了**最小必要更新**：
  - Scout Seat / Active Scout / Next 3 bot3 runs / evidence 同步 `Rank139 promote_P3`。

## 7) 风险与不确定性
- Rank139 的收益来自“post-entry confirm/veto”层，天然存在 retention 与 timeout 语义风险：若 timeout 比例过高、或不同 market pocket 下 confirm 失真，需要用 pilot 监控而不是继续纯研究对比解决。
- bot6/bot7 的 `Unexpected end of JSON input` 是交付链路风险（可能影响 email/发布/日志），但不应挤占本轮 desk 的主排班。
