# 2026-03-20 03:12 UTC — Rank 107 MTF CHOP charged-up count clean replication → park

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `3.9h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD`，本轮合法主动作仍是 `Scout Seat`，且只该拿 **`Rank 107 / MTF CHOP charged-up count`** 的那唯一一手最小 clean replication。

## 开轮检查
- branch：`master`
- repo 脏文件：大量历史脏文件仍在（本轮未混提）
- 最近 optimization logs：
  - `2026-03-20_0254_rank107-mtf-chop-intake.md`
  - `2026-03-20_0231_rank106-clean-replication-park.md`
  - `2026-03-20_0228_rank106-elephant-intake.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前 `Scout Seat = Rank 107 / MTF CHOP charged-up count`

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 107 / MTF CHOP charged-up count`**
   - 上轮已完成 `source intake + 两条轻量诚实守门`，当前是唯一合法的 queue-facing 下一手。
   - 它最直接回答当前 desk 仍缺的那件事：`多周期一起变糊` 这类 regime 信息，到底能不能诚实地当作 `Fib retest_hold / EMA continuation long` 的 veto / size-down 层。
2. **`prebreak higher-low pressure ladder context gate`**
   - 仍是后备 fresh repo context backlog；只有在 `Rank 107` 收口后才该接棒。
3. **fresh paper / repo intake reserve（7.10）**
   - 只在当前 backlog 也 exhausted 时才切过去。
4. **旧 `P1 evidence_pool` / `Rank 17` 低频 health-check / `tiny-live plumbing`**
   - 当前都不该抢主资源位。

结论：本轮只认领 `Rank 107` 的最小 clean replication，不并开任何第二条候选。

## 本轮认领
- 主点：`Rank 107 / MTF CHOP charged-up count`
- 紧邻子点：把 clean replication artifact、reader-facing 页面、`TODO` 顶板与下一轮顺序一次写齐

## Clean replication 口径（strict queue-facing）
- 数据：`BTC/ETH/SOL Binance Futures 120d 15m`
- 执行：`signal 当根及之前数据 + MTF CHOP lookahead_off + next-bar open + no-overlap + hold 4 bars + 6bps/side`
- MTF CHOP：
  - `15m / 30m / 60m` 三层
  - `CHOP(14)`
  - `charged` 定义：`CHOP >= 61.8`
  - `charged_count` 定义：三层里满足 `charged` 的 TF 数
- baseline long proxy：
  - 严格冻结后，实际留下来的 queue-facing样本几乎只剩 `ema_continuation_long`
  - 也就是说，这轮没有再强行把更自由度的 `retest_hold` 代理偷渡进结果里
- 三臂只比较：
  1. `baseline`
  2. `hard_veto`：`charged_count >= 2` 的 bar 直接不做
  3. `size_down`：`charged_count >= 2` 只做 `0.5x`

## 结果摘要
### overall（4 bars / 6 bps per side）
- `baseline`
  - `events = 1248`
  - `charged_count>=2 share ≈ 4.57%`
  - `mean_net_ret ≈ -15.42bps`
  - `win_rate ≈ 35.74%`
  - `fail_below_ema20_4bars ≈ 29.41%`
  - `left_tail_p5 ≈ -126.89bps`
- `hard_veto`
  - `events = 1203`
  - `trade_count_retention ≈ 96.39%`
  - `mean_net_ret ≈ -15.57bps`
  - `win_rate ≈ 35.58%`
  - `fail_below_ema20_4bars ≈ 28.76%`
  - `left_tail_p5 ≈ -126.90bps`
- `size_down`
  - `events = 1248`
  - `avg_position_size ≈ 0.98x`
  - `mean_net_ret ≈ -15.41bps`
  - `win_rate ≈ 35.34%`
  - `left_tail_p5 ≈ -122.77bps`

### 怎么读
- `hard_veto` 确实有一点“少做高噪声 long”的味道：`fail_below_ema20_4bars` 小幅下降。
- 但 desk 当前真正关心的不是“有一点改善味道”，而是它能不能作为 queue-facing gate 留在默认主资源位。
- 这轮答案是否定的：
  1. `mean_net_ret` 没改善，反而从 `-15.42bps` 微幅恶化到 `-15.57bps`；
  2. `left_tail` 基本没变；
  3. `size_down` 只是把左尾略削浅，不是 expectancy 翻盘；
  4. 严格口径下实际留下来的 queue-facing样本几乎只剩 `ema_continuation_long`，说明它连“对 retest_hold 也稳定适用”这层都还不够硬。
- 所以这条线最诚实的定位仍是：**anti-chop 风险备注 / long-side caution overlay evidence**，而不是可继续升格的 `P2 / paper candidate`。

## 当前硬结论
**`Rank 107 = park / evidence pool`**。

翻成人话：记住“多周期一起变糊时，别硬做 long continuation”这条经验，但别把这条经验误包装成更强的结论。它现在更像一条局部 risk note，不值得继续占住默认 Scout 主资源位。

## 本轮交付（deployable artifact）
- artifact：
  - `reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/event_log.csv`
  - `reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/charged_bucket_summary.csv`
  - `reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/symbol_summary.csv`
  - `reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/verdict_summary.csv`
  - `reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/summary_snapshot.json`
- reader-facing 页面：
  - `reports/site/factors/scout_rank107_mtf_chop_chargedup_15m/report.html`
  - `reports/site/reading/repo_scout/rank107_mtf_chop_chargedup_clean_replication.html`
- 可复现脚本：
  - `scripts/build_rank107_mtf_chop_clean_replication.py`

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 默认从 `Rank 107` 切到 **`prebreak higher-low pressure ladder context gate`**
- 当前 active Scout 顺序应改写为：
  1. `prebreak higher-low pressure ladder context gate`
  2. `fresh paper / repo intake reserve（RECENT_PAPER_SEEDS / quant_digests / validated shortlist）`
  3. `旧 P1 evidence_pool`
  4. `Rank 17 low-frequency health-check fallback`
  5. `tiny-live plumbing`
- 当前最新 `Next 3`：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 prebreak higher-low pressure ladder context gate 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 prebreak higher-low pressure ladder context gate guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前仍是 `waiting_not_due`
- `python3 scripts/build_rank107_mtf_chop_clean_replication.py`
  - 成功生成 rank107 clean replication artifact 与 reader-facing 页面
- 回读以下文件，确认已写入成功：
  - `reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/verdict_summary.csv`
  - `reports/site/reading/repo_scout/rank107_mtf_chop_chargedup_clean_replication.html`
  - `docs/TODO.md`

## 备注
- 本轮没有并开 `prebreak ladder`、fresh intake reserve 或任何 `P3 continuity`
- 本轮没有整理或覆盖无关脏文件
- 工作区仍有大量历史脏文件；本轮只做 selective write-back
