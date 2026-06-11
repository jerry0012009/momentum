# 别再把 BTC lead-lag 只当 shared gate：这份 2026 新仓库更值得先测的是「BTC 5m shock → alt basket delayed follow-through」完整 raw alpha
- 时间：2026-03-24 05:54 UTC
- 类型：2026 GitHub 新仓库 + 近 5 年论文地基 + 代码规则拆解
- 主题类型：raw alpha
- 基础 alpha：BTC 在 `5m` 内出现足够大的单边冲击后，alt basket 会在接下来 `15m~30m` 里发生带方向的延迟跟随 / 反身修复；方向由 `7d/3d` BTC regime 决定
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-market/lead-lag/btc/alt-basket/intraday/momentum/reversal/regime/entry-exit/sizing/cost/repo/paper/crypto/1m/3m/5m/15m
- 证据类型：仓库 README + 配置/回测脚本代码 + 论文地基

## 1. 这次看了什么
先回答 base alpha：**这不是 filter，本体就是 cross-market lead-lag raw alpha**。

这轮不再把 `Cross-Market Intraday Time-Series Momentum` 只读成“能不能给现有 15m 三条线当 shared gate”，而是顺着一份新的 2026 仓库 `mamipour/lead-lag-trader`，把它改读成更适合我们 desk 的版本：

**当 BTC 在 `5m` 内先发生足够大的冲击时，直接交易 alt basket 在随后 `15m~30m` 的延迟反应。**

这比继续把它硬塞成 `breakout / retest / EMA` 的外接确认层更符合当前 intake 优先级，因为它本身就能写成完整策略：`entry / exit / sizing / risk / cost` 都清楚。

## 2. 核心结论
- **一句话结论：** 这条线值得进 raw-alpha 素材池，而且最该先测的不是“BTC 先动能不能给所有策略放行”，而是 **`BTC 5m shock -> alt basket delayed follow-through` 这个 standalone alpha 本体**。  
- **一句话怎么证明：** 新仓库已经把它写成完整骨架：按 BTC `5m` 冲击触发、用 `7d/3d` regime 区分 bear-short 与 bull-dip-buy、给出固定持有时长、篮子交易、杠杆上限、黑窗与成本假设。

关键数据点（以仓库公开回测口径为准，尚未做本地独立复核）：
1. 回测区间 `2022-04 -> 2026-03`，仓库报告组合从 **$10,000 -> $47,839（+378%）**，年化约 **49%**。  
2. 同期报告 **25,230 笔 alt 交易**、**55% 胜率**、**47.1% 最大回撤**，滚动 `6M` 窗口 **13/14** 为正。  
3. 若按 `19` 个 alt 同步开仓粗算，约等于 **0.92 次事件/天**；也就是说它不是高频噪声刷单，更像“低频触发、成组出手”的短周期事件 alpha。  

## 3. 为什么和当前项目直接相关
- 它直接补的是 **raw alpha**，不是再补一个解释层。  
- 它正好接住我们最近的学习缺口：`trend / momentum` 之外，短周期里还需要一个 **cross-market / leader-laggard** 家族的可执行骨架。  
- 它与 `LEARNING_TRACK` 里“先吸收成熟策略范式、先做单因子/单策略诚实验证”的方向一致：规则短、状态清楚、参数不多、可直接拉公共数据做最小实验。  
- 它也符合 `RECENT_PAPER_SEEDS` 对 `Cross-Market Intraday Time-Series Momentum` 的定位：**更贴近 intraday / cross-market / 更短周期**。  

## 3.5 策略拆解（必填）
- 方向属性：cross-market / leader-laggard / intraday event alpha  
- 基础 alpha：BTC 先动，alt 对同一冲击存在短时延迟反应；在不同 regime 下，反应方向不完全一样  
- regime：
  - `bear`：BTC `7d return <= -5%`，做 **alt short follow-through**
  - `bull`：BTC `7d return >= 0%` 且 `3d return >= 0%`，做 **dip-buy rebound / overshoot**
  - `neutral`：不开机
- filter / veto：
  - bear 侧跳过 `BTC 5m drop > 2%` 的极端 crash（防 bounce-back）
  - UTC `07~11` 黑窗不做
  - bull 侧要求 `BTC 3d return >= 0%`
- risk / sizing / execution overlay：
  - bear 侧杠杆随跌幅在 `1x~2x` 间缩放
  - bull 侧固定 `1x`
  - 统一 basket 分配、统一固定持有时长、统一成本入账

## 4. 仓库里真正值得偷的规则骨架
### 4.1 Bear 分支：BTC dump -> short alt basket
- 触发：`BTC 5m return <= -1.0%`
- 失效上限：若 `BTC 5m drop > 2.0%`，直接跳过
- 环境：`BTC 7d return <= -5%`
- 动作：同时做空 `19` 个 alt futures
- 持有：`15m`
- 仓位：按 BTC 跌幅从 `1x` 线性放大到 `2x`

翻成人话：
**在熊市里，BTC 的快速下跌更像“领导先砸”，alt 会在后面补跌；但如果 BTC 已经砸得太狠，就不追，怕接到短时反抽。**

### 4.2 Bull 分支：BTC dip -> long alt basket
- 触发：`BTC 5m return <= -0.5%`
- 环境：`BTC 7d return >= 0%` 且 `BTC 3d return >= 0%`
- 动作：同时做多 `19` 个 alt futures
- 持有：`30m`
- 仓位：`1x`

翻成人话：
**在牛市里，BTC 的急跌更像流动性踩踏后的短时折价，alt 往往不是继续补跌，而是跟着修复甚至超调。**

### 4.3 成本与交易载体
- 数据抓取：Binance `1m` / `5m` 公共 OHLCV
- live paper trade：Kraken Futures 公共 WebSocket
- 成本口径：maker `0.02%/side` + slippage `1bp/side`

这点很重要：
**它不是一句“有 lead-lag”就结束，而是已经把 data / trigger / holding window / fee/slippage / live paper plumbing 串起来了。**

## 5. 与 `1m/3m/5m/15m` 的关系
- `1m`：用于数据采样与实时监控最自然；但如果直接逐分触发，容易过拟合到单次 wick。  
- `3m/5m`：最适合做 **formation window**；仓库主触发就是 `5m BTC shock`。  
- `15m`：最适合承接 bear 分支持有窗，也是我们 first verdict 最容易复核的频率。  
- `30m`：bull 分支当前更像 `15m` 的延长 holding，而不是另起一套主框架。  

所以对当前 desk 的正确定位是：
**这条线不是 15m 共享 gate，而是一个 `5m formation -> 15m/30m monetization` 的 standalone short-horizon raw alpha。**

## 6. 最小可复现实验口径
- 数据源：Binance USDⓈ-M Futures klines（公开 REST）
- 公开性：公开可得
- 更新频率：`1m` / `5m` bar，可直接映射我们关心的 `1m/3m/5m/15m`
- 最小实验建议：
  - leader：`BTCUSDT perp`
  - followers：先别一口气上 `19` 个，先用流动性更好的 `ETH / SOL / BNB / XRP / DOGE / ADA`
  - formation：`BTC 5m return` 阈值（bear `-1.0%`，bull `-0.5%`）
  - regime：`BTC 7d` 与 `3d` return
  - execution：signal bar close 后 `next bar open`
  - exit：固定 `15m` / `30m`
  - cost：先跑 `4 / 8 / 12 bps round-trip`，再加 basket 冲击近似

## 7. 下一步怎么测（必须）
1. **先做 desk 缩版 first verdict**：只跑 `BTC -> 6 个大/中流动性 alt`，比较 `bear_short / bull_dipbuy / dual-regime` 三臂。  
2. **先验真假分开看**：不要先看累计收益，先看 `event count / hit rate / average post-cost return / cross-asset breadth`。  
3. **做 formation 宽度扫描**：把 BTC 触发从 `-0.4/-0.6/-0.8/-1.0/-1.2%` 分层，看是不是存在“太弱没用、太强反而反抽”的非线性区间。  
4. **做 follower 分层**：大市值 vs 中市值 vs meme 分层，检验这个 alpha 是否主要来自 beta 放大，而不是稳定 lead-lag。  
5. **把 basket 改成 ranking 版**：不是每次都全买/全卖 `19` 个，而是只做最近 `20~40` 天里对 BTC 冲击最敏感的 top-K laggards，测试能否显著降成本、提纯 edge。  
6. **补交易可行性**：把仓库乐观的 `maker+1bp` 扩成更接近 desk 的 `crossed fill / partial fill / participation cap` 场景；如果一改成本就塌，这条线只能留在素材池，不能升 shadow。  

## 8. 风险与保留意见
- 当前强证据主要来自 **新仓库自报回测**，还不是我们本地独立 clean replication。  
- 仓库 `0 star / 2026-03-18 新建`，信号新鲜但也意味着**外部社会验证几乎没有**。  
- 它用 Binance 历史数据回测，却把 live paper trade 放在 Kraken Futures，存在 **cross-venue microstructure mismatch**。  
- 回测成本假设偏乐观；若真是 basket 同时成交，实盘冲击可能显著高于 `maker 2bp + 1bp slippage/side`。  
- `47.1%` 最大回撤不低，说明即便方向对，也不是“低波稳健套利”，更像高波动事件策略。  

## 9. 来源
1. **Mamipour, M. (2026). _lead-lag-trader_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/mamipour/lead-lag-trader  
   - Repo URL: https://github.com/mamipour/lead-lag-trader  
2. **Mamipour, M. (2026). _README.md / src/paper/config.py / scripts/simulate_6months.py_（仓库内策略说明与回测脚本）.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/mamipour/lead-lag-trader/main/README.md  
   - Repo URL: https://github.com/mamipour/lead-lag-trader/blob/main/src/paper/config.py  
3. **Xu, D., Li, B., Singh, T., & Li, J. (2023). _Cross-Market Intraday Time-Series Momentum_. SSRN Electronic Journal / Working Paper.**  
   - Venue: SSRN Electronic Journal  
   - DOI: https://doi.org/10.2139/ssrn.4651331  
   - Readable URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4651331  
   - Repo URL: N/A  
4. **Binance Developers. _USDⓈ-M Futures Market Data: Kline/Candlestick Data_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data  
   - Repo URL: N/A  
5. **Kraken. _Futures WebSocket API / public market data_（用于仓库 paper-trading 口径）.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://docs.kraken.com/api/docs/futures-api/websocket/introduction/  
   - Repo URL: N/A
