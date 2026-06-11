# 别把 PFE 高阈值当 15m follow-up 放行：它更像 extreme-move veto / size-down overlay
- 时间：2026-03-23 08:03 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题类型：overlay
- 基础 alpha：breakout / fib retest / ema-psar continuation（既有 setup）
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：breakout-short/v3/final-verdict/follow-up/fibonacci/retest-hold/ema/psar/pfe/path-efficiency/exhaustion/veto/position-sizing/regime/filter/repo/crypto/5m/15m
- 证据类型：工程证据 + 本地快检（可复现）

## 1. 这次看了什么
这次主看 `fmzquant/strategies` 里的 **ChaoZhang (2024)《Polarized Fractal Efficiency (PFE) Trading Strategy》**。它最值得我们 desk 拿来用的旁支，不是“再加一个主触发器”，而是把 **路径效率极值**变成 `follow-up` 的拒单/降仓条件。

## 2. 核心结论
- **一句话核心结论：** 在 15m 上，`|PFE_EMA|` 高阈值不该被当成 continuation 绿灯，更像“末端冲刺/追单风险”提示；更诚实的角色是 `veto / size-down overlay`。
- **一句话证明方式：** 用仓库默认参数（`Length=9, LengthEMA=5`）在 `BTC/ETH/SOL` 近 180 天 15m 数据做轻量分桶，比较 `|PFE_EMA|` 不同区间的后续方向延续率。

本地最小快检（pooled，`n=52,401`）：
- `|PFE_EMA|<=20`：`1-bar continuation=49.08%`，`4-bar continuation=48.84%`；
- `20<|PFE_EMA|<=50`：`1-bar continuation=48.50%`，`4-bar continuation=47.91%`；
- `|PFE_EMA|>50`：`1-bar continuation=47.13%`，`4-bar continuation=47.77%`。

可执行读法：`high_abs` 相比 `low_abs` 在 1-bar continuation 低约 **1.95pct**，不支持“PFE 越极端越该追”。

补充：按资产看（BTC/ETH/SOL）`high_abs` 的 `cont_hit_1` 都低于各自低分桶，方向一致。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：post-break 末端冲刺时，`|PFE_EMA|` 极值可做 no-chase veto，减少追在最后一脚。
- **Fibonacci confirmation / retest_hold**：retest 刚站回位时，若同步出现极端路径效率，先降仓或等 1 根再确认，避免“刚站回就过冲回吐”。
- **EMA / PSAR raw alpha focus**：PFE 不替代 EMA/PSAR 的方向角色，只补一个“是否已经太直太急”的执行层风险门。

## 3.5 策略拆解（角色定位）
- 方向属性：不是 raw alpha，不单独开仓。
- 基础 alpha：沿用现有 breakout / fib retest / ema-psar setup。
- regime/filter：`|PFE_EMA|` 极值区作为 anti-chase 风险过滤。
- risk/sizing：极值区优先 `size-down`，次选 `temporary veto`。

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** 相比 baseline，`high-|PFE_EMA|` veto/降仓能降低 post-break 假延续与回吐损失，而不靠“砍光交易数”取胜。
- **可计算定义（沿用仓库公式）：**
  - `PFE = sqrt((close-close[9])^2 + 100)`
  - `C2C = sum(sqrt((close-close[1])^2 + 1), 9)`
  - `xFracEff = sign(close-close[9]) * round((PFE/C2C)*100)`
  - `PFE_EMA = EMA(xFracEff, 5)`
- **A/B/C 三臂（15m，next-bar open，no-overlap）：**
  1. A：baseline（不加 PFE）
  2. B：`|PFE_EMA| > rolling_q90` 时 veto 新 follow-up
  3. C：同条件不 veto，仅 `size × 0.5`
- **最小数据切口：** `BTC/ETH/SOL` perpetual，120~180 天，成本 `6/10/15 bps`。
- **先看 4 个指标：** `post_cost_expectancy`、`false_follow_ratio@4bars`、`trade_count_retention`、`max_drawdown`。

## 5. 风险与保留意见
- 本轮是轻量分桶快检，不是完整 clean replication；用于“值不值得升格下一轮”。
- PFE 绝对值阈值跨币不一定可移植，生产化应优先用 rolling quantile，而非固定 50。
- 若 B/C 改善只来自交易数大幅塌缩（retention 太低），就应直接降级为 setup-specific 规则，不升 shared gate。

## 6. 来源
1. **ChaoZhang. (2024). _Polarized Fractal Efficiency (PFE) Trading Strategy_. FMZ Strategy / GitHub Mirror.**
   - Authors / Year / Title / Venue: ChaoZhang / 2024 / Polarized Fractal Efficiency (PFE) Trading Strategy / FMZ Strategy (mirrored in `fmzquant/strategies`)
   - DOI: N/A
   - Readable URL: https://www.fmz.com/strategy/438792
   - Repo URL: https://github.com/fmzquant/strategies/blob/master/%E6%9E%81%E5%8C%96%E5%88%86%E5%BD%A2%E6%95%88%E7%8E%87PFE%E4%BA%A4%E6%98%93%E7%AD%96%E7%95%A5Polarized-Fractal-Efficiency-PFE-Trading-Strategy.md
2. **Binance USDⓈ-M Futures Market Data API（最小实验数据口径）**
   - Authors / Year / Title / Venue: Binance / ongoing / USDⓈ-M Futures Market Data REST API / Binance Developers
   - DOI: N/A
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api
   - Repo URL: https://github.com/binance/binance-futures-connector-python

## 7. 本地复现产物
- `reports/artifacts/quant_digests/pfe_path_efficiency_proxy_20260323/btcusdt_pfe_frame.csv`
- `reports/artifacts/quant_digests/pfe_path_efficiency_proxy_20260323/ethusdt_pfe_frame.csv`
- `reports/artifacts/quant_digests/pfe_path_efficiency_proxy_20260323/solusdt_pfe_frame.csv`
- `reports/artifacts/quant_digests/pfe_path_efficiency_proxy_20260323/bucket_summary_by_asset.csv`
- `reports/artifacts/quant_digests/pfe_path_efficiency_proxy_20260323/bucket_summary_cross_asset.csv`
- `reports/artifacts/quant_digests/pfe_path_efficiency_proxy_20260323/bucket_summary_pooled.csv`
