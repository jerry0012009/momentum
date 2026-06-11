# volume-weighted XS momentum × AVR repeated-hit fresh intake -> background/P0

- 时间：2026-04-21 05:12 UTC
- 对象：`volume-weighted cross-sectional momentum × abnormal-volume repeat gate`
- 类型：fresh intake first verdict
- 结论：`background/P0`

## 本轮执行的小点
按 `cycle_plan` 第 1 项，对 `research/quant_digests/2026-04-21_0449_volumeweighted-xs-momentum-avr-router.md` 做 fresh intake first verdict；只补 1 个最小 decisive blocker：在 `15m top1 strongest-only`、统一 `8bps`、recent slice 与 symbol/day concentration 下，确认 AVR repeated-hit router 是否仍保留不是单币/少数好日子驱动的 after-cost continuation pocket。

## 读取到的现成证据
- digest：`research/quant_digests/2026-04-21_0449_volumeweighted-xs-momentum-avr-router.md`
- 历史 portability 基线：`research/quant_digests/2026-03-25_0220_volume-weighted-xs-momentum-flow-confirmation.md`
- 历史 artifact：`reports/artifacts/quant_digests/volume_weighted_xs_momentum_probe_20260325/summary.json`

## 最小 honesty / decisive blocker 复核
我按 digest 中给出的同一骨架做了最小 recent 复算：
- universe：`BTC/ETH/SOL/XRP/BNB/DOGE/ADA/LINK/SUI/AVAX`
- 频率：`15m`
- score：`sqrt(3) * (mu3 - mu60) / sigma60 * (qvol3 / qvol60)`
- gate：最近 `5` 根里 `AVR > 2` 至少 `3` 次
- entry：`next bar open proxy`（用 next bar close 近似最小 bar-close 后入场）
- horizon：`next 2/4/8 bars`
- cost：统一 round-trip `8bps`

### 1) 只有 hold8 勉强为正，短一点立即明显费后为负
- `n=249`
- `next 2 bars`：`gross≈+0.08bps`，`net8≈-7.92bps`
- `next 4 bars`：`gross≈+1.99bps`，`net8≈-6.01bps`
- `next 8 bars`：`gross≈+8.52bps`，`net8≈+0.52bps`

这说明它不是一个“child-entry 后立刻可承接”的厚 continuation pocket；即便放宽到 `8 bars`，费后也只剩极薄余量。

### 2) 表面为正的 hold8 由少数大赢家拉动，不是广谱稳定 pocket
`next 8 bars` 在统一 `8bps` 后：
- `mean net8≈+0.52bps`
- `median net8≈-19.63bps`
- `win rate≈38.15%`

均值为正，但中位数深负、胜率不到四成，说明正边际并不是靠稳定小盈利累积出来，而是典型尾部事件拉动。

### 3) symbol concentration 明显：只有少数币真正赚钱，majors 多数为负
按 `next 8 bars net8` 聚合：
- 正贡献几乎全部来自 `AVAX (+1467.62bps)` 与 `SOL (+973.08bps)`；`SUI/ADA` 只有小量补充
- `BTC (-532.21bps)`、`ETH (-206.23bps)`、`XRP (-281.11bps)`、`DOGE (-267.15bps)`、`BNB (-1210.34bps)` 全为负

也就是说，这条线当前并没有保住“非单一 symbol / 非少数 alt pocket”的 front-slot 质量，更像少数高弹性 alt 的阶段性 continuation router。

### 4) day concentration 更严重：去掉最好的少数日后立刻大幅转负
按交易日聚合 `next 8 bars net8`：
- `top1 day share≈2822.3%`
- `top3 day share≈3315.5%`
- 去掉 top1 day 后：剩余 `216` 笔，`avg net8≈-16.40bps`
- 去掉 top2 day 后：剩余 `194` 笔，`avg net8≈-20.52bps`
- 去掉 top3 day 后：剩余 `181` 笔，`avg net8≈-23.11bps`

这已经满足“少数好日子驱动”的 decisive blocker：表面正均值并不来自可复制的常态 edge，而是由极少数异常日一次性抬起。

## verdict
`volume-weighted cross-sectional momentum × abnormal-volume repeat gate` 的 fresh intake first verdict 已诚实收口：在 `15m top1 strongest-only`、统一 `8bps` 与 recent slice 下，`next 2/4 bars` 明显费后为负，`next 8 bars` 也只剩 `mean net8≈+0.52bps` 的极薄余量且 `median net8≈-19.63bps`、`win rate≈38.15%`；正边际主要由 `AVAX/SOL` 少数高弹性币和极少数最好交易日拉动，去掉 top1~3 days 后剩余样本平均 `net8` 立刻转为约 `-16.40/-20.52/-23.11bps`，未通过“不是单币/少数好日子 lucky run”的 decisive blocker，因此本轮直接收口 `background/P0`。
