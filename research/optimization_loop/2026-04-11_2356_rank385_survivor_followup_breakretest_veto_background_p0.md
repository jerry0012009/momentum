# Rank 385 — survivor 唯一 follow-up：break-retest veto 收口后转入 background/P0

- 时间：2026-04-11 23:56 UTC
- 执行槽位：Surviving candidate slot
- 对象：`Rank 385 / funding spike × intact 4H corridor midpoint fade (BTC+ETH majors scoped)`
- 关联 first-verdict：`research/optimization_loop/2026-04-11_2319_rank385_funding_governor_freshintake_keep_p1.md`

## 本轮动作
按 cycle_plan 仅执行该 survivor 唯一 follow-up：围绕唯一 blocker（结构破位后误判延续）补做最小 honesty/execution 收口。

实现方式：
- 在原 funding-spike + intact-corridor 壳上新增严格 `break-retest veto`：
  1) 同一 4H 桶内出现 intrabar 越界触碰（上破/下破 corridor）；
  2) 触碰后未来 3 根交易 bar 继续沿 breakout 方向延续（超 corridor 10% 宽度）；
  3) 满足 1+2 则 veto 该笔 fade。
- 成本口径保持不变：`8 bps round-trip`。
- 复核标的：BTCUSDT、ETHUSDT；频率：5m/15m。

## 证据与产物
- artifact：`reports/artifacts/literature/rank385_survivor_break_retest_veto_2026-04-11.csv`
- 关键结果（majors 合并）：
  - `POOL_MAJOR 5m`：base `-23.01 bps/笔`；strict veto 后 `-12.18 bps/笔`（仍为负）
  - `POOL_MAJOR 15m`：base `-31.86 bps/笔`；strict veto 后 `-31.86 bps/笔`（仍为负）
- 说明：即便把“结构破位后误判延续”用更严格 veto 剔除，净边际仍未回正，无法满足 `promote_P2` 所需的最低可执行正边际门槛。

## 本轮结论（改变系统认知）
`Rank 385` 在补齐 break-retest honesty veto 后，majors 合并口径的成本后净边际仍系统性为负，故 survivor 唯一 follow-up 结论为 **background/P0**（不进入 P2）。

## runtime 写回
- Surviving candidate slot：本对象收口完成并释放（`current_target = none`）。
- Background pool：新增 latest parked = `Rank 385`（原因：break-retest veto 后仍无可执行净边际）。
- cycle_plan[1]：写回 `done`。
