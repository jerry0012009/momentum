# Rank pending fresh intake：bull-regime BTC dip -> alt basket rebound 诚实收口 background/P0

- 时间：2026-04-25 16:01 UTC
- 对象：`research/quant_digests/2026-04-25_1450_bullregime-btcdip-altbasket-realitycheck.md`
- 槽位：Fresh intake slot
- 执行动作：按 `cycle_plan` 对 `bull-regime BTC dip -> alt basket rebound` 做 first verdict；不扩展成第二个 pending 小点，只依据现有 repo audit + public portability probe 判断它在统一成本口径下是否仍保留独立可交易 pocket。

## 结论
`bull-regime BTC dip -> alt basket rebound` 已诚实收口 `background/P0`：公开可复现实验已经把这条 raw alpha 在统一成本口径下打成 after-cost 不成立，当前没有足够证据支持 `keep_P1`。

## 改变系统认知的一句话
这条 bull-regime lead-lag 分支不是“还差一点验证”，而是现成 portability 证据已显示 `60d/180d` 两个窗口在 `8 bps` roundtrip 下 event-level mean net 均明显为负，因此默认不应继续占用前排 fresh/survivor 资源。

## 本轮采用的最小 decisive blocker
唯一需要回答的问题是：是否已经存在一个具体 asset basket / execution 口径，在统一成本后仍保留明确净 edge，足以让它成为 `keep_P1`？

答案：**没有。**

## 证据摘录
来自目标 digest 的最小可执行证据已足够形成 first verdict：

- repo bull 分支规则清晰：`BTC 5m dip >= 0.5%`、`BTC 7d >= 0`、`BTC 3d >= 0`，触发后 long alt basket，默认 hold `30m`，UTC `7~11` 不做。
- public Binance USDⓈ-M portability probe（non-overlap event backtest，粗扣 `8 bps` roundtrip）结果：
  - `60d` / 10-asset：事件数 `30`，event mean net `-13.05 bps`，median `-17.84 bps`，hit-rate `33.3%`
  - `180d` / 6-asset：事件数 `46`，event mean net `-14.10 bps`，median `-14.81 bps`，hit-rate `41.3%`
  - 两个窗口里“最不差”的 `DOGE` 也仍为负（约 `-2.87 bps` / `-8.30 bps`）
- 该 digest 已把最关键问题回答完：这不是单纯“执行壳还没补”，而是 raw alpha 在当前 public portability + 粗成本口径下尚未穿过生存线。

## 为什么不是 keep_P1
`keep_P1` 至少要求存在一个仍可保留的净 spread / return pocket，哪怕只在较窄 basket 或较具体 execution 设定里成立；但当前材料只支持：

1. 想法与策略壳完整；
2. public 代理口径可复现；
3. after-cost 结果持续为负。

因此它更像一个**已被现实检验淘汰的 raw alpha 分支**，而不是值得锁定 survivor 资源的候选。

## 运行态处置
- Fresh intake verdict：`background/P0`
- 不分配 Rank（未达到 `keep_P1`）
- 不进入 survivor slot
- 不提升到 `P2`

## 备注
若未来要 reopen，只能以用户明确要求或出现全新 execution / basket 证据为前提；当前自动轮次不应继续沿同一 fresh-intake 方向重复补检。 
