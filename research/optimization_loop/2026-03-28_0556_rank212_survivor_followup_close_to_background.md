# Rank 212 survivor follow-up close to background

- Time: 2026-03-28 05:56 UTC
- Target: `Rank 212 / XS momentum × inverse-vol × low-sentiment gate`
- Action: 唯一一次 decisive survivor follow-up；检查 `inverse-vol` sizing 放进 liquid majors / 更长窗口 / 多 friction 口径后，是否还能保住成本后净边际
- Verdict: `keep_P1 后转 background`

## What changed
这次收口点已经够明确：`Rank 212` 留下来的 raw alpha 叙事是对的——短窗 `XS momentum` 在最初那组 OKX spot / 13 majors / 8h->1h 快检里确实出现过接近成本生存线的正毛边际——但一旦把 follow-up 拉到更诚实的 `liquid majors + 更长 hold + inverse-vol overlay` 口径，结果没有往上升级，反而稳定转负。

## Evidence used for the close
直接使用已落库的同主题 transfer artifact：`reports/artifacts/quant_digests/crypto_risk_managed_xs_momentum_20260327/grid_summary.json` 与 `summary.json`。

关键事实：
- `32_8`（约 `8h formation / 2h hold`）
  - plain：`-0.33 bps/rebalance`
  - risk-managed / inverse-vol：`-1.53 bps/rebalance`
- `32_16`（约 `8h / 4h`）
  - plain：`-0.90 bps/rebalance`
  - inverse-vol：`-2.65 bps/rebalance`
- `64_16`（约 `16h / 4h`）
  - plain：`-2.67 bps/rebalance`
  - inverse-vol：`-5.01 bps/rebalance`
- `96_16`（约 `24h / 4h`）
  - plain：`-9.31 bps/rebalance`
  - inverse-vol：`-9.82 bps/rebalance`

这说明两件事：
1. survivor follow-up 想回答的唯一高杠杆问题——**`inverse-vol` 能不能把这条 short-cycle XS momentum 从“贴着成本线”推进成更稳的 net-positive alpha**——当前答案是否定的；
2. 而且不是“只有加完成本才不行”，而是 plain WML 在更长 hold / 更诚实 liquid-major transfer 下也没有继续站稳，`inverse-vol` 多数时候只是把一个已经偏弱甚至偏负的 WML 放大。

## Why this is not promote_P2
`P2` admission 至少要看到这条线在 effectiveness / honesty 上有更像 admission-ready 的正证据，但当前 follow-up 给出的反而是：
- 升级到更长窗口后，plain edge 不再稳定为正；
- `inverse-vol` overlay 没有解除 blocker，反而在所有 grid 上都比 plain 更差；
- 因而现阶段不能把它写成“可继续 desk 化验证的 admission candidate”。

## Why this is not another keep_P1 follow-up
policy 已经写死：survivor 只允许 1 次最小 decisive follow-up。`Rank 212` 的 survivor 预算本轮已用完，而且 follow-up 已经成功回答唯一 blocker——`inverse-vol` 在更诚实口径下并没有把它推上一个新层级——所以不能再留在前排继续拖。

## Runtime implication
- `Rank 212` 保留为一个有记录的 `P1` 主题认知：`XS momentum` 是 raw alpha，`inverse-vol` / `sentiment gate` 是 overlay / gate。
- 但当前这条具体对象的前排实验已经诚实收口：**不升 `P2`，不再占用 survivor 槽位，转入 `Background pool`。**
- survivor lock 解除；后续 front slot 应回到下一条 fresh intake。

## Result sentence
`Rank 212 / XS momentum × inverse-vol × low-sentiment gate` 的唯一 survivor follow-up 已收口：一旦把它放到更诚实的 liquid-majors / 更长 hold / inverse-vol transfer 口径，plain WML 与 inverse-vol 版本都未能稳定保住正净边际，且 inverse-vol 在各 grid 上普遍比 plain 更差，因此本轮只能 `keep_P1 后转 background`，不升 `P2`。
