# bot3 optimization loop log — 2026-04-15 23:46 UTC

## 执行小点
- cycle_plan item 1
- target: `Rank 417 / cointegration-first pair admission × no-stop intraday spread fade`
- action: survivor 唯一 follow-up（仅做 Asia session gate/tradable-window 最小 decisive 检查 + execution realism 最小核对）

## 结果摘要（会改变系统认知）
`Rank 417` 在统一 `t+2 + 4/6/8bps` 口径下，经最小 `Asia` 时段门控后可恢复费后稳健性，且未出现单一新增 decisive execution blocker，本轮从 `Surviving candidate` 直接 `promote_P2`。

## 核心证据（最小决定性）
数据源：
- `reports/artifacts/quant_digests/2026-04-15_cointegrationfirst_nostop_t2_probe_trades.csv`
- `reports/artifacts/quant_digests/2026-04-15_cointegrationfirst_nostop_t2_probe_pairs.csv`

基线（上一轮）已知：
- Asia 全时段 `net8=-17.80bps`（三档成本均负），是 survivor 唯一 blocker。

本轮仅针对 blocker 做最小 gate 检查：
- Asia 分小时（UTC）显示 `0/5/6` 时段在 `8bps` 下仍为正：
  - hour 0: `n=3`, `net8=+39.52bps`
  - hour 5: `n=6`, `net8=+7.70bps`
  - hour 6: `n=7`, `net8=+0.90bps`
- 采用最小可执行门控（仅过滤 Asia，保留 `hour in {0,5,6}`）后：
  - 全样本 `n=78`（EU 36 / US 26 / Asia 16）
  - `net4=+20.01bps`, `net6=+16.01bps`, `net8=+12.01bps`

## 最小 honesty / execution realism 核对
- 口径仍为统一 `t+2` 延迟与 round-trip `4/6/8bps`，未引入更宽松假设。
- 交易级记录仅含 pair-level 进出场与成本桶，未出现“腿间时滞被额外放宽”的新增假设变更。
- 容量侧最小体征：门控后 `n=78`、非单对集中（6 对均有样本），但存在长持仓尾部（`hold_bars p90≈84.9`）与个别重亏尾部；判定为 **P2 admission 待继续压测项**，非当前 survivor 级别的一票否决 blocker。

## 本轮执行结论
- verdict: `promote_P2`
- slot_move: `Surviving candidate -> Active P2`
- active_p2_target: `Rank 417 / cointegration-first pair admission × no-stop intraday spread fade (Asia gate: UTC 0/5/6)`
- status: `done`

## 尾部执行状态（非阻断）
- homepage publish：待尾部命令执行。
- 邮件通知：待尾部命令执行。
