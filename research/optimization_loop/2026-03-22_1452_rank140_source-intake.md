# Bot3 Optimization Loop — Rank 140 / PBO-CSCV honesty gate source intake

- 时间：2026-03-22 14:52 UTC
- 主点：`Rank 140 / pbo-cscv deflated sharpe honesty gate`
- 本轮遵循：`Run 1 -> Run 2 -> Run 3`
- 本轮范围控制：只做 **1 个主点**（Rank 140 的权威 source intake），外加 **1 个紧邻子点**（把它翻译成 desk 可执行的最小接入规则）；**没有同时打开多个 Scout 候选**。

## 0) 顺序执行记录

### Run 1 = EMA due-check first
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`，当前没有 `due-now / overdue` lane。

最新最近 due：
- `Crypto 1d+1wk（BTC/ETH/SOL）`：约 `9.1h` 后
- `创业板ETF 1d`：约 `16.1h` 后
- `贵州茅台 1d+1wk`：约 `16.1h` 后

结论：这轮 **不得伪造 refresh，也不得空转**，按顶板要求立刻切下一允许动作。

### Run 2 = Hosted P3 continuity（事件驱动）
检查 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`：
- `run_at_utc = 2026-03-22T14:51:50Z`
- `new_closed_trades_appended = 0`

结论：当前**没有看到新的 status-changing event**（没有 refresh 失步、ledger 爆雷、open-position 异常、red-watch 级别变化），因此本轮按规则 **跳过**，不做近义健康检查重复劳动。

### Run 3 = Rank 140（本轮实际主动作）
本轮只做 `source intake`，不再重复 proxy/demo，也不同时打开别的 Scout 候选。

---

## 1) 本轮锁定的权威 source（authoritative source lock）

### 选定文献
**Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. J. (2015). _The Probability of Backtest Overfitting_. Journal of Computational Finance.**
- DOI/SSRN：`https://doi.org/10.2139/ssrn.2326253`
- Readable：`https://ssrn.com/abstract=2326253`

### 为什么这篇是 Rank 140 当前最该锁的 canonical source
因为 Rank 140 当前不是在找“又一个新 alpha 想法”，而是在给现有候选池补一个**诚实守门层**。这篇 paper 刚好回答的就是：

> 当我们从一堆回测候选里挑“样本内最好”的那条时，究竟有多大概率只是挑中了噪声？

它的价值不在于生成信号，而在于：
1. 给 `model selection / 参数搜索 / 规则挑选` 这一步提供统一的 honesty check；
2. 把“best Sharpe 看起来很强”翻译成“这很可能只是被选择偏差喂出来的幻觉”；
3. 非常契合当前 desk 的真实工作流：我们确实在 `EMA / PSAR`、`breakout-short`、`Fib retest_hold` 上不断枚举变体，再从中挑最好的那条。

所以它比泛泛的“Sharpe 更稳健”讨论更贴 Rank 140 的主任务定义，应该作为**canonical first source** 锁定。

---

## 2) 人话摘要：这篇 paper 到底在说什么

### 一句话版
**如果你试了很多版本，再拿样本内表现最好的那个去讲故事，你大概率是在高估自己；PBO 就是把这种“挑中假强者”的概率量化出来。**

### desk 口径版
对当前 momentum desk 来说，这篇 paper 的核心提醒是：
- 不是某个确认层本身一定有问题；
- 真正危险的是：**同一条策略线上试太多小变体后，再把“最赢的那条”当成真 edge**；
- 所以 `Rank 140` 的职责应该是给候选池加一个统一 admission gate，而不是自己去竞争 `Paper Seat`。

### 更直白一点
假设你对同一套 15m 数据试了 80 个过滤器/阈值组合，最后总会有几条看起来特别漂亮。问题是：
- 漂亮，不等于可迁移；
- 很多时候只是刚好把历史噪声拟合得很好；
- 一旦换到 OOS 或下一段时间，就会塌。

PBO/CSCV 的作用，就是专门衡量这种“历史里挑冠军”的幻觉有多重。

---

## 3) 本轮沉淀的最小 canonical interpretation（给工程落地用）

### 3.1 Rank 140 的对象不是单条策略，而是“候选集合”
如果只有 1 条规则，PBO 几乎没什么意义；它要处理的是：
- 同一 research line 下的一组可枚举候选；
- 例如 `breakout-short` 的不同确认窗 / 阈值；
- 或 `Fib retest_hold` 的不同 zone 深度 / 容差 / volume gate；
- 或 `EMA/PSAR` 的不同 admission / veto / delay 组合。

所以 Rank 140 的最小落地单元应是：
**`candidate family -> aligned return matrix -> CSCV/PBO verdict`**。

### 3.2 它回答的不是“赚不赚钱”，而是“你是不是在挑样本幻觉”
因此它应放在流程里的位置是：
- `clean replication` 之后，`promote_to_paper_candidate` 之前；或
- 至少放在“候选集里挑 winner”那一步之前。

换句话说，它更像：
- `honesty-layer`
- `selection-bias toll gate`
- `shared admission check`

而不是新的信号本体。

### 3.3 当前最朴素、最适合 desk 的门槛
先别发明复杂制度，本轮建议只沉淀这条最小口径：
- `PBO < 0.20`：可继续保留到下一轮
- `0.20 <= PBO <= 0.40`：高风险候选，只能带保留意见继续
- `PBO > 0.40`：默认不升格，优先 park

这不是终版制度，但已经足够让当前 desk 避免继续被“best backtest line”反复诱导。

---

## 4) 紧邻子点：把论文翻成当前 desk 的接线规则

本轮只补 1 个紧邻子点，不再扩散到实现细节大工程。

### 建议的接线位置
对任一 fresh Scout family：
1. 先完成最小 clean replication；
2. 若要在多个近义变体中挑 winner，先形成统一 `returns matrix`；
3. 再跑 `CSCV/PBO`；
4. 只有在 `PBO` 过最小门槛后，才允许继续争取 `paper candidate / tiny-live review`。

### 当前最适合的首个接线对象
优先不是已经 hosted 的 P3 lane，而是**未来还会继续枚举变体的 fresh scout family**。
也就是说，Rank 140 的边际价值主要服务：
- 新 intake 的 confirmation / veto / filter 变体筛选；
- 而不是回头给已 hosted 的旧 lane 做漂亮但边际价值很低的事后统计装饰。

---

## 5) 本轮 hard verdict

### 对 Rank 140 的当前结论
**`guard-passed / source_locked / ready_for_canonical_offline_implementation`**

含义：
- `minimal proxy demo` 已经完成；
- 这轮又补上了 1 篇真正对口的权威母体文献；
- 因此 Rank 140 下一次合法主动作，应是：
  **把 CSCV/PBO/DSR 做成可离线复跑、可喂给单个 candidate family 的 canonical implementation**；
- 不应再回头重复“它为什么有意义”的近义 intake。

### 对 desk 队列的影响
如果后续 `EMA` 仍 `waiting_not_due`、P3 也无事件，那么 Rank 140 下一轮就不该再做 source intake，而应该直接进：
- `canonical offline implementation`（优先）
- 输入：单一 family 的 aligned returns matrix
- 输出：`PBO / OOS degradation / DSR` 的最小 scorecard

---

## 6) 本轮留痕 / 外显
- 日志：本文件
- 首页刷新：应在本轮后执行 `bash scripts/publish_homepage_index.sh`
- 邮件：应以本文件作为正文发送中文摘要

## 7) 给下一轮 bot3 的一句话
**Rank 140 的“为什么要做”已经够了；下一手别再讲故事，直接做 canonical offline implementation。**
