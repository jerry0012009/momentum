# RL pair dynamic scaling fresh intake -> background/P0（cost-realism 收口）

- 时间：2026-04-18 03:52 UTC
- 对象：`research/quant_digests/2026-04-18_0356_rl-pair-dynamic-scaling-statarb-alpha.md`
- 本轮动作：fresh intake first verdict
- 结论：`background/P0`

## 为什么这一步足以改变系统认知
这条线当前不值得作为新的 pairs/stat-arb front object 保留。公开 `15m` proxy 的最小 honesty 检查已经说明：所谓 `dynamic scaling / excursion-aware sizing` 目前主要只是在 deeper-excursion bucket 上放大 gross mean-reversion，但并没有留下任何一个在统一双腿 round-trip 成本后仍为正、且足够干净可承接 survivor 的 pair/cost pocket；换句话说，它更像“把 gross 和摩擦一起放大”的 sizing 故事，而不是已经能独立排队的新 front alpha。

## 本轮只做的最小 blocker 检查
按 cycle_plan 要求，只检查一个最小 honesty / execution-realism blocker：

> deeper-excursion bucket 的 gross 改善，在统一双腿成本后是否仍足以支撑独立 front-slot？

依据 digest 附带的 portability probe（`reports/artifacts/quant_digests/2026-04-18_rlpairs_dynamicscaling_probe_summary.json`）：

### ETHUSDT-BTCUSDT
- `2654` trades
- static gross: `+0.85bps/trade`
- dynamic gross: `+1.09bps/trade`
- 统一 `8bps` round-trip 后：
  - static net: `-7.15bps/trade`
  - dynamic net: `-9.52bps/trade`

解释：dynamic sizing 确实略微放大 gross，但放大后的净值更差，不支持 front-slot。

### SOLUSDT-ETHUSDT
- `2883` trades
- static gross: `-1.20bps/trade`
- dynamic gross: `-1.06bps/trade`
- 统一 `8bps` round-trip 后：
  - static net: `-9.20bps/trade`
  - dynamic net: `-12.97bps/trade`
- deeper buckets：
  - `2.5-3.0σ`: `+2.38bps`
  - `3.0σ+`: `+3.66bps`

解释：确实存在“偏得更深时 gross 更像真的”的现象，但 strongest bucket 的 gross 仍远低于统一双腿成本；没有形成可诚实承接的净 pocket。

### BNBUSDT-ETHUSDT
- `4695` trades
- static gross: `-1.02bps/trade`
- dynamic gross: `-0.98bps/trade`
- 统一 `8bps` round-trip 后：
  - static net: `-9.02bps/trade`
  - dynamic net: `-11.17bps/trade`
- deeper buckets：
  - `2.0-2.5σ`: `+1.02bps`
  - `2.5-3.0σ`: `+2.25bps`

解释：和 SOL-ETH 同样，deeper excursion 只改善 gross，不足以越过成本门槛。

## first verdict
本轮 fresh intake 直接收口 `background/P0`。

一句话结果：
> `RL pair dynamic scaling / excursion-aware sizing` 在公开 `15m` proxy 上只证明了“deeper excursion 会改善 gross”，但统一 `8bps` 双腿成本后三组 proxy pair 的 static/dynamic net 全部为负，且最强深桶 gross 也不足以留下单一干净可承接 survivor 的 pair/cost pocket，因此当前不值得作为新的 front object 保留。

## 对 runtime 的影响
- 不分配 Rank（因为没有得到 `keep_P1` 或更高 verdict）
- `Fresh intake slot` 完成当前对象的 first verdict，更新为已收口到 `background/P0`
- 本轮 `cycle_plan` 只回写 item1：`status=done`

## 尾部事项
- 首页刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步执行后收到 `signal SIGKILL`（非阻断尾部失败，未回滚 verdict/state/log）
- 邮件命令 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] RL动态配对缩放收口P0" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-18_0352_rlpair_dynamicscaling_freshintake_background_p0_costrealism.md` 已成功发送
