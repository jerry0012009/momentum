# 别把 Fib 回踩默认钉死在 0.71-0.79：15m fresh-breakout 里，`38-62` 比 `62-79` 更像可执行的 retest_hold admission 区
- 时间：2026-03-19 20:41 UTC
- 类型：GitHub + 本地 clean-room 代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/fib-zone-depth/bos/pullback/confirmation/repo/crypto/15m
- 证据类型：repo 规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮不是复刻 repo 的“整套机器人”，而是只抽了一个对当前 desk 更有边际价值的旁支问题：

> `Fibonacci confirmation / retest_hold` 在 15m 应该默认等“更深回踩（62-79 或 71-79）”吗？
> 还是浅中回踩（38-50 / 50-62）更实用？

对应来源是 **Madrycrypto (2026) 的 `fibo71-bot`**。repo 主叙事强调 CP2.0 的深回踩区（71-79），但它自己的回测文档也给了一个可检验信号：
- H1/D1 上不同品种的最优区间并不一致；
- 文档汇总里 `38-50` 的平均表现并不差，甚至在多数品种更稳。

所以这轮只回答一个最小问题：
**在我们 15m crypto 执行口径下，Fib 深浅区间应该如何排序。**

## 2. 核心结论
1. **一句话结论**：在 15m `fresh breakout -> pullback retest` 代理里，默认应优先 `38-62`（浅中），而不是把 `62-79`（深）当成默认 admission。  
2. **一句话证据**：同一 clean-room 口径下，深区间在收益、成功率、触达时效都系统性更差，且没有换来更好的跨资产一致性。  
3. 关键数据（BTC/ETH/SOL，120d，15m，6bps/side）：
   - 分区间 `avg_net_ret`：
     - `38-50`: `-0.0458%`
     - `50-62`: `-0.0147%`（四档里最好）
     - `62-71`: `-0.0951%`
     - `71-79`: `-0.0978%`
   - 分区间 `success_rate`（先回到 breakout high 再算成功）：
     - `38-50`: `34.9%`
     - `50-62`: `28.8%`
     - `62-71`: `20.4%`
     - `71-79`: `14.4%`
   - 触达中位时间 `bars_to_touch`：`4.0 -> 5.0 -> 6.5 -> 7.0`（越深越慢）。
4. 按桶聚合：
   - `shallow_mid_38_62`: `avg_net_ret = -0.0328%`
   - `deep_62_79`: `avg_net_ret = -0.0963%`
   - 深桶约为浅中桶亏损斜率的 **~2.9x**（按 `avg_net_ret` 绝对值）。
5. 资产侧只看到一个亮点：`BTC@50-62` 的 `total_return = +5.57%`；其余多数资产-区间组合仍为负，说明这不是“深回踩天然更稳”的市场事实。

## 3. 为什么它直接服务当前三条收口线
- **Fibonacci confirmation / retest_hold（最直接）**：把“回踩要不要等更深”从经验句改成可回测的 admission 排序。  
- **EMA / PSAR raw alpha focus**：可直接把 Fib depth 作为 continuation 前置过滤（`38-62` 常态、`62-79` 条件触发），不是再加一个同质震荡指标。  
- **V3 breakout-short follow-up**：当反向 pullback 深到 `62-79` 且触达时间拉长时，更像 post-break continuation 衰减信号，可作为 follow-up 的 failure/降权线索。

## 4. 最小实验口径（可复现）
### 4.1 数据源与公开性
- 数据源：Binance Futures 公共 K 线（本地 cache 复用）
- 公开性：公开可得
- 更新频率：5m / 15m（本轮使用 15m）

### 4.2 clean-room 规则
- 样本：`BTCUSDT / ETHUSDT / SOLUSDT`，`120d 15m`
- breakout 定义：`close > prev_high_20` 且 bullish `body_ratio >= 0.40` 且 `breakout_extension_atr >= 0.20`
- 锚点：`anchor_high = breakout bar high`，`anchor_low = prev_low_20`
- 入场：breakout 后 `12` 根内首次触达 Fib 区间，**next-bar open**
- 退出：先到 `anchor_high` 记 TP；先到 `anchor_low` 记 stop；否则 `hold 8 bars` time stop
- 成本：`6 bps / side`
- 执行约束：`no-overlap`（每资产每区间）

### 4.3 产物
- `reports/artifacts/quant_digests/fib_zone_depth_proxy/trade_log.csv`
- `reports/artifacts/quant_digests/fib_zone_depth_proxy/overall_summary.csv`
- `reports/artifacts/quant_digests/fib_zone_depth_proxy/asset_summary.csv`
- `reports/artifacts/quant_digests/fib_zone_depth_proxy/depth_bucket_summary.csv`
- `reports/artifacts/quant_digests/fib_zone_depth_proxy/summary_snapshot.json`
- 复现实验脚本：`scripts/build_quant_digest_fib_zone_depth_proxy.py`

## 5. 下一步怎么测（直接可排期）
1. **深浅动态切换，不再固定单区间**：
   - baseline 用 `38-50` 与 `50-62` 双臂；
   - 仅在 `trend_strength`（如 ADX/ER/HTF EMA 斜率）达标时开放 `62-71`，`71-79` 默认关闭。
2. **和 Fib 主线做最小并入实验**：
   - 在现有 `fib_retest_long` 上做 A/B：`fixed 0.618 hold` vs `depth-adaptive admission`；
   - 先看四个指标：`post_cost_expectancy / retention / fail_back_inside_4bars / stopout_rate`。
3. **5m 执行 / 15m 判势分层**：
   - 15m 只决定“允许哪个深度桶”；
   - 5m 只负责触发（减少深回踩等待导致的迟到与空转）。

## 6. 风险与保留意见
- 来源仓库是新 repo（创建于 2026-03-15，stars=0），工程信号可读，但还不构成“外部共识”。
- 本轮是最小代理，不等于完整策略 OOS 结论。
- 结果显示“浅中优于深”并不代表浅中已是正 alpha；当前更像是 **减亏排序** 与 **admission 优先级** 证据。

## 7. 来源
1. **Madrycrypto. (2026). _fibo71-bot: Fibo 71 Trading Bot - Fibonacci retracement strategy with BOS detection_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/Madrycrypto/fibo71-bot>
   - Repo URL: <https://github.com/Madrycrypto/fibo71-bot>
2. **Madrycrypto. (2026). _BACKTEST_RESULTS.md_ (repo 文档).**
   - Venue: GitHub Docs
   - DOI: N/A
   - Readable URL: <https://github.com/Madrycrypto/fibo71-bot/blob/main/docs/BACKTEST_RESULTS.md>
   - Raw URL: <https://raw.githubusercontent.com/Madrycrypto/fibo71-bot/main/docs/BACKTEST_RESULTS.md>
3. **Madrycrypto. (2026). _fibonacci_extended.py_ (entry zone 0.62–0.71 与扩展位实现).**
   - Venue: GitHub Source
   - DOI: N/A
   - Readable URL: <https://github.com/Madrycrypto/fibo71-bot/blob/main/src/indicators/fibonacci_extended.py>
   - Raw URL: <https://raw.githubusercontent.com/Madrycrypto/fibo71-bot/main/src/indicators/fibonacci_extended.py>
4. **Binance Futures API. (Public). _Klines endpoint_.**
   - Venue: Public Exchange API
   - DOI: N/A
   - Readable URL: <https://fapi.binance.com/fapi/v1/klines>
   - 用途：15m 公开行情最小复现实验数据源
