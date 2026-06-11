# 2026-03-19 12:52 UTC — Rank 89 outside-close -> back-inside-close clean replication -> park

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short | wc -l = 1412`
  - 最近 optimization logs 最新到：
    - `2026-03-19_1219_rank89-outside-inside-intake.md`
    - `2026-03-19_1201_rank88-clean-replication-park.md`
    - `2026-03-19_1149_rank88_macro_event_overlay_intake.md`
- 已再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 7.2h`、`Crypto 11.2h`、`A股 18.2h`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮合法主动作必须落在 `Scout Seat / Rank 89 minimal clean replication`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 2 / Rank 89 / outside-close -> back-inside-close failure verdict minimal clean replication`
- **紧邻子点**：根据 replication 结果，直接回答 `promote_to_P2 / park`，并回写 `TRADING DESK BOARD / Next 3`

## 先比较 active Scout 候选边际价值（3.5）
本轮按顶板默认顺序执行，当前允许动作只有：
1. `Rank 89 / outside-close -> back-inside-close failure verdict`
2. `close-range compression asymmetry`
3. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

由于 `Rank 89` 已在上轮完成 intake + 两条轻量诚实守门，本轮必须先把它的唯一那次最小 clean replication 跑完，不能并开 `close-range compression asymmetry`，也不能回头给 `P1 evidence_pool` 或 `P3 continuity` 续命。

## 本轮执行内容
### 1) 最小 clean replication 口径
- 新增脚本：`scripts/build_rank89_outside_inside_clean_replication.py`
- 统一数据口径：
  - `BTC/ETH/SOL 120d 15m` 本地 cache
  - `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- base setups 固定为：
  - `ema_psar_long`
  - `fib_retest_long`
  - `breakout_short`
- 只比较三臂：
  - `baseline`
  - `outside_inside_binary`
  - `outside_inside_seqext_size`

### 2) failure verdict 的最小实现
- rolling 区间：前 `16` 根 `15m` 高低区间（约 4h），全部 `shift(1)`；
- `outside close`：`close > zone_high` 或 `close < zone_low`；
- `back-inside close`：在接下来 `1~4` 根内，收盘回到区间内部；
- 只有最近 `4` 根内出现与当前 setup 同方向的 failure verdict，才允许放行对应 base setup；
- `seqext_size` 只做一件事：若最近 overshoot 深度达到区间宽度 `25%` 以上，则把仓位降到 `0.5x`，否则维持 `1.0x`。

## Hard verdict
- **`Rank 89 = park / evidence_pool`**

### 为什么不是 promote_to_P2
#### overall（6 bps / side）
- `baseline`
  - `mean_total_return ≈ -28.85%`
  - `positive_asset_ratio = 1/3`
  - `mean_trades ≈ 292.3`
  - `trade_count_retention ≈ 86.96%`
  - `4bar early-fail ≈ 77.57%`
- `outside_inside_binary`
  - `mean_total_return ≈ +2.34%`
  - `positive_asset_ratio = 2/3`
  - `mean_trades ≈ 14.3`
  - **`trade_count_retention ≈ 4.45%`**
  - `4bar early-fail ≈ 73.08%`
- `outside_inside_seqext_size`
  - `mean_total_return ≈ +1.85%`
  - `positive_asset_ratio = 2/3`
  - `mean_trades ≈ 14.3`
  - `trade_count_retention ≈ 4.45%`
  - `mean_position_size_mult ≈ 98.72%`
  - `4bar early-fail ≈ 73.08%`

### 更诚实的读法
- 它不是“稳稳过滤掉坏 break”，而是主要靠 **极端缩样本** 换来成本后少亏 / 微正；
- `trade_count_retention` 只剩约 `4.45%`，远低于 desk 当前对 queue-facing fast lane 可接受的水平；
- `sequence-extreme` 分档没有新增诚实增益：`seqext_size` 还略弱于纯 `binary`；
- 因此当前更像 **局部 verdict clue**，不够格升到 `P2 / paper candidate pool`。

### setup 级读法
- `breakout_short`
  - `baseline @6bps ≈ -15.99%`
  - `outside_inside_binary @6bps ≈ +1.71%`
  - 但 retention 仅约 `3.47%`
- `fib_retest_long`
  - `baseline @6bps ≈ -7.60%`
  - `outside_inside_binary @6bps ≈ +0.99%`
  - retention 仅约 `5.52%`
- `ema_psar_long`
  - `baseline @6bps ≈ -5.26%`
  - `outside_inside_binary @6bps ≈ -0.03%`
  - 仍未转正

结论：改善主要集中在少量 `breakout_short / fib_retest_long` 样本，并没有形成足够厚、足够共享、足够保留交易数的 shared overlay。

## 新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/scout_rank89_outside_close_back_inside_failure_15m/overall_summary.csv`
- `reports/artifacts/scout_rank89_outside_close_back_inside_failure_15m/setup_summary.csv`
- `reports/artifacts/scout_rank89_outside_close_back_inside_failure_15m/asset_summary.csv`
- `reports/artifacts/scout_rank89_outside_close_back_inside_failure_15m/trade_samples.csv`
- `reports/artifacts/scout_rank89_outside_close_back_inside_failure_15m/meta.csv`

### reader-facing 网页
- `reports/site/factors/scout_rank89_outside_close_back_inside_failure_15m/report.html`
- `reports/site/reading/repo_scout/rank89_outside_close_back_inside_failure_clean_replication.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `12:52 UTC` 补充，冻结 `Rank 89 = park / evidence_pool`；
- 当前 active Scout 顺序改写为：
  1. `close-range compression asymmetry`
  2. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
  3. `P3 continuity`
  4. `tiny-live plumbing`
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = close-range compression asymmetry source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 close-range compression asymmetry 已 guard-pass，则给 1 次最小 clean replication；若直接 hard-fail，才允许回退到 Rank 82 / 80 / 81 evidence_pool`

## 最小验证
- 已确认以下文件存在并可读：
  - `reports/artifacts/scout_rank89_outside_close_back_inside_failure_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank89_outside_close_back_inside_failure_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank89_outside_close_back_inside_failure_15m/meta.csv`
  - `reports/site/reading/repo_scout/rank89_outside_close_back_inside_failure_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件（`1412`）。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要空转；
- 直接切 `close-range compression asymmetry` 的 source intake + 两条轻量诚实守门；
- 不要回头继续磨 `Rank 89` 的说明页，也不要让 `P3 continuity` 插队。
