# 2026-03-30 08:30 UTC — Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing：fresh intake -> keep_P1

- 时间：2026-03-30 08:30 UTC
- 对象：`Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing`
- 轮次类型：bot3 auto optimization
- 结论：`fresh intake passed -> keep_P1`

## 这轮做了什么
按当前 `cycle_plan` 只执行最前的 pending 小点：判断 `leader-basket → selected-follower spread catch-up / network follower routing` 是否构成一个**独立前排对象**，而不是把旧的 cross-crypto lead-lag / alt basket catch-up 家族换个 network 说法再写一遍。

本轮只回答三件事：
1. 主语是否已经被锁死为 **`leader basket 先动 + selected follower 明显落后时，下一根做 spread catch-up`**；
2. 新信息是否真的来自 **pair-specific routing**，而不是“所有 alt 都会跟”的泛叙事；
3. 它与当前库里的近邻对象相比，是否保留了足够清楚的独立对象边界，值得进入前排做一次 survivor follow-up。

## 最小证据
### 1) 源 digest 已把 alpha 本体写清楚
`research/quant_digests/2026-03-30_0808_network-leaderbasket-follower-routing-alpha.md` 已经把对象边界写成：
- leaders 固定在高影响 `BTC/ETH/LTC` 篮子；
- 不是追整个 alt basket，而是只在 **selected follower** 明显落后时做 `long follower / short leader basket` 的相对回补；
- stablecoin synergy 只是后续可选的 regime/gate，不是 alpha 本体。

也就是说，这条线的主语不是“network 结构分析”，而是很具体的 **pair-routed spread catch-up**。

### 2) 本地快检留下的是 pair pocket，不是无差别 basket
同一份 digest 的本地 `15m` pocket scan 已经给出：
- equal-weight follower basket：约 `-0.04 bps/trade`，几乎没边；
- 但 pair-specific pocket 仍存在：
  - `LINKUSDT`：约 `+7.92 bps/trade`
  - `ADAUSDT`：约 `+3.00 bps/trade`
  - `XRPUSDT`：约 `+1.73 bps/trade`

这点很关键：它直接把对象从“泛 alt basket catch-up”收窄成了“leader basket -> selected follower routing map”。

### 3) 与现有近邻对象相比，它有独立边界
我额外对照了库内近邻：
- `common-shock lag ranking` 更像 **大 common shock 下的 laggard ranking**；
- `volume-ranked theme leader-follower spread` 更像 **theme/volume 主导的 basket-follower 叙事**；
- `btc-alt liquidity-ranked delay` 更像 **低流动性 laggard ranking**；
- `BTC 盘口压力 -> ETH 补动` / `BTC->ADA 57s lag` 是 **更短时钟、更单对单、更偏 microstructure / tick** 的 lead-lag。

而这条线新增的是：
- **慢更新的 network routing map**（论文里相邻周 pairwise network 相似度常 `> 0.9`）；
- **leader basket 固定、follower 按路由精选**；
- **对象目标是 spread catch-up，不是全市场跟涨**。

这足以把它和已有的“泛 BTC 带 alt”或“shock lag ranking”分开。

## 本轮判断
这条线不该判成 `background/P0`。原因不是它已经足够升 `P2`，而是：
1. **对象边界已经清楚。** leader 选择、selected-follower routing、spread 触发、下一根 catch-up 持有和最小 honest cost 口径都已经有了可执行雏形。
2. **新增信息确实来自 routing，而不是旧叙事重述。** equal-weight basket 没边、但 pair pocket 存在，这就是这轮最关键的新信息。
3. **还没完成真正 admission。** 当前证据仍是 spot `15m` pocket scan，尚未进入 perp 可执行口径、rolling walk-forward routing 稳定性、after-cost 验证，因此还不该直接升 `P2`。

因此，本轮最诚实的 first verdict 是：**给正式 Rank，保留为 `P1 / surviving candidate`，只允许 1 次 follow-up 去回答“rolling follower routing + perp/after-cost”下是否还留有可执行 pocket。**

## 会改变系统认知的话
`Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing` 不是旧 cross-crypto lead-lag 的泛重述：它把 alpha 主语收窄为 `leader basket 先动 + pair-specific follower routing 的下一根 spread catch-up`，且当前证据显示 edge 来自 selected-follower pockets 而非 equal-weight alt basket，因此本轮给 `keep_P1`，进入唯一 survivor follow-up。

## 产物
- 源记录：`research/quant_digests/2026-03-30_0808_network-leaderbasket-follower-routing-alpha.md`
- 本轮日志：`research/optimization_loop/2026-03-30_0830_rank249_network_leaderbasket_follower_routing_intake_keep_p1.md`
