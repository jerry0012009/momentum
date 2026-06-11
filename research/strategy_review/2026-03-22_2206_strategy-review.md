# Strategy Review (bot2)

Time: 2026-03-22 22:06 UTC

## 本轮一句话判断
Desk 主线不变：**Paper Seat 仍以 EMA / 创业板ETF 1d 为 primary anchor，继续 running paper pilot / waiting_not_due；Live Seat 继续暂空；bot3 主资源继续压在 Scout Seat = Rank 140（PBO/CSCV/Deflated Sharpe honesty gate）**。最新 Run3 已把 `Rank 127 / shared_gate` 也纳入显式三臂对照，结果再次证明当前 honesty-layer 仍未出现可升格 family，因此下一轮仍应坚持 **EMA due-check → Hosted P3 事件驱动 continuity → Rank140 单 family 显式三臂 scorecard**，不要分心。

## 1) 必检：Repo 状态
- 分支：`master`
- 工作区：**dirty（大量已修改 + 未跟踪产物/脚本/报告）**
- 结论：当前 repo 明显处于高噪声状态；本轮不做清理，只把它视为“误混代码/产物、误 commit”的持续风险。

## 2) 必检：最近 optimization_loop / strategy_review
### 最近 `research/optimization_loop/`（最新 5 条）
- `2026-03-22_2206_rank140-rank127-shared-three-arm.md`
- `2026-03-22_2142_rank140-rank111-window-plus-timeout.md`
- `2026-03-22_2131_rank140-rank112-basis-extreme-veto.md`
- `2026-03-22_2050_rank140-family-board.md`
- `2026-03-22_2035_rank140-rank111-explicit-three-arm.md`

### 最近 `research/strategy_review/`（上一批 5 条）
- `2026-03-22_2037_strategy-review.md`
- `2026-03-22_1950_strategy-review.md`
- `2026-03-22_1910_strategy-review.md`
- `2026-03-22_1831_strategy-review.md`
- `2026-03-22_1733_strategy-review.md`

## 3) 必检：当前 cron 列表（只看与 desk 相关的关键项）
- `bot3-momentum-auto-opt-13m`：enabled；最近一次状态 `ok`，但当前仍在运行，说明 13m loop 正常推进中。
- `bot2-strategy-review-40m`：enabled；上次错误是 cron 自己的 JSON 解析失败，不是 desk 研究逻辑失败。
- `momentum-narrow-paper-lanes-20m`：enabled；最近 `ok`。
- `bot7-quant-digest-30m`：enabled；最近 `ok`。
- `bot6-park-reframe-2h`：enabled；最近 `ok`。

结论：当前 cron 方向与 desk 主线仍基本一致；最值得关注的是 **bot3 正在正常跑，不需要 bot2 改排班去救火**。

## 4) Desk 核心回答（authoritative）
### 4.1 Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **当前状态**：`running paper pilot / waiting_not_due`
- **hosted / family lanes**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- **最关键 gate / blocker**：不是再讲 EMA 故事，而是 **refresh continuity + week-1 review continuity + active/shadow demotion discipline**。

### 4.2 Live Seat 是否空
- **Live Seat：空（暂空）**
- 理由：当前没有任何 Scout 候选已经到 `paper candidate / tiny-live review` 的可信门槛；bot2 不该为了“桌上要有 live challenger”硬塞一个席位。

### 4.3 Scout 复刻对象
- **Scout Seat 当前主点**：`Rank 140 / pbo-cscv deflated sharpe honesty gate`
- 当前复刻方式不是再 intake 新论文/新 repo，而是对已 relevant family 做 **显式三臂 returns matrix（baseline / gate_kept / gate_veto）+ canonical CSCV/PBO/DSR scorecard**。
- 最新已跑 family：
  - `Rank 125 / rl_gate`
  - `Rank 111 / same_window_only`
  - `Rank 111 / window_plus_timeout`
  - `Rank 112 / basis_extreme_plus_oi_veto`
  - `Rank 112 / basis_extreme_veto`
  - `Rank 127 / shared_gate`

### 4.4 候选 P0~P4 分档（本轮口径）
- **P1 / keep_P1（主资源位只保留 1 个）**
  - `Rank 140 / pbo-cscv deflated sharpe honesty gate`
    - `recommended_action = keep_P1`
    - `why_now = 显式三臂 scorecard 管线已能稳定复用，但还没出现一条真正过关的参考 family`
    - `main_weakness = kept/veto 分裂后的 OOS 稳定性仍差，PBO 持续 guard_failed`
- **P1 / evidence input only（不抢主资源）**
  - `Rank 125`：目前仍是 Rank140 家族里**最像样**的参考 family，但仍 `guard_failed`
  - `Rank 111`：split 最平衡，但 `same_window_only` 与 `window_plus_timeout` 都 guard_failed
  - `Rank 112`：一旦不再用极端 split，美化效果消失，不适合再当优先参考 family
- **P0 / park / evidence pool**
  - `Rank 127`：最新显式三臂结果显示 **veto 臂优于 kept 臂**，对 Rank140 来说更像反证，不再值得继续磨近义 shared 变体
  - `Rank 137 / 138 / 127 之外的其余已 park ranks`：维持 park
- **P3 / hosted narrow paper continuity**
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
  - `Rank 139`（独立 runner）
  - `Rank 122`（sidecar monitoring）
- **P2 / P4**：本轮无新增升格对象

## 5) strongest evidence / weakest lines / should-park
### strongest evidence
1. **EMA 继续是真正的 Paper Seat anchor**：Run1 连续合规返回 `waiting_not_due`，说明当前不是执行飘移，而是市场时钟未到。
2. **Hosted P3 continuity 已经被正确降级成事件驱动**：本轮出现了 `Rank 29` 新增 closed trade append，bot3 只做最小记账核对，没有把它抬回 Scout 主资源位。
3. **Rank140 的 honesty-layer 结论在收敛，而不是在扩张故事**：
   - `Rank111 / window_plus_timeout`：`kept:veto = 113:85`，但 `PBO = 0.8000`，仍 guard_failed
   - `Rank127 / shared_gate`：`kept:veto = 525:299`，但 **veto 臂优于 kept 臂**，`PBO = 0.6286`
   - 这说明当前不是“还差一点就 promote”，而是“family board 正在诚实排除不合格家族”。

### weakest / should-park lines
- **最该彻底收口的是：把 `Rank127` 继续当 shared honesty-layer 候选来磨。**
  - 最新显式三臂读法已经很清楚：这个 gate 留下来的那一臂并没有更好，继续近义变体只会重复劳动。
- **不该回潮的线：Hosted P3 常规健康检查**
  - 只要没有 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`，它们就不该抢 Scout 主资源。

## 6) Next 3 bot3 runs（本轮排班）
1. **Run 1 = EMA due-check first**
   - 若真实 `due-now / overdue`，先做 paper refresh；
   - 若仍 `waiting_not_due`，立刻切到 Run 2。
2. **Run 2 = Hosted P3 continuity（只在 status-changing event 时认领）**
   - 允许认领：`closed-trade append / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`
   - 若只是常规运行，无事件则跳过，不做近义健康检查。
3. **Run 3 = Rank 140（只做 1 条 family）**
   - 继续显式三臂 returns matrix + canonical scorecard
   - **优先从仍可能出现“kept 优于 veto + split 可解释”的 family 里选 1 条**
   - **明确不要再回头磨 Rank127 的 shared 近义变体**

## 7) TODO / Board 是否要改
- **本轮结论：不改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。**
- 理由：
  1. 当前三席位定义仍完全正确：`Paper=EMA`、`Live=空`、`Scout=Rank140`
  2. `Next 3 bot3 runs` 仍与最新实际执行一致
  3. 最新新增证据虽然更强，但属于 **supporting evidence / family-board 内部收敛**，尚未触发 seat 级别或排班级别改变

## 8) 网页 / cron / 自动化建议
### 网页 / 表达
- 首页与 TODO 镜像只需常规 publish 刷新，不需要额外改 reader-facing 结论页。
- 下一次如果 `Rank140` 出现一条真正像样的“kept 优于 veto 且 PBO 明显改善”的 family，再考虑把 family board 的结论外显到 reader-facing 页面。

### cron / 节奏
- 当前无需改 cron 频率。
- 维持：`bot3 13m` 快循环、`narrow-paper 20m` continuity、`bot2 40m` 排兵布阵。
- 当前最重要的是 **继续让 bot3 保持“一轮只做 1 条 family”的 discipline**，而不是为了快把 family board 一口气铺满。

## 9) Top 1~3（按优先级）
1. **继续 Rank140，但只做 1 条 family 的显式三臂 + canonical scorecard**，目标是尽快确认有没有真正能留在 P1 池里的 family。
2. **EMA 继续严格 due-check**，不要因为 waiting_not_due 就伪造 refresh，也不要因此全 desk 空转。
3. **Hosted P3 只保留事件驱动 continuity**，防止常规 append/健康检查重新侵占主资源。

## 10) 风险与不确定性
- 当前 `Rank140` 最大风险不是“还没做够”，而是**继续做了很多 family 但始终没有一条能跨过 guard_failed**。若再跑 1~2 条仍无改善，bot2 下一轮应考虑把它从 `keep_P1` 压回更接近 `park / evidence layer` 的口径，而不是无限延长。
- repo 仍然很脏；若后续需要真实代码修改，混入无关产物的风险很高。

## 11) 本轮我改了什么
- 未改 `docs/TODO.md`
- 新写本轮 `strategy_review` 记录
- 将执行常规首页刷新 + 邮件发送