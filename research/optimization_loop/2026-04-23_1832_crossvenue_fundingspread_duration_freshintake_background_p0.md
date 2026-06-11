# cross-venue funding spread × duration-before-reversal — fresh intake first verdict

- 时间：2026-04-23 18:32 UTC
- 对象：`research/quant_digests/2026-04-23_1806_crossvenue-fundingspread-duration-alpha.md`
- 轮次角色：bot3 executor
- 结论：`background/P0`

## 本轮执行的小点
对 `cross-venue funding spread × duration-before-reversal` 做 fresh intake first verdict，只补 1 个最小 decisive blocker：它是否留下可独立排队的 after-cost spread-duration pocket，而不是只剩 funding carry / execution-hazard 提示。

## 使用的最小证据
1. 现成 portability 复核：`reports/artifacts/quant_digests/funding_spread_threshold_portability_probe_2026-04-16_summary.json`
   - `BTC/ETH/SOL`，`15m`，160d，`z_entry=2.0`，`funding_min_bps=0.5`，`hold_bars_max=96`，统一 `34bps` roundtrip。
   - 结果：
     - BTC：`61` 笔，`avg_net_bps=-32.81`
     - ETH：`56` 笔，`avg_net_bps=-32.64`
     - SOL：`28` 笔，`avg_net_bps=-31.54`
     - 组合：`145` 笔，`avg_net_bps=-32.33`，`win_rate=0`
   - 同时平均 funding 贡献只有约 `0.036~0.062bps/笔`，远低于统一双腿摩擦。
2. 更诚实的 cross-venue/t+2/queue 检查：`reports/artifacts/quant_digests/2026-04-16_crossvenue_perpperp_hysteresis_t2_session_cost_summary.json`
   - baseline `t+2` 下可见样本已经只剩 `SOL 1` 笔，gross 约 `+1.20bps`；
   - 再加 `t+3 + queue realism` 后 gross 变成约 `-1.01bps`；
   - `4/6/8bps` 成本梯度下 net 全负，且完全不具备非单 venue-pair、非单 lucky-run 的可迁移性。
3. live sanity snapshot：`reports/artifacts/quant_digests/20260330_perp_perp_funding_diff_netev/live_sanity_snapshot.json`
   - BTC/ETH 跨 Binance/Bybit/OKX 的当下 richest-vs-cheapest funding spread 只有约 `0.16~0.93bps/8h`；
   - 对应 break-even funding diff 需要约 `23.5~27.5bps/8h`；
   - 即使先不谈 reversal hazard，公开可见 spread 本身离覆盖双腿交易/滑点/延迟/库存风险的门槛也很远。

## first verdict reasoning
这条线的 digest 说得对：真正该看的不是“spread 是否存在”，而是“spread 能否维持足够久而不被 reversal 吃掉”。但当前 desk 已有的最小公开复核表明，问题甚至更早就已经出现：

- spread-threshold 版本在 `BTC/ETH/SOL` 上已经是稳定费后负值；
- 再补 duration / hysteresis / queue realism 后，样本进一步塌缩到几乎不可交易；
- live snapshot 还显示常态 funding diff 离 break-even 很远，不像还有一个独立的 spread-duration after-cost pocket 只是等待更细调参被挖出来。

因此，本对象没有留下“至少一个非单 venue-pair、非单 spread-age lucky-run 的 after-cost carry+convergence pocket”。它当前更像两类 shared 提示：

1. `funding spread / duration-before-reversal` 适合作为已有 funding/carry 壳的 admission gate；
2. `leader venue + reversal hazard + queue realism` 适合作为 cross-venue 执行风险提示。

## 会改变系统认知的话
`cross-venue funding spread × duration-before-reversal` 已完成 fresh intake first verdict 并收口 `background/P0`：现成 portability 与更诚实的 `t+2/t+3+queue` 复核都表明，跨 venue funding spread 在 `BTC/ETH/SOL` 上要么稳定费后为负（组合 `145` 笔 `avg_net≈-32.33bps/笔`），要么样本塌缩到仅 `SOL 1` 笔且 queue realism 后 gross 反转为负；同时 live richest-vs-cheapest funding diff 常态仅 `0.16~0.93bps/8h`，远低于约 `23.5~27.5bps/8h` 的 break-even 门槛，因此它没有留下可独立排队的 after-cost spread-duration pocket，只保留为 funding carry / cross-venue execution-hazard admission 提示。
