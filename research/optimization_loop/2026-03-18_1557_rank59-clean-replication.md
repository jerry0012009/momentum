# 2026-03-18 15:57 UTC — Rank 59 / Ichimoku Kijun + cloud-side 最小 clean replication

## 为什么这轮轮到它
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍没有新的 `due-now / overdue` lane：
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- 因此 `Paper Seat / EMA` 仍是 **`running paper / waiting_not_due`**，不能把整桌误判成等待态。
- 顶板上一轮（`2026-03-18 15:37 UTC`）已经把 **`Rank 59 / Ichimoku Kijun + cloud-side continuation gate`** 冻结为 `guard-passed / admit_to_clean_replication_queue`；按当前合法顺序，这轮应直接执行 **`Run 2 / Rank 59 minimal clean replication`**。
- `manual_narrow_paper_last_run_summary.json` 最新一次虽已有 `new_closed_trades_appended=1`，但当前仍不足以越过 `Scout Seat` 默认优先级；尤其在 `EMA = waiting_not_due` 且 `Rank 59` 仍有唯一一手合法预算时，不应回头挤占受限的 `P3 continuity` 预算。

## 开轮检查（repo / 最近 runs / 脏文件 / 当前席位）
- repo 状态：工作区存在大量既有脏文件与未跟踪产物，本轮不做混提 commit。
- 最近 optimization runs：
  - `2026-03-18_1537_rank59-source-intake.md`
  - `2026-03-18_1524_rank58-clean-replication.md`
  - `2026-03-18_1505_rank58-source-intake.md`
- 当前席位：
  - `Paper Seat = EMA`：`running paper / waiting_not_due`
  - `Live Seat`：暂空
  - `Scout Seat`：本轮主资源位 = `Rank 59`
- 脏文件风险：本轮只新增 `Rank 59` clean replication 相关脚本 / artifact / 页面 / TODO 顶板写回 / 本日志，避免混入其他旧脏改动。

## 本轮主点（只认领 1 个主点）
完成 **`Rank 59 / Ichimoku Kijun + cloud-side continuation gate`** 的唯一那手最小 clean replication。

### 本轮冻结口径
- 只复用 `BTC/ETH/SOL 120d 15m` 本地 cache；不追新 bar。
- 只在三条现有 archetype 上验证：
  - `ema_psar_long`
  - `fib_retest_long`
  - `breakout_short`
- 五臂固定为：
  - `base`
  - `kijun_only`
  - `cloud_side`
  - `kijun+cloud_side`
  - `kijun+cloud_side+ADX floor`
- 统一冻结到：
  - `signal 当根及之前数据`
  - `next-bar open`
  - `no-overlap`
  - `hold 8 bars`
- 当前不偷渡：`Chikou / RSI / 时间过滤 / BE / trailing`。

## 做了什么改动
### 新增脚本
- `scripts/build_rank59_ichimoku_kijun_cloud_clean_replication.py`

### 新增 artifact
- `reports/artifacts/scout_rank59_ichimoku_kijun_cloud_15m/signal_windows.csv`
- `reports/artifacts/scout_rank59_ichimoku_kijun_cloud_15m/trade_log.csv`
- `reports/artifacts/scout_rank59_ichimoku_kijun_cloud_15m/asset_summary.csv`
- `reports/artifacts/scout_rank59_ichimoku_kijun_cloud_15m/overall_summary.csv`
- `reports/artifacts/scout_rank59_ichimoku_kijun_cloud_15m/time_pockets.csv`
- `reports/artifacts/scout_rank59_ichimoku_kijun_cloud_15m/setup_compare.csv`

### Reader-facing 落点
- `reports/site/factors/scout_rank59_ichimoku_kijun_cloud_15m/report.html`
- `reports/site/reading/repo_scout/rank59_ichimoku_kijun_cloud_clean_replication.html`

### Authoritative writeback
- `docs/TODO.md` 顶部 `Next 3 bot3 runs` 已追加 `2026-03-18 15:57 UTC` 补充，冻结本轮 hard verdict 与下一轮排班。

## 核心结果（6bps/side）
### 1) setup-level 对比
- `ema_psar_long`
  - `base ≈ -3.67%`
  - `kijun_only ≈ -4.71%`
  - `cloud_side ≈ -1.18%`
  - `kijun+cloud_side ≈ -0.87%`
  - `kijun+cloud_side+ADX ≈ -2.09%`
- `fib_retest_long`
  - `base ≈ +1.17%`
  - `kijun_only ≈ +0.22%`
  - `cloud_side ≈ -0.83%`
  - `kijun+cloud_side ≈ +0.11%`
  - `kijun+cloud_side+ADX ≈ 0.00%`
- `breakout_short`
  - `base ≈ -3.55%`
  - `kijun_only ≈ -3.70%`
  - `cloud_side ≈ -3.26%`
  - `kijun+cloud_side ≈ -4.00%`
  - `kijun+cloud_side+ADX ≈ -2.72%`

### 2) 四个便宜指标怎么读
#### `trade_count_retention`
- `ema_psar_long / kijun+cloud_side ≈ 59.05%`
- `fib_retest_long / kijun+cloud_side ≈ 6.06%`
- `breakout_short / kijun+cloud_side ≈ 77.61%`
- 读法：在 `fib_retest_long` 上已经明显像切样本，不够诚实。

#### `4~8 bar failure rate`
- `ema_psar_long`：`base fail4 ≈ 81.90%`，`combo fail4 ≈ 77.47%`
- `fib_retest_long`：`base fail4 ≈ 81.82%`，`combo fail4 ≈ 50.00%`
- `breakout_short`：`base fail4 ≈ 80.65%`，`combo fail4 ≈ 81.26%`
- 读法：
  - `EMA-PSAR long` 上确实有一点 shared continuation gate 味道；
  - `Fib retest` 的 fail4 改善主要伴随 retention 崩塌；
  - `breakout_short` 基本没有改善。

#### `winner_truncation_rate`
- `ema_psar_long / combo ≈ 34.80%`
- `fib_retest_long / combo ≈ 93.33%`
- `breakout_short / combo ≈ 32.50%`
- 读法：`Fib retest` 这条线把 base 赢家也切掉了大半，说明不是“更聪明地过滤”，更像“过滤得过头”。

#### `post-cost return`
- 只有 `ema_psar_long` 的 `cloud_side / combo` 显著少亏；
- `fib_retest_long` 虽然 `combo` 仍为微正，但已经几乎没有样本；
- `breakout_short` 没有被修好。

## 当前硬结论
- **`Rank 59 / Ichimoku Kijun + cloud-side continuation gate = P1 weak candidate / evidence pool`**。
- 更直白地说：
  - 它不是纯幻觉，至少在 `ema_psar_long` 上有一点 shared continuation / avoid-chop 价值；
  - 但当前改善还不够统一，尤其 `fib_retest_long` 明显靠砍样本，`breakout_short` 也没有被修好；
  - 所以这条线当前更诚实的状态不是升格，而是进 **`P1`**，只配再拿 **1 次便宜诚实检查**，默认优先 `time stability`。

## 下一轮只允许做什么
- 若下一轮 `EMA` 仍 `waiting_not_due`：
  - 只允许给 `Rank 59` 做 **1 次便宜诚实检查**；
  - 默认优先 `time stability`（按时间三分桶，不重下新数据、不加新复杂过滤）；
  - 核心问题只问：`EMA-PSAR long` 上这点改善是不是稳定存在，还是只是 pocket-level 偶然收敛。
- 若 cheap check 后仍不能更诚实地升格，就直接 `park`，然后回到 fresh intake（`continuation fail-fast overlay > pullback-quality / CQI > fresh pool 其他 source`）。

## 最小验证
- 成功执行：`python3 scripts/build_rank59_ichimoku_kijun_cloud_clean_replication.py`
- stdout：`verdict=P1 weak candidate / evidence pool`
- 已确认产物存在：
  - `reports/artifacts/scout_rank59_ichimoku_kijun_cloud_15m/overall_summary.csv`
  - `reports/site/factors/scout_rank59_ichimoku_kijun_cloud_15m/report.html`
  - `reports/site/reading/repo_scout/rank59_ichimoku_kijun_cloud_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板包含 `2026-03-18 15:57 UTC` 补充。

## Git / 风险备注
- 工作区有大量与本轮无关的既有脏文件和未跟踪产物；本轮未提交，避免混提。
- 本轮只做了最小必要写回，不涉及外部交易、live seat 重开或重型下载。
