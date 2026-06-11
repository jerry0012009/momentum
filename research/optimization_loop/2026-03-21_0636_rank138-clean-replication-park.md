# 2026-03-21 06:36 UTC — Rank 138 / funding × OI crowding breadth / 最小 clean replication + 硬裁决（park）

## 本轮一句话
先执行 `EMA require-due`，结果继续 `waiting_not_due`；按 desk 规则切到 `Scout Seat`，对 active Scout 做边际价值比较后，认领 `Rank 138` 的 **1 次最小 clean replication**（30d, BTC/ETH/SOL, 15m, baseline vs size/veto/extra-confirm），结论：**hard verdict = park（single-pocket dependency）**。

## 0) 开场检查（执行要求 1）
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - Run 1: EMA due-check first
  - Run 2: 若 waiting_not_due，做 Rank 138 最小 clean replication
  - Run 3: 给 Rank 138 keep_P1/promote_P2/park 的硬结论
- `git status --short`：存在大量与本轮无关脏文件，继续保持 **不混提**。
- 最近 runs：最近两轮已完成 Rank 138 source intake（guard-passed）与 Rank 137 park。

## 1) Run 1：EMA due-check first
执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

结果：
- 当前无 `due-now / overdue` lane（exit code 2 = waiting/not-due guard hit）
- 最靠前 lane：`Crypto 1d+1wk（BTC/ETH/SOL）`，约 `17.4h` 后到点

结论：
- 本轮合法切到 Scout Seat，不空转。

## 2) 先比较 active Scout 的边际价值（执行要求 3.5）
- `Rank 138`：已 guard-passed，正处于 Run 2 指定动作（最小 clean replication）；一次即可改变去留 verdict。
- `Rank 127 / 125 / 112 / 111`：都属于 `P1 + budget-used/evidence_pool`，本轮若跳过去会偏离顶板顺序。
- `Rank 2 / 17 / 29 / 32b / 122`：`P3 continuity`，在 `EMA=waiting_not_due` 下不应优先占主资源。

结论：
- 本轮主资源继续给 `Rank 138`（1 主点），不并开其他候选。

## 3) Run 2 + Run 3 合并闭环：Rank 138 最小 clean replication

### 3.1 可部署产物（deployable artifact）
新增脚本：
- `scripts/build_rank138_funding_oi_crowding_breadth_clean_replication.py`

核心冻结口径：
- 样本：`BTC/ETH/SOL`，15m，本地 cache 最近 30d
- 外部特征：Binance 公共 `fundingRate` + `openInterestHist(5m)` 聚合到 15m
- breadth：`long/short crowding breadth`，滚动分位阈值 `p80/p90`（统一 `shift(1)` 防泄漏）
- baseline setup：
  - `ema_trend_long`
  - `reclaim_long`
  - `breakdown_short`
- overlay 仅 3 个最小接法：
  - `size_discount_p80`（拥挤侧 size×0.6）
  - `veto_p90`（拥挤极端直接跳过）
  - `extra_confirm_p80`（拥挤时多一根确认）
- 统一执行：`next-bar open + no-overlap + hold 8 bars`
- 指标：`post_cost_expectancy`、`failure_rate_4bars`、`trade_count_retention`、`max_drawdown`

### 3.2 本轮产物输出
- artifacts：
  - `reports/artifacts/scout_rank138_funding_oi_crowding_breadth_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank138_funding_oi_crowding_breadth_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank138_funding_oi_crowding_breadth_15m/scorecard.csv`
  - `reports/artifacts/scout_rank138_funding_oi_crowding_breadth_15m/summary.csv`
  - `reports/artifacts/scout_rank138_funding_oi_crowding_breadth_15m/trade_log.csv`
- reader-facing：
  - `reports/site/factors/scout_rank138_funding_oi_crowding_breadth_15m/report.html`
  - `reports/site/reading/repo_scout/rank138_funding_oi_crowding_breadth_clean_replication.html`

### 3.3 硬结论（Run 3）
`summary.csv`：
- verdict = `park`
- detail = `最好的最小接法 veto_p90 仍不够诚实：post-cost expectancy 改善 0.04%，positive_asset_ratio=33.33%，trade retention=70.05%。更像单 pocket / 砍交易数换来的好看数字。`

`scorecard.csv`：
- recommended_action = `park`
- hard_fail_flags = `single_pocket_dependency`

## 4) 对 desk 的回写
已更新 `docs/TODO.md` 顶板：
- Scout 当前主点改为 `Rank 127`（P1 最后一次便宜诚实检查）
- Active Scout 排序中将 `Rank 138` 下调到 `P0 / park`
- `Next 3 runs` 切换到 `Rank 127` 路线
- `最近关键 evidence` 新增本轮 due-check 与 Rank 138 park 证据

## 5) 最小验证
实际执行：
1. `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`（waiting_not_due, 合法切 Scout）
2. `python3 scripts/build_rank138_funding_oi_crowding_breadth_clean_replication.py`（成功，产出完整 artifacts + 页面）

## 6) 风险与边界
- 本轮是最小 clean replication，不是完整 stability pack（时间稳定性仅给了轻量分，不做重型扩样本）。
- `Rank 138` 已有明确 park 结论；后续默认不再占主资源，除非出现新的状态变化或外部证据重开。

## 7) 提交与工作区说明
- 未提交 git。
- 原因：工作区存在大量本轮无关脏文件，严格不混提。
