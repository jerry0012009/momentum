# Rank 215 / Tether mint Whale Alert BTC impulse intake → keep P1

- 时间：2026-03-28 08:36 UTC
- 对象：`research/quant_digests/2026-03-28_0756_tether-mint-whalealert-btc-impulse-alpha.md`
- 结论：`keep_P1`
- 新分配 Rank：`215`

## 本轮回答的问题
这条 `公开 USDT mint 事件 -> BTC 5~30m follow-through` 的事件型 raw alpha，在当前 desk 里是否仍值得保留为可独立判分的主线对象，而不是直接降级成别的 BTC intraday 策略的稀疏 event gate？

## 最小证据
1. digest 已把对象的 base alpha 说清楚，而且是可直接写成交易规则的：
   - 信号不是泛泛的 stablecoin 叙事，而是 `公开 USDT mint` 事件
   - 方向是 `mint-only long`，默认不把 burn 硬写成对称 short
   - 主要持有窗口集中在 `5m / 10m / 15m / 30m`
2. 论文给出的核心量级足以说明它不是纯故事层：
   - 按 `每 +1bn USDT mint` 估计，BTC 在 `5m/10m/15m/30m` 的响应大致为 `+0.24% / +0.38% / +0.51% / +0.68%`
   - `60m` 开始衰减，`1d` 不显著，说明 alpha 半衰期确实落在我们关心的短窗
3. asymmetry 很明确，支持把对象读成一条独立 long-only 事件线，而不是对称双边策略：
   - mint 在 `5~30m` 显著
   - burn 大多不显著
   - 公开扩散（Whale Alert）与正向 sentiment 只是在放大同一条 raw alpha，而不是替代 alpha 本体
4. 这条线和当前 desk 已有的 own-return / XS momentum / funding / basis 家族不重合：
   - 它是 `公开外部事件 -> 单资产短窗 directional`，属于新的 alpha family
   - 因而即便样本还旧，也值得保留一次 survivor follow-up，而不是直接丢回 background

## 为什么不是 promote_P2
- 当前证据仍主要来自 `2014-2021` 的论文样本，没有完成现代市场 transfer；这不足以支持它已接近 `paper trade / paper launch`。
- 事件依赖外部公开 feed 与扩散口径，仍需要先确认 `公开可交易 pocket` 是否在近两年仍存活，不能直接把论文系数当成 desk 现货。
- 这轮 intake 也还没有把 `mint size threshold / diffusion split / cost cliff / event-time implementation` 做成当前仓内可复算 admission artifact，因此不该直接升 `P2`。

## 为什么不是直接 drop
- 和很多只能做 overlay 的稳定币话题不同，这条对象留下的是清楚的 raw alpha 本体：`公开 mint -> BTC 短窗 follow-through`。
- 它的半衰期、方向性与执行窗口都够具体，值得做一次便宜诚实的 survivor follow-up，去确认现代样本里它究竟还是独立 alpha，还是已退化为 event gate。

## 本轮正式 verdict
`Rank 215 / Tether mint Whale Alert BTC impulse` fresh intake 首轮 verdict 完成：它确实保留了一个与价格内生动量不同的 `公开 USDT mint 事件 -> BTC 5~30m follow-through` 稀疏事件驱动 long-only raw alpha 家族，因此本轮应记为 `keep_P1` 并获得正式 Rank；但现有证据仍主要停留在 `2014-2021` 论文样本与外部公开扩散口径，尚未完成现代市场 transfer，所以暂不直接升 `P2`。
