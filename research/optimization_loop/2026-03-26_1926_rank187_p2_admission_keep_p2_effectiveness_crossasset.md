# Rank 187 / BTCUSDT 15m late-session path-shape swing — 首轮 P2 admission（keep_P2）

- Time: 2026-03-26 19:26 UTC
- Target: `Rank 187 / BTCUSDT 15m late-session path-shape swing`
- Step type: first `P2 admission`
- Verdict: `keep_P2`

## 本轮只回答的问题
对冻结后的 exact pocket

- market: `BTCUSDT`
- bar: `15m`
- observation window: 前 `8h`（`32` 根 bars）
- lookback: `60d`
- similarity: `k=3` nearest-neighbor partial path shape
- entry: only when implied remainder path still points to a higher future max
- baseline exit: `predicted-max timing`

只回答它在 **`effectiveness + cross-asset`** 上，是否足够继续留在 `P2`，还是应该直接 `drop_to_background`。

## 证据 1：effectiveness 这条轴当前过关，不该直接判死
沿用 intake / survivor 阶段已经冻结的 canonical artifact：

- `reports/artifacts/quant_digests/bitcoin_intraday_curve_shape_20260326_1633/variant_summary.csv`
- `reports/artifacts/quant_digests/bitcoin_intraday_curve_shape_20260326_1633/selected_variant_trades.csv`

`h32_k3` 这条 canonical pocket 当前仍是该 digest 里最厚的版本：

- `18` 笔交易
- gross `avg trade +0.4628%`
- gross Sharpe `3.25`
- max drawdown `-6.97%`
- 扣 `6bps` round-trip 后，`avg trade` 仍约 `+0.4028%`

和同一批 variant 的相邻对照相比，它也不是随便挑出来的弱 pocket：

- `32 bars, k=5` 仍为正，但已降到 `+0.2711% / trade`、Sharpe `2.06`
- `24 bars, k=3` 已转负到 `-0.3392% / trade`
- `12 bars, k=5` 也为负到 `-0.1575% / trade`

所以这条 admission 的第一问，当前答案很明确：**它有样本少的问题，但在 effectiveness 上还没有弱到该被直接扔回 background。**

## 证据 2：cross-asset 还不够支持升级，但也没暴露“一换资产就反向”的 fatal flaw
本轮没有重开一个新的 ETH canonical strategy；只做了最便宜、最诚实的 transfer proxy：

- 取 `Rank 187` 在 BTC 上已经锁定的 `18` 个 entry / exit 时间戳；
- 把同样的时间窗口平移到 `ETHUSDT 15m` 上，观察 **同一批 late-session swing 时段** 的方向是否大致同向；
- 这只是 cross-asset proxy，不是正式的 ETH 版独立策略定义。

结果：

- `ETHUSDT` same-time transfer proxy：`18` 笔
- gross `avg trade +0.5557%`
- median `+0.2334%`
- hit rate `50%`
- 扣 `6bps` 后 mean 仍约 `+0.4957%`

这说明两件事：

1. **当前看到的 late-session swing 并不明显是纯 BTC 特例。** 至少在这批已经被 BTC path-state 选中的日子里，ETH 同时段并没有系统性反着走。  
2. 但这还 **不能**被写成“cross-asset 已通过”。因为这只是 `same-time transfer proxy`，不是“用 ETH 自己的 partial-day path-shape 信号独立生成 ETH trades” 的正式复制。

换句话说：
- cross-asset 这条轴现在 **不是 fatal negative**；
- 但它也 **还不是 admission 已完成** 的正面通关证据。

## 为什么本轮不是 drop_to_background
如果本轮看到的是下面任一情形，应该直接 drop：

- canonical BTC pocket 扣基本成本后已经很薄甚至翻负；
- 或者一做最小 transfer proxy，ETH 就明显系统性反向；
- 或者 BTC 的“最强 pocket”其实只是从一堆差不多的负值/噪声里偶然挑出来。

但当前都不是：

- BTC canonical pocket 仍明显为正；
- ETH 同时段 proxy 没有翻成负向打脸；
- 同一批 variant 对照也显示 `h32_k3` 的确是当前 family 里最厚的 pocket，而不是随便一格都差不多。

因此它现在更像：

> **effectiveness 已够继续 admission；cross-asset 暂时未被证伪，但还需要正式复制检查。**

这正是 `keep_P2`，而不是 `drop_to_background` 的状态。

## 本轮之后，唯一合理的下一条 admission 轴
既然首轮已经回答了 `effectiveness + cross-asset`，下一轮不该再回头重复“BTC 还赚钱吗 / ETH 同不同步”。

更高杠杆的下一轴应收敛到：

- **`time stability`**：回答这 `18` 笔收益是不是被 `2026-02` 少数几天包办，还是在 `2026-01 / 2026-02 / 2026-03` 至少保持同向、只是厚薄不同；必要时补 `non-overlap` / 月份分层的最小检查。

## 本轮结论（一句话）
**Rank 187 / BTCUSDT 15m late-session path-shape swing 首轮 P2 admission 维持 `keep_P2`：canonical `h32_k3` pocket 在 BTC 上仍有 `18` 笔、gross `+0.4628%/trade`、扣 `6bps` 后约 `+0.4028%/trade` 的厚度，而 ETH 的 same-time transfer proxy 未出现反向打脸；因此它已足够继续留在 P2，但 cross-asset 仍未强到可以直接升 P3，下一轴应收敛到 `time stability`。**
