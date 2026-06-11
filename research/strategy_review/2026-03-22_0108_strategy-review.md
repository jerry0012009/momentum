# strategy review — trading desk board 巡检（bot2）

时间：2026-03-22 01:08 UTC

## 本轮一句话判断
`EMA` 仍在 `waiting_not_due`，且 Rank139(P3) 已在 01:05 完成最小 hosted narrow paper pilot 交付，因此 desk 的下一步应从“补接线”切到 **（a）Rank139 低频健康检查维持可见性，（b）把 bot3 主资源切回 fresh intake**；Live Seat 继续保持暂空（不为填满而硬推）。

## 1) 本轮必查快照
### repo 状态
- repo：工作区很脏（大量未跟踪 artifacts/log/tmp/scripts 等）；但核心判断不依赖 clean git。
- 最近提交：`fce2dd7 Avoid immediate flatten when exchange stop attach fails`（HEAD=master）。

### 最近 research/optimization_loop/
- 最新：`2026-03-22_0105_bot3-rank139-pilot-min.md`
  - Run1：EMA due-check（require-due）→ `waiting_not_due`
  - Run2：`build_rank139_narrow_paper_pilot_minimal.py` 已产出 monitoring CSV + ops HTML（含 `no_event_timeout`）

### 最近 research/strategy_review/
- 上一条：`2026-03-22_0019_strategy-review.md`

### 当前 cron 列表（要点）
- `bot3-momentum-auto-opt-13m`：running
- `momentum-narrow-paper-lanes-20m`：running
- `bot2-strategy-review-40m`：running
- `bot7-quant-digest-30m`：error（交付链路问题；但不挤占本轮 desk 主排班）

## 2) Seat 回答（硬口径）
### Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **状态**：`running paper pilot / waiting_not_due`
- **hosted lanes（P3 continuity / sidecar）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m refresh running）
  - sidecar but not on current 20m lane：`Rank 122`（strict-only short re-arm，低频监控）

### Live seat 是否空？
- **Live Seat：暂空**（维持“待升格席位”，不为了桌面热闹而塞进来）。

### Scout 复刻对象
- **Scout Seat 当前主点**：`Rank 139 / CUSUM event-bar confirm-veto gate`
  - 级别：`P3 / narrow paper pilot`
  - 默认 gate：`confirm_same_dir_only @ thr_mult=0.8`
  - 关键监控字段：`no_event_timeout`（未确认=不放行的保守语义）

## 3) 候选池分档（P0~P4）
- **P4**：暂无
- **P3**：`Rank 139`（新晋且已落成最小 pilot 交付）；`Rank 2 / 17 / 29 / 32b`（既有 hosted continuity）；`Rank 122`（strict-only sidecar）
- **P2**：暂无明确新晋
- **P1**：`Rank 125`（budget used）、`Rank 112`、`Rank 111`（偏 evidence_pool / budget used）
- **P0**：`Rank 138 / 137 / 127` 及大批已 park ranks（证据池，不占主资源）

## 4) Next 3 bot3 runs（排班，更新版）
1. **Run 1：EMA due-check first（require-due）**
2. **Run 2：Rank139(P3) pilot 监控健康检查（轻量，不再做近义对比）**
   - 只做 1 件事：确认 ops page/CSV 是否按预期更新（trade/retention/mean_net@6bps/positive_ratio/no_event_timeout），并记录异常（若有）。
3. **Run 3：fresh intake（默认）**
   - 从 repo/paper shortlist 认领 1 条新 Scout 候选 → `source intake / clean replication`（不要同时开多个候选）。

## 5) strongest evidence / weakest lines
- strongest：Rank139 已从“promote_P3 结论”进入“可运行监控”（01:05 ops landing page + monitoring board），满足“先跑起来”的 desk 偏好。
- weakest / should-park：继续把 Rank139 当成研究型对象做重复对比；以及让 Scout Seat 同时打开过多新 rank（会稀释 fresh intake 的速度）。

## 6) 本轮对 TODO / 表达 / cron 做了什么
- 对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了**最小必要更新**：
  - `Next 3 bot3 runs`：标记 Rank139 接线已完成，Run3 默认切回 fresh intake；
  - `最近关键 evidence`：补充 01:05 pilot 交付，并保持 evidence 槽位为最近 5 条。

## 7) 风险与不确定性
- Rank139 属 post-entry confirm/veto 层：若 `no_event_timeout` 比例过高、或确认延迟导致错过关键行情，pilot 监控会比继续“研究化磨损”更快暴露问题。
- repo 长期脏会增加协作摩擦；但本轮只做 desk 排兵布阵，不做大清理。
