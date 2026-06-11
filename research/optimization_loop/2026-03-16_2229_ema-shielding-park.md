# 2026-03-16 22:29 UTC — EMA shielding clean replication → park

## 本轮 desk 读法
- 先检查了 `docs/TODO.md` 顶部 `TRADING DESK BOARD`、repo 当前脏文件、最近 optimization loop / strategy review。
- `Paper Seat = EMA` 当前仍是 `waiting_not_due / due_soon`，没有新的 `due-now / overdue` refresh 可做；因此按 desk board 默认顺序，主资源切到 `Scout Seat`。
- active Scout 边际价值比较：
  - `Rank 2 combo_all`：已连续多轮补齐 `ledger / refresh / weekly review / writeback / continuity`，本轮没有真实 append-ready refresh/review row，也没有明确 verdict-changing check，继续做它属于低边际 wiring。
  - `Rank 7 adaptive trend combo`：刚完成 clean replication + Light Stability Pack，hard verdict 已是 `park`，继续追打没有边际价值。
  - 其余活跃线里，最适合本轮的是**新的 paper/repo based 15m crypto intake**；为了避免继续强调 breakout，本轮选了更贴近当前主线的 `EMA shielding / threshold + retest_hold`。

## 本轮认领
- 主点：`Run 2 / Scout Fast Lane` 新 intake —— `Rank 8 EMA shielding / threshold + retest_hold`
- 紧邻子点：把 desk board / shortlist 同步写回，明确该候选已经 `park`，避免下一轮又默认绑回这条线。

## 做了什么
1. 新建脚本：`scripts/build_ema_shielding_clean_replication.py`
   - 直接复用现有 `Binance 120d / 15m / BTC+ETH+SOL` cache。
   - clean-room 比较三条最小变体：
     - `raw_cross`
     - `threshold_005`
     - `retest_hold`
   - 执行口径固定为：`next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | friction ladder 6/10/15/20 bps per side`
   - 同轮补齐 `Light Stability Pack`：
     - 时间稳定性
     - 参数稳定性（threshold 邻域）
     - 跨标的稳定性
     - 成本 / 交易数稳定性
2. 生成 deployable / reader-facing 产物：
   - 网页：`reports/site/factors/scout_ema_shielding_15m/report.html`
   - 主要 artifact：
     - `reports/artifacts/scout_ema_shielding_15m/overall_summary.csv`
     - `.../time_stability_drycheck.csv`
     - `.../parameter_stability_drycheck.csv`
     - `.../cross_asset_stability_drycheck.csv`
     - `.../cost_trade_stability_drycheck.csv`
     - `.../clean_replication_meta.csv`
3. 更新 desk-facing 编排文件：
   - `docs/TODO.md`
   - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`

## 硬结论（hard verdict）
- `Rank 8 EMA shielding / threshold + retest_hold` → **`park / evidence pool`**
- 当前 winner 虽然是 `retest_hold`，但依然不达标：
  - `6bps/side mean_total_return ≈ -6.50%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 54 / asset`
  - `mean_no_trade_ratio ≈ 5.38%`（并不是靠极端少交易才显得“不那么差”）
- baseline 对照：
  - `raw_cross @ 6bps ≈ -15.76%`
  - `threshold_005 @ 6bps ≈ -15.54%`
  - `retest_hold @ 6bps ≈ -6.50%`
- 诚实守门：
  - `trade on / trade off` 可明确写清
  - 当前实现未使用 future label / repaint 口径
- 但 `Light Stability Pack` 四项全出现硬 fail：
  - 时间稳定性：`0/3 positive buckets`
  - 参数稳定性：`0/5 threshold neighbors positive`
  - 跨标的稳定性：`0/3 assets positive`
  - 成本稳定性：`0/4 cost levels positive`

## 为什么这轮不是 NO_PROGRESS
- 产出了一条新的 **clean replication + Light Stability Pack + hard verdict**，并且已经同步到 reader-facing 页面。
- 这直接减少了 Scout 不确定性：`EMA shielding` 不再是待研究方向，而是明确归入 `park / evidence pool`。
- 也因此把下一轮默认主入口继续推向**下一条新的 paper/repo based 5m/15m crypto intake**，而不是重复认领 `Rank 2/7/8`。

## 验证
- 运行：`python3 /root/clawd/jerry/momentum/scripts/build_ema_shielding_clean_replication.py`
- 结果：成功，生成 artifact 与站点页。

## 工作区 / git 备注
- 当前 repo 里存在大量与本轮无关的既有脏文件与未跟踪产物；本轮没有尝试混提或清理它们。
- 本轮只最小修改了与当前动作直接相关的文件：
  - `scripts/build_ema_shielding_clean_replication.py`
  - `docs/TODO.md`
  - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - `reports/artifacts/scout_ema_shielding_15m/*`
  - `reports/site/factors/scout_ema_shielding_15m/report.html`

## 下一步默认建议
- 继续遵守当前 board：`Scout Seat（new intake first） > tiny-live plumbing > 其他维护`。
- 下轮除非 `EMA` 真正 due，或 `Rank 2` 出现真实 append/review need / verdict-changing check，否则默认不要再回去磨 `Rank 2/7/8` 的近义文书。
- 更高边际价值的主入口应继续是：新的 `paper / repo based 5m / 15m crypto` 候选。