# 2026-03-19 22:12 UTC — Rank 101 3-step volume dry-down long-bias gate source intake

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - Crypto 1d+1wk：约 `1.8 小时` 后到点
  - 当前无 `due-now / overdue` lane
- 因此按当前 desk 纪律，`Paper Seat` 不能空转；本轮合法主动作切到 fresh Scout intake。

## 开轮检查
- repo 工作区仍有大量与本轮无关的既有脏文件：`git status --short | wc -l = 1574`。
- 当前分支：`master`。
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T22:04:13Z`
  - `new_closed_trades_appended = 0`
  - 结论：当前没有需要 bot3 插队主资源处理的 `P3 status-changing event`。
- 最近 optimization logs：
  - `2026-03-19_2200_rank100-fib-depth-clean-replication.md`
  - `2026-03-19_2140_rank100-fib-depth-intake.md`
  - `2026-03-19_2130_rank99-time-stability-park.md`

## Active Scout 候选边际比较（本轮先比较后认领）
1. **`Rank 101 / 3-step volume dry-down long-bias gate reserve`**
   - `Rank 100` 已在 clean replication 后如实压回 `park / evidence pool`。
   - 顶板当前 `Next 3` 已明确写成：若 `EMA` 仍 `waiting_not_due`，本轮就只给 `Rank 101` 做 source intake + 两条轻量诚实守门。
   - 它直接回答当前 desk 更缺的一层：`pullback participation decay`，也就是“回踩像吸收，还是只是没人接”。
2. **fresh source pool retry（7.10）**
   - 只有在 `Rank 101` intake 直接 hard-fail / exhausted 后，才轮到回 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 再认领一条新的 `5m / 15m crypto` source。
3. **`tiny-live plumbing`**
   - 当前没有新的 promoted live candidate，也没有理由让它插队到本轮主资源位。

结论：本轮主资源给 `Rank 101`；不并开 clean replication，也不回头续命旧 evidence_pool / P3 continuity。

## 本轮认领
- 主点：`Rank 101 / 3-step volume dry-down long-bias gate`
- 紧邻子点：把 verdict、reader-facing 页面、`TODO` 顶板更新一次写齐

## 本轮交付（deployable artifact）
- source intake card：
  - `reports/artifacts/literature/scout_rank101_volume_drydown_long_bias_source_intake_card.csv`
- reader-facing 页面：
  - `reports/site/reading/repo_scout/rank101_volume_drydown_long_bias_source_intake.html`
- 参考 digest（已存在）：
  - `research/quant_digests/2026-03-19_2009_abnormal-volume-drydown-long-bias-gate.md`
  - `reports/site/reading/quant_digests/2026-03-19_2009_abnormal-volume-drydown-long-bias-gate.html`

## 两条轻量诚实守门（已过）
### 1) trade on / trade off
- trade on：只把这条线当 **long-side pullback / retest / continuation 的 hold-quality gate**，不是 shared trigger。默认骨架是：higher-tf bias 仍向上，回踩阶段先出现 `3` 根递减成交量（单根衰减约 `5%~30%`）且整体低于 `20-bar` 均量预算，然后才看 EMA/Fib reclaim 是否成立。
- trade off：若 dry-down 只是把样本切得过窄、成本后仍只是“少亏一点”的排序，而不是足够诚实的 edge，就不得升格；同时也不允许把这套 long-side dry-down 逻辑直接镜像成 short admission。当前更诚实的 short 读法最多只是 `short veto / size-down`。

### 2) lookahead / repaint / leakage
- repo 里的 `abnormalVolLoss`、`decreasingVolume`、`consecutiveCandlesLimit=3`、`minVolChange`、`maxVolChange` 本身是当下可得的因果式 bar 规则；
- desk 迁移时必须统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap`；
- 不得把后续 `3~8 bars` 的 path、未来是否成功 hold、或事后挑出的漂亮 retrace 区间倒灌回 dry-down 标签。

## 当前硬结论
**`Rank 101 = guard-passed / admit_to_clean_replication_queue`**。

## 对 Next 3 的直接影响
- `Run 1 = EMA due-check only（优先盯 Crypto 1d+1wk due_soon）`
- `Run 2 = 若 EMA 仍 waiting_not_due，则给 Rank 101 1 次最小 clean replication`
- `Run 3 = 若 Rank 101 clean replication 直接 hard-fail / exhausted，则按 7.10 回 fresh source pool；只有 fresh source 也 exhausted，才允许回退到 tiny-live plumbing`

## 边界与验证
- 仅做最小必要 intake + 守门，不重跑重型下载。
- 不触发 P3 continuity（继续遵守 budget 与优先级）。
- 工作区有大量本轮无关脏文件，未做 commit。
