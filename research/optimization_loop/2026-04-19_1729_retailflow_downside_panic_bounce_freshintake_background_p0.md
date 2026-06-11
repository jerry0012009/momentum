# bot3 optimization loop — retail-flow downside panic bounce fresh intake -> background/P0

- 时间：2026-04-19 17:29 UTC
- 对象：`research/quant_digests/2026-04-19_1526_retailflow-downside-panic-bounce-alpha.md`
- 动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮只回答的唯一问题
`downside momentum extreme × participation spike -> panic-bounce fade` 在 next-bar / 5m child execution 与统一成本下，是否仍保有不是单日极端事件硬撑的独立 after-cost 价值。

## 复核到的最小证据
直接复核 digest 引用的本地事件表与 summary：
- 产物：
  - `reports/artifacts/quant_digests/2026-04-19_hdm_retail_extreme_fade_events.csv`
  - `reports/artifacts/quant_digests/2026-04-19_hdm_retail_extreme_fade_downside_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_hdm_retail_extreme_fade_symbol_summary.csv`
- `15m`、`core4(BTC/ETH/SOL/LTC)`、`ret_z<=-2 & vol_z>=1`、downside-only long bounce：
  - hold `2 bars`: `n=372`, `gross=+8.89bps`, `net8=+0.89bps`, win `62.6%`
  - hold `4 bars`: `n=372`, `gross=+10.29bps`, `net8=+2.29bps`, win `61.3%`
  - hold `8 bars`: `gross=+6.74bps`, `net8=-1.26bps`
- 但这条 pocket 不是稳定、多维一致的干净 after-cost pocket：
  - `15m hold4` 虽整体为正，但 symbol 维度已不一致：`BTC +2.19`, `LTC +1.20`, `SOL +7.55`, `ETH -1.07 net8(bps)`。
  - month 维度也不闭合：`2026-02 net8=-15.42bps`，`2026-03 net8=+6.46bps`，`2026-04 net8=+7.74bps`；换成更贴近“next-bar bounce”的 `hold2` 时，`2026-04` 又回到 `net8=-2.11bps`。
  - `5m` child execution 层在同样 `core4 + downside-only + ret_z<=-2 & vol_z>=1` 下没有保住统一 `8bps` 后正净值：
    - hold `3 bars`: `gross=-2.39bps`, `net8=-10.39bps`
    - hold `6 bars`: `gross=+1.77bps`, `net8=-6.23bps`
    - hold `12 bars`: `gross=+6.06bps`, `net8=-1.94bps`
  - `5m` 子层还出现明显时间集中：`2026-03` 仅 `20` 个事件时是正的，但 `2026-04` 的 `260` 个事件在 `3/6/12` bars 下分别约 `net8=-13.26/-9.21/-2.21bps`。

## 为什么这轮直接收口，而不是 keep_P1
这条线确实给出了一个有意思的方向性负面/正面拆分：`upside short-fade` 明显应 veto，而 `15m downside-only` 母信号在 `core4` 上仍能看见薄正 gross 到薄正 net 的 bounce 余量。

但按本轮 first verdict 的唯一 blocker 来看，它还没有诚实保住“可独立承接”的 after-cost pocket：
1. 真正更接近执行层的 `5m child` 没有在统一 `8bps` 下转正；
2. `15m` 母信号只能在 `hold4` 这种较宽 time-stop 下保留薄 net，而更贴近 next-bar bounce 的 `hold2` 在最新月份已失效；
3. cross-asset 也没有闭合成稳定 core4 共识，`SOL` 明显更强、`ETH` 仍为负。

因此当前更像“一个值得记住的 raw-alpha 方向提示（只做 downside panic，不做 upside short）”，还不是已经保住独立 survivor 资格的 front object。

## 本轮 verdict（写回 runtime 的一句话）
`downside panic-bounce` 的 first verdict 已诚实收口：`15m core4 downside-only` 虽在 `hold4` 保留薄 `net8≈+2.29bps`，但 `5m child execution` 在统一 `8bps` 下 `3/6/12` bars 全部为负、`hold2` 最新月份也转负，且强度主要偏向 `SOL` 而非稳定 core4 共识，因此本轮直接收口 `background/P0`。
