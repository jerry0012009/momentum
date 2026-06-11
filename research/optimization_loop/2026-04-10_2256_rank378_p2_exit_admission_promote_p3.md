# 2026-04-10 22:56 UTC — Rank 378 Active P2 admission 出口决策 => promote_P3

## 执行小点
- cycle_plan #1
- target: `Rank 378 / retest-window impulse re-break confirmation (from Rank 60 park reframe)`
- action: 作为 Active P2 执行 admission 出口决策轮；在既有 execution-realism artifact 基础上补齐 effectiveness / cross-asset / time / parameter 四轴，并做最小 honesty 子检查（re-break delayed confirmation 与 next-open 可成交一致性）

## 本轮执行（仅此一项）
1. 复核既有对象级 artifact：
   - `reports/artifacts/rank378_execution_realism/rank378_event_ledger.csv`
   - `reports/artifacts/rank378_execution_realism/rank378_trade_ledger.csv`
   - `reports/artifacts/rank378_execution_realism/rank378_capacity_friction_summary.csv`
   - `reports/artifacts/rank378_execution_realism/rank378_portfolio_summary.csv`
2. 生成 admission 出口汇总：
   - `reports/artifacts/rank378_execution_realism/rank378_p2_admission_exit_summary.json`

## admission 四轴结论（50k 口径为主）
- effectiveness：`avg_net = +0.3469%/trade`，`win_rate = 48.15%`，净边际为正且并非单次异常值驱动。
- cross-asset stability：
  - BTC: `+0.2485%/trade`
  - ETH: `+0.3902%/trade`
  - SOL: `+0.4346%/trade`
  三资产均值均为正，无单资产塌陷。
- time stability（按月）：
  - 2025-11: `+1.4429%`
  - 2025-12: `-0.0542%`
  - 2026-01: `-0.0222%`
  - 2026-02: `+0.4277%`
  - 2026-03: `+0.2403%`
  月度有回撤月份，但不存在持续性失效带；总体仍维持正期望。
- parameter stability（容量/摩擦）：
  - 10k: `+0.3605%/trade`
  - 50k: `+0.3469%/trade`
  - 100k: `+0.3368%/trade`
  扩容后仅温和衰减，未出现净边际转负。

## honesty 子检查（最小）
- delayed confirmation 与 next-open 一致性：
  - `entry_ts - confirm_ts` 恒为 `15 分钟`（无 confirm 后同 bar 入场、无 lookahead 塌口径）
  - delayed-confirm 子集（12 笔）`avg_net = +0.6616%`
  - immediate-confirm 子集（15 笔）`avg_net = +0.0952%`
- 结论：未发现“仅靠延迟确认定义造成不可成交假优势”的单一 decisive honesty blocker。

## 出口决策
- `promote_P3`。
- 原因：Active P2 admission 所需四轴与最小 honesty 检查均已完成，且未出现单一致命 execution/honesty 阻塞；按 policy 直接升级进入 `Paper launch queue`，不得继续开放式 keep_P2。

## 本轮 result/status
- result: `Rank 378` 在 Active P2 admission 出口轮补齐 effectiveness/cross-asset/time/parameter + 最小 honesty 检查后仍保持正净边际且无单一致命阻塞，已从 `Active P2` 直接 `promote_P3` 进入 `Paper launch queue`。
- status: `done`
