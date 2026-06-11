# 2026-03-20 07:35 UTC · Rank 112 / basis dislocation short veto clean replication

## Run 1 -> Run 2 执行
- Run 1：按 desk 顶板先检查 `EMA due-check first`
- 结果：当前 `EMA = waiting_not_due`
  - `ema_paper_trading_due_guardrail_snapshot.csv` 显示当前全 desk 无 `due-now / overdue` lane
  - 最近 due：`美股 1d+1wk -> 2026-03-20 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-21 00:00 UTC`、`创业板ETF 1d -> 2026-03-23 07:00 UTC`
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T07:24:44Z` 仍为 `new_closed_trades_appended=0`
- 因此按当前 `TRADING DESK BOARD` 的 authoritative `Next 3`，本轮合法主动作继续落在 `Scout Seat`，且只允许给 **`Rank 112 / basis dislocation short veto`** 做那 1 次最小 clean replication。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short` 仍显示大量与本轮无关的脏文件（不安全混提）
- 最近 optimization logs：
  - `2026-03-20_0715_rank112-basis-dislocation-intake.md`
  - `2026-03-20_0652_rank111_event_clock_clean_replication.md`
  - `2026-03-20_0614_rank110-time-stability-park.md`
- 当前席位直读：
  - `Paper Seat = EMA / 创业板ETF 1d primary anchor / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前 `Scout Seat = Rank 112 / basis dislocation short veto`

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 112 / basis dislocation short veto`**
   - 上轮已完成 `source intake + 两条轻量诚实守门`，这轮正好轮到唯一允许的那 1 次最小 clean replication。
   - 它直接服务 desk 当前最缺的 breakout-short 最后一道问题：**这次下破到底该不该追空。**
2. **`alpha-beta abstain / profit-window`**
   - 仍是紧邻后备，但只有在 `Rank 112` 这轮 clean replication 完成后，才应上位接手 Scout 主资源。
3. **`Rank 111 / abnormal-return event clock`**
   - 已是 `P1 evidence_pool / budget used`，这轮不该回头续命。

结论：本轮只认领 `Rank 112` 的最小 clean replication，不并开 `alpha-beta`，也不回头挤占 `P3 continuity`。

## 本轮认领
- 主点：`Rank 112 / basis dislocation short veto` 的 **1 次最小 clean replication**
- 紧邻子点：同步 reader-facing 落点、顶板顺序刷新

## 本轮动作
- 新增脚本：`scripts/build_rank112_basis_dislocation_clean_replication.py`
- 执行：`python3 scripts/build_rank112_basis_dislocation_clean_replication.py`
- 数据口径：
  - 价格：固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache
  - 衍生品公开数据：`Binance USDⓈ-M premiumIndexKlines + openInterestHist`
- 统一冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- base setup：固定复用同一套 `breakout_short` 触发（不是新造独立 alpha）
- 三臂对照：
  - `baseline`
  - `basis_extreme_veto`：若 `basis_pct_30d <= 10%` 则 `skip short`
  - `basis_extreme_plus_oi_veto`：若 `basis_pct_30d <= 10% 且 oi_delta_1h <= 0` 则 `skip short`
- 指标：`false_break@4/8/12`、`post-cost expectancy`、`trade_count retention`、`MAE/MFE`

## 当前硬结论
**`Rank 112 = keep_P1 / honest veto signal`**。

翻成人话：
- **“极端负 basis 时别继续追空”** 这件事本身确实有一点 honest veto 味道；
- 但把它再收成 **`极端负 basis + oi_delta_1h <= 0`** 并没有带来额外增益，当前更像多余噪声；
- 因此它当前只够留在 **`P1 weak candidate / evidence_pool`**，不足以升到 `P2 / paper candidate pool`，更不配抢 `Live Seat`。

## 关键结果
### desk 级（6bps/side）
- `baseline`
  - `mean_total_return≈-3.38%`
  - `positive_asset_ratio=0/3`
  - `false_break_8bars≈63.60%`
  - `trade_count_retention=100.00%`
- `basis_extreme_veto`
  - `mean_total_return≈-3.10%`
  - `positive_asset_ratio=0/3`
  - `false_break_8bars≈61.82%`
  - `trade_count_retention≈85.40%`
- `basis_extreme_plus_oi_veto`
  - `mean_total_return≈-3.90%`
  - `positive_asset_ratio=0/3`
  - `false_break_8bars≈64.39%`
  - `trade_count_retention≈98.61%`

### 资产级（6bps/side）
- `BTC`
  - `baseline≈-1.25%`
  - `basis_extreme_veto≈-3.46%`
  - `basis_extreme_plus_oi_veto≈-1.25%`
- `ETH`
  - `baseline≈-5.01%`
  - `basis_extreme_veto≈-4.69%`
  - `basis_extreme_plus_oi_veto≈-5.01%`
- `SOL`
  - `baseline≈-3.88%`
  - `basis_extreme_veto≈-1.14%`
  - `basis_extreme_plus_oi_veto≈-5.45%`

### veto 读法
- `basis_extreme_veto` 在 6bps 下共 veto：`BTC=2`、`ETH=2`、`SOL=5`
- `basis_extreme_plus_oi_veto` 在 6bps 下只额外触发 `SOL=1` 次 veto
- 这说明当前最有信息量的是 **basis 极端本身**；`oi_delta_1h <= 0` 这层在当前样本里既没形成更有力的 bad-trade 指向，也没提供足够额外过滤。

## 对顶板的直接影响
- `Paper Seat = EMA / 创业板ETF 1d primary anchor / waiting_not_due`
- `Live Seat = 暂空`
- `Rank 112` 应从 `P1 weak candidate / guard-passed / admit_to_clean_replication_queue` 更新为：**`P1 weak candidate / evidence_pool / budget used`**
- 当前更诚实的 active Scout 顺序：
  1. `alpha-beta abstain / profit-window`（`P0 / fresh paper+repo reserve / ex-ante translation honesty gate first`）
  2. `Rank 112 / basis dislocation short veto`（`P1 weak candidate / evidence_pool / budget used`）
  3. `Rank 111 / abnormal-return event clock`（`P1 evidence_pool / budget used`）
  4. `旧 P1 evidence_pool`
  5. `已 park 的 P0`
  6. `P3 continuity sidecar`
- 当前 `P2` 仍空、`P4` 仍空。
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check first（若 due-now / overdue，先做 guarded refresh）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 alpha-beta abstain / profit-window 1 次 ex-ante honesty gate source intake`
  3. `Run 3 = 若 alpha-beta guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则回到 fresh intake（优先 RECENT_PAPER_SEEDS / quant_digests / validated shortlist），只有 fresh intake 也 exhausted 后才允许 tiny-live plumbing fallback`

## 本轮交付（deployable artifact）
- script：`scripts/build_rank112_basis_dislocation_clean_replication.py`
- artifacts：
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/veto_reason_summary.csv`
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/time_bucket_summary.csv`
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/trade_log.csv`
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/summary.json`
- public-data cache：
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/public_data_cache/*`
- reader-facing 页面：
  - `reports/site/factors/scout_rank112_basis_dislocation_short_veto_15m/report.html`
  - `reports/site/reading/repo_scout/rank112_basis_dislocation_short_veto_clean_replication.html`
- 顶板刷新：`docs/TODO.md`

## 最小验证
- 回读：
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/summary.json`
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/veto_reason_summary.csv`
  - `reports/site/factors/scout_rank112_basis_dislocation_short_veto_15m/report.html`
  - `docs/TODO.md`

## 风险 / 边界
- 这轮只完成了最小 clean replication，**没有**进入 `Light Stability Pack`。
- 当前最诚实的读法不是“basis + OI 形成了更强 veto”，而是：**basis 极端本身值得保留为 P1 证据，但 OI 负增量这层暂时不值得继续包装。**
- 当前工作区有大量与本轮无关的脏文件，因此不安全混提。

## Commit hash
- 未提交。
- 原因：工作区存在大量无关脏文件，本轮只做局部脚本 / 产物 / 顶板回写，不适合混提。
