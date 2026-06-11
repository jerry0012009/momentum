# 别把跨交易所同币价差当“看见就赚”：这份 2026 C++ 仓库更该先测的是 `fee cliff + latency budget` 的 spatial-arb raw alpha
- 时间：2026-03-24 09:36 UTC
- 类型：2026 GitHub 新仓库 + 近 5 年论文 + Binance/OKX 公共盘口最小快检
- 主题类型：raw alpha
- 基础 alpha：同一资产在不同交易所的瞬时报价偏离（spatial spread）回归 / 收敛
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/spatial-arbitrage/cross-exchange/orderbook/latency/execution/cost/1m/3m/5m/15m/repo/paper
- 证据类型：工程证据 + 论文证据 + 公开数据快检

## 1. 这次看了什么
先回答 base alpha：**这条线的 base alpha 不是“趋势判断”，而是同币跨所报价短时错位会回归。**

这次主看：
- 2026 新仓库 **Ra1nForest/Crypto_HFT_Engine**（C++17，多线程、双所 order book、fee-adjusted arbitrage detector）；
- 2025 论文 **Werapun et al.** 的跨交易所自动套利（CEX/DEX 路由思路）；
- 2023 论文 **Shu et al.** 的 Binance/Coinbase 跨 venue 价差事件证据；
- 外加一组本地公开 API 最小快检（Binance + OKX，ETHUSDT）。

## 2. 核心结论
- **一句话核心结论：** 这条 raw alpha 的关键不是“是否存在价差”，而是“价差能不能跨过手续费+延迟+冲击这道生存线”；在我们这轮公开盘口快检里，答案偏保守。  
- **一句话证明方式：** repo 给出可执行的实时骨架（order book→spread→fee-adjusted 判定），我用 Binance/OKX 公共 top-of-book 做 120 点快检，直接对比 `gross spread` 与 `post-fee spread`。

关键数据点：
1. **工程可行性（repo）**：orderbook 更新 benchmark 从 `862ns` 到 `48ns`（约 **18x**），解析延迟给到 `p50 8~15us`、`p99 <100us`（仓库 README 声明口径）。
2. **公开盘口快检（本地）**：120 个样本（0.5s 采样，ETHUSDT），`best gross spread` 均值约 **0.95 bps**、`p95 ≈ 1.95 bps`、最大约 **2.41 bps**。
3. **成本生存线**：按 round-trip **4 bps** 起算，`positive_after_4bps_ratio = 0`；8/12/20 bps 同样为 0，说明“看得见价差”并不等于“可交易利润”。

## 3. 为什么和当前项目有关
这轮仍然是 **raw alpha**，且能直接补 desk 的 `relative value / stat-arb` 素材池，不是继续在固定形态里打转。

它的价值在于：
- 能和当前 `pairs / basis / funding` 线形成互补：都属于 market-neutral 家族，但这条是更偏 execution/microstructure 的“短半衰期”版本；
- 可直接拆成完整策略组件，不是只有过滤层：entry/exit/sizing/risk/cost 全都能写清；
- 可以自然映射到 `1m/3m/5m/15m`：
  - `1m/3m` 先看机会密度与成本后存活率；
  - `5m/15m` 适合验证“低频化后是否还能保留可交易边际”。

## 3.5 策略拆解（必填）
- 方向属性：relative value / stat-arb（双边对冲）
- 基础 alpha：同币跨交易所报价偏离回归（spatial arbitrage）
- regime：高流动、高更新频率、跨所连接稳定时更有效；事件时段可能放大机会也放大风险
- filter / veto：
  - `gross_spread <= fee + slippage_buffer` 直接 veto
  - orderbook 深度不足、盘口单边空洞、连接延迟飙升时 veto
- risk / sizing / execution overlay：
  - 双腿名义对齐、单笔 participation 上限
  - 信号 TTL（超时即弃单）
  - 失败重试上限与单 venue 风险上限
  - 成本阶梯（maker/taker、滑点、冲击）必须实时计入

## 4. 可复刻的最小实验
### 4.1 数据源 / 公开性 / 更新频率
- Binance Spot `bookTicker` / depth：公开 API，秒级到百毫秒级可取
- OKX `market/ticker` / books：公开 API，秒级到百毫秒级可取
- 主题主要依赖外部盘口数据，但它本身就是 raw alpha（不是伪装 filter）

### 4.2 最小实验口径（先做 1m，再扩 3m/5m/15m）
1. 标的：`ETHUSDT`（Binance）vs `ETH-USDT`（OKX）
2. 信号：
   - `s1 = (okx_bid - bin_ask) / bin_ask * 1e4`
   - `s2 = (bin_bid - okx_ask) / okx_ask * 1e4`
   - `edge = max(s1, s2)`
3. 交易开关：仅当 `edge > fee_total + slippage_buffer + latency_buffer` 才允许入场
4. 出场：
   - spread 回归到 `exit_threshold`
   - 或 TTL 到期（强制平）
5. 先看指标：
   - `post-fee bps/trade`
   - `opportunity_survival_ratio`（过成本线的机会占比）

### 4.3 本轮快检产物
- `reports/artifacts/quant_digests/spatial_cross_exchange_probe_20260324/summary.json`
- `reports/artifacts/quant_digests/spatial_cross_exchange_probe_20260324/samples.csv`

## 5. 风险与保留意见
- 这类 alpha 半衰期短，**延迟预算**和**真实成交概率**往往比预测逻辑更关键。  
- 公开 top-of-book 不等于可成交深度，若不加 depth 与冲击约束，容易高估收益。  
- 单纯“看到正价差”并不够，必须先过成本门；本轮快检显示在常见 fee 档位下几乎全灭。  
- 因此它更像“需要强执行条件才可能存活”的 raw alpha，不应被当作低门槛策略。

## 6. 下一步怎么测（明确动作）
1. **从 top-of-book 升级到 depth-5/10**：把可成交量引入 edge 计算，重算 post-fee 生存线。  
2. **加入延迟仿真**：对每个机会强制 +100ms/+300ms/+500ms 执行延迟，看幸存率如何塌陷。  
3. **多标的扩展**：`BTC/ETH/SOL` 三组并行，比较机会频次与容量。  
4. **时间尺度映射**：把机会事件聚合到 `1m/3m/5m/15m`，确认哪些频段仍能留住净边际。

## 7. 来源
1. **Ra1nForest. (2026). _Crypto_HFT_Engine_. GitHub Repository.**  
   - Repo URL: https://github.com/Ra1nForest/Crypto_HFT_Engine  
   - Readable URL: https://github.com/Ra1nForest/Crypto_HFT_Engine/blob/main/README.md
2. **Werapun, W., Boonpeam, N., Sangiamkul, E., & Suaboot, J. (2025). _The Automated Arbitrage Strategy of Cross-Cryptocurrency Exchanges_. International Journal of Information Technology & Decision Making.**  
   - DOI: `10.1142/S0219622025500130`  
   - Readable URL: https://doi.org/10.1142/S0219622025500130
3. **Shu, A., Cheng, F., Han, J., Liang, Z., & Pan, Z. (2023). _Arbitrage across different Bitcoin exchange venues: Perspectives from investor base and market related events_. Accounting & Finance.**  
   - DOI: `10.1111/acfi.13102`  
   - Readable URL: https://doi.org/10.1111/acfi.13102
4. **Binance Spot API Docs / OKX API Docs（公开市场数据接口）**  
   - Binance: https://developers.binance.com/docs/binance-spot-api-docs  
   - OKX: https://www.okx.com/docs-v5/en
