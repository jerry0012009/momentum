# 2026-03-22 11:52 UTC — bot2 strategy review

## 本轮一句话判断
`EMA(Paper) 继续保持 running paper pilot / waiting_not_due；Live Seat 继续暂空；Scout 主资源继续围绕 Rank139(P3) 做低频健康检查 + pbo-cscv(P1) 只做 1 个“权威 source intake/或 canonical 实现”交付。`

## 1) Repo / 节奏健康
- repo 当前为 **大量未提交改动**（主要集中在 reports/site & reports/artifacts + 若干 docs/scripts），属于“持续产出+网站发布”的常见状态；本轮不做整理/commit。
- 最近 `research/optimization_loop/` 更新集中在：
  - `Rank139(P3)` health-check 连续性
  - `pbo-cscv` honesty gate 的 proxy/canonical scorecard 推进
- 最近 `research/strategy_review/` 最新条目停在 `2026-03-22_1006`；本轮补 1 条。

## 2) TRADING DESK BOARD 顶部核对（最小必要更新）
- 已核对 `docs/TODO.md` 顶部作战板：状态描述一致、Next 3 bot3 runs 顺序清晰。
- 本轮 **不需要改**（避免无意义 churn）。

## 3) Seats / Anchors / Hosted lanes（明确回答）
### Paper Seat
- **primary paper anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **当前状态**：`running paper pilot / waiting_not_due`
- **hosted / family lanes（paper family）**：
  - 美股 `1d+1wk（SPY/QQQ/AAPL）`
  - Crypto `1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### Live Seat
- **是否空**：是，`暂空`（符合当前 desk 规则：只在 Scout 候选足够接近 paper/tiny-live review 时才升格）

### Scout Seat
- **当前复刻/运行对象（主点）**：`Rank 139 / CUSUM event-bar confirm-veto gate`
  - 定位：`P3 / narrow paper pilot continuity`
  - 本轮动作边界：只做低频健康检查（ops page/CSV 更新、no_event_timeout/retention/mean_net@6bps 基本监控）；避免回到“近义研究对比”。

### 候选分档（P0~P4）
- **P3（narrow paper pilot / hosted）**：
  - `Rank 139 / CUSUM event-bar confirm-veto gate`（Scout 主点）
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（hosted narrow paper lanes，20m refresh continuity）
  - `Rank 122`（strict-only sidecar，低频 monitoring only）
- **P1（只允许 1 次便宜诚实检查 / 或 1 个小交付）**：
  - `pbo-cscv / deflated sharpe honesty gate`（横向诚实守门层，不与 rank 线竞争 seat；下一步只做 source intake 或 canonical 实现二选一）
  - `Rank 125 / range location veto gate`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
- **P0（park / evidence pool）**：
  - `Rank 138 / funding×OI crowding breadth overlay`
  - `Rank 127 / signal→confirm ATR delta phase gate`
  - `Rank 137 / state expiry latency budget gate`
  - 以及作战板里列出的其余 park ranks
- **P2 / P4**：当前作战板未指定 active P2 或 P4（P4= tiny-live review candidate 仍空缺）。

## 4) strongest evidence / weakest lines
### strongest evidence
- `Rank139(P3)` 已进入“可运行监控”的 hosted narrow paper pilot 形态，且最近 health-check 未见爆雷信号（retention/no_event_timeout 没有异常飙升、ops/CSV 持续更新）。

### weakest / should-park / 不该再磨的线
- 任何把 `Rank139(P3)` 拉回“thr_mult 继续对比、重复验证同类指标”的动作：边际价值低，且违反 P3 预算/定位。

## 5) 下一步优先级（Top 1~3）
1. **Run1（Paper）**：EMA due-check first（若真实 due-now/overdue 先做 paper refresh；否则立即切换，不空转）
2. **Run2（P3 continuity）**：Rank139(P3) hosted pilot 低频健康检查：只做 1 件事（更新/核对监控字段；记录是否出现爆雷信号）
3. **Run3（Scout honesty layer）**：pbo-cscv：只做 1 个小交付（`权威 source intake + 人话摘要` 或 `canonical CSCV/PBO/DSR 离线实现` 二选一）

## 6) 风险与不确定性
- repo 长期脏工作区会放大“误改/难回滚”风险：但这不是本轮 40m review 的主矛盾；建议后续择机做一次“发布产物与源码分离”的最小整理（不要在 bot2 轮次硬做）。
- Live Seat 仍空：这是刻意策略（避免为了填座位而引入不够诚实的 live challenger）。
