# 别把 R-Breaker 只读成老派期货日内线：对 short-cycle crypto desk，更该先测的是「前一 session 高低收六线 × breakout/reversal 双模态」这条完整 raw alpha
- 时间：2026-04-22 01:06 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `strategies/24_r_breaker.py`）+ Binance USDⓈ-M public-data portability probe（8 个 liquid majors，`5m/15m`，`90d`）
- 主题类型：raw alpha
- 基础 alpha：用前一交易 session 的高/低/收锚定 6 条日内价格线；极端突破时顺势跟、冲高/杀低失败时反手做回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / intraday / breakout / reversal / pseudo-session / r-breaker / single-asset / binance-perpetual / 5m / 15m / repo / public-data / cost / risk
- 证据类型：源码规则 + public-data portability probe

## 1. 这次看了什么
这次看的是 `ringoshinnytech/tqsdk-strategies` 这个 2026 仍在更新的中文策略仓，重点是 `strategies/24_r_breaker.py`。它给的不是“某个指标碰一下就下单”的半成品，而是一个相对完整的日内策略骨架：

1. 用上一 session 的 **高 / 低 / 收** 算出 6 条线；
2. 当价格直接冲破最外层线时，按 **breakout** 追；
3. 当价格先摸到“观察线”，随后又跌回/涨回“反转线”时，按 **failed extreme → reversal** 反手；
4. session 结束前强制平仓，不过夜。

它对 crypto desk 的价值，不是“这套 90 年代期货公式神奇有效”，而是：**这是一条天然适合 `5m/15m` 的、可直接拆成完整策略的 raw alpha 母板**。因为它把 breakout 和 mean reversion 两条腿，统一放到了同一个前序锚点上。

## 2. 核心结论
- **一句话核心结论：** R-Breaker 对 crypto 不该被读成“老派期货老古董”，它更像一个 **session-anchored 双模态 alpha 壳**：行情真展开时追，极端失败时反手。
- **一句话 first verdict：** 用 Binance USDⓈ-M 8 个 liquid majors 做 `90d` 快检后，能看到这条线 **有 pocket，但绝不是 broad-book 通杀**；而且 **24h pseudo-day 普遍比 8h funding session 更像样**，后者明显容易过度交易。
- repo 默认是 5 分钟期货日内交易思路，非常接近我们 desk 的 child timeframe；迁到 crypto 时，真正要调的不是公式本身，而是 **session 定义、交易腿拆分、趋势日止损**。
- 我做了两个 session 口径：
  - **24h pseudo-day**：按 UTC 日切；
  - **8h pseudo-session**：按 funding window 切。
- 结果很清楚：**8h 版交易笔数暴涨，但均值大多更差**。例如 `5m` 全池里，24h 版共约 `200` 笔，8h 版约 `642` 笔；`15m` 里，24h 版约 `189` 笔，8h 版约 `580` 笔。换成人话：8 小时切法让它更忙，但不更赚钱。
- 24h 版出现了少数值得继续追的 pocket：
  - `DOGEUSDT 5m`：约 **`+47.8 bps/笔`**，胜率 **`65.2%`**；
  - `ADAUSDT 5m`：约 **`+32.1 bps/笔`**；
  - `DOGEUSDT 15m`：约 **`+24.8 bps/笔`**，胜率 **`52.2%`**；
  - `BTCUSDT 5m` 也有 **`+6.7 bps/笔`**，但远没有 meme/alt pocket 厚。
- 8h 版只有零散 pocket 还勉强站住，比如 `SOLUSDT 15m` 约 **`+7.2 bps/笔`**、`LINKUSDT 5m` 约 **`+11.4 bps/笔`**；但多数品种仍为负，说明它更像 **把前一段噪音也当锚点**，不是更懂市场结构。
- 所以 first verdict 不是“R-Breaker 可直接全市场上线”，而是：**这条线值得进入素材池，因为它给了一个很清楚的完整 raw alpha 骨架；但第一优先测试应该是 24h anchor + leg 拆分，不是 8h 全量硬跑。**

## 3. 为什么和当前项目有关
这条线和 desk 现在的关系很直接：我们最近已经补了不少 pure trend、pairs、basis、grid、microstructure 素材，但 **“同一套 session 锚点里，趋势追随和失败反转如何并存”** 这个位置，其实还缺一个足够朴素、足够完整、足够能快速复现的母板。

R-Breaker 补的正是这个空缺。

换成人话：
- 如果价格真把昨天区间狠狠干穿，那你别老想着抄顶抄底，先承认它在走趋势；
- 但如果价格只是先冲过头、随后又缩回来，那就别再追，反而该把它当成“失败突破后的回摆”。

这对 `1m/3m/5m/15m` desk 很有用，因为它天然支持两件事：
1. **同一框架里同时容纳 breakout 与 mean reversion**；
2. **很容易拆成 router**：突破腿给 continuation，反转腿给 fade，不用混着写。

## 3.5 策略拆解（必填）
- 方向属性：单资产、日内双向、breakout + reversal 双模态
- 基础 alpha：previous-session anchored price-level reaction
- regime：上一 session 的范围与当天是否真正扩张
- filter / veto：可加 ADX、前一 session range percentile、volume expansion、funding 窗口黑名单
- risk / sizing / execution overlay：固定 1x notional 起步；趋势腿可用 ATR/中线追踪；反转腿必须加 hard stop 与 time-stop

## 4. 可复刻的最小实验
### 4.1 规则原型
先用上一 session 的 `H/L/C` 算 6 条线：
- `Pivot = (H + L + C) / 3`
- `BBreak = H + 2 × (Pivot - L)`
- `SSetup = Pivot + (H - L)`
- `SEnter = 2 × Pivot - L`
- `BEnter = 2 × Pivot - H`
- `BSetup = Pivot - (H - L)`
- `SBreak = L - 2 × (H - Pivot)`

### 4.2 最小交易壳
- **Breakout long**：收盘上穿 `BBreak`
- **Breakout short**：收盘下穿 `SBreak`
- **Reversal short**：当日先触及 `SSetup`，随后收盘跌回 `SEnter` 下方
- **Reversal long**：当日先触及 `BSetup`，随后收盘反弹回 `BEnter` 上方
- **Flat rule**：session 结束强平

### 4.3 我这次的 public-data probe 口径
- 标的：Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`
- 周期：`5m`、`15m`
- 样本：最近 `90d`
- session：`24h` 与 `8h` 两版
- 成本：粗扣单边 `4 bps`，翻仓按更高 round-trip 粗算
- 结果文件：`reports/artifacts/quant_digests/rbreaker_pseudosession_probe_summary_2026-04-22.csv`

## 5. 结果怎么读
### 5.1 最重要的不是“均值正不正”，而是 session 定义
这套东西本质上依赖“上一段价格区间”是不是一个有信息量的锚点。Crypto 24/7 连续交易，没有天然开收盘，所以 **session 切法本身就是策略参数**。

这次快检说明：
- **24h anchor** 更像“市场真的记得昨天高低收”；
- **8h anchor** 更像把 funding 节点硬塞成 session，噪音更大，交易更频。

### 5.2 这条线更像 alt/meme pocket，不像 broad market baseline
DOGE、ADA 在 24h 版里明显更厚，BTC 只有薄正，ETH/BNB/XRP/LINK 多数口径仍然不理想。说明这条线更可能依赖：
- 明确的日内 crowding；
- 更爱冲过头又拉回来的币种；
- 对“昨天区间”仍有记忆的单币行为。

也就是说，它不像 pairs/basis 那种结构性价差，更像 **session memory 驱动的单币方向/反转混合壳**。

## 6. 风险与保留意见
- repo 给的是完整骨架，但 **没有真正 crypto-first 的止损/费用/滑点校准**。
- 如果把 breakout 腿和 reversal 腿混在一起看，很容易误判来源：某些币可能只是 reversal 腿赚钱，breakout 腿纯亏；反之亦然。
- 8h 切法过度交易这一点很明显，说明 **funding window 不是天然“更高信息量”的 session**。
- 24h 版虽然出现 pocket，但宽度仍不够说明“可直接 broad-book 上线”；更像下一轮要继续做 leg attribution 的候选。

## 7. 下一步怎么测
1. **先拆腿，不要混测。** 分开跑 breakout-only、reversal-only、combined，确认 edge 到底来自哪一边。
2. **先保留 24h anchor，暂时别把 8h 当主线。** 8h 可以留作对照，不要当默认生产口径。
3. **加“前一 session range percentile”筛选。** 只保留前一段不是极端大波动、也不是极端死寂的中等 range，看能否减少假突破。
4. **给 reversal 腿补 hard stop。** 最简单先测：`1.0~1.5 × previous-session range fraction` 或 `0.75~1.0 ATR`，否则趋势日里反转腿会被连打。
5. **给 breakout 腿补“只做首次突破”版本。** 避免同一天多次翻来覆去过度交易。
6. **做 alt pocket router。** 第一轮先聚焦 `DOGE/ADA/SOL`，不要一上来 broad basket 等权。

## 8. 结论
如果现在问一句：**它为什么比继续补 raw alpha 更值得？**

答案是：因为它本身就是 raw alpha，而且还是少数那种 **一上来就带 entry / reversal / flat / sizing 基线** 的完整母板。它不是又一个只能当 filter 的旁支件。

但如果再问一句：**它现在是不是 production-ready alpha？**

答案也是明确的：**还不是。** 这轮最值得保留的，不是“R-Breaker 公式神奇有效”，而是 **session-anchored 双模态框架** 这件事本身，尤其是 `24h` 口径下的 breakout/reversal leg 拆分。

## 9. 相关产物
- Probe summary：`reports/artifacts/quant_digests/rbreaker_pseudosession_probe_summary_2026-04-22.csv`

## 10. 来源
- ringoshinnytech. (2026). **tqsdk-strategies**. GitHub repo.  
  Repo URL: `https://github.com/ringoshinnytech/tqsdk-strategies`
- Source file: `strategies/24_r_breaker.py`  
  Readable URL: `https://raw.githubusercontent.com/ringoshinnytech/tqsdk-strategies/main/strategies/24_r_breaker.py`
- Source file: `README.md`  
  Readable URL: `https://raw.githubusercontent.com/ringoshinnytech/tqsdk-strategies/main/README.md`
- Practitioner origin often attributed to **Richard Saidenberg**, *Futures Magazine*, early R-Breaker write-up. DOI: N/A. Readable URL: N/A.
