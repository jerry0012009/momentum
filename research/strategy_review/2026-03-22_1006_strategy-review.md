# Strategy Review (bot2) — 2026-03-22 10:06 UTC

## 本轮一句话判断
`EMA (Paper Seat)` 继续保持为 paper 主锚，但当前最该盯的是 **refresh / week-1 review 的连续性**；在 `EMA waiting_not_due` 的大部分时间里，把 bot3 主资源明确导向：**Rank139(P3) 低频健康检查（只做1件事） + pbo/CSCV/PBO/DSR honesty gate 的“权威 source intake / canonical implementation 二选一”**，避免再开新候选。

## 1) Repo / 最近记录 / cron 快速巡检
- repo: `master`，工作区 **很脏**（大量 report/artifacts 变更 + 若干 docs 修改 + 多个未跟踪目录/临时文件）。本轮不做 commit，只做 desk board 的最小必要更新。
- 最近 optimization_loop：
  - `2026-03-22_1004_rank139-health-check.md`（最新）
  - `2026-03-22_0951_pbo-cscv-canonical-scorecard.md`
  - `2026-03-22_0935_rank139-healthcheck.md`
- 最近 strategy_review：
  - `2026-03-22_0840_strategy-review.md`（最近一条）
- cron 列表（关键信号）：
  - `bot3-momentum-auto-opt-13m` 正常启用
  - `momentum-narrow-paper-lanes-20m` 正常启用（Rank2/17/29/32b lane refresh）
  - `bot2-strategy-review-40m` 正常启用

## 2) Strongest evidence（会改变排兵布阵的）
1. `Rank 139` 已明确定位为 **post-entry confirm/veto gate**，且已给出 `hard verdict = promote_P3`，并已经落成 **ops landing page + monitoring CSV**（从“研究结论”进入“可运行监控”）。
2. `pbo-cscv / DSR` 作为“横向诚实守门层”已完成 minimal proxy demo + scorecard 雏形：下一步应转向 **权威 source + canonical 实现**，而不是继续做更多 proxy。

## 3) Weakest / 应该避免继续磨损的线
- 任何对 `Rank139` 的近义研究重复（thr_mult/版本花样、更多漂亮图）——当前阶段边际价值很低，除非出现爆雷信号。
- `P1 budget used` 的遗留 rank（Rank125/112/111 等）：本轮不再继续投入；它们属于 evidence pool。

## 4) P0~P4 分档（本轮只点名仍 relevant 的）
- **P3（narrow paper pilot / hosted）**
  - `Rank 139 / CUSUM event-bar confirm-veto gate`
  - `Rank 2 / 17 / 29 / 32b`（20m refresh hosted lanes，sidecar only）
  - `Rank 122`（strict-only sidecar）
- **P1（只允许再做一次便宜诚实检查）**
  - `pbo-cscv / deflated sharpe honesty gate`（但它不与 rank 线竞争 seat：只做 source+canonical）
  - `Rank 125 / range location veto gate`（budget used，除非有明确“最后一刀”检查，否则不再排进 Next3）
- **P0（park / evidence only）**
  - `Rank 138 / funding×OI breadth overlay` 等已明确 single-pocket dependency 的条目

## 5) Seat & 排班结论（回答 Desk Board 必答项）
### Paper primary anchor + hosted lanes
- **Paper primary anchor**：`EMA / 创业板ETF 1d (active_primary)`（保持不变）
- **hosted lanes（P3 continuity / sidecar）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m refresh）+ `Rank 122`（low-frequency monitoring）

### Live seat 是否空
- **Live Seat：仍暂空**（没有新的候选达到“足够接近 tiny-live review”的升格门槛）。

### Scout 复刻对象（当前主 scout）
- **Scout Seat：Rank 139 (P3) narrow paper pilot continuity** + `pbo-cscv honesty gate`（只做 1 个小交付，不开新候选）。

### Next 3 bot3 runs（建议维持现状，但更明确“只做 1 件事”）
1. **Run 1 = EMA due-check first**（若 due-now/overdue 先做 paper refresh；否则立刻切 Run2）
2. **Run 2 = Rank139(P3) hosted narrow paper pilot 低频健康检查（只做 1 件事）**
   - 目标：确认 ops/CSV 更新 + 观察 `no_event_timeout / retention / mean_net@6bps` 是否出现爆雷
3. **Run 3 = pbo-cscv honesty gate（只做 1 个小交付）**
   - 二选一：`权威 source intake + 人话摘要` **或** `canonical CSCV/PBO/DSR 离线实现（可复用脚本/模块）`

## 6) 本轮我改了什么
- 对 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：仅做 **最小必要** 更新——把 `Rank139` 最新一次 health-check（10:04 UTC）写入 `最近关键 evidence`，并保持 evidence 槽位不膨胀。

## 7) 网页 / 表达建议
- 首页/入口页应继续强化一句话主线：**“EMA 进入 running paper；Rank139 作为 P3 hosted gate 只做低频健康检查；honesty gate 只做 canonical source/implementation”**，避免读者误以为 desk 在同时推进十几条 rank。

## 8) 风险与不确定性
- repo 工作区脏导致“下一步想要严谨提交/回滚”成本偏高；后续若要做真正的部署/cron prompt/监控接线改动，建议先做一次整理：把明显临时文件移入 tmp/ 或加入 .gitignore（但这属于独立清理任务，不在本轮展开）。
- `Rank17` open-position 快照仍存在“exit_ts_marked 但 open inferred”的不确定性：应等待下一次 20m lane refresh 或专门核对。
