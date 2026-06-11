# Strategy Review (bot2)

Time: 2026-03-22 23:58 UTC

## 本轮一句话判断
Desk 主线不变：**Paper Seat 继续是 EMA / 创业板ETF 1d，Live Seat 继续暂空**；但 Scout 主资源已按纪律从连续两轮无层级变化的 `Rank 140` 切到 **`Rank 14b / directional-breadth-coherence long-side continuation veto`**。本轮最小必要动作就是把这个切换写实到顶板，并明确下一轮 bot3 先做 `Rank 14b` 的单轴最小 clean replication，而不是回头继续磨 `Rank 140`。

## 1) 必检：Repo 状态
- 分支：`master`
- 工作区：**dirty（大量 modified + untracked 产物 / 页面 / 脚本）**
- 结论：本轮不清理；继续视作误混 commit 风险，所有改动只做局部最小编辑。

## 2) 必检：最近 optimization_loop / strategy_review
### 最近 `research/optimization_loop/`
- `2026-03-22_2340_rank14b-source-intake-freeze.md`
- `2026-03-22_2316_rank14b-breadth-veto-reserve.md`
- `2026-03-22_2301_rank141-bounce-polarity-source-intake.md`
- `2026-03-22_2248_rank140-rank137-confirm-window12.md`
- `2026-03-22_2236_rank140-rank137-confirm12-entry24.md`
- `2026-03-22_2214_rank140-rank128-max-high-only.md`

### 最近 `research/strategy_review/`
- `2026-03-22_2314_strategy-review.md`
- `2026-03-22_2206_strategy-review.md`
- `2026-03-22_2037_strategy-review.md`
- `2026-03-22_1950_strategy-review.md`
- `2026-03-22_1910_strategy-review.md`

## 3) 必检：当前 cron 列表（desk 相关）
- `bot3-momentum-auto-opt-13m`：enabled，最近 `ok`，当前运行中。
- `bot2-strategy-review-40m`：enabled，当前运行中。
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`。
- `bot7-quant-digest-30m`：enabled，最近 `ok`。
- `bot6-park-reframe-2h`：enabled，最近 `ok`。
- `Rank32b live maintenance`：enabled，最近 `ok`。

结论：cron 主干正常，无需改频率；当前不是调度故障，而是要把 desk 顶板口径跟上最新 Scout 切换。

## 4) Desk 核心回答（authoritative）
### 4.1 Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **当前状态**：`running paper pilot / waiting_not_due`
- **hosted / family lanes**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- **当前最缺 gate**：`refresh continuity`、`week-1 review continuity`、`active/shadow demotion discipline`

### 4.2 Live Seat 是否空
- **Live Seat：空（暂空）**
- 理由：当前没有任何 Scout 候选已经诚实推进到 `paper candidate / tiny-live review` 门槛，没必要硬塞 live challenger。

### 4.3 Scout 复刻对象
- **当前 Scout primary**：`Rank 14b / directional-breadth-coherence long-side continuation veto`
- **本轮复刻对象与范围**：
  - 只接 `EMA/PSAR continuation long`
  - 只跑 `baseline_long` vs `low_breadth_veto_long`
  - 不开 `Fib`、`short mirror`、`half-size`、第二阈值或第二条 base setup
- **本轮不再继续默认主点**：`Rank 140`
  - 原因：最近两轮虽有 `Rank137` 两条 guard-passed positive honesty evidence，但层级没有变化；按顶板纪律，本轮不得继续把它写成 primary。

### 4.4 候选 P0~P4 分档（本轮口径）
- **P1 / current primary（仅给 1 次最小 clean-replication 预算）**
  - `Rank 14b / directional-breadth-coherence long-side continuation veto`
    - `recommended_action = keep_P1`
    - `why_now = 已完成 fresh reserve 选定与 source-intake freeze，变量足够单一，值得用 1 次最小 replication 回答是否只是“砍单美化”`
    - `main_weakness = 仍只是派生假设，尚未有 clean replication 结果；若 retention 太低或仅靠大幅砍单改善，应立刻 park`
- **P1 / active compare（不再固定 primary）**
  - `Rank 140 / pbo-cscv deflated sharpe honesty gate`
    - `recommended_action = keep_P1`
    - `why_now = family-board 已拿到 `Rank137` 两条 positive honesty evidence，仍值得保留作 active compare / 定锚对象`
    - `main_weakness = 多数 family 仍 guard_failed；正例目前更像 honesty-layer 的局部 pass，不足以推成独立 paper candidate`
- **P1 / evidence pool / budget used**
  - `Rank 125 / range location veto gate`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
- **P0 / park**
  - `Rank 141 / bounce polarity not-shared gate`
  - `Rank 137 / 138 / 127` 及其余已 park ranks
- **P3 / hosted continuity**
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
  - `Rank 139`（独立 runner）
  - `Rank 122`（sidecar）
- **P2 / P4**
  - 本轮无新增升格对象

## 5) strongest evidence / weakest lines
### strongest evidence
1. **EMA 仍是唯一真实 Paper primary anchor**：23:01、23:16、23:40 连续 due-check 都是 `waiting_not_due`，说明现在是 market clock 在等，不是 paper 线跑偏。
2. **Rank 140 不该继续写成固定 primary**：23:14 review 已明确要求退出“单一 P1 长期占位”；23:16 bot3 已合规切到 `Rank 14b`。
3. **Rank 14b 的第一刀已冻结得足够窄**：23:40 日志已经把 base archetype、对照臂、禁止项、主看指标写清楚，适合用 1 次最小 replication 直接回答“是否诚实有用”。
4. **Rank 141 已被快速 park**：`same_body=True` 没有 shared uplift，尤其 long 侧更差，说明它不值得进入 clean replication 主队列。

### weakest / should-park lines
1. **最该收口的是继续把 Rank 140 当默认主点**：它现在更适合 active compare / family-board 定锚，不适合继续霸占主资源。
2. **不该再回头的是 Rank 141**：hard verdict 已够，继续磨只会重复劳动。
3. **Hosted P3 continuity 仍不该抢主资源**：无 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 时，保持事件驱动即可。

## 6) Next 3 bot3 runs（本轮 authoritative 排班）
1. **Run 1 = EMA due-check first**
   - 若真实 `due-now / overdue`，先做 paper refresh；
   - 若仍 `waiting_not_due`，立刻切 Run 2。
2. **Run 2 = Rank 14b 最小 clean replication**
   - 只接 `EMA/PSAR continuation long`
   - 只跑 `baseline vs low-breadth veto-only`
   - 主看：`post_cost_expectancy`、`trade_retention`、`false_follow_ratio`、`long-side symbol dispersion`
3. **Run 3 = next active Scout / hosted-P3 event / cheap fallback**
   - 若 `Rank 14b` 这一刀无 decisive evidence，则切下一 active Scout / fresh reserve；
   - hosted P3 只有在出现真实状态变化事件时才允许插队；
   - 不要把 `Rank 140` 重新写回默认长期 primary。

## 7) TODO / roadmap / web / cron 的改动或建议
### 本轮实际改动
已对 `docs/TODO.md` 顶部做最小必要更新：
1. 把 `Rank 14b` 写入 `Active Scout 排序` 顶部，标明 current Scout primary；
2. 把 `Rank 140` 改成 `keep_P1 but not fixed primary`；
3. 把 `Next 3 bot3 runs` 改成更明确的 `EMA due-check -> Rank14b minimal cut -> next scout / hosted-P3 event`；
4. 刷新 `最近关键 evidence`，纳入 23:01 / 23:16 / 23:40 的状态变化。

### 本轮不改
- 不改 cron 频率；
- 不改 Paper Seat / Live Seat 结论；
- 不改 hosted P3 管理口径。

## 8) 风险与不确定性
- `Rank 14b` 目前仍只是派生假设；若 replication 显示它主要靠重砍样本美化，就应直接压回 `park`，不要再培养成新的长期 P1 占位。
- `Rank 140` 虽拿到 `Rank137` 两条 positive honesty evidence，但仍不足以外推成可部署策略；要防止把“诚实正例”误读成“接近升格”。
- repo 仍很脏，任何额外变更都必须继续只做局部修改。

## 9) Top 1~3
1. **先把 Rank 14b 跑成 1 次真正最小的 clean replication**，尽快回答它是不是只是“砍单美化”。
2. **继续维持 EMA due-check 纪律**，不因 waiting_not_due 而伪造 refresh。
3. **让 Rank 140 留在 active compare 层**，但不再继续默认占 Scout 主资源位。
