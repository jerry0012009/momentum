# Rank 233 / volume-shock polarity-by-coin-alpha — fresh intake first verdict (`keep_P1`)

- Time: 2026-03-29 08:36 UTC
- Target: `research/quant_digests/2026-03-29_0648_volume-shock-polarity-by-coin-alpha.md`
- Source artifact: `reports/artifacts/quant_digests/20260329_volume_return_polarity/summary_z2_ret50bp.csv`
- Action type: fresh intake first verdict

## What was checked

只做最小首判，不扩写新排班：复核 digest 中已经落地的 public-data sanity check，确认它是否已经足以作为独立 raw alpha 候选保留，还是只是旧有 continuation / reversal filter 的换壳版本。

本轮直接依赖的已落地证据：

- Binance USDⓈ-M perpetual `5m` public bars
- 事件定义：`|ret_5m| >= 50bps` 且 `log(quote_volume)` rolling `z >= 2`
- 执行口径：`next-bar open`，hold `1/2/3` bars，no-overlap
- 当前样本：每币约最近 `5000` 根 `5m` bar（约 17 天）
- 当前 artifact：`summary_z2_ret50bp.csv`

## What changes system belief

这条线已经证明：**post-shock volume-return 不该被统一读成 continuation 或统一读成 fade，而应按 coin-specific polarity 独立交易。**

当前最关键的可保留信息：

- `BTCUSDT`：contrarian `3 bars` 平均约 `+7.17 bps`，`n=30`
- `XRPUSDT`：contrarian `1 bar` 平均约 `+7.56 bps`，`n=37`
- `ETHUSDT`：continuation `2 bars` 平均约 `+10.34 bps`，`n=65`
- `SOLUSDT`：continuation `2~3 bars` 平均约 `+7.30 / +8.26 bps`，`n=54`

这已经足够说明：它不是“统一 volume confirmation gate”，而是一条**可独立定义 trigger / direction / hold 的 single-asset post-shock raw alpha family**。

## Why it does NOT go straight to P2

当前证据还不够诚实地直接升 `P2`，因为 decisive blocker 很明确：

1. **样本太短**：现有 sanity check 只有最近约 17 天，不足以回答 time stability。
2. **尚未扣费**：现在还是未扣 round-trip cost 的 polarity read，不足以回答 effectiveness after friction。
3. **参数稳定性未冻结**：`ret threshold / volume z / hold bars` 仍只展示了一个切片，不足以证明不是局部参数偶然。
4. **cross-asset coverage 还不够**：虽然已显示 major coins polarity 不同，但还没做 frozen replication 去回答这是否能稳定胜过 `always continuation` / `always fade` 两个常数方向基线。

因此，**它值得保留为独立 raw alpha 候选，但当前最诚实的 first verdict 只能是 `keep_P1`，不能直接 `promote_P2`。**

## Formal verdict

- Assigned rank: `Rank 233`
- Verdict: `keep_P1`
- Slot effect: 进入 `Surviving candidate slot`
- Required next decisive follow-up: 做一次 `180d 5m` frozen replication，强制 `next-bar open + no-overlap + 6bps/side`，并把 `monthly polarity map` 与 `always continuation` / `always fade` 并排比较；若成本后仍显著优于常数方向基线，则可升 `P2`，否则收口回 background。

## One-line result

`Rank 233 / volume-shock polarity-by-coin` fresh intake 首判完成：现有公开样本已足够证明它是值得独立保留的 coin-specific post-shock raw alpha family，而不是统一 continuation gate；但因证据仍停在 17 天、未扣费的 polarity sanity check，本轮按 `keep_P1` 收口并进入 survivor，不直接升 `P2`.
