# 别把 `hammer/engulf` 直接当 breakout-short 共享确认：在 15m 上它更像 Fib / EMA 回踩确认的 long-side 质量门
- 时间：2026-03-23 00:31 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/hammer/engulfing/pattern-gate/asymmetry/confirmation/filter/repo/crypto/15m/5m
- 证据类型：工程证据（仓库源码）+ 本地最小代理快检

## 1. 这次看了什么
这轮选题来自近期仓库 **caizongxun/crypto-15m-trading-strategy (2026)**。仓库主张三层确认（MA 趋势 + MACD/RSI 动量 + volume），并在信号里加入 `hammer / engulfing` 形态与 divergence。

我没有照搬整套策略，而是只抽一个更贴 desk 的旁支问题：
> 在 `15m` 的“趋势中回踩后再确认”场景里，`hammer/engulf` 是否值得做成三条收口线共享 gate？

这个问题直接服务当前三条线：
- `Fibonacci confirmation / retest_hold`
- `EMA / PSAR raw alpha focus`
- `V3 breakout-short follow-up`

## 2. 核心结论
- **一句话结论**：`hammer/engulf` 在 15m 更像 **long-side 的回踩质量过滤层**；不适合直接升为 breakout-short 的 shared hard gate。  
- **一句话证明方式**：用 Binance Futures `BTC/ETH/SOL` 最近 `120d` 的 `15m` K 线，固定 `next-bar open` 入场 + `+1.5ATR/-1ATR` first-hit（8 bars）做代理判决，对比 `base` vs `pattern gate` 四臂，观察多空非对称结果。

关键数据点（BTC/ETH/SOL 合并）：
1. **long 侧：pattern gate 有净提升但会显著降频**  
   - `base`: `n=306`, `target_rate=34.6%`, `stop_rate=51.3%`, `avg_pnl_r=+0.0319`  
   - `pattern`: `n=102`, `target_rate=33.3%`, `stop_rate=47.1%`, `avg_pnl_r=+0.0925`
2. **short 侧：pattern gate 未改善**  
   - `base`: `n=365`, `avg_pnl_r=-0.1148`  
   - `pattern`: `n=126`, `avg_pnl_r=-0.1151`
3. **形态子类拆分显示来源不对称**  
   - long-`hammer`: `n=16`, `avg_pnl_r=+0.3125`（稀疏但质量高）  
   - long-`engulf`: `n=84`, `avg_pnl_r=+0.0631`  
   - short-`hammer`（倒锤）：`n=21`, `avg_pnl_r=-0.5536`（明显拖累）

## 3. 为什么和当前项目有关
- 对 **Fib retest_hold**：可作为“回踩确认质量门”，优先拦掉低质量 rebound。  
- 对 **EMA/PSAR**：更像 admission/filter，不是 raw alpha 主触发；角色应放在确认层。  
- 对 **breakout-short follow-up**：当前证据不支持共享默认放行，至少应先做 short 独立拆分（例如只留 bearish engulfing，剔除倒锤）。

## 3.5 策略拆解（必填）
- 方向属性：顺势 continuation（以回踩后重启为主）  
- 基础 alpha：趋势中回踩再延续（MA 结构 + 回踩确认）  
- regime：`SMA5>SMA20>SMA60`（long）/ `SMA5<SMA20<SMA60`（short）  
- filter / veto：`hammer/engulf` 形态门（当前证据：long 可用、short 需拆分）  
- risk / sizing / execution overlay：`next-bar open`、`+1.5ATR/-1ATR`、8 bars first-hit

## 4. 可复刻的最小实验（下一步怎么测）
做一个最小三臂 A/B（先不加复杂模型）：
1. `base_retest`（无形态门）
2. `base_retest + long_pattern_gate`（仅 long 开启 hammer/engulf）
3. `base_retest + short_engulf_only`（short 仅保留 bearish engulf，禁倒锤）

统一口径：
- 资产：BTC/ETH/SOL perp
- 周期：`15m signal`，并补 `5m execution` 对照
- 判决：`+1.5ATR/-1ATR`, 8 bars
- 成本：`6/10/15 bps per side`

优先看两项：
- `post-cost avg_pnl_r`
- `trade retention`（交易保留率）

升级条件：若 long gate 在 15m 和 5m 执行下都维持正边际，且交易保留率 > 35%，可进入三条收口线的候选确认层。

## 5. 风险与保留意见
- 这是 **proxy first-hit**，不是完整组合回测；
- long 改善并非全币种一致（BTC long 侧未改善，ETH/SOL 贡献更大）；
- short 侧对形态定义非常敏感，直接共享会误伤；
- 形态样本偏稀疏，需滚动窗口和成本敏感性复核。

## 6. 来源
1. **Cai Zongxun. (2026). _crypto-15m-trading-strategy_. GitHub Repository.**  
   - Authors: Cai Zongxun  
   - Year: 2026  
   - Title: crypto-15m-trading-strategy  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/caizongxun/crypto-15m-trading-strategy`  
   - Repo URL: `https://github.com/caizongxun/crypto-15m-trading-strategy`

2. **Cai Zongxun. (2026). _crypto_15m_strategy.pine_.**  
   - Authors: Cai Zongxun  
   - Year: 2026  
   - Title: crypto_15m_strategy.pine  
   - Venue: GitHub raw source file  
   - DOI: N/A  
   - Readable URL: `https://raw.githubusercontent.com/caizongxun/crypto-15m-trading-strategy/main/crypto_15m_strategy.pine`  
   - Repo URL: `https://github.com/caizongxun/crypto-15m-trading-strategy`

3. **Binance. (2026). _USDⓈ-M Futures REST API – Kline/Candlestick Data_.**  
   - Authors: Binance  
   - Year: 2026  
   - Title: Kline/Candlestick Data  
   - Venue: Binance Developers Docs  
   - DOI: N/A  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`  
   - Repo URL: N/A

## 7. 本轮落地产物
- `scripts/run_quant_digest_caizongxun_pattern_retest_proxy.py`
- `reports/artifacts/quant_digest_caizongxun_pattern_retest_proxy/event_log.csv`
- `reports/artifacts/quant_digest_caizongxun_pattern_retest_proxy/summary.csv`
- `reports/artifacts/quant_digest_caizongxun_pattern_retest_proxy/pattern_subtype_summary.csv`
- `reports/artifacts/quant_digest_caizongxun_pattern_retest_proxy/asset_variant_summary.csv`
- `reports/artifacts/quant_digest_caizongxun_pattern_retest_proxy/meta.json`
