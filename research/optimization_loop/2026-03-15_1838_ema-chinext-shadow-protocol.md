# 2026-03-15 18:38 UTC｜EMA：创业板ETF 1d PSAR overlay 影子保护协议

## 为什么这次选这个
- 先做了环境观测：`git status --short`、最近 optimization loop 记录、`docs/TODO.md`、`docs/AUTO_OPTIMIZATION_LOOP.md`。
- 当前 steering 下，`EMA baseline family` 仍是最接近 `paper trading / 伪实盘` 的对象；但真实 `market-close refresh / week-1 review` 还在等下一根 completed bar，继续补近义 board / sync 已经边际很低。
- breakout 线这边，`scope verdict / one_more_gate` 已基本收口；在没有新的 `pure-test / down-tail` forward 命中前，继续同一样本 micro-slicing 不再是高杠杆动作。
- 所以本轮选一个更 deployment-facing、且不伪造 forward 的小收口：**把唯一还能继续观察的 `PSAR overlay` pocket（`创业板ETF 1d`）压成 narrow `shadow protective protocol`，明确它下一次真实收盘时到底该怎么作为 sidecar 运行，而不是继续停留在“候选 protective overlay”这句口头话上。**

## 本轮主点 / 子点
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`创业板ETF 1d` 的 `PSAR overlay` 候选，只做 primary lane sidecar，不改默认 EMA 持有规则

## 做了什么改动

### 1) 新增 `创业板ETF 1d` 专属 shadow protective protocol
- 修改：`scripts/build_ema_psar_raw_alpha_report.py`
- 新增 artifact：`reports/artifacts/ema_psar_raw_alpha/ema_chinext_daily_psar_shadow_protocol.csv`
- 新增报告段落：`reports/site/factors/ema_psar_raw_alpha/report.html` 的 `Q35g`

这张 protocol 表把四件事写死：
1. **scope freeze**：只限 `创业板ETF 1d`；不得外推到 `沪深300ETF 1d`、整个 `A股 daily family`、更不能去 reopen `Crypto 60m`。
2. **market-close sidecar refresh**：只允许跟主账本共用同一次 A 股收盘 refresh；没有新的 completed bar 时保持 `waiting next close`，不补伪 forward。
3. **weekly relative review**：只看 sidecar 相对 `EMA-only` 的 `cumulative relative delta / added trade churn / drawdown delta / execution mismatch`；没出现连续两次 relative red 之前，只保留 shadow protective watch。
4. **promotion / rollback gate**：只有 live shadow 也复现 `>=60%` 改善占比、`median relative delta > 0`，并同时通过项目级 `paper_live_promotion_gate_v1`（默认 `30d + >=20` closed cycles、`max(1.25x, +3pp)` drawdown guardrail、无 execution mismatch），才配讨论有限 default-overlay trial；否则继续 shadow-only。

### 2) 把这个 protocol 接回 runbook，而不是另起一页近义 board
- 修改：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_runbook.csv`
- 修改：`reports/site/factors/ema_psar_raw_alpha/report.html`

`创业板ETF 1d` 的 runbook 现在明确写成：
- `PSAR` 若继续观察，也只允许按 `ema_chinext_daily_psar_shadow_protocol.csv` 做 sidecar shadow review；
- 默认 `EMA-only` primary ledger 不改；
- 不允许因为这格 pocket 的局部改善，就提前改写默认持有规则。

### 3) closure board 同步项目级口径
- 修改：`scripts/build_alpha_closure_board_report.py`
- 修改：`reports/site/factors/alpha_closure_board/report.html`

首页入口现在收紧成：
- `EMA` 仍是 closest-to-paper 的默认 baseline / paper candidate；
- `PSAR overlay` 已被进一步收口成 **`创业板ETF 1d` narrow shadow-protective protocol**；
- 它不是 family-wide default overlay，也不是 `沪深300ETF 1d` promotion patch。

### 4) TODO 回写
- 修改：`docs/TODO.md`
- 新增并勾选：
  - `[x] EMA：把 创业板ETF 1d 的 PSAR overlay 候选压成 narrow shadow protective protocol（只做 sidecar，不改默认持有）`

固定下来的当前口径：
- `创业板ETF 1d` 虽有约 `75%` strict holdout 改善、median net20 delta 约 `+2.00pp`；
- 但 `A股 daily overall` 仍只有约 `50%` 改善、median delta 约 `-0.38pp`；
- 因此更诚实的写法仍是：**`EMA-only primary + PSAR sidecar shadow`**。

## 验证 / 证据
最小必要验证：
1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_alpha_closure_board_report.py`
4. `python3 scripts/build_plans_site.py`

结果：全部通过；仅有既有 matplotlib 中文字体 warning，不影响 CSV / HTML 输出。

关键产物检查：
- `ema_chinext_daily_psar_shadow_protocol.csv` 已生成，包含 `scope freeze / market-close sidecar refresh / weekly shadow review / promotion-or-default-overlay gate` 四步。
- `ema_paper_trading_runbook.csv` 的 `创业板ETF 1d` 行已显式引用该 protocol。
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已新增 `Q35g`。
- `reports/site/factors/alpha_closure_board/report.html` 已同步更新为 `创业板ETF 1d` 的 narrow shadow protocol 读法。

## 为什么这轮算有效推进
- 这轮没有伪造新的 forward / week-1 结果，也没有继续堆近义 `monitoring / operating / closure-copy` 页面。
- 它把一个容易被口头化的结论——`candidate_protective_overlay`——真正接成了 **下一次真实 market close 到来时可执行的 sidecar protocol**。
- 对 Jerry 的实际判断价值是：现在可以更清楚地区分
  - 什么叫“还可以继续观察”；
  - 什么叫“仍然不能接进默认 runbook”；
  - 以及下次真实收盘到来时，应该怎么记录这格 overlay，而不是继续讲抽象概念。

## 风险 / 边界
- 这不是新的 alpha 证据，也不是 `PSAR` 已经过 admission 的证明。
- 当前 `A股 daily overall` 仍是 mixed；所以 protocol 的意义是**限制它只能怎么被观察**，不是为它提前升格。
- 真正改变 `PSAR overlay` 地位的，仍然必须是后续 live shadow / paper 里的真实 relative review，而不是这次 protocol 文本本身。

## 执行层 hygiene
- `git status --short` 只作为环境观测，不作为失败条件。
- 当前 repo 仍有大量与本轮无关的历史脏改 / 未跟踪文件；本轮没有去混做 breakout / Fibonacci，也没有 reopen `pytrendline_event_validation_v3`。
- 本轮触达的主要文件：
  - `docs/TODO.md`
  - `scripts/build_ema_psar_raw_alpha_report.py`
  - `scripts/build_alpha_closure_board_report.py`
  - `reports/site/factors/ema_psar_raw_alpha/report.html`
  - `reports/site/factors/alpha_closure_board/report.html`
  - `reports/site/plans/{momentum_todo,index,report}.html`
  - `reports/artifacts/ema_psar_raw_alpha/ema_chinext_daily_psar_shadow_protocol.csv`

## Commit hash
- HEAD：`c271463`
- 本轮未提交。
- 原因：当前工作区存在大量与本轮无关的既有脏改 / 未跟踪文件；为避免混入无关改动，本轮只落地脚本、报告、artifact 与记录，不做 selective commit。
