# 2026-03-19 16:32 UTC — Rank 92 时间稳定性检查后压回 park

## 为什么这轮是它
- 先实际执行了 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 脚本继续返回 **`waiting_not_due`**：当前没有 `due-now / overdue` 的 EMA lane；最近 due 约为 `美股 3.5h`、`Crypto 7.5h`、`A股 14.5h`。
- `manual_narrow_paper_last_run_summary.json` 仍没有新的 `P3 status-changing event` 可挤掉 Scout。
- 按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最新 `Next 3 bot3 runs`，本轮合法主动作就是 **`Rank 92 / opening-drive adaptive offset continuation gate`** 剩下那 1 个 truly verdict-changing 的 `Light Stability Pack / 时间稳定性`。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 92` 的时间稳定性检查，并直接回答 `promote_to_P2 / keep_P1 / park`
- **紧邻子点**：把 verdict、active Scout 顺序、下一轮 `Next 3` 最小写回到 `TRADING DESK BOARD`

## 本轮实现口径
- 新增脚本：`scripts/build_rank92_time_stability_check.py`
- 完全复用上一轮 artifact：`reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/trades.csv`
- 不追新 bar，不改规则，不重跑 source intake / clean replication
- 只把每个 `asset × setup × variant` 按时间顺序切成 `3` 个等样本 bucket
- 固定口径仍是：`BTC/ETH/SOL | 120d | 15m | 6bps/side | signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 对象只看两条还可能改变 verdict 的线：
  - `adaptive_offset_gate`
  - `adaptive_offset_halfsize`

## 结果摘要
### desk 级时间稳定性 verdict
- `adaptive_offset_gate`
  - `overall_mean_total_return≈-6.91%`
  - `positive_asset_ratio≈33.33%`
  - `positive_bucket_count=1/3`
  - `min_bucket_return≈-1.31%`
  - `weakest_setup=breakout_short`
- `adaptive_offset_halfsize`
  - `overall_mean_total_return≈-6.39%`
  - `positive_asset_ratio≈33.33%`
  - `positive_bucket_count=1/3`
  - `min_bucket_return≈-1.83%`
  - `weakest_setup=breakout_short`

### 人话解释
- 这条线的问题不是 path-quality 没改善，而是**收益改善没有稳定穿过时间维度**。
- `full gate` 与 `half-size` 都只剩 **`1/3` 正桶**，说明它们更像某一段 pocket，而不是能跨时间段稳定工作的 shared gate。
- 更直白地说：**前两桶大多还在漏，只有后段才勉强转正**。这不够支持继续留在 active Scout 主资源位。

## hard verdict
**`Rank 92 = park / evidence pool`**

原因收口：
- `full gate` 没有经住时间稳定性；
- `half-size` 也没有给出足够稳的 fallback；
- 所以更诚实的做法不是继续续命，而是**压回 park，释放 Scout 主资源给 fresh intake 的 `Rank 95`**。

## 本轮产物
### reader-facing 落点
- `reports/site/factors/scout_rank92_opening_drive_adaptive_offset_15m/time_stability_check.html`
- `reports/site/reading/repo_scout/rank92_opening_drive_adaptive_offset_time_stability.html`

### artifacts
- `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/time_stability_window_summary.csv`
- `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/time_stability_verdict_summary.csv`
- `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/time_stability_summary.json`

## desk board 写回
已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最小刷新为：
- `Rank 92 = park / evidence pool`
- active Scout 顺序：`Rank 95 > Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 92 park / evidence_pool > Rank 94 park / evidence_pool > P3 continuity > tiny-live plumbing`
- `Next 3 bot3 runs`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 95 / Vajra controlled-pullback depth-budget 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 95 guard-pass，则只给它 1 次最小 clean replication；若 Rank 95 intake 直接 hard-fail / exhausted，才允许回退到旧 evidence_pool；P3 continuity 与 tiny-live plumbing 继续不得插队`

## 验证 / 命令
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 已执行：`python3 -m py_compile scripts/build_rank92_time_stability_check.py`
- 已执行：`python3 scripts/build_rank92_time_stability_check.py`
- 本轮未做重下载，完全复用本地 cache / artifact

## 额外修正
- 初版 `scripts/build_rank92_time_stability_check.py` 出现 1 处字符串拼接语法错误；已立即修正并重新 `py_compile` 通过。
- 初次自动写回 `docs/TODO.md` 时，`16:28 UTC` 段落插入到了 `16:07 UTC` 明细之前；已在本轮内立即整理回正常时间顺序，避免板子误读。

## git / 脏区说明
- `git status --short | wc -l = 1484`
- 与本轮直接相关的脏文件：
  - `docs/TODO.md`
  - `scripts/build_rank92_time_stability_check.py`
  - `research/optimization_loop/2026-03-19_1632_rank92-time-stability-park.md`
  - `reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/`
  - `reports/site/factors/scout_rank92_opening_drive_adaptive_offset_15m/`
  - `reports/site/reading/repo_scout/rank92_opening_drive_adaptive_offset_time_stability.html`
- 其余大量脏文件与本轮无关，因此本轮不提交，避免混提。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`，默认切到 **`Rank 95 / Vajra controlled-pullback depth-budget`** 的 `source intake + 两条轻量诚实守门`。
- 不要再继续磨 `Rank 92` 的 wording / continuity 文案；除非后续出现真正新的 status-changing 证据，否则它当前就应留在 `park / evidence pool`。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件，混提不安全。
