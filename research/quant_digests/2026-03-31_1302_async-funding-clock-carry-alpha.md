# 别把 Hyperliquid×Bybit funding carry 继续写成普通跨所利差：这份 2024/2026 GitHub repo 更该先测的是「asynchronous funding clock × net-hour hurdle」完整 raw alpha

- 时间：2026-03-31 13:02 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/carry/funding/perp-perp/cross-venue/relative-value/stat-arb/asynchronous-settlement-clock/net-hour-normalization/hyperliquid/bybit/delta-neutral/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：2024/2026 GitHub 仓库元数据 + `README.md` / `docs/strategy.md` / `docs/risk-management.md` / `src/strategy/funding_arb.py` source audit + Hyperliquid / Bybit 公共 funding API live sanity check

- 主题类型：raw alpha
- 基础 alpha：同一币种在 Hyperliquid 与 Bybit perpetual 上的 funding 现金流差，按统一日化/小时口径归一后做 delta-neutral cross-venue carry
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主看的是 **gabrielee5/funding-arbitrage** 这个公开仓库。它表面上像一个“执行面板”，但真正值得 desk 拿走的不是 UI，而是它把 **Hyperliquid 1h funding** 和 **Bybit 8h funding** 放进了同一个可执行框架里：

- 同币种双 perp、双边对冲；
- `min(HL_balance, BB_balance)` 做 sizing；
- 分 tranche 同步下单；
- 一条腿出事，另一条腿立刻 emergency close；
- 风险不是抽象“市场波动”，而是 **异步 funding 时钟 + 一腿成交另一腿没成交 + 单腿先爆仓**。

所以它不是“又一个 funding 看板”，而是一个已经能落成 **entry / execution / sizing / risk / monitor** 的完整 raw alpha 骨架。

## 2. 为什么这次值得进研究池
这轮 bot7 默认优先级里，`可独立复现且可直接落地完整策略` 高于纯解释型材料。这个主题值得 intake，不是因为“funding carry 很新”，而是因为它补的是我们当前素材池里相对少的一块：

1. **base alpha 很清楚**：alpha 本体不是 filter，不是 overlay，就是 **同 underlier、不同 venue 的 funding cashflow spread**。
2. **这份 repo 有真正可迁移的 execution OS**：不是只给一个 ranking 表，而是给了 tranche、保护单、balance cap、linked exit。
3. **它和已有 generic funding digest 不完全重复**：这次新增的关键细节是 **异步结算时钟**。很多 funding 笔记默认两边都是同一个 8h 钟点；这份仓库明确处理的是 `HL 1h` vs `Bybit 8h`，这决定了我们不能只看一个静态 funding diff，而要看 **未来持有窗口里到底能收几次、付几次**。

## 3. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = 同一资产在不同 venue perpetual 上的净 funding spread，经统一时钟归一后，做 market-neutral carry。**

写成最简单的方向判断：
- 若做 **`short HL / long BB`**，粗口径日化 gross carry 近似是 `24 × f_HL - 3 × f_BB`；
- 若做 **`long HL / short BB`**，则是 `3 × f_BB - 24 × f_HL`；
- 选 gross carry 更大的那一边，再扣掉开平仓成本、basis 漂移预算、滑点预算。

所以它是 **carry / relative-value / stat-arb raw alpha**，不是只给 trend 策略加一个 funding veto。

## 4. 核心来源
### 4.1 主仓库
- **Authors / Org**：GitHub `gabrielee5`
- **Year**：仓库创建于 2024-12-21，2026-03-31 仍在更新
- **Title**：*funding-arbitrage*
- **Venue**：GitHub Repository
- **DOI**：无
- **Readable URL**：https://github.com/gabrielee5/funding-arbitrage
- **Repo URL**：https://github.com/gabrielee5/funding-arbitrage
- **本次重点审阅文件**：
  - `README.md`
  - `docs/strategy.md`
  - `docs/risk-management.md`
  - `src/strategy/funding_arb.py`

### 4.2 公开数据 / 文档来源
1. **Hyperliquid Docs / Public API**
   - Readable URL：https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
   - 本次实际使用：`POST https://api.hyperliquid.xyz/info` with `{"type":"metaAndAssetCtxs"}`
   - 公开性：公开 REST，无需登录
   - 更新频率：近实时

2. **Bybit V5 Market API**
   - Readable URL：https://bybit-exchange.github.io/docs/v5/market/tickers
   - 本次实际使用：`GET /v5/market/tickers?category=linear&symbol=...`
   - 公开性：公开 REST，无需登录
   - 更新频率：近实时

## 5. 证据里最值得拿走的硬点
### 5.1 这份 repo 不是只讲概念，它已经把整套交易壳写明白了
仓库文档直接给出：
- **支持对冲腿**：Hyperliquid × Bybit perp-perp；
- **默认标的**：`BTC / ETH / SOL / ARB / DOGE / WIF / PEPE / LINK / AVAX / OP`；
- **sizing**：`available_capital = min(HL_available_balance, BB_available_balance)`；
- **默认 tranche**：`3` 档；
- **默认 tranche offset**：`10 bps`；
- **fill timeout**：`60s`；
- **grace period**：`30s`；
- **默认 max leverage**：`3x`；
- **默认 max allocation**：`50%`；
- **monitor 轮询**：每 `5s` 检查一次仓位与保护单。

这几个数字很重要，因为它说明这条线不是“先证明 alpha，再慢慢补 execution”，而是 **strategy shell 已经存在**。

### 5.2 真正新信息不是 funding diff，而是「不同 funding 结算时钟」
repo 写得很明确：
- **Hyperliquid funding：每 1 小时结算一次**；
- **Bybit funding：每 8 小时结算一次（00:00 / 08:00 / 16:00 UTC）**。

对 desk 的正确翻译不是“把 1h rate 和 8h rate直接摆一排”，而是：
- 先统一到同一个口径（小时或日化）；
- 再根据计划持有时长 `H`，计算 **未来窗口内实际会发生几次 HL funding、几次 BB funding**；
- 最后才决定这笔 carry 是不是够厚。

换句话说，**静态 diff 只是候选池；真正 entry 该看的是 forward carry over holding window**。

### 5.3 这份 repo 把最致命的风险说对了：不是方向错，而是单腿活下来、另一腿死掉
`docs/risk-management.md` 最值得拿走的不是“风控很重要”这种废话，而是两条很具体的规则：

1. **linked SL/TP**
   - 用各自实际 liquidation price 反推出 stop；
   - 一边 stop 触发，另一边按对应价格 take-profit / emergency close；
   - 目标不是赚更多，而是避免一腿清算、另一腿裸奔。

2. **one-leg fill mismatch 先处理，再谈省手续费**
   - 一条腿 fill、另一条腿没 fill 时，先接受 market unwind 也可以；
   - 因为 funding carry 的核心风险不是多花一点手续费，而是临时暴露成方向仓位。

这非常适合我们 desk：carry 类 alpha 最容易死在“执行时不够诚实”，这份 repo 至少在原则上是诚实的。

### 5.4 本地 live quick check：当前重叠 10 个币里，真正够厚的窗口并不多
我用 Hyperliquid `metaAndAssetCtxs` 和 Bybit `v5/market/tickers` 对 repo 的 10 个重叠币做了一个极简快检，把 funding 统一成日化 gross carry，再选更优方向。

结果文件：
- `reports/artifacts/quant_digests/hl_bybit_funding_clock_normalized_20260331_1302.csv`

当前快照里：
- **AVAX**：最佳方向 `short HL / long BB`，gross carry 约 **4.60 bps/day**；
- **WIF**：最佳方向 `short HL / long BB`，gross carry 约 **3.79 bps/day**；
- **DOGE**：约 **2.52 bps/day**；
- **ETH**：约 **0.88 bps/day**；
- **BTC**：几乎没有，只剩 **0.02 bps/day**。

这几个数的直观翻译：
- 若你假设一笔对冲头寸全成本约 **10 bps**，那当前大概需要：
  - **AVAX ~2.17 天** 才能回本；
  - **WIF ~2.64 天**；
  - **ETH ~11.32 天**；
  - **BTC ~418 天**，基本没法看。

所以这条线的正确用法不是 `always-on carry`，而是：
- **做 event-driven / pocket-driven carry**；
- 只在少数币、少数窗口里开；
- 并且必须把持有期也写进 entry。

## 6. 对 crypto 1m / 3m / 5m / 15m 的正确读法
### 6.1 它是 raw alpha，但不是“逐根 K 线方向预测”
这类策略的 alpha 本体是 funding cashflow，不是下一根 return sign。

所以对 `1m / 3m / 5m / 15m` desk，更合理的分层是：
- **signal / decision layer**：每 1m 或 5m 扫 funding、basis、盘口、可成交量；
- **execution layer**：按短周期盘口去分 tranche、控 slippage；
- **carry realization layer**：真正兑现 alpha 发生在接下来的若干 funding 结算点。

别把它硬伪装成“每根 5m bar 都该有预测力”的主观趋势信号。

### 6.2 短周期里最值得测的，不是 generic rank，而是「forward holding-window carry」
我认为 first-pass 应该把 entry 改写成：

`expected_net_carry(H) = funding_cashflow_over_next_H - open_close_cost - basis_drift_budget - slippage_budget`

只在 `expected_net_carry(H) > 0` 时开仓。

这比单纯比较 `current_funding_diff` 更适合 desk，因为：
- HL 每小时结一次；
- BB 每 8 小时结一次；
- 同一个“当前 diff”，在 **距离下一个 Bybit funding 还剩 7h50m** 和 **还剩 10m** 时，真实价值差很多。

### 6.3 对 1m/3m/5m/15m 最自然的迁移方式
- **1m / 3m**：更适合做执行与盘口 veto，不适合频繁换币轮动；
- **5m**：最适合做 live scanner + expected carry refresh；
- **15m**：适合做持有期、成本、净额统计与 boundary bucket 回测。

换句话说，这条 alpha 的“交易频率”未必高，但它的 **research / scan / execution cadence** 完全可以是 1m~15m。

## 7. 如果把它落成完整策略，应该怎么写
### 7.1 Entry
对每个重叠币、每个方向，计算：

1. **统一口径 funding edge**
   - `gross_edge_day(direction)`
2. **未来持有窗口的 funding 现金流**
   - 用下一次 HL / BB funding 时间算未来 `H` 小时内会发生几次收付
3. **成本预算**
   - 开仓 + 平仓 fee
   - 预估滑点
   - basis / mark-oracle 偏离预算
4. **盘口 veto**
   - 若盘口太薄、双边价差过宽、或一边 API 不稳定，则放弃

first pass 可直接用：
- `H = 24h / 48h / 72h` 三档；
- 只有 `expected_net_carry(H) > 0` 才开；
- 同时要求 `basis_gap_z` 不要太极端，避免赚 funding、亏 basis 回归。

### 7.2 Exit
至少三种 exit：
1. **净 carry 失效**：`expected_net_carry(H_remaining) <= 0`
2. **basis / premium 失控**：mark-oracle gap 或跨所价差超过风控阈值
3. **时间止盈 / 止损**：达到计划 funding 窗口数后平仓，不恋战

不要只写“funding 反转就平”，因为很多时候 **carry 还没反转，但已经不够覆盖 close cost**。

### 7.3 Sizing
直接继承 repo 最合理的部分：
- 资本基数用 `min(HL_balance, BB_balance)`；
- 单笔不超过可用资本的 `25%~50%`；
- 再叠加一个 **volatility / liquidity scalar**：
  - BTC/ETH 可以更高；
  - WIF/PEPE/ARB 之类应更低；
- 单腿 notional 与单 narrative exposure 设 hard cap。

### 7.4 Risk
最关键的四个：
- **one-leg fill mismatch**：超过 `grace_period` 优先去掉裸 exposure；
- **linked protective orders**：避免一腿清算；
- **venue health**：任一 venue WebSocket / API 异常，不再开新仓；
- **clock risk**：不要在临近低流动时段硬开，需要单独记录不同 funding boundary 的 fill quality。

### 7.5 Cost
这条线的研究成败几乎全靠成本诚实度：
- fee tier
- maker/taker mix
- 开平两次滑点
- 资金占用与持仓期间的 basis 漂移
- 极端行情时的跨所不同步

如果成本写得太乐观，这条 alpha 会看起来“几乎一直能做”；真实情况下并不是。

## 8. 对当前 desk，最值得先测的不是“大而全”，而是这 3 个最小实验
### 实验 A：统一口径 funding scanner（必须先做）
- 数据源：Hyperliquid `metaAndAssetCtxs` + Bybit `v5/market/tickers`
- 频率：每 `5m`
- 输出：
  - `gross_edge_day`
  - `expected_net_carry_24h / 48h / 72h`
  - `best_direction`
  - `days_to_recoup_10bps / 20bps`
- 目标：先知道到底哪些币、哪些时段值得看。

### 实验 B：Bybit funding boundary bucket test（这轮最该补）
- 数据源：同上 + 1m mid/mark/basis 快照
- 频率：`1m`
- 切桶：距离 Bybit funding 结算 `[-60m, -30m, -10m, +10m, +30m, +60m]`
- 问题：同样的 normalized carry，**在 Bybit funding 前后开仓** 的 realized PnL / fill quality / close cost 是否不同？
- 目标：验证“异步时钟”到底是不是可交易的 admission layer。

### 实验 C：execution honesty replay
- 数据源：1m order book top-of-book / bid-ask spread / trade notional proxy
- 频率：`1m`
- 问题：用 repo 的 `3 tranche + 10bps offset + 60s timeout`，实际能不能在 10 个币里诚实成交？
- 目标：防止 paper edge 全被成交摩擦吃掉。

## 9. 下一步怎么测
1. **先把 `expected_net_carry(H)` 扫描器落地**：别再只看 static funding diff。至少先跑 `H=24/48/72h`。  
2. **补一份 1m boundary 数据集**：围绕 Bybit `00/08/16 UTC` 前后各 60 分钟抓 funding / mark / spread / top-of-book。  
3. **把 repo 风控参数照搬成 first baseline**：`3x leverage`、`25 bps liquidation buffer`、`3 tranches`、`60s timeout`、`30s grace`，先别自己发明。  
4. **先做 10 个 repo 支持币，不要一上来全市场**：这条线更像 pocket alpha，不像全市场 always-on rank。  
5. **在回测里强制写 2 套成本**：一套乐观 maker-heavy，一套保守 taker-heavy；没有双成本对照，这个方向很容易自欺。  

## 10. 一句话结论
这份 Hyperliquid×Bybit repo 真正值得拿走的，不是“funding carry 还能做”这种老话，而是：**把 cross-venue funding carry 明确改写成“异步 funding 时钟下、按未来持有窗口计价的完整 raw alpha”**。当前 live 快照也说明它不是大票息常开策略——更像少数币、少数窗口、需要 execution honesty 的 pocket carry。
