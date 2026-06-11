# 2026-03-17 13:10 UTC · P3 lane bot3 回补触发队列

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / reconciliation / parity / dry-run`
- 触发原因：
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`
  - `Run 2 / Scout Fast Lane` 里最近一批本地 `paper / repo based 5m / 15m crypto` fresh intake 已完成当前允许动作：`Rank 35` 已 park，`Rank 30 / 31 / 32 / 33 / 34` 也都已完成最小 clean replication 并 park
  - 本地 shortlist 剩余 `Rank 5 / Rank 6` 仍偏外部数据依赖，不适合作为这轮默认 Scout 主资源
  - 上一轮虽已把 `Rank 2 / 17 / 29` 统一写成 `no_default append/review need`，但 reader-facing 页面还没有把“**什么条件下 bot3 才应该重新接管这些 P3 lane**”写成显式触发器；这仍是一个容易反复误读的 plumbing 小 blocker

## 开始前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，因此本轮只做 selective 写入，不混提
- 当前席位状态：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = 本地 fast-intake 暂无更高边际价值的便宜 fresh candidate`
- 当前 `P3` lane 状态（来自 `manual_narrow_paper_status.csv`）：
  - `Rank 2`：`new_trades_appended = 0`，无 open position
  - `Rank 17`：仍有 `2` 个 open paper positions，但都只是 continuity
  - `Rank 29`：`new_trades_appended = 0`，无 open position

## active Scout / plumbing 边际价值比较
- `Rank 17 / Rank 2 / Rank 29`：仍是 `P3 narrow paper pilot`，但当前没有新的真实 `append/review row`
- `Rank 35`：刚完成最小 clean replication，hard verdict 已是 `park`
- `Rank 30 / 31 / 32 / 33 / 34`：都已完成当前允许动作并 park，不该重开
- `Rank 5 / Rank 6`：外部数据依赖仍偏重，不适合这轮 13 分钟快筛
- 结论：本轮最诚实的动作仍是 `Run 3`，但主点从“owner / no-default 边界”进一步下沉到“**bot3 重新介入的显式触发器**”

## 本轮主点 + 紧邻子点
- **主点**：为 `manual narrow paper lanes` 新增一张 `bot3 re-entry trigger queue`，把 `Rank 2 / 17 / 29` 何时才值得重新回到 bot3 默认排班写成可审计 artifact
- **紧邻子点**：把同一张触发表同步挂到 reader-facing 页面，避免后续继续把 `Rank 17` 的 open position 或 `P3` 身份本身误读成“当前就该由 bot3 继续补 append/review”

## 本轮做了什么
### 1) 给 manual narrow paper builder 增加回补触发表产物
修改：`scripts/build_manual_narrow_paper_lanes_report.py`

新增导出：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_bot3_reentry_queue.csv`

表内固定写清：
- `current_owner = manual_narrow_paper_runner`
- `bot3_reentry_now = no`
- `trigger_condition = manual narrow-paper refresh 新增 closed trade append 或 weekly-review row`

并按 lane 分开写出当前状态：
- `Rank 2 = narrow_paper_seeded_waiting_real_append`
- `Rank 17 = open_positions_waiting_manual_refresh`
- `Rank 29 = monitoring_seeded_waiting_real_append`

### 2) reader-facing 页面同步增加触发队列区块
重建：
- `reports/site/factors/manual_narrow_paper_lanes/report.html`

页面新增：
- `Bot3 re-entry trigger queue` 区块
- Artifact 列表新增 `manual_narrow_paper_bot3_reentry_queue.csv`

这让网页不只说“当前不是默认 bot3 append/review need”，而是进一步说清：
**只有当 manual narrow-paper refresh 真正追加 closed trade 或新的 weekly-review row 时，bot3 才重新回到默认排班。**

### 3) 本轮工具级编辑 fallback
- 在给 artifact 列表插入新 CSV 链接时，第一次 `edit` 因 exact-text 不匹配失败
- 已按 loop 要求立刻执行 fallback：先 `read/exec sed` 重读目标片段，再用更小片段重新精确替换
- 最终已成功写入，不把这类可恢复编辑错误升级成整轮失败

## 核心 hard verdict
**当前三条 `P3` lane 仍统一维持：`bot3_reentry_now = no`。**

更直白地说：
- `Rank 17` 现在有 open paper positions，**不等于** bot3 现在就该继续围着它补近义 wiring
- `Rank 2 / 29` 也都不是“因为仍属 P3，所以默认继续认领”
- bot3 的默认重新介入触发器必须是：`manual narrow-paper refresh` 真的追加了 `closed trade append` 或新的 `weekly-review row`

## 交付物
### deployable / plumbing artifacts
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_bot3_reentry_queue.csv`
- `reports/site/factors/manual_narrow_paper_lanes/report.html`

### 关键触发摘要
- `Rank 2 -> no / waiting_real_append`
- `Rank 17 -> no / open_positions_waiting_manual_refresh`
- `Rank 29 -> no / monitoring_seeded_waiting_real_append`

## 最小验证
已运行：
- `python3 scripts/build_manual_narrow_paper_lanes_report.py`

已抽查：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_bot3_reentry_queue.csv`
- `reports/site/factors/manual_narrow_paper_lanes/report.html`

结果：
- builder 成功退出（code 0）
- 触发队列 CSV 已成功生成
- 页面已出现 `Bot3 re-entry trigger queue` 区块，并挂出新 artifact 链接
- 三条 lane 当前都明确写成 `bot3_reentry_now = no`

## 风险 / 边界
- 这轮没有新开 fresh intake，也没有推进新的 clean replication；它解决的是 `P3 lane 何时才该回到 bot3` 的调度歧义
- 该触发表依赖 `manual narrow-paper refresh` 链正确续写；如果后续 refresh 没有产出新的 closed-trade append / weekly-review row，bot3 仍不该因为 open positions 本身而误判需要接管
- 若下一轮拿到更高边际价值的 `paper / repo based 5m / 15m crypto` 新候选，默认仍应优先回到 `Scout Seat`

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提
