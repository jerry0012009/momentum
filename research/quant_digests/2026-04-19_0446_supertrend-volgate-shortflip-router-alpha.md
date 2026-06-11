# 别把这份 SuperTrend 仓只读成“TradingView 指标自动下单脚本”：对 short-cycle crypto desk，更该先拆的是「ATR-trail 趋势翻转 × vol gate × strongest short flip」这条 raw alpha
- 时间：2026-04-19 04:46 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：当价格从 SuperTrend 下方重新跌回其下、且最近短窗波动已明显抬升时，说明 ATR-adjusted 趋势翻转可能刚开始而不是噪音回摆；若同一时点多币一起翻空，优先做离 SuperTrend 最远的一档。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：trend / supertrend / atr / trend-flip / short-router / volatility-gate / binance-perpetual / 15m / 5m
- 证据类型：工程经验 + repo source audit + public-data portability probe

## 1. 这次看了什么
看的是 GitHub 仓 `yanboishere/Trade.with-SuperTrend.parameter`。虽然仓最早建于 2023，但最近可见更新时间到 `2026-04-06`，核心就是把 TradingView 的 SuperTrend 翻转信号接到交易接口，再补上 stop-loss / take-profit、波动率开仓门槛、以及“最近 30 分钟没继续变化就平仓”的超短超时逻辑。

**一句话核心结论：** 这条线当前不能被读成“SuperTrend 双向翻转都能直接做”，更像一个 **`15m` strongest-only short flip pocket**；long 端和全样本都偏薄。  
**一句话证明方式：** 我把 repo 的 `ATR-trail trend flip + vol gate + timeout` 思路，映射到 Binance USDⓈ-M `15m/5m` 多币公共数据上，比较 all-signals、long/short 拆分、以及同刻只留最强一档的 router 表现。

## 2. 核心结论
- repo 提供的是**完整策略壳**，不是纯指标说明：有 SuperTrend 计算、下单、止损止盈、波动率门槛，还额外给了“近 `30m` 没继续变化就平仓”的退出思路。
- 但 portability probe 很清楚：**对称 long/short 读法不成立**。`15m` 全样本 `1263` 笔，next `8` bars（约 `2h`）只有约 `-0.17bps gross / -8.17bps net`；`5m` 全样本 `1667` 笔更差，约 `-0.98bps gross / -8.98bps net`。
- `15m` long flip 明显偏弱：`628` 笔，约 `-1.88bps gross / -9.88bps net`；这说明别把“翻多”想当然当成对称镜像机会。
- 真正留下 pocket 的，是 **`15m` vol-positive strongest short flip top1 router**：`237` 笔，约 `+9.17bps gross / +1.17bps net`，median 约 `+1.78bps gross`，胜率约 `50.63%`。厚度不算夸张，但至少说明“翻空后再顺着打最强那一档”比 all-signals 更像可继续深挖的 raw alpha。
- `5m` 的 top1 long 虽然比 all-signals 好一些（`299` 笔，约 `+3.98bps gross`），但粗扣 `8bps` 后仍约 `-4.02bps net`；所以当前更像 **`15m` 母信号 + `5m` child execution**，不是裸 `5m` 主策略。

## 3. 为什么和当前项目有关
最近素材池里虽然已有不少 breakout / continuation / MR，但 **ATR-trailing trend flip** 这种“趋势翻转壳”还没有被单独拆干净。这类 repo 的价值，不是告诉我们“SuperTrend 很神”，而是把一个常见 TradingView 指标，往 **entry / exit / timeout / volatility veto / router** 这些更 desk-friendly 的组件上拆开。当前 probe 又进一步告诉我们：这类壳更值得先研究的是 **short-side admission / router**，而不是照单全收双向开仓。

## 3.5 策略拆解（必填）
- 方向属性：顺势翻转 / 单资产；当前 pocket 偏 short-only
- 基础 alpha：ATR-adjusted trend flip after volatility expansion
- regime：更适合近期波动已经抬起来、不是低波死区里的假翻转
- filter / veto：`realized_vol20 > 0.2%`；优先 `volume_z > 0`；同一时点多币同时翻转时只留 `|close-supertrend|/ATR` 最大的一档
- risk / sizing / execution overlay：下一根开盘进场；固定 `8 x 15m` time-box；可补 repo 里的 `30m no-change timeout` 与止损止盈；成本先按 `8bps` round-trip 粗算

## 4. 可复刻的最小实验
- 研究假设：当 `15m` 收盘刚从 SuperTrend 上方翻到下方，且近 `20` 根的 realized vol 已超过 `0.2%`，后续 `~2h` 更可能继续顺势而不是立刻打回。
- 一个可计算定义：标准 `SuperTrend(ATR=10, multiplier=3)`；若 `trend` 从 `+1 -> -1`，记为 short flip；若当刻 `realized_vol20 > 0.2%`，且 `volume_z > 0`，则入候选池；若同刻多币同时触发，只做 `|close-supertrend|/ATR` 最高的一档。
- 最小回测切口：Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`，先测 `15m` 信号持有 `8` 根，再把 entry 下沉到 `5m` 做 pullback / child execution。
- 最该先看：`15m top1 short` 的 net bps 是否能在更长样本、更多币、以及不同成本梯度下保持为正；其次再看 `timeout exit` 是否比固定 `8 bars` 更好。

## 5. 风险与保留意见
- 当前 pocket 很薄：`15m top1 short` 虽然转正，但 net 只约 `+1.17bps/trade`，远称不上“可直接上线”。
- 胜率并不高，优势更多来自右尾而不是稳定高命中；如果 child execution 没做好，很容易被成本再吃掉。
- 这类指标仓常见问题是**把视觉上顺眼的翻转误当成系统性 alpha**；本轮 probe 已明确提醒：long 端和全样本都不行。
- repo 本身更偏 API / demo 项目，不是严谨 backtest 框架；真正值钱的是它给出的组件拆法：`trend flip -> vol veto -> timeout exit -> strongest-only router`。

## 6. 来源
- yanboishere. (repo active through 2026 metadata). *Trade.with-SuperTrend.parameter*.
  - Repo URL: `https://github.com/yanboishere/Trade.with-SuperTrend.parameter`
  - Readable URL: `https://github.com/yanboishere/Trade.with-SuperTrend.parameter/blob/master/README.md`
- Source audit used in this digest:
  - `https://raw.githubusercontent.com/yanboishere/Trade.with-SuperTrend.parameter/master/README.md`
  - `https://raw.githubusercontent.com/yanboishere/Trade.with-SuperTrend.parameter/master/How.SuperTrend.code.works.md`
  - `https://raw.githubusercontent.com/yanboishere/Trade.with-SuperTrend.parameter/master/main.py`
  - `https://raw.githubusercontent.com/yanboishere/Trade.with-SuperTrend.parameter/master/%E6%A3%80%E6%9F%A5%E4%BB%A3%E7%A0%81%E8%BF%90%E8%A1%8C%E5%89%8D%E7%9A%84K%E7%BA%BF%E4%B8%AD%20%E5%A6%82%E6%9E%9C%E8%BF%87%E5%8E%BB%E4%B8%80%E6%AE%B5%E6%97%B6%E9%97%B4%20K%E7%BA%BF%E6%9C%80%E5%A4%A7%E6%B3%A2%E5%8A%A8%E7%8E%87%E5%B0%8F%E4%BA%8E0.2%25%20%E5%88%99%E4%B8%8D%E5%BC%80%E4%BB%93%E4%BA%A4%E6%98%93%20%E7%9B%B4%E5%88%B0%E6%B3%A2%E5%8A%A8%E7%8E%87%E5%A4%A7%E4%BA%8E%E8%BF%99%E4%B8%80%E6%B0%B4%E5%B9%B3%20%E5%86%8D%E8%BF%9B%E8%A1%8C%E6%8E%A5%E4%B8%8B%E6%9D%A5%E7%9A%84%E5%BC%80%E4%BB%93%E6%93%8D%E4%BD%9C.py`
  - `https://raw.githubusercontent.com/yanboishere/Trade.with-SuperTrend.parameter/master/%E6%A3%80%E6%9F%A5%E8%B6%85%E7%BA%A7%E8%B6%8B%E5%8A%BF%E6%8C%87%E6%A0%87%E6%98%AF%E5%90%A6%E5%9C%A8%E6%9C%80%E8%BF%9130%E5%88%86%E9%92%9F%E5%86%85%E5%8F%91%E7%94%9F%E5%8F%98%E5%8C%96%EF%BC%8C%E5%B9%B6%E5%9C%A8%E6%9C%89%E4%BB%93%E4%BD%8D%E6%97%B6%E5%B9%B3%E4%BB%93.py`

## 7. 本地 portability probe 产物
- `reports/artifacts/quant_digests/2026-04-19_supertrend_flip_summary.csv`
- `reports/artifacts/quant_digests/2026-04-19_supertrend_flip_router_summary.csv`
- `reports/artifacts/quant_digests/2026-04-19_supertrend_flip_15m_events.csv`
- `reports/artifacts/quant_digests/2026-04-19_supertrend_flip_5m_events.csv`
- `reports/artifacts/quant_digests/2026-04-19_supertrend_flip_portfolio.json`
