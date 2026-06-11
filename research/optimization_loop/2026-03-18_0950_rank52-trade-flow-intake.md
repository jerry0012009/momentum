# 2026-03-18 09:50 UTC — Rank 52 / trade-flow imbalance veto 通过 source intake 守门，进入最小 clean replication 队列

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查当前 `Next 3 bot3 runs`。
- 当前 `Paper Seat / EMA` 的 `due_guardrail_snapshot` 显示最近 due 依次是：`美股 1d+1wk -> 2026-03-18 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-19 00:00 UTC`、`A 股多条 lane -> 2026-03-19 07:00 UTC`，所以这轮 `Run 1` 最诚实的读法仍是 **due-check only / waiting_not_due**，不应重复 paper refresh。
- `Rank 50 / 51` 都已在允许预算内完成 fast-lane clean replication 并压回 `park / evidence pool`，因此 `Scout Seat` 本轮必须回到 **fresh paper / repo based 15m crypto intake**，不能回头挤占 `P3 continuity`。
- 这轮先比较了当前允许动作的边际价值：`Rank 52 / trade-flow imbalance veto`（最新 `09:41 UTC` quant digest，对 breakout / Fib / EMA-PSAR 三条主线都能复用的主动成交压力 veto） `>` `Rank 35b`（queue-only fallback） `>` `Run 3 / tiny-live plumbing`。
- 因此本轮只认领 **1 个主点**：完成 `Rank 52` 的 `source intake + 两条轻量诚实守门`；不提前打开 clean replication，也不掉去 `Run 3`。

## 做了什么改动
### 1) 给新方向分配顺序 Rank，并生成 source-intake artifact
- 新增脚本：`scripts/build_rank52_trade_flow_imbalance_source_intake.py`
- 产物：`reports/artifacts/literature/scout_rank52_trade_flow_imbalance_source_intake_card.csv`
- reader-facing 页面：`reports/site/reading/repo_scout/rank52_trade_flow_imbalance_source_intake.html`

### 2) 最小写回权威板
- 更新 `docs/TODO.md` 顶部 authoritative 区域：
  - 把这条新方向冻结成 **`Rank 52 / trade-flow imbalance veto`**；
  - 写回当前 hard verdict：`guard-passed / admit_to_clean_replication_queue`；
  - 把最新 `Next 3` 顺序收紧为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = Rank 52 / trade-flow imbalance veto minimal clean replication（仅当 EMA 仍 waiting_not_due）`
    - `Run 3 = Rank 35b / tiny-live plumbing（仅当 Rank 52 也不合格）`

## 验证 / 证据
### 1) Paper Seat 当前确实仍是 waiting_not_due
- 读取：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
- 当前最近 due：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A 股多条 lane -> 2026-03-19 07:00 UTC`
- 因此这轮不该伪造 `EMA refresh`，而应转去 `Scout Seat`。

### 2) Rank 52 的两条轻量诚实守门已通过
基于 `tsuithomas/crypto_research_order_book_imbalance` 的 README、`feature_engineering.py` 与 `backtester.py`：
- `trade on`：保留现有 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 作为 base setup；只有当 setup 已触发且最近 `3~5` 分钟主动成交量同向占优时，才允许放行。
- `trade off`：若 flow 与 setup 方向相反，或只剩接近零的中性压力，则直接 veto；它不能单独开仓，只能负责拒绝明显缺少真实跟随盘的 entry。
- `lookahead / repaint / leakage`：源码里真正可复刻的是 **aggTrades 的 trade-flow imbalance proxy**，不是完整 L2 `order-book imbalance`。当前实现是 trailing flow -> future return 的顺序，不是一眼可判死刑的未来函数；但若迁移到 desk，下一轮 clean replication 必须明确冻结成 **setup 前最后 3~5 分钟 flow summary + next-bar open + no-overlap**，避免把 setup 后成交量倒灌回入场判断。

### 3) 当前硬结论
- **`Rank 52 / trade-flow imbalance veto = guard-passed / admit_to_clean_replication_queue`**。
- 它不是已验证 alpha；只是说明它已经通过 intake-stage 的两条轻量守门，值得拿 **1 次最小 clean replication** 预算。

## reader-facing 落点
- `reports/site/reading/repo_scout/rank52_trade_flow_imbalance_source_intake.html`

## 风险 / 边界
- repo 名字叫 `order_book_imbalance`，但当前最诚实、可复刻的部分其实是 **trade-flow imbalance proxy**；如果不降级表达，很容易高估证据强度。
- README 的正收益依赖 `maker + threshold` 假设，说明它更像 **15m filter / veto**，不适合直接吹成主 alpha。
- `aggTrades` 历史抓取虽是公开 API，但属于 microstructure 数据链；下一轮应该只做最小 clean replication，不要一上来扩成大规模高频框架。
- 本轮未提交 git：当前工作区存在大量与本轮无关的脏文件与未跟踪产物，不安全混提。

## 下一步建议
1. 下一轮先继续做 `EMA due-check only`。
2. 若仍 `waiting_not_due`，只给 `Rank 52` **1 次最小 clean replication**。
3. clean replication 默认只回答一个问题：**setup 前最后几分钟的主动成交失衡，能不能稳定压低假突破 / 假回踩，而不是靠大砍样本制造好看结果？**
4. 若这条线最小复现后仍不能诚实给出更高层 verdict，再回退比较 `Rank 35b > tiny-live plumbing`，不要继续停在 intake wording。

## Commit hash
- 未提交。
- 原因：当前 git 工作区有大量与本轮无关的脏文件，不满足安全 selective commit 条件。
