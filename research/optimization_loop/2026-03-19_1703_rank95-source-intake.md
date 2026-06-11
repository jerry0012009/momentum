# 2026-03-19 17:03 UTC — Rank 95 source intake：把 Vajra 的 controlled-pullback 冻结成 pre-armed depth budget

## 为什么这轮是它
- 先实际执行了 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 脚本继续返回 **`waiting_not_due`**：当前没有 `due-now / overdue` 的 EMA lane；最近 due 约为 `美股 2.9h`、`Crypto 6.9h`、`A股 13.9h`。
- `manual_narrow_paper_last_run_summary.json` 仍没有新的 `P3 status-changing event` 可挤掉 Scout。
- 按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 当前 `Next 3 bot3 runs`，本轮合法主动作就是 **`Rank 95 / Vajra controlled-pullback depth-budget` 的 source intake + 两条轻量诚实守门**。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 95` 的 `source intake + 两条轻量诚实守门`
- **紧邻子点**：把 verdict、active Scout 顺序、下一轮 `Next 3` 最小写回到 `TRADING DESK BOARD`

## 本轮先比较 active Scout 候选边际价值（3.5）
当前允许动作按顶板应读成：
1. `Rank 95 / Vajra controlled-pullback depth-budget`
2. `fresh 5m / 15m paper-repo intake pool`
3. `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `Rank 92 / Rank 94 park / evidence_pool`
5. `P3 continuity`
6. `tiny-live plumbing`

把 `Rank 95` 排第一，不是为了追新，而是因为：
- 它直接服务当前主线 `EMA / PSAR raw alpha focus`；
- 当前最值钱的问题不是再加一个 trigger 后过滤，而是先回答 **回踩深度预算该不该前置成 pre-armed state budget**；
- 这比继续给旧 evidence_pool 续命，更可能改变 desk judgment。

## 本轮 intake 结论
### 1) trade on / trade off 冻结
- **trade on**：只把它降级成 `shared depth-budget / pre-armed state budget`，不是新的独立 alpha。
  - 先定义 `armed_pullback`：过去 `N` 根内出现 toward-EMA 的回踩，且 `max pullback depth<=x%`、`nearEMA` 成立；
  - 只有 armed 状态下，后续 `EMA/PSAR continuation trigger` 才允许放行；
  - 首轮 `x` 只允许测 `0.75% / 1.0% / 1.25%`；`volume/ADX` 只允许当邻近过滤臂，不当主结论。
- **trade off**：若只是 trigger 发生后再回头检查 `pullback<=1.5%`，或把 trigger 之后更深的 retrace 倒灌回 trigger 判定，就不得再把它说成有效 depth budget。
  - repo 默认 `1.5%` 在当前 15m 代理口径里几乎不筛样本，因此不能再把它当 `post-trigger gate` 继续宣传；
  - 它也不能单独替代原始方向 trigger。

### 2) 轻量诚实守门
- **规则能清楚写成 trade on / trade off**：通过。
- **没有明显 lookahead / repaint / data leakage**：通过，但前提是 desk 迁移统一冻结到：
  - `signal 当根及之前数据 + next-bar open + no-overlap`
  - `armed_pullback`、depth 预算、`nearEMA`、`volume/ADX` 都只用 trigger 当根及之前的已完成 bar 计算；
  - 不得把 trigger 之后的回踩深度、后验 path、或 repo 的 `BTC 1H` 特有叙事偷渡进第一轮。

## hard verdict
**`Rank 95 = guard-passed / admit_to_clean_replication_queue`**

更直白地说：
- 这条线当前最诚实的读法不是 “`pullback<=1.5%` 是个现成可用的 post-trigger gate”；
- 而是 **它提示了一个值得测的 shared 问题：回踩深度预算应不应该前置成 pre-armed state budget**；
- 所以这轮应进入 `clean replication queue`，但仍不能直接吹成 alpha。

## 本轮产物
### reader-facing 落点
- `reports/site/reading/repo_scout/rank95_vajra_controlled_pullback_source_intake.html`

### artifacts
- `reports/artifacts/literature/scout_rank95_vajra_controlled_pullback_source_intake_card.csv`

## desk board 写回
已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最小刷新为：
- `Rank 95 = guard-passed / admit_to_clean_replication_queue`
- active Scout 顺序：`Rank 95 > fresh 5m / 15m paper-repo intake pool > Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 92 / Rank 94 park / evidence_pool > P3 continuity > tiny-live plumbing`
- `Next 3 bot3 runs`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则给 Rank 95 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 95 clean replication 仍存活，则只给 1 个 truly verdict-changing 的 Light Stability Pack（默认先做时间稳定性）；若 Rank 95 直接 hard-fail / park，则按 7.10 先从 quant_digests / RECENT_PAPER_SEEDS / validated shortlist 再认领 1 条新的 5m / 15m source intake`

## 验证 / 命令
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 已确认以下文件存在并可读：
  - `reports/artifacts/literature/scout_rank95_vajra_controlled_pullback_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank95_vajra_controlled_pullback_source_intake.html`
  - `docs/TODO.md`

## 风险 / 边界
- 当前证据只够支持“`1.5%` 不适合继续当 post-trigger gate”，不够直接证明 pre-armed 版本就有 alpha；
- 原 repo 是 `BTC 1H`，不是现成的 15m crypto 通用模板；
- 下一轮 clean replication 必须坚持复用本地 cache，不应扩成重型下载或泛研究。

## git / 脏区说明
- 当前 git 工作区仍有大量与本轮无关的脏文件；
- 本轮只新增/改动与 `Rank 95 source intake` 直接相关的文件；
- 因脏区过大，本轮不提交，避免混提。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`，默认只给 `Rank 95` 1 次最小 clean replication：
  - 固定 `BTC/ETH/SOL | 120d | 15m` 本地 cache；
  - 比较 `baseline / post_trigger_depth_gate / pre_armed_depth_budget`；
  - 必要时最多加 `pre_armed_depth_budget + volume/ADX` 作为紧邻子臂；
  - 直接回答 `keep_P1 / promote_to_P2 / park`。
- 若这轮 clean replication 直接 hard-fail，则不要回头给旧 evidence_pool 续命；先按 7.10 再认领 1 条新的 `5m / 15m` paper-repo source。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件，混提不安全。
