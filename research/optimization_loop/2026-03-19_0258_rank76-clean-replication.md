# 2026-03-19 02:58 UTC｜Rank 76 / intraday clock polarity + event blackout gate minimal clean replication（park）

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 76 minimal clean replication`
- 紧邻子点：`TODO` 顶板 `Next 3 bot3 runs` 顺序刷新

## 开始前检查
- `Run 1 / EMA due-check`：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 当前无 `due-now / overdue` lane；最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 继续是 `running paper / waiting_not_due`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended=0`，本轮没有新的 `P3 status-changing event` 值得回头挤占 continuity。
- 顶板当前权威顺序：`Run 1 = EMA due-check only -> Run 2 = Rank 76 minimal clean replication -> Run 3 = fresh paper / repo source re-rank（默认 one-regime-per-session overlay 优先）`。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 76` clean-replication script、artifact、reader-facing 页面、`TODO` 写回与本轮日志，不做混提。

## 为什么这轮仍然是 Rank 76
这轮先按板子显式比较 active Scout 候选的边际价值：
1. `Rank 76 / intraday clock polarity + event blackout gate`
2. `one-regime-per-session overlay`
3. `Rank 35b`
4. `Rank 16b`
5. `tiny-live plumbing`

之所以先给 `Rank 76` 这唯一那手 clean replication：
1. 它是上一轮刚通过两条轻量诚实守门的 queue-facing shared gate；
2. 它直接服务 `ema_psar_long / fib_retest_long / breakout_short` 三条当前 desk archetype；
3. 板子已经明确写死：若 `EMA` 仍 `waiting_not_due`，此轮合法动作就是给它跑最小 clean replication，而不是跳去别的 fresh intake。

## 这轮冻结的最小实验
- 样本：固定复用 `BTC/ETH/SOL 120d 15m` cache（不额外追重型下载）。
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`。
- archetype：`ema_psar_long / fib_retest_long / breakout_short`。
- 三臂对照：
  1. `baseline`
  2. `polarity_only`
  3. `polarity_plus_blackout`
- 小时极性实现：
  - 先把 15m 合成 `1h`；
  - 对每个 UTC 小时单独，用过往同小时的 `hour_ret × next_hour_ret` 做滚动统计；
  - `t-stat >= 1.96 且均值 > 0` 记为 `continuation`；
  - `t-stat <= -1.96 且均值 < 0` 记为 `reversal`；
  - 否则 `neutral`。
- gate 映射：
  - `ema_psar_long`、`breakout_short` 只在 `continuation` 小时放行；
  - `fib_retest_long` 只在 `reversal` 小时放行；
  - `polarity_plus_blackout` 再叠一层 `FOMC ±2h` veto。

## 关键结果（6bps / side）
### 主读法：`polarity_plus_blackout`
- `ema_psar_long ≈ 0.00% / retention≈0.00% / false_break≈-`
- `fib_retest_long ≈ 0.00% / retention≈0.00% / false_break≈-`
- `breakout_short ≈ -0.06% / retention≈4.17% / false_break≈66.67%`

### baseline 对照
- `ema_psar_long ≈ -5.34%`
- `fib_retest_long ≈ +0.88%`
- `breakout_short ≈ -2.58%`

### 最值得写下来的诚实信息
1. 改善看起来主要来自**几乎把交易全砍掉**，不是来自更干净地挑出一批仍能活下来的样本。
2. `ema_psar_long` 与 `fib_retest_long` 在当前极性门槛下直接缩到 **0 笔**，说明这条 gate 现在更像“默认 neutral / 不给票”，不是可用的 shared allow-deny spine。
3. `breakout_short` 虽从 `-2.58%` 收到 `-0.06%`，但 retention 只剩 **约 4.17%**，且 false-break 反而升到 **66.67%**，不够诚实。
4. `blackout` 在当前样本里几乎没带来额外信息量；当前结果主要由 `polarity` 本身决定。
5. `hourly_polarity_summary.csv` 也直观说明了问题：绝大多数小时仍然落在 `neutral`，少数 `continuation / reversal` pocket 稀薄且跨资产不稳。

## Hard verdict
**`Rank 76 / intraday clock polarity + event blackout gate = park / evidence pool`**

## 为什么是这个 verdict
- 它没有通过“别靠砍单伪改善”的最小诚实门槛；
- 主改善几乎都来自把样本削到接近没有，而不是在合理 retention 下提升生存率；
- `Fib` 与 `EMA` 两条线都没留下可继续 cheap-check 的交易密度；
- 因此这条线当前更像 `method note / evidence pool`，而不是 `P1 weak candidate`。

## 本轮新增产物
1. Clean replication script：
   - `scripts/build_rank76_intraday_clock_polarity_clean_replication.py`
2. Artifact：
   - `reports/artifacts/scout_rank76_intraday_clock_polarity_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank76_intraday_clock_polarity_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank76_intraday_clock_polarity_15m/time_pocket_summary.csv`
   - `reports/artifacts/scout_rank76_intraday_clock_polarity_15m/hourly_polarity_summary.csv`
   - `reports/artifacts/scout_rank76_intraday_clock_polarity_15m/trade_log.csv`
3. Reader-facing 页面：
   - `reports/site/factors/scout_rank76_intraday_clock_polarity_15m/report.html`
   - `reports/site/reading/repo_scout/rank76_intraday_clock_polarity_clean_replication.html`
4. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`

## 对交易台顺序的影响
- `Rank 76` 已消耗掉这唯一那手最小 clean replication，当前应诚实压回 `P0 park / evidence pool`。
- 当前 active Scout 候选顺序应切到：
  1. `one-regime-per-session overlay`
  2. `RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 source`
  3. `Rank 35b`
  4. `Rank 16b`
  5. `tiny-live plumbing`
- 更新后的 `Next 3`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = fresh paper / repo source re-rank（默认 one-regime-per-session overlay 优先）`
  3. `Run 3 = 只有 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 已实际运行：
  - `python3 /root/clawd/jerry/momentum/scripts/build_rank76_intraday_clock_polarity_clean_replication.py`
- 已确认以下输出文件存在：
  - `reports/site/factors/scout_rank76_intraday_clock_polarity_15m/report.html`
  - `reports/site/reading/repo_scout/rank76_intraday_clock_polarity_clean_replication.html`
  - `reports/artifacts/scout_rank76_intraday_clock_polarity_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank76_intraday_clock_polarity_15m/hourly_polarity_summary.csv`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 风险 / 边界
- 这轮用的是 `120d 15m` 现成 cache，而不是论文语义里更长的 `180d/365d` full sample；但按本轮目标，这已经足够回答“要不要继续给预算”。
- 当前实现只是最小迁移版 polarity gate；它不是对论文原始结果的完整复刻。
- 即便以后重开，也必须有会改变 verdict 的新证据（比如更长样本下保留合理 retention），而不是继续在当前 sparse polarity 映射上打转。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
