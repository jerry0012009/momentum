# 2026-03-25 23:40 UTC — Rank 171 survivor 唯一 follow-up（friction / execution realism 收口）

- 执行轮次：bot3 auto 13m
- 对象：`Rank 171 / volume-ranked theme leader-follower spread`
- 本轮动作：按 policy 对 survivor 做唯一一次 decisive follow-up；只回答这条 `volume-ranked leaders → followers catch-up spread` 在真实 friction / execution realism 下，是否仍保留值得进入 `P2` 的可复制净边

## 结论
**Rank 171 本轮不升 `P2`，并退出前排回到 background pool。当前证据只支持把它保留为一个 `1m/3m/5m` 题材内 lead-follower relative-value 背景假设；在已看到的最小诚实口径下，毛边仍主要停留在单一 gaming/metaverse proxy，且只有约 `+1.515 ~ +1.660 bps gross`（`5m`、leader shock top-30%、持有 1~3 bars）的 follower-minus-leader spread。这个厚度不足以诚实覆盖真实双腿执行摩擦，因此还不够形成值得升入 `P2` 的可复制净边。**

## 本轮为什么可以直接收口
前一轮 intake 已经把这条线的核心翻译清楚：真正值得保留的不是论文原文里的日频 metaverse 题材故事，而是 **题材篮子内按 rolling quote volume 分层的 `leaders → followers catch-up spread`**。因此本轮唯一需要补的，不是再换一个措辞，而是问一个更硬的问题：

> 这点毛边，在真实 friction / execution realism 下还能活吗？

现有 artifact 已足够回答这个问题。

## 证据怎么读
来自 `reports/artifacts/quant_digests/theme-leadlag_20260325_2156/summary.csv` 的最关键读数：

- 样本仍只是一组 **gaming/metaverse proxy**：`MANA/SAND/AXS/ENJ/GALA/IMX/APE`
- ranking 口径：rolling `1d` quote volume，`top-3 leaders` vs `bottom-3 followers`
- 交易口径：leader 当根冲击后，从下一根开始做 `followers - leaders` spread
- 最好看的 bucket 是 `5m + top30 shock`
  - hold 1 bar：`+1.515 bps`
  - hold 2 bars：`+1.606 bps`
  - hold 3 bars：`+1.660 bps`
- 但到了 `15m + top30 shock`，同模板已经转负：
  - hold 1/2/3 bars：`-0.418 / -1.046 / -1.509 bps`

翻成人话：**alpha 本体可能存在，但当前“活着”的区域很窄，只剩单题材、短持有、薄毛边的 pocket。**

## 为什么这还不够升 P2
### 1) 毛边厚度不足以诚实穿过执行摩擦
这条线是双腿 relative-value spread，不是单腿方向交易。即使不假设粗暴的 taker-taker，现实里也至少要面对：
- 双腿建仓与平仓的盘口价差/冲击
- leader/follower 不同步成交造成的 slippage
- 低量 follower 腿在冲击后更容易吃到差价
- 题材币在真正放量时，quote volume 分层会和可成交深度一起快速漂移

而我们当前看到的最好 gross 只在 **`1.5~1.7 bps` 级别**。这意味着它对执行的要求不是“优化一下更好”，而是 **必须非常理想的撮合与队列位置才能不被吃光**。在没有更细粒度成交级证据前，把它升进 `P2` 会把一个“薄 pocket”误写成“已有可复制净边”。

### 2) 现有证据仍停留在单一 proxy，不足以证明它是可扩展 family
policy 要求 survivor follow-up 给出诚实结论，而不是继续开放式拖延。当前这条线最像是：
- 某个 gaming/metaverse 篮子里存在 volume-ranked lead-lag 现象；
- 但还没有证据证明它能稳定迁移到其他 narrative basket；
- 因此还不能把 edge 归因为“可扩展的题材内 lead-follower family”，更像一个 **单题材 pocket**。

### 3) `15m` 已经明显不给面子，说明可部署窗口更窄
同模板到了 `15m` 全线转负，说明它不是一个宽容的中频结构，而更像非常短、非常薄的快 alpha。对这类结构，execution realism 不是附属检查，而是 admission 前提。既然这一步还没过，就不该进入 `P2`。

## 为什么不是 keep_P1 再拖一轮
policy 已经规定 survivor 只有这 **唯一一次** decisive follow-up。前一轮已完成 fresh intake 首判；本轮必须收口，不能再给第二次 survivor follow-up。既然现在没有足够证据把它诚实升成 `P2`，默认就应退出前排，而不是继续以“以后再测 cost / 再扩 basket”为理由留在主资源位。

## 为什么也不是 fatal flaw
这条线并非被完全证伪：
- `5m` top-shock bucket 的 spread 确实为正；
- 论文给的 economic story（题材内信息扩散速度差）也合理；
- deployable skeleton 已经清楚。

所以更准确的归类是：**值得留档，但当前不够进前排。**

## 对 runtime 的直接影响
- `Surviving candidate slot` 清空：`Rank 171` 用完唯一 follow-up，退出前排
- `Active P2 slot` 继续保持 `none`
- `Fresh intake slot` 仍为 `idle / none`，等待 bot2 下一轮按现有条件把资源切到新的 fresh intake
- `Background pool` 新增一条正式收口：`Rank 171` 保留为题材内 `leaders → followers catch-up spread` 的快频背景假设，但当前不升 `P2`

## 一句话写回系统认知
`Rank 171 / volume-ranked theme leader-follower spread` 已完成 survivor 唯一 follow-up：现有正毛边只停留在单一 gaming/metaverse proxy 的 `5m` top-shock pocket，厚度约 `1.5~1.7 bps gross`，不足以诚实覆盖真实双腿执行摩擦，因此不升 `P2`，回到 background pool。
