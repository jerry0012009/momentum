# 2026-03-19 16:13 UTC — Rank 92 opening-drive adaptive offset clean replication → keep_P1

## 为什么这轮是它
- 先实际执行了 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 脚本继续返回 **`waiting_not_due`**：当前没有 `due-now / overdue` 的 EMA lane；最近 due 约为 `美股 3.9h`、`Crypto 7.9h`、`A股 14.9h`。
- `manual_narrow_paper_last_run_summary.json` 仍没有新的 `P3 status-changing event` 可挤掉 fresh Scout。
- 按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最新 `Next 3 bot3 runs`，本轮合法主动作就是 **`Rank 92 / opening-drive adaptive offset continuation gate`** 的那 1 次最小 clean replication。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 92` 的最小 clean replication，并直接回答 `keep_P1 / promote_to_P2 / park`
- **紧邻子点**：把 verdict、active Scout 顺序、下一轮 `Next 3` 最小写回到 `TRADING DESK BOARD`

## 本轮实现口径
- 新增脚本：`scripts/build_rank92_opening_drive_adaptive_offset_clean_replication.py`
- 样本：`BTC/ETH/SOL | 120d | 15m`
- 三臂：
  - `baseline`
  - `adaptive_offset_gate`
  - `adaptive_offset_halfsize`
- 执行冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- `opening-drive` 代理定义：**UTC 日内前 4 根 15m bar**
- 代理字段：`drive_high/drive_low`、`drive_mid`、`drive_range`、`sessionVWAP`
- 偏移定义：`adaptive_offset = max(|drive_mid-sessionVWAP|, 0.15*drive_range, 5bps*price)`

## 结果摘要（6bps/side）
### desk 级总表
- `baseline`：`mean_total_return≈-5.99%` / `positive_asset_ratio≈66.67%` / `retention=100%` / `trade_count=198`
- `adaptive_offset_gate`：`mean_total_return≈-6.91%` / `positive_asset_ratio≈33.33%` / `retention≈52.53%` / `trade_count=104`
- `adaptive_offset_halfsize`：`mean_total_return≈-6.39%` / `positive_asset_ratio≈33.33%` / `retention=100%` / `mean_position_size≈0.75x`

### setup 侧读法
- `ema_psar_long`
  - `baseline total≈-10.98%`
  - `adaptive_offset_gate total≈-16.36%`，`retention≈52.88%`
  - 虽然 `hold4 38.46% -> 69.09%`、`fail_back_inside4 49.04% -> 16.36%` 明显改善，但收益和跨 setup 统一性都没跟上
- `fib_retest_long`
  - `baseline total≈+3.64%`
  - `adaptive_offset_gate total≈+0.79%`，`retention≈33.33%`
  - 只剩很窄 pocket，小样本改善不够支撑升格
- `breakout_short`
  - `baseline total≈-10.61%`
  - `adaptive_offset_gate total≈-5.17%`，`retention≈62.30%`
  - 这条线上确实更像 shared continuation-quality gate，但还不够把全 desk 拉正

## hard verdict
**`Rank 92 = keep_P1`**

更直白地说：
- `adaptive_offset_gate` 的确把 path-quality 指标拉好了：`mean_hold4≈69.28%`、`mean_fail_back_inside4≈15.90%`；
- 但它是靠 **砍掉近一半样本** 换来的，而且 desk 级 `mean_total_return` 仍比 `baseline` 更差；
- `adaptive_offset_halfsize` 也没有把结果真正拉回 shared positive verdict；
- 所以当前最诚实的结论不是 `promote_to_P2`，也不是直接 `park`，而是：**保留成 `P1 weak candidate`，下一轮只允许再给 1 个 truly verdict-changing 的 `Light Stability Pack`（默认先做时间稳定性）**。

## 本轮产物
### reader-facing 落点
- `reports/site/factors/scout_rank92_opening_drive_adaptive_offset_15m/report.html`
- `reports/site/reading/repo_scout/rank92_opening_drive_adaptive_offset_clean_replication.html`

### artifacts
- `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/overall_summary.csv`
- `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/desk_overall_summary.csv`
- `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/setup_compare.csv`
- `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/per_asset_summary.csv`
- `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/summary.json`

## desk board 写回
已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最小刷新为：
- `Rank 92 = keep_P1 / P1 weak candidate（minimal time-stability next）`
- active Scout 顺序：`Rank 92 > Rank 95 > Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 94 park / evidence_pool > P3 continuity > tiny-live plumbing`
- `Next 3 bot3 runs`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 92 1 个 truly verdict-changing 的 Light Stability Pack（默认时间稳定性）`
  3. `Run 3 = 若 Rank 92 在时间稳定性后 hard-fail / park，则切 Rank 95 source intake；否则再回答是否 promote_to_P2`

## 验证 / 命令
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 已执行：`python3 scripts/build_rank92_opening_drive_adaptive_offset_clean_replication.py`
- 本轮未做重下载，完全复用本地 `120d / 15m` cache

## git / 脏区说明
- `git status --short | wc -l = 1480`
- 与本轮直接相关的脏文件：
  - `docs/TODO.md`
  - `scripts/build_rank92_opening_drive_adaptive_offset_clean_replication.py`
  - `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/`
  - `reports/site/factors/scout_rank92_opening_drive_adaptive_offset_15m/`
- 其余大量脏文件与本轮无关，因此本轮不提交，避免混提。

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`，只给 `Rank 92` **1 个真正会改变 verdict 的时间稳定性检查**：
  - 仍固定 `BTC/ETH/SOL 120d 15m`
  - 只看 `adaptive_offset_gate` 与 `adaptive_offset_halfsize`
  - 直接回答：`promote_to_P2 / keep_P1 / park`
- 若时间稳定性直接 hard-fail，则不要继续磨 wording，立刻切 `Rank 95 / Vajra controlled-pullback depth-budget` source intake。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件，混提不安全。
