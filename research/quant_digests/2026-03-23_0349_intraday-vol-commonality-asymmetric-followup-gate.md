# 别把“跨币波动共振”写成 15m 的 shared 放行键：`intraday volatility commonality` 更像 breakout-short 的 asymmetric follow-up gate
- 时间：2026-03-23 03:49 UTC
- 类型：论文 + GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/final-verdict/follow-up/fibonacci/retest-hold/ema/psar/intraday-volatility/commonality/regime/filter/risk-overlay/crypto/15m
- 证据类型：论文证据 + 工程实现线索 + 本地公开数据代理快检

## 1. 这次看了什么
这轮主看 **Djanga, Cucuringu, Zhang (2023)** 的“intraday volatility commonality”方向，以及其配套仓库 `edjanga/crypto_volatility_forecasting_using_commonality_in_intraday_volatility`。对我们 desk 最有用的旁支，不是“做更复杂波动预测模型”，而是：

> 把“多币种是否同时进入高波动状态”当成 **15m follow-up 的状态读数**，先回答“现在这笔 continuation 值不值得继续”，而不是把它伪装成逐根主触发。

## 2. 核心结论
- **一句话结论**：`vol commonality` 在 15m 上不适合做三条线 shared allow gate，更像 **breakout-short follow-up 的偏空侧过滤/放行层**；对 Fib/EMA/PSAR 的 long 侧只够当轻量 size-down 或 veto 参考。  
- **一句话证明方式**：用 Binance USDⓈ-M 公共 15m K 线（BTC/ETH/SOL，120d）做最小代理快检：`next-bar open` 入场、持有 8 bars、双边 12 bps 成本，比较 `commonality_count<=1` vs `>=2` 的成本后表现。

关键数据点（本地最小快检）：
1. **BTC breakout-short follow-up 明显受益于高共振桶**：`mean_net_bp -15.09 -> -4.13`（改善 `+10.96bp`），`win_rate 0.32 -> 0.40`。  
2. **long 侧没有形成同等稳定增益**：BTC long `-10.42` vs `-10.81`（几乎无改善），说明它不是对称 shared gate。  
3. **跨资产 short 侧方向性改善并非“全币一致”**：在 `>=2` 高共振桶里，short 侧 `BTC/SOL` 改善、`ETH` 走弱，说明更像 setup-specific + symbol-aware overlay，而不是一刀切规则。

## 3. 为什么和当前项目有关
- **对 `V3 final-verdict / breakout-short follow-up`**：最直接。可把 `vol commonality` 挂在 FT/NFT 或 follow-up 判决前后，减少“低共振噪声段硬做 continuation”。
- **对 `Fibonacci confirmation / retest_hold`**：更像 long 侧风险覆盖层（size-down/veto），而不是确认层主信号。
- **对 `EMA / PSAR raw alpha focus`**：支持“EMA/PSAR 不单扛主 alpha”的既有判断；`vol commonality` 更应当是 regime/filter 角色。

## 3.5 策略拆解（必填）
- 方向属性：偏顺势 follow-up（但具明显多空不对称）
- 基础 alpha：沿用现有 breakout-short / fib_retest / ema-psar baseline
- regime：跨币 1h 实现波动共振计数（15m 频率更新）
- filter / veto：`commonality_count>=2` 作为 short-follow-up 放行候选；long 侧优先当 size-down/veto 候选
- risk / sizing / execution overlay：long 侧默认降仓；short 侧允许正常仓位或轻微加权（需后续验证）

## 4. 可复刻的最小实验（下一步怎么测）
**研究假设**：15m follow-up 的成本后生存，不只取决于本币形态，还取决于“是否发生跨币同步高波动共振”。

**数据源与公开性**：
- 数据源：Binance USDⓈ-M `GET /fapi/v1/klines`（公开可得，无需私钥）
- 更新频率：15m（可滚动汇总到 1h RV）
- 资产：BTC/ETH/SOL
- 最小样本：最近 120d（建议扩到 180d 做稳健性）

**最小可复现实验口径**：
1. 对每个币算 `rv1h = sqrt(sum(ret_15m^2, last 4 bars))`，再做 96-bar z-score；
2. 定义 `commonality_count = # {rv_z > 1.0}`（0~3）；
3. 挂到 `breakout-short V3` 的 follow-up 层，比较三臂：`baseline / low-commonality-only / high-commonality-veto-or-allow`；
4. 统一 `next-bar open + no-overlap + post-cost`，主看：`mean_net_bp / false_follow_through / trade_count_retention`。

## 5. 风险与保留意见
- 本轮是代理快检，不是完整策略回测；当前 baseline 触发定义仍较简化。  
- `commonality` 阈值（如 z>1）对样本分桶敏感，必须训练段冻结后再测试。  
- 该因子更像过滤层，不应包装成独立主触发；否则容易把 regime 信息误读成 alpha 本体。

## 6. 来源
1. **Djanga, E., Cucuringu, M., & Zhang, C. (2023). _Cryptocurrency volatility forecasting using commonality in intraday volatility_. 4th ACM International Conference on AI in Finance (ICAIF).**  
   - DOI: <https://doi.org/10.1145/3604237.3626912>  
   - Readable URL: <https://dblp.org/rec/conf/icaif/DjangaCZ23>  
   - Venue URL: <https://doi.org/10.1145/3604237.3626912>

2. **Djanga et al. repository (2023, updated 2026). _crypto_volatility_forecasting_using_commonality_in_intraday_volatility_.**  
   - Repo URL: <https://github.com/edjanga/crypto_volatility_forecasting_using_commonality_in_intraday_volatility>  
   - Readable URL: <https://github.com/edjanga/crypto_volatility_forecasting_using_commonality_in_intraday_volatility>

3. **Binance Futures API Documentation (public market data).**  
   - Endpoint: `GET /fapi/v1/klines`  
   - Readable URL: <https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data-market_data>

4. **本地最小快检产物**  
   - Artifact: `reports/artifacts/literature/commonality_intraday_vol_proxy_summary_2026-03-23.csv`
