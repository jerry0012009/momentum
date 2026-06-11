# 别把这份 Hyperliquid×Pacifica 机器人只读成“资金费率看板”：对 short-cycle desk，更该先拆的是「predicted funding spread × liquidity+price-spread veto」这条完整 raw alpha 壳

- 时间：2026-04-16 05:38 UTC
- 类型：2025/2026 GitHub repo source audit（`README.md` + `bot_config.json` + `hyperliquid_pacifica_hedge.py` + `fetch_funding_rates_public.py`）+ Hyperliquid/Pacifica public API portability probe
- 主题类型：raw alpha
- 基础 alpha：**跨交易所 delta-neutral carry：每轮选 `|next funding APR 差|` 最大且通过流动性/价差门槛的币，对低 funding 交易所做多、对高 funding 交易所做空，持有到 funding 窗口后退出**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（baseline 级完整壳）
- 主题标签：raw-alpha/carry/funding/cross-venue/relative-value/stat-arb/delta-neutral/predicted-funding/net-apr/liquidity-filter/price-spread-veto/worst-leg-stop/hyperliquid/pacifica/1m/3m/5m/15m/repo/public-api/cost/risk
- 证据类型：repo + public-api probe

## 1) 先回答：这篇东西的 base alpha 是什么？

一句话：**base alpha 不是“机器人框架”，而是“下一 funding 周期的跨 venue funding spread carry（delta-neutral）”。**

也就是：
- 先比较 Hyperliquid 与 Pacifica 的 **predicted/next funding**；
- 对 funding 更低的一侧做多、funding 更高的一侧做空；
- 靠 funding spread 收益，而不是赌方向。

## 2) 来源信息（repo-based）

- **Authors：** GitHub `@djienne`（仓库维护者）
- **Year：** 2025（repo 创建）/ 2025-11（最近主要代码更新）
- **Title：** *Hyperliquid-Pacifica Cross-Exchange Funding Rate Delta Neutral Bot*
- **Venue：** GitHub repository
- **DOI：** N/A（仓库）
- **Readable URL：** <https://github.com/djienne/CROSS_EXCHANGE_DELTA_NEUTRAL_HYPERLIQUID_PACIFICA>
- **Repo URL：** <https://github.com/djienne/CROSS_EXCHANGE_DELTA_NEUTRAL_HYPERLIQUID_PACIFICA>

## 3) 这轮 intake 拆出的“可直接复现策略壳”

从源码可还原出一条很清晰的流程：

1. **信号层（alpha body）**
   - 使用两边 **predicted funding**（不是历史已结算 funding）
   - 计算 `net_apr = |APR_hl - APR_pacifica|`
   - 决策：`long low-funding exchange / short high-funding exchange`

2. **admission / veto 层（不是 alpha 本体）**
   - `min_net_apr_threshold = 5%`
   - Pacifica 24h 成交额过滤：`>= 50M USD`
   - 跨交易所价格偏离过滤：`<= 0.15%`

3. **执行与持有层**
   - 默认 `hold_duration_hours = 8`（对齐 funding 周期）
   - `wait_between_cycles_minutes = 5`

4. **风险层**
   - 动态 stop-loss（按杠杆映射）
   - 关键点：stop-loss 以 **worst leg**（最差腿）触发，而不是只看净和，防单腿风险扩张

这已经是 `entry/exit/sizing/risk/cost` 都能落地的一条完整 raw alpha 壳。

## 4) public-data portability probe（本轮快检）

### 4.1 数据源与公开性

- Hyperliquid public API：`/info`（predictedFundings / allMids）
- Pacifica public API：`/api/v1/info`、`/api/v1/kline`
- **公开性：**公开可访问，无需私钥（快检口径）
- **更新频率：**funding 与行情为准实时/高频更新；kline 可用于近 24h 流动性估算

### 4.2 本轮快检产物

- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/hl_pacifica_probe_20260416_0536/funding_volume_probe.json`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/hl_pacifica_probe_20260416_0536/funding_volume_probe.csv`

### 4.3 关键数据点（2026-04-16 05:36 UTC 快照）

在有双边 predicted funding 的 `13` 个符号里：

1. **只有 1 个符号同时通过 `net_apr>=5%` + `vol>=50M` 联合门槛：ETH**
   - ETH：`net_apr ≈ 16.23%`，Pacifica 24h volume `≈ $398.87M`（通过）
2. **PUMP 的 net_apr 虽高（≈27.54%），但 volume 仅 ≈$2.09M（被 veto）**
3. **SOL 接近边界：net_apr ≈6.36%，但 volume ≈$49.04M，低于 50M 门槛（被 veto）**

这三个点很重要：
- 说明该壳并不是“看到高 APR 就冲”；
- 流动性 veto 能显著压掉看起来很肥但不可交易的候选；
- 在短周期 desk 里，这种 admission 比盲目扩币池更值钱。

## 5) 与 `1m/3m/5m/15m` 的关系（怎么映射）

这条策略天然是“事件驱动 + 短周期执行”：

- **信号更新频率：**funding 预测刷新节奏（非逐 bar）
- **执行层频率：**可在 `1m/3m/5m` 做下单、补腿、风控监控
- **持有层：**以 `8h` funding 窗口为主，可在 `15m` 做 PnL 与风险巡检

所以它不是纯 `1m` 方向信号，而是标准的 **carry/stat-arb raw alpha + short-cycle execution shell**。

## 6) 最小可复现实验口径（可直接开跑）

1. Universe：`BTC/ETH/SOL/BNB/XRP`（先 liquid）
2. 每小时（或每 30m）抓取 predicted funding，构造 `net_apr` 排序
3. admission：
   - `net_apr >= 5%`
   - Pacifica 24h volume >= 50M
   - cross-venue mid/mark spread <= 0.15%
4. 进场：long low-funding / short high-funding，名义资金对等
5. 出场：
   - `hold 8h` 到点平仓
   - 或 worst-leg stop-loss 触发提前平仓
6. 评估（必须 post-cost）：
   - funding 收入
   - 双腿 taker/maker fee
   - 开平滑点
   - 失败补腿惩罚（单腿敞口）

## 7) 下一步怎么测（本轮结论后的直接动作）

1. **先做 friction ladder（最优先）**
   - 成本档位：`6 / 10 / 14 bps`（单边综合）
   - 看 `net_apr` 门槛是否要从 5% 上调到 8%/12%

2. **把 volume 门槛做成分层，而不是硬阈值**
   - `>=200M`：正常仓位
   - `50M~200M`：半仓
   - `<50M`：禁入

3. **做“跨 venue 价差持续时间” veto**
   - 不只看瞬时 `<=0.15%`，而是要求过去 `N` 分钟大部分样本也在阈值内
   - 避免开仓时刚好遇到短时错价

4. **加入强制 flatten 审计**
   - 记录每次 close 后两腿剩余名义敞口
   - 把“名义 delta-neutral”变成“审计可验证 delta-neutral”

---

## 参考

1. `djienne/CROSS_EXCHANGE_DELTA_NEUTRAL_HYPERLIQUID_PACIFICA` repo: <https://github.com/djienne/CROSS_EXCHANGE_DELTA_NEUTRAL_HYPERLIQUID_PACIFICA>
2. Hyperliquid public API（predicted fundings）: <https://api.hyperliquid.xyz/info>
3. Pacifica public API（market info / kline）: <https://api.pacifica.fi/api/v1/info> , <https://api.pacifica.fi/api/v1/kline>
