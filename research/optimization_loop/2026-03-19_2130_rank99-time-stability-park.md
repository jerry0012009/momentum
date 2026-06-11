# 2026-03-19 21:30 UTC · Rank 99 time stability -> park

## 本轮一句话
先按交易台要求执行 EMA due-check；确认 `Paper Seat` 仍是 `waiting_not_due` 后，只给 `Rank 99 / CLV asymmetric admission layer` 做了 **1 次 truly verdict-changing 的 Light Stability Pack（时间稳定性）**。结果：**park / evidence pool**，下一轮默认切 fresh repo intake（`fib-depth shallow-mid admission gate reserve`，进 queue-facing 时先拿 `Rank 100`）。

## 先检查的桌面状态
- repo dirty count：`1564`
- 当前分支：`main`
- 最近 optimization logs：
  - `2026-03-19_2053_rank99-clv-clean-replication.md`
  - `2026-03-19_2027_rank99-clv-intake.md`
  - `2026-03-19_2014_ema-us-due-refresh.md`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-19T21:02:24Z`：`new_closed_trades_appended=0`
- 本轮开始时 desk 读法：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = Rank 99 / CLV asymmetric admission layer（P1 / clean replication done / 1x Light Stability Pack next）`

## 执行顺序
### 1) Run 1：EMA due-check first
执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：脚本返回 `waiting_not_due`（exit code `2`），当前无 `due-now / overdue` lane；最靠前仍是：
- `Crypto 1d+1wk（BTC/ETH/SOL） | due_soon | 约 2.5 小时后到点`

结论：`Paper Seat` 本轮没有真实 due window 要消化，合法主动作切到 `Run 2`，不能空转。

### 2) Run 2：Rank 99 / CLV asymmetric admission layer · 时间稳定性
新增并执行：
```bash
python3 scripts/build_rank99_time_stability_check.py
```

数据口径：
- 完全复用 `reports/artifacts/quant_digests/zenoclaw_clv_proxy/event_log.csv`
- 不追新 bar，不改规则
- 每个 `asset × variant` 按时间顺序切成 `3` 个等样本 bucket
- 继续冻结在：`signal 当根及之前数据 + next-bar open + hold 4 bars + 12bps round-trip`

关注的主变体：
- `short_clv080`
- `short_clv070_plus_volume`
- `long_volume_only`
- `long_volume_plus_clv`

## 硬结论（hard verdict）
**`Rank 99 = park / evidence pool`**

原因很直接：
- `short_clv080`：仅 **`1/3`** 个正桶；最差桶 `mean_total_return≈-9.32%`
- `short_clv070_plus_volume`：仅 **`1/3`** 个正桶；最差桶 `≈-11.75%`
- `long_volume_only`：**`0/3` 正桶**
- `long_volume_plus_clv`：**`0/3` 正桶**

换成人话：
- strict CLV 的 short 改善不是完全假的，但主要是 **前段 pocket**；一做时间切片，中段 bucket 就重新显著转负。
- long 侧无论只加 volume 还是 volume+CLV，都没穿过时间稳定性，因此不能把 `high-close` 包装成 long continuation 充分条件。
- 所以这条线最多只留下 **short-biased bar-quality 线索**，不再配占 active Scout 主资源位。

## 关键产物
### artifact
- `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/time_stability_window_summary.csv`
- `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/time_stability_asset_window_summary.csv`
- `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/time_stability_verdict_summary.csv`
- `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/time_stability_summary.json`

### reader-facing
- `reports/site/factors/scout_rank99_clv_asymmetric_admission_15m/time_stability_check.html`
- `reports/site/reading/repo_scout/rank99_clv_asymmetric_admission_time_stability.html`

## 对交易台板子的影响
更新后桌面读法：
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat = fib-depth shallow-mid admission gate reserve（fresh repo intake next；进入 queue-facing 时先拿 Rank 100）`

更诚实的 active Scout 顺序：
1. `fib-depth shallow-mid admission gate reserve`（P0 / fresh repo intake reserve）
2. `3-step volume dry-down long-bias gate reserve`（P0 / fresh repo intake reserve）
3. `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`（P1 / budget used）
4. `Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 park / evidence pool`
5. `P3 continuity`
6. `tiny-live plumbing`

最新 `Next 3 bot3 runs`：
- `Run 1 = EMA due-check only（优先盯 Crypto 1d+1wk due_soon）`
- `Run 2 = 若 EMA 仍 waiting_not_due，则切 fib-depth shallow-mid admission gate reserve 的 source intake（进入 queue-facing 时先拿 Rank 100）`
- `Run 3 = 若 Rank 100 guard-pass，则只给它 1 次最小 clean replication；若 Rank 100 intake 直接 hard-fail / exhausted，则切 3-step volume dry-down long-bias gate reserve（拿 Rank 101）；只有 fresh source 这一层也 exhausted，才允许回退到旧 evidence_pool / park / P3 continuity`

## 本轮修改文件
- `scripts/build_rank99_time_stability_check.py`（新增）
- `docs/TODO.md`（更新最新 desk 补充与 Next 3）
- `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/time_stability_*`
- `reports/site/factors/scout_rank99_clv_asymmetric_admission_15m/time_stability_check.html`
- `reports/site/reading/repo_scout/rank99_clv_asymmetric_admission_time_stability.html`

## 备注
- 本轮没有去碰 `P3 continuity`，因为 `manual_narrow_paper` 最新 run 仍是 `new_closed_trades_appended=0`，不构成 status-changing 插队理由。
- 没有继续给 `Rank 99` 做 promote/keep 的近义收口，因为 truly verdict-changing 的时间稳定性已经明确给出 `park`。