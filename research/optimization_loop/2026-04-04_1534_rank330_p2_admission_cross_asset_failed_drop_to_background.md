# Rank 330 — P2 admission 第一轮：effectiveness / cross-asset failed，drop to background

- Time: 2026-04-04 15:34 UTC
- Target: `Rank 330 / dual SuperTrend flip × EMA50 × volume gate`
- Action type: `Active P2` admission round 1
- Verdict: `drop_to_background`
- Admission board artifact: `reports/artifacts/rank330_p2_admission_cross_asset_20260404_1455/summary.json`

## What this round tested

在上一轮已经确认 canonical SuperTrend 可以恢复 firing density 之后，这一轮只回答 `P2` admission 的前两轴：

1. `effectiveness / expected return`（含成本前后）
2. `cross-asset stability`

最小板：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`，`15m`，recent `90d`，同一套 canonical fast/slow SuperTrend + `EMA50` + volume gate + repo 既定 exit 壳。

## Key results

### Signal shell 确实恢复了，不再是“不 firing”问题
- aggregate `bull_flip = 554`
- aggregate `bear_flip = 556`
- aggregate `long_signals = 287`
- aggregate `short_signals = 346`
- aggregate `trades = 629`

这说明 canonical 化后，策略壳会开火；问题已经不再是 source implementation freeze。

### 但 effectiveness 没过，而且不是“换币才塌”，而是含成本后全线塌

#### BTCUSDT
- trades: `154`
- gross return: `+58.82%`
- net return: `-21.24%`
- avg net trade: `-13.79`

#### ETHUSDT
- trades: `182`
- gross return: `-16.66%`
- net return: `-63.92%`
- avg net trade: `-35.12`

#### SOLUSDT
- trades: `148`
- gross return: `-19.28%`
- net return: `-52.67%`
- avg net trade: `-35.59`

#### BNBUSDT
- trades: `145`
- gross return: `+2.05%`
- net return: `-56.67%`
- avg net trade: `-39.08`

#### Aggregate
- gross return on 10k each: `+6.23%`
- net return on 10k each: `-48.62%`
- win rate: `34.98%`

## What changed system truth

`Rank 330` 的 canonical 版虽然已经恢复出正常 firing density，但在 `BTC/ETH/SOL/BNB 15m recent 90d` 上并没有形成可迁移、含成本后仍站得住的 trend raw alpha：只有 BTC 在成本前显著为正，ETH/SOL/BNB 连成本前都不稳，而成本后四个主流币全部转负，因此这不是可以继续开放式 `keep_P2` 的 admission 对象，而应直接从 `Active P2` 收口回 `background/P0`。

## Why this is not a one-time P2->P1 re-scope

`P2 -> P1 re-scope` 只在存在唯一明确缩圈方向时才成立。当前证据不支持那种解释：

1. 不是“跨币不稳但某个清楚子宇宙稳定”——只有 BTC 成本前明显为正，但成本后也转负；
2. 不是“只是某个次要 filter 写错”——这轮已经在 canonical firing density 前提下重跑，问题转成收益/成本现实性；
3. 不是“只差再补一点 admission”——第一轮已经回答了最核心的 effectiveness/cross-asset，答案是负面的。

如果未来要 reopen，它应作为全新 re-spec 对象重新定义（例如完全改 execution/cost/hold shell），而不是把当前这条对象继续留在前排。

## Runtime decision

- `Active P2 slot`: clear to `none`
- `Background pool`: append `Rank 330` as latest parked object
- Current cycle impact: 原定第 2 个 `Rank 330` 出口决策小点前置条件失效，应标记为 `blocked`

## Result sentence

`Rank 330`：canonical 版本已恢复 firing density，但 `BTC/ETH/SOL/BNB 15m recent 90d` 的 effectiveness / cross-asset admission 明确失败——只有 BTC 成本前有 trend shell、成本后四币全负，因此这条对象不再保留在 `Active P2`，直接 `drop_to_background`。
