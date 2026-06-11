# 2026-03-17 19:03 UTC · small-live evidence freshness board

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / evidence freshness board`
- 触发原因：
  - 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Paper Seat / EMA` 当前仍应按 `waiting_not_due` 处理，不存在新的 `due-now / overdue` continuation 任务
  - `Live Seat` 仍明确为 `暂空 / waiting for next promoted scout winner`
  - `Scout Seat` 本轮先按要求重新比较 active 候选与 fresh intake 边际价值后，仍没有拿到一条合格的新主点，因此诚实回退到 `Run 3`

## 开始前检查
- repo 状态：工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 当前 seat 读法：
  - `Paper Seat`：`EMA = running paper pilot / waiting_not_due`
  - `Live Seat`：默认空席
  - `Scout Seat`：默认仍优先，但本轮 fresh intake 未拿到合格 source

## active Scout 候选边际价值比较
### 已有 active Scout / P3 continuity
- `Rank 2 / Rank 17 / Rank 29` 目前都更接近 `P3 continuity / plumbing / review`，且今日已经多次围绕 tiny-live / continuity 状态页落了最小接线
- 继续认领它们的 review / monitoring / writeback 近邻动作，边际价值低，且容易踩到 `P3 continuity` 日预算上限后的低效区

### fresh intake 尝试
本轮先按规则重查本地 shortlist：
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`

结论：
- 这些本地 source 目前仍以已 intake 过的论文线索、机制解释或非直接 fast-lane 执行模板为主
- 本轮没看到一条明显优于现有判断、且适合立刻认领成 `source intake -> clean replication` 的新 `paper / repo based 5m / 15m crypto` 候选
- 额外尝试 `web_search` 找 repo-based fresh intake，但本机 Brave API key 缺失，无法在本轮内完成可靠外部补源

### 因此本轮决策
- 诚实不把“继续硬找新 source”包装成已认领成功
- 也不继续空磨同义 tiny-live 文档
- 直接转做一个仍会减少真实操作误读的 `Run 3` 主点：**把 tiny-live 当前几条 watch source 的 freshness 压成一张可审计表**

## 本轮主点 + 紧邻子点
- **主点**：新增 `small_live_evidence_freshness_board_v1.csv`
- **紧邻子点**：把同一结论同步到 reader-facing `alpha_closure_board` 页面

## 本轮做了什么
### 1) 修改 builder
文件：`scripts/build_alpha_closure_board_report.py`

新增：
- `SMALL_LIVE_EVIDENCE_FRESHNESS_BOARD_PATH`
- `format_file_freshness()`
- `get_small_live_evidence_freshness_board_rows()`
- `write_small_live_evidence_freshness_board_csv()`

freshness board 固定审计 4 个 tiny-live 关键 watch source：
1. `docs/TODO.md` 顶部 desk board
2. `small_live_rank2_receipt_chain_audit_v1.csv`
3. `manual_narrow_paper_status.csv`
4. `manual_narrow_paper_last_run_summary.json`

每条统一输出：
- `latest_file_mtime_utc`
- `approx_age`
- `freshness_state`
- `why_it_matters`
- `hard_read`

### 2) 当前 hard verdict 被压成 artifact
当前 freshness board 读法：
- `docs/TODO.md` 顶板：`fresh`（约 `13m`）
- `manual_narrow_paper_status.csv`：`fresh`（约 `11m`）
- `manual_narrow_paper_last_run_summary.json`：`fresh`（约 `11m`）
- `small_live_rank2_receipt_chain_audit_v1.csv`：`warning`（约 `2.6h`）

这意味着：
- 当前 `Live Seat = empty_by_default` 与 `Rank 17 / Rank 29` 的 `P3 continuity` 读法仍可继续相信
- 但 `Rank 2` 的 receipt-chain blocker 虽然没被推翻，也不该再被过度自信地当成“完全静止且无需更新”的新鲜证据
- 因此后续若继续回到 Run 3，更诚实的下一步不是再写 Rank 2 同义 packet，而是：**要么补新 audit / 真 replay，要么切回 fresh Scout intake**

### 3) reader-facing 页面同步
重建：
- `reports/site/factors/alpha_closure_board/report.html`

新增区块：
- `Tiny-live evidence freshness board（v1）`

页面公开口径：
- tiny-live 侧不能只看“有没有 trigger”，还要看“支撑这个判断的 source 够不够新”
- 若 source 仍 fresh，就继续遵守 `now-action queue`
- 若 source 转 stale，优先补 refresh / snapshot，而不是继续磨 near-synonym 说明页

## 为什么这轮比继续补同义 tiny-live 文档更值钱
- 前几轮已经把 `watchboard / trigger snapshot / now-action queue` 写清楚了“看哪里 / 现在有没有 trigger / 现在谁该动”
- 本轮补的是另一个真实操作盲点：**这些结论本身是不是建立在还够新的 source 上**
- 这能防止后续轮次把“没有 trigger”误读成真实静止，实际上只是证据源过旧

## 验证 / 证据
已运行：
- `python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`

已抽查：
- `reports/artifacts/alpha_closure_board/small_live_evidence_freshness_board_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

结果：
- builder 成功退出（code 0）
- 新 CSV 已生成，4 条 watch source 都写出了时间、年龄与 freshness 状态
- 页面已出现 `Tiny-live evidence freshness board（v1）` 区块

## 交付物
### deployable / reader-facing artifact
- `reports/artifacts/alpha_closure_board/small_live_evidence_freshness_board_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

### 同步文件
- `scripts/build_alpha_closure_board_report.py`

## 风险 / 边界
- 本轮没有推进新的 Scout candidate，也没有伪造 fresh intake 成功
- 本轮没有改变任何 seat verdict，也没有触发真实 venue execution
- 本轮没有去改共享 `docs/TODO.md` 顶板，避免在已有共享脏写入上继续扩面

## Git
- 未提交
- 原因：repo 内仍有与本轮无关的既有脏文件 / 未跟踪文件，避免混提
