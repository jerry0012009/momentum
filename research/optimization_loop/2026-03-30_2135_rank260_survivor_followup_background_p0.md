# Rank 260 / perp-perp funding diff × net-EV hurdle — survivor 唯一 follow-up 收口回 background/P0

- 时间：2026-03-30 21:35 UTC
- 执行者：bot3 auto 13m loop
- 对象：`Rank 260 / perp-perp funding diff × net-EV hurdle`
- 本轮动作：survivor 唯一 decisive follow-up
- 结论：`唯一 follow-up 用尽，回 background/P0`

## 本轮要回答的唯一问题
按 `BTC / ETH / SOL × Binance / Bybit / OKX` 的 funding windows 回放后，这条 same-underlier cross-venue 双 perp funding differential，在统一 `z-score + net_ev > 0 (+ quote/depth veto 只会更严)` 口径下，到底是可持续 admission 候选，还是只是极低频 funding dislocation pocket？

本轮结论是：**它更像极低频尾部事件 pocket，不足以进入 P2 admission。**

## 本轮新增证据
新产物目录：
- `reports/artifacts/rank260_perp_perp_netev_followup_20260330/summary.json`
- `reports/artifacts/rank260_perp_perp_netev_followup_20260330/summary.csv`
- `reports/artifacts/rank260_perp_perp_netev_followup_20260330/pair_window_details.csv`
- `reports/artifacts/rank260_perp_perp_netev_followup_20260330/raw_counts.json`

统计口径：
- 时间窗：`2025-03-30 ~ 2026-03-30`
- 标的：`BTC / ETH / SOL`
- venue：`Binance / Bybit / OKX`
- taker fee：Binance `4bps` / Bybit `6bps` / OKX `5bps`
- slippage：`2bps/leg`
- latency：`0.5bps total`
- inventory risk：`1bps total`
- notional：`50,000 USD`
- z-score lookback：`30` 个 funding windows
- 入口门：`abs(z) >= 2` 且 `net_ev > 0`
- 说明：若在 **未加 quote/depth veto 前**，`z-score + net_ev > 0` 已几乎从不成立，则再加 `quote/depth veto` 只会进一步降低频率，不会把它救成 admission 候选。

## 关键结果
### 1) BTC：三组 venue pair 全部 0 个过线窗口
- `BTC / binance-bybit`：`507` 个样本，`z + net_ev > 0` 为 `0`
- `BTC / binance-okx`：`43` 个样本，`0`
- `BTC / bybit-okx`：`100` 个样本，`0`
- 其中最好的一组 `binance-bybit`，历史最大绝对 spread 也只有 `2.4131 bps / 8h`，离 breakeven `15.5 bps / 8h` 很远。

### 2) ETH：三组 venue pair 也全部 0 个过线窗口
- `ETH / binance-bybit`：`507` 个样本，`0`
- `ETH / binance-okx`：`43` 个样本，`0`
- `ETH / bybit-okx`：`100` 个样本，`0`
- ETH 最接近的一组 `binance-bybit`，历史最大绝对 spread `12.7719 bps / 8h`，仍低于 breakeven `15.5 bps / 8h`；最佳 `net_ev` 也还是 `-13.64 USD`。

### 3) SOL：只有 1 个窗口勉强过线，但频率低到不能支撑 admission
- `SOL / binance-bybit`：`507` 个样本里，只有 **1 个** 窗口满足 `z + net_ev > 0`，过线率仅 `0.197%`
- 那个唯一窗口是：`2025-10-11 00:00 UTC`
  - spread `19.7239 bps / 8h`
  - z-score `22.72`
  - `net_ev = +21.12 USD`
- `SOL / binance-okx`：`43` 个样本，`0`
- `SOL / bybit-okx`：`100` 个样本，`0`

换句话说，在这套 taker-first、50k 名义本金的诚实口径下，**9 组 asset×venue pair 里只有 1 组出现过 1 次过线窗口，其余全是 0。**

## 为什么这足以收口回 background/P0
1. **它不是“稀疏但仍能 admission”的级别，而是“几乎完全不出现”。**
   如果近 12 个月里 `BTC / ETH` 全部是 0、`SOL` 也只是 1/507，说明这条线更像极端 funding dislocation 的尾部事件，而不是可以进入 `P2` 去补 time/parameter/honesty admission 的前排候选。

2. **本轮 survivor follow-up 的核心问题已经被直接回答。**
   上轮留下的问题是：它到底是可持续 admission 候选，还是仅属极低频事件 pocket？
   这次统计已经足够回答：**是后者。**

3. **再补 quote/depth veto 不会改变方向。**
   本轮还没做逐窗口历史盘口 veto，但这不是遗漏主 blocker；因为在更宽松的 `z-score + net_ev > 0` 口径下，过线窗口已接近零。加入 `mid spread / top-of-book depth / quote stability` 只会让过线率更低，不会把它从 `background-ready` 救成 `P2-ready`。

## 改变系统认知的一句话
**Rank 260 的 survivor 唯一 follow-up 已回答关键出口问题：近 12 个月 `BTC/ETH/SOL × Binance/Bybit/OKX` 里，统一 `z-score + net_ev > 0` 口径下只有 `SOL binance-bybit` 出现过 `1` 次过线窗口（`0.197%`），其余全部为 `0`，因此这条线应被定格为极低频 funding dislocation pocket，而不是可持续 P2 admission 候选。**

## 最终 verdict
- `Rank 260：唯一 follow-up 用尽，回 background/P0`
- 不进入 `P2`
- 不占用 survivor 槽位
