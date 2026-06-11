# Rank 216 / Hyperliquid funding-aware multi-window TSMOM × edge gate intake → keep P1

- 时间：2026-03-28 09:25 UTC
- 对象：`research/quant_digests/2026-03-28_0850_hyperliquid-fundingaware-tsmom-universe-audit.md`
- 结论：`keep_P1`
- 新分配 Rank：`216`

## 本轮回答的问题
这条 `多窗口 TSMOM + directional funding penalty + edge gate` 留下来的到底是不是一条**可独立判分的 perp raw alpha**，还是主要只是一个包装完整、但在关键口径没修前还不能当策略对象讨论的工程骨架？

## 最小证据
1. **repo 本体确实有独立 alpha，而不只是执行壳。**
   - `momentum_trading/signals/engine.py` 直接把核心信号写成：多窗口历史收益的 rolling z-score 平均，得到 `s_raw`，再叠加 directional funding penalty 得到 `s_adj`。
   - 也就是说，方向性预测的起点不是 generic execution/risk wrapper，而是明确的 `TSMOM raw alpha`。
2. **它的“值钱层”也确实不只是 README 讲故事。**
   - `risk/engine.py` 明确实现了 `w ~ s_adj / sigma`、liquidity/OI caps、以及 `edge >= min_ratio * friction` 的交易门槛。
   - 这让对象保留下来的不是“趋势永远有效”这种空话，而是一个可被 desk 单独判分的组合：`TSMOM 本体 × funding 惩罚 × edge gate`。
3. **digest 指出的关键 universe blocker 可以在 live snapshot 里复现，不是想象出来的。**
   - 我用 Hyperliquid 公共 `metaAndAssetCtxs` 现场快照复算后，按 repo 原写法把 `openInterest >= 5,000,000` 当成阈值时，当前只剩 `6` 个币通过过滤；
   - 若按更合理的 `OI_USD = openInterest × midPx` 口径，同样阈值会得到 `12` 个币，并把 `BTC / ETH / SOL / BCH / TAO / ZEC` 拉回 universe；
   - 这说明 repo 当前默认 universe 不是“略微有偏”，而是**会系统性错删主流高价币**，直接改变策略到底在测什么。
4. **因此当前 blocker 很清楚，但不是致命到该直接 drop。**
   - `config/4h_swing.yaml` 的 `lookbacks: [24,96,240]` 注释写成 `24h/4d/10d`，但代码按 bar 数解释，实际在 `4h` bar 上对应 `4d/16d/40d`；
   - funding 层当前用的是 predicted funding，不是最终收付 funding；
   - 这些都说明它还没到 admission-ready，但也正因为 blocker 很集中，才值得保留一次 survivor follow-up，而不是直接丢回 background。

## 为什么不是 promote_P2
- 还没有完成最关键的 honest transfer：`OI_USD` universe 修正后，`裸 TSMOM / + funding penalty / + edge gate / + universe 修正` 四臂到底哪一层在成本后真的留下净边，目前仓内还没有 admission artifact。
- 当前 funding 层仍混着 `predicted funding` 与实际持仓收付语义，不能直接把 repo 默认实现当成 desk-ready 真收益。
- 这轮 intake 已经把 blocker 缩到非常具体的两件事：**universe 口径** 与 **funding realism**；在它们没做完前，直接升 `P2` 会把工程修口径误包装成 alpha 已经过审。

## 为什么不是直接 drop
- 它和已有 `plain TSMOM` / `high-vol low-liq pocket` 线索不一样：这里留下来的不是“趋势还行吗”，而是**`趋势信号本体` 与 `funding/edge/execution realism` 能否被拆开判分**这一层更完整的 perp raw-alpha 母版。
- 而且当前 live snapshot 已经证明 repo 默认 universe 会把 `BTC/ETH/SOL` 等高价主流币错删掉；这意味着对象当前最大的风险不是“alpha 根本不存在”，而是**还没在对的 universe 上被 honest 地测过**。
- 既然 blocker 已集中到一次便宜 follow-up 可回答的问题，就应该先保留为 `keep_P1`，而不是把它和普通工程模板一起扔掉。

## 唯一合理的 survivor follow-up
若进入 survivor，唯一一次 follow-up 应直接回答：
- 把 universe 固定为 `dayNtlVlm >= 10M` 且 `OI_USD >= 5M` 后，`15m` 上的 `裸 TSMOM / + funding penalty / + edge gate / 全部叠加` 四臂，哪一层在成本后真的保留净边；
- 把 predicted funding 改成更接近实际收付的 realized/next-hour proxy 后，funding penalty 还是 alpha 增强器，还是只是在回测里看起来聪明；
- 若修完口径后只剩 execution shell、没有独立 post-cost 优势，则应直接收口转 background，不再把它当新前排对象拖长。

## 本轮正式 verdict
`Rank 216 / Hyperliquid funding-aware multi-window TSMOM × edge gate` fresh intake 已完成首轮正式 verdict：repo 原始实现确实留下了一条可独立判分的 perp raw alpha 家族——`多窗口 TSMOM + directional funding penalty + edge gate`，而不是纯执行壳；但当前 live snapshot 已复现其核心 universe blocker（把币本位 `openInterest` 当成 USD 只剩 `6` 币，修正成 `OI × midPx` 后变 `12` 币并把 `BTC/ETH/SOL` 拉回），因此它现在最诚实的位置仍是 `keep_P1`，先做一次修 universe/OI 口径与 funding-realism 的 survivor 收口，而不是直接升 `P2`。
