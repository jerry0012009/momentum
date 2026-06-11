# bot3 optimization log — auction-profile value-area re-entry × LVN traverse shell

- Time: 2026-04-18 03:22 UTC
- Target: `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
- Cycle step: `fresh intake first-verdict`
- Verdict: `background/P0`

## What was checked
按 `cycle_plan` 只补 1 个最小 honesty / execution realism blocker：检查这条线当前能否在公开可复算口径下，凭 repo 里现成的 bar-volume profile proxy 诚实支撑独立 front-slot，而不是只是分箱/会话切法叙事。

## Key finding
当前源码中的 `POC/VA/LVN` 建立方式并不是逐笔 volume-at-price，而是把每根 OHLCV bar 的成交量均匀分摊到 bar 覆盖价格区间。对这条策略壳来说，这不是一个可忽略的小近似：

1. `VA re-entry` 与 `LVN traverse` 的核心定义都直接依赖 profile 形状；
2. bar-based uniform binning 会把长实体 bar 内并不存在的成交密度“抹平”，从而重写 `POC/VA/LVN` 位置；
3. crypto 24/7 下 session 切法本就高度敏感，而当前公开证据还没有证明 edge 能跨 `UTC daily / 8h / rolling` profile 保持；
4. 因此现阶段可继承的主要是“auction structure 研究母板”叙事，不是已经足以独立排队的可诚实 raw alpha 对象。

## Decision
`auction-profile value-area re-entry × LVN traverse shell` 在最小 bar-profile proxy / execution-realism honesty 检查下未能诚实保住 front-slot：源码里的 `POC/VA/LVN` 目前建立在 OHLCV bar-volume 均匀分箱 proxy 上，当前又缺少能证明 edge 不是 session/binning 幻觉的更细成交分布复核，因此本轮 fresh intake first verdict 直接收口 `background/P0`。
