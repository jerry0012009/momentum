# 2026-03-22 23:40 UTC · Rank 14b / directional breadth coherence source-intake freeze

## 本轮按顶板顺序执行

### Run 1 · EMA due-check first
已实际运行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

结果：`waiting_not_due`
- 当前没有 `due-now / overdue` lane
- 最靠前 lane：`Crypto 1d+1wk（BTC/ETH/SOL）`
- 状态：`due_soon`
- 距下次到点：约 `19 分钟`

结论：`Paper Seat / EMA` 仍在等，不得伪造 refresh；必须立刻切去允许动作。

### Run 2 · Scout Seat 主点
本轮只保留 **1 个主点**：`Rank 14b / directional-breadth-coherence long-side continuation veto`

这轮不回头继续磨：`Rank 140 / 125 / 112 / 111`。
原因很直接：
1. 顶板已要求：连续两轮没有层级变化、也没有 decisive evidence 的 `P1`，不得继续霸占 Scout 主资源；
2. 上一轮已把 Scout 主点切到 `Rank 14b`，这轮该做的不是再换候选，而是把它的 **source intake / clean-replication 第一刀真正冻结清楚**；
3. `Rank 14b` 的修改轴仍然只有一条：**不用 peer confirm；改成 pre-signal 1h directional breadth coherence 过低时，直接 veto 新 long entry。**

### Run 3 · 便宜但可能改变级别的小动作
本轮只做 1 个紧邻子点：**冻结 Rank 14b 的第一刀接线顺序与禁止项**。

## 本轮硬冻结（source-intake 口径）

### 1) 第一刀只接 1 条 archetype
**先接 `EMA/PSAR continuation long`，暂不并行接 `Fib retest_hold long`。**

原因：
- digest 已给出明显多空不对称：`low breadth` 对 long 侧更坏；
- `EMA/PSAR continuation long` 是 desk 当前更自然的 shared continuation archetype，接线最直；
- 若第一刀同时接 `EMA + Fib`，就会把“变量信息量”与“base setup 差异”混在一起，不符合本轮只开 1 个主点 + 1 个紧邻子点的纪律。

### 2) 第一刀只比较两臂
- `baseline_long`
- `low_breadth_veto_long`（`dir_breadth_1h <= 0.45` 时 veto）

本轮**不允许**顺手加入：
- `half-size`
- `short mirror`
- `second threshold`
- `第二条 base setup`
- 新 exit / 新 universe / 新 regime stack

### 3) 第一刀主看 4 个指标
1. `post_cost_expectancy`
2. `trade_retention`
3. `false_follow_ratio`（或同义的快失败占比）
4. `long-side symbol dispersion`

### 4) 第一刀的 desk 判分门槛
本轮先不给它虚高层级，只冻结最小 admission 规则：
- 若 `veto_long` 只能靠大幅砍单美化，`trade_retention` 明显过低，则直接压回 `park / evidence_pool`；
- 若 `trade_retention` 仍可接受，且 `post_cost_expectancy` / `false_follow_ratio` 至少有一项出现诚实改善，再保留 `keep_P1`；
- 在只做 `EMA/PSAR long` 单臂前，不讨论 `promote_P2`。

## 本轮结论
**`Rank 14b = keep as current Scout primary for exactly one minimal clean-replication cut`**

但这次保留是有明确护栏的：
- 只许接 `EMA/PSAR continuation long`
- 只许跑 `baseline vs veto-only`
- 只许回答上面 4 个便宜问题
- 若下一刀仍拿不出 decisive evidence，就应继续切到下一 active Scout / fresh reserve，而不是把 Rank 14b 也磨成新的长期占位候选

## 给下一轮的最短提醒
- 若 EMA 到点：先做真实 `Run 1` refresh。
- 若 EMA 仍未到点：优先把 `Rank 14b` 落成 **EMA/PSAR long 单臂 clean replication**，不要同时把 `Fib retest_hold` 也打开。

## 本轮交付
- 日志：`research/optimization_loop/2026-03-22_2340_rank14b-source-intake-freeze.md`
