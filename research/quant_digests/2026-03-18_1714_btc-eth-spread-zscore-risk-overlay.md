# 别把 continuation 失败都怪进场形状：更值得先测的是 BTC-ETH spread z-score 作为三条线共用 risk overlay
- 时间：2026-03-18 17:14 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/pairs-trading/cointegration/spread-zscore/risk-overlay/position-sizing/crypto/15m
- 证据类型：仓库代码 + 公开 OHLCV / 可快速复现实验

## 1. 这次看了什么
这次看的是 `eshan-kaul/PairsTrading-Crypto`（2022）的 notebook。它主线是配对交易，但对我们当前 desk 更有价值的旁支，不是“直接做 market-neutral 主策略”，而是把 `BTC-ETH` 的相对价差偏离度（spread z-score）降级成 **15m 的风险覆盖层**，给三条收口线统一做 `allow / reduce / veto`。

## 2. 核心结论
- **一句话核心结论**：对当前三条线，最值得先偷的不是配对交易本体，而是“当 `BTC-ETH` 相对价差进入极端偏离时，先降低或否决 continuation 仓位”。
- **一句话证明方式**：repo 在同一个 notebook 里把流程写成了可复刻链条：先做相关/协整筛选（Engle-Granger + Johansen），再构造 `spread = A2 - b*A1`（OLS 对冲比），最后用 `z-score` 阈值（示例为 ±1）触发信号；说明其可迁移价值在“偏离度量”本身，而不在某个神秘指标。
- 对我们当前阶段最有用的读法：把 spread z-score 当 **risk overlay / position sizing**，不是硬伪装成逐根 15m 的主入场信号。
- 这条线和今天已写的 OI / liquidation / VWAP 不冲突：它只用公开价格数据，成本低、上线快，适合作为 shared second-order filter。

## 3. 为什么和当前项目有关
- `V3 final-verdict / breakout-short follow-up`：当 `|z_spread|` 很高时，常见是“主币相对强弱在重配”，这类阶段 continuation 更容易被反抽；可先做 follow-up veto 或降仓。
- `Fibonacci confirmation / retest_hold`：Fib 给位置，但 spread z-score 可以回答“这个回踩是不是发生在跨主币失衡修复期”；若是，优先降置信度。
- `EMA / PSAR raw alpha focus`：EMA/PSAR 负责方向，spread 偏离负责拥挤/失衡风险提示；角色清晰，不和 entry trigger 打架。

## 4. 可复刻的最小实验
- **研究假设**：给三条 setup 加上 `BTC-ETH spread z-score` 风险覆盖层，能在不明显砍掉样本的前提下，降低 continuation 失败率与回撤。
- **数据源（公开可得）**：Binance USDⓈ-M `BTCUSDT`、`ETHUSDT` 15m Kline（公开 REST）。
- **最小可计算口径**：
  1. 在 15m 上计算 `ret_btc`、`ret_eth`；
  2. 滚动 OLS 得到 `beta_t`（如 288 bars）；
  3. `spread_t = ret_eth - beta_t * ret_btc`；
  4. `z_t = (spread_t - ma_96) / std_96`；
  5. 覆盖层规则：`|z_t|<=1` 全仓、`1<|z_t|<=2` 半仓、`|z_t|>2` 禁入新 continuation。
- **第一轮 bucket**：`base` vs `size-overlay` vs `hard-veto`。
- **最先看 4 个指标**：`post-cost expectancy`、`trade count retention`、`false-break/false-hold rate`、`max drawdown`。
- **下一步怎么测**：先固定 `BTC/ETH/SOL`、最近 `180d`、`next-bar open`、`no-overlap`，只回答一件事：`|z_spread|>2` 的 veto，是否能在 trade retention ≥70% 前提下，把三条线的成本后回撤和失败率同时压下去；若做不到，就不要继续美化成“跨币种智能风控”。

## 5. 风险与保留意见
- 该 repo 是教学型 notebook，不是生产级交易系统；结论可启发，但不能当成已验证实盘模板。
- 原仓库示例偏日频/较长窗口思路，直接搬到 15m 可能过噪；需滚动窗口敏感性检查。
- spread z-score 与已有 regime/filter 可能信息重叠，后续必须做 ablation，确认它不是“换名字重复过滤”。
- 这是 overlay，不是主信号；若把它升级成主入场条件，容易偏离当前三条线收口目标。

## 6. 来源
- Eshan Kaul. (2022). *Implementing the Pairs Trading Strategy on Crypto Markets* (GitHub notebook). Venue: GitHub. DOI: N/A.
  - Readable URL: <https://github.com/eshan-kaul/PairsTrading-Crypto>
  - Repo URL: <https://github.com/eshan-kaul/PairsTrading-Crypto>
  - Notebook URL: <https://raw.githubusercontent.com/eshan-kaul/PairsTrading-Crypto/main/Pairs%20Trading%20Strategy%20for%20Crypto%20Markets.ipynb>
  - Repo metadata snapshot: created `2022-07-07`, `12` stars at fetch time.
- Binance USDⓈ-M Futures API. *Kline/Candlestick Data*.
  - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
  - 用途：构造 `BTC/ETH 15m` spread z-score 风险覆盖层的最小可复现实验。
