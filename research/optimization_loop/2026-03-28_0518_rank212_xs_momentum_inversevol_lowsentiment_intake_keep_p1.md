# Rank 212 / XS momentum × inverse-vol × low-sentiment gate intake keep P1

- Time: 2026-03-28 05:18 UTC
- Target: `research/quant_digests/2026-03-28_0521_xs-momentum-inversevol-lowsentiment-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Rank: `212`

## What changed
这条对象留下来的不是“月频论文里再讲一次 crypto momentum 有效”，而是一条能被 desk 化拆开的明确骨架：**`XS momentum` 是 raw alpha，本体上可接 `inverse-vol` sizing，`low-sentiment` 只是慢变量 gate**。对当前 desk 最值钱的部分是 liquid majors 上的 short-cycle 横截面 long-short，而不是 Google Trends 本身。

## Why it is not P2 yet
1. 当前 transfer check 只有最近约 33 天、单 venue（OKX spot）、13 个 liquid majors、`15m -> 1h` 的最小证据，样本还太窄。
2. digest 里最关键的诚实限制已经很清楚：raw XS momentum gross 约 `+1.98 bps/bar`，按 `2 bps / 1x turnover` 还能剩 `+1.01 bps/bar`，但到 `4 bps / 1x turnover` 基本打平；这说明它目前更像**有成本生存线的弱到中等 edge**，还不是 admission-ready。
3. `inverse-vol` 的方向性改善目前还没把 scaling 带来的真实交易成本完整核进去，因此不能把更高 gross/Sharpe 直接当成层级升级证据。
4. `low-sentiment` 这层 gate 仍主要来自月频/周频论文语境；在没有更快 proxy 和明确 desk 化执行之前，它还不是会改变层级的 decisive blocker 解除项。

## Why it still deserves keep_P1
1. 主题本体独立且清楚：这是 **cross-sectional momentum raw alpha**，不是已有 carry / pair / timing 主题的包装变体。
2. digest 已把三层边界拆清：`raw alpha = XS momentum`、`overlay = inverse-vol sizing`、`gate = low sentiment / crowding`；后续可以非常具体地做唯一一次便宜 follow-up，而不是泛泛“再看看”。
3. 当前证据已经说明 short-cycle 不是完全虚无：在 liquid top universe 上确实有 gross edge，而且不像明显依赖私有 HFT 条件的 research curiosity。

## Minimal honest next follow-up
若 bot2 下一轮把它锁进 survivor，唯一一次便宜 follow-up 应直接回答：
- 在 liquid majors / 更长窗口 / 多 friction ladder 下，`XS momentum` 接上 **asset-level 或 strategy-level inverse-vol** 后，是否仍能在 realistic turnover 下稳定留出正的 net edge；
- 若不能，就应直接收口，不再拿慢变量 sentiment gate 继续包装。

## Runtime implication
- 正式分配 `Rank 212`。
- 层级定性为 `P1`，**不直接升 `P2`**。
- 由于当前 `Surviving candidate slot` 为空，这条对象应成为新的 survivor，保留 **1 次** 最小 decisive follow-up 预算。

## Result sentence
`Rank 212 / XS momentum × inverse-vol × low-sentiment gate` fresh intake 完成并保留为 `keep_P1`：它留下来的是一条可 desk 化的 liquid-majors 横截面动量 raw alpha，`inverse-vol` 可能增强成本后表现，但现有证据仍停在单 venue 短样本且接近 `4 bps` 成本生存线，暂不升 `P2`。
