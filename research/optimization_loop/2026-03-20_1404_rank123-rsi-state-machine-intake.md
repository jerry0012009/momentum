# 2026-03-20 14:04 UTC · Rank 123 RSI state-machine admission source intake

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，因此本轮主动作落在 fresh Scout，并把 `13:53 UTC` 的 repo digest 正式冻结为 **`Rank 123 / RSI enter→exit→re-enter state-machine admission`**，完成 `source intake + 两条轻量诚实守门`，当前 hard verdict 为 **`guard-passed / admit_to_clean_replication_queue`**。

## 先检查了什么
- `git -C /root/clawd/jerry/momentum status --short --branch`
  - 结果：`master`，工作区非常脏；本轮只做 selective write-back，不混提无关文件。
- 最近 optimization logs
  - 最新到 `2026-03-20 13:40 UTC / Rank 122 时间稳定性检查 -> 升到 P3 narrow paper pilot`
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
  - 最近 due 约为：`美股 1d+1wk -> 5.9h`、`Crypto 1d+1wk -> 9.9h`、`创业板ETF 1d -> 64.9h`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 当前 authoritative `Next 3`（本轮开工前）：
    1. `Run 1 = EMA due-check first`
    2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 123 做 source intake + 两条轻量诚实守门`
    3. `Run 3 = 若 Rank 123 guard-pass，则只给它 1 次最小 clean replication`

## 为什么本轮认领 Rank 123
- `EMA` 继续 `waiting_not_due`，Paper Seat 没有 due-now / overdue 动作。
- `Rank 122` 已在上一轮升到 `P3 / narrow paper pilot approved`，当前只配 hosted continuity，不该继续燃烧 bot3 的 `P3 continuity` 预算。
- `Rank 112 / 111` 都已经是 `P1 evidence_pool / budget used`，当前边际价值低于 fresh source。
- `2026-03-20 13:53 UTC` 的 quant digest 提供了新的 **paper / repo based 15m crypto** source，符合 desk 对 `Scout Seat` 的当前默认偏好。

## 本轮主点
### Rank 123 source intake + 两条轻量诚实守门
把 `MoDiggler75/crypto-trading-bot` 里的 RSI retest 状态机，收窄成 desk 可执行的 queue-facing 描述：
- **trade on**：只先当 `Fib retest_hold + EMA/PSAR long-side` 的 sparse admission overlay。先有 base long trigger，再看 signal 前最近 8 根 RSI14 是否先进入低位区、随后在 signal bar 回到中性/偏强区，作为 `enter -> exit -> re-enter` 的轻量代理。
- **trade off**：不是独立 alpha，不是通用 breakout filter，当前默认 **不 shared 到 breakout-short**，也不能在没有 base long trigger 时单独开仓。
- **honesty gate**：RSI 状态与 retest 只能来自 `signal 当根及之前数据`；下一轮 clean replication 必须统一到 `next-bar open + no-overlap`；relaxed 阈值只能在训练段冻结，再去测试段验证。

## 关键代理证据（来自 13:53 UTC digest）
- `Fib + EMA long` baseline：`n=137`、`win8=59.1%`、`mean8=+10.3bps`
- `Fib + EMA long` + relaxed RSI state machine：`n=13`、`win8=69.2%`、`mean8=+72.9bps`
- `breakout-short` baseline：`n=61`、`mean8=+37.6bps`
- `breakout-short` + gated：`n=9`、`mean8=-51.8bps`
- strict repo 风格双触发版本：当前 15m 样本下近似 `n=0`

## authoritative verdict
**`Rank 123 / RSI state-machine admission = guard-passed / admit_to_clean_replication_queue`**

翻成人话：
- 值得给 **1 次最小 clean replication** 预算；
- 但当前只配先验证它能否作为 `Fib retest_hold + EMA/PSAR long-side` 的 sparse admission；
- 目前不支持把它写成 `breakout-short` 的 shared gate；
- 也完全不配抢 `Live Seat`。

## 紧邻子点
已补最小 queue-facing / reader-facing 落点：
- `reports/artifacts/literature/scout_rank123_rsi_state_machine_admission_source_intake_card.csv`
- `reports/site/reading/repo_scout/rank123_rsi_state_machine_admission_source_intake.html`
- `docs/TODO.md` 顶部 desk board 新增 `14:04 UTC` authoritative write-back

## 对 desk board 的写回
当前更诚实的 active Scout 顺序更新为：
- `Rank 123 / RSI state-machine admission`（`P1 / guard-passed / clean replication next`）
- `Rank 112 / basis dislocation short veto`（`P1 weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock`（`P1 evidence_pool / budget used`）
- `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`（`P3 hosted continuity / sidecar only`）
- `Rank 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`（`P0 / park / evidence pool`）

更新后的 `Next 3`：
1. `Run 1 = EMA due-check first`
2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 123 1 次最小 clean replication`
3. `Run 3 = 若 Rank 123 clean replication hard-fail / exhausted，则回 fresh intake；若它保留 honest uplift 且无 decisive fail，则直接给出 keep_P1 / promote_P2 / park`

## 产物
- `reports/artifacts/literature/scout_rank123_rsi_state_machine_admission_source_intake_card.csv`
- `reports/site/reading/repo_scout/rank123_rsi_state_machine_admission_source_intake.html`
- `docs/TODO.md`
- `research/optimization_loop/2026-03-20_1404_rank123-rsi-state-machine-intake.md`

## 验证
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 已核对写出文件存在：
  - `reports/artifacts/literature/scout_rank123_rsi_state_machine_admission_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank123_rsi_state_machine_admission_source_intake.html`
  - `docs/TODO.md`

## 风险 / 保留意见
- 当前证据仍以 repo 逻辑 + 最小代理快检为主，不是完整策略回测。
- long 侧 gated 样本很小，下一轮 clean replication 必须优先验证成本后 uplift 是否只是缩样本幻觉。
- strict 版本在当前 15m 样本近乎零触发，不适合直接拿来做 desk 默认版本。

## 提交情况
- 未提交
- 原因：repo 有大量与本轮无关的脏文件；本轮只做 selective write-back
