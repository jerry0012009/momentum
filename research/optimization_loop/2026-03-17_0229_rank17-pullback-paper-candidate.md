# 2026-03-17 02:29 UTC · Rank 17 pullback recovery clean replication 并晋级 paper candidate

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：`Paper Seat=EMA` 当前是 `waiting_not_due`，因此本轮主资源按规则切到 `Scout Seat`。
- 先比较 active Scout 候选边际价值：`Rank 7~16` 已完成 clean replication + Light Stability Pack 且多数为 `park`；`Rank 2` 已是 narrow paper pilot，当前若继续做也只剩 wiring 微动作。
- 因此本轮认领一个 fresh、paper/repo based、能直接复用本地 cache 的 15m crypto 候选：`pullback recovery confirmation`（repo 现有模块 + Lo/Jiang 结构语义映射）。

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 17 pullback recovery confirmation` 的 `clean replication + Light Stability Pack` 并给 hard verdict。
- 紧邻子点：把 desk 指挥板写回（新增 Rank 17 状态与 Run 2 执行口径）。

## 做了什么改动
1. 新增脚本：
   - `scripts/build_pullback_recovery_scout_clean_replication.py`
   - 复用 `reports/artifacts/scout_tau_band_breakout_15m/cache/*__120d__15m.csv`，不下载新数据。
   - 冻结规则：
     - `trade on` = 5m/15m baseline momentum 同向 + 最近 2 根出现缩量回调 + 当前 bar 放量突破前 1 根高/低点
     - `trade off` = 任一条件不满足
   - 输出 clean replication 与四项轻量稳定性产物。

2. 产出 artifact（deployable / reader-facing）：
   - `reports/artifacts/scout_pullback_recovery_confirmation_15m/`
     - `clean_replication_summary.csv`
     - `clean_replication_asset_summary.csv`
     - `time_stability.csv`
     - `parameter_stability.csv`
     - `cross_asset_stability.csv`
     - `cost_trade_stability.csv`
     - `paper_candidate_admission_memo.csv`
     - `clean_replication_meta.csv`
   - 网页：
     - `reports/site/factors/scout_pullback_recovery_confirmation_15m/report.html`

3. 更新 `docs/TODO.md` 顶部战板（最小局部写回）：
   - 新增 `Rank 17 pullback recovery confirmation -> paper candidate pool`
   - 更新 `Next 3 bot3 runs` 当前窗口排班说明
   - 在 `Run 2` 新增 `2k` 执行条目，明确继续认领边界（只做最小 wiring 或 verdict-changing check）

## 验证 / 证据（Light Stability Pack）
- 主变体：`pullback2_vol1.0_break1`
- 聚合（6bps/side）：
  - `mean_total_return ≈ +10.21%`
  - `positive_asset_ratio = 2/3`
  - `mean_trades ≈ 69.7`
- 成本稳定性：
  - `10bps/side ≈ +4.07%`
  - `20bps/side ≈ -9.81%`
- 时间稳定性：
  - 正收益 bucket 占比 `4/9`（偏混合）
- 参数稳定性：
  - 邻域内 `4/6` 参数组合仍为正，最优邻域 `pb2_v1.5_b1`（`mean_total_return≈+62.55%`）
- 跨标的稳定性（6bps 主变体）：
  - BTC 负，ETH/SOL 正（`2/3` 为正）

## 本轮 hard verdict
- `Rank 17 pullback recovery confirmation`：**进入 `paper candidate pool`，暂不升 `narrow paper pilot`**。
- 原因：已满足最小 paper candidate 门槛（6bps 正、2/3 标的为正、10bps 仍存活、交易数不稀疏），但时间稳定性仍混合且 20bps 下转负，尚不够稳。

## 风险 / 边界
- 当前结果对高 friction 较敏感（20bps 下转负），后续若进入更实盘化约束需优先看成本与执行摩擦。
- 时间稳定性仍有明显 pocket 差异，暂不宜直接提升为 narrow paper pilot。

## 过程异常与 fallback 记录（按 8.1）
- 在更新 `docs/TODO.md` 当前窗口段落时，首次 `edit` 因 exact-match 失败。
- 已按规则立刻 fallback：`read` 重新定位最新片段后，二次 `edit` 成功；本轮未因可恢复编辑错误中断。

## 下一步建议
1. 若下轮继续认领 Rank 17：仅做一个会改变 verdict 的最小检查（例如更贴执行摩擦的一刀）或最小 paper-candidate wiring。
2. 若无真实追加价值，按板子切回 fresh Scout intake，避免在同一候选上反复文档打磨。

## 提交状态
- 本轮未提交 git。
- 原因：工作区存在大量与本轮无关的历史脏文件，当前只做 selective 产物写入与战板最小更新，避免混提。
