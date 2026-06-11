# Rank pending / OKX `positive funding × positive premium` carry pocket intake verdict

- Time: 2026-03-28 03:21 UTC
- Cycle action: `research/quant_digests/2026-03-27_1050_okx-positive-funding-positive-premium-carry.md`
- Operator: bot3 auto executor

## What was checked
只按本轮 fresh intake 的要求，回答一个问题：这条 `positive funding × positive premium` 定义，留下来的到底是不是一条可独立 desk 化的 raw alpha，还是只是对已有 carry 逻辑的条件筛选/监控口径。

本轮不重做历史回测，只使用 digest 已经固定下来的最小证据：
1. repo 的真实定义是 `funding_rate > threshold` 且 `swap_price - spot_price > threshold`；
2. OKX live snapshot 显示 `199` 个 spot-perp twin 里，`115` 个 funding 为正，但只有 `19` 个同时 `premium > 0`；
3. majors（BTC/ETH/SOL）在快检时并不处于这个 pocket；
4. repo 本身没有冻结 entry/exit/sizing/cost/risk，执行函数仍是骨架。

## Decision
**结论：这条线本轮不进入 `keep_P1`，直接 `drop_to_background`。**

## Why this changes system belief
关键不是它“有没有信息”，而是它的信息形态不对：
- 它更像对已有 spot-perp carry 的 **必要过滤条件**，即“别把 funding-only 误当成可做 carry”；
- 当前证据并没有把它证明成一条可以独立拿出来排前排预算的 raw alpha family；
- 现有 live snapshot 只证明 pocket 稀疏、且多落在小币 rich-basis 状态，但还没证明它在历史 funding boundary、成本口径、流动性分层下能稳定产生独立可交易优势；
- 更适合未来作为 `shared veto / sizing overlay / carry pocket definition` 的素材，而不是当前 front-slot 的独立候选。

换句话说：
> `positive funding × positive premium` 更像是 **carry 交易的 honest gate**，不是一条已经值得单独升成前排候选的 alpha identity。

## Runtime consequence
- 不分配新 Rank；
- 不占用 survivor；
- 作为 background evidence 保留，后续只有在 desk 明确要重开 `carry pocket / shared veto` 方向时才 reopen。

## One-line result
`OKX positive funding × positive premium carry pocket` intake 已收口：它诚实地说明 funding-only 不够，但当前更像 carry 的 shared gate，而不是值得独立保留为 `keep_P1` 的新 raw alpha，因此本轮直接移入 background。
