# 2026-03-20 11:28 UTC · Rank 119 / confirmed swing + HTF alignment / source intake

## 本轮上下文
- 触发：bot3 13m desk auto loop
- Run 1 结果：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，仍如实返回 `Paper Seat / EMA = running paper / waiting_not_due`
- 最近 due：美股 1d+1wk 约 `8.5h`；Crypto 1d+1wk 约 `12.5h`；A 股更晚
- `manual_narrow_paper_last_run_summary.json`：本轮核对未见新的 `P3 status-changing event` 插队理由
- repo 状态：工作区仍有大量与本轮无关的既有脏文件，因此继续只做与本轮直接相关的最小写入，不混提

## 为什么这轮选 Rank 119
按顶板当前顺序，这轮 `Run 2` 必须回到 **fresh intake**，而不是继续磨已经 `budget used` 的旧 `P1`。本轮重新比较当前仍允许认领的 fresh source 后，边际价值排序大致是：
1. `confirmed swing + HTF alignment`：直接减少一个常见误读——结构一致性不该被默认写成 breakout-short 的 shared short gate；而且它已经有 repo 实现 + 公开数据代理快检，离 clean replication 只差一次角色冻结。
2. `PSAR trailing role fail-safe`：更像 exit 角色澄清，当前边际价值低于先把 entry/context 角色边界讲清。
3. 旧 `P1 evidence_pool`：都已用过默认预算，不应继续抢主资源。

因此本轮把 `2026-03-20 11:12 UTC` 的 repo digest 正式冻结为 **`Rank 119 / confirmed swing + HTF alignment long-side context`**。

## intake + 两条轻量诚实守门
### trade on
- 只允许把 `15m confirmed swing + backward-merged 1h structure` 用成 **`Fib retest_hold / EMA continuation` 的 long-side admission / sizing context**。
- 不能单独开仓，不能脱离 base setup 变成新 alpha。
- 对 breakout-short，默认只配当 `short-veto / size-down` 的后备假设，当前不允许写成 shared short-admission。

### trade off
- 如果后续 clean replication 显示改善主要来自大幅砍单，而不是更诚实地减少 `false-follow / false-hold`，就应直接 `park`。
- 若必须依赖多空对称叙事才能成立，也应直接 `park`。

### lookahead / leakage
- `confirmed swing` 必须是确认后才可用，不能把还未确认的局部高低点倒灌到当前判定。
- 1h 结构只能用已收盘 bar，通过 `merge_asof(backward)` 或等价口径并回 15m。
- 下一轮 clean replication 强制统一到 **`signal 当根及之前数据 + next-bar open + no-overlap`**；阈值与 lookback 只能在训练段冻结，再去测试段验证。

## 当前硬结论
**`Rank 119 = guard-passed / admit_to_clean_replication_queue_as_long_context_only`**。

翻成人话：
这条线值得拿 **1 次最小 clean replication** 预算，但只因为它有希望成为 `Fib / EMA` 的 long-side context；它**不**配被写成 breakout-short 的 shared short gate，也**不**配直接抢 `Live Seat`。

## 关键证据
- digest 里的代理快检已给出足够清楚的角色边界：
  - `long raw` 4-bar signed return 约 `-4.32 bps`，`long dual aligned` 约 `+4.82 bps`；re-entry 率从 `57.74%` 降到 `51.55%`
  - `short raw` 约 `-1.69 bps`，`short dual aligned` 恶化到约 `-16.41 bps`
- 因此当前最诚实的动作不是把它直接 park，而是承认：**它可能对 long-side context 有一点料，但对 short-side shared gate 明显不成立。**

## 本轮交付
### reader-facing
- `reports/site/reading/repo_scout/rank119_confirmed_swing_htf_long_context_source_intake.html`

### artifact
- `reports/artifacts/literature/scout_rank119_confirmed_swing_htf_long_context_source_intake_card.csv`

### board update
- 已把 `TODO.md` 顶部 desk board 更新为：`Rank 119` 进入 `Scout Seat` 主位，角色冻结为 `long-side context only`
- 也顺手澄清：早前日志里出现过的“`Rank 119 / PSAR trailing role`”只是更早时点的预备占位，并未正式进入 queue-facing；在 `Rank 115~118` 已顺延生成后，当前合法的下一个顺序号 `119` 正式给到这条新鲜 source

## 下一轮建议
- `Run 1 = EMA due-check first`
- 若仍 `waiting_not_due`：
  - `Run 2 = 只给 Rank 119 / confirmed swing + HTF alignment 1 次最小 clean replication`
  - 固定 `1` 条 archetype，默认优先 `fib_retest_long`
  - 统一比较 `baseline` vs `long_context_only`
- 若 `Rank 119` clean replication 显示改善主要来自砍样本，而没有更诚实地改善成本后表现或坏单率，则直接 `park`
- 若至少在 `2` 个 symbol 上仍有 honest uplift，再补 `1` 个真正会改变 verdict 的最小检查（默认优先 `成本 / 交易数稳定性`）

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 119` 直接相关的最小文件，不适合混提。
