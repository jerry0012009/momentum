# 别把“科技股带 crypto”只读成日频相关：这篇 2025 JIFMIM 论文更该先测的是「QQQ+NVDA 同向冲击 → BTC/ETH 1h 跟随」跨资产 raw alpha
- 时间：2026-03-27 16:50 UTC
- 类型：2025 *Journal of International Financial Markets, Institutions and Money* 论文摘要证据 + Yahoo Finance 公共 `15m` 本地 quick check
- 主题类型：raw alpha
- 基础 alpha：**美股科技龙头（尤其 `QQQ` / `NVDA`）在美股现金时段的同向极端 `15m` 冲击，会在接下来 `1h` 内向 BTC / ETH 传导出同向 follow-through；对 desk 最可落地的版本不是“长期配 beta”，而是 `US cash-session cross-asset lead-lag`。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-asset/lead-lag/us-tech/qqq/nvda/btc/eth/session-overlap/15m/1h/momentum/follow-through/paper/external-data
- 证据类型：论文摘要 + 本地公共数据最小迁移快检

> 先回答 base alpha：**这是 raw alpha，不是单纯 filter。** 论文 headline 是“科技股与 crypto 有 mutual predictability”，但对我们 desk 更值钱的读法，不是继续停在日频相关，而是把它 desk 化成一条可以在 `15m / 1h` 上快速验证的跨资产 lead-lag：**当 `QQQ` 和 `NVDA` 在美股现金时段同向打出极端 bar，BTC / ETH 往往会在后面 2~4 根 `15m` bar 把方向补进去。**

## 1. 这次看了什么
这次主看：

1. **Elie Bouri, Amin Sokhanvar, Harald Kinateder, Serhan Çiftçioğlu (2025)**, *Tech titans and crypto giants: Mutual returns predictability and trading strategy implications*, *Journal of International Financial Markets, Institutions and Money*.  
   - DOI: `10.1016/j.intfin.2024.102109`  
   - DOI URL: `https://doi.org/10.1016/j.intfin.2024.102109`
2. 本地 quick check：
   - 数据源：Yahoo Finance Chart API（公开可得）
   - 标的：`QQQ`、`NVDA`、`BTC-USD`、`ETH-USD`
   - 频率：`15m`
   - 样本：最近 `60d`，对齐美股现金时段 `13:30~20:00 UTC`
   - 产物：`reports/artifacts/quant_digest_us_tech_crypto_leadlag_15m/`

这篇 paper 的 headline 很直白：**美国科技板块 / 半导体 / Nvidia 和大 crypto 之间存在显著的双向收益预测关系，基于 cross-quantilogram 的策略跑赢 benchmark。**

但按当前 desk 的偏好，最该先偷的不是“互相有关”这句大话，而是更窄、更工程化的一条：

- **谁更适合当 intraday leader？** `QQQ` 和 `NVDA`
- **谁更适合当 lagging follower？** `BTC` 和 `ETH`
- **什么时段最自然？** 美股现金盘和 crypto `24/7` 的重叠时段
- **什么信号最便于最小复现？** `15m` 极端同向 leader shock 后的 `1h` crypto 跟随

## 2. 核心结论
- **一句话核心结论：** 这篇东西最值得 desk 先落地的，不是“科技股和 crypto 长期耦合”，而是 **`QQQ + NVDA` 同向极端 `15m` 冲击后，BTC / ETH 在后续 `1h` 出现同向 follow-through** 这条跨资产 raw alpha。
- **一句话它怎么证明：** 论文在日频上证明 **美国科技 / 半导体 / Nvidia 对 BTC / ETH / DOGE 存在显著正向预测力，且策略优于 always-long benchmark**；我用公开 `15m` 数据做的最小迁移快检显示，这个关系在最近 `60d` 的美股现金时段里，至少在 **双 leader 同向极端 bar** 的 pocket 上仍能看到。

更 desk 化地说：
1. 不是所有 tech move 都值得追；
2. **单 leader 有信号，双 leader 同向更像可交易 pocket；**
3. ETH 对这类 shock 的放大通常比 BTC 更明显；
4. 真正该测的是 `US cash-session overlap`，而不是把日频论文硬抄成全天候 always-on 策略。

## 3. 3 个关键数据点
1. **论文摘要直接给了可交易含义。** 作者写得很明确：**U.S. tech / semis / Nvidia 对 crypto returns 的预测力在多个 quantiles 与 lags 上显著成立，且据此构造的 trading strategy 跑赢 benchmark。**
2. **本地 `15m` quick check 里，`QQQ+NVDA` 同时 top-decile 上冲后的 `1h`，BTC / ETH 有正向 follow-through。** 在最近 `60d`、美股现金盘重叠样本里：
   - `BTC`：后 `4` 根 `15m` 平均 **`+13.0 bps`**，命中率 **`58.2%`**；
   - `ETH`：后 `4` 根 `15m` 平均 **`+15.2 bps`**，命中率 **`56.4%`**。  
3. **反向 pocket 也成立，而且 ETH 更强。** `QQQ+NVDA` 同时 bottom-decile 下挫后：
   - `BTC`：后 `1h` 平均 **`-15.0 bps`**；
   - `ETH`：后 `1h` 平均 **`-20.7 bps`**。  
   这说明它不是只能做 long-on-risk-on，也能做 **short crypto on coordinated tech shock**。

补一个次级数据点：即使不用双 leader，**`NVDA` 单独 top-decile `15m` bar 后，BTC / ETH 后 `1h` 也分别有约 `+10.2 / +13.0 bps`**，说明 Nvidia 本身就像一个强 leader，而不是纯粹 `QQQ` beta。

## 4. 为什么和当前短周期 desk 有关
### 4.1 它服务的是哪类 raw alpha
- 分类：**cross-asset / lead-lag / momentum follow-through raw alpha**
- 不是：
  - 纯解释型相关性 paper
  - 纯 regime gate
  - 纯宏观叙事素材

### 4.2 它补的是素材池哪块缺口
最近 digest 已经积了不少：
- crypto 内部 lead-lag
- pairs / stat-arb
- funding / carry / basis
- event-clock

但**“外部风险资产 leader → crypto follower”** 这块可直接工程化的 `15m / 1h` 口袋还不算多，尤其是：
- leader 很清楚（`QQQ` / `NVDA`）
- 时段很清楚（US cash session）
- follower 很清楚（`BTC` / `ETH`）
- 最小实验很清楚（同向极端 bar 后看 `2~4` 根 `15m`）

这比再写一篇泛泛“risk-on 对 crypto 有影响”更有用，因为它已经接近完整策略骨架了。

## 5. desk 化后的最小策略草图
## 5.1 信号定义
先做最小可复现版本：

- 频率：`15m`
- leader：`QQQ`、`NVDA`
- follower：`BTC perp`、`ETH perp`
- 交易时段：仅 `13:30~20:00 UTC`
- leader shock：
  - `QQQ` 当根 `15m` 收益进入滚动 `20~40` 交易日同钟点分布的 top / bottom decile
  - `NVDA` 同时也进入对应方向 decile
- 方向：
  - 两者都极强上涨 → 做多 BTC / ETH
  - 两者都极强下跌 → 做空 BTC / ETH

## 5.2 entry / exit
- **entry**：leader bar 收盘后、下一根 crypto `15m` bar 开盘附近进场
- **holding**：先固定持有 `4` 根 `15m`（`1h`）
- **early exit**：
  - 若下一根 `QQQ` / `NVDA` 明显反抽/反弹，提前减半或平仓
  - 若 crypto 在前 `2` 根 bar 已走完 `0.8~1.0 x` 预期波幅，可分批止盈

## 5.3 sizing
- 初版别做复杂：
  - `BTC` / `ETH` 各半，或按逆波动配重
  - 单次事件总风险预算 `25~50 bps` NAV
- 若后续发现 ETH edge 更高但噪音也更大，可改成：
  - `BTC 40% / ETH 60%`
  - 或只在 `NVDA` shock 特别强时加 ETH 权重

## 5.4 risk / veto
下面这些 veto 必须加：
1. **只做美股现金盘重叠，不做亚洲时段硬套。**
2. **只做双 leader 同向版本作为 primary。** 单 leader 先留作 secondary。 
3. **FOMC / CPI / NFP / Powell 讲话前后先禁做。** 否则 leader 可能只是宏观 headline 的共振噪音。  
4. **若 crypto 已先于 leader bar 提前走出同方向大波动，放弃追单。** 这条线赚的是 delayed follow-through，不是末端接力。  
5. **若美股 leader bar 主要出现在收盘前最后一根，单独拆 bucket。** close auction 结构和普通 cash-session bar 不一样。  

## 5.5 cost
- 这条线 gross edge 目前大概在 `10~20 bps / 1h` pocket；
- 所以第一轮成本别瞎乐观，至少要跑：
  - `BTC`: round-trip `4 / 6 / 8 bps`
  - `ETH`: round-trip `5 / 7 / 10 bps`
- 如果净后只剩几 bps，必须继续加：
  - stronger shock threshold
  - double-confirmation (`QQQ+NVDA`)
  - overlap-only veto

## 6. 本地 quick check 读法（要诚实）
我这次只做了**非常轻量的 transfer check**，不是正式回测：
- 数据来自 Yahoo Finance，而不是交易所逐笔或官方历史接口；
- 样本只有最近 `60d`；
- 还没做 funding、perp basis、真实成交价、盘口冲击；
- 还没把 `QQQ`、`NVDA` 的 shock 强度标准化到 rolling same-clock z-score。

所以现在只能说两件事：
1. **这个想法没有立刻死掉；**
2. **它最像一个“US overlap 口袋 alpha”，不是全天候 always-on 因子。**

## 7. 下一步怎么测
按优先级直接往下做：

1. **换成官方源重做。**  
   - `QQQ` / `NVDA`：Polygon / Alpaca / Nasdaq Data Link / 券商 API 任一稳定源  
   - `BTC` / `ETH`：Binance / OKX / Bybit perp `1m` 或 `5m`
2. **做更像 desk 的事件标准化。**  
   不要只看全样本 decile；要做 **rolling same-clock percentile / z-score**，避免把 open 与午盘混成一锅。  
3. **拆 leader 结构。**  
   跑：
   - `QQQ only`
   - `NVDA only`
   - `QQQ+NVDA both`
   - `semis ETF (SOXX/SMH) + NVDA`
4. **拆 follower。**  
   跑：
   - `BTC only`
   - `ETH only`
   - `BTC/ETH equal-weight basket`
   - 高 beta alt basket（只在有足够流动性和成本余量时）
5. **正式成本与滑点压力测试。**  
   至少看 `4 / 6 / 8 / 10 bps` round-trip 后，edge 是否仍主要保留在：
   - 双 leader 同向
   - 更强 quantile cut
   - 后 `2~4` 根 bar，而不是第一根乱跳
6. **做宏观事件剔除。**  
   把 FOMC / CPI / NFP / Powell / NVDA 财报日单独剔出来，看 alpha 是靠平时稳定 pocket，还是只靠 event day。  

> **最该先测的正式版本：** `US cash-session`, `15m`, `QQQ+NVDA same-direction extreme bar -> BTC/ETH 1h follow-through`，先跑 `2024-01` 以来的滚动样本外，配 `6~8 bps` round-trip friction。若净后仍活，再往 `5m` 细化；若只在财报 / 宏观事件日有效，就把它降级成 event overlay，而不是主策略。

## 8. 文件与产物
- 研究笔记：`research/quant_digests/2026-03-27_1650_us-tech-crypto-cash-session-followthrough-alpha.md`
- quick check 产物目录：`reports/artifacts/quant_digest_us_tech_crypto_leadlag_15m/`
- 核心结果表：`reports/artifacts/quant_digest_us_tech_crypto_leadlag_15m/signal_summary.csv`
- 元数据：`reports/artifacts/quant_digest_us_tech_crypto_leadlag_15m/meta.json`

## Sources
1. **Bouri, E., Sokhanvar, A., Kinateder, H., & Çiftçioğlu, S. (2025). _Tech titans and crypto giants: Mutual returns predictability and trading strategy implications_. Journal of International Financial Markets, Institutions and Money.**  
   - DOI: `10.1016/j.intfin.2024.102109`  
   - DOI URL: `https://doi.org/10.1016/j.intfin.2024.102109`
2. **OpenAlex abstract metadata for the above article.**  
   - URL: `https://api.openalex.org/works?search=Tech%20titans%20and%20crypto%20giants%3A%20Mutual%20returns%20predictability%20and%20trading%20strategy%20implications`
3. **Yahoo Finance Chart API**（本地最小迁移快检数据源）  
   - 示例：`https://query1.finance.yahoo.com/v8/finance/chart/QQQ?range=60d&interval=15m`
   - 示例：`https://query1.finance.yahoo.com/v8/finance/chart/NVDA?range=60d&interval=15m`
   - 示例：`https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=60d&interval=15m`
   - 示例：`https://query1.finance.yahoo.com/v8/finance/chart/ETH-USD?range=60d&interval=15m`
