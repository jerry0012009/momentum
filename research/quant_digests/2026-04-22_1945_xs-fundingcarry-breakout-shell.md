# 别把 `Crypto-Stat-Arb` 只读成“三因子练习册”：对 short-cycle crypto desk，更该先拆的是「liquid-perp cross-sectional funding carry × breakout net-bias」这条完整 raw alpha 壳

- 时间：2026-04-22 19:45 UTC
- 类型：2024 GitHub repo + blog source audit（`readme.md` + *Crypto Stat Arb: Quantifying & Combining Alphas*）+ Binance USDⓈ-M public-data portability probe（10 liquid majors，`8h` parent / `15m` child-exec 解释口径，`2025-12-01 ~ 2026-04-22`）
- 主题类型：raw alpha
- 基础 alpha：在 liquid perps 横截面里，**近期 funding 更高的合约，下一结算窗更容易继续相对跑赢 funding 更低的合约**；breakout 不是 alpha 本体，而是给组合一个 time-series net-bias overlay
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/carry/funding/breakout/momentum/liquid-perp/binance-perpetual/8h/15m/repo/public-data/cost/risk
- 证据类型：repo 规则骨架 + public-data first probe

## 1) 这次看了什么

这轮看的是：

- **Author**：Ryan Chew
- **Year**：2024
- **Title**：Crypto Stat Arb
- **Venue**：GitHub repo + accompanying research note
- **DOI**：N/A
- **Readable URL**：<https://analytic-musings.com/2024/03/10/crypto-stat-arb-I/>
- **Repo URL**：<https://github.com/ryanczm/Crypto-Stat-Arb>
- **Raw README**：<https://raw.githubusercontent.com/ryanczm/Crypto-Stat-Arb/master/readme.md>

repo 的核心不是“carry/momentum/breakout 都来一点”，而是把一个**可直接交易的完整壳**写清楚了：

- universe：按 `30d rolling dollar volume` 选 top 30 Binance perps；
- features：`carry = 最近 24h funding`，`momo = 10d return`，`breakout = 离 20d 高点有多近`；
- 组合：`0.5 carry + 0.2 momentum + 0.3 breakout`；
- 归一化：每日按 `abs(weight)` 归一到 1；
- 解释口径：carry / momentum 是横截面排序信号，breakout 更像给组合加 time-series 倾斜。

## 2) 先回答一句：base alpha 是什么？

> **base alpha = cross-sectional funding carry continuation。**

也就是：在同一批 liquid perps 里，**funding 更高的那一边，下一结算窗更容易继续相对更强**。这和我们最近常写的 `basis / perp-vs-spot convergence` 不一样；这里不是赌回归，而是把 funding 当作**横截面强弱排序器**。

所以这篇东西是 `raw alpha`，不是纯 overlay。`breakout` 在这套壳里更像 **net-bias / regime tilt**，不是第一位的 base alpha。

## 3) first probe：方向上更像 continuation，但常规 taker 化太薄

我先不照搬 repo 的日频 top30 全市场，而是做一个更贴 desk 的最小 portability probe：

- 标的：`BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK/AVAX/LTC`
- 频率：每次 funding 结算点做一次横截面排序（`8h` parent）
- 交易：`long highest funding / short lowest funding`，持有下一个 `8h`
- 对照：同样也测 `reversal` 反向版本

对应产物：
- `reports/artifacts/quant_digests/2026-04-22_xs_funding_carry_probe.py`
- `reports/artifacts/quant_digests/xs_funding_carry_probe_summary_2026-04-22.csv`
- `reports/artifacts/quant_digests/xs_funding_carry_probe_trades_2026-04-22.csv`
- `reports/artifacts/quant_digests/xs_funding_carry_probe_assets_2026-04-22.csv`

最关键的数字：

- `183` 次事件里，**repo-faithful continuation** 版本平均约 `+1.01 bps/8h`，简单累计约 `+1.85%`，`Sharpe ≈ 0.44`
- 但粗扣一组多空 round-trip `8 bps` 后，平均约 **`-6.99 bps/笔`**，累计约 **`-12.79%`**
- `reversal` 版本 gross 约 **`-1.01 bps/8h`**，说明**方向上更像 continuation，不像均值回复**
- 高低 funding 的平均 spread 只有 **`1.88 bps`**；最近更活跃的 funding 分位主要集中在 `SOL/AVAX/XRP/ADA`，`p90 |funding|` 约 `1.34 ~ 1.64 bps`

**人话结论**：这条 raw alpha 不是假的，方向上也没读反；但它在 liquid majors 上明显**薄到不适合无脑 taker**。更合理的定位是：`8h parent cross-sectional carry router`，下面接 `15m/5m maker-first child execution`，或者继续往更“rich-funding mid-cap”口袋里找厚度。

## 4) 为什么和当前 desk 有关

这条线值得进池子，不是因为它今天就能直接上线，而是因为它把 funding 从“又一个 delta-neutral 套壳”换成了另一个更 desk-friendly 的读法：

1. **它是 raw alpha，不只是 carry 解释层**：可以直接写成 `rank -> long strongest / short weakest -> hold -> rebalance`
2. **它能服务 15m/5m 执行层**：虽然 parent 节奏是 `8h`，但 entry 不必在结算瞬间粗暴追单，可以拆成 child execution
3. **它和已有 basis / pairs / xs momentum 库互补**：最近我们写了很多回归型 relative-value，这条是更偏 continuation 的 xs carry 排序

## 5) 策略拆解（必填）

- 方向属性：横截面 / relative-value / carry-continuation
- 基础 alpha：`funding rank high -> relative outperformance continuation`
- regime：优先在 funding spread 足够宽、liquidity 足够高的时段启用
- filter / veto：可加 `spread_funding_bps >= 门槛`、quote-volume / OI / funding-stability 过滤；breakout 只作 bias overlay
- risk / sizing / execution overlay：按 `abs(funding spread)` 和流动性分层 sizing；`15m/5m` maker-first 分批入场；若 funding spread 快速收敛或价差反向穿越则提早退出

## 6) 下一步怎么测（明确动作）

1. **把 fixed majors 升级成动态 top30 universe**：更贴 repo 原设定，先复刻 `30d rolling volume` 口径。  
2. **做 friction ladder**：`maker rebate / maker 0 / taker fallback` 三档，看 edge 是否只在 maker 化后能活。  
3. **补 breakout overlay A/B**：比较 `pure carry rank` vs `carry + 20d breakout tilt`，确认 breakout 到底是抬 Sharpe，还是只是在牛市里放大 beta。  
4. **把 8h parent 拆到 15m child execution**：结算后 `0~60m` 分 4 桶入场，比较 next-open/taker 与 VWAP/post-only 的净差。  
5. **往 richer pocket 扩样**：从 `SOL/AVAX/XRP/ADA/LINK` 这类 funding 更活跃币开始，而不是只盯 `BTC/ETH`。

## 7) 风险与保留意见

- repo 主体是 `2019-2024` 研究练习，不是 production-grade live strategy；
- 当前 probe 用的是 fixed-major + 8h close-to-close 简化口径，不等于真实成交后净值；
- funding 这条线天然不是 `15m` 逐 bar 主信号，硬伪装成 per-bar alpha 会失真；
- 当前最大问题不是方向错，而是**spread 太薄、成本太厚**。

## 8) 结论一句话

**`Crypto-Stat-Arb` 最值得收进池子的，不是“三因子拼一下”，而是把 funding 明确读成一条可独立复现的横截面 raw alpha：high-funding names tend to keep winning relative to low-funding names；只是 recent liquid-major transfer 显示它更适合作为 `8h parent router + 15m/5m maker-first child execution`，而不是直接 taker 化。**
