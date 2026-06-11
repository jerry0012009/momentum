# 2026-03-17 02:33 UTC · Rank 17 paper-candidate wiring（含 friction 诚实修正）

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：`Paper Seat=EMA` 当前是 `waiting_not_due`，因此本轮主资源按规则切到 `Scout Seat`。
- 先比较 active Scout 候选边际价值：
  - `Rank 7~16` 已完成 clean replication + Light Stability Pack，当前都在 `park / evidence pool`；
  - `Rank 2` 已是 `narrow paper pilot approved`，若继续做通常只剩 append/review 类最小维护；
  - `Rank 17` 刚进入 `paper candidate pool`，按 board 允许继续认领，但只应做**最小 paper-candidate wiring**或一个会真正改变 verdict 的最小检查。
- 因此本轮认领 `Rank 17` 的最小 wiring，而不是再开新候选，也不是继续磨 `Rank 2` 的近义文档。

## 本轮主点 + 紧邻子点
- 主点：把 `Rank 17 pullback recovery confirmation` 压成最小 `paper candidate monitoring + refresh seed` 产物。
- 紧邻子点：把当前更诚实的 friction 读法（`15bps` 已转负）写回 desk board 与 reader-facing 页面。

## 先检查的当前状态
- repo 工作区存在大量**与本轮无关**的历史脏文件与未跟踪产物；本轮只做 selective 写入，不混提。
- `Paper Seat` 当前无 due-now / overdue refresh need，仍按 board 视作 `waiting_not_due`。
- 当前 active Scout 候选里，`Rank 17` 是最接近“减少真实 gate”的一条；`Rank 2` 当前若继续做，边际价值低于把 `Rank 17` 的 paper-candidate 接线真正落地。

## 做了什么改动
1. 新增脚本：
   - `scripts/build_pullback_recovery_paper_candidate_wiring.py`
   - 只复用既有产物：
     - `clean_replication_summary.csv`
     - `clean_replication_asset_summary.csv`
     - `clean_replication_trades.csv`
     - `time_stability.csv`
     - `cost_trade_stability.csv`
     - `paper_candidate_admission_memo.csv`
   - 不下载新数据，不追新 bar。

2. 新增 deployable / plumbing artifact：
   - `reports/artifacts/scout_pullback_recovery_confirmation_15m/paper_candidate_monitoring_board.csv`
   - `reports/artifacts/scout_pullback_recovery_confirmation_15m/paper_candidate_refresh_seed_rows.csv`
   - `reports/artifacts/scout_pullback_recovery_confirmation_15m/paper_candidate_refresh_history.csv`

3. 更新 reader-facing 页面：
   - `reports/site/factors/scout_pullback_recovery_confirmation_15m/report.html`
   - 本页已从“只讲 clean replication”改成：
     - 如实强调 `15bps` 已转负；
     - 展示 `paper candidate monitoring board`；
     - 展示 `refresh seed rows`；
     - 明确当前仍是 `paper candidate only`，不是 `narrow paper pilot`。

4. 更新战板：
   - `docs/TODO.md`
   - 写回 `Rank 17` 最新状态与 `Next 3 bot3 runs` 当前窗口说明：
     - 已补完最小 paper-candidate wiring；
     - 当前 blocker 明确为 `BTC weak leg / 15bps negative / time pocket mixed`；
     - 若无 genuinely new honest evidence，后续默认应把 Scout 主资源让回 fresh intake。

## 本轮新增的硬事实 / 验证
- 当前现有样本的 friction ladder：
  - `6bps/side ≈ +10.21%`
  - `10bps/side ≈ +4.07%`
  - `15bps/side ≈ -3.13%`
  - `20bps/side ≈ -9.81%`
- 这意味着：上一轮摘要把 Rank 17 的成本韧性说得偏松；更诚实的 desk 读法应是：
  - 它**够资格留在 `paper candidate pool`**；
  - 但**还不够资格自动升到 `narrow paper pilot`**。
- 6bps 下跨资产读法仍为：
  - `positive_asset_ratio = 2/3`
  - `BTC-USD total_return ≈ -17.63%`
  - `ETH-USD total_return ≈ +23.71%`
  - `SOL-USD total_return ≈ +24.53%`
- 时间稳定性仍偏混合：`4/9` bucket 为正，且 BTC / SOL 在早期 bucket 有明显负 pocket。

## 本轮 hard verdict
- `Rank 17 pullback recovery confirmation`：**继续保留在 `paper candidate pool`，本轮不升 `narrow paper pilot`**。
- 原因：
  1. 已有 clean replication + Light Stability Pack + 最小 paper-candidate wiring；
  2. 但当前最关键 blocker 仍在：`15bps 已转负`、`BTC weak leg`、`time pocket mixed`；
  3. 因此这轮最有价值的推进是把这些 blocker 压成可复用 monitoring/seed，而不是文档性偷升格。

## 风险 / 边界
- 当前 `paper candidate_monitoring_board.csv` 已把 promotion boundary 锁死：这套接线只服务 `paper candidate only`。
- 如果后续 1~2 轮拿不到 genuinely new honest evidence，就不应继续在 `Rank 17` 上补更多近义 wiring；应把 Scout 主资源切回 fresh paper/repo intake。
- `BTC` 弱腿必须继续单列 red watch，不能被 aggregate 均值盖过去。

## 过程异常与 fallback 记录（按 8.1）
- 本轮未触发 `edit exact text` 失败；战板更新均一次成功。
- 额外诚实修正：在复查既有 `cost_trade_stability.csv` 时，发现当前样本实际是 `15bps` 已转负；已把该事实同步写回 report / TODO / 本日志，避免延续上一轮偏乐观口径。

## 下一步建议
1. 默认把 `Rank 17` 从“可继续补 wiring”改成“除非有 genuinely new honest evidence，否则让位给 fresh intake”。
2. 若下一轮仍想认领 `Rank 17`，只允许做一个真正改变 verdict 的最小检查；否则转去新的 `paper / repo based 5m / 15m crypto` 候选。
3. `Rank 2` 只在存在真实 append/review need 时再回补；不要默认重回 `Rank 2` 的近义接线。

## 提交状态
- 本轮未提交 git。
- 原因：工作区存在大量与本轮无关的历史脏文件 / 未跟踪产物，当前只做 selective 产物写入与战板最小更新，避免混提。
