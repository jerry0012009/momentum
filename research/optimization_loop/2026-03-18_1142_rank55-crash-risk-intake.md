# 2026-03-18 11:42 UTC — Rank 55 论文型 crash-risk overlay source intake

## 为什么这次选这个
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：`ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane，`EMA` 继续处于 `running paper / waiting_not_due`。
- 因此按当前权威 `Next 3`，本轮应执行 `Run 2 = fresh paper/repo intake`，而不是回头挤占 `P3 continuity` 或过早掉到 `Rank 35b / Rank 16b / tiny-live plumbing`。
- 在当前允许动作里重新比较边际价值后，这轮认领的是 **`Rank 55 / order-imbalance crash-risk overlay`**：它不是新主 alpha，而是给现有 `breakout-short / Fib retest_hold / EMA-PSAR` 三条主线补一个共享 risk overlay。

## 做了什么改动
### 主点：Rank 55 source intake + 两条轻量诚实守门
- 新增 intake artifact：
  - `reports/artifacts/literature/scout_rank55_order_imbalance_crash_risk_source_intake_card.csv`
- 新增 reader-facing 页面：
  - `reports/site/reading/repo_scout/rank55_order_imbalance_crash_risk_source_intake.html`

### 紧邻子点：authoritative board 最小写回
- 在 `docs/TODO.md` 顶部权威区追加 `2026-03-18 11:42 UTC` 补充：
  - 把这条 fresh paper intake 正式冻结为 **`Rank 55`**；
  - 写回它的边际价值比较、当前 `guard-passed / admit_to_clean_replication_queue` verdict；
  - 把 `Next 3` 收紧成：`Run 1 = EMA due-check only -> Run 2 = Rank 55 minimal clean replication（仅当 EMA 仍 waiting_not_due） -> Run 3 = 若 Rank 55 replication 没有被判死刑，则只给它 1 个 truly verdict-changing 的 Light Stability Pack；否则回退 Rank 35b > Rank 16b > tiny-live plumbing`。

## 验证 / 证据
### 1）Paper Seat 仍是 waiting_not_due
`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 当前显示：
- `美股 1d+1wk -> 2026-03-18 20:00 UTC`
- `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
- `A股三条 lane -> 2026-03-19 07:00 UTC`
- `due_bucket` 全部仍为 `waiting_not_due`

因此本轮不该伪造 `EMA` continuation，而应转到 `Scout Seat` 的 fresh intake。

### 2）为什么是 Rank 55，而不是直接回退到 Rank 35b / tiny-live
这轮重新按当前允许动作做了边际价值比较：
- `Rank 55 / order-imbalance crash-risk overlay`（fresh paper-based、可横向服务三条现有主线的 shared risk layer）
- `>` `Rank 35b`（derived fallback）
- `>` `Rank 16b`（derived fallback）
- `>` `Run 3 / tiny-live plumbing`

原因很直接：它不重写 entry，只回答“当前是不是 crash-prone，应该不应该放行/减仓”。这比继续磨派生 fallback 更贴当前 desk 主线，也更符合 `Scout Seat` 的“先硬门槛、再分级、再限预算”。

### 3）两条轻量诚实守门
- `trade on`：base setup 继续负责方向与价位；只有当最近 `3~6` 根 `1m/5m` 主动成交失衡与短窗波动共同把 `p_crash` 推到高阈值时，才允许把它作为 regime gate：
  - `breakout-short`：可放行/略增仓；
  - `Fib retest_hold / EMA-PSAR long`：减仓或直接 veto。
- `trade off`：若 `p_crash` 仍低或接近中性，则 overlay 不单独开仓；它只能负责风险放行/减仓，不能把论文里的日级 crash nowcast 偷换成逐根 `15m` alpha。
- `lookahead / repaint / leakage`：论文主问题是 crash nowcast，不是逐根入场；desk 迁移时必须把特征冻结在 setup 前最近 `3~6` 根 micro-flow 摘要，统一 `next-bar open + no-overlap`，并明确这里只能公开复刻 `aggTrades flow proxy`，不是完整 L2 order-book。

### 4）当前最小 clean replication 口径（只预留下一轮）
下一轮若 `EMA` 仍 `waiting_not_due`，只允许给它 **1 次最小 clean replication**：
- `BTC/ETH/SOL 180d 15m`
- 复用现有三条 base archetype（`breakout-short / Fib retest_hold / EMA-PSAR`）
- 比较三臂：
  - `base`
  - `+binary crash-risk veto`
  - `+size haircut`
- 执行冻结为：`setup 前 micro-flow summary -> next-bar open -> no-overlap -> hold 8 bars`
- 先看四个便宜指标：
  - `post-cost return@6bps`
  - `max drawdown`
  - `false-hold-4bars`
  - `trade_count_retention`

## 当前硬结论
- **`Rank 55 / order-imbalance crash-risk overlay = guard-passed / admit_to_clean_replication_queue`**。
- 更直白地说：它值得拿 1 次最小 clean replication 预算，但当前还只是 shared risk overlay 候选，不是新主 alpha，也不配无限续命。

## Reader-facing 落点
- `reports/site/reading/repo_scout/rank55_order_imbalance_crash_risk_source_intake.html`
- `docs/TODO.md` 顶部权威板已同步写回
- 原始 quant digest 证据页：`reports/site/reading/quant_digests/2026-03-18_1125_order-imbalance-crash-risk-overlay.html`

## 风险 / 边界
- 这是对论文思想的 desk 降级迁移，不是对原论文完整统计管线的全量复现；
- 论文核心资产是 BTC crash nowcast，迁移到 ETH/SOL 必须接受“先做 proxy / 不默认参数共享”的边界；
- 当前 git 工作区存在大量与本轮无关的脏文件，未做 commit，避免混提。

## 下一步建议
1. 下一轮先继续 `EMA due-check only`；
2. 若仍 `waiting_not_due`，只允许给 `Rank 55` 1 次最小 clean replication；
3. 若 `Rank 55` replication 后没有被判死刑，则再给它 1 个 truly verdict-changing 的 `Light Stability Pack`（默认先看时间稳定性），直接做 `P2 / park` 判断；
4. 若 `Rank 55` 也失败，再回退比较 `Rank 35b > Rank 16b > tiny-live plumbing`。

## Commit hash
- 未提交。
- 原因：当前 git 工作区有大量与本轮无关的脏文件与未跟踪产物，不安全 selective commit。
