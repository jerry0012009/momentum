# 2026-03-16 23:43 UTC — Rank11 clean replication + Light Stability Pack（park）

## 为什么这轮选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：`Paper Seat=EMA` 当前是 `waiting_not_due / due_soon`，`Run 1` 不能空转。
- 比较 active Scout 候选边际价值后，上一轮新入口 `Rank 11 Lo-style causal extrema pattern gate` 仍是本轮最高优先级，因为它刚完成 source intake，最缺的是 **clean replication + 4 项 Light Stability Pack** 的硬结论。
- `Rank 2` 已是 `narrow paper pilot approved` 且无真实 append/review need，本轮不应再补 wiring 文档。

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 11` 最小 clean replication，并给出 `promote / park` 硬结论。
- 紧邻子点：把 `TODO` 顶部战板里 `Rank 11` 状态与 `Next 3 runs` 更新为新 verdict，避免后续继续按旧口径重复认领。

## 做了什么改动
1. 新增并运行：
   - `scripts/build_lo_extrema_pattern_clean_replication.py`
2. 产出 clean replication artifact：
   - `reports/artifacts/scout_lo_extrema_pattern_15m/overall_summary.csv`
   - `reports/artifacts/scout_lo_extrema_pattern_15m/asset_summary.csv`
   - `reports/artifacts/scout_lo_extrema_pattern_15m/trades.csv`
   - `reports/artifacts/scout_lo_extrema_pattern_15m/time_stability_drycheck.csv`
   - `reports/artifacts/scout_lo_extrema_pattern_15m/parameter_stability_drycheck.csv`
   - `reports/artifacts/scout_lo_extrema_pattern_15m/cross_asset_stability_drycheck.csv`
   - `reports/artifacts/scout_lo_extrema_pattern_15m/cost_trade_stability_drycheck.csv`
   - `reports/artifacts/scout_lo_extrema_pattern_15m/clean_replication_meta.csv`
3. 更新 reader-facing 页面：
   - `reports/site/factors/scout_lo_extrema_pattern_15m/report.html`
4. 局部更新 `docs/TODO.md` 顶部 command board：
   - `Rank 11` 从 `source intake / clean replication next` 改为 `park / evidence pool`
   - `Next 3 bot3 runs` 当前窗口与 `2e` 子项同步新 verdict（默认切回 new repo-based 15m intake first）

## 最小验证 / 证据
- 语法检查：
  - `python3 -m py_compile scripts/build_lo_extrema_pattern_clean_replication.py`
- 主脚本执行：
  - `python3 scripts/build_lo_extrema_pattern_clean_replication.py`
  - 成功输出：`[ok] lo extrema pattern clean replication generated`
  - 运行耗时：`ELAPSED=2:40.49`（首次 120s 限时被 SIGTERM，随后在更长超时窗口重跑成功）

## Light Stability Pack 结论（四项）
- 时间稳定性：`fail`（`1/3` positive buckets）
- 参数稳定性：`fail`（`0/5` 邻域配置为正）
- 跨标的稳定性：`fail`（`0/3` 资产为正）
- 成本/交易数稳定性：`fail`（`0/4` cost levels 为正）

## 硬结论（hard verdict）
- `Rank 11 Lo-style causal extrema pattern gate` 当前应判定为：**`park / evidence pool`**。
- 关键数字（6bps/side, winner=`double_bottom_reclaim`）：
  - `mean_total_return ≈ -4.33%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 58.3`
- 结论含义：这条线完成了诚实快筛闭环，但不满足 `paper candidate` 准入。

## 对交易台主线的影响
- `Paper Seat`：不变（`EMA running paper / waiting_not_due`）
- `Live Seat`：不变（暂空）
- `Scout Seat`：`Rank 11` 已完成并 `park`，默认主资源应转向**新的 paper/repo based 15m intake**，而不是继续磨 `Rank 11` 近义说明。

## 风险 / 边界
- 本轮完全复用现有 `Binance 120d 15m` cache；未引入新数据源、未扩样本。
- 当前 workspace 存在大量与本轮无关脏文件，不适合安全 selective commit。

## 下一步建议
- 下一轮 `Run 2`：直接认领新的 `paper / repo based 15m crypto` fresh intake（source intake -> clean replication），不要回到 `Rank 11` 文案打磨。

## Commit
- 未提交（原因：repo 存在大量与本轮无关的脏文件 / 未跟踪文件，避免混提）。
