# Rank 211 / CME BTC futures sign classifier intake keep P1

- Time: 2026-03-28 03:56 UTC
- Target: `research/quant_digests/2026-03-27_0904_cme-btcfutures-sign-classifier-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Rank: `211`

## What changed
这条对象留下来的不是“论文里某个 SVM headline accuracy 很高”的黑箱故事，而是一条可独立 desk 化的 raw alpha 假设：`next-bar sign classifier + high-threshold abstain` 可能在 crypto futures 上形成方向型状态机，但当前 public-kline 迁移已经诚实证明它暂时还只是 **weak directional edge**，离可直接升 `P2` 还差一层 decisive microstructure / execution 证据。

## Why it is not P2 yet
1. digest 里最小迁移已经给出关键负面：
   - `BTCUSDT perp 15m` OOS accuracy 约 `52.3%`
   - `0.55/0.45` 阈值下 trade hit 约 `56.5%`
   - 但扣 `4 bps` 后仍约 `-1.05 bps/bar`
2. 这说明当前证据支持的是“有弱方向 edge，但 taker 先不过线”，不是“已经具备足够诚实的 admission 通过条件”。
3. 真正会改变层级的下一步，不该再停留在论文 headline 或继续看 kline accuracy，而应直接回答：加入 `aggTrades/bookTicker` 风格的更细 microstructure 特征后，极端置信度分层能否把净 edge 拉过 realistic cost gate。

## Why it still deserves keep_P1
1. 主题本身是独立的 single-asset directional raw alpha，不是已有 carry / pair / regime 主题的重复包装。
2. digest 已经把策略骨架说清楚：`signal probability -> abstain threshold -> hold 1~3 bars -> cost veto`，可以被诚实复刻成明确实验对象。
3. 当前失败点也足够聚焦：不是泛泛“再补点稳定性”，而是非常具体的 `microstructure feature richness + execution realism` 问题。

## Runtime implication
- 正式分配 `Rank 211`。
- 层级定性为 `P1`，但**不直接升 `P2`**。
- 由于当前 survivor 槽位仍被 `Rank 210` 合法占据，这一轮只把 `Rank 211` 记为已完成首判的 ranked intake；是否获得后续前排跟进，留待 bot2 在下一轮按 policy 重排。

## Result sentence
`Rank 211 / CME BTC futures sign classifier` fresh intake 完成并保留为 `keep_P1`：它留下来的是一条可 desk 化的 `next-bar sign classifier + high-threshold abstain` 方向型 raw alpha，但现有 public-kline 证据只够证明“弱 edge、taker 不过线”，还不够直接升 `P2`。
