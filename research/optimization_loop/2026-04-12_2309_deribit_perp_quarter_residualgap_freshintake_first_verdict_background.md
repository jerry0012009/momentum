# bot3 optimization loop — deribit perp-quarter residual gap fresh intake first verdict（background/P0）

## 本轮执行小点
- target: `research/quant_digests/2026-04-12_2101_deribit-perp-quarter-residual-gap-alpha.md`
- action: fresh intake first-verdict（最小费后快检 + execution realism 子检查）

## 最小实验（可复现）
- 数据源：Deribit public API `get_instruments` + `get_tradingview_chart_data`
- 标的：`BTC-PERPETUAL` vs `BTC-24APR26`（当前最近未到期 dated future）
- 频率/窗口：最近约 `3d` 的 `1m` bars（有效样本 `4321` bars）
- 信号：
  - 先用 `rolling annualized basis median (720m)` 构造 fair-gap
  - residual=`(future_close-perp_close)-fair_gap`
  - `rolling 240m z-score`，`z>=2` 做 `short spread`，`z<=-2` 做 `long spread`
- 执行口径：`signal(i) -> next-bar open(i+1)` 入场，固定 `15m` time-stop，`no-overlap`

## 结果
- trade count: `80`
- gross mean edge: `+4.49 bps/trade`（winrate `80%`）
- net edge（round-trip）:
  - `2 bps`: `+2.49 bps/trade`
  - `5 bps`: `-0.51 bps/trade`
  - `8 bps`: `-3.51 bps/trade`
  - `10 bps`: `-5.51 bps/trade`

## honesty / execution realism 子检查
- 对齐检查通过：所有信号均按 `next-bar open` 入场，未使用 signal 当根成交；
- 两腿价格均来自同 timestamp 的可交易 bar（无单腿缺失填补）；
- `no-overlap` 执行生效（每笔交易结束后才允许下一笔）。

## verdict
`deribit perp-quarter residual gap` fresh intake first verdict = `background/P0`。

单一 decisive blocker：`edge_after_cost` 不足。该信号在 gross 层有收敛特征，但对现实 round-trip 成本（>=5bps）敏感，费后不再成立，当前不进入 `keep_P1`。
