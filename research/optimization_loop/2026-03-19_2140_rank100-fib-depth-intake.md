# 2026-03-19 21:40 UTC — Rank 100 fib-depth shallow-mid admission gate source intake

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - Crypto 1d+1wk：约 `2.3 小时` 后到点
  - 当前无 `due-now / overdue` lane
- 因此按当前 desk 纪律，`Paper Seat` 不能空转；本轮合法主动作切到 fresh Scout intake。

## Active Scout 候选边际比较（本轮先比较后认领）
- `fib-depth shallow-mid admission gate reserve`
- `3-step volume dry-down long-bias gate reserve`
- `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
- `Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 park`
- `P3 continuity`
- `tiny-live plumbing`

结论：本轮主资源给 `fib-depth shallow-mid admission gate reserve`，不回头续命旧 evidence_pool，也不挤占 P3 continuity。

## 本轮认领
- 主点：`Rank 100 / fib-depth shallow-mid admission gate`
- 紧邻子点：无（未并行打开 `3-step volume dry-down`）

## 本轮交付（deployable artifact）
- source intake card：
  - `reports/artifacts/literature/scout_rank100_fib_depth_shallow_mid_source_intake_card.csv`
- reader-facing 页面：
  - `reports/site/reading/repo_scout/rank100_fib_depth_shallow_mid_source_intake.html`
- 参考 digest（已存在）：
  - `research/quant_digests/2026-03-19_2041_fib-depth-shallow-mid-admission-gate.md`
  - `reports/site/reading/quant_digests/2026-03-19_2041_fib-depth-shallow-mid-admission-gate.html`

## 两条轻量诚实守门（已过）
### 1) trade on / trade off
- trade on：只把这条线当 **Fib retest_hold / continuation 的 depth admission gate**，默认比较 `shallow_mid_38_62` 与 `deep_62_79`；必要时再拆成 `38-50 / 50-62 / 62-71 / 71-79`。当前主问题不是再造新 alpha，而是回答：15m pullback 默认该优先浅中回踩，还是继续迷信深回踩。
- trade off：若改善只是因为浅区间更容易成交，但成本后并没有真实增量；或 deep bucket 只在事后挑窗口 / 品种才显得更好，就不得把 Fib 深度写成独立 edge，应降级为 generic retrace ordering。

### 2) lookahead / repaint / leakage
- Fib 区间、swing anchor、breakout bar、触达顺序都只用 `signal 当根及之前` 数据；
- 执行口径固定 `next-bar open + no-overlap`；
- 不得把后续 `4~8 bars` 的 path、事后重选 anchor、或未来 breakout 失败信息倒灌回 depth gate。

## 当前硬结论
**`Rank 100 = guard-passed / admit_to_clean_replication_queue`**。

## 对 Next 3 的直接影响
- `Run 1 = EMA due-check only（优先盯 Crypto 1d+1wk due_soon）`
- `Run 2 = 若 EMA 仍 waiting_not_due，则给 Rank 100 1 次最小 clean replication`
- `Run 3 = 若 Rank 100 clean replication 直接 hard-fail / exhausted，则切 3-step volume dry-down long-bias gate reserve（拿 Rank 101）；只有 fresh source 这一层也 exhausted，才允许回退旧 evidence_pool / park / P3 continuity`

## 边界与验证
- 仅做最小必要 intake + 守门，不重跑重型下载。
- 不触发 P3 continuity（继续遵守 budget 与优先级）。
- 工作区有大量本轮无关脏文件，未做 commit。
