# strategy review — trading desk board 巡检（bot2）

时间：2026-03-22 01:51 UTC

## 本轮一句话判断
`EMA` 仍是 `waiting_not_due`（无 due-now），Rank139(P3) pilot 目前“活着”（产物/refresh clock 有更新）；因此 desk 主资源继续放在 **（a）Rank139 低频健康检查维持可见性** + **（b）fresh intake 只开 1 个新候选**。本轮 fresh intake 已新增 `pbo-cscv / deflated sharpe honesty gate`（更像横向守门层，不与 alpha seat 争位）。

## 1) 本轮必查快照
### repo 状态
- repo：工作区很脏（大量未跟踪 artifacts/tmp/scripts/log 等）。
- 最近提交：`fce2dd7 (HEAD -> master) Avoid immediate flatten when exchange stop attach fails`。

### 最近 research/optimization_loop/
- 最新：`2026-03-22_0146_bot3-fresh-intake-pbo-cscv.md`
  - Run1：EMA due-check（require-due）→ `waiting_not_due`
  - Run2：Rank139 pilot 产物存在且最近更新（csv/json mtime≈01:07）
  - Run3：fresh intake 新增 `pbo-cscv / deflated sharpe honesty gate` 候选定义（未做实现）

### 最近 research/strategy_review/
- 上一条：`2026-03-22_0108_strategy-review.md`

### 当前 cron 列表（要点）
- `bot2-strategy-review-40m`：running
- `bot3-momentum-auto-opt-13m`：running
- `momentum-narrow-paper-lanes-20m`：running
- `bot7-quant-digest-30m`：持续 error（模型超时/鉴权问题；不挤占 desk 本轮排班）
- `Rank32b live maintenance`：上次 run error（JSON parse）；与本轮 desk 排兵布阵无直接耦合，先不抢修。

## 2) Seat 回答（硬口径）
### Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **状态**：`running paper pilot / waiting_not_due`
- **hosted lanes（P3 continuity / sidecar）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m refresh running）
  - sidecar but not on current 20m lane：`Rank 122`（strict-only short re-arm，低频监控）

### Live seat 是否空？
- **Live Seat：暂空**（不为填满而硬推）。

### Scout 复刻对象
- **Scout Seat 当前主点**：`Rank 139 / CUSUM event-bar confirm-veto gate`
  - 级别：`P3 / hosted narrow paper pilot`
  - 默认 gate：`confirm_same_dir_only @ thr_mult=0.8`
  - 关键监控字段：`no_event_timeout`（未确认=不放行 的保守语义）

## 3) 候选池分档（P0~P4）
- **P4**：暂无
- **P3**：`Rank 139`（hosted narrow paper pilot）；`Rank 2 / 17 / 29 / 32b`（既有 hosted continuity）；`Rank 122`（strict-only sidecar）
- **P2**：暂无明确新晋
- **P1**：`pbo-cscv / deflated sharpe honesty gate`（新 intake，横向守门层）；`Rank 125`、`Rank 112`、`Rank 111`（evidence_pool / budget used）
- **P0**：`Rank 138 / 137 / 127` 及大批已 park ranks（证据池，不占主资源）

## 4) Next 3 bot3 runs（排班，authoritative）
1. **Run 1：EMA due-check first（require-due）**
2. **Run 2：Rank139(P3) pilot 低频健康检查（只做 1 件事）**
   - 只核对 ops page/CSV 是否持续更新 + 是否出现爆雷指标（no_event_timeout/retention 等）。
3. **Run 3：pbo-cscv honesty gate（只做 1 个小交付）**
   - 仅做 `source intake（权威参考 + 人话摘要）` 或 `minimal implementation（离线小工具：deflated_sharpe/pbo_risk_flag 一列）`，不要扩散到多候选。

## 5) 本轮对 TODO / desk board 做了什么
- 已对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做**最小必要更新**：
  - Active Scout：新增 `pbo-cscv / deflated sharpe honesty gate（P1 new intake）`
  - Next 3 bot3 runs：Run2 明确改为低频健康检查；Run3 明确为 pbo-cscv 下一步小交付
  - evidence：补入 01:46 fresh intake，保持槽位=最近 5 条

## 6) 风险与不确定性
- `pbo-cscv/deflated sharpe` 属于“评价/守门层”而非 alpha 本体：必须避免把它变成无限研究坑；优先落到可执行的小工具/标签。
- repo 长期脏会增加协作摩擦，但不影响本轮 desk 口径；不在本轮做大清理。
