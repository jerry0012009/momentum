# 别把 ETF 先行强度继续写成全天 shared gate：repo 里的 US close-window momentum，更像 BTC/ETH 15m 的 session-specific continuation confirm
- 时间：2026-03-23 04:49 UTC
- 类型：GitHub 仓库 + ETF 公共行情数据
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/etf/us-close/session/continuation/confirmation/veto/external-data/repo/crypto/5m/15m
- 证据类型：工程证据（公开 notebook + 公开数据 + 5m 验证）

## 1. 这次看了什么
这次主看 **GitHub 用户 BNeillDickey 在 2026-03-09 发布的 notebook 仓库**：它把 spot crypto 的 US equity open/close reversal、以及 **IBIT/FBTC/ETHA/FETH 在 US close 附近的 momentum** 放在同一套框架里回测，还专门用 5m 数据复核了 after-hours 结果。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得我们偷的，不是“再做一套 ETF 独立 alpha”，而是把 **US close 的 ETF tape** 当成 `BTC/ETH 15m continuation confirm / short-veto`，而不是全天共享 gate。
- **一句话说明它怎么证明：** 作者把 ETF 的 `15:30–16:00 ET` 信号窗、`16:00–17:00 ET` 持有窗冻结下来，和 spot crypto reversal 放在同一 notebook 中做同口径回测，并补了 after-hours 的 5m 验证。
- repo 里最干净、最可交易的结果，是 **ETF close-window momentum**：`15:30–16:00 ET` 信号、`16:00–17:00 ET` 持有，四只 ETF 合成组合 **SR=3.29（约 500 个交易日）**。
- 拆开看也不是单只基金偶然：**BTC ETF 组 SR=3.72**，**ETH ETF 组在上市后样本里 SR=4.17（398 天）**。
- after-hours 最佳窗在 60m 上看见 **SR=8.62**，但 repo 也老实承认这是粗粒度偏乐观；换到 5m 只剩 **SR=2.37（56 天）**。这反而说明：**close 附近的方向延续可信，但不能把 after-hours 神化。**
- 这和中小市值 spot crypto 的 US session reversal 恰好相反：说明 **ETF tape 更像“制度化资金继续推同方向”，而不是全市场普适的 15m 主信号。**

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：若 `15:30–16:00 ET` ETF basket 明显转强，`16:00–17:30 ET` 就不该继续把 BTC/ETH breakout-short follow-up 当默认可追；它更像 **short-side veto**。
- 对 `Fibonacci confirmation / retest_hold`：BTC/ETH 在 US close 附近若出现回踩守住，且 ETF tape 同向，才更像“真有后续买盘接力”，适合做 **confirmation / size-up**。
- 对 `EMA / PSAR raw alpha focus`：这条线最适合被放在 **session-specific overlay**，回答“US close 这段，裸 EMA continuation 到底该不该开更大、还是该缩”。
- 这题比继续磨单一 K 线参数更值钱，因为它**直接服务当前三条收口线里最难的那部分：post-break / post-reclaim 到底有没有 follow-through**，而且数据公开、5m 可拿、最小实验便宜。

## 3.5 策略拆解（必填）
- 方向属性：外部 cross-venue continuation confirm（带明显多空不对称）
- 基础 alpha：仍是 breakout-short / Fib retest_hold / EMA-PSAR 原有 15m 入场
- regime：仅限 `US close` 附近（优先 `15:30–17:30 ET`）
- filter / veto：ETF basket close-window return / z-score / direction alignment
- risk / sizing / execution overlay：同向加仓、冲突 veto、其余 half-size

## 4. 可复刻的最小实验
### 研究假设
把 `ETF close tape` 映射成 15m 的 session overlay 后，**BTC/ETH 的 long-side continuation 质量会变好，short-side 追空假延续会下降**；若只把它当全天 shared gate，效果会被稀释。

### 一个可计算定义
- 数据：Yahoo Finance / yfinance 的 `IBIT / FBTC / ETHA / FETH` 5m（不够长时退回 60m 做慢版），Binance BTC/ETH/SOL perpetual 15m。
- 先算 ETF basket：
  - `basket_ret_close = Σ(w_i * ret_i)`，`w_i` 可先用等权；若能稳定拿到成交额，再改成美元成交额权重。
  - 信号窗固定为 `15:30–16:00 ET`。
  - `close_tape_z = zscore_20d(basket_ret_close)`。
- 映射到 15m 执行层：
  - `close_tape_z > +0.75`：只放宽 BTC/ETH 的 Fib / EMA long continuation；对 breakout-short follow-up 默认 veto 或 half-size。
  - `close_tape_z < -0.75`：允许 short-side follow-up，long-side confirmation 缩仓。
  - 中性区间：不 veto，但不开 size-up。
- `SOL` 第一轮不要硬套成同等级强门；只把 `BTC+ETH ETF basket` 当弱 proxy，单独看 transferability。

### 最小回测切口
- 标的：BTC / ETH / SOL perpetual
- 周期：15m 主信号 + ETF 5m overlay
- 样本：近 180d（若 ETF 5m 历史不足，则补 60m 慢版验证）
- 执行：next-bar open，no-overlap
- 成本：6 / 10 / 15 bps per side

### 第一轮先看
- post-cost expectancy
- `false_follow_through_ratio`（尤其 short-side）
- trade retention（别靠砍单伪改善）
- BTC/ETH 与 SOL 的迁移差异

## 5. 风险与保留意见
- 这份 repo 是 **工程型 notebook**，不是同行评审论文；证据强度够启发，但还不是最终学术 verdict。
- ETF 结论主要落在 **post-launch 制度期**，样本不长，后续可能被参与者适应抹平。
- BTC/ETH ETF 对 SOL 的映射天然更弱，因此不应一上来当三线共享 hard gate。
- after-hours 的超高 SR 在 5m 上明显衰减，所以 desk 迁移时应优先相信 `US close confirm`，不要神化更晚的 after-hours 延续。
- 这类外部数据更适合做 `session overlay / veto / sizing`，不该硬包装成逐根 15m 主入场。

## 6. 来源
1. **BNeillDickey (2026). _Intraday Return Reversals and Momentum Around the US Equity Session in Cryptocurrency Markets_. GitHub repository / Jupyter Notebook.**
   - Authors / Org: GitHub user `BNeillDickey`
   - Year: 2026
   - Venue: GitHub Repository
   - DOI: N/A
   - Readable URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project
   - Repo URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project
   - Notebook URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project/blob/main/Intraday_Crypto_Reversal_Project.ipynb
2. **Yahoo Finance / yfinance ETF public bars（公开可得）**
   - Data source: Yahoo Finance Chart API / yfinance
   - Publicness: 公开可得
   - Update frequency: 分钟级（5m / 60m 可取，窗口受平台限制）
   - Readable URL: https://finance.yahoo.com/
3. **Binance USDⓈ-M Futures Kline API（最小迁移实验的数据源）**
   - Data source: Binance Developers
   - Publicness: 公开可得
   - Update frequency: 分钟级
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
