# 别把这份 2026 Hyperliquid quant dashboard 只读成“信号看板”：对 short-cycle crypto desk，更该先拆的是「cross-sectional overextension top-vs-bottom fade」这条 raw alpha
- 时间：2026-04-19 19:06 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `app/reversion/page.tsx` + `app/api/signals/route.ts` + `lib/calc/reversion.ts` + `lib/calc/relative-strength.ts` + `lib/data/hyperliquid.ts`）+ Hyperliquid public `15m/5m` portability probe（10 liquid majors）
- 主题类型：raw alpha
- 基础 alpha：同一时刻里，**短窗最“涨多了且贴近上轨”的币**，后续更容易跑输 **最“跌多了且贴近下轨”的币**；把它做成 top-vs-bottom market-neutral spread，比单腿追空/抄底更适合当前 desk
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/mean-reversion/overextension/bollinger-position/return-zscore/top-vs-bottom/router/hyperliquid/15m/5m/repo/public-data/cost/risk
- 证据类型：仓库源码规则 + 公共 API 最小探针

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 很清楚，就是 raw alpha，不是 filter。**

主材料是 2026 新仓库 **`zkmike11/crypto-quant-dashboard`**。repo 表面上像“实时因子仪表盘”，但对我们更值钱的不是网页本身，而是它在 `reversion` 这条分支里把两个很适合短周期 desk 的部件拼成了一个透明的 mean-reversion score：
- `lib/calc/reversion.ts`：`bollingerPosition(closes, 20, 2)`，衡量价格贴近上/下轨的程度；
- `app/api/signals/route.ts`：先算横截面 `priceZScores1W`，再把它喂给 `computeReversionFromCandles`；
- `relativeReversion(priceChange1WZScore) = -priceChange1WZScore`，即**最近相对涨多的更该被做空，跌多的更该被做多**；
- 最终 `compositeReversion = 0.5 * bollingerPos + 0.5 * relativeReversion`。

repo 自己用的是 Hyperliquid 公共数据、偏 `1D/1W` 可视化语境；但它给的 skeleton 很适合我们 desk 直接压缩到 `15m/5m`：
**把“横截面 return z-score + 自身布林带位置”做成 overextension score，然后做 strongest-overbought vs strongest-oversold 的 spread fade。**

## 2. 核心结论
- **一句话结论：** 这条线当前最值得 intake 的，不是把 dashboard 原样搬来，而是把它改写成 **`15m` top1-vs-top1 cross-sectional overextension fade** 的 market-neutral raw alpha。
- **一句话证据：** 我按 repo 的 reversion skeleton 做了 Hyperliquid 公共 `15m/5m` portability probe；结果显示 `15m` 的 top-vs-bottom spread 在 `1h~3h` 持有窗里都稳定为正，且 `12-bar` 最像样。

最关键的数据点：
1. **`15m` top1-bottom1，持有 `4` bars（约 `1h`）**：`n=4909`，`gross_mean≈+5.60 bps`，胜率约 `54.9%`。  
2. **`15m` top1-bottom1，持有 `8` bars（约 `2h`）**：`n=4905`，`gross_mean≈+8.56 bps`，胜率约 `55.4%`。  
3. **`15m` top1-bottom1，持有 `12` bars（约 `3h`）**：`n=4901`，`gross_mean≈+12.04 bps`，胜率约 `56.0%`。  
4. **`5m` top1-bottom1，持有 `8` bars（约 `40m`）**：`n=4731`，`gross_mean≈+6.11 bps`，胜率约 `56.4%`。  
5. **`5m` top1-bottom1，持有 `12` bars（约 `1h`）**：`n=4727`，`gross_mean≈+7.81 bps`，胜率约 `56.2%`。  

如果按保守口径把它理解成 **两腿 roundtrip 合计约 `8 bps`** 的 taker 成本，那么：
- `15m, 12-bar` 仍大致还能留出 **`~+4 bps`** 的净空间；
- `15m, 8-bar` 基本接近成本线；
- `5m` 版本更像 **child execution / quicker recycle**，不如 `15m` 母信号稳。

## 3. 为什么和当前 desk 直接相关
这轮值得保留，不是因为“又找到一个 loser→winner fade”，而是因为 repo 给的是一个更**可工程化、可模块化、可扩 universe** 的 raw alpha 壳：
- **横截面腿**：同一时刻找谁“相对涨太多/跌太多”；
- **时序腿**：再看这个币自身是否已经贴近布林带极端；
- **组合方式**：不是单腿猜方向，而是直接做 `most-overextended short` vs `most-oversold long`；
- **数据源**：Hyperliquid 公共 API，无需 key，可快速复现；
- **落地形态**：天然适合 `15m signal -> 5m execution`，也适合接 funding / OI / liquidity veto。

换句话说，它不是“纯解释性看板”，而是**已经把 signal family 写进代码**的 repo-based raw alpha intake。

## 3.5 策略拆解（必填）
- 方向属性：横截面、relative-value、market-neutral、mean-reversion
- 基础 alpha：同一时刻里，涨幅最离谱且贴上轨的币更容易回吐；跌幅最离谱且贴下轨的币更容易反弹
- regime：更适合 liquid majors、非单边爆量趋势挤压时段；若市场进入单边 broad risk-on/risk-off，同向挤压会削弱 fade
- filter / veto：
  - 横截面分布太平（`ret_z` 不够分散）时不做；
  - 布林带宽度过窄时，可能只是无聊震荡，不值得付费；
  - funding / OI / news shock 很极端时，单纯价格 overextension 容易被 trend 碾过去
- risk / sizing / execution overlay：
  - 基础版用 top1-bottom1 等权；
  - 每腿 notional 对称，做成 beta-lite spread；
  - 先用 `8/12` bars 固定退出，再比较 `score` 回归中性提前平仓

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A（主策略来源）：GitHub 公开仓 `zkmike11/crypto-quant-dashboard`
- 数据源 B（代理回测数据）：Hyperliquid 公共 `candleSnapshot` REST API，无需 API key
- 更新频率：原仓通过 Hyperliquid 公共接口实时更新；本轮最小实验使用 `15m/5m` candles
- 最小实验口径：
  - 标的：`BTC/ETH/SOL/XRP/DOGE/ADA/LINK/AVAX/BNB/HYPE`
  - `15m` 样本：近 `60d`，1 日 lookback = `96` bars
  - `5m` 样本：近 `20d`，1 日 lookback = `288` bars
  - 分数：`score = 0.5 * bb_pos + 0.5 * ret_z`
  - 组合：每个 bar 做 `long lowest-score 1`、`short highest-score 1`
  - 持有：`4/8/12` bars 固定持有
  - 成本：研究口径先用 **两腿合计 `8 bps` roundtrip** 做保守压力测试

### 4.2 这组快检怎么读
- **最值得保留的是 spread，不是单腿。** 单腿很容易被 broad market 方向淹没，但 top-vs-bottom 更贴合 repo 的横截面 DNA。  
- **`15m` 比 `5m` 更像母信号。** `5m` 也有 edge，但更像执行层和加速版，不如 `15m` 稳。  
- **持有时间不是越短越好。** 当前结果反而是 `12-bar` 明显优于 `4-bar`，说明这条线不是秒级噪声修复，而是 **`1~3h` 的 overextension normalization**。  

## 5. 为什么这次不把它降级成 filter / overlay
因为这里最核心的问题“到底做什么”已经很清楚：
> **做多当前最被压低的一腿，做空当前最被抬高的一腿，赌的是相对价格回归。**

这就是标准的 raw alpha 叙事，而且 entry / hold / sizing / cost 都能讲清楚。它不是只在告诉你“什么时候别做别的 alpha”，而是自己就能站成一个独立的 relative-value 策略原型。

## 6. 下一步怎么测
1. **先做 cost ladder**：重点看 `4 / 6 / 8 / 10 bps` 下，`15m 8-bar` 和 `15m 12-bar` 还能不能保住正净值。  
2. **加横截面 admission**：只有当 `max(score) - min(score)` 超过阈值时才开仓，避免平庸时段白付手续费。  
3. **把 top1-bottom1 扩成 top2-bottom2**：检验 edge 是 strongest-only 还是可以平滑成 basket。  
4. **补 funding / OI veto**：若最强 overextended 同时伴随极端 funding/OI 扩张，可能更适合延后 fade。  
5. **做 `15m signal -> 5m child execution`**：比较 next-open、半仓分批、回踩入场三种执行，对净 bps 的影响。  
6. **再切到更贴近实盘的 universe**：把 `BTC/ETH/SOL/XRP/LINK/BNB` 作为第一版 production pool，先验证是否比 10 币混池更干净。  

## 7. 风险与保留意见
- 这轮是 **repo skeleton portability probe**，不是对作者 dashboard 全栈逐行复刻。  
- repo 原始代码更偏日级 lookback 和 broad universe 看板；我们这轮做的是 **short-cycle desk 改写版**，因此结果应理解为“这个 skeleton 能否迁移”，而不是“作者原设定已经被完全验证”。  
- 这条线和我们近期一些 loser-winner / residual-reversal 主题有家族相似性，所以更需要靠 **`bb_pos` 这条时序 overextension 腿** 来证明它不是单纯重复 old idea。  

## 8. 来源
1. **zkmike11. (2026). _crypto-quant-dashboard_. GitHub repository.**  
   - Repo URL: https://github.com/zkmike11/crypto-quant-dashboard  
   - Readable URL: https://github.com/zkmike11/crypto-quant-dashboard  
   - GitHub API metadata 显示创建时间：`2026-04-13`
2. **Source audit files**  
   - README: https://github.com/zkmike11/crypto-quant-dashboard/blob/main/README.md  
   - Reversion page: https://github.com/zkmike11/crypto-quant-dashboard/blob/main/app/reversion/page.tsx  
   - Signals route: https://github.com/zkmike11/crypto-quant-dashboard/blob/main/app/api/signals/route.ts  
   - Reversion calc: https://github.com/zkmike11/crypto-quant-dashboard/blob/main/lib/calc/reversion.ts  
   - Relative strength calc: https://github.com/zkmike11/crypto-quant-dashboard/blob/main/lib/calc/relative-strength.ts  
   - Hyperliquid data adapter: https://github.com/zkmike11/crypto-quant-dashboard/blob/main/lib/data/hyperliquid.ts
3. **Hyperliquid Docs / Public API usage context**  
   - Readable URL: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint  
   - 本轮实际调用的是公开 `info` endpoint 下的 `candleSnapshot`

## 9. 本地产物
- Probe 脚本：`reports/artifacts/quant_digests/2026-04-19_hl_xs_overextension_probe.py`
- `15m` panel：`reports/artifacts/quant_digests/2026-04-19_hl_xs_overextension_15m_panel.csv`
- `15m` top1 summary：`reports/artifacts/quant_digests/2026-04-19_hl_xs_overextension_15m_top1_summary.csv`
- `15m` top1 events：`reports/artifacts/quant_digests/2026-04-19_hl_xs_overextension_15m_top1_events.csv`
- `5m` panel：`reports/artifacts/quant_digests/2026-04-19_hl_xs_overextension_5m_panel.csv`
- `5m` top1 summary：`reports/artifacts/quant_digests/2026-04-19_hl_xs_overextension_5m_top1_summary.csv`
- `5m` top1 events：`reports/artifacts/quant_digests/2026-04-19_hl_xs_overextension_5m_top1_events.csv`
- JSON summary：`reports/artifacts/quant_digests/2026-04-19_hl_xs_overextension_summary.json`
