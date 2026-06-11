# bot3 auto：fee-aware spot x-venue gap conditional fresh intake blocked

- 时间：2026-04-22 08:26 UTC
- 当前执行小点：cycle_plan 第 3 项
- target：`research/quant_digests/2026-04-22_0458_feeaware-spot-xvenue-gap-shell.md`
- action：conditional fresh intake，前置条件为“只在第 1 项未形成 survivor/P2 时执行”

## 结论

第 3 项本轮必须标记为 `blocked`，因为第 1 项已经产生 `Rank 433 / 24h loser→winner majors8 RV fade` 的 `keep_P1` survivor，随后第 2 项也已经完成该 survivor 的唯一 follow-up 并转入 `background/P0`；按本轮 cycle_plan 的显式条件，第 3 项不是合法可执行主动作，bot3 不得把它自行重排成新的 fresh intake。

## 最小 sanity note（不改变槽位）

在发现前置条件冲突前已做了一个最小 live quote sanity probe，仅作为不入槽的旁证：Bitstamp/Kraken BTCUSD、ETHUSD 约 8 个 5s 样本中，top-of-book gross gap 均值分别约 `1.26bps`、`0.65bps`，最大约 `3.22bps`、`2.14bps`。这与原 digest 的判断一致：主流现货同币跨所裸 gap 很薄，普通 taker/taker 显性费用后很难保留独立 after-cost alpha，更像 inventory/maker-first deployment shell；但由于本小点前置条件不成立，本轮不把它升级、rank 化或写成正式 fresh-intake verdict。

## Runtime 写回

- 仅更新 cycle_plan 第 3 项：`result` 写明前置条件已被第 1/2 项结果否定；`status` 改为 `blocked`。
- Fresh intake / Survivor / Active P2 / Paper queue 的 runtime truth 不做层级迁移。

## Tail

- homepage refresh：待执行（best-effort）
- email summary：待执行
