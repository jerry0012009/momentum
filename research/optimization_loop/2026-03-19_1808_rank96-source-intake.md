# 2026-03-19 18:08 UTC — Rank 96 source intake：把 AdvancedMA 的 retestCount 冻结成 second-touch admission layer

## 为什么这轮是它
- 先实际执行了 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 脚本继续返回 **`waiting_not_due`**：当前没有 `due-now / overdue` 的 EMA lane；最近 due 约为 `美股 1.8h`、`Crypto 5.8h`、`A股 12.8h`。
- `manual_narrow_paper_last_run_summary.json` 最新仍是 `new_closed_trades_appended=0`，没有新的 `P3 status-changing event` 可挤掉 Scout。
- 按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 当前 `Next 3 bot3 runs`，本轮合法主动作就是 **`Rank 96 / AdvancedMA retest-count admission layer` 的 source intake + 两条轻量诚实守门**。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 96` 的 `source intake + 两条轻量诚实守门`
- **紧邻子点**：把 verdict、active Scout 顺序、下一轮 `Next 3` 最小写回到 `TRADING DESK BOARD`

## 本轮先比较 active Scout 候选边际价值（3.5）
当前允许动作按顶板应读成：
1. `Rank 96 / AdvancedMA retest-count admission layer`
2. `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
3. `Rank 95 / Rank 92 / Rank 94 park / evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

把 `Rank 96` 排第一，不是为了重新强调 breakout，而是因为：
- 它来自 **fresh repo source**，而不是预算已用的旧 `P1 evidence_pool`；
- 它补的是当前 desk 还缺的一条明确执行语义：**第一次回踩只是 probe，第二次回踩才更像 admission**；
- 相比继续磨旧候选，它更可能改变当前 `breakout-short follow-up / Fib retest / EMA-PSAR` 三条主线的 gate 读法。

## 本轮 intake 结论
### 1) trade on / trade off 冻结
- **trade on**：只把它降级成 `shared admission / veto layer`，不是新的独立 alpha。
  - 先定义 level zone 与 `retest_count`；
  - 只有最近 `1~4` 根内已经出现过第一次有效 retest，且当前这次是 `second-touch`（或 `retestCount>=2`）重新收回 / 压回 level 时，才允许它放行对应 base setup；
  - 首轮只允许比较 `baseline / first_touch_only / second_touch_only / second_touch_plus_candle_quality` 四臂。
- **trade off**：若只是单次 touch、单次 wick、或 level zone / retest count 需要事后回看未来路径才能成立，就不得硬说它形成了 confirmation。
  - 它不能偷渡成新的独立 breakout alpha，也不能把任何回踩都包装成 `re-entry setup`；
  - 对 long 侧，如果 `second-touch` 只是少亏但没翻正，就只能保留成 setup-specific admission 线索，不得吹成 shared gate。

### 2) 轻量诚实守门
- **规则能清楚写成 trade on / trade off**：通过。
- **没有明显 lookahead / repaint / data leakage**：通过，但前提是 desk 迁移统一冻结到：
  - `signal 当根及之前数据 + next-bar open + no-overlap`
  - `zone_high/zone_low`、`touch_count`、`reclaim/back-below level` 与 retest sequence extreme 都只用 signal 当根及之前可得的 `15m/5m` 数据构造；
  - 不得把后续 overshoot、future path 或事后主观重画区间倒灌回第一轮。

## hard verdict
**`Rank 96 = guard-passed / admit_to_clean_replication_queue`**

更直白地说：
- 这条线当前最诚实的读法不是“新的 breakout alpha”；
- 而是 **值得做最小 clean replication 的 retest-count admission / veto overlay**；
- 对 short follow-up 最直接；对 Fib / EMA long 侧当前只够当减亏对照，不够提前写成 shared hard gate。

## 本轮产物
### reader-facing 落点
- `reports/site/reading/repo_scout/rank96_advancedma_retest_count_source_intake.html`

### artifacts
- `reports/artifacts/literature/scout_rank96_advancedma_retest_count_source_intake_card.csv`

## desk board 写回
已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最小刷新为：
- `Rank 96 = guard-passed / admit_to_clean_replication_queue`
- active Scout 顺序：`Rank 96 > Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 95 / Rank 92 / Rank 94 park / evidence_pool > P3 continuity > tiny-live plumbing`
- `Next 3 bot3 runs`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则给 Rank 96 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 96 clean replication 仍存活，则只给 1 个 truly verdict-changing 的 Light Stability Pack（默认先做时间稳定性）；若 Rank 96 直接 hard-fail / park，则按 7.10 再认领 1 条新的 5m / 15m paper-repo source intake`

## 验证 / 命令
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 已确认以下文件存在并可读：
  - `reports/artifacts/literature/scout_rank96_advancedma_retest_count_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank96_advancedma_retest_count_source_intake.html`
  - `docs/TODO.md`

## 风险 / 边界
- 当前证据只够支持“`retestCount>=2` 值得做最小 clean replication”，不够直接证明它是三条线共享的稳定 gate；
- `second-touch` 天然会砍样本，下一轮必须优先看 retention、失败率与成本后收益是不是一起更诚实；
- 默认不允许把它提前写成 live challenger，也不应在 clean replication 前继续补 intake 近义文案。

## git / 脏区说明
- 当前 git 工作区仍有大量与本轮无关的脏文件；`git status --short | wc -l = 1517`。
- 本轮只新增/改动与 `Rank 96 source intake` 直接相关的文件；
- 因脏区过大，本轮不提交，避免混提。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`，默认只给 `Rank 96` 1 次最小 clean replication：
  - 固定 `BTC/ETH/SOL | 120d | 15m` 本地 cache；
  - 比较 `baseline / first_touch_only / second_touch_only / second_touch_plus_candle_quality`；
  - 直接回答 `keep_P1 / promote_to_P2 / park`。
- 若这轮 clean replication 直接 hard-fail，则不要回头给旧 evidence_pool 续命；先按 7.10 再认领 1 条新的 `5m / 15m` paper-repo source。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件，混提不安全。
