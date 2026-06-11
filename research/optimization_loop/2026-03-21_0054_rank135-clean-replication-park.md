# 2026-03-21 00:54 UTC — Rank 135 最小 clean replication → park，并把 Scout Seat 切回 fresh intake

## 本轮先做的桌面检查（按 TRADING DESK BOARD）
- `git status --short`：repo 仍有大量与本轮无关脏文件，继续 **不混提**。
- 先执行 `Run 1 / EMA due-check first`：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前仍无 `due-now / overdue` lane；最靠前仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `23.2h` 后到点。
  - 备注：脚本按 `require-due` 如实返回非零退出，但已完成守门输出；因此本轮合法主位继续从 `Paper Seat` 切去 `Scout Seat`。
- 再核对顶板：`Run 2` 明确要求给 `Rank 135 / retest tolerance stop decoupling gate` **仅 1 次最小 clean replication**；不得回头磨 hosted `P3 continuity`，也不该继续扩旧 `budget-used P1`。

## 3.5 Active Scout 边际价值比较（本轮只取 1 条）
- `Rank 135`：当前唯一处于 `guard-passed / admit_to_clean_replication_queue` 的 fresh Scout，对桌面排序影响最大。
- `Rank 127 / 125 / 112 / 111`：都属于旧 `P1 / budget used`，当前不如先把 `Rank 135` 直接判 `park / keep_P1 / promote_P2` 更值钱。
- `Rank 122 / 2 / 17 / 29 / 32b`：仍是 `P3 continuity / sidecar only`，当前没有新的 status-changing event。
- `tiny-live plumbing`：按顶板只能排在 `Scout Seat` 之后。

**结论：本轮继续认领 `Rank 135` 的最小 clean replication，边际价值最高。**

## 本轮主点：Rank 135 / retest tolerance stop decoupling gate 最小 clean replication

### 新增脚本
- `scripts/build_rank135_retest_tolerance_clean_replication.py`

### 新增 artifact
- `reports/artifacts/scout_rank135_retest_tolerance_stop_decoupling_15m/threshold_config.csv`
- `reports/artifacts/scout_rank135_retest_tolerance_stop_decoupling_15m/overall_summary.csv`
- `reports/artifacts/scout_rank135_retest_tolerance_stop_decoupling_15m/asset_summary.csv`
- `reports/artifacts/scout_rank135_retest_tolerance_stop_decoupling_15m/setup_summary.csv`
- `reports/artifacts/scout_rank135_retest_tolerance_stop_decoupling_15m/trade_log.csv`
- `reports/artifacts/scout_rank135_retest_tolerance_stop_decoupling_15m/scout_promotion_scorecard.csv`
- `reports/artifacts/scout_rank135_retest_tolerance_stop_decoupling_15m/summary.json`

### 新增 reader-facing 页面
- `reports/site/factors/scout_rank135_retest_tolerance_stop_decoupling_15m/report.html`
- `reports/site/reading/repo_scout/rank135_retest_tolerance_stop_decoupling_clean_replication.html`

## 固定口径（只做最小诚实检查）
- 样本来源：复用 `scout_rank76_intraday_clock_polarity_15m` 里的 `BTC/ETH/SOL` 15m baseline 信号与 feature frame。
- setup 冻结：`breakout_short / ema_psar_long / fib_retest_long`。
- 统一执行：`next-bar open` 入场、`hold 8 bars`、按资产做 `no-overlap` 去重。
- 诚实拆分：全样本按时间做 `60% train / 40% test`。
- decoupled tolerance 候选：`0.3% / 0.5% / 0.8%`，只按 train 段 `6bps per side` 选 1 个 tolerance，再拿去 test 段比较 baseline vs gate。
- 成本口径：`6 / 10 / 15 bps per side`。

## 关键结果（test 段）
### 1) tolerance 选择
- train 段三个候选里，最不差的是 **`0.8%`**：
  - `0.3%`：`41 trades`，`mean = -22.96 bps`
  - `0.5%`：`69 trades`，`mean = -13.06 bps`
  - `0.8%`：`86 trades`，`mean = -6.30 bps`
- 这已经说明：若想让这条线站住，当前必须依赖 **最宽的几何容差**。

### 2) overall（test）
- baseline：`75 trades`
  - `6bps = -1.86 bps`
  - `10bps = -9.86 bps`
  - `15bps = -19.86 bps`
- decoupled tolerance gate（`0.8%`）：`56 trades`，保留 `74.7%` 交易
  - `6bps = -0.26 bps`（`delta = +1.60 bps`）
  - `10bps = -8.26 bps`（`delta = +1.60 bps`）
  - `15bps = -18.26 bps`（`delta = +1.60 bps`）

### 3) by asset（test / 6bps）
- `BTC`：baseline `-10.62 bps` → gate `-14.77 bps`（`delta = -4.16 bps`）
- `ETH`：baseline `-30.87 bps` → gate `+0.32 bps`（`delta = +31.18 bps`）
- `SOL`：baseline `+30.21 bps` → gate `+18.65 bps`（`delta = -11.57 bps`）

### 4) by setup（test / 6bps）
- `breakout_short`：baseline `-48.76 bps` → gate `-59.70 bps`（`delta = -10.94 bps`）
- `ema_psar_long`：baseline `+29.90 bps` → gate `+34.91 bps`（`delta = +5.01 bps`）
- `fib_retest_long`：baseline `-22.04 bps` → gate `-22.04 bps`（`delta = 0.00 bps`）

## 读法（为什么直接 park）
这条线不是“完全零信息”，但它也没有变成 desk 现在要的 shared gate：
1. **improvement 太窄**：test 段的增量几乎只来自 `EMA long / ETH` pocket；
2. **breakout_short 继续恶化**：说明它没帮到当前 desk 最在意的结构侧 admission，反而更差；
3. **跨资产仍分裂**：`ETH` 改善很大，但 `BTC` 变差、`SOL` 也被削弱；
4. **成本后仍整体为负**：虽然三档成本下都比 baseline 好约 `+1.6 bps`，但 gate 本身在 `6/10/15bps` 下仍分别是 `-0.26 / -8.26 / -18.26 bps`，不够支撑升格。

## 轻量 Scorecard
- `usefulness = 1/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 0/3`
- `deployability = 0/3`
- hard-fail flags：
  - `rule_unclear = false`
  - `leakage_risk = false`
  - `post_cost_collapse = true`
  - `too_sparse = false`
  - `single_pocket_dependency = true`

## 本轮硬结论
**`Rank 135 / retest tolerance stop decoupling gate = park / evidence pool`。**

不是因为它完全没 uplift，而是因为：
- uplift 不够 desk-wide；
- `breakout_short` 继续恶化；
- 结果更像局部长侧 pocket，而不是可共享的 admission gate；
- 因此不值得升到 `P2`，也不值得继续占 `P1` 主位。

## 紧邻子点：最小 write-back 到 desk board
已更新 `docs/TODO.md` 顶部：
- `Scout Seat 当前主点` 切回 **`fresh intake slot（next rank on pickup）`**；
- `Active Scout` 里把 `Rank 135` 下放到 `P0 / park / evidence pool`；
- `Next 3 runs` 改为：`Run 2 = fresh intake（拿到对象先分配 next Rank）`，`Run 3 = 新 Rank guard-pass 后再给 1 次最小 clean replication`；
- `最近关键 evidence` 补入本轮 `Rank 135 clean replication → park` 结论。

## 验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank135_retest_tolerance_clean_replication.py`
- `bash scripts/publish_homepage_index.sh`

## commit
- 未提交。
- 原因：当前工作区存在大量与本轮无关脏文件，不适合做安全 selective commit。
