# 2026-03-20 12:01 UTC · Rank 120 / strict BMS impulse quality gate / source intake

## 本轮上下文
- 触发：bot3 13m desk auto loop
- 顶板 authority：`docs/TODO.md` 顶部 `2026-03-20 11:51 UTC` desk review
- Run 1 结果：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，仍如实返回 `Paper Seat / EMA = running paper / waiting_not_due`
- 最近 due：美股 `1d+1wk -> 约 8.0h`；Crypto `1d+1wk -> 约 12.0h`；创业板ETF `1d -> 约 67.0h`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件，不混提
- hosted P3 状态补充：`manual_narrow_paper_last_run_summary.json @ 2026-03-20T11:59:07Z` 显示 `new_closed_trades_appended=1`，但当前顶板没有把它升级为新的 seat；本轮仍严格只从 `Next 3` 认领动作，不插队改做 continuity

## 为什么这轮选 Rank 120
按 `11:51 UTC` 顶板，这轮 `Run 2` 已被明确收紧为：
1. `Run 1 = EMA due-check first`
2. 若仍 `waiting_not_due`，则只给 **`Rank 120 / strict BMS impulse quality gate`** 做 `source intake + 两条轻量诚实守门`
3. 只有当 `Rank 120` guard-pass，下一轮才配拿 1 次最小 clean replication；若当场 `hard-fail / 过稀疏 / 守门不过`，则切 `Rank 121 / PSAR trailing role fail-safe`

因此本轮不并开别的 fresh source，也不回头磨 `Rank 112 / 111`。

## source intake + 两条轻量诚实守门
### 这条线到底在说什么
这轮 intake 直接继承 `research/quant_digests/2026-03-20_1132_strict-bms-impulse-not-shared-gate.md` 的 repo 工程定义：
- 最近 `3` 根 K 与 breakout 同向
- 每根 `|close-open| / (high-low) >= 0.60`
- `break_distance / ATR14 > 0.5`

翻成人话：它不是“又一个通用趋势门”，而是试图只留下 **最硬、最直、最有冲击质量** 的 breakout 样本。

### trade on
- 只配当 **high-conviction subset / long-side bucket / conditional veto 对照组**。
- 适合后续放进既有 breakout / Fib / EMA follow-up 研究里，做“极少数高质量冲击样本”的旁路标签。

### trade off
- 不得直接写成 breakout-short / Fib / EMA-PSAR 的 **shared admission gate**。
- 如果必须靠“shared 多空对称门”叙事才能成立，就应直接 `park`。
- 如果表面改善主要来自交易数塌缩，而不是更诚实地降低坏单率，也应直接 `park`。

### honesty gate 1：规则是否写得清楚
能写清楚，但写清楚以后，反而更容易看出它**不适合 shared 化**：
- 这更像“只有特别强的冲击 candle 才打标签”
- 不是“默认所有 follow-up setup 都要先过这道门”

### honesty gate 2：有没有明显 leakage / data leakage
- 规则本身只看过去 `3` 根 K、body ratio 与 ATR14，本身没有强制 lookahead
- 但 source intake 阶段已经有足够硬证据说明：即使因果写得干净，**它的稀疏度和 side instability 也已经足以否决 shared-gate 占位**
- 因而这轮不需要继续申请 clean replication，直接在守门阶段做 hard verdict 更诚实

## 关键证据
来自 digest 附带的 `BTC/ETH/SOL | 120d | 15m` 代理快检：
- long 侧：`raw=2385`，strict impulse 仅 `10`（`0.42%`）
- short 侧：`raw=2560`，strict impulse `33`（`1.29%`）
- long 侧 4-bar signed return：`raw -2.37 bps -> strict +35.52 bps`，但样本极少
- short 侧 4-bar signed return：`raw +1.08 bps -> strict -16.54 bps`
- `reentry4_rate` 虽然明显下降（long `44.1% -> 10.0%`；short `39.3% -> 9.1%`），但这更像筛到极少数“冲得最直”的样本，而不是足以 desk-wide 共享的稳定 gate

这套证据已经足够回答当前最重要的问题：
**strict BMS impulse 可以保留为标签，但不该继续占用 active Scout 主资源去争 shared gate 身份。**

## 本轮硬结论
**`Rank 120 / strict BMS impulse quality gate = P0 / park / evidence pool`**。

翻成人话：
- 它不是无效；
- 但它当前最诚实的定位就是“极稀疏的高确信度标签”，不是 desk 当前要推进的 paper candidate；
- 因而这轮在 source intake 阶段就够资格直接收口，不再申请 clean replication 预算。

## 本轮交付
### reader-facing
- `reports/site/reading/repo_scout/rank120_strict_bms_impulse_quality_gate_source_intake.html`

### artifact
- `reports/artifacts/literature/scout_rank120_strict_bms_impulse_quality_gate_source_intake_card.csv`

### board update
- 已把 desk board 的 active Scout 主点收口为：`Rank 120 = park / evidence pool`
- 并把下一手 reserve 前推到 `Rank 121 / PSAR trailing role fail-safe`

## 下一轮建议
- `Run 1 = EMA due-check first`
- 若仍 `waiting_not_due`：
  - `Run 2 = 只给 Rank 121 / PSAR trailing role fail-safe 做 source intake + 两条轻量诚实守门`
  - `Run 3 = 若 Rank 121 guard-pass，则只给它 1 次最小 clean replication；若它也 hard-fail / exhausted，才允许继续回退到 tiny-live plumbing fallback`

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 120` 直接相关的最小文件，不适合混提。
