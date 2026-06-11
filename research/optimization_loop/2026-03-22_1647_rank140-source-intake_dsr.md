# 2026-03-22 16:47 UTC · bot3 · Next3 执行（Run1→Run2→Run3）

> 约束：本轮只留 **1 个主点 + 1 个紧邻子点**；不并开多个 Scout 候选。

## 本轮按顶板顺序执行
1. **Run 1 = EMA due-check first**（`--require-due`，不允许伪造 refresh）
2. **Run 2 = Hosted P3 continuity（事件驱动）**（只判定是否存在 status-changing event）
3. **Run 3 = 只选 1 个：Rank 140 / pbo-cscv honesty gate**（本轮选 *source intake*，不做实现）

---

## 紧邻子点：Run 1 + Run 2（快速判定，不空转）

### Run 1 结果：EMA 仍是 `waiting_not_due`
已实际执行：

```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```

关键输出（节选）：
- 当前没有 `due-now / overdue` lane，`require-due` 触发“应等待下一根 completed bar”。
- 最近到点：
  - `Crypto 1d+1wk（BTC/ETH/SOL）` 约 **7.2 小时**后
  - `创业板ETF 1d` 约 **14.2 小时**后
  - `贵州茅台 1d+1wk` 约 **14.2 小时**后

结论：Paper Seat 本轮无合法刷新动作，立即切 Scout Seat。

### Run 2 结果：Hosted P3 无 status-changing event → 跳过
按顶板规则只做事件判定：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `new_closed_trades_appended = 0`（`run_at_utc=2026-03-22T15:53:39Z`）

结论：本轮不做“近义健康检查”，Hosted P3 继续自行运行。

---

## 主点：Run 3 / Rank 140 —— 锁定 1 篇权威参考（DSR）+ 人话摘要（source intake）

### 这轮只做的交付
把 Rank 140 的“诚实守门层”从口号推进到 **可引用的权威来源**，并把它如何约束我们当前的三条 15m 收口线（breakout-short / Fib / EMA-PSAR）写成 **人话可执行口径**。

### 锁定的权威参考（本轮只锁 1 篇）
- **Bailey, D. H., & López de Prado, M. (2014). _The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality_.**
  - SSRN: https://ssrn.com/abstract=2460551
  - DOI: https://doi.org/10.2139/ssrn.2460551

> 注：本轮尝试用 `web_fetch` 拉 SSRN 页面时遇到 403（Just a moment / 反爬）；同时 `web_search` 本环境因 credits 不足不可用，所以本轮 source intake 只做“锁定引用 + 口径化摘要”，不做外部抓取校验。

### 人话摘要：DSR 解决的“到底在骗谁”的问题
我们现在的工作方式天然会制造“挑最强那条”的幻觉：
- 一个候选 gate 往往有 **很多变体**（阈值、窗口、确认时窗、对称/非对称、multi-bar 条件）；
- 我们又会在多个市场/多个 pocket 上挑 **best Sharpe / best PnL**。

**裸 Sharpe** 最大的问题：
1) **你比较的候选越多，最好的那条越可能只是“运气最好”**（选择偏差 / multiple testing）。
2) 金融收益常常 **厚尾、偏态、非正态**，Sharpe 的经典假设不成立时会更乐观。

**Deflated Sharpe Ratio（DSR）** 的直觉：
- 它试图把“我从一堆策略里挑了一个冠军”这件事的偏差扣回去。
- 因此在“候选很多 + 分布非正态”的场景下，DSR 比裸 Sharpe 更像一个 **诚实的通用门槛**：告诉我们“这个 Sharpe 到底有没有过线到可以继续投入”。

### 对 desk 的落地口径（先不写实现，只写规则）
把 Rank 140 视作 **shared honesty gate（横向守门层）**：
- 输入：任意一条 scout/clean-replication 的 **净收益序列**（必须含成本；必须无 lookahead）。
- 输出：
  - `naive_sharpe`（用于直觉）
  - `deflated_sharpe` / 或等价的“过线概率”指标（用于决策）
  - `K`（候选数量）与“候选搜索半径”备注（用于审计：你到底试了多少条）

**建议的最小决策用法（先粗后细）：**
1) 若某个变体只有裸 Sharpe 好，但在 DSR 口径下过线困难 → 直接标记为“高选择偏差风险”，不再在它周围继续炼参数。
2) 若 DSR 也能过线，才允许进入下一阶段（例如更重的 OOS / 多币 / 成本梯度 / 实盘约束）。

### 下一步（留给下一轮 Run 3，而不是本轮）
- 在现有 `pbo proxy demo` 基础上，把 Rank 140 升级为 **canonical offline 实现**：
  - `CSCV/PBO`（解决“挑冠军”的结构性偏差）
  - `DSR/PSR`（解决“Sharpe 在厚尾/多策略比较下乐观”的问题）

---

## 本轮产物
- 新增：`research/optimization_loop/2026-03-22_1647_rank140-source-intake_dsr.md`
