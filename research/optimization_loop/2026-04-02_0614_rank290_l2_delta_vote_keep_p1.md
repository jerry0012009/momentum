# Rank 290 — L2 imbalance × aggressive trade delta × EMA vote：first verdict = keep_P1

- 时间：2026-04-02 06:14 UTC
- 对象：`research/quant_digests/2026-04-02_0550_orderbook-delta-vote-microstructure-alpha.md`
- 类型：fresh intake first verdict
- 结论：`keep_P1`（进入 `Surviving candidate slot`，保留 1 次最小 decisive follow-up）
- 正式 Rank：`290`

## 为什么不是直接打回 P0
这条候选虽然属于已经很拥挤的 OBI / OFI / microstructure 家族，但**还不只是旧 OBI 叙事换壳**。它至少有三个值得保留到 survivor follow-up 的点：

1. **主语够具体，不是泛 microstructure 故事**
   - 不是单看盘口厚度；
   - 而是 `top20 imbalance`、`recent aggressor delta`、`EMA trend` 三腿同向共振；
   - 触发逻辑是明确的 `3-of-4 vote` admission，不是抽象“看订单流强弱”。

2. **entry / flip skeleton 已经足够可独立复核**
   - repo 已给出可运行原型；
   - digest 也把 `entry / opposite-vote flip / sizing` 拆得比较清楚；
   - 对 short-cycle desk 来说，这已经够支撑一次便宜、诚实的 follow-up，而不是停留在论文解释学。

3. **最小前向路径现实可做**
   - 所需数据源都是 Binance public market data；
   - 真正缺的是连续 recorder 与 after-cost markout，而不是缺核心信号定义。

## 为什么也不能直接升 P2
它还没有强到可以跳过 P1，原因也很明确：

1. **当前还没有任何 after-cost 证据**
   - 这是一个容易频繁 flip 的 taker-ish 短周期壳；
   - 若 `10~20bps` round-trip 一上去就被磨平，那它更像 lower-TF confirmation，不一定配得上独立 alpha admission。

2. **当前 live sanity check 只证明“会触发”，没证明“能赚钱”**
   - digest 里的 `27` 个 symbol-snapshots 只能说明信号不是全天乱闪；
   - 还不能回答 `+1/+3/+5 bar markout`、turnover、成本后净边到底留不留得住。

3. **distinctness 虽成立，但 edge 仍可能主要来自 alt 单边环境，而不是通用 microstructure alpha**
   - 目前 digest 自己也更像在暗示 `SOL/BNB/DOGE` 这类 beta alt 更容易触发；
   - 这意味着它更像“特定币 / 特定时段 continuation pocket”，还不够资格直接按广义单币 microstructure alpha 升 P2。

## 本轮改变系统认知的话
`Rank 290` 不是“旧 OBI 家族换个名再讲一遍”，而是一个有清晰三腿共振主语、可直接前向录数复现的单币 microstructure continuation 原型；但在拿到最基础的 after-cost markout 之前，还不够诚实地直接升 `P2`。

## 唯一 survivor follow-up 应该测什么
按 policy，survivor 只配 1 次最小 decisive follow-up；最值钱的不是再补概念说明，而是直接回答这一个 blocker：

> `OBI + delta + EMA` 这条 admission 在最小前向 / bar-close markout 口径下，是否在 `BTC/ETH/SOL/BNB/DOGE` 中至少留下一小块 **成本后仍存活** 的 `1m/3m` pocket？

优先 follow-up 口径：
- 做 `+1 / +3 / +5 bar` markout；
- 成本至少压 `10 / 15 / 20bps` 三档；
- 比较 `BTC/ETH` 与 `SOL/BNB/DOGE` 的 per-symbol signal density 与净边；
- 顺手验证 `volume bonus` 是否只是噪音装饰，而不是 alpha 本体。

若这一步回答为“after-cost 全灭”或只剩极薄、不可迁移毛边，则应直接 `background/P0`；若至少留下一块清晰 pocket，再考虑升 `P2`。
