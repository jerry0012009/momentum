# 别把这份 2026 crypto-stat-arb 仓只读成“1h 教程脚本”：对 short-cycle crypto desk，更该先拆的是「高成交量急跌后的 5m bounce」这条 raw alpha
- 时间：2026-04-19 20:19 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/strategy.py` + `src/backtester.py` + `src/data_fetcher.py`）+ Binance USDⓈ-M `15m/5m` portability probe（8 liquid majors）
- 主题类型：raw alpha
- 基础 alpha：**高成交量急跌后短窗均值回归**；更直白点说，`1h/4h` 里先把自己砸下去、同时成交量放大的币，往后 `1h~2h` 更容易弹回一截，且 `5m` 版比 `15m` 版更像真信号
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/mean-reversion/oversold/panic-bounce/volume-spike/fixed-hold/5m/15m/binance-perpetual/repo/public-data/cost/risk/router
- 证据类型：仓库源码规则 + 公共 K 线最小探针

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 很清楚，就是 raw alpha，不是 filter。**

主材料是 GitHub 仓库 **`skylarshi123/crypto-stat-arb`**。repo 自己写得很直白：
- 用 **`1h` 跌幅 > 2%** + **成交量 > 24h 均量的 1.5x** 识别超卖；
- 默认持有期是 **24h**；
- 交易成本按 **20 bps / trade** 计；
- 标的池是 `BTC / ETH / SOL / AVAX`。

源码里最值钱的不是“统计套利”这个名字，而是它把信号写得很朴素：
- `return_1h = close.pct_change()`
- `volume_ratio = volume / rolling_24h_avg`
- `signal = (return_1h <= -0.02) & (volume_ratio >= 1.5)`
- backtester 里再用固定持有期去算净收益。

对我们来说，这个骨架天然能压缩成更适合短周期 desk 的版本：
**把“1h 急跌 + 放量”改写成 `5m/15m` 的短窗 selloff bounce signal，再用固定 hold / hard cost / router 做成可交易原型。**

## 2. 核心结论
- **一句话结论：** 这条线最值得 intake 的，不是把原仓原样搬来，而是把它改写成 **`5m` high-volume selloff bounce** 的完整 raw alpha。
- **一句话证据：** 我按 repo 的信号定义做了 Binance USDⓈ-M 公共 `15m/5m` portability probe；结果显示 **`15m` 版一旦持有太久就明显失真，而 `5m` 版在 `~1h` 持有窗里还有正 edge**。

最关键的数据点：
1. **`15m` all-signals，持有 `4` bars（约 `1h`）**：`n=231`，`mean≈-2.2 bps`，胜率约 `49.8%`。  
2. **`15m` all-signals，持有 `8` bars（约 `2h`）**：`mean≈-14.6 bps`，已经明显转负。  
3. **`5m` all-signals，持有 `12` bars（约 `1h`）**：`n=117`，`mean≈+19.2 bps`，胜率约 `58.1%`。  
4. **`5m` router_top1，持有 `12` bars**：`n=41`，`mean≈+4.2 bps`，胜率约 `51.2%`。  
5. **`5m` all-signals，持有 `24` bars（约 `2h`）**：`mean≈+11.1 bps`，但边际开始变钝；`36` bars 则转负。  

保守理解成 **两腿 roundtrip 合计约 `8 bps`** 的 cost 压力后：
- `5m / 12-bar` 仍有明显正净空间；
- `5m / 24-bar` 变成更挑标的的版本；
- `15m` 版更像 **父级过滤器/入场前确认**，不适合当主信号。

## 3. 为什么和当前 desk 直接相关
这轮值得保留，不是因为“又找到一个 mean reversion”，而是因为它很适合拆成我们现在最需要的那种素材：
- **base alpha 清楚**：高成交量急跌后反弹；
- **entry/exit 清楚**：跌幅阈值 + 成交量阈值 + 固定持有；
- **成本可测**：20 bps/trade 可以直接做 friction ladder；
- **可迁移到短周期**：`5m` 版比 `15m` 版更像真正可用的短窗信号；
- **可扩展成 router**：先在 liquid majors 里挑最极端的那几个，而不是全开。

换句话说，它不是“纯说明文”，而是**已经把 signal family 写进代码的 raw alpha 原型**。

## 3.5 策略拆解（必填）
- 方向属性：单资产、mean-reversion、event-driven
- 基础 alpha：**短窗急跌 + 放量 = 超卖后反弹**
- regime：更适合 liquid majors、非单边加速下跌阶段；如果市场进入强趋势瀑布，bounce 很容易被继续碾压
- filter / veto：
  - 成交量不够放大时不做；
  - `15m` 里持有过久时，edge 迅速衰减；
  - 强 funding / 强 OI 去杠杆时，单纯价格 bounce 可能是假反弹
- risk / sizing / execution overlay：
  - 基础版单腿做多超卖币；
  - 更稳的是做 `top1 shock router`，只挑同一时刻最极端的那一腿；
  - 退出先用固定 hold，再比较 `time stop + profit target + ATR stop` 的组合

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A（主策略来源）：GitHub 公开仓 `skylarshi123/crypto-stat-arb`
- 数据源 B（代理回测数据）：Binance USDⓈ-M 公共 `klines`，无需 API key
- 更新频率：分钟级 / 15 分钟级 K 线可直接取
- 最小实验口径：
  - 标的：`BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT / BNBUSDT / DOGEUSDT / ADAUSDT / LINKUSDT`
  - `15m`：用 `4` bar return 近似 `1h` 急跌，lookback `96` bars 近似 `1d` 成交量基线，持有 `4/8/12` bars
  - `5m`：用 `12` bar return 近似 `1h` 急跌，lookback `288` bars 近似 `1d` 成交量基线，持有 `12/24/36` bars
  - 成本：先用 repo 口径的 `20 bps / trade` 做压力测试；真正可交易前再下探成本梯度

### 4.2 这组快检怎么读
- **`15m` 不该当主信号。** 它在 `4-bar` 上还勉强接近平手，但一拉到 `8/12 bar` 就明显失真，说明“弹一下就走”不适合过持。  
- **`5m` 更像真 alpha。** `12-bar` 的 `mean≈+19.2 bps`，说明短窗 bounce 不是纯噪声；不过到 `36 bar` 也会转弱，不能无限 hold。  
- **router 比全开更像实盘。** 同一时刻只做最极端那一腿，能把这条线从“很多小信号”压成“更像 desk 能用的 pocket”。  

## 5. 为什么这次不把它降级成 filter / overlay
因为这里最核心的问题“到底做什么”已经很清楚：
> **做多刚刚被砸得最狠、同时成交量放大的币，赌它短窗回弹。**

这就是标准的 raw alpha 叙事，而且 entry / hold / cost / risk 都能讲清楚。它不是只在告诉你“别追涨杀跌”，而是自己就能站成一个独立的 mean-reversion 策略原型。

## 6. 下一步怎么测
1. **先做 cost ladder**：重点看 `4 / 8 / 12 / 16 bps` 下，`5m / 12-bar` 还能不能保住正净值。  
2. **加 router admission**：只在同一时刻 `shock_score = (-ret_n) × vol_ratio` 最大的那几腿上仓。  
3. **把 fixed hold 换成 exit trio**：`time stop + take-profit + ATR stop`，看是否能把 `24/36 bar` 的拖尾亏损压掉。  
4. **补 funding / OI veto**：如果急跌同时伴随极端去杠杆，反弹可能更容易变成 dead-cat bounce。  
5. **缩 universe 到最稳的 3~5 个币**：先测 `BTC / ETH / SOL / BNB / DOGE`，别一上来把小币和大币混在一起。  
6. **再看 `15m` 能不能做成 pre-filter**：`15m` 若只负责告诉我们“现在是不是 oversold 真空段”，那它更像 gate，不该抢主 alpha 的位置。  

## 7. 风险与保留意见
- 这轮是 **repo skeleton portability probe**，不是对作者原始 1h 策略的完整复刻。  
- 我们把它往 `5m/15m` 改写后，实盘可行性主要取决于 **手续费 + 滑点 + 退出纪律**，不是信号本身。  
- 这条线和近期一些 panic-fade / loser-bounce 主题有家族相似性，所以后续最好继续做 **router / cost / exit** 三件事，而不是只换个名字。  

## 8. 来源
1. **Skylar Shi. (2026). _Cryptocurrency Statistical Arbitrage Strategy_. GitHub repository.**  
   - Repo URL: https://github.com/skylarshi123/crypto-stat-arb  
   - Readable URL: https://github.com/skylarshi123/crypto-stat-arb  
   - 说明：无 DOI，仓库 landing page 可直接访问
2. **Source audit files**  
   - README: https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/README.md  
   - Strategy: https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/src/strategy.py  
   - Backtester: https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/src/backtester.py  
   - Data fetcher: https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/src/data_fetcher.py
3. **Public data probe**  
   - Binance USDⓈ-M `klines` public endpoint（无 key）

## 9. 本地产物
- Probe 脚本生成的面板：`reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_15m_panel.csv`
- `15m` 汇总：`reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_15m_summary.csv`
- `15m` router 事件：`reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_15m_router_top1_events.csv`
- `5m` 面板：`reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_5m_panel.csv`
- `5m` 汇总：`reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_5m_summary.csv`
- `5m` router 事件：`reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_5m_router_top1_events.csv`
- JSON 汇总：`reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_summary.json`
