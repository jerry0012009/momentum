# 别把这份 2026 microstructure repo 只当模拟器：对 short-cycle desk，更该先测的是「same-underlier cross-venue gap mean reversion × latency budget」这条完整 raw alpha
- 时间：2026-04-04 01:46 UTC
- 类型：GitHub 新仓库 / notebook source audit / 本地公共数据快检
- 主题类型：raw alpha
- 基础 alpha：**同一标的在不同 venue 的短暂报价偏离会向共同价格回归；当 `买便宜腿 + 卖更贵腿` 的预期收敛幅度大于双边费用、spread 与延迟损耗时，可做成短周期 cross-venue stat-arb。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**是**
- 主题标签：raw-alpha/relative-value/stat-arb/same-underlier/cross-venue/latency-arbitrage/mean-reversion/latency-budget/transfer-delay/binance/okx/public-data/repo/1m/3m/5m/15m/execution/cost
- 证据类型：2026 GitHub repo README + notebook source audit（NB04）+ 本地 Binance/OKX 公共 `1m` close 粗快检

## 1. 这次看了什么
这轮刻意补一条**不是 filter、不是 overlay，而是能直接写成完整策略的 raw alpha**：2026 新仓库 **`mengrenman/microstructure-lab`** 里的 **Notebook 04 — Two-Venue Latency Arbitrage Stress Study**。它最有价值的地方不是“又一个模拟器”，而是把这条 alpha 说得很白：**base alpha 就是 same-underlier cross-venue gap mean reversion；真正决定这条线能不能活的，不是你会不会算价差，而是你的 latency budget 有多紧。**

更关键的是，它正好补上了当前素材池里相对少的一块：我们最近已经补了很多 pairs / funding / OFI / same-underlier multispread，但**“跨 venue 同标的价差回归 + 延迟预算”**这条线还缺一篇专门把 entry/exit/cooldown/threshold 和 execution cliff 拆开讲清楚的 digest。

## 2. 核心结论
- 这篇东西的 base alpha 很清楚：**同标的跨 venue 价差回归**，不是 filter，也不是泛化 execution 综述。
- repo 的玩具市场里，`threshold = 0.12`、`transfer_delay = 5` 时：
  - **`latency = 0`**：`final_pnl = +2.068`，`36` 笔，`win_rate = 86.1%`
  - **`latency = 1`**：`final_pnl = -0.901`，`36` 笔，`win_rate = 33.3%`
  - 也就是说，**只多 1 个 step 的信号-成交延迟，就从赚钱翻成亏钱**；这就是这条策略最核心的 latency cliff。
- 同一个 toy setup 下，`threshold = 0.12` 时即使把 `transfer_delay` 从 `1` 拉到 `40`，在 `latency = 0` 仍然保持正值（`+2.521 → +1.445`）；但一旦 `latency >= 1`，各个 delay 桶几乎全部转负。**结论很直接：delay 主要伤害机会数，latency 才直接杀 edge。**
- baseline `latency = 1, delay = 5` 的 threshold sweep 也很干净：
  - `0.06`: `-10.987`（`290` 笔，`29.3%` 胜率）
  - `0.08`: `-7.532`
  - `0.10`: `-3.504`
  - `0.12`: `-0.901`
  - `0.16`: `-0.239`
  - `0.20`: `-0.032`
  - 提高 threshold 只是**少做错单**，并不能把一条已经被 1-step latency 杀死的策略救回来。
- 我又用公开可得的 Binance/OKX `1m` close 做了一个**很粗的 bar 级快检**（最近 `300` 个重合 bar，只看 next-bar 收敛、未计真实双腿成交/深度）：
  - **BTCUSDT**：venue gap 绝对值中位数约 **`0.40 bps`**，`p95 ≈ 1.11 bps`；当 gap `>= 1 bps` 时只有 `27` 次样本，但 next-bar gross 平均约 **`+0.83 bps`**，胜率 **`92.6%`**。
  - **ETHUSDT**：绝对 gap 中位数约 **`1.02 bps`**；gap `>= 1 bps` 有 `159` 次，next-bar gross 平均约 **`+0.31 bps`**，胜率 **`67.9%`**。
  - **SOLUSDT**：绝对 gap 中位数约 **`1.25 bps`**；gap `>= 2 bps` 有 `50` 次，next-bar gross 平均约 **`+1.79 bps`**，胜率 **`86.0%`**。
- 这组公共数据快检的意义不是“证明实盘能赚”，而是说明：**bar 级别的 venue-gap 回归确实存在，但 gross edge 普遍只有亚 `1~2 bps` 量级，极度 fee/latency sensitive。** 所以这条线对 desk 的正确定位不是“慢速 5m stat-arb”，而是**`1m / 3m` 优先、执行条件极其严格的高强度 raw alpha**；`5m / 15m` 更适合拿来做 regime / sizing / 资产筛选，而不是慢悠悠地主执行。

## 3. 为什么和当前项目有关
这条线和我们最近的积累是**互补**，不是重复：
- 和 pairs / cointegration 线不同：它不需要先找长期稳定 spread，直接吃**同一标的跨 venue 的瞬时错位**。
- 和 funding / basis 线不同：它不是等 funding 窗口收息，而是吃**更快的 price convergence**。
- 和 OFI / directional microstructure 线不同：它天然是**市场中性 / 相对价值**，更适合补 desk 的 raw alpha 池结构。
- 和已有 same-underlier multispread 线不同：那条更偏**单 venue 内多 quote / 多 spread 优化**；这一条更偏**跨 venue execution budget**。

一句话说，这轮不是再补一个“确认层”，而是补一个**对实盘基础设施要求更高、但逻辑非常干净的 raw alpha 类型**。

## 3.5 策略拆解（必填）
- 方向属性：**relative-value / stat-arb / same-underlier cross-venue mean reversion**
- 基础 alpha：**同一标的跨 venue 的短时价差会回归，alpha 来自 gap convergence，而不是方向判断。**
- regime：**大市值、高流动性、盘口同步快、手续费低、可双边持仓/有库存时最适合；剧烈跳价、网络抖动、某 venue API 退化时应降权或停机。**
- filter / veto：**仅当 `|gap| > fee + spread + latency buffer + leg-risk buffer` 才能开；禁止低深度盘口、禁止单腿成交概率过低、禁止超出 venue inventory cap。**
- risk / sizing / execution overlay：**按双边最小可成交深度定名义；设 per-venue / per-asset / per-leg exposure cap；若出现单腿成交未对冲，立即进入 kill/flatten 流程；对 transfer delay 用 inventory-funded 与 cooldown 两种版本分别回测。**

## 4. 可复刻的最小实验
**研究假设：** 在 `Binance / OKX / Bybit` 这类主流 venue 上，`BTC / ETH / SOL` 的同标的 gap 在 `1m / 3m` 仍有可测的回归倾向；但只有当阈值覆盖真实双腿成本，并且 latency 足够低时，才可能留下净 edge。

**可计算定义：**
1. 数据：先拿**公开 BBO / top-of-book**（理想是 `1s` 或 `5s`）；如果临时只拿得到 bar，则先用 `1m` close 做 very rough precheck。
2. gap：
   - `gap_bps_t = (rich_price_t - cheap_price_t) / mid_t * 10,000`
   - rich / cheap 每个时点动态判定。
3. entry：当 `|gap_bps_t| >= max(threshold_static, fee_spread_stack, k * rolling_sigma_gap, q95_gap_asset)` 时开仓。
4. direction：**long cheap venue leg / short rich venue leg**。
5. exit：优先测两种：
   - **收敛退出**：`|gap_bps| <= exit_threshold`
   - **超时退出**：持有 `1m` 或 `3m` 强平
6. sizing：按 `min(depth_cheap, depth_rich)`、venue 限额和 inventory 余量共同决定。

**最小回测切口：**
- 资产：先只做 `BTCUSDT / ETHUSDT / SOLUSDT`
- 频率：`1s/5s` 为主，`1m` 只做粗筛；聚合后看 `1m / 3m / 5m / 15m` 哪个 horizon 还保留 edge
- 样本：最近 `14~30` 天
- venue：先 `Binance / OKX`，再扩到 `Bybit`

**先看 4 个指标：**
- `gross convergence bps`（按 horizon 分桶）
- `net bps after fee+spread`（静态成本先估，之后再上盘口）
- `latency bucket pnl`：`L0 / L1 / L2 / L3`
- `opportunities per day` 与 `capital-at-risk per venue`

**下一步怎么测：**
1. **先做最便宜的粗筛**：拉 `Binance/OKX/Bybit` 的 `1m` close 或 mark，确认 gap 的分布、频次和 next-bar gross 收敛是否存在。
2. **再上真正有意义的频率**：把样本提升到 `1s` 或 `5s` top-of-book，重算 `gap -> next-horizon convergence`，并且显式加入 `L0/L1/L2` 延迟桶。
3. **把 threshold 改成成本感知版本**：不是固定 `1/2/3 bps`，而是 `fee + spread + latency_buffer + z * sigma_gap`。
4. **做两套执行假设并对照**：
   - `inventory-funded`：不依赖即时转账，只看双边库存与风险限额
   - `transfer-cooled`：每次平仓后加 cooldown，验证 repo 里“delay 伤频次、不像 latency 那样直接杀 edge”的结论是否在真实数据还成立。
5. **最后才谈 5m/15m**：如果 `1s/5s/1m` 证明这条线只在快频有效，那 `5m/15m` 应该退到资产选择、仓位上限或是否启用该 alpha 的 regime gate，而不是硬把它伪装成慢频主信号。

## 5. 风险与保留意见
- 这份 repo 的核心证据来自**synthetic market + notebook stress test**，不是 live PnL；它证明的是**机制**，不是收益保证。
- NB04 明确简化了很多关键现实约束：**没有 queue position、没有单腿失配、没有真实 bid/ask crossing、没有真实双边出入金/资金费路径**；因此 notebook 里的正值结果应被视为**理论上界**。
- 我做的 Binance/OKX `1m` close 快检只是一层很粗的 sanity check：它没有盘口、没有撮合、没有真实 entry/exit 价格，只能说明**“gap 回归倾向存在”**，不能说明**“可净赚”**。
- 对这条线最致命的，不一定是方向判断错，而是：**成交太慢、双腿一边先跑、费用高过 gross edge、盘口深度不够、API 抖动**。
- 所以它虽然是 raw alpha，但更像一条**基础设施敏感型 raw alpha**：有条件就很值得做，没有条件就不该自欺欺人地拿 bar close 回测当实盘替身。

## 6. 来源
1. **Meng Ren. (2026). _microstructure-lab_. GitHub repository.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/mengrenman/microstructure-lab>
   - Repo URL: <https://github.com/mengrenman/microstructure-lab>

2. **Meng Ren. (2026). _Notebook 04 — Two-Venue Latency Arbitrage Stress Study_. In `microstructure-lab`.**
   - Venue: GitHub Notebook
   - DOI: N/A
   - Readable URL: <https://github.com/mengrenman/microstructure-lab/blob/main/notebooks/04_two_venue_latency_arb_analysis.ipynb>
   - Repo URL: <https://raw.githubusercontent.com/mengrenman/microstructure-lab/main/notebooks/04_two_venue_latency_arb_analysis.ipynb>

3. **Binance. (2026 access). _Spot API Docs – Market Data Endpoints_.**
   - Venue: Official API Docs
   - DOI: N/A
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints>

4. **OKX. (2026 access). _REST API – Get Candlesticks History / Candlesticks_.**
   - Venue: Official API Docs
   - DOI: N/A
   - Readable URL: <https://www.okx.com/docs-v5/en/#rest-api-market-data-get-candlesticks>
