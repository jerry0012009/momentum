# 15m perp 价格×OI 象限路由：green+OI_up continuation，red+OI_up short veto
- 时间：2026-04-11 04:31 UTC
- 类型：论文 + 公共数据快检
- 主题类型：raw alpha
- 基础 alpha：**单根 `15m` 收益方向 × `open-interest shock` 象限，能把 perp bar 区分成“趋势确认”与“挤仓陷阱”；其中 `green+OI_up` 最像可直接交易的 continuation，`red+OI_up` 更像 short veto / long-fade overlay**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：open-interest / perpetuals / continuation / squeeze / short-veto / binance / 5m / 15m / BTC / ETH / SOL
- 证据类型：论文证据 + 公共数据快检

## 1. 这次看了什么
主线材料是 **Ioannis Giagkiozis, Emilio Said (2024), _Reconciling Open Interest with Traded Volume in Perpetual Swaps_, Ledger**。这篇文章的 headline 不是“给你一个现成 alpha”，而是更基础也更重要的一件事：**先确认 OI 口径能不能信**。作者用 2023 年七家主流交易所 tick 级数据指出：一些大所的 BTC perp open interest 存在系统性错报、延迟记账或清算消息滞后的问题。

这对 desk 的真正启发不是“别看 OI”，而是：**OI 先过数据口径 sanity check，再把它和 bar 方向一起用**。于是这轮我没有把论文硬翻成抽象市场结构评论，而是直接拿 **Binance USDⓈ-M 公共 `openInterestHist + 15m/5m klines`** 做最小快检，看看 **`价格方向 × ΔOI` 象限** 能不能变成一条短周期 raw alpha。

## 2. 核心结论
- **一句话核心结论：** `15m` 上，OI 不是方向神谕，但 **`bar sign × OI shock quadrant`** 的确能路由不同交易模式：
  - `green + OI_up`：最像 **趋势确认 continuation raw alpha**
  - `red + OI_up`：最像 **short veto / long-fade overlay**（新空拥挤，容易被反向 squeeze）
  - `green + OI_down`：在部分大币上更像 **慢一点的 short-covering continuation**
- **一句话证明方式：** 我用 Binance 公共 `7` 个 liquid perp（`BTC/ETH/SOL/XRP/DOGE/BNB/ADA`）近窗 `15m/5m` 数据，按 `ΔOI` 的 rolling MAD z-score 分四象限，发现 **`15m green+OI_up`** 的后续漂移最稳定，而 **`15m red+OI_up`** 明显不该继续追空。
- 本轮最值得 desk 先测的，不是“只要 OI 上升就追”，而是 **先用 OI 给同一根 bar 做语义分类**：这根 bar 到底是趋势确认、长仓挤出、还是新空堆积的 squeeze fuel。
- Binance 公共近窗快检（`7` 个币，`ΔOI z` 阈值先取 `|z| > 1.5`）：
  - **`15m green+OI_up`**：持有 `4` 根（约 `1h`），总计约 `112` 笔、**+26.87 bps/笔 gross**、命中率约 `51.8%`；若只看 `2` 根（约 `30m`），仍有 **+12.00 bps/笔 gross**。
  - **`15m red+OI_up`**：持有 `2` 根时，signed return 约 **-7.23 bps**，命中率仅 **39.4%**；翻成人话就是：**下跌同时 OI 还在明显增加时，继续追空反而更容易吃到反打**。
  - **`15m green+OI_down`**：持有 `8` 根（约 `2h`） aggregate 约 **+23.80 bps**；其中 `BTCUSDT` 单币约 `25` 笔、**+49.32 bps/笔 gross**，更像慢一点的 short-covering continuation。
  - 资产侧不完全对称：`green+OI_up` 的 `1h` continuation 在 `SOL/ETH/XRP/BTC` 上更明显；`red+OI_up` 的 short-veto 在 `ETH/SOL/XRP` 上最明显，`BTC` 则相对没那么极端。

## 3. 为什么和当前项目有关
这不是慢频“情绪指数故事”。它是 **交易所公开可拿、分钟级更新、能直接映射到 perp 方向书** 的 crowding / leverage 语义信号。对当前 `1m/3m/5m/15m` desk，它至少有三种用途：
- 一条独立 raw alpha：`green+OI_up` continuation
- 一条共享 veto：`red+OI_up` 不要机械追空
- 一条附属 pocket：`green+OI_down` 在部分大币可当 slower squeeze-follow

和已有 funding / top-trader / liquidation 线相比，这条线的价值在于：**它只依赖一个最基础、最容易公开获得的 positioning proxy（exchange-wide OI）**，不要求额外抓 trader bucket、资金费率结算窗、或清算地图聚类。

## 3.5 策略拆解（必填）
- 方向属性：顺势为主，兼带一个反身性 veto
- 基础 alpha：`15m green+OI_up` continuation
- regime：优先 liquid majors；当前快检里 `15m` 明显优于 `5m`
- filter / veto：
  - **核心 long**：只做 `ret_15m > 0` 且 `ΔOI_z > 1.5`
  - **short veto**：若 `ret_15m < 0` 且 `ΔOI_z > 1.5`，默认不追空；更适合等下一根确认或直接反向当 long-fade pocket 测
  - **可选第二条 continuation**：`ret_15m > 0` 且 `ΔOI_z < -1.5`，只在 `BTC/SOL/BNB` 先测
- risk / sizing / execution overlay：
  - 持有期先试 `2 / 4 / 8` 根（`30m / 1h / 2h`）
  - 单笔先粗扣 `8~10 bps` round-trip 做 friction ladder
  - 仓位可按 `|ΔOI_z|` 分层，但要设单币上限；因为 `OI` 极端往往伴随波动放大，别把“大信号”误当“可无限加杠杆”

## 4. 可复刻的最小实验
- **研究假设：** 当 `15m` 正收益 bar 同时伴随显著 OI 扩张，它更像新风险入场后的趋势确认；当负收益 bar 同时伴随显著 OI 扩张，它更像新空堆积、后续更容易反打而不是继续流畅下跌。
- **可计算定义：**
  - `ret_15m = close / close[-1] - 1`
  - `dOI = pct_change(sumOpenInterestValue)`
  - `ΔOI_z = robust_zscore(dOI, rolling_median, rolling_MAD, window=96)`
  - 象限先试四类：`green+OI_up`、`green+OI_down`、`red+OI_up`、`red+OI_down`
- **最小回测切口：** Binance USDⓈ-M 公共 `BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT / DOGEUSDT / BNBUSDT / ADAUSDT`；优先跑 `15m`，入场后固定持有 `2/4/8` 根。
- **first verdict（当前）**：
  1. `green+OI_up` 是当前最像 raw alpha 的主线；
  2. `red+OI_up` 不该被包装成“更强下跌确认”，更像 short veto；
  3. `green+OI_down` 值得作为 BTC/SOL 定向 continuation 分支单独再测。
- **最该先看：** 扣 `8/10/12 bps` 后的 `bps/笔` 是否仍存活，以及 `asset × side` 是否稳定；不要强行把一个 OI 规则全币统一开机。

## 5. 风险与保留意见
- **论文本身解决的是 OI 数据可信度，不是直接给 bar-bar alpha。** 这轮是有意识地从 paper 里抽取一个更适合 desk 的旁支：**先过 OI integrity，再做 quadrant router**。
- Binance 公共 `openInterestHist` 是聚合口径，不是逐笔开平仓分类；它能告诉我们“杠杆在变多还是变少”，但不能直接区分到底是谁主动开仓、谁被平仓。
- `5m` 版本当前不够干净：`green+OI_up` 近窗几乎贴近零边，而 `red+OI_up` 更像轻微反打；所以别急着把 `15m` verdict 硬压到 `5m`。
- 这类信号天然带 regime 性：宏观日、单边 squeeze 日、周末薄流动性时会更显著；常态期 edge 可能快速掉到成本线。
- 因为 OI 本身有口径/延迟风险，**建议先加一道数据完整性检查**：若 `|ΔOI|` 与同窗成交量/成交额明显不匹配，宁可跳过该 bar，不要迷信单点数值。

## 6. 下一步怎么测
1. **先把 `green+OI_up` 单独做成可执行壳**：`15m` 入场，`30m/1h/2h` 三档 time-stop，比较 gross / net / MFE / MAE。
2. **做 asset-side admission**：先只留 `BTC/ETH/SOL/XRP` 四个 first verdict 更像 continuation 的币，`BNB/DOGE` 先降级观察。
3. **把 `red+OI_up` 从“做空信号”改成 veto 卡**：拿它去拦已有 breakout-short / jump-follow / panic-short，比较被拦掉的亏损单占比。
4. **加一层 funding / basis 交互**：只问一个简单问题——`green+OI_up` 在 `neutral-to-positive basis` 下是否比 `negative basis` 更能续；如果是，就把 basis 变成二级 filter，而不是 alpha 本体。
5. **做完整性门槛**：先复用 OI-volume reconciliation 思路，过滤掉明显口径失真的 bar，再看 alpha 是否更干净。

## 7. 来源
1. **Giagkiozis, I., & Said, E. (2024). _Reconciling Open Interest with Traded Volume in Perpetual Swaps_. Ledger, 9.**  
   DOI: `10.5195/ledger.2024.325`  
   Readable URL: `https://ledger.pitt.edu/ojs/ledger/article/view/325`  
   说明：本轮实际阅读到摘要与正文可读页；核心用途是给 OI 口径风险和 integrity check 做地基。
2. **Binance USDⓈ-M Futures public endpoints**  
   - `futures/data/openInterestHist`  
   - `fapi/v1/klines`  
   说明：公开可得；`openInterestHist` 提供 `5m/15m/...` 聚合 OI 历史，足够做最小实验。
3. **本地 portability artifacts**  
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_perp_oi_quadrant_router_probe_summary_2026-04-11.csv`  
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_perp_oi_quadrant_router_probe_detail_2026-04-11.csv`

## 8. 数据源 / 公开性 / 更新频率 / 最小复现实验口径
- **数据源**：Binance USDⓈ-M Futures 公共 API
- **公开性**：公开，无需私钥
- **更新频率**：可直接请求 `5m / 15m` OI 历史聚合；K 线同样公开
- **最小可复现实验口径**：
  - universe：`BTC/ETH/SOL/XRP/DOGE/BNB/ADA`  
  - bar：`15m`  
  - signal：`ret_15m` 与 `ΔOI_z` 四象限  
  - holding：`2 / 4 / 8` bars  
  - cost：先粗扣 `8~10 bps` round-trip  
  - verdict：先做 `green+OI_up` raw alpha，再把 `red+OI_up` 作为 short veto 单独评估
