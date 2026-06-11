# bot3 optimization loop — 2026-04-19 10:55 UTC

## 执行小点
- target: `research/quant_digests/2026-04-19_0016_intraday-extreme-return-router-alpha.md`
- action: fresh intake first verdict
- required honesty axis: `jump/event veto + 15m 母信号到 5m child 执行`

## 本轮最小检查
围绕 digest 里 strongest-only 版本（`15m ret_8 z-score top1 + |z|>=1.5 + volume_z>0 + 2h hold`），补做了 1 条最小 honesty / execution 轴：
1. 用现成 `60d 15m` perp cache 重建母信号；
2. 用 Binance USDⓈ-M 公共 `5m` klines 做 child execution；
3. 信号在 `15m` bar close 才视为已知，入场改为 **下一根 `5m` child open**，持有 `24x5m = 2h` 后退出；
4. 额外加一个最便宜的 `jump veto` 代理：若当前信号 `15m` 单根 `abs(ret1) >= 150bps`，则跳过。

产出 artifacts：
- `reports/artifacts/quant_digests/2026-04-19_intraday_router_child_jump_honesty_summary.csv`
- `reports/artifacts/quant_digests/2026-04-19_intraday_router_child_jump_honesty_by_symbol.csv`
- `reports/artifacts/quant_digests/2026-04-19_intraday_router_child_jump_honesty_events.csv`

## 关键结果
### 1) 15m->5m child execution 后，原先 digest 的 `+8.43bps gross` 已经不再稳定保留
- `child_all`: `n=1011`, `gross_mean=+7.07bps`, `net8=-0.93bps`, `p50=-3.78bps`, `win_rate=47.4%`
- 也就是说，只要把入场从理想化 `15m` 母信号 close 进一步压成更诚实的 **下一根 `5m` child open**，在单腿 `8bps` 粗成本口径下，平均已经转成负。

### 2) 加 `jump veto` 后只能把均值勉强拉到 break-even 附近，不能回答“独立 after-cost alpha 已保住”
- `child_no_current_15m_jump_absret_ge_150bps`: `n=967`, `gross_mean=+8.21bps`, `net8=+0.21bps`, `p50=-3.78bps`, `win_rate=47.3%`
- `jump veto` 确实把最极端尾部去掉后均值拉回到约 break-even，但提升很薄，仍不足以诚实支撑一个独立 queue-facing front object。

### 3) 结果明显依赖少数大尾部与少数币，不满足“不是离群样本幻觉”
- `top5_contribution_share` 仍高达约 `2.09x`，说明总收益高度依赖极少数大赢家；
- no-jump 版本按币拆开后，`BTC/ETH/XRP/ADA` 仍为负，`BNB/LINK` 只剩薄正；
- 主要靠 `SOL/LTC/AVAX/DOGE` 拉动均值，其中 `DOGE/AVAX/LTC` 的尾部贡献尤其重。

## 结论 / verdict
`extreme recent return × strongest-only continuation router` 在补上本轮要求的唯一 honesty 轴后，**没有诚实保住“独立 after-cost 价值且不是离群样本幻觉”**：
- 15m 母信号一旦压成 5m child 执行，`8bps` 下整体已接近或低于 break-even；
- jump veto 只能把结果拉回极薄的 `+0.21bps`；
- 跨币稳定性明显不足，且收益对少数尾部事件过度集中。

因此本轮 first verdict 直接收口：**`background/P0`**，不进入 `keep_P1`。

## 对 runtime 的改变
- fresh intake 当前对象已完成 first verdict，结论为 `background/P0`
- `cycle_plan` 第 2 小点写回 `done`
- fresh intake 槽位前移到下一个仍为 pending 的具体对象：
  `research/quant_digests/2026-04-19_0224_crossmarket-intraday-tsmom-breadth-basket-alpha.md`

## 尾部执行
- 将按要求独立尝试：
  1. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  2. `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] 极端收益路由首判收口 P0" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-19_1055_intraday_extreme_return_router_freshintake_background_p0_childexec_jumpveto.md`
