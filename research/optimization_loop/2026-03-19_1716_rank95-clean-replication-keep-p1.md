# 2026-03-19 17:16 UTC — Rank 95 Vajra controlled-pullback clean replication → keep_P1

## 为什么这轮是它
- 先实际执行了 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 脚本继续返回 **`waiting_not_due`**：当前没有 `due-now / overdue` 的 EMA lane；最近 due 约为 `美股 2.7h`、`Crypto 6.7h`、`A股 13.7h`。
- `manual_narrow_paper_last_run_summary.json` 仍没有新的 `P3 status-changing event` 可挤掉 fresh Scout。
- 按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最新 `Next 3 bot3 runs`，本轮合法主动作就是 **`Rank 95 / Vajra controlled-pullback depth-budget`** 的那 1 次最小 clean replication。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 95` 的最小 clean replication，并直接回答 `keep_P1 / promote_to_P2 / park`
- **紧邻子点**：把 verdict、active Scout 顺序、下一轮 `Next 3` 最小写回到 `TRADING DESK BOARD`

## 本轮实现口径
- 新增脚本：`scripts/build_rank95_vajra_controlled_pullback_clean_replication.py`
- 样本：`BTC/ETH/SOL | 120d | 15m`
- base setup：`ema_psar_long`
- 执行冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 对比臂：
  - `baseline`
  - `post_trigger_depth_1p0`
  - `prearmed_depth_0p75`
  - `prearmed_depth_1p0`
  - `prearmed_depth_1p25`
  - `prearmed_depth_1p0_plus_filters`（紧邻过滤子臂，仅回答 repo 的 green/volume/ADX 会不会只是暴力缩样本）

## 规则冻结（这轮真正回答的问题）
- **不是**继续把 `pullback<=1.5%` 当 repo 原样照抄的 `post-trigger gate`。
- **而是**比较：
  1. trigger 后才检查 depth，是否真的提供信息；
  2. 如果把 depth budget 前置成 `pre-armed state`，是否更诚实。
- `prearmed` 的最小 desk 口径：
  - 只读取 `signal` 之前 `5` 根 bar 的已完成信息；
  - 最近必须出现 toward-EMA 的回踩 / touch；
  - 回踩深度预算只允许测 `0.75% / 1.0% / 1.25%`；
  - repo 自带 `green / volume>1.2x / ADX>=25` 只作为邻近过滤臂，不偷渡成主结论。

## 结果摘要（6bps/side）
### overall
- `baseline`：`mean_total_return≈-5.68%` / `positive_asset_ratio≈33.33%` / `trade_count_retention≈94.64%` / `4bar early-fail≈80.76%`
- `post_trigger_depth_1p0`：`mean_total_return≈-4.09%` / `positive_asset_ratio≈33.33%` / `trade_count_retention≈91.91%` / `4bar early-fail≈80.18%`
- **`prearmed_depth_0p75`（最佳子臂）**：`mean_total_return≈-3.61%` / `positive_asset_ratio=0/3` / `trade_count_retention≈53.36%` / `4bar early-fail≈77.86%`
- `prearmed_depth_1p0`：`mean_total_return≈-3.80%` / `positive_asset_ratio=0/3` / `trade_count_retention≈66.08%` / `4bar early-fail≈82.18%`
- `prearmed_depth_1p25`：`mean_total_return≈-5.72%` / `positive_asset_ratio=0/3` / `trade_count_retention≈78.95%` / `4bar early-fail≈82.03%`
- `prearmed_depth_1p0_plus_filters`：`mean_total_return≈-4.92%` / `positive_asset_ratio=0/3` / `trade_count_retention≈13.21%` / `4bar early-fail≈96.43%`

### 资产侧（最佳子臂 `prearmed_depth_0p75`）
- `BTC-USD`：`26` 笔，`total_return≈-1.25%`
- `ETH-USD`：`15` 笔，`total_return≈-5.44%`
- `SOL-USD`：`18` 笔，`total_return≈-4.16%`
- 结论：改善存在，但还没有哪一条资产真正翻到稳定正值，说明它还不是可以诚实升格的 shared gate。

### 时间分桶（`prearmed_depth_1p0` 作为默认 time-stability 接线口径）
- `bucket_1≈-0.28%`
- `bucket_2≈-1.90%`
- `bucket_3≈-1.63%`
- 只看这张快照，还看不出可以直接升 `P2` 的稳定性；下一轮若仍给 Rank 95 预算，最合理也只剩 **1 个 truly verdict-changing 的时间稳定性检查**。

## hard verdict
**`Rank 95 = keep_P1 / mixed but honest`**

更直白地说：
- 这轮确实支持一个更诚实的 desk 读法：**depth budget 更像该前置成 pre-armed state，而不是继续放在 trigger 后当补刀过滤**；
- 但当前最优子臂 `prearmed_depth_0p75` 仍然 **`positive_asset_ratio=0/3`**，并没有把资产层读法拉成可部署 shared 改善；
- repo 自带 `green / volume / ADX` 过滤也被证实更像暴力缩样本，不是诚实增益；
- 所以这条线还不够硬到 `P2 / paper candidate`，但也不应直接说成没增量：更诚实的落点就是 **`keep_P1`**。

## 本轮产物
### reader-facing 落点
- `reports/site/factors/scout_rank95_vajra_controlled_pullback_15m/report.html`
- `reports/site/reading/repo_scout/rank95_vajra_controlled_pullback_clean_replication.html`

### artifacts
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/overall_summary.csv`
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/asset_summary.csv`
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/prearmed_threshold_summary.csv`
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/trade_log.csv`
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/meta.csv`

## desk board 写回
已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最小刷新为：
- `Rank 95 = keep_P1 / mixed but honest`
- active Scout 顺序：`Rank 95（time-stability next） > fresh 5m/15m paper-repo intake pool > Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 92 / Rank 94 park / evidence_pool > P3 continuity > tiny-live plumbing`
- `Next 3 bot3 runs`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 95 1 个 truly verdict-changing 的时间稳定性检查`
  3. `Run 3 = 若 Rank 95 time-stability 后 hard-fail / park，则按 7.10 切 fresh intake；若仍只是 keep_P1，也不要继续第三轮磨同一条线，默认仍切 fresh intake`

## 验证 / 命令
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 已执行：`python3 scripts/build_rank95_vajra_controlled_pullback_clean_replication.py`
- 本轮未做重下载，完全复用本地 `120d / 15m` cache

## git / 脏区说明
- `git status --short | wc -l = 1490`
- 当前 git 工作区仍有大量与本轮无关的脏文件；
- 本轮直接相关的新增/改动主要包括：
  - `scripts/build_rank95_vajra_controlled_pullback_clean_replication.py`
  - `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/`
  - `reports/site/factors/scout_rank95_vajra_controlled_pullback_15m/`
  - `reports/site/reading/repo_scout/rank95_vajra_controlled_pullback_clean_replication.html`
  - `docs/TODO.md`
- 因脏区过大，本轮不提交，避免混提。

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`，只给 `Rank 95` **1 个 truly verdict-changing 的时间稳定性检查**：
  - 固定复用这轮 `trade_log / time_bucket_summary` 的口径；
  - 不追新 bar、不扩成重下载；
  - 直接回答 `promote_to_P2 / keep_P1 / park`。
- 若时间稳定性不过关，立刻按 7.10 切 fresh paper/repo intake，不要继续给 Rank 95 补近义说明或第三轮小修小补。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件，混提不安全。
