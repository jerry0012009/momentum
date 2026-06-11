# 2026-03-19 06:10 UTC — Rank 81 RS+/RS- asymmetry gate source intake

## 本轮先核对的 desk 状态
- repo 工作区存在大量与本轮无关的脏文件；本轮未做 commit，也未混提无关改动。
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 全 desk 仍无 `due-now / overdue`
  - 最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- 顶板最新 `06:04 UTC` desk review 已明确：`Rank 80` 只剩 `keep_P1 / evidence_pool`，当前默认主资源应切到新的 fresh source，而不是继续磨旧候选。

## 本轮只认领的主点
- **主点：`Scout Seat / Rank 81 / RS+/RS- realized-semivariance asymmetry gate` 的 source intake + 两条轻量诚实守门**
- 未额外打开 ETF / Fib 等其他 fresh source；只在 active Scout 中做边际价值比较后认领 1 条主线。

## 为什么本轮选 Rank 81
本轮按当前 active Scout 候选重新比较边际价值：
1. **Rank 81 / RS+/RS- asymmetry gate**
   - 比 ETF 外部链路更便宜
   - 比 Fib 单 lane admission layer 更共享
   - 在 `Rank 80` 已完成那 1 次便宜诚实检查却只到 `keep_P1` 后，它最适合接替成为新的 queue-facing 主资源位
2. **ETF lead regime gate**
   - 仍有共享价值，但接外部 ETF 5m 链路更重
3. **Fib trend-strength admission layer**
   - 更偏单 lane admission / sizing，不如先做 shared directional veto

因此本轮更诚实的动作不是继续围着 `Rank 80` 打磨，也不是回头挤占 `P3 continuity`，而是把 `RS+/RS-` 正式冻结成新的 fresh Scout 候选。

## 本轮冻结的 source-intake 口径
- 候选：`Rank 81 / RS+/RS- realized-semivariance asymmetry gate`
- 来源：`Liu et al. (2023 JEF)` + `Patton & Sheppard (2015)`
- 核心迁移：
  - 不把“总波动高/低”当成单轴门
  - 而是把 `RS+` 与 `RS-` 分开，做成 **shared directional veto + sizing overlay**
  - long setup 遇到 `RS-` 尾部占优时，更该 `half-size / veto`
  - short setup 遇到 `RS+` 尾部占优时，同理处理

### 两条轻量诚实守门
1. **trade on / trade off 已可清楚写成规则**
   - `trade on`：方向至少不明显错配时，保留 breakout-short / Fib retest_hold / EMA-PSAR 原始入场资格
   - `trade off`：当 long 遇到明显 `RS-` 尾部、或 short 遇到明显 `RS+` 尾部时，只做 `half-size / veto`
2. **无明显 lookahead / repaint / data leakage**
   - 首轮只允许使用 signal 当根及之前可得的 trailing `5m` 收益构造 rolling `RS+ / RS-`
   - desk 统一执行口径仍是：`signal 当根及之前数据 + next-bar open + no-overlap`
   - 不允许用后续 session 收益、future realized-vol 或 future lane PnL 回填标签

## 本轮 hard verdict
- **`Rank 81 / RS+/RS- realized-semivariance asymmetry gate = guard-passed / admit_to_clean_replication_queue`**
- 当前 seat 分级更新建议：
  - `Rank 81 = P1 weak candidate（guard-passed / minimal clean replication next）`
  - `Rank 80 = P1（cheap honest check 已用 / keep_P1 / evidence_pool）`
  - `ETF lead regime gate`、`Fib trend-strength admission layer` = `P0 intake pool`
  - `Rank 78 = P3 narrow paper pilot（EMA-only suppression overlay）`
  - `Rank 17 / 2 / 29 / 32b = P3 narrow paper continuity`
  - `Rank 79 / 77 / 76 / 75 / 74 / 73 / 72 = P0 park / evidence pool`

## 本轮产物
- artifact:
  - `reports/artifacts/literature/scout_rank81_rs_semivariance_asymmetry_source_intake_card.csv`
- reader-facing page:
  - `reports/site/reading/repo_scout/rank81_rs_semivariance_asymmetry_source_intake.html`

## 对顶板的建议更新（Next 3）
- `Run 1 = EMA due-check only（若仍 waiting_not_due，不得空转）`
- `Run 2 = Rank 81 / RS+/RS- asymmetry gate minimal clean replication（仅当 EMA 仍 waiting_not_due）`
- `Run 3 = ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source；只有 Rank 81 这次 clean replication 已完成且 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 读回 `2026-03-19_0343_realized-semivariance-asymmetry-gate.md`，确认 source 口径与 trade-on/trade-off 一致
- 新建 artifact 与 reader-facing HTML 文件成功落盘
- `docs/TODO.md` 已更新 seat 分级与 `Next 3`

## 备注
- 本轮没有重拉外部数据，没有跑重型 clean replication，只做 source intake + honesty gate 冻结。
- 工作区存在大量历史脏文件与未跟踪产物；本轮未尝试整理、提交或覆盖这些无关改动。
