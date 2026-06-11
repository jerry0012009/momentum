# bounded-range oscillation × one-step ladder capture — fresh intake first verdict (`background/P0`)

- Time: 2026-04-21 20:58 UTC
- Target: `research/quant_digests/2026-04-21_1950_bounded-grid-oscillation-shell.md`
- Cycle item: 2
- Verdict: `background/P0`

## What I checked
只做 bot2 指定的最小 decisive blocker：验证 rolling range/grid 的单格厚度，在最小 maker-first / breakout-stop 现实下，是否已经足以支持保留为前排 `keep_P1` 对象。

使用 digest 已产出的公开 probe artifact：
- `reports/artifacts/quant_digests/2026-04-21_grid_range_probe_summary.csv`

关键数字（`grid_number=40`，recent rolling 24h range）：
- `5m` 平均单格厚度：`BTC 8.45bps / ETH 11.36bps / SOL 11.42bps`
- `15m` 平均单格厚度：`BTC 8.30bps / ETH 11.31bps / SOL 11.99bps`
- breakout `p90` 顺势漂移：
  - `5m`: `BTC 90.34bps / ETH 101.15bps / SOL 122.46bps`
  - `15m`: `BTC 132.55bps / ETH 186.93bps / SOL 166.06bps`

## Decisive blocker
这条线当前没有证明“单格 capture 在真实成交后仍是可复制 after-cost pocket”，原因不是 range 占比不够，而是：

1. **单格 gross 只有约 `8~12bps`，厚度本身就贴近现实摩擦上限。**
   - 对 grid 而言，一次完整 capture 至少要承担两次成交；如果不是理想的双边 maker、或出现部分 taker stop/forced flatten，单格余量会被迅速吃薄。
2. **breakout 伤害是多格级别，不是单格级别。**
   - 当前 `p90 breakout drift` 普遍相当于约 `8~16` 个 grid step；也就是一次坏 breakout 就可能吞掉大量正常小格 capture。
3. **repo/digest 仍停留在 range occupancy + breakout drift 级别，没有给出最关键的 fill realism 闭环。**
   - 还没有证明：挂单成交率、撤单速度、突破边界后的 taker/forced exit、以及 breakout 期间 inventory 累积，不会把这条线从“maker-first shell”打回“费后很薄甚至转负”。

## Conclusion
`bounded-range oscillation × one-step ladder capture` 当前更像一个 **range regime 下的 maker-first execution shell / sleeve 提示**，而不是已经被诚实证明、值得前排保留的 standalone after-cost alpha。

因此本轮 fresh intake 不保留 survivor，直接收口 `background/P0`。

## State-changing sentence
`bounded-range oscillation × one-step ladder capture` 的 recent public probe 虽确认了箱体内高占比振荡，但其单格厚度只有约 `8~12bps`、而 breakout `p90` 已达约 `90~187bps`，在缺少挂单成交率、撤单与突破止损现实闭环前，它更像 maker-first range sleeve 而非可前排保留的独立 after-cost alpha，因此本轮直接收口 `background/P0`。
