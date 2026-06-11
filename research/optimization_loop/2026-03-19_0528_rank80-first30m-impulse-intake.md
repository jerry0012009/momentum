# 2026-03-19 05:28 UTC — Rank 80 first-30m impulse quality source intake

## 本轮先核对的 desk 状态
- repo 工作区存在大量与本轮无关的脏文件；本轮未做 commit，也未混提无关改动。
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 全 desk 仍无 `due-now / overdue`
  - 最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T05:16:03Z`
  - `new_closed_trades_appended=0`
  - 结论：当前没有新的 `P3 continuity` status-changing event 需要抢占主资源
- 顶板最新 `Next 3` 显示：`Rank 79` 已在 05:07 UTC 给出 `park / evidence pool`，因此本轮合法主动作应回到 fresh Scout，并优先比较：`first-30m impulse quality gate > RS+/RS- asymmetry gate > 其他 fresh source`

## 本轮只认领的主点
- **主点：`Scout Seat / Rank 80 / first-30m impulse quality shared gate` source intake + 两条轻量诚实守门**
- 未额外打开其他候选；只做边际价值比较后认领 1 条 fresh source。

## 为什么本轮选 Rank 80
本轮按当前 active Scout 候选重新比较边际价值：
1. **Rank 80 / first-30m impulse quality gate**
   - 最直接服务当前主线的 continuation 假延续问题
   - 只依赖 5m OHLCV/volume/volatility，工程最便宜
   - 能同时服务 `breakout-short / EMA-PSAR continuation`，并给 `Fib retest_hold` 一个 shared 质量闸门
2. **RS+/RS- asymmetry gate**
   - 更像方向性 veto / sizing layer
   - 价值仍高，但优先级低于先回答“这段 continuation 根本该不该放行”
3. **ETF lead regime gate / Fib trend-strength layer / 其他 fresh source**
   - 前者外部数据链路更重；后者更偏单 lane admission

因此本轮主资源应先给 `first-30m impulse quality`，而不是直接跳去 RS+/RS- 或继续回头磨 `P3 continuity`。

## 本轮冻结的 source-intake 口径
- 候选：`Rank 80 / first-30m impulse quality shared gate`
- 来源：`Shen, Urquhart, Wang (2022)` + `Gao et al. (2018)`
- 核心迁移：
  - 不把“开段强”偷渡成独立 alpha
  - 只把它当成 shared continuation gate：
    - `开段 30 分钟方向明确 + 高量 + 高波动` 时，放宽 continuation
    - 否则 `half-size / veto`

### 两条轻量诚实守门
1. **trade on / trade off 已可清楚写成规则**
   - `trade on`：session 前 30 分钟的方向、量能、波动共同确认，才放宽 continuation setup
   - `trade off`：不满足条件时只做 `half-size / veto`，不能把该 gate 偷渡成独立进场逻辑
2. **无明显 lookahead / repaint / data leakage**
   - 首轮只允许使用当前 session 前 `6` 根 `5m` 的收益、成交量 z-score、realized-vol
   - desk 统一执行口径仍是：`signal 当根及之前数据 + next-bar open + no-overlap`
   - 不允许用后续 session 表现回填 quality 标签

## 本轮 hard verdict
- **`Rank 80 / first-30m impulse quality shared gate = guard-passed / admit_to_clean_replication_queue`**
- 当前 seat 分级更新建议：
  - `Rank 80 = P1 weak candidate（guard-passed / minimal clean replication next）`
  - `RS+/RS- asymmetry gate = P0 fresh-source queue / source intake next`
  - `ETF lead regime gate`、`Fib trend-strength admission layer` = `P0 intake pool`
  - `Rank 79 / 77 / 76 / 75 / 74 / 73 / 72 = P0 park / evidence pool`
  - `Rank 17 / 2 / 29 / 32b = P3 narrow paper continuity`

## 本轮产物
- artifact:
  - `reports/artifacts/literature/scout_rank80_first30m_impulse_quality_source_intake_card.csv`
- reader-facing page:
  - `reports/site/reading/repo_scout/rank80_first30m_impulse_quality_source_intake.html`

## 对顶板的建议更新（Next 3）
- `Run 1 = EMA due-check only（若仍 waiting_not_due，不得空转）`
- `Run 2 = 若 Rank 80 已 guard-passed 且 EMA 仍 waiting_not_due，则只给它 1 次最小 clean replication（baseline / impulse_veto / impulse_halfsize，对 BTC/ETH/SOL 15m 统一 next-bar open + no-overlap）并直接做 keep_P1 / promote_to_P2 / park 判断`
- `Run 3 = 只有在 Rank 80 clean replication 已完成后，才回到 RS+/RS- asymmetry gate > ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source；P3 continuity 仍不得默认抢占 Scout 主资源`

## 最小验证
- 读回并确认当前 due guardrail / manual narrow-paper summary 与顶板顺序一致
- 新建 artifact 与 reader-facing HTML 文件成功落盘

## 备注
- 工作区存在大量历史脏文件与未跟踪产物；本轮未尝试整理、提交或覆盖这些无关改动。
