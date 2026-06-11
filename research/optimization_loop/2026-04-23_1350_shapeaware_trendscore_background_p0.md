# shape-aware trend score fresh intake -> background/P0

- 时间：2026-04-23 13:50 UTC
- 对象：`research/quant_digests/2026-04-23_0432_shapeaware-trendscore-portability-verdict.md`
- 执行动作：fresh intake first verdict（只补 1 个最小 decisive blocker：它是否留下可独立排队的 short-cycle after-cost trend alpha，而不是只剩 shared scoring / portability 提示）
- 结论：`shape-aware trend score` 完成 fresh intake first verdict 并收口 `background/P0`。

## 本轮最小证据
直接复核该 digest 自带的 public-data probe artifact：
- `reports/artifacts/quant_digests/2026-04-23_shapeaware-trend_proxy_grid.csv`
- `reports/artifacts/quant_digests/2026-04-23_shapeaware-trendscore_vs_plainmom_probe.csv`

关键读数：
- `15m`, `lookback=8`, `hold=1`, `long_top1`：shape `-0.10 bps/trade`，plain momentum `-0.13 bps/trade`
- `15m`, `lookback=8`, `hold=2`, `long_top1`：shape `-0.38 bps/trade`，plain momentum `-0.43 bps/trade`
- `15m`, `lookback=8`, `hold=1`, `ls_topbot1`：shape `-0.63 bps/trade`，plain momentum `-0.68 bps/trade`
- `15m`, `lookback=4`, `hold=1`, `short_bot1`：shape `-0.85 bps/trade`，plain momentum `-0.92 bps/trade`

## 为什么这一步足够收口
这轮要求回答的是：它有没有留下“可独立排队的 short-cycle after-cost trend alpha”。

当前最强证据只说明：
1. `R²` shape proxy 相比裸 momentum 有零点几 bps 的微弱改善；
2. 但各最优切口本身仍是负的 gross bps；
3. 因此它没有展示出一个非单月、非单币 lucky-run 的独立 after-cost pocket；
4. 更合理的角色仍是已有 trend / momentum / breakout 家族的 shared trend-quality filter，而不是独立 raw alpha。

## runtime verdict
`shape-aware trend score` 已完成 fresh intake first verdict 并收口 `background/P0`：当前 Binance majors `15m` portability probe 里，shape proxy 仅表现为“比 plain momentum 少亏一点”，例如 `lookback=8` 下 `top1 long` 约 `-0.10~-0.38 bps/trade`、`top1-bottom1` 约 `-0.63 bps/trade`，仍未留下任何可独立排队的 short-cycle after-cost trend pocket；当前只保留为 trend-quality filter / scoring 提示，不占用 survivor。

## tail step status
- `publish_homepage_index.sh`：异步执行最终 `SIGKILL` 失败（非阻断尾部失败，不回滚本轮结论/state/log）。
- 中文邮件摘要：已成功发送。
