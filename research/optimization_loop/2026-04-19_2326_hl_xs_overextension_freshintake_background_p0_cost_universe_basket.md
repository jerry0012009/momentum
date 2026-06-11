# Rankless fresh intake收口：cross-sectional overextension top-vs-bottom fade -> background/P0

- 时间：2026-04-19 23:26 UTC
- 对象：`research/quant_digests/2026-04-19_1906_hl-xs-overextension-fade-alpha.md`
- 执行动作：fresh intake first verdict
- 目标 blocker：当前 `15m top1-bottom1 hold12` 的薄正 gross，在统一双腿成本、major-only universe 与 top1-vs-top2 basket 诚实检查后，是否仍保住可独立承接的 after-cost spread pocket
- 结论：**不能。该对象本轮直接收口 `background/P0`，不保留为 survivor，也不分配 Rank。**

## 本轮最小诚实检查
基于现成产物 `reports/artifacts/quant_digests/2026-04-19_hl_xs_overextension_15m_panel.csv`，直接按 spread 组合真实口径重算：
- spread 回报使用 `(long_leg_fwd - short_leg_fwd) / 2`，避免把双腿名义收益直接相加后高估 gross
- 统一成本口径：双腿 roundtrip 合计 `8bps`
- universe 检查：`all10`、`majors6(BTC/ETH/SOL/XRP/BNB/LINK)`、`core4(BTC/ETH/SOL/XRP)`
- 集中度检查：`top1-bottom1` 对比 `top2-bottom2 basket`
- 持有窗：`4 / 8 / 12` bars

## 关键结果
### 1) all10：最强 `hold12 top1-bottom1` 也只有 `gross≈+6.01bps`，`net8≈-1.99bps`
- `hold4`: `gross≈+2.79bps`, `net8≈-5.21bps`
- `hold8`: `gross≈+4.28bps`, `net8≈-3.72bps`
- `hold12`: `gross≈+6.01bps`, `net8≈-1.99bps`
- 月份均值还出现早期负值：`2026-02 hold12 mean≈-5.70bps`

### 2) majors6：缩到更贴近 production 的 pool 后仍无正 net
- `hold12 top1-bottom1`: `gross≈+5.02bps`, `net8≈-2.98bps`
- `hold8 top1-bottom1`: `gross≈+3.70bps`, `net8≈-4.30bps`
- 虽然月均都为正 gross（`2026-02/03/04 ≈ +7.22/+5.13/+4.67bps` for hold12），但全部低于统一 `8bps` 双腿成本

### 3) core4：进一步缩池后边际更薄
- `hold12 top1-bottom1`: `gross≈+3.80bps`, `net8≈-4.20bps`
- `hold8 top1-bottom1`: `gross≈+2.65bps`, `net8≈-5.35bps`
- `2026-04 hold12 mean≈+1.99bps`，说明更核心池并未留下可承接 pocket

### 4) top2-bottom2 basket：不是 strongest-only router 被平滑后更干净，反而更差
- `all10 hold12 top2-bottom2`: `gross≈+4.52bps`, `net8≈-3.48bps`
- `majors6 hold12 top2-bottom2`: `gross≈+3.27bps`, `net8≈-4.73bps`
- `core4 hold12 top2-bottom2`: `gross≈+2.23bps`, `net8≈-5.77bps`

## 为什么这一步会改变系统认知
原 digest 里的 `+12.04bps` 来自把 long/short 双腿 forward return 直接相减后未折算到等权 spread 资本口径；一旦改成更诚实的 `(long-short)/2` 组合收益，并统一按双腿 `8bps` 成本计，原本看起来像 `15m hold12` 的 after-cost pocket 其实整体不存在。

因此，这条线当前不能诚实回答成 `keep_P1`：
- 不是仅剩一个 child-execution blocker；
- 不是 major-only 缩池后变干净；
- 不是 top2 basket 可平滑承接；
- 也没有保住独立的 after-cost spread pocket。

## 本轮 verdict
- `cross-sectional overextension top-vs-bottom fade` 的 fresh intake first verdict：**直接收口 `background/P0`**。
- 不进入 survivor；不分配 Rank。
