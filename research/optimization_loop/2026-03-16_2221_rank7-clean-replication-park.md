# 2026-03-16 22:21 UTC · Rank7 clean replication + Light Stability Pack，verdict=park

## 为什么本轮选这个
- 先按 `TRADING DESK BOARD` 检查：`Paper Seat` 当前是 `waiting_not_due / due_soon`，因此不做 Run1 空转，转入 `Run2 Scout Fast Lane`。
- 先比较 active Scout 候选边际价值：
  - `Rank 2`：已是 `narrow paper pilot approved`，且近期已连续补完 ledger/refresh/review wiring；本轮无真实 append-ready 需求。
  - `Rank 5`：已完成 first verdict，当前是 `park`。
  - `Rank 7`：仍在 `source intake / clean replication next`，且是 board 明确指定的 fresh intake 入口，边际价值最高。
- 因此本轮主点认领：`Rank 7 adaptive trend combo` 的 **clean replication**；紧邻子点：补齐 **Light Stability Pack 4项** 并给出三选一硬结论。

## 本轮改动
1. 新增脚本：
   - `scripts/build_adaptive_trend_combo_clean_replication.py`
   - 基于现有 `Binance 120d 15m` cache，完成 `source intake -> clean replication -> Light Stability Pack`。
2. 产出 Rank7 artifacts（deployable + reader-facing）：
   - `reports/artifacts/scout_adaptive_trend_combo_15m/overall_summary.csv`
   - `reports/artifacts/scout_adaptive_trend_combo_15m/time_stability_drycheck.csv`
   - `reports/artifacts/scout_adaptive_trend_combo_15m/parameter_stability_drycheck.csv`
   - `reports/artifacts/scout_adaptive_trend_combo_15m/cross_asset_stability_drycheck.csv`
   - `reports/artifacts/scout_adaptive_trend_combo_15m/cost_trade_stability_drycheck.csv`
   - `reports/artifacts/scout_adaptive_trend_combo_15m/clean_replication_meta.csv`
3. 同步网页可见落点：
   - `reports/site/factors/scout_adaptive_trend_combo_15m/report.html`
4. 同步指挥板最小更新（局部）：
   - `docs/TODO.md` 顶部 `TRADING DESK BOARD`：把 Rank7 状态从 `clean replication next` 更新为 `park / evidence pool`，并把 Run2 的 fresh intake 入口从 Rank7 切回“下一条新候选”。

## 验证 / 证据
- 脚本执行：
  - `python3 scripts/build_adaptive_trend_combo_clean_replication.py`（成功）
- 关键结果（6bps/side）：
  - `fixed_priority`: `mean_total_return=+2.33%`，`positive_asset_ratio=2/3`，但 `mean_no_trade_ratio≈98.60%`（几乎不交易）。
  - `state_weighted_vote`: `mean_total_return=-21.75%`，`positive_asset_ratio=0/3`。
  - `equal_vote`: `mean_total_return=-33.68%`，`positive_asset_ratio=0/3`。
- Light Stability Pack：
  - 时间稳定性：`pass/pass/watch`（最差 bucket `-1.34%`）。
  - 参数稳定性：`fail`（`0/5` 邻域配置为正，跨标的邻域也 `0/5`）。
  - 跨标的稳定性：`pass/pass/watch`（BTC 最弱腿约 `-1.15%`）。
  - 成本/交易数稳定性：`pass/pass/pass`（20bps 仍微正）。
- `clean_replication_meta.csv` 已写入：`verdict_tag=park`。

## 硬结论（本轮）
- `Rank 7 adaptive trend combo` 当前应 **`park / evidence pool`**，不进入 `paper candidate pool`。
- 主要原因：当前“看起来不差”的版本依赖超高 `no_trade_ratio`，而更具代表性的 `state_weighted/equal` 版本在 6bps 已明显为负，且参数邻域出现硬 fail。

## 风险 / 边界
- 本轮严格复用历史样本与本地 cache，未引入新下载，也未追新 bar。
- 当前 verdict 仅服务 Scout 快筛；不构成 Live Seat 占位依据。

## 下一步建议
- 下轮 Run2 默认切入**新的 paper/repo-based 5m/15m crypto intake**（Rank7 已完成本阶段并 park）。
- `Rank 2` 仅在出现真实 `append/review` need 或 verdict-changing check 时再认领。

## 提交信息
- 本轮未提交 git。
- 原因：工作区存在大量与本轮无关脏文件，无法做安全的最小 selective commit。
