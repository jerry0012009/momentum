# Rank none / tightened-supertrend-alpha fresh intake -> background/P0

- 时间：2026-04-25 14:51 UTC
- 对象：`research/quant_digests/2026-04-24_2120_tightened-supertrend-feeaware-verdict.md`
- 槽位：Fresh intake slot
- 本轮动作：fresh intake first verdict
- 结论：`dual SuperTrend convergence × EMA50 × ATR bracket` 直接诚实收口为 `background/P0`，不进入 survivor，也不分配 Rank。

## 为什么这一步已经足够
当前 digest 已经完成本轮 success criterion 所要求的最小 decisive blocker 检查，而且结论是负面的：

1. `BTC/ETH/SOL/BNB` 四个 liquid majors 在统一 round-trip `10 bps` 成本口径下全部为负；
2. pooled `430` 笔，win rate 仅 `34.7%`，avg net `-11.37 bps/笔`；
3. 相对最接近可做的 `SOL` 也只有 `-3.26 bps/笔`，说明不是单一币种略差，而是 continuation 本体在 liquid-major `15m` 上整体偏薄；
4. volume filter 仍保留 `25%~27%` 的 pass rate，说明问题不是“几乎无交易样本”，而是信号厚度不够覆盖成本。

## 系统认知变化
这条 repo 更适合保留为“结构完整但成本后不成立的趋势壳反例素材”，而不是当前前排候选：README 的完整策略叙事没有被公开 `15m` portability probe 兑现成可复用的 after-cost pocket，因此本轮直接判为 `background/P0`。

## 对 runtime 的直接影响
- Fresh intake 当前对象完成 first verdict，结果为 `background/P0`；
- 不进入 `Surviving candidate slot`；
- 不分配 Rank；
- 等待 bot2 下一轮重排后切换到下一个 intake 对象。
