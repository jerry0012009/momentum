# 2026-03-19 20:53 UTC — Rank 99 CLV asymmetric admission layer clean replication

## 本轮先核对的 desk 状态
- repo 工作区仍有大量与本轮无关的既有脏文件：`git status --short | wc -l = 1559`。
- 最近 optimization logs：
  - `2026-03-19_2027_rank99-clv-intake.md`
  - `2026-03-19_2014_ema-us-due-refresh.md`
  - `2026-03-19_1953_rank98-fib-placebo-clean-replication.md`
- 先实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：`waiting_not_due`
  - 当前无 `due-now / overdue` lane；最近 due 仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `3.2h` 后到点。
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-19T20:19:15Z`
  - `new_closed_trades_appended = 0`
  - 结论：当前没有需要 bot3 插队主资源处理的 `P3` 异常。

## 本轮只认领的主点
- **主点：`Scout Seat / Rank 99 / CLV asymmetric admission layer` 的 1 次最小 clean replication**
- 紧邻子点：把当前 top board 收口为 `Rank 99 = keep_P1 / evidence_pool`，并明确下一轮只允许给它 `1` 个 truly verdict-changing 的 `Light Stability Pack`。

## 为什么本轮还是 Rank 99
这轮先按顶板重新比较 active Scout 边际价值：
1. **Rank 99 / CLV asymmetric admission layer**
   - 上一轮 intake 已 guard-pass；本轮正好是顶板写死的 `Run 2 = Rank 99 minimal clean replication`
   - 它直接服务当前 desk 三条主线都缺的同一个语义问题：decision bar 到底要不要 close near edge，而且多空是否该不对称处理
2. **Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81**
   - 仍是 `P1 evidence_pool / budget used`
   - 本轮不该回头给旧 `P1` 续命
3. **Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94**
   - 当前都已是 `P0 park / evidence pool`
   - 只有 Rank 99 也 exhausted 后才该回 fresh source / fallback

## 本轮 clean replication 口径
- 数据：严格复用 `reports/artifacts/quant_digests/zenoclaw_clv_proxy/`
  - `BTC/ETH/SOL`
  - `120d`
  - `15m`
  - `next-bar open`
  - `hold 4 bars`
  - `12bps round-trip`
- 本轮不追新 bar，不改 signal，只把 intake 里的方向不对称假设真正落成最小 replication 对照。
- 复现比较臂：
  - `short_baseline`
  - `short_clv070`
  - `short_clv080`
  - `short_clv070_plus_volume`
  - `long_baseline`
  - `long_clv070_only`
  - `long_volume_only`
  - `long_volume_plus_clv`

## 最小结果
### short 侧
- `baseline mean_net_ret_h4 ≈ -5.89bps`
- `CLV>=0.70 ≈ -2.36bps`
- `CLV>=0.80 ≈ -0.43bps`
- `CLV>=0.70 + volume>=1.5 ≈ -1.21bps`
- 读法：strict CLV 确实把 short follow-up 的 after-cost 损失压缩到接近打平；其中 `CLV>=0.80` 最干净，`CLV+volume` 则给出更好的 `positive_asset_ratio≈66.67%`。

### long 侧
- `baseline mean_net_ret_h4 ≈ -12.61bps`
- `CLV-only ≈ -13.97bps`
- `volume-only ≈ -9.98bps`
- `volume+CLV ≈ -11.26bps`
- 读法：long 侧不能把 close-near-high 单独当 continuation 成立；比起 CLV，本轮仍然是 `volume/context` 更有用。

## 本轮 hard verdict
- **`Rank 99 / CLV asymmetric admission layer = keep_P1 / evidence_pool`**

### 为什么不是 promote_to_P2
1. short 侧虽然明显改善，但 best arm 也只是“接近打平”，不是足够硬的 desk-level shared edge。
2. long 侧 `CLV-only` 直接恶化，说明它不能被写成多空对称万能过滤。
3. 当前 clean replication 仍是公开 breakout proxy，不是 EMA / Fib / breakout-short 三条正式 archetype 的直连 deployment verdict。

### 为什么也不是直接 park
- 它至少证明了一个真实收获：**CLV 值得作为 short-biased admission / sizing 线索保留**。
- 因此更诚实的收口不是“这条线彻底没用”，而是：保留在 `P1 weak candidate`，但只再给 `1` 次 truly verdict-changing 的稳定性检查，不能无限续命。

## 产物
- script:
  - `scripts/build_rank99_clv_asymmetric_clean_replication.py`
- artifact:
  - `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/verdict_summary.csv`
  - `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/summary_snapshot.json`
- reader-facing:
  - `reports/site/factors/scout_rank99_clv_asymmetric_admission_15m/report.html`
  - `reports/site/reading/repo_scout/rank99_clv_asymmetric_admission_clean_replication.html`

## 对顶板的更新结论
- `Rank 99 = P1 weak candidate（clean replication done / 1x Light Stability Pack next）`
- 当前 `P2` 仍空，`P4` 仍空
- 最新 `Next 3`：
  1. `Run 1 = EMA due-check only（优先盯 Crypto 1d+1wk due_soon）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 99 1 个 truly verdict-changing 的 Light Stability Pack（默认时间稳定性）`
  3. `Run 3 = 若 Rank 99 时间稳定性后仍未 hard-fail，则直接做 promote_to_P2 vs keep_P1 收口；若直接 park / exhausted，则按 7.10 回 fresh source intake`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前还是 `waiting_not_due`
- `python3 scripts/build_rank99_clv_asymmetric_clean_replication.py`
  - 已成功写出 artifact 与两张 reader-facing 页面
- 读回 `docs/TODO.md`
  - 确认最新 supplement、Scout 分级与 `Next 3` 已写回

## 备注
- 本轮没有动用 `P3 continuity` 预算，也没有回头续磨旧 `P1 evidence_pool`。
- 本轮没有 commit；原因是工作区有大量与本轮无关的历史脏文件，不安全混提。
