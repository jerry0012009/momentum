# bot3 optimization loop — global intraday TSMOM × market-characteristic admission first verdict

- 时间：2026-04-23 17:06 UTC
- 对象：`research/quant_digests/2026-04-23_1249_global-intraday-tsmom-marketchar-portability.md`
- 轮次角色：bot3 执行器
- 本轮动作：按 cycle_plan 执行该 fresh intake 的 first verdict，只补 1 个最小 decisive blocker：它在 24/7 crypto 里是否还留下独立、非单时段 lucky-run 的 after-cost continuation pocket。

## 结论
`global intraday TSMOM × market-characteristic admission` 的 fresh intake first verdict 已诚实收口 `background/P0`：现有 portability 基线已显示 `15m 30m->30m` continuation 在统一 `8bps round-trip` 下整体 `avg net≈-8.56bps/笔`；本轮再补最小 hour-of-day blocker 后，`BTC/ETH/SOL` 120d `15m` cache 的 `24` 个 UTC 小时里 **0 个小时** 保持 aggregate after-cost 为正、**0 个小时** 达到 `>=2` 个币同向为正。最好的 `15:00 UTC` 也只是 `SOL≈+0.19bps` 的单币薄 pocket，而 `ETH≈-1.49bps`、`BTC≈-7.26bps` 仍为负，说明它没有留下非单时段、非单币 lucky-run 的独立 after-cost intraday continuation alpha；当前新增价值只剩 `high-vol / liquid-hours admission map` 这种 shared gate 提示，不保留 survivor。

## 本轮最小 honesty / decisive blocker
使用现有本地 `15m` 120d cache（`BTCUSDT/ETHUSDT/SOLUSDT`）做最小 hour-of-day 切片：
- lookback：过去 `30m`（前两根 `15m`）方向
- hold：下一段 `30m`（当前与下一根 `15m`）方向
- 成本：统一 `8bps round-trip`
- 检查目标：是否存在非单一 lucky hour、且不是单币支撑的 after-cost continuation pocket

结果摘要：
- `24/24` UTC 小时的 aggregate mean net bps 全部为负
- `0/24` 小时满足 aggregate after-cost `>0`
- `0/24` 小时满足至少 `2` 个币同向 after-cost 为正
- 最佳小时为 `15:00 UTC`，aggregate `mean net≈-2.85bps`
  - `SOL≈+0.19bps`
  - `ETH≈-1.49bps`
  - `BTC≈-7.26bps`
- 最差小时为 `14:00 UTC`，aggregate `mean net≈-13.19bps`

这说明本对象当前没有通过 cycle_plan 要求的 decisive blocker：不存在足够清楚的 same-idea after-cost pocket 能支持 `keep_P1`。

## 对系统认知的改变
- 论文里的“intraday continuation 在某些 market characteristics 下更强”可以保留为 shared gate 思路；
- 但在当前 crypto `15m` portability 下，raw continuation 本体没有形成值得单独排队的 front object；
- 因此本对象应直接收口 `background/P0`，不要占用 survivor 槽位。

## 相关数据/方法
- 来源 digest：`research/quant_digests/2026-04-23_1249_global-intraday-tsmom-marketchar-portability.md`
- 基线摘要：`reports/artifacts/quant_digests/crossmarket_intraday_tsmom_probe_2026-04-23_summary.csv`
- hour-of-day blocker：本轮基于 `reports/artifacts/scout_tau_band_breakout_15m/cache/{BTCUSDT,ETHUSDT,SOLUSDT}__120d__15m.csv` 的最小脚本切片
