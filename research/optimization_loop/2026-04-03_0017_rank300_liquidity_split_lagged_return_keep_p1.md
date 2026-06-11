# Rank 300 / liquidity-split lagged-return sign-flip alpha — fresh intake first verdict = keep_P1

- Time: 2026-04-03 00:17 UTC
- Target: `research/quant_digests/2026-04-02_2319_liquidity-split-lagged-return-alpha.md`
- Slot: Fresh intake
- Verdict: `keep_P1`
- Assigned Rank: `300`

## Why this changes system belief

这条题目不是旧 `loser-bounce / top-N reversal` 家族的换词包装，而是一条可以独立成立的 **raw alpha family**：

> `24h lagged return` 的横截面排序本身有预测力，但 **信号符号取决于 liquidity bucket**；高流动性端更像 winner-follow，低流动性端才可能出现 loser-bounce。

这和单纯说“crypto 有短期 reversal”不一样；它要求 desk 在同一个 lagged-return 母因子下做 **direction fork**，而不是只叠一个 filter。

## Why not P2 yet

当前 digest 已经给出足够清楚的独立主语、desk 化翻译和最小 clean-room 壳，但还 **没有** 到可以直接进入 `P2 admission` 的程度，原因有三点：

1. **当前可移植证据主要落在 liquid-perp continuation 端**  
   Binance USDⓈ-M `15m -> 1h` portability probe 里，`mom_all` / `mom_liq` 明显成立，而 `rev_ill` 在当前 top-volume perp universe 上仍显著为负；说明这个 family 在我们当前 desk 上最像 “liquid winner-follow sleeve”，而不是完整 sign-flip 双臂都已经站稳。

2. **关键 cutoff 仍未收口**  
   现在还不知道 continuation 只存在于 top decile / top quintile，还是更广 liquid bucket 都有效；没有 decile 级 cutoff 图，就还缺最关键的 desk governance 轴。

3. **formation / holding 网格仍未补齐**  
   目前主证据集中在 `24h formation + 1h hold`，还没回答 short-cycle desk 最关心的 `6h/12h/24h/48h × 15m/30m/1h/2h/4h` 哪个 pocket 才是真正可迁移的主 pocket。

## System-level conclusion

因此本轮 first verdict 不是 `background/P0`：
- 它 **有独立 raw-alpha 主语**；
- 也 **有公开数据 clean-room 路径**；
- 还给出了和现有 reversal family 不同的结构性新信息：**alpha 方向受 liquidity 决定，liquid perp desk 默认先测 winner-follow。**

但它也还 **不够直接升 `P2`**，因为真正可 desk 化的 admission 主体当前只在 family 的一侧（liquid momentum sleeve）显示出生命迹象，另一侧并未在现有 perp universe 上成立。

## Runtime action taken

- 为该 fresh intake 分配正式 `Rank 300`
- 结论写回为：`keep_P1`
- 该对象进入 `Surviving candidate slot`，保留 **1 次** 最小 decisive follow-up 预算
- 当前最值得的 follow-up 方向应围绕：**liquidity cutoff 是否真能把 lagged-return family 从 reversal 改判为 continuation**，而不是再泛泛重复 loser-bounce
