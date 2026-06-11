# Rank 182 / LOB LGBM quantile timing alpha intake — keep_P1

- Time: 2026-03-26 08:34 UTC
- Target: `research/quant_digests/2026-03-26_0536_lob-lgbm-quantile-timing-alpha.md`
- Verdict: `keep_P1`
- Rank assigned: `182`
- Slot transition:
  - `Fresh intake -> keep_P1`
  - `Surviving candidate slot <- Rank 182`

## What changed
`Rank 182 / lob-lgbm-quantile-timing-alpha` 首判为 `keep_P1`：值得保留的是 `LOB probability edge + rolling-quantile trigger` 这条 `1m/3m` 事件驱动微观结构 directional alpha 骨架，而不是把它降格成泛 execution timing 小组件。

## Why this clears the intake bar
1. **对象本体清楚，不是泛方法论。**
   这里保留的不是“机器学习做盘口预测”这句空话，而是完整可交易骨架：`probability edge -> smoothing -> rolling quantile trigger -> explicit cost gate`。

2. **诚实性明显强于普通 repo headline。**
   digest 已指出这条线至少显式处理了：
   - `mild` 中性区（把手续费门槛内的小波动剔掉）
   - purged walk-forward
   - lagged rolling quantile 阈值
   - 双边 fee 计入
   所以它不是只报 accuracy 的黑箱分类仓库。

3. **repo 原始绩效不惊艳，但说明“有边、易被成本吃掉”。**
   这反而适合前排 survivor：当前最应该回答的不是“headline 漂不漂亮”，而是这条边在更诚实的 desk 语境里，是否还能在 `1m/3m` event-driven pocket 留下可迁移净边。

4. **本地便宜快检给了继续做一次 follow-up 的理由。**
   digest 中的 Binance `1m` proxy 结果虽然不厚，但 ETH/BTC 都留下了弱到中等的方向影子，且 `2-bar persistence` 比单点极值更像可交易条件；这足以支持进入唯一一次 survivor follow-up，而不是直接 park。

## Why not promote to P2 yet
还不够。当前证据主要还是：
- repo 自带结果
- 文献地基
- Binance `1m` proxy 快检

缺的仍是一个**便宜但 decisive** 的 follow-up：
- 把对象严格锁定成 `1m/3m microstructure event-driven directional alpha`
- 检查 `persistence / threshold mode / cost stress` 下，是否存在能穿过保守成本的窄 pocket
- 若没有，就应诚实收口，不继续把它当泛 microstructure 平台研究

## Single best next follow-up
下一步只该做一次 survivor follow-up，回答：

> 在 `BTC/ETH/SOL` 的公开可得高频代理或秒级事件流里，`probability-edge + rolling-quantile governance` 这条骨架，在 `30s/90s/180s`、尤其 `1m/3m` 的事件触发场景下，是否能在 `fee / fee+0.5tick / fee+1tick` 下留下稳定净边；若不能，就应直接 `park_to_background`。

## Bottom line
这条线通过了 fresh intake 的最低门槛，因为它保留的是一个**可治理、可 stress、可迁移**的 raw alpha 骨架，而不是单纯“模型预测更准”。但它还没有强到直接进 `P2`；最合理位置是 `keep_P1`，并用掉那唯一一次 survivor follow-up 来决定去留。
