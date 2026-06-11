# Rank 347 / adaptive 2-SMA walk-forward perp trend survivor follow-up -> background / P0

- 时间：2026-04-06 05:22 UTC
- 对象：`Rank 347 / adaptive 2-SMA walk-forward perp trend`
- 槽位：`Surviving candidate slot`
- 本轮动作：执行唯一一次决定性 follow-up，直接回答 `BTC/ETH × 5m/15m × fixed-vs-walk-forward × slow-window` 在显式 after-cost 口径下是否仍保留可迁移 baseline
- 结论：`background / P0`

## 本轮先回答结论
`Rank 347` 的 **slow-window 2-SMA 趋势壳并没有在本轮诚实 follow-up 里压出“跨 `BTC/ETH`、跨 `5m/15m`、且 walk-forward 后仍保留”的 after-cost baseline**：
- `5m` 上，为了绕开 Hyperliquid `candleSnapshot` 的单次约 `5000` bar 上限，使用最近约 17 天数据做 **`10d train / 3d test` honest walk-forward**；结果 `BTC` 与 `ETH` 两边都为负；
- `15m` 上，用最近约 120 天数据做 **`30d train / 7d test` honest walk-forward`**，`BTC` 为负、`ETH` 为正；
- 对照的 **fixed global best** 虽然在若干样本窗里还能显得不错，但那本质上是带 lookahead 的对照，不够当 admission 证据。

所以这条对象当前最诚实的系统结论不是升 `P2`，而是：
**它可以继续留作“单资产 perp 趋势 baseline 的一个研究备忘”，但本轮唯一 survivor follow-up 用尽后，证据仍不足以把它保留在前排，应直接退回 `background / P0`。**

## 本轮补了什么证据
### 1) `5m`：honest walk-forward 没有保留 baseline
使用 Hyperliquid 公开 `5m` K 线，显式按 `1.5bps/side` 扣费，并把候选限制在 intake 首判 already implied 的 **slow-window bias**（`slow ∈ {144,192,288,384}`）里。

由于单次 API 只能拿约 `5000` bars，`5m` 只能做最近约 17 天的诚实滚动检验，因此采用：
- `train = 10d`
- `test = 3d`
- walk-forward 每次在训练窗里重选 `(fast, slow)`，再只看后续 OOS 3 天

结果：
- `BTC 5m`：
  - segment1 选到 `24/144`，OOS `cumret = -6.99%`
  - segment2 选到 `48/144`，OOS `cumret = -1.25%`
  - 合并后 `cumret = -8.15%`，Sharpe 明显为负
- `ETH 5m`：
  - segment1 选到 `48/288`，OOS `cumret = -6.82%`
  - segment2 选到 `16/288`，OOS `cumret = -3.28%`
  - 合并后 `cumret = -9.87%`，Sharpe 明显为负

这一步已经足够回答一个关键问题：
**当参数必须诚实地顺着时间往前走时，`5m` 上这条壳目前并没有显示出可以迁移的成本后 baseline。**

### 2) `15m`：只出现单边复制，不够构成跨资产 baseline
在 `15m` 上，可以从 Hyperliquid 单次拿到约 120 天，故采用：
- `train = 30d`
- `test = 7d`
- 同样限制 slow-window bias，并按 walk-forward OOS 检验

结果：
- `BTC 15m` honest walk-forward：
  - 合并 `cumret = -3.38%`
  - Sharpe 为负
  - 3 个 OOS segments
- `ETH 15m` honest walk-forward：
  - 合并 `cumret = +4.96%`
  - Sharpe 为正
  - 3 个 OOS segments

这说明它最多只能暂时被表述成：
**“在当前近端样本里，`ETH 15m` 似乎还有一点可用 pocket，而 `BTC 15m` 与两边 `5m` 并没有同步复制。”**

这还远远不到 `P2` admission 想要的“跨资产 / 时间 / 参数 / honesty 都至少像个 baseline”的程度。

### 3) fixed best 还能亮，不等于 walk-forward 后也成立
对照里仍能看到一些看上去不差的 fixed 组合，例如：
- `BTC 15m` 的全样本对照 best `16/288`，样本内 `cumret ≈ +7.07%`
- `ETH 15m` 的 honest walk-forward 也有一段正 pocket

但这轮 policy 要的不是“还能不能挑出一组看起来顺眼的窗口”，而是：
**把参数重选、跨资产与成本口径都摆正后，它有没有变成值得保留在前排的诚实 baseline。**

这一问的答案，本轮更接近 **没有**。

## 会改变系统认知的话
`Rank 347` 的唯一 survivor follow-up 已经诚实收口：`walk-forward + slow-window bias` 在 `BTC/ETH × 5m/15m` 上没有形成可迁移的 after-cost baseline，结果表现为 `5m` 两边都负、`15m` 只有 `ETH` 单边保留 pocket，因此对象不升 `P2`，直接退回 `background / P0`。

## 产物
- `reports/artifacts/quant_digests/adaptive_2sma_20260406/cross_asset_time_portability_summary.json`
- `reports/artifacts/quant_digests/adaptive_2sma_20260406/cross_asset_time_portability_followup_120d.json`
- `reports/artifacts/quant_digests/adaptive_2sma_20260406/btc_15m_wf_honest_120d.json`
- `reports/artifacts/quant_digests/adaptive_2sma_20260406/eth_15m_wf_honest_120d.json`

## 对 runtime 的直接影响
- `Rank 347` 用尽唯一 `Surviving candidate` follow-up 预算；
- 对象不进入 `P2`，直接退回 `Background pool`；
- `Surviving candidate slot` 清空，等待 bot2 下一轮按 policy 重新排班。
