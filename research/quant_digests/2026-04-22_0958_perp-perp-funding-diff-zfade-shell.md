# 别把 perp-perp funding diff 只读成“低频收租”：对 short-cycle crypto desk，更该先拆的是「跨所同标的 funding spread z-score fade × child execution」这条 raw alpha 壳

- 时间：2026-04-22 09:58 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `strategies/perp_perp.py` + `config/main.yaml` + `backtest/execution_sim.py`）+ Binance / Bybit 公开 funding history portability probe（`BTC/ETH`，最近 `200` 个 8h funding 点）
- 主题类型：`raw alpha`
- 基础 alpha：`同一永续合约在两个交易所的 funding rate 差值出现统计极端时，做空高 funding venue、做多低 funding venue，赚下一段 funding differential，并等待差值回归`
- 是否可独立复现：`是`
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：`是`
- 主题标签：raw-alpha/carry/funding/relative-value/stat-arb/perp-perp/cross-venue/zscore/convergence/binance/bybit/1m/5m/15m/repo/public-data/cost/risk

## 0) 先说结论（给 desk 的一句话）
**这条线值得进素材池，但不要照搬 repo 默认阈值直接上 BTC/ETH。** `gencersarp/cryptoarb` 给了一条很干净的 perp-perp funding differential 完整壳：entry、exit、sizing、max-hold、cost simulator 都齐；但最近 `Binance vs Bybit` 的 `BTC/ETH` 公开 funding 差太窄，repo 默认 `2 bps/8h` 门槛在近 `200` 个结算点里没有触发。更合理的 desk 用法是：把它当 **1m/5m 扫描 + 5m/15m child execution 的稀疏 relative-value alpha**，先扩到多 venue / 多 asset，再决定是否值得接实盘执行。

## 1) 这次为什么值得写（且不重复）
最近已有多篇 `basis / funding / pairs` digest，但这篇不是再写 spot-perp basis，也不是泛泛的“跨所 funding APR 榜单”。它的新增点在于：

- **alpha 本体更窄**：只做 `same asset, perp vs perp, venue A funding - venue B funding`；不需要 spot leg，也不赌币价方向；
- **entry 不是单纯 APR 排名**：要求 funding spread 同时过绝对阈值与 rolling z-score 极端；
- **exit 清楚**：spread z-score 回到中性区间就平，不强行持有到很久；
- **工程壳完整**：repo 同时写了 walk-forward、1-bar delay、maker/taker fee、vol×ADV slippage、partial fill、downtime、forced close、cost stress。

一句话：**这是 relative-value raw alpha，不是 filter；低频 funding 是收益来源，短周期 bars 负责扫描、入场、补腿、退出和风控。**

## 2) 来源与策略拆解（repo source audit）
主来源：
- Authors / Owner：`gencersarp`
- Year：`2026`（created `2026-03-29`，pushed `2026-04-06`）
- Title：*cryptoarb: Production-grade crypto market-neutral arbitrage research & backtesting framework*
- Venue：GitHub repository
- DOI：`N/A`
- Readable URL / Repo URL：`https://github.com/gencersarp/cryptoarb`
- 关键源码：`strategies/perp_perp.py`, `config/main.yaml`, `backtest/execution_sim.py`

`strategies/perp_perp.py` 的核心规则可以还原为：

1. 对同一资产取两个 venue 的 funding：`fr_hi`, `fr_lo`；
2. 计算 `spread = fr_hi - fr_lo`；
3. 用过去 `30` 个 funding bars 计算 spread z-score；
4. 入场条件：
   - `abs(spread) >= min_funding_spread`，repo 默认 `0.0002`，即 `2 bps/8h`；
   - `abs(z) >= entry_z`，repo 默认 `2.0`；
5. 方向：
   - `spread > 0`：venue A funding 更高，short venue A perp，long venue B perp；
   - `spread < 0`：反过来；
6. 出场：`abs(z) < exit_z`，repo 默认 `0.5`；
7. 组合约束：`max_hold_bars = 6`、`position_size_pct = 0.30`、`max_open_positions = 2`。

这里要注意一个源码层细节：`perp_perp.py` 里的 `Signal` 只显式发了 `v_hi` 那条腿，另一条低 funding venue 的 hedge leg 需要由 backtest / execution 层补齐；我们复现时应把它明确写成双腿组合，避免把一条腿误测成方向交易。

## 3) 最小公开数据 portability probe
### 3.1 数据与口径
- 数据源：Binance USDⓈ-M Futures public funding history + Bybit v5 public funding history
- 标的：`BTCUSDT`, `ETHUSDT`
- 频率：8h funding settlement；对 short-cycle desk，信号每 8h 变，但可用 `1m/5m/15m` 做 child execution 和补腿监控
- 样本：每个标的最近 `200` 个 matched 8h 点，约 `2026-02-15 00:00 UTC` 到 `2026-04-22 08:00 UTC`
- 指标：`spread = binance_funding - bybit_funding`，rolling `30` 点 z-score
- 成本：本轮只是 feasibility probe，未扣真实双腿成交成本；因此只能判断“有没有足够厚的 funding 差”，不能直接判断净收益

### 3.2 关键观察
`BTCUSDT`：
- matched funding points：`200`
- 平均绝对 funding spread：`0.377 bps/8h`
- p95 绝对 spread：`0.897 bps/8h`
- 最大绝对 spread：`1.473 bps/8h`
- repo 默认门槛 `2 bps/8h + |z|>=2`：`0` 次触发

`ETHUSDT`：
- matched funding points：`200`
- 平均绝对 funding spread：`0.388 bps/8h`
- p95 绝对 spread：`0.978 bps/8h`
- 最大绝对 spread：`1.570 bps/8h`
- repo 默认门槛 `2 bps/8h + |z|>=2`：`0` 次触发

把绝对门槛降到更现实的 `0.5/1.0/1.5 bps` 后，信号会出现但非常稀疏：

| symbol | min spread | z gate | entries | next-1 funding spread 收敛率 | next-3 收敛率 |
|---|---:|---:|---:|---:|---:|
| BTCUSDT | `0.5 bps` | `|z|>=2` | `7` | `85.7%` | `100%` |
| BTCUSDT | `1.0 bps` | `|z|>=2` | `4` | `100%` | `100%` |
| ETHUSDT | `0.5 bps` | `|z|>=2` | `11` | `90.9%` | `100%` |
| ETHUSDT | `1.0 bps` | `|z|>=2` | `6` | `100%` | `100%` |
| ETHUSDT | `1.5 bps` | `|z|>=2` | `1` | `100%` | `100%` |

人话解释：**spread 的确有回归性，但最近 BTC/ETH 两大 venue 太有效，raw edge 厚度很薄；如果双腿都吃 taker，绝大多数信号不够扣费。**

## 4) 对 `1m / 3m / 5m / 15m` 的关系
这条 alpha 的收益结算不是逐根 K 线，而是 funding settlement；但短周期并不无关：

- `1m/3m`：用于 funding 快照轮询、盘口价差、腿间偏离、partial fill / orphan leg 监控；
- `5m`：用于 child execution，把双腿拆成 maker-first / post-only 尝试，若价差恶化则撤单；
- `15m`：用于持仓巡检、z-score exit、max-hold、venue exposure rebalancing；
- `8h`：用于 funding PnL attribution，不应把 funding alpha 伪装成每根 K 的方向预测。

## 5) 怎么落成完整策略壳
最小可落地版本：

- **Universe**：先做 `BTC/ETH/SOL/BNB/XRP/DOGE/LINK/AVAX`，venue 至少 `Binance / Bybit / OKX / Hyperliquid`；
- **Entry**：对每个 `(asset, venue_i, venue_j)` 计算 funding spread；要求 `|z_30|>=2` 且 `expected_next_funding_edge_bps > round_trip_cost_bps + safety_margin`；
- **Direction**：short 高 funding perp，long 低 funding perp，双腿 delta-neutral；
- **Sizing**：`notional = min(capital*0.10~0.30, venue_cap, depth_cap)`；用 `edge_after_cost / volatility` 做缩放，不要用 APR 幻觉放大；
- **Exit**：`|z|<0.5`、下一期 expected edge 转负、腿间 mark divergence 超阈值、或 max hold `1~3` 个 funding intervals；
- **Risk**：orphan-leg kill switch、venue exposure cap、margin buffer、funding timestamp mismatch、borrow / transfer / API outage 处理；
- **Cost**：双腿 maker/taker fee + slippage + funding timestamp miss + collateral fragmentation；若不能 maker-first，默认把信号降级。

## 6) 取舍：它值得进池，但当前应如何排优先级
- 值得进：因为 base alpha 清楚、可复现、直接 market-neutral，和趋势/反转类信号相关性低；
- 不该高估：BTC/ETH 的 Binance-Bybit recent spread 不够厚，repo 默认 `2 bps/8h` 门槛近期根本不触发；
- 真正要测的是 **多 venue / 多 asset / maker-first**，不是只在两大所 BTC/ETH 上硬卷；
- 如果后续扩 universe 后仍然没有 `post-cost > 0` 的事件密度，就把它降级成 `funding-regime gate`：当某币 funding cross-venue 极度不一致时，提醒别让其他方向 alpha 裸追拥挤腿。

## 7) 下一步怎么测（直接可执行）
1. **扩 universe / venue sweep**：用公开 funding history 拉 `Binance / Bybit / OKX / Hyperliquid`，覆盖至少 `20` 个永续，共同 timestamp 对齐到 8h。
2. **事件阈值 sweep**：测试 `min_abs_spread = 0.5/1.0/1.5/2.0 bps` × `z = 1.5/2.0/2.5`；不要先固定 repo 默认值。
3. **加入真实成本**：双腿 maker / taker 三种情景：`maker-maker`、`maker-taker`、`taker-taker`；只有 maker-first 版本为正才值得继续。
4. **用短周期 child execution 回放**：entry signal 在 8h bar 产生后，用 `1m/5m` orderbook / kline 近似成交，记录 leg-in slippage 与 orphan-leg 暴露时长。
5. **归因**：把 PnL 拆成 funding income、mark-to-market drift、fee/slippage、missed funding；若收益主要来自价格方向而非 funding diff，则不能算这条 alpha 过关。

## 8) 关键来源
1. **gencersarp (2026)**. *cryptoarb: Production-grade crypto market-neutral arbitrage research & backtesting framework*. GitHub Repository.  
   - Venue：GitHub  
   - DOI：`N/A`  
   - Repo URL：`https://github.com/gencersarp/cryptoarb`  
   - Source files：`strategies/perp_perp.py`, `config/main.yaml`, `backtest/execution_sim.py`
2. **Binance USDⓈ-M Futures API**. Funding Rate History.  
   - Readable URL：`https://binance-docs.github.io/apidocs/futures/en/#get-funding-rate-history`
3. **Bybit v5 API**. Get Funding Rate History.  
   - Readable URL：`https://bybit-exchange.github.io/docs/v5/market/history-fund-rate`

---

## 附：本轮实验文件
- `reports/artifacts/quant_digests/perp_perp_funding_diff_probe_20260422/summary.txt`
- `reports/artifacts/quant_digests/perp_perp_funding_diff_probe_20260422/threshold_sweep.csv`
- `reports/artifacts/quant_digests/perp_perp_funding_diff_probe_20260422/BTCUSDT_binance_bybit_funding_diff.csv`
- `reports/artifacts/quant_digests/perp_perp_funding_diff_probe_20260422/ETHUSDT_binance_bybit_funding_diff.csv`
