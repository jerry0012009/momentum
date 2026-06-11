# 2026-03-19 19:28 UTC — Rank 98 Fib placebo honesty source intake

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 美股 1d+1wk：约 `32 分钟` 后到点
  - Crypto 1d+1wk：约 `4.5 小时` 后到点
  - 创业板ETF 1d：约 `11.5 小时` 后到点
- 因此按当前 `Next 3`，本轮切到 Run 2：`Fib placebo-zone honesty gate` source intake。

## Active Scout 候选边际比较（本轮先比较后认领）
- `Fib placebo-zone honesty gate`
- `CLV asymmetric admission layer reserve`
- `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
- `Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 park`
- `P3 continuity`
- `tiny-live plumbing`

结论：本轮主资源给 `Fib placebo-zone honesty gate`，不回头续命旧 evidence_pool。

## 本轮认领
- 主点：`Rank 98 / Fib placebo-zone honesty gate`
- 紧邻子点：无（未并行打开 CLV）

## 本轮交付（deployable artifact）
- source intake card：
  - `reports/artifacts/literature/scout_rank98_fib_placebo_honesty_source_intake_card.csv`
- reader-facing 页面：
  - `reports/site/reading/repo_scout/rank98_fib_placebo_honesty_source_intake.html`
- 参考 digest（已存在）：
  - `research/quant_digests/2026-03-19_1803_fib-placebo-zone-honesty-gate.md`
  - `reports/site/reading/quant_digests/2026-03-19_1803_fib-placebo-zone-honesty-gate.html`

## 两条轻量诚实守门（已过）
### 1) trade on / trade off
- trade on：只把这条线当 **Fib 主线的 honesty gate**，比较 `fib_exact`、`fib_zone`、`placebo_zone`，验证 Fib ratio 是否真的有增量信息。
- trade off：若改善主要来自 zone 放宽、随机比率也同步改善，或依赖事后挑 ratio，就不得继续把 Fib 写成 ratio-edge。

### 2) lookahead / repaint / leakage
- ratio/zone/swing/context 全部只用 `signal 当根及之前` 数据；
- 执行口径固定 `next-bar open + no-overlap`；
- placebo ratio 需固定随机种子并预先排除 Fib 邻域，禁止后验挑选。

## 当前硬结论
**`Rank 98 = guard-passed / admit_to_clean_replication_queue`**。

## 对 Next 3 的直接影响
- `Run 1 = EMA due-check only`
- `Run 2 = 若 EMA 仍 waiting_not_due，则给 Rank 98 1 次最小 clean replication`
- `Run 3 = 若 Rank 98 clean replication 直接 hard-fail / park，则切 CLV reserve source intake；仅当 CLV 也 exhausted，才回退旧 evidence_pool`

## 边界与验证
- 仅做最小必要 intake + 守门，不重跑重型下载。
- 不触发 P3 continuity（继续遵守 budget 与优先级）。
- 工作区有大量本轮无关脏文件，未做 commit。
