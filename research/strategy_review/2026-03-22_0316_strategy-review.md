# Strategy Review (bot2)

时间：2026-03-22 03:16 UTC

## 本轮一句话判断
`Paper Seat(EMA)` 仍是主线，但当前看起来处于 **waiting_not_due**；因此 bot3 主资源应继续按作战板：**先 due-check，再做 Rank139(P3) 低频健康检查，然后只做 1 个“pbo-cscv 诚实守门层”的最小交付**；同时注意 bot3 cron 最近出现 `Unexpected end of JSON input` 报错，优先把“输出/写文件/发邮件/刷新首页”的链路稳住。

## Repo / 状态
- git branch: `master`
- HEAD: `fce2dd7 Avoid immediate flatten when exchange stop attach fails`
- working tree: **大量未跟踪 artifacts / reports / logs**（不在本轮清理范围；建议后续统一 `.gitignore` / 归档策略，避免影响真实 diff 信噪比）

## 最近 optimization_loop / strategy_review 变化（抽样）
- optimization_loop 最近：
  - `2026-03-22_0253_bot3-rank139-health_pbo-source-intake.md`
  - `2026-03-22_0240_rank139-health_pbo-cscv-intake.md`
  - `2026-03-22_0227_rank139-p3-healthcheck.md`
  - `2026-03-22_0146_bot3-fresh-intake-pbo-cscv.md`
  - `2026-03-22_0136_run3-rank51-fresh-intake.md`
- strategy_review 最近：
  - `2026-03-22_0235_strategy-review.md`
  - `2026-03-22_0151_strategy-review.md`
  - `2026-03-22_0108_strategy-review.md`

## 当前席位结论（回答作战板问题）
### Paper Seat
- **primary paper anchor**：`EMA / 创业板ETF 1d (active_primary)`
- hosted / family lanes（当前）：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### Live Seat
- **是否空**：是（保持“暂空”合理；暂无明确应升格为 tiny-live review 的 winner）

### Scout Seat（当前复刻对象）
- **Rank 139 / CUSUM event-bar confirm-veto gate**（当前定位：`P3 narrow paper pilot`，以 hosted pilot/monitoring/refresh 口径维持可见性，不再做近义研究磨损）

## Scout 候选 P0~P4 分档（以当前作战板为准）
- **P3（narrow paper pilot / hosted continuity）**：
  - `Rank 139`（当前 Scout 主点）
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m refresh hosted lanes；sidecar only）
  - `Rank 122`（strict-only sidecar；低频监控）
- **P1（只允许 1 次便宜诚实检查/最小交付）**：
  - `pbo-cscv / deflated sharpe honesty gate`（新 intake；下一步做 source intake 或 minimal implementation 二选一）
  - `Rank 125 / range location veto gate`（budget used）
  - `Rank 112 / basis dislocation short veto`（budget used）
  - `Rank 111 / abnormal-return event clock`（budget used）
- **P0（park / evidence pool）**：
  - `Rank 138 / funding×OI crowding breadth overlay`（single-pocket dependency）
  - `Rank 127 / ATR delta phase gate`（time-stability 转负，不升 P2）
  - 以及作战板列出的其余 parked ranks
- **P2 / P4**：当前作战板没有明确 active P2 或 P4（维持不强行填空）

## Next 3 bot3 runs（排班确认）
1. **Run 1：EMA due-check first**（如有 due-now/overdue → 先 paper refresh；如 waiting_not_due → 立刻切 Run2）
2. **Run 2：Rank139(P3) hosted narrow paper pilot 低频健康检查（只做 1 件事）**
3. **Run 3：pbo-cscv honesty gate 只做 1 个最小交付**
   - 二选一：`source intake（锁定 1 篇权威参考 + 人话摘要）` 或 `minimal implementation（给 scout scorecard 加 deflated_sharpe / pbo_risk_flag 1 列）`

## Strongest evidence（本轮最重要）
- Rank139 已从“候选结论”推进到 **P3 hosted narrow paper pilot**（monitoring/ops 字段已落地，包含 `no_event_timeout`）。

## Weakest / should-park lines
- 当前大量 P1 候选已 `budget used`，不应再继续磨；除非出现明确“能改变档位”的廉价检查，否则默认维持 park/evidence。

## TODO / web / cron 建议（本轮最小干预）
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`：**本轮不改**（当前已与最新 evidence 一致，且 Next 3 runs 排班清晰）。
- cron 风险提示：
  - `bot3-momentum-auto-opt-13m` 上次报错：`Unexpected end of JSON input`（consecutiveErrors=1）→ 建议下一轮 bot3 优先做“最短链路的成功交付”，避免长输出导致 JSON 截断。
  - 多个任务出现同类 JSON 截断（bot6 / rank32b live 等）→ 可能是某处输出被截断/拼接；后续若持续出现，应单独开一条 infra 排查任务。

## 风险与不确定性
- 当前 desk 的主要不确定性不在“是否还有更强的 rank 候选”，而在 **paper/hosted pilot 的持续运行可审计性**（refresh continuity、review continuity、输出链路稳定性）。
