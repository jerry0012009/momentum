# 别把这份 2026 Hyperliquid perp bot 只读成“BTC 布林带脚本”：对 short-cycle crypto desk，更该先保留的是「EMA200 顺势下的外轨触碰回归 × opposite-band maker exit」这条完整 raw alpha 壳
- 时间：2026-04-19 21:32 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/perps_trading.py` + `tests/test_signals.py` + `tests/test_stop_logic.py` + `config/accounts.json`）+ Binance USDⓈ-M `15m/5m` portability probe（`BTC/ETH/SOL`）
- 主题类型：raw alpha
- 基础 alpha：**顺着大趋势做小波动均值回归**；更直白点说，`EMA200` 还没坏时，价格短暂戳穿 Bollinger 外轨，后面更容易先回到带内、再朝对侧 band 修复一段
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/mean-reversion/trend-filter/bollinger-band/ema200/opposite-band-exit/maker-first/hyperliquid/binance-perpetual/5m/15m/repo/public-data/cost/risk/shell
- 证据类型：仓库源码规则 + 公共 K 线最小探针

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 很清楚，是 raw alpha，而且是能直接落地成完整策略的那种。**

主材料是 GitHub 仓库 **`vitor-chagas/dex-trading-bot`**（创建于 `2026-03-21`，Python）。repo 自己给出的核心壳很完整：
- `5m` K 线；
- **LONG**：价格触到/跌破下轨，且价格仍在 `EMA200` 上方；
- **SHORT**：价格触到/突破上轨，且价格仍在 `EMA200` 下方；
- 入场是**挂在 band 上的限价单**；
- 止盈是**对侧 band**；
- 止损是**固定百分比 stop**；
- band 漂移到不利于当前仓位时，退出会降到**保本**；
- sizing 直接由 `target_risk_pct / leverage / stop_loss_pct` 算出来。

这就不是“有个 signal，别的你自己补”的半成品，而是把 **entry / exit / stop / maker-vs-taker / sizing / live-loop** 都写出来了。

更关键的是，repo README 里把它说成“Bollinger Band mean-reversion strategy with EMA trend filter”，而源码/测试把交易逻辑拆得很干净：
- `tests/test_signals.py` 明确测了 **下轨+EMA 上方做多 / 上轨+EMA 下方做空**；
- `tests/test_stop_logic.py` 明确测了 **固定 stop** 和 **inverted band → breakeven**；
- `src/perps_trading.py` 里则把这条线包成了 **maker-first 的完整执行壳**。

对 desk 来说，真正值得 intake 的不是“又一个 BB 策略”，而是：
> **顺大势、吃小过冲、用对侧 band 做动态回补退出。**

## 2. 核心结论
- **一句话结论：** 这条线值得保留成 **完整 raw alpha 壳**，而不是只记成“布林带回归”。
- **一句话证据：** 我把 repo 的 entry / exit 骨架搬到 Binance USDⓈ-M 公共 `15m/5m` 数据上做最小 portability probe，结果显示：**`15m` 版更稳，`5m` 版要给它更长一点持有窗才像真 edge。**

最关键的数据点（均为**扣除 roundtrip `8 bps` 成本后**）：
1. **`15m` all-signals，持有 `4` bars（约 `1h`）**：`n=2870`，`mean≈+2.5 bps`，胜率约 `52.4%`。  
2. **`15m` all-signals，持有 `8` bars（约 `2h`）**：`n=2870`，`mean≈+4.2 bps`，胜率约 `54.0%`。  
3. **`15m` all-signals，持有 `12` bars（约 `3h`）**：`n=2870`，`mean≈+4.5 bps`，胜率约 `54.9%`。  
4. **`5m` all-signals，持有 `6` bars（约 `30m`）**：`n=4820`，`mean≈-1.2 bps`，说明太快拿利润不够。  
5. **`5m` all-signals，持有 `12` bars（约 `1h`）**：`n=4820`，`mean≈+0.8 bps`，刚过盈亏平衡。  
6. **`5m` all-signals，持有 `24` bars（约 `2h`）**：`n=4820`，`mean≈+6.4 bps`，胜率约 `64.1%`，是这轮 probe 最像 pocket 的窗口。  
7. **`5m / 24-bar` 分币结果**：`BTC≈+6.1 bps`、`ETH≈+3.6 bps`、`SOL≈+9.5 bps`，说明这条线不只在 BTC 上站得住。

保守一点读，这组结果在说：
- **这不是超短 30 分钟 scalp edge**；
- 它更像 **`15m` parent shell**，或者 **`5m` 上但愿意拿到 `~2h` 的顺势回归壳**；
- 对我们当前 short-cycle desk 来说，最值钱的是它把 **trend filter + mean reversion + dynamic band exit + maker-first execution** 串成了一个完整组件。

## 3. 为什么和当前 desk 直接相关
这轮值得保留，不是因为“又遇到一个均值回归”，而是因为它刚好补的是我们现在需要的那种 **完整策略壳**：
- **base alpha 清楚**：顺着长趋势，去接短时过冲；
- **entry 清楚**：触下轨/上轨 + `EMA200` 方向过滤；
- **exit 清楚**：优先回到对侧 band，不行就 stop，band 漂坏了就保本；
- **execution 清楚**：band 上挂单、maker-first；
- **sizing 清楚**：risk target / leverage / stop 三者联动；
- **适合 5m/15m 最小实验**：全都能用公开 K 线先做低成本验证。

换句话说，这条线不是“解释文”，而是已经足够像一个 **可实盘拆件**：
你可以把 signal 留着，也可以直接把 execution/exit/sizing 抽出来给别的 mean-reversion 家族复用。

## 3.5 策略拆解（必填）
- 方向属性：单资产、trend-filtered mean-reversion、双向
- 基础 alpha：**长趋势没坏时，短时价格对 Bollinger 外轨的过冲会向带内回归，并有机会继续修复到对侧 band**
- regime：更适合**非瀑布式单边趋势**、而是“趋势还在，但短时甩出过冲”的行情
- filter / veto：
  - `EMA200` 是主过滤：只做顺势那一边；
  - 如果 band 太窄，回归空间可能不够吃成本；
  - 如果市场进入强单边加速，外轨触碰可能不是过冲，而是趋势继续加速
- risk / sizing / execution overlay：
  - 固定 stop（repo README 提 `2.5%`，配置里也出现 `3%~4%` 变体）
  - 对侧 band 动态止盈
  - inverted target 时切到 breakeven
  - maker-first 限价挂单
  - sizing 可由 `target_risk_pct / (leverage × stop_pct)` 直接算

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A（主策略来源）：GitHub 公开仓 `vitor-chagas/dex-trading-bot`
- 数据源 B（代理回测数据）：Binance USDⓈ-M 公共 `klines`，无需 API key
- 更新频率：`5m / 15m` K 线公开可取
- 最小实验口径：
  - 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
  - 参数：`BB(20, 2)` + `EMA200` + `2.5%` stop
  - LONG：`low <= lower_band` 且 `close > EMA200`
  - SHORT：`high >= upper_band` 且 `close < EMA200`
  - 退出：先看对侧 band 是否被打到；若先 hit stop 则止损；若到时限仍未打到则 `time stop`
  - 成本：roundtrip 统一先扣 `8 bps`
  - `15m`：持有 `4 / 8 / 12` bars
  - `5m`：持有 `6 / 12 / 24` bars

### 4.2 这组快检怎么读
- **`15m` 比 `5m` 更像 parent shell。** 它在 `1h~3h` 都还能留正净值，不像很多 15m 假信号那样一拉长就死掉。  
- **`5m` 不是不能做，但不能太急。** `30m` 基本不够，`1h` 只是刚过线，愿意拿到 `2h` 时才开始有明显 pocket。  
- **这条线不靠超级低频外部数据。** 光用公开 K 线就能先做最小复现，因此非常适合作为素材池里的“快速验证壳”。

## 5. 为什么这次不把它降级成 filter / overlay
因为这里最核心的问题“到底做什么”已经完全说得清楚：
> **顺着 EMA200 的大方向，在价格戳到 Bollinger 外轨时反向接回归，优先吃回到对侧 band 的那一段。**

这本身就是完整的 raw alpha 叙事，不是单纯在告诉你“市场不好别做”或“仓位要缩小”。
而且 repo 把 **entry / exit / stop / sizing / execution** 都给了，所以它比一般“只给信号、不给交易结构”的素材更值得优先 intake。

## 6. 下一步怎么测
1. **先做 band-width gate。** 当前 probe 没有用最小带宽过滤，下一轮应直接测 `band_width_pct` 分桶，看窄带假信号能不能被砍掉。  
2. **做 maker-fill realism。** 现在默认“触 band 就能成交”，下一步要把“挂单后 1 bar 内是否真成交、挂多久撤单”补进去。  
3. **把 `15m parent + 5m child execution` 拆开。** 比起直接拿 `5m` 裸做，也许更该用 `15m` 决定方向与 admission，再在 `5m` 里做更细的挂单和止损。  
4. **测 stop 宽度梯度。** 比较 `2.0% / 2.5% / 3.0% / 4.0%`，因为 repo README 和 live config 已经暗示这条线对 stop 宽度很敏感。  
5. **补 funding / OI veto。** 当外轨触碰发生在极端去杠杆/追杠杆时，顺势回归可能会退化成“接飞刀”或“逆势抄顶”。  
6. **区分 BTC 与 alt。** 当前 probe 显示 SOL pocket 最强，说明这条线可能该按波动属性分参数，而不是全币同参。

## 7. 风险与保留意见
- 这轮是 **repo skeleton portability probe**，不是对作者 Hyperliquid live bot 的逐条成交复刻。  
- 当前 probe 没有真正模拟 **maker queue priority / 未成交撤单 / funding / exchange fee tier**，所以实盘净值会更保守。  
- 这条线和我们已经收集过的 `envelope / lower-band / oversold fade` 家族是近亲；但它的独特价值在于：**退出逻辑和执行逻辑明显更完整**，值得单独存成策略壳。  
- 如果未来发现主要收益只来自更长持有，而不是 band 触碰本身，那它就更应被重命名成“trend-filtered pullback shell”，而不该继续包装成纯 intrabar BB edge。

## 8. 来源
1. **Vitor Chagas. (2026). _dex-trading-bot_. GitHub repository.**  
   - Year: 2026  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/vitor-chagas/dex-trading-bot  
   - Repo URL: https://github.com/vitor-chagas/dex-trading-bot
2. **Source audit files**  
   - README: https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/README.md  
   - Trading logic: https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/src/perps_trading.py  
   - Signal tests: https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/tests/test_signals.py  
   - Stop logic tests: https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/tests/test_stop_logic.py  
   - Live config: https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/config/accounts.json
3. **Public data probe**  
   - Binance USDⓈ-M public `klines` endpoint（无需 API key）

## 9. 本地产物
- Probe 脚本：`reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_probe.py`
- `5m` 事件面板：`reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_5m_events.csv`
- `5m` 汇总：`reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_5m_summary.csv`
- `5m` router 事件（实验性）：`reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_5m_router_top1_events.csv`
- `15m` 事件面板：`reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_15m_events.csv`
- `15m` 汇总：`reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_15m_summary.csv`
- `15m` router 事件（实验性）：`reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_15m_router_top1_events.csv`
- JSON 汇总：`reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_summary.json`
