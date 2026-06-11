# 2026-03-17 06:56 UTC · Rank 26 regime_triplet 快筛并推进到 P2

## 为什么这轮选这个
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - `Paper Seat / EMA` 当前是 `waiting_not_due`，`Run 1` 无 due-now 动作。
  - 按默认顺序应落到 `Run 2 / Scout Seat`。
- 先比较 active Scout 候选边际价值：
  - `Rank 17 / Rank 2` 都是 `P3 narrow paper pilot`，本轮未出现新的真实 `append/review` 缺口。
  - 因此本轮应执行 fresh intake，而不是继续磨 P3 文档接线。

## 本轮主点 + 紧邻子点
- 主点：把 fresh intake `Rank 26 regime_triplet state gate` 一次推进到 `clean replication + Light Stability Pack + hard verdict`。
- 紧邻子点：把 verdict 与动作边界写回 `docs/TODO.md` 顶板与 Run 2 候选列表，形成下一轮可执行指挥口径。

## 先过两条轻量诚实守门
1. **trade on / trade off 可写清楚**
   - trade on：`baseline multi-tf momentum` 同向，且 `long=up_regime`、`short=down_regime`（`strict_up_down`）。
   - trade off：基线方向缺失，或状态门未过。
2. **无明显 lookahead / repaint / leakage**
   - `regime_triplet` 仅使用 `t-3..t` 的 `open/close/volume + rolling MA/vol MA`；
   - 固定沿用下一根 bar 执行口径；
   - 全程复用已有 `BTC/ETH/SOL 120d 15m` cache，不追新 bar。

## 实施内容
1. 新增脚本：
   - `scripts/build_regime_triplet_scout_clean_replication.py`
2. 生成 artifact：
   - `reports/artifacts/scout_regime_triplet_15m/clean_room_spec_v1.csv`
   - `clean_replication_summary.csv`
   - `clean_replication_asset_summary.csv`
   - `clean_replication_trades.csv`
   - `time_stability.csv`
   - `parameter_stability.csv`
   - `cross_asset_stability.csv`
   - `cost_trade_stability.csv`
   - `paper_candidate_admission_memo.csv`
   - `clean_replication_meta.csv`
3. 生成网页落点：
   - `reports/site/factors/scout_regime_triplet_15m/report.html`

## 本轮关键结果（hard verdict）
- `Rank 26 regime_triplet state gate`：**`paper candidate（P2）`**
- 主变体：`strict_up_down`
  - `6bps/side`：`mean_total_return≈+14.65%`，`positive_asset_ratio=2/3`，`mean_trades≈141`
  - 时间稳定性：正收益 bucket `2/3`
  - 参数稳定性：最佳邻域 `ma15_vol96_k08≈+27.10%`（非单点热像素）
  - 成本稳定性：`10bps/side≈+2.44%`，但 `15/20bps` 已转负（约 `-11.01% / -22.68%`）
- 约束：`mean_no_trade_ratio≈86.58%` 偏高，当前不直接升 `P3`。

## 由结果触发的最小纠偏
- 初跑时脚本默认主变体设成 `regime_triplet_default`，会把 verdict 压到 `park`。
- 因同轮对照里 `strict_up_down` 明显更强，且会改变 desk verdict，已在同轮完成最小纠偏：
  - 将脚本 `PRIMARY_LABEL` 切到 `strict_up_down`
  - 重跑全套 clean replication + Light Stability Pack
  - 最终以 `paper candidate（P2）` 写回。

## TODO / 指挥板写回
已更新 `docs/TODO.md`：
- 顶部 `authoritative override` 更新为 06:52 UTC 口径，明确 `Rank 26 -> P2`。
- `Run 2` 列表新增 `2s. Rank 26 regime triplet state gate`。
- rank 主清单新增 `26` 条目（含冻结规则、结果边界、下一步允许动作）。

## 最小验证
- `python3 -m py_compile scripts/build_regime_triplet_scout_clean_replication.py`
- `python3 scripts/build_regime_triplet_scout_clean_replication.py`
- 校验 CSV：
  - `paper_candidate_admission_memo.csv`
  - `clean_replication_summary.csv`
  - `time_stability.csv`
  - `cost_trade_stability.csv`

## 边界与下一步
- 本轮只认领 1 条 Scout 主线（Rank 26），未并行扩候选。
- 下一轮若继续认领 Rank 26，按 `P2` 预算只允许 1 次 genuinely verdict-changing 最小检查，目标二选一：
  - 升到 `narrow paper pilot`，或
  - 压回 `park`。

## Git
- 工作区存在大量与本轮无关脏文件；本轮不做 commit，避免混提。
