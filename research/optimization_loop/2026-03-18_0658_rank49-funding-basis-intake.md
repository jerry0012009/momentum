# 2026-03-18 06:58 UTC — Run 2 fresh intake: Rank 49 funding/basis crowding gate

## 1) 轮次定位（先看交易台指挥板）
- 读取 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`。
- 当前窗口仍是 A 股 `07:00 UTC` 前的 due-soon：`Run 1 / EMA` 仍属 `waiting_not_due`，本轮按规则自动切到 `Run 2`（fresh intake）。
- 现有已活跃 Scout 线里：`Rank 48` 已在上一轮给出 `park`，`Rank 35b` 仍是 fallback。

## 2) 本轮只认领 1 主点 + 1 紧邻子点
### 主点（Scout Seat）
- 执行 `fresh source intake`，只认领 1 条 paper/repo based 15m crypto 候选：
  - **`Rank 49 / funding-basis crowded-long unwind gate`**
  - 来源：He et al.《Fundamentals of Perpetual Futures》+ Binance Funding/Premium Index 公共 API

### 紧邻子点
- 把 intake 结果写回 authoritative board（`docs/TODO.md` 的 `Next 3` 区域）并刷新下一轮顺序。

## 3) 边际价值比较（满足 3.5）
- `Rank 49`（fresh、paper+public data、直接服务 `breakout-short / EMA-short` 执行过滤）
- `Rank 35b`（queue-only fallback）
- 本轮结论：`Rank 49 > Rank 35b`，因此主资源位给 `Rank 49`。

## 4) 两条轻量诚实守门（满足 6）
- `trade on / trade off` 已冻结：
  - trade on：`funding_z > 0.5 && premium_z > 0.5`（crowded_long）
  - trade off：`funding_z < -0.5 || premium_z < 0`（already_crowded_short）默认 veto/降仓
- 无明显 lookahead/repaint/data leakage 设计：
  - funding/premium 仅用入场前最后一个已发布值
  - 执行统一 `next-bar open + no-overlap`

## 5) 产物（deployable / reader-facing）
- artifact：
  - `reports/artifacts/literature/scout_rank49_funding_basis_crowding_source_intake_card.csv`
- reader-facing 页面：
  - `reports/site/reading/repo_scout/funding_basis_crowding_source_intake.html`
- board 写回：
  - `docs/TODO.md` 新增 `06:58 UTC` authoritative 补充（含下一轮顺序）

## 6) 本轮硬结论
- **`Rank 49 = guard-passed / admit_to_clean_replication_queue`**（source intake 阶段）
- 下一轮策略：
  - 若仍 `EMA waiting_not_due`：给 `Rank 49` 仅 1 次最小 clean replication
  - 若已进入 due-now/overdue：优先回 `EMA paper refresh`

## 7) 验证与约束
- 仅做最小改动；未触发重型下载；未扩展多候选并行。
- git 工作区存在大量本轮无关脏文件，未做混提 commit。
