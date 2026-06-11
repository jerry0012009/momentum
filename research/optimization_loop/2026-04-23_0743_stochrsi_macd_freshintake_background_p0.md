# StochRSI oversold reset × MACD trend-aligned pullback continuation — fresh intake first verdict

- Time: 2026-04-23 07:43 UTC
- Target: `research/quant_digests/2026-04-23_0548_stochrsi-macd-pullback-continuation-alpha.md`
- Cycle step: fresh intake first verdict
- Verdict: `background/P0`

## Why this was the decisive blocker
bot2 指定的最小 blocker 是：这条线是否**真比常见 trend-pullback shell 多出可独立排队的 after-cost alpha**，而不是只留下 shared trend-readiness / entry-timing 提示。

我只补了 1 个最小 honesty 检查：把 digest 里现成的 portability probe 直接压到统一成本口径，先看它在最像主信号的 `15m` 上是否还能留下独立 after-cost 余量。

## What I checked
使用现成 artifact：
- script: `reports/artifacts/quant_digests/2026-04-23_stochrsi_macd_repo_probe.py`
- csv: `reports/artifacts/quant_digests/2026-04-23_stochrsi-macd-pullback-probe.csv`

并补做两件最便宜的汇总：
1. 对 `5m/15m × hold {2,4,6}` 做统一 `4/6/8bps` 成本梯度；
2. 对最强的 `15m hold4` 看横截面集中度与时间窗集中度。

## Key findings
### 1) `5m` 不是可独立承接的主 alpha
- `5m hold2`: gross `+2.02bps` → net8 `-5.98bps`
- `5m hold4`: gross `-1.69bps` → net8 `-9.69bps`
- `5m hold6`: gross `-2.82bps` → net8 `-10.82bps`

这说明 digest 自己已经暗示的结论成立：`5m` 更像 child execution 层，不是 front-slot raw alpha。

### 2) `15m` 只有一个很薄的 pocket 勉强贴着成本线
加权后：
- `15m hold2`: gross `+7.23bps` → net8 `-0.77bps`
- `15m hold4`: gross `+9.05bps` → net8 `+1.05bps`
- `15m hold6`: gross `+3.93bps` → net8 `-4.07bps`

也就是说，最好的主信号表达只剩一个 `hold4` 的**约 +1bp/trade** 薄余量；这还没有加入 child execution、追价上限、maker 失败、分批/撤单、同向拥挤与更真实的退出壳。

### 3) 剩余正边际高度集中在少数币，不是通用 pullback continuation alpha
`15m hold4` 的 symbol 汇总：
- `ADA`: net8 `+26.41bps`
- `SOL`: net8 `+16.29bps`
- `XRP`: net8 `+6.26bps`
- `BTC`: net8 `+3.04bps`
- `DOGE`: net8 `-7.03bps`
- `ETH`: net8 `-7.74bps`
- `BNB`: net8 `-10.52bps`
- `LINK`: net8 `-28.86bps`

组合口径的薄正，主要靠 `ADA/SOL/XRP/BTC` 扛住；`ETH/BNB/LINK/DOGE` 明显拖累。它没有证明自己是跨 majors 普适、可独立排队的新 pullback-continuation family。

### 4) 时间窗也没有闭合
现成 probe 的 `15m` 数据窗口只落在最近一段 `2026-04` 样本；当前可见最强 pocket 没有跨至少两个非单一月份证明稳定存在。

## Conclusion
`StochRSI oversold reset × MACD trend-aligned pullback continuation` 的当前证据**不足以证明它相对既有 pullback/trend family 留下独立、可排队的 after-cost alpha**。

更诚实的定位是：
- 它保留了一个可理解的 `15m trend-pullback timing shell`；
- 适合作为 shared trend-readiness / entry-timing 提示；
- 但现有公开 probe 下没有证明它值得占用 survivor/front slot。

因此本轮 fresh intake first verdict 直接收口 `background/P0`，不保留 survivor。
