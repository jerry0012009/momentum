# Rank 326 — survivor follow-up verdict: background/P0

- Time: 2026-04-04 10:05 UTC
- Target: `Rank 326 / signed flow imbalance × maker-only conviction gate`
- Verdict: `background/P0`
- Slot impact: 用尽唯一 survivor follow-up；释放 `Surviving candidate slot`

## Why this changes runtime truth
这轮唯一 follow-up 已把对象最关键的归因问题收口：`Rank 326` 并没有证明自己是离开极低成本与最优成交假设后仍可独立推进的 short-cycle raw alpha。

现有证据更像是：
1. **base signal 很薄**：最小 portability sanity check 里，线性读法下 `corr(obi, fwd_5m)=0.0736`，`q99` 预测幅度只有约 `1.08bps`，按 repo 自带 `15bps` conviction threshold 基本零交易；
2. **一旦能打出交易，主导也已不是 signed flow 本体**：随机森林快检虽能在 3 天样本里产出 9 笔交易，但 `OOS R²=-0.0468`，特征重要性由 `volatility_20` 主导（约 `54.0%`），`obi` 只占约 `8.7%`；
3. **execution economics 仍是生死线**：repo 结论依赖 `maker-only` 低费率与高 conviction threshold；离开这个 best case，它更像 shared microstructure gate / toxicity filter，而不是一条可独立迁移的 raw alpha lane。

## Honest exit
因此本轮不能把 `Rank 326` 升到 `P2`。这条对象最诚实的定位是：

> `signed flow imbalance` 仍值得保留为别的短周期策略的 shared execution / conviction gate 备查证据，但当前不足以作为独立 front-slot alpha 继续推进。

## Runtime result sentence
`Rank 326`：唯一 survivor follow-up 已确认其 edge 主要依附 `maker-only` 执行与 volatility interaction，未证明离开最优成交假设后仍保留可迁移的独立 `signed flow -> 5m return` pocket，因此本轮诚实收口到 `background/P0`。
