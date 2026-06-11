# 2026-03-19 19:53 UTC — Rank 98 Fib placebo honesty clean replication -> park

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 美股 1d+1wk：约 `10 分钟` 后到点
  - Crypto 1d+1wk：约 `4.2 小时` 后到点
  - 创业板ETF 1d：约 `11.2 小时` 后到点
- 因此按当前 `Next 3`，本轮合法主动作切到 Run 2：`Rank 98 / Fib placebo-zone honesty gate` 的 **1 次最小 clean replication**。

## 开轮检查
- 已检查 repo 脏区：`git status --short` 仍有大量与本轮无关的脏文件，本轮不混提。
- 已检查最近 optimization logs：最新到 `2026-03-19_1928_rank98-fib-placebo-intake.md`。
- 已检查当前 seat 状态：`Paper Seat = EMA / running paper / waiting_not_due`，`Live Seat = 暂空`，`P3 continuity` 无新的 status-changing event。

## 本轮认领
- 主点：`Rank 98 / Fib placebo-zone honesty gate`
- 紧邻子点：把 hard verdict 与 `Next 3` 最小写回 `docs/TODO.md`

## 本轮新增 / 执行
- 新增脚本：`scripts/build_rank98_fib_placebo_clean_replication.py`
- 固定口径：`BTC/ETH/SOL | 120d | 15m | signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 比较四臂：
  - `fib_exact`
  - `fib_zone_015`
  - `fib_zone_030`
  - `placebo_zone_mean`（固定随机种子 `20260319`，24 个非 Fib ratio，预先排除 Fib 邻域）

## 交付物
### artifact
- `reports/artifacts/scout_rank98_fib_placebo_honesty_15m/overall_summary.csv`
- `reports/artifacts/scout_rank98_fib_placebo_honesty_15m/overall_summary_primary_6bps.csv`
- `reports/artifacts/scout_rank98_fib_placebo_honesty_15m/asset_summary_primary_6bps.csv`
- `reports/artifacts/scout_rank98_fib_placebo_honesty_15m/placebo_ratio_summary.csv`
- `reports/artifacts/scout_rank98_fib_placebo_honesty_15m/meta.json`

### reader-facing 落点
- `reports/site/factors/scout_rank98_fib_placebo_honesty_15m/report.html`
- `reports/site/reading/repo_scout/rank98_fib_placebo_honesty_clean_replication.html`

## 硬结论
**`Rank 98 = park`**。

换成人话：
- 这轮最小 clean replication 没证明 `0.618` 本身比一批非 Fib placebo zone 更特别。
- `fib_exact` 不是完全失效，但 `fib_zone` 没把它抬成更强独立 edge；更诚实的读法是 **Fib 更像坐标系 / retrace scaffold**，而不是值得继续占 Scout 主资源的 ratio-edge。

## 关键读数（6bps/side）
### Desk 总体
- `fib_exact`
  - `mean_total_return ≈ +3.66%`
  - `positive_asset_ratio = 2/3`
  - `mean_trades ≈ 24.0`
  - `mean_post_cost_expectancy ≈ +0.163%`
  - `mean_false_rebreak_4bars_rate ≈ 67.88%`
- `fib_zone_015`
  - `mean_total_return ≈ +3.40%`
  - `positive_asset_ratio = 2/3`
  - `mean_trades ≈ 24.3`
  - `mean_post_cost_expectancy ≈ +0.153%`
  - `mean_false_rebreak_4bars_rate ≈ 68.08%`
- `fib_zone_030`
  - `mean_total_return ≈ +3.36%`
  - `positive_asset_ratio = 2/3`
  - `mean_trades ≈ 24.7`
  - `mean_post_cost_expectancy ≈ +0.152%`
  - `mean_false_rebreak_4bars_rate ≈ 68.27%`
- `placebo_zone_mean`
  - `mean_total_return ≈ +4.75%`
  - `positive_asset_ratio = 3/3`
  - `mean_trades ≈ 66.3`
  - `mean_post_cost_expectancy ≈ +0.093%`
  - `mean_false_rebreak_4bars_rate ≈ 47.92%`

### 为什么直接 park
1. **Fib 不是明显优于 placebo**：`fib_zone_030 - placebo_zone_mean` 的 `mean_post_cost_expectancy` 只剩 `≈ +0.059%`，不够支撑继续把 Fib 写成独立 ratio-edge。
2. **zone 放宽没有带来独立增益**：`fib_exact -> fib_zone_015 -> fib_zone_030` 的 expectancy 不是增强，反而轻微走弱。
3. **placebo 也能得到类似甚至更宽的“好看结果”**：说明这里更像 generic retrace geometry，而不是 `0.618` 特有信息。
4. **当前主问题已回答**：本轮要解决的是 honesty gate，不是把 Fib 线包装得更漂亮。这个问题已经有足够诚实的否定答案。

## 对交易台指挥板的影响
- `Paper Seat`：继续 **`EMA / running paper / waiting_not_due`**
- `Live Seat`：继续空
- `Scout Seat`：`Rank 98` 本轮 clean replication 后，**直接压回 park / evidence pool**
- 当前 active Scout 顺序：
  1. `CLV asymmetric admission layer reserve`（source intake next；进入 queue-facing 时先拿 `Rank 99`）
  2. `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
  3. `Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 park`
  4. `P3 continuity`
  5. `tiny-live plumbing`

## 对 Next 3 的直接 handoff
- `Run 1 = EMA due-check only`
- `Run 2 = 若 EMA 仍 waiting_not_due，则切 CLV asymmetric admission layer reserve 的 source intake（进入 queue-facing 时先拿 Rank 99）`
- `Run 3 = 若 CLV reserve guard-pass，则只给 1 次最小 clean replication；若 CLV 也 hard-fail / exhausted，则再按 7.10 认领 1 条新的 5m / 15m paper-repo source intake`

## 验证与边界
- 只做最小必要验证：本地 cache、单次 clean replication、主口径 `6bps/side`（同时附带 `10/15bps` 成本表）
- 未追新 completed bar、未做重型下载、未打开 `P3 continuity`
- 当前 git 工作区仍有大量与本轮无关的脏文件；本轮未 commit，避免混提
