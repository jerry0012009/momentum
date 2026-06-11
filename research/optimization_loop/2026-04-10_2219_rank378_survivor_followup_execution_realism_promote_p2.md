# 2026-04-10 22:19 UTC — Rank 378 survivor follow-up（execution realism）=> promote_P2

## 执行小点
- cycle_plan #1
- target: `Rank 378 / retest-window impulse re-break confirmation (from Rank 60 park reframe)`
- action: 在 frozen spec 不改写前提下，补齐对象级 execution realism 证据载体（next-open fill proxy、容量切片、摩擦上限）并直接给出出口判定

## 本轮最小执行（唯一小点）
1. 使用既有 `BTC/ETH/SOL 120d 15m` cache，按 Rank 378 冻结口径重建事件：
   - breakout_short 宿主；
   - retest 后记录 `pre_retest_impulse_extreme`；
   - `N=6` 窗口内 `close` 重破（short 方向为再创新低）才确认；
   - `next-bar open` 入场，`hold=8 bars`。
2. 生成 execution-realism artifact（对象级 runtime 证据）：
   - `reports/artifacts/rank378_execution_realism/rank378_event_ledger.csv`
   - `reports/artifacts/rank378_execution_realism/rank378_trade_ledger.csv`
   - `reports/artifacts/rank378_execution_realism/rank378_capacity_friction_summary.csv`
   - `reports/artifacts/rank378_execution_realism/rank378_portfolio_summary.csv`
   - `reports/artifacts/rank378_execution_realism/rank378_execution_summary.json`
3. honesty/execution 口径：
   - 基础摩擦 `6 bps/side`；
   - 容量切片名义规模：`10k / 50k / 100k USD`；
   - impact proxy：`18 * sqrt(participation) bps/side`，并入 side cost。

## 关键结果
- 事件数：`27`
- 组合口径（`50k USD`）
  - `avg_net = +0.3469%/trade`
  - `total_net = +9.64%`
  - `asset_positive_ratio = 1.0`（BTC/ETH/SOL 三资产均值均为正）
- 扩容到 `100k USD` 后，`avg_net` 仍为正（`+0.3368%/trade`），未出现因容量/摩擦导致的净边际转负。

## 出口判定
- 本轮 survivor 唯一 follow-up 已对“诚实成交口径下是否仍成立”给出肯定答案。
- 结论：`promote_P2`（非 `drop_to_background`）。
- decisive blocker：`none`（当前未见单一 execution realism 致命阻塞）。

## 本轮 result/status
- result: `Rank 378` 在 next-open + 容量/摩擦上限的 execution-realism 口径下仍保留稳定正 net edge，survivor 唯一 follow-up 收口为 `promote_P2` 并进入 Active P2。
- status: `done`
