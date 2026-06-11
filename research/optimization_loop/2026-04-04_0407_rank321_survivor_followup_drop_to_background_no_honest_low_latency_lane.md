# Rank 321 — same-underlier cross-venue gap mean reversion × latency budget survivor follow-up：drop_to_background

- Time: 2026-04-04 04:07 UTC
- Target: `Rank 321 / same-underlier cross-venue gap mean reversion × latency budget`
- Action type: surviving candidate single decisive follow-up
- Verdict: `background/P0`

## 结论
`Rank 321` 的唯一一次 `P1 survivor` follow-up 已经足够收口为 `background/P0`：当前证据没有给出哪怕一条**诚实可迁移的低延迟 desk lane**，能在更真实的 `fee / spread / latency / double-fill` 口径下稳定留下净边。它仍然是一条主语清楚的 raw alpha 母板，但现在最像的是“只有在极强基础设施优势下才可能成立的 execution-sensitive relative-value idea”，而不是当前 desk 可以继续推进到 `P2 admission` 的候选。

## 为什么这一步直接收口，而不是 promote_P2
这次 follow-up 要回答的不是“venue gap 会不会回归”——那个问题在 first verdict 里已经答过了；要回答的是：**是否存在至少一条诚实可迁移的最小 desk lane。** 结合已有 digest 证据，这个问题目前应答为 **没有**：

1. **gross edge 太薄，默认先输给现实成本。**
   first verdict 里最乐观的 public-data 粗检，`BTC/ETH/SOL` 的 next-bar gross convergence 也普遍只有亚 `1~2 bps` 量级；这还没有扣掉双边 taker/maker fee、bid/ask crossing、queue loss、以及双腿不对称成交的损耗。对 cross-venue same-underlier stat-arb 来说，这种毛边厚度不足以支持“可迁移 lane 已存在”的正面结论。

2. **repo stress study 已经把 latency cliff 讲得太清楚。**
   digest 记录的 toy stress test 里，`threshold = 0.12, transfer_delay = 5` 时，`latency = 0` 还是正值，但只多 `1` 个 step 延迟就从 `+2.068` 翻到 `-0.901`。这不是“小幅退化”，而是说明这条线的生死几乎完全压在极窄 latency budget 上。只要本轮拿不出“当前 desk 确实拥有接近该条件的 lane”这条新证据，就不能把它抬到 `P2`。

3. **现有证据里并没有冒出唯一清楚的可迁移 lane。**
   按 cycle plan，本轮优先看的应该是 `BTC/ETH/SOL × Binance/OKX(/Bybit) × inventory-funded / top-of-book / 秒级或更细 latency bucket`。但 first verdict 给出的 reader-facing 证据恰好相反：
   - `1m` bar 只足够证明“回归倾向存在”，不足以证明可净赚；
   - 真正决定生死的是 `1s/5s top-of-book + latency bucket`；
   - 还必须显式加入双边库存、双腿成交、费用与 spread。
   换句话说，当前并不是“已经看到一条可用 lane，只差细化 admission”，而是“连最小诚实 lane 是否存在都还没被正面证明”。这就不该继续往前排资源。

4. **这条线缺的不是再补同维度解释，而是基础设施事实。**
   若继续留在前排，下一步也只能继续围绕低延迟执行可行性打转；而 policy 已明确：`P1 survivor` 只有一次最小 decisive follow-up，用完就要收口，不能因为主语好看就无限续命。

## 为什么也不是 P2->P1 re-scope
这里不存在一个“唯一明确的 re-scope lane”可供重写成更小更干净的策略壳：
- 改成只做 `BTC`、只做 `Binance/OKX`、只做 `inventory-funded`，本质上仍然没有新增证据证明净边能穿过真实成本与延迟 cliff；
- 改更慢频只会进一步偏离这条 alpha 的真正工作区间，因为 digest 已经说明它不是慢速 `5m/15m` 主执行信号；
- 改成“等未来更强 infra 再看”不是 re-scope，只是把 blocker 往后拖。

因此，这一步最诚实的出口不是 `promote_P2`，也不是一次伪装成 re-scope 的续命，而是直接 `drop_to_background`。

## 写回 runtime 的系统认知变化
- `Rank 321` 已用完唯一一次 `P1 survivor` follow-up。
- 当前没有证据支持其进入 `P2 admission`。
- 该对象从前排退出，进入 `background/P0`；若未来出现真实 `1s/5s top-of-book + fee/spread + latency-bucket` 级别的新正证据，再由人工明确 `reopen`。

## Reader-facing 一句话
`Rank 321` 的问题不是 alpha 主语不清楚，而是它的毛边太薄、对 latency cliff 太敏感；在没有任何一条被正面证明可穿过真实 `fee/spread/double-fill` 的低延迟 desk lane 之前，它不配继续占用前排资源。
