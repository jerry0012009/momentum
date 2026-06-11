# 别把 anti-chop 继续写成单轴阈值：`MTF CHOP charged-up count` 在 15m 更像 `Fib retest_hold` 的 long-side veto，不是 breakout-short 的统一放行键
- 时间：2026-03-20 00:08 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/choppiness/anti-chop/mtf/regime/veto/risk-overlay/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 代理快检（公开行情）

## 1. 这次看了什么
主来源是 GitHub 仓库 **thibaulthenry/mtf-chop-index (2022)**。这个脚本把 CHOP（Choppiness Index）做成了多周期并行读数，并给出“charged-up”（进入高震荡）计数。

代码里有两个对我们 5m/15m 特别实用的点：
1) 它不是只看单一 TF 的 CHOP，而是同时看多条 TF（可静态指定，也可按当前 TF 倍数扩展）；
2) 它把“高震荡”做成计数对象（`>=1, >=2, ...`），天然适合当 **regime gate / veto layer**，而不是主入场信号。

> 注：该仓库 `request.security(..., lookahead=barmerge.lookahead_on)` 在实盘/回测里有前视风险，不能原样抄；本轮只借用“多周期 charged-count”这个思路。

## 2. 核心结论
- **一句话核心结论**：`MTF CHOP charged-up count` 目前更像 **Fib retest_hold 的 long-side veto**；对 breakout continuation（含 short follow-up）并未显示成统一放行键。
- **一句话证明方式**：在 BTC/ETH/SOL 15m（近 120 天）代理快检里，`charged_count>=2` 对 retest 样本显著更差（尤其 long），但对 raw breakout continuation 改善不明显。

代理快检关键读数（15m, forward=4 bars）：
1) **Retest-hold proxy**：`charged>=2` 的中位数约 **-20.69 bps**，`charged<=1` 约 **-2.93 bps**；fail rate **60.87% vs 53.05%**（n=23 vs 1785）。
2) **Retest long 子样本**：`charged>=2` 中位数约 **-31.80 bps**，`charged<=1` 约 **-2.93 bps**；fail rate **71.43% vs 53.49%**（n=14 vs 873）。
3) **Breakout continuation proxy（多空合并）**：`charged>=2` 与 `charged<=1` 差异不稳定（中位数都为负，且样本量严重不平衡：66 vs 2841），不支持把它升级成统一 admission gate。

## 3. 为什么和当前项目有关
这轮是继续帮三条线收口，不是开新坑：
- `V3 final-verdict / breakout-short follow-up`：当前证据不支持把 `charged_count` 当硬放行；最多当 **size-down / caution overlay**。
- `Fibonacci confirmation / retest_hold`：这是本轮最直接受益线。`charged>=2` 更像 **long retest veto**（先拒绝，少做“回踩看起来守住但后面磨死”的交易）。
- `EMA / PSAR raw alpha focus`：可作为上层风险覆盖（`charged>=2` 时降低 long 权重、收紧持仓时长），而不是把 EMA/PSAR 主触发替换掉。

## 4. 可复刻的最小实验
### 研究假设
在 15m，`MTF CHOP charged_count` 作为 veto（而非入场）会先改善 `retest_hold long` 的失败率与左尾，而不是直接提升所有 breakout continuation 的胜率。

### 一个可计算定义（最小版）
- 先算经典 CHOP（n=14）：
  \[
  CHOP = 100 * \log_{10}\left(\frac{\sum TR(1,n)}{HH_n-LL_n}\right) / \log_{10}(n)
  \]
- `charged` 定义：`CHOP >= 61.8`。
- `charged_count`：在 `{15m, 30m, 60m}` 中满足 charged 的 TF 数量。
- `veto`：`charged_count >= 2` 时，不开 `retest_hold long`（或降权到 0.5x）。

### 最小回测切口
- 资产：BTC/ETH/SOL perp
- 周期：15m（上层 MTF：30m/60m）
- 样本：近 120 天滚动
- 成本：`6/10 bps per side`
- 对照组：
  1) baseline（现有 retest_hold）
  2) baseline + `charged_count>=2` hard veto
  3) baseline + `charged_count` 仅做 size-down（比如 1.0x→0.5x）

### 最先看 3 个指标
1. `post_cost_return`
2. `fail_rate_4bars`
3. `left_tail_pnl_p5`

## 5. 风险与保留意见
- 该仓库是工程指标，不是审稿论文；证据强度来自“可读代码 + 本地复核”。
- 本轮 `charged>=2` 样本量偏小（尤其 retest-short），结论先按 **方向性证据** 看，不宜过度参数化。
- 原仓库使用 `lookahead_on`，实装必须改成 non-repaint 口径（`lookahead_off` + 严格右侧对齐）。

## 6. 来源
1. Thibault Henry. (2022). *mtf-chop-index*. GitHub Repository.  
   - Authors: Thibault Henry  
   - Year: 2022  
   - Title: MTF Choppiness Index  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/thibaulthenry/mtf-chop-index/main/indicator.pine  
   - Repo URL: https://github.com/thibaulthenry/mtf-chop-index
2. TradingView Support. (n.d.). *Choppiness Index (CHOP)*.  
   - Authors: TradingView  
   - Year: N/A  
   - Title: Choppiness Index (CHOP)  
   - Venue: TradingView Support  
   - DOI: N/A  
   - Readable URL: https://www.tradingview.com/support/solutions/43000501980-choppiness-index-chop/  
   - Repo URL: N/A
3. Binance Developers. (2026). *USDⓈ-M Futures REST API — Kline/Candlestick Data*.  
   - Authors: Binance  
   - Year: 2026  
   - Title: Kline/Candlestick Data API  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data  
   - Repo URL: N/A

---
### 附：本轮代理快检产物
- `reports/artifacts/quant_digests/mtf_chop_chargedup_veto_proxy_20260320/summary.csv`
- `reports/artifacts/quant_digests/mtf_chop_chargedup_veto_proxy_20260320/breakout_side_summary.csv`
- `reports/artifacts/quant_digests/mtf_chop_chargedup_veto_proxy_20260320/retest_side_summary.csv`
- `reports/artifacts/quant_digests/mtf_chop_chargedup_veto_proxy_20260320/breakout_events.csv`
- `reports/artifacts/quant_digests/mtf_chop_chargedup_veto_proxy_20260320/retest_events.csv`
- `reports/artifacts/quant_digests/mtf_chop_chargedup_veto_proxy_20260320/meta.json`
