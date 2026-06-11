# 别把 continuation 写成“第一根 break 出去就够了”：`2-bar outside-range follow-through` 更像 breakout-short / Fib / EMA-PSAR 的 shared persistence gate
- 时间：2026-03-19 14:48 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/follow-through/two-bar-outside-range/path-persistence/continuation/confirmation/repo/crypto/15m
- 证据类型：repo 代码规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **Carlos Rodriguez (2025) 的 `MQL5-Trading-Bot`**。我没有照搬它整套 SMC + LSTM + kill-zone 框架，而是只抽其中最适合当前 desk 的一条旁支：

- `FT`：最近两根收盘都还在“更早两根 bar 的区间外”；
- `SFT`：在 `FT` 基础上，再要求两根同向实体推进，且至少一根是明显扩张 bar。

翻成我们更朴素的 15m 语言，其实就是一句话：
**别急着把“第一根破位”当成 continuation verdict；先问第二根有没有继续站在外面。**

这轮值得做，是因为最近几篇 digest 已经补了 `penetration / base-age / level-memory / wick rejection`，但还缺一块最直接的 path 问题：**第一根出去之后，路径有没有延续，而不是立刻虚掉。**

## 2. 核心结论
1. **一句话核心结论**：`2-bar outside-range follow-through` 更像三条收口线共用的 **path-persistence admission gate**，不是新 alpha；它回答的是“这次 break/reclaim 后有没有第二脚继续站稳”。
2. **一句话证明方式**：repo 把 `FT/SFT` 明确写成可编码规则（两根收盘持续在前一段小区间外；`SFT` 再加同向实体 + 扩张 bar）；我再用 Binance Futures 公开 `BTC/ETH/SOL 15m`、近 `120d` 做 Donchian 事件代理快检。
3. 代理结果（`next-bar open` 进，持有 `4` 根，round-trip 成本 `12bps`）显示：
   - **全部 single-break 事件**：`2922` 笔，`win4 = 36.8%`，`mean net = -9.75 bps`
   - **FT-or-better**：`1325` 笔，保留率 `45.3%`，`win4 = 39.2%`，`mean net = -4.80 bps`
   - **SFT-lite**（去掉 repo 里较难代理的 fractal sweep / kill-zone，仅保留两根同向 + 扩张）：`918` 笔，保留率 `31.4%`，`win4 = 39.8%`，`mean net = -3.06 bps`
4. 分方向看也一致：
   - **long**：`-12.55 bps -> -6.02 -> -3.12`
   - **short**：`-7.04 bps -> -3.76 -> -3.00`
5. 诚实读法不是“它已经变成 standalone alpha”，而是：**第一根 break 先给观察票，第二根还站在外面才给 continuation 正式票。**

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：下破后若第二根收盘没继续留在前箱体外，follow-up 就该降级；这比只看“第一根破了没”更像 final verdict。
- **Fibonacci confirmation / retest_hold**：Fib reclaim 之后，不该只问“有没有收回线内上方”，还要问**接下来两根能不能继续守在 reclaim box 外**；守不住，就更像假 hold。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 给方向很快，但最怕第一脚突破后路径塌掉；`2-bar outside-range` 是比再堆一个新指标更便宜的 persistence gate。

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：5m / 15m
- 本轮产物：
  - `reports/artifacts/quant_digests/2026-03-19_two_bar_followthrough_proxy_trades.csv`
  - `reports/artifacts/quant_digests/2026-03-19_two_bar_followthrough_proxy_summary.csv`
  - `reports/artifacts/quant_digests/2026-03-19_two_bar_followthrough_proxy_by_side.csv`
  - `reports/artifacts/quant_digests/2026-03-19_two_bar_followthrough_proxy_summary.json`

### 4.2 最小可复现实验口径（建议先做这个）
把三条 archetype（`breakout_short / fib_retest_long / ema_psar_long`）统一接一层 `follow-through state`：
1. 先定义一个父区间：`parent_high/low = max/min(signal 前 2 根)`；
2. **FT**：信号 bar 后两根收盘都仍在父区间外；
3. **SFT-lite**：FT + 两根同向实体 + 至少一根 `range >= 1.5 * avg_range_10`；
4. 做三臂对照：
   - A：baseline
   - B：第一根 break 先半仓，只有 FT 才加到满仓
   - C：只有 SFT-lite 才放行，其他全 veto

首轮只看 4 个指标：
- `post_cost_expectancy`
- `trade_count_retention`
- `false_follow_ratio`（入场后 4 bars 内被打回父区间）
- `setup-wise contribution`

**最值得先测的不是 hard gate，而是 `0.5x -> 1.0x` 的两段式升仓**：这样能直接回答“第二根 persistence 到底值不值得加码”，也更贴当前 desk 的收口线。 

## 5. 风险与保留意见
- 本轮快检只代理了 repo 的 `FT / SFT` 路径骨架，没有把 `fractal sweep / premium-discount / kill-zone` 一起复刻；
- 结果仍是成本后负值，说明它更像“少做错单”的过滤层，不是已成立的主信号；
- 保留率从 `100%` 降到 `45.3% / 31.4%`，要防止把“少交易”误读成“更强 alpha”；
- 真正值得继续的前提，是它在三条 archetype 上都能降低 `false_follow_ratio`，而不只是把样本砍薄。

## 6. 来源
1. **Rodriguez, C. (2025). _MQL5-Trading-Bot_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/carlosrod723/MQL5-Trading-Bot>
   - Repo URL: <https://github.com/carlosrod723/MQL5-Trading-Bot>
2. **关键说明：README 中的 `FT / SFT / NFT / CT` 四套路径定义**
   - Readable URL: <https://github.com/carlosrod723/MQL5-Trading-Bot/blob/main/README.md>
3. **关键实现：`MQL5/Experts/MyTradingBot.mq5`（`CheckFTSetup` / `CheckSFTSetup`）**
   - Readable URL: <https://github.com/carlosrod723/MQL5-Trading-Bot/blob/main/MQL5/Experts/MyTradingBot.mq5>
   - Raw URL: <https://raw.githubusercontent.com/carlosrod723/MQL5-Trading-Bot/main/MQL5/Experts/MyTradingBot.mq5>
4. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>
