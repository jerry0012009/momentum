# Rank 5 / Rank 6 external-data probe — 2026-03-17 15:25 UTC

## 任务
验证当前环境下：
- `Rank 5 / Polymarket lag-arb / BTC indicator score betting`
- `Rank 6 / BTC-equity proxy spread / COIN-MSTR-tech relative-value`

是否已经具备足够的数据可得性与 first-pass 证据，值得继续探索。

## Probe 范围（故意收窄）
### Rank 5
- 只验证：
  1. Polymarket 公开接口是否现在就能拿到；
  2. 当前 active BTC 相关市场是否足够多、足够贴近 `15m / intraday BTC`；
  3. 是否已经适合直接做 honest 的 lag-arb clean replication。
- **不做**：交易下单、账户权限、HMAC 认证、实盘 execution。

### Rank 6
- 只验证：
  1. `BTC spot 15m` 与 `SPY / QQQ / COIN / MSTR 15m` 是否可直接拿到；
  2. overlapping intraday bars 是否足够；
  3. 有没有值得继续的相关性 / 轻 lead-lag 结构。
- **不做**：完整 stat-arb / z-score spread 组合回测。

## Probe 结果

### Rank 5 — Polymarket
**数据可得性：可以拿到，但当前市场结构不太适合直接做 15m lag-arb 主线。**

#### 1. 接口是否可用
当前环境下可直接访问：
- `gamma-api.polymarket.com/markets`
- `gamma-api.polymarket.com/events`
- `clob.polymarket.com/prices-history`
- `clob.polymarket.com/book`

说明：
- 做 `source intake / 市场筛选 / 历史价格抓取` 不一定需要额外 API key；
- 但若未来要做真正的 CLOB 交易、下单、撤单、账户侧查询，则按官方文档仍需要 wallet + API creds / HMAC auth。

#### 2. 当前 active BTC 市场够不够贴近 intraday thesis
本轮分页抓取了约 `2000` 个 active+unresolved market，筛出显式 BTC / Bitcoin 相关的 active 市场只有 `4` 个：
- `Will bitcoin hit $1m before GTA VI?`
- `Will Bitcoin hit $150k by March 31, 2026?`
- `Will Bitcoin hit $150k by June 30, 2026?`
- `Will Bitcoin hit $150k by December 31, 2026?`

这些市场的问题很直接：
- 都是**长周期里程碑/门槛式问题**；
- 不是围绕近端 intraday price action 的高频事件市场；
- 价格更多反映长期 hit-probability，而不是 15m 级别可套利的机械滞后。

#### 3. 初步结论
- **公开数据链：可用**
- **当前 active BTC 市场结构：不够贴近 15m lag-arb 主线**
- 因此 `Rank 5` 当前更诚实的结论是：
  - **值得继续保留在 external-data / source-intake 池里**；
  - 但**暂时不值得直接升为默认 clean replication 主线**。

#### 4. 何时值得重开
只有满足下面任一条，`Rank 5` 才更值得继续：
1. 发现更短周期、更贴近 BTC price action 的 active prediction markets；
2. 能拿到更细的可成交价格/盘口/成交流数据，并证明问题语义足够贴近短周期波动；
3. bot2 明确允许把它当作“外部数据探索线”，而不是继续要求它符合当前 `paper / repo based 5m / 15m crypto` fast-lane。

---

### Rank 6 — BTC vs equity proxies
**数据可得性已经足够，且 COIN / MSTR 确实值得做下一步最小 clean replication。**

#### 1. 当前能直接拿到什么
- `BTCUSDT 15m`：Binance spot
- `SPY / QQQ / COIN / MSTR 15m`：Yahoo Finance chart API
- overlapping regular-session bars：每个标的当前都有约 `1212` 根可对齐的 `15m` 样本

所以 `Rank 6` 已经不再是“完全因为数据拿不到而无法推进”的状态。

#### 2. First-pass 结果
核心 probe 指标：
- same-bar return correlation
- one-bar BTC-leads-equity correlation
- one-bar equity-leads-BTC correlation
- 大幅 BTC move 后下一根 equity bar 的方向命中率

结果简表：
- `SPY`：same-bar corr ≈ `0.50`；BTC leads 1 bar ≈ `0.046`
- `QQQ`：same-bar corr ≈ `0.49`；BTC leads 1 bar ≈ `0.064`
- `COIN`：same-bar corr ≈ `0.73`；BTC leads 1 bar ≈ `0.091`
- `MSTR`：same-bar corr ≈ `0.79`；BTC leads 1 bar ≈ `0.093`

读法：
- `SPY / QQQ` 跟 BTC 有同步相关，但更像大盘 risk-on/risk-off 共振，不够像短周期可交易 proxy；
- `COIN / MSTR` 与 BTC 的 intraday 同步性明显更强；
- 非零 lag 里，最强的一档都是 **`lag = -1`**，即更像 **BTC 先动、`COIN/MSTR` 下一根 bar 才部分跟随**；
- 这个 lag 不大，但已经足够支持做一轮 **最小 clean replication**。

#### 3. 初步结论
`Rank 6` 当前更诚实的 verdict 是：
- **值得继续**；
- 但应该先**收窄 scope**，不要一上来就做 `BTC vs SPY/QQQ/COIN/MSTR` 全家桶；
- 下一轮更适合只做：
  - `BTC -> COIN`
  - `BTC -> MSTR`
  的最小 cross-asset proxy replication。

#### 4. 推荐的下一步（只允许 1 刀）
下一刀只做一个最小 first verdict：
1. 固定 overlapping session（美股 regular session）
2. 固定 `BTC lead window = 前 1 根 / 2 根 15m`
3. 固定 2~3 个简单规则：
   - `btc_large_move_follow_proxy`
   - `btc_zscore_dislocation_vs_coin`
   - `btc_zscore_dislocation_vs_mstr`
4. 只回答：
   - post-cost return
   - trade_count
   - sign-hit / follow-through
   - 时间 pocket 是否极端集中

如果这 1 刀也没有给出比随机更清楚的结果，再 park；不要无限扩张到全美股 proxy 宇宙。

---

## 总结 verdict
- **Rank 5 / Polymarket**：
  - 数据链可用；
  - 但当前 active BTC 市场更像长周期概率市场，不够贴近 `15m lag-arb`；
  - **暂不建议立刻升格**，保留在 external-data exploration queue。

- **Rank 6 / BTC-equity proxy**：
  - 数据链已足够；
  - `COIN / MSTR` 对 BTC 的 15m 同步性明显强于 `SPY / QQQ`；
  - **值得做下一轮最小 clean replication**，但只建议从 `BTC->COIN / BTC->MSTR` 两条窄线开始。

## 产物
- `reports/artifacts/external_data_probes/rank5_polymarket_btc_market_probe.csv`
- `reports/artifacts/external_data_probes/rank6_btc_equity_proxy_probe_metrics.csv`
- `reports/artifacts/external_data_probes/rank5_rank6_external_data_probe_summary.json`
