# bot3 optimization loop — triangular cycle fresh intake first verdict → background / P0

- 时间：2026-04-09 00:00 UTC
- 对象：`research/quant_digests/2026-04-08_1105_triangular-cycle-cost-latency-alpha.md`
- 槽位：`Fresh intake`
- 动作：对 `spot triangular cycle gap × fee/latency/staleness gate` 做 first verdict
- 结论：`background / P0`

## 本轮为什么这么判
这条线的源码确实把同 venue 三角路径、手续费、滑点、延迟和报价陈旧度都写进了 signal gate，说明它不是空泛“支持 arbitrage”，而是一个完整的执行壳。

但按当前 policy 要问的是：它是否已经压成一个值得前排继续推进的**独立 raw alpha 主语**。这里答案是否定的：

1. **主语并不新**：`same-venue triangular parity gap -> cycle close` 本质上就是经典三角无套利平价回归，新增信息主要是把 `fee/slippage/latency/staleness` 写成工程化闸门，而不是提出新的 desk pocket。
2. **honesty blocker 仍然是 execution realism**：文档本身也承认，public klines 不够，至少要 `bookTicker/L1` 级别；而现在没有任何本地 quote-level replay、leg sequencing、残腿处理或 fillable opportunity 证据，无法说明 public quote 条件下还留有可迁移净 edge。
3. **当前增量更像 execution shell，不是新 alpha**：它更适合作为我们评估相对价值/套利策略时的 friction checklist，而不是值得占用 `Surviving candidate` 槽位的一条新 raw alpha。

## 会改变系统认知的一句话
`spot triangular cycle gap × fee/latency/staleness gate` 当前提供的是一套更诚实的三角套利执行壳，而不是一个脱离经典三角无套利框架、已证明在 public quote 条件下仍有可迁移净 edge 的新 raw alpha，因此 fresh intake 首判直接收口为 `background / P0`。

## 对 runtime 的直接影响
- 不分配 Rank（因为 verdict 未达到 `keep_P1`）
- 不进入 `Surviving candidate slot`
- 更新 `Fresh intake slot` 的 latest result 为本对象的 `background / P0` 首判
- 更新 `Background pool latest_parked`

## 交付记录
- `BOT2_BOT3_STATE.md` 已回写本轮首判
- 中文邮件已发送：`[momentum-bot3-auto] 三角套利首判收口为背景`
- 已尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，但本轮进程被宿主 `SIGKILL`；本轮 runtime 结论已生效，首页刷新未完成
