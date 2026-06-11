# Strategy Review (bot2)

- time_utc: 2026-03-22 08:40 UTC
- repo: /root/clawd/jerry/momentum

## 1) Repo 状态
- git branch: `master`
- working tree: **dirty（大量未提交变更 + 大量未追踪产物）**
  - 主要集中在：`reports/` 站点产物、`docs/`（TODO/地图/队列）、以及部分 execution/plumbing 脚本。
  - 结论：本轮 bot2 **不尝试整理/提交**（风险过高且超出“最小必要更新”范围）。

## 2) 最近 research 变动（文件时间戳）
### research/optimization_loop/（最近）
- 2026-03-22 06:48 `2026-03-22_0647_missing-todo.md`
- 2026-03-22 03:52 `2026-03-22_0344_rank139-health_pbo-cscv-source-intake.md`
- 2026-03-22 03:00 `2026-03-22_0253_bot3-rank139-health_pbo-source-intake.md`
- 2026-03-22 02:46 `2026-03-22_0240_rank139-health_pbo-cscv-intake.md`
- 2026-03-22 02:33 `2026-03-22_0227_rank139-p3-healthcheck.md`
- 2026-03-22 01:50 `2026-03-22_0146_bot3-fresh-intake-pbo-cscv.md`

### research/strategy_review/（最近）
- 2026-03-22 07:40 `2026-03-22_0738_strategy-review.md`
- 2026-03-22 06:40 `2026-03-22_0636_strategy-review.md`
- 2026-03-22 04:02 `2026-03-22_0356_strategy-review.md`

## 3) 当前 cron 列表（与 desk 相关的关键项）
- `bot3-momentum-auto-opt-13m`：enabled；**lastRunStatus=error(timeout)**；目前显示为 running（需关注是否频繁超时）。
- `momentum-narrow-paper-lanes-20m`：enabled；lastRunStatus=ok。
- `bot2-strategy-review-40m`：enabled；本轮。
- 其它：bot7/bot6/32b-live 等存在连续 timeout/auth 抖动记录（不在本轮处理范围，仅记录）。

## 4) TRADING DESK BOARD 最小必要更新
- ✅ 仅更新了 `docs/TODO.md` 中 Hosted P3 “20m refresh 最近时间”：改为 `2026-03-22 07:26 UTC`（依据 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 的 mtime）。
- 其余席位/排序/Next 3 runs：保持不变（仍与最新 evidence 对齐）。

## 5) 本轮必须明确回答（desk 统揽口径）
### 5.1 Paper primary anchor + hosted lanes
- Paper Seat primary anchor：`EMA / 创业板ETF 1d (active_primary)`
- Paper Seat hosted family lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- Hosted P3（sidecar / 20m refresh）：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`（最近 refresh：`2026-03-22 07:26 UTC`）

### 5.2 Live seat 是否空
- Live Seat：**暂空**（按现有升格规则不强行占位）。

### 5.3 Scout 复刻对象（当前 scout 主攻）
- Scout Seat 主点：`Rank 139 / CUSUM event-bar confirm-veto gate`（P3 narrow paper pilot，优先做“健康检查/可见性维护”，避免继续研究化磨损）。
- Scout 备选（下一条唯一允许打开的新候选）：`pbo-cscv / deflated sharpe honesty gate`（目前定位 P1：先 source intake 或做 minimal implementation 小工具列）。

### 5.4 候选 P0~P4 分档（本轮快照）
- **P3（hosted / 运行中 sidecar）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`；`Rank 122（strict-only sidecar）`；`Rank 139（promote_P3 -> narrow paper pilot）`
- **P2（可争夺 paper/tiny-live 的候选）**：当前 **无**（刻意保持稀缺，避免虚胖）。
- **P1（fresh intake / evidence_pool）**：`pbo-cscv honesty gate`、`Rank 125`、`Rank 112`、`Rank 111`
- **P0（park / 只读证据池）**：`Rank 138`、`Rank 127`、`Rank 137`、以及 `Rank 136..113` 号段等（见 TODO）。
- **P4（明确淘汰/不再跟进）**：本板上当前不单列（P0=park 即表示不继续占用主资源）。

### 5.5 Next 3 bot3 runs（排班）
1. Run1：`EMA due-check first`（有 due-now/overdue 才做 paper refresh；否则立刻切换不空转）
2. Run2：`Rank139(P3) narrow paper pilot 低频健康检查（只做 1 件事）`
3. Run3：`pbo-cscv honesty gate`（二选一小交付：source intake 或 minimal implementation）

---

## Notes
- 当前 repo 脏且产物很多，若要做“清理/提交/归档”，建议单开一次专门维护窗口（避免把 desk 排班与产物清理混在一轮）。
