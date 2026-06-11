# 别把 breakout 判成“越线就行”：单根 `body% + edge-close` breakout bar，更像 15m breakout-short / Fib / EMA 的 cheap conviction gate
- 时间：2026-03-22 08:58 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/breakout-bar/body-ratio/close-location/candle-quality/continuation/failure/filter/repo/crypto/15m
- 证据类型：工程经验 + 公共数据快检

## 1. 这次看了什么
这次没有再追一个更重的多条件模板，而是回头看 **突破发生的那一根 K 本身够不够像“真突破”**：`TheVision333/trading-bot` 在 retest 逻辑里要求突破/确认 bar 至少有像样实体，并把收盘压到蜡烛外侧；`Madrycrypto/fibo71-bot` 也把 confirmation candle 的 `body >= 50% range` 写成显式门槛。这个想法刚好卡在我们最近两条结论之间：**比“裸越线”更诚实，但比 `3 连动量 + body≥60% + 距离>0.5ATR` 的 strict BMS 便宜得多**。

## 2. 核心结论
- **一句话核心结论：** 真正值得继续跟踪的 breakout，不只是“过线了”，而是**突破这根 K 自己要有实体、并且收在外侧尾部**；否则更像 leak-through，不像 continuation。
- **它是怎么证明的：** 证据主要来自两个开源仓库的规则设计，再加一轮 BTC/ETH/SOL 15m 公共数据快检；不是论文统计显著性结论，而是“工程规则 + 最小代理验证”。
- 我用 Binance USDⓈ-M 15m 公共 K 线做了一个 **120 天、BTC/ETH/SOL、20-bar breakout 代理快检**。若只保留 `body_pct >= 0.50` 且 long 收在区间上 30%、short 收在下 30% 的 breakout bar，**样本保留 61.9%**（2892 → 1791），不是那种会把交易数砍光的门。
- 这个 gate **没有把 proxy 直接翻正**，但把整体 `4-bar` 成本后均值从 **-9.4bps 改善到 -7.8bps**，同时把 **4-bar 回到突破位内的 re-entry rate 从 56.3% 降到 52.1%**。说明它更像一个便宜的 failure-veto，而不是独立 alpha。
- **short 侧更值得优先测。** pooled short 的 `4-bar` 成本后均值从 **-6.2bps 改善到 -3.5bps**，re-entry rate 从 **54.1% 降到 49.3%**；这和我们当前 `breakout-short follow-up` 正在收口的方向最贴。

## 3. 为什么和当前项目有关
- **对 `V3 final-verdict / breakout-short follow-up`：** 这相当于给“第一脚跌破/涨破”补一个最便宜的 bar-quality verdict。先过滤掉“刚好越线但实体很虚”的 break，再去看 post-break path，会比先堆更复杂的路径条件更省。
- **对 `Fibonacci confirmation / retest_hold`：** Fib 腿不该从软绵绵的 leak-through 开始画。只有 breakout leg 本身够硬，后面的回踩守住才更像真的 retest_hold，而不是把噪声 swing 画成 Fib。
- **对 `EMA / PSAR raw alpha focus`：** EMA/PSAR 不一定要自己生方向；它们更适合继承一个“有实体 + 收在边缘”的确认 bar。也就是说，这个想法更像 raw alpha 的 admission layer，而不是替代 trigger。
- 如果问“为什么这轮值得先做它，而不是继续发散新题”，答案很简单：**它正好填补了 `裸 break 太松` 和 `strict BMS 太紧` 之间的空位**，而且对三条收口线都能直接复用。

## 4. 可复刻的最小实验
- **研究假设：** 在 15m crypto 上，突破 bar 若满足 `body_pct >= 0.50` 且收盘位于本 bar 外侧 30% 区间（long `CLV >= 0.70`，short `CLV <= 0.30`），后续 continuation 更稳定、回到突破位内的概率更低。
- **一个可计算定义：**
  - `body_pct = abs(close-open)/(high-low)`
  - `clv = (close-low)/(high-low)`
  - long breakout quality：`body_pct>=0.5 and clv>=0.7`
  - short breakout quality：`body_pct>=0.5 and clv<=0.3`
- **最小回测切口：** 先接到当前三条线里最便宜的版本：
  1. `breakout-short`：只在首次跌破 bar 质量达标时，才允许进入后续 follow-up / final-verdict 分支；
  2. `fib retest_hold`：只给“质量达标的 breakout leg”生成 Fib anchor；
  3. `EMA/PSAR`：只在 reclaim/continuation bar 质量达标时放行 raw trigger。
- **样本建议：** BTC/ETH/SOL perp，15m，近 180d；先做 long/short 分拆，不要合池看均值。
- **最该先看 2 个指标：**
  1. `t+4 / t+8` 的 signed return 或 excess return；
  2. `N-bar re-entry rate`（突破后 N 根内是否重新收回 level 内）。
- **本轮代理文件：** `reports/artifacts/quant_digests/breakout_bar_quality_proxy_20260322/comparison.csv`、`summary.csv`、`event_log.csv`。

## 5. 风险与保留意见
- 这轮快检用的是 **20-bar breakout proxy**，不是 desk 当前精确定义的 `V3 / Fib / EMA` 触发器，所以只能证明“这个 bar-quality 维度值得接入”，不能证明它已经是最终可上线参数。
- 它和 3/19 的 `CLV` 笔记、3/20 的 strict BMS impulse 有亲缘关系，但这次的价值在于：**把信息压缩到“单根 breakout bar 的便宜判决”**，避免再走向过稀疏。
- 阈值不一定多空对称；从这轮结果看，**short 侧更有希望**，long 侧更像轻减亏，不一定值得同权部署。
- 成本后均值仍为负，所以别把它包装成 standalone alpha；更诚实的定位是 **entry veto / continuation confirmation / Fib leg admission**。

## 6. 来源
- TheVision333. (2026). *trading-bot*. GitHub.
- Readable URL: `https://github.com/TheVision333/trading-bot`
- Repo URL: `https://github.com/TheVision333/trading-bot`
- 相关文件：`strategy/retest_signals.py`

- Madrycrypto. (2026). *fibo71-bot / BMS Fibo Liquidity Strategy*. GitHub.
- Readable URL: `https://github.com/Madrycrypto/fibo71-bot/blob/main/README_BMS_STRATEGY.md`
- Repo URL: `https://github.com/Madrycrypto/fibo71-bot`

- Binance. (2026). *USDⓈ-M Futures API Docs – Kline/Candlestick Data*.
- Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
