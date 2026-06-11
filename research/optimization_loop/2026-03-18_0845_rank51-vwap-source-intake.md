# 2026-03-18 08:44 UTC — Rank 51 / vwap-trend-defense 通过 source intake 守门，进入最小 clean replication 队列

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与最新 `Next 3 bot3 runs` 检查当前 desk。
- 当前 `Paper Seat / EMA` 的最新 `due_guardrail_snapshot` 仍显示全 desk **没有 `due-now / overdue` lane**，因此 `Run 1` 的最诚实读法仍是 `due-check only`，不应伪造 refresh。
- 目前 `Rank 49`、`Rank 50` 都已在允许预算内给出 hard verdict 并压回 `park / evidence pool`，所以本轮按排班应转向 `Run 2 / Rank 51 / vwap-trend-defense source intake`。
- 本轮只认领 **1 个主点**：完成 `Rank 51` 的 `source intake + 两条轻量诚实守门`；不提前打开 clean replication，也不回头磨 `Rank 35b / tiny-live plumbing`。

## 先比较 active Scout 候选的边际价值
- `Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate`
  - fresh repo-based `15m` confirmation skeleton；
  - 能同时服务 `Fib retest_hold` 与 `EMA / PSAR continuation` 两条现有主线；
  - 主要风险是原 repo 偏 ES/MES session 语境、`0-star` 社会证明偏弱。
- `Rank 35b`
  - 仍是 queue-only fallback；
  - 不是当前应先拿主资源的 fresh repo / paper source。

**本轮结论：`Rank 51 > Rank 35b`。**
不是因为 `Rank 51` 已经更强，而是它至少还是新的 repo source，而 `Rank 35b` 目前还没有比 fresh intake 更高的边际价值。

## 做了什么改动
### 1) 新增 source-intake 产物生成脚本
- 新增：`scripts/build_rank51_vwap_trend_defense_source_intake.py`
- 用途：最小生成 `Rank 51` 的 artifact card 与 reader-facing HTML 页面。

### 2) 生成 deployable artifact
- 产物：`reports/artifacts/literature/scout_rank51_vwap_trend_defense_source_intake_card.csv`
- 网页：`reports/site/reading/repo_scout/rank51_vwap_trend_defense_source_intake.html`

### 3) 最小写回权威板
- 更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs` 区块：
  - 写回 `2026-03-18 08:41 UTC` 最新补充；
  - 冻结 `Rank 51` 当前状态为 `guard-passed / admit_to_clean_replication_queue`；
  - 将下一轮顺序收紧为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = Rank 51 / vwap-trend-defense minimal clean replication（仅当 EMA 仍 waiting_not_due）`
    - `Run 3 = Rank 35b / tiny-live plumbing`

## 验证 / 证据
### 1) Paper Seat 当前确实仍是 waiting_not_due
- 读取：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
- 当前最近 due 依次是：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A 股三条 lane -> 2026-03-19 07:00 UTC`
- 因此这轮不该继续做 EMA refresh，而应转去 `Scout Seat`。

### 2) Rank 51 的两条轻量诚实守门已冻结
- `trade on`：保留 base retest / continuation setup，只在价格回踩 `session VWAP` 后重新 reclaim 到强侧、且最近 `4~6` 根仍多数站在 VWAP 强侧时，才允许视作 defense-confirmed continuation。
- `trade off`：只碰 VWAP 不 reclaim、breadth 已掉回弱侧、或 base setup 自身已经失效时，不交易。
- `lookahead / repaint / leakage`：
  - 当前 repo 语义里未见一眼可判死刑的未来函数；
  - 但 clean replication 必须明确冻结成 **`UTC session VWAP + next-bar open + no-overlap`**，避免把同 bar reclaim 与同 bar fill 混成乐观成交。

### 3) 当前硬结论
- **`Rank 51 / vwap-trend-defense = guard-passed / admit_to_clean_replication_queue`**。
- 这不是说它已经是 alpha；只是说它已经通过 intake-stage 的两条轻量守门，值得拿 **1 次最小 clean replication** 预算。

## reader-facing 落点
- `reports/site/reading/repo_scout/rank51_vwap_trend_defense_source_intake.html`

## 风险 / 边界
- 原 repo 主语境是 ES/MES session-long 模板；迁移到 `24/7 crypto` 时，最容易过拟合的不是 VWAP 本身，而是 `session 定义` 与 breadth 窗口。
- 因此下一轮默认只允许做 **1 次最小 clean replication**：
  - 固定 `BTC/ETH/SOL 15m` cache；
  - 统一 `UTC session VWAP + next-bar open + no-overlap`；
  - 只比较 `base_setup`、`+vwap_reclaim`、`+vwap_reclaim+breadth_gate` 三臂；
  - 若改善主要来自砍样本而不是降低 `false-retest`，就应快速压回 `park / evidence pool`。
- 本轮未提交 git：当前工作区存在大量与本轮无关的脏文件与未跟踪产物，不安全混提。

## 下一步建议
1. 下一轮先继续做 `EMA due-check only`。
2. 若仍 `waiting_not_due`，只给 `Rank 51` **1 次最小 clean replication**。
3. 若 `Rank 51` 最小复现后仍不能诚实给出更高层 verdict，再回退到 `Rank 35b / tiny-live plumbing`，不要继续停在 intake wording。

## Commit hash
- 未提交。
- 原因：当前 git 工作区有大量与本轮无关的脏文件，不满足安全 selective commit 条件。
